from fastapi import APIRouter
from fastapi.responses import JSONResponse

home_router = APIRouter(prefix="/home", tags=["home"])

@home_router.get("/")
async def home():
    """ 
    home page 

    we can use JSONResponse to return json or fastAPi returns dict as json no need return {"message":"welcome to your ai"}
    
    we can use pydantic models validate and parse for u  or use data = await request.json()  we acces as data.get('name')
     
    """
    return JSONResponse(content={"message": "Welcome to the AI Agent Server!"})