import json
import redis
import os
from app.config import settings


redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses= True
)

def load_history(session_id: str) ->list:

    """
    load history from redis of session_id pased as argumnt
    if no history found return empty list

    message looks like
     each message looks like:
    {
        "role": "human",
        "content": "fix my loop"
    }
    or
    {
        "role": "ai",
        "content": "here is the fixed loop..."
    }
    """

    key= f"kingslanding:{session_id}"

    try:
        redis_loaded_data= redis_client.get(key)

        if redis_loaded_data:
            # we deserialize the json string back to a list of messages
            return json.loads(redis_loaded_data)
        else:
            print(f"Redis: no history found for session_id: {session_id}")
            return []
    except Exception as e:
        print(f"error loading history from redis: {e}")
        return []

def add_message(session_id: str, role:str, content: str):
    """
    add a message to redis for a given user session_id, role( if human or ai) and content of message
    
    """
    key = f"kingslanding:{session_id}"

    history = load_history(session_id)

    history.append({"role": role, "content": content})

    save_history(session_id, history)


def save_history(session_id: str, history: list):
    """
    save the history list to redis for a given session_id
    """
    key = f"kingslanding:{session_id}"

    try:
        # serialize the history then push to redis
        redis_client.setex(key, settings.redis_ttl, json.dumps(history))
    except Exception as e:
        print(f"error saving history to redis: {e}")

    
def clear_history(session_id: str):
    """ clear the history from redis for given session_id """

    key = f"kingslanding:{session_id}"

    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"error clearing history from redis: {e}")


