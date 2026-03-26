import asyncio
import os

class GeminiClient:
    def __init__(self):
        # Команда системного CLI
        self.cli_cmd = "/opt/homebrew/bin/gemini"

    async def generate_content(self, model: str, payload: dict, stream: bool = False):
        # Извлекаем промпт
        contents = payload.get("contents", [])
        prompt = contents[-1].get("parts", [{}])[0].get("text", "") if contents else ""

        # Формируем команду для CLI: gemini -m model -p "текст"
        cmd = [self.cli_cmd, "-m", model, "-p", prompt]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if stream:
            # Читаем стрим напрямую
            return process.stdout
        else:
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Gemini CLI error: {stderr.decode()}")
            
            return {
                "id": f"gemini_{os.urandom(4).hex()}",
                "candidates": [{"content": {"parts": [{"text": stdout.decode().strip()}]}}],
                "usageMetadata": {"promptTokenCount": 0, "candidatesTokenCount": 0}
            }

    async def count_tokens(self, model: str, payload: dict):
        # Аналогично OpenAI, или через спец флаг если есть в CLI
        prompt = payload.get("contents", [{}])[-1].get("parts", [{}])[0].get("text", "")
        return {"totalTokens": len(prompt) // 4}

gemini_client = GeminiClient()
