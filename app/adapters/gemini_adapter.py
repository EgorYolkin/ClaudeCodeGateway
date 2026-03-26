from typing import Dict, Any, List
from app.schemas import AnthropicMessagesRequest, AnthropicMessagesResponse, Usage, MessageContent
from app.settings import settings

class GeminiAdapter:
    @staticmethod
    def to_gemini_request(request: AnthropicMessagesRequest) -> Dict[str, Any]:
        contents = []
        for msg in request.messages:
            role = "user" if msg.role == "user" else "model"
            content_val = msg.content
            if isinstance(content_val, list):
                # Simple text extraction for v1
                text_parts = []
                for c in content_val:
                    if isinstance(c, dict):
                        if c.get("type") == "text":
                            text_parts.append(c.get("text", ""))
                    elif hasattr(c, "type") and c.type == "text":
                        text_parts.append(getattr(c, "text", "") or "")
                content_val = " ".join(text_parts)
            contents.append({"role": role, "parts": [{"text": content_val}]})

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
            
            if system_text:
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
