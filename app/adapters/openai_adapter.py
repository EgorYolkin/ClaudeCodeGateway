from typing import Dict, Any, List
from app.schemas import AnthropicMessagesRequest, AnthropicMessagesResponse, Usage, MessageContent
from app.settings import settings

class OpenAIAdapter:
    @staticmethod
    def to_openai_request(request: AnthropicMessagesRequest) -> Dict[str, Any]:
        route_info = settings.ROUTES.get(request.model, {})
        openai_model = route_info.get("model", "gpt-5.3-codex")
        reasoning_effort = route_info.get("reasoning_effort")

        messages = []
        
        # Handle complex system instruction
        system_text = ""
        if isinstance(request.system, str):
            system_text = request.system
        elif isinstance(request.system, list):
            system_text = " ".join([block.get("text", "") for block in request.system if isinstance(block, dict) and block.get("type") == "text"])
            
        if system_text:
            messages.append({"role": "system", "content": system_text})
        
        for msg in request.messages:
            content = msg.content
            if isinstance(content, list):
                # Simple text extraction for v1
                text_parts = []
                for c in content:
                    if isinstance(c, dict):
                        if c.get("type") == "text":
                            text_parts.append(c.get("text", ""))
                    elif hasattr(c, "type") and c.type == "text":
                        text_parts.append(getattr(c, "text", "") or "")
                content = " ".join(text_parts)
            messages.append({"role": msg.role, "content": content})

        payload = {
            "model": openai_model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "stream": request.stream
        }
        
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort
            
        return payload

    @staticmethod
    def from_openai_response(openai_res: Dict[str, Any], model_id: str) -> AnthropicMessagesResponse:
        # Assuming OpenAI Responses API output format
        # Usually choices[0].message.content
        choice = openai_res.get("choices", [{}])[0]
        message = choice.get("message", {})
        content_text = message.get("content", "")
        
        usage_data = openai_res.get("usage", {})
        usage = Usage(
            input_tokens=usage_data.get("prompt_tokens", 0),
            output_tokens=usage_data.get("completion_tokens", 0)
        )

        return AnthropicMessagesResponse(
            id=openai_res.get("id", "msg_local_openai"),
            model=model_id,
            content=[MessageContent(type="text", text=content_text)],
            usage=usage
        )

openai_adapter = OpenAIAdapter()
