from fastapi import FastAPI
from app.config import settings
from contextlib import asynccontextmanager  # lets a normal function or async use yield for before/after

app_state={} # we use a dict for we will reuse loaded llama model in whole application a a normal variable local will not persist whenimported

@asynccontextmanager
async def Lifespan(app: FastAPI):

    print(f"starting {settings.app_name}")
    print(f"connecting to llama AI server at {settings.ollama_base_url}")

    from langchain_ollama import OllamaLLM
    app_state['llm'] = OllamaLLM(
        model=settings.ollama_model,
        base_url = settings.ollama_base_url,
        num_ctx=2048, # content window amount of words AI can see at ince rougly 1500 words for my small 8GB ram computer 4096 for more 
        keep_alive=0
    )
    # app_state["db"] = connect_to_database()              # connect to DB once

    yield # after startup here we run the app and receive requests and respond 
    # pasue here do what app does and come backe later

    print('shutting down...')
    app_state['llm'] =None  #free llm from ram
    app_state.clear()


def create_app() -> FastAPI:
    app = FastAPI(
    settings.app_name,
    settings.app_name,
    lifespan=Lifespan
    )


    return app
