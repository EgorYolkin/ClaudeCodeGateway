from typing import Dict, Any, List
from app.schemas import AnthropicMessagesRequest, AnthropicMessagesResponse, Usage, MessageContent
from app.settings import settings

class GeminiAdapter:
    MAX_HISTORY_MESSAGES = 16
    MAX_HISTORY_CHARS = 12000

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
    def _sanitize_message_text(text: str) -> str:
        noise_markers = (
            "mcp:",
            "mcp startup:",
            "OpenAI Codex v",
            "Keychain initialization encountered an error",
            "Using FileKeychain fallback for secure storage.",
            "Loaded cached credentials.",
            "session id:",
            "workdir:",
            "provider:",
            "approval:",
            "sandbox:",
            "reasoning effort:",
            "tokens used",
        )
        lines = [line for line in text.splitlines() if not line.strip().startswith(noise_markers)]
        return "\n".join(lines).strip()

    @staticmethod
    def _build_contents(request: AnthropicMessagesRequest) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for msg in request.messages:
            role = "user" if msg.role == "user" else "model"
            text = GeminiAdapter._sanitize_message_text(GeminiAdapter._extract_text_content(msg.content))
            if text:
                normalized.append({"role": role, "parts": [{"text": text}]})

        selected: List[Dict[str, Any]] = []
        total_chars = 0
        for msg in reversed(normalized):
            text = msg["parts"][0]["text"]
            msg_len = len(text)
            if selected and (
                len(selected) >= GeminiAdapter.MAX_HISTORY_MESSAGES
                or total_chars + msg_len > GeminiAdapter.MAX_HISTORY_CHARS
            ):
                break
            selected.append(msg)
            total_chars += msg_len
        selected.reverse()
        return selected

    @staticmethod
    def to_gemini_request(request: AnthropicMessagesRequest) -> Dict[str, Any]:
        contents = GeminiAdapter._build_contents(request)

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": request.max_tokens,
                "temperature": request.temperature,
                "topP": request.top_p,
                "topK": request.top_k,
            }
        }
        
        if request.system:
            system_text = ""
            if isinstance(request.system, str):
                system_text = request.system
            elif isinstance(request.system, list):
                system_text = " ".join([block.get("text", "") for block in request.system if isinstance(block, dict) and block.get("type") == "text"])
            
            if system_text and not GeminiAdapter._is_internal_claude_system_text(system_text):
                payload["systemInstruction"] = {"parts": [{"text": system_text}]}
            
        return payload

    @staticmethod
    def from_gemini_response(gemini_res: Dict[str, Any], model_id: str) -> AnthropicMessagesResponse:
        # Assuming Gemini generateContent output format
        # candidates[0].content.parts[0].text
        candidate = gemini_res.get("candidates", [{}])[0]
        content_part = candidate.get("content", {}).get("parts", [{}])[0]
        content_text = content_part.get("text", "")
        
        # Usage metadata
        usage_metadata = gemini_res.get("usageMetadata", {})
        usage = Usage(
            input_tokens=usage_metadata.get("promptTokenCount", 0),
            output_tokens=usage_metadata.get("candidatesTokenCount", 0)
        )

        return AnthropicMessagesResponse(
            id=gemini_res.get("id", "msg_local_gemini"),
            model=model_id,
            content=[MessageContent(type="text", text=content_text)],
            usage=usage
        )

gemini_adapter = GeminiAdapter()
