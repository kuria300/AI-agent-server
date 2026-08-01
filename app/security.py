from .config import settings
from fastapi import HTTPException, Header, status
# from fastapi.security import APIKeyHeader

# checks header name and auto_error to false to allow us to raise a custom error
# api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)   

async def verify_api_key(api_key: str = Header(...)):
    """
    this protects the routes by checking if aoi_key passed is present and simillar to one in backend

    api_key type is str= header(...)  epilisis means the header must not be empty
    """
    if api_key != settings.api_key:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")