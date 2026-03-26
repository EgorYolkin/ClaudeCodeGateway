import httpx
from app.settings import settings

class AnthropicClient:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY # Мы добавим отдельный ключ в .env или используем этот
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def proxy_request(self, payload: dict, headers: dict, stream: bool = False):
        # Очищаем заголовки для передачи в Anthropic
        clean_headers = {
            "x-api-key": headers.get("x-api-key") or os.getenv("ANTHROPIC_API_KEY", ""),
            "anthropic-version": headers.get("anthropic-version", "2023-06-01"),
            "content-type": "application/json"
        }
        if headers.get("anthropic-beta"):
            clean_headers["anthropic-beta"] = headers.get("anthropic-beta")

        async with httpx.AsyncClient(timeout=120.0) as client:
            if not stream:
                response = await client.post(self.base_url, headers=clean_headers, json=payload)
                return response.json()
            else:
                # Для стриминга пробрасываем поток напрямую
                return client.stream("POST", self.base_url, headers=clean_headers, json=payload)

anthropic_client = AnthropicClient()
