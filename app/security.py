from .config import settings
from fastapi import Request, HTTPException, status

async def verify_api_key(request: Request):
    """
    Protects application endpoints by checking if the incoming request contains
    the correct API key inside its headers, while safely allowing browser
    OPTIONS preflight requests to bypass security checks.
    """

    if request.method == "OPTIONS":
        return

    x_api_key = request.headers.get("x-api-key")

  
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid API key"
        )
