from app.prompts.prompt import SYSTEM_PROMPT, CODING_PROMPT, RESEARCH_PROMPT
from app.state import app_state
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic import hub
from langsmith import Client
# from langchain.core.prompts import PromptTemplate
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from app.tools.tools import read_file, calculator, search, get_weather, search_documents
from app.services.redis_service import redis_client, clear_history as clear_history_redis
from app.config import settings


PROMPTS= {
    "general": SYSTEM_PROMPT,
    "coding": CODING_PROMPT,
    "research":RESEARCH_PROMPT
}

client = Client()

def _composite_session_id(session_id: str, mode: str) -> str:
    """
    scope each mode to its own redis history by folding mode into the session key
    e.g. 'abc123' + 'coding' -> 'abc123:coding'
    """
    return f"{session_id}:{mode}"

def get_tool_for_mode(mode: str) -> list:
    """
    each mode gets different tools 
    """

    if mode == "coding":
        return [calculator, DuckDuckGoSearchRun(), read_file, search_documents]

    elif mode == "research":
        return [search, DuckDuckGoSearchRun(), calculator, search_documents]

    else:
        return [get_weather, search, calculator, read_file, search_documents]


def get_prompt_for_mode(mode:str):
    """
    each mode gets its own personality 

    use different prompts for thinking
    """

    if mode == 'coding':
        prompt = client.pull_prompt("hwchase17/react-chat", dangerously_pull_public_prompt=True)
        prompt = prompt.partial(system_message=CODING_PROMPT)
    elif mode == 'research':
        prompt = client.pull_prompt("hwchase17/react-chat", dangerously_pull_public_prompt=True)
        prompt = prompt.partial(system_message=RESEARCH_PROMPT)
    else:
        prompt = client.pull_prompt("hwchase17/react-chat", dangerously_pull_public_prompt=True)
        prompt = prompt.partial(system_message=SYSTEM_PROMPT)

    return prompt


def build_memory_from_redis(session_id:str) -> RedisChatMessageHistory:
    """
    we use langchain_community.chat_message_histories.RedisChatMessageHistory to build memory from redis for given session_id
    so we can pass it to agent
    and we pass session_id, redis_client, ttl, key_prefix to RedisChatMessageHistory to build memory from redis
    """
    memory = RedisChatMessageHistory(
        session_id=session_id,
        url=settings.redis_url,
        ttl=settings.redis_ttl,
        key_prefix="kingslanding:"   
    )
    return memory


def clear_history(session_id: str, mode: str= "general"):
    """
    clear the history from redis for given session_id
    """
    try:
        clear_history_redis(_composite_session_id(session_id, mode))
    except Exception as e:
        print(f"error clearing history from redis: {e}")


def get_chat_history(session_id: str, mode: str = "general") -> list[dict]:
    """
    load existing messages for a session_id+mode pair, so the frontend can
    rehydrate a mode's chat when the user switches back to it
    """
    memory = build_memory_from_redis(_composite_session_id(session_id, mode))
    return [
        {"role": "user" if m.type == "human" else "ai", "text": m.content} for m in memory.messages
    ]

def list_sessions() -> list[dict]:
    """ 
    scan redis for all kingslanding: keys and turn them into a flat list of
    {session_id, mode, label} for the sidebar's Recents list

    keys() blocks the server, preventing it from satisfying other client requests. By contrast, 
    SCAN only returns a few results at a time, allowing the server to stay responsive to all clients.
    """

    sessions = []
    key_prefix = "kingslanding:"

    for key in redis_client.scan_iter(match=f"{key_prefix}*"):
        key_decode = key.decode() if isinstance(key, bytes) else key
        composite = key_decode[len(key_prefix):]  # "kingslanding:abc123:coding" -> "abc123:coding"

        if ":" not in composite:
            continue  # skip legacy keys

        session_id, mode = composite.rsplit(":", 1)

        memory = build_memory_from_redis(composite)
        messages = memory.messages
        if not messages:
            continue

        first_human = next((m.content for m in messages if m.type == 'human'), "New Chat")
        label = (first_human[:10] + "...") if len(first_human) > 10 else first_human

        sessions.append({
            "session_id": session_id,
            "mode": mode,
            "label": label,
        })

    return sessions



async def generate_reply(question: str,  session_id: str, mode: str = 'general') -> str:
    """
    we send the request question user send from frontend 

    together with the prompt + reply from tools called

     then return reply back to user 
    """

    llm = app_state['llm']

    tools= get_tool_for_mode(mode=mode)

    prompts = get_prompt_for_mode(mode=mode)

    # build agent with right tools, instructioins and pass llm
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompts,
    )

    # executor runs the agent 
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=(
        "Parsing Error! Please correct your mistake immediately by checking these rules:\n"
        "1. Check your output and make sure Action and Action Input are on separate lines, then try again.\n"
        "2. Check your available tools! If you do not need a tool to answer or the tool does not exist, output your Final Answer directly."
    )
    )

    # build memory from redis for given session_id
    # This automatically writes to and reads from redis!
    agent_with_memory = RunnableWithMessageHistory(
        runnable=executor,
        get_session_history=build_memory_from_redis,  
        input_messages_key="input",                    
        output_messages_key="output",                 
        history_messages_key="chat_history"             
    )

    # Run with question using async execution
    result = await agent_with_memory.ainvoke(
        {"input": question}, 
        config={"configurable": {"session_id": _composite_session_id(session_id, mode)}}
    )

    return result["output"]







