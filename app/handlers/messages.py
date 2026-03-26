import json
import asyncio
import logging
import os
from typing import Dict, Any, AsyncGenerator, Union
from app.schemas import AnthropicMessagesRequest, AnthropicMessagesResponse
from app.settings import settings

logger = logging.getLogger(__name__)

from app.adapters.openai_adapter import openai_adapter
from app.adapters.gemini_adapter import gemini_adapter
from app.clients.openai_client import openai_client
from app.clients.gemini_client import gemini_client
from app.clients.anthropic_client import anthropic_client
from app.utils.sse import (
    message_start_event, content_block_start_event,
    content_block_delta_event, content_block_stop_event,
    message_delta_event, message_stop_event
)

async def handle_messages(request: AnthropicMessagesRequest, headers: Dict[str, str]) -> Union[AnthropicMessagesResponse, AsyncGenerator[str, None]]:
    model_name = request.model

    # 1. Логика переключения Gemini (Custom Slot)
    if model_name == "gemini":
        raw_data = request.model_dump()
        effort = raw_data.get("reasoning_effort", "medium")
        if effort == "low":
            model_name = "gemini-flash-lite"
        elif effort == "high":
            model_name = "gemini"
        else: # medium
            model_name = "gemini-flash"
        logger.info(f"Routing gemini (effort: {effort}) -> {model_name}")

    # 2. Логика переключения Codex (Hijacked Slot)
    if model_name == "codex":
        raw_data = request.model_dump()
        effort = raw_data.get("reasoning_effort", "medium")
        if effort == "low":
            model_name = "codex-low"
        elif effort == "high":
            model_name = "codex-high"
        logger.info(f"Routing codex (effort: {effort}) -> {model_name}")

    # 3. Маршрутизация по провайдерам
    route_info = settings.ROUTES.get(model_name)
    
    # Если модели нет в ROUTES, но она начинается на claude- -> проксируем в Anthropic
    if not route_info and model_name.startswith("claude-"):
        logger.info(f"Proxying {model_name} to Anthropic")
        if not request.stream:
            return await anthropic_client.proxy_request(request.model_dump(), headers)
        else:
            return handle_anthropic_streaming(request, headers)

    if not route_info:
        raise ValueError(f"Model {model_name} not found")

    provider = route_info.get("provider")

    if provider == "openai":
        openai_payload = openai_adapter.to_openai_request(request)
        openai_payload["model"] = route_info.get("model")
        if not request.stream:
            response_json = await openai_client.create_response(openai_payload)
            return openai_adapter.from_openai_response(response_json, request.model)
        else:
            return handle_streaming(request, provider, route_info, model_name)
            
    elif provider == "google":
        gemini_model = route_info.get("model")
        gemini_payload = gemini_adapter.to_gemini_request(request)
        if not request.stream:
            response_json = await gemini_client.generate_content(gemini_model, gemini_payload)
            return gemini_adapter.from_gemini_response(response_json, request.model)
        else:
            return handle_streaming(request, provider, route_info, model_name)

async def handle_anthropic_streaming(request: AnthropicMessagesRequest, headers: Dict[str, str]) -> AsyncGenerator[str, None]:
    async with await anthropic_client.proxy_request(request.model_dump(), headers, stream=True) as response:
        async for line in response.aiter_lines():
            if line:
                yield line + "\n"

async def handle_streaming(request: AnthropicMessagesRequest, provider: str, route_info: Dict[str, Any], model_id: str) -> AsyncGenerator[str, None]:
    yield message_start_event(model_id, f"msg_stream_local_cli_{model_id}")
    yield content_block_start_event(0)

    if provider == "openai":
        openai_payload = openai_adapter.to_openai_request(request)
        openai_payload["model"] = route_info.get("model")
        stdout_stream = await openai_client.create_response(openai_payload, stream=True)
        while True:
            line = await stdout_stream.readline()
            if not line: break
            text = line.decode(errors='replace')
            if text:
                yield content_block_delta_event(text)
                
    elif provider == "google":
        gemini_model = route_info.get("model")
        gemini_payload = gemini_adapter.to_gemini_request(request)
        stdout_stream = await gemini_client.generate_content(gemini_model, gemini_payload, stream=True)
        while True:
            line = await stdout_stream.readline()
            if not line: break
            text = line.decode(errors='replace')
            if text:
                yield content_block_delta_event(text)

    yield content_block_stop_event(0)
    yield message_delta_event()
    yield message_stop_event()

async def handle_count_tokens(request: AnthropicMessagesRequest, headers: Dict[str, str]) -> int:
    model_name = request.model
    if model_name == "gemini":
        raw_data = request.model_dump()
        effort = raw_data.get("reasoning_effort", "medium")
        model_name = "gemini-flash-lite" if effort == "low" else ("gemini" if effort == "high" else "gemini-flash")
    elif model_name == "codex":
        raw_data = request.model_dump()
        effort = raw_data.get("reasoning_effort", "medium")
        model_name = "codex-low" if effort == "low" else ("codex-high" if effort == "high" else "codex")

    route_info = settings.ROUTES.get(model_name)
    if not route_info and model_name.startswith("claude-"):
        return len(str(request.messages)) // 4

    provider = route_info.get("provider")
    if provider == "openai":
        openai_payload = openai_adapter.to_openai_request(request)
        openai_payload["model"] = route_info.get("model")
        response = await openai_client.count_tokens(openai_payload)
        return response.get("input_tokens", 0)
    elif provider == "google":
        gemini_model = route_info.get("model")
        gemini_payload = gemini_adapter.to_gemini_request(request)
        response = await gemini_client.count_tokens(gemini_model, gemini_payload)
        return response.get("totalTokens", 0)
    return 0
