from app.prompts.prompt import SYSTEM_PROMPT, CODING_PROMPT, RESEARCH_PROMPT
from app import app_state
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
# from langchain.core.prompts import PromptTemplate
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from app.tools.tools import read_file, calculator, search_news, get_weather
from app.services.redis_service import redis_client, clear_history as clear_history_redis
from app.config import settings


PROMPTS= {
    "general": SYSTEM_PROMPT,
    "coding": CODING_PROMPT,
    "research":RESEARCH_PROMPT
}

def get_tool_for_mode(mode: str) -> list:
    """
    each mode gets different tools 
    """

    if mode == "coding":
        return [calculator, DuckDuckGoSearchRun(), read_file]

    elif mode == "research":
        return [search_news, DuckDuckGoSearchRun(), calculator]

    else:
        return [get_weather, search_news, calculator, read_file]


def get_prompt_for_mode(mode:str):
    """
    each mode gets its own personality 

    use different prompts for thinking
    """

    if mode == 'coding':
        prompt = hub.pull("hwchase17/react-chat-conversational")
        prompt = prompt.partial(system_message=CODING_PROMPT)
    elif mode == 'research':
        prompt = hub.pull("hwchase17/react")
        prompt = prompt.partial(system_message=RESEARCH_PROMPT)
    else:
        prompt = hub.pull("hwchase17/react")
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
        redis_client=redis_client,
        ttl=settings.redis_ttl,
        key_prefix="kingslanding:"   
    )
    return memory


def clear_history(session_id: str):
    """
    clear the history from redis for given session_id
    """
    try:
        clear_history_redis(session_id)
    except Exception as e:
        print(f"error clearing history from redis: {e}")

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
        handle_parsing_errors=True,
    )

    # build memory from redis for given session_id
    # This automatically writes to and reads from redis!
    agent_with_memory = RunnableWithMessageHistory(
        runnable=executor,
        message_history=build_memory_from_redis,
        input_key="input", # 
        output_key="output",
        history_key="chat_history"

    )

    # run with question, return answer
    result = agent_with_memory.invoke({"input": question}, config={"configurable": {"session_id": session_id}})
    return result["output"]








