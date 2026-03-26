from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.schemas import AnthropicMessagesRequest, AnthropicMessagesResponse, CountTokensResponse
from app.handlers.messages import handle_messages, handle_count_tokens
from app.auth import get_api_key
from typing import Optional, Union, AsyncGenerator
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Claude Code Gateway")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/v1/messages")
async def messages(
    request: AnthropicMessagesRequest,
    req: Request, # Получаем объект запроса для заголовков
    _token: str = Depends(get_api_key),
    anthropic_version: Optional[str] = Header(None, alias="anthropic-version"),
    anthropic_beta: Optional[str] = Header(None, alias="anthropic-beta")
):
    logger.info(f"Incoming request for model: {request.model}")
    try:
        # Прокидываем все заголовки
        headers = dict(req.headers)
        result = await handle_messages(request, headers)
        if request.stream:
            return StreamingResponse(result, media_type="text/event-stream")
        return result
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/messages/count_tokens", response_model=CountTokensResponse)
async def count_tokens(
    request: AnthropicMessagesRequest,
    req: Request,
    _token: str = Depends(get_api_key)
):
    try:
        headers = dict(req.headers)
        input_tokens = await handle_count_tokens(request, headers)
        return CountTokensResponse(input_tokens=input_tokens)
    except Exception as e:
        logger.error(f"Error handling count_tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
