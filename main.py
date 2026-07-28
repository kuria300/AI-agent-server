from fastapi import FastAPI
from pydantic import BaseModel

app= FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_valid: bool

@app.get('/')
def root():
    return {'msg':'hello fastApi'}


@app.get("/users/{user_id}")
async def users(user_id: int, username: str | None=None):
    return {'user_id': user_id, "username": username}


@app.put("/items/{item_id}")
def items(item_id: int, item: Item):
    return {'item_name': item.name, 'item_price': item.price, 'is_active': item.is_valid}
