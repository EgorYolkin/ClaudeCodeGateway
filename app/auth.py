from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.settings import settings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
x_api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)

async def get_api_key(
    api_key: str = Security(api_key_header),
    x_api_key: str = Security(x_api_key_header)
):
    token = api_key or x_api_key
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
    
    # In Anthropic API, it might be "Bearer <token>"
    if token.startswith("Bearer "):
        token = token[7:]
    
    if token != settings.GATEWAY_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return token
