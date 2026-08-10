from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.security import verify_api_key
from ..services.agent import get_chat_history, clear_history, list_sessions

chat_hist_router = APIRouter(prefix="/api/agent", tags=['agent'], dependencies=[Depends(verify_api_key)])

@chat_hist_router.get('/chat-history')
async def history(session_id: str, mode: str = "general"):
    """get history of a specific mode"""
    return get_chat_history(session_id, mode)


@chat_hist_router.delete("/history")
async def new_chat(session_id: str, mode: str = "general"):
    clear_history(session_id, mode)
    return {"status": "cleared"}


@chat_hist_router.get('/summary')
async def session_summary():
    """get summary of sessions for that one user"""
    return list_sessions()


