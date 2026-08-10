from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.security import verify_api_key
from app.services.agent import generate_reply

# prefix puts /agent in route tags grooup all routes under this in swagger docs
# depends is for dependency injection in fastapi run a function and injet the results in the route here we run and verify apikey on this routes
chat_router = APIRouter(prefix="/api/agent", tags=["agent"], dependencies=[Depends(verify_api_key)])

class ChatReq(BaseModel):
    question: str
    mode: str = 'general'

@chat_router.post('/chat')
async def chat(session_id: str, request: ChatReq):
    ans = await generate_reply(
        question=request.question,
        mode=request.mode,
        session_id=session_id
    )

    return {"message": ans}



