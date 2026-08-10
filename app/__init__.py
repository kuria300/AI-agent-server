from fastapi import FastAPI
from app.config import settings
from contextlib import asynccontextmanager  # lets a normal function or async use yield for before/after
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import chat_router
from app.routes.home import home_router
from app.routes.file import files_router
from app.routes.fetchHistory import chat_hist_router
from .state import app_state
from .db import get_engine


@asynccontextmanager
async def Lifespan(app: FastAPI):

    print(f"starting {settings.app_name}")
    print(f"connecting to llama AI server at {settings.ollama_base_url}")

    from langchain_ollama import OllamaLLM
    app_state['llm'] = OllamaLLM(
        model=settings.ollama_model,
        base_url = settings.ollama_base_url,
        num_ctx=2048, # content window amount of words AI can see at ince rougly 1500 words for my small 8GB ram computer 4096 for more 
        temperature=0.1,
        keep_alive="10m",
    )

    app_state['thread_pool'] = ThreadPoolExecutor(max_workers=4)
    # app_state["db"] = connect_to_database()              # connect to DB once
    # initialize a async engine to be used by app 
    engine = get_engine()

    yield # after startup here we run the app and receive requests and respond 
    # pasue here do what app does and come backe later

    print('shutting down...')

    await engine.dispose()
    if 'thread_pool' in app_state:
        app_state['thread_pool'].shutdown(wait=True)
    app_state['llm'] =None  #free llm from ram
    app_state.clear()


def create_app() -> FastAPI:
    app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=Lifespan
    )

    origins= [
        "http://192.168.0.120:3000",
        "http://localhost:3000"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)
    app.include_router(home_router)
    app.include_router(files_router)
    app.include_router(chat_hist_router)




    return app
