from typing import Dict, Any, List, Optional
from app.schemas import AnthropicMessagesRequest, AnthropicMessagesResponse, Usage, MessageContent

class OpenAIAdapter:
    @staticmethod
    def _is_internal_claude_system_text(text: str) -> bool:
        markers = [
            "x-anthropic-billing-header:",
            "You are Claude Code, Anthropic's official CLI for Claude.",
            "IMPORTANT: Assist with authorized security testing",
        ]
        return any(marker in text for marker in markers)

    @staticmethod
    def _extract_text_content(content: Any) -> str:
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts: List[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif hasattr(item, "type") and getattr(item, "type", None) == "text":
                    text_parts.append(getattr(item, "text", "") or "")
            return " ".join([part for part in text_parts if part])

        return str(content)

    @staticmethod
    def to_openai_request(
        request: AnthropicMessagesRequest,
        route_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        route_info = route_info or {}
        openai_model = route_info.get("model", request.model)
        reasoning_effort = route_info.get("reasoning_effort")

        messages: List[Dict[str, str]] = []
        
        system_text = ""
        if isinstance(request.system, str):
            system_text = request.system
        elif isinstance(request.system, list):
            system_text = " ".join([block.get("text", "") for block in request.system if isinstance(block, dict) and block.get("type") == "text"])
            
        if system_text and not OpenAIAdapter._is_internal_claude_system_text(system_text):
            messages.append({"role": "system", "content": system_text})
        
        for msg in request.messages:
            content_text = OpenAIAdapter._extract_text_content(msg.content)
            messages.append({"role": msg.role, "content": content_text})

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
