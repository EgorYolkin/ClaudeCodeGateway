import asyncio
import os

class GeminiClient:
    def __init__(self):
        # Команда системного CLI
        self.cli_cmd = "/opt/homebrew/bin/gemini"

    @staticmethod
    def _build_prompt(contents: list[dict]) -> str:
        lines: list[str] = []
        for item in contents:
            role = str(item.get("role", "user")).upper()
            parts = item.get("parts", [])
            text = ""
            if parts and isinstance(parts, list):
                text = str(parts[0].get("text", ""))
            if text:
                lines.append(f"{role}: {text}")
        lines.append("MODEL:")
        return "\n\n".join(lines)

    async def generate_content(self, model: str, payload: dict, stream: bool = False):
        contents = payload.get("contents", [])
        prompt = self._build_prompt(contents)

        # Формируем команду для CLI: gemini -m model -p "текст"
        cmd = [self.cli_cmd, "-m", model, "-p", prompt]
        
        stderr_target = asyncio.subprocess.STDOUT if stream else asyncio.subprocess.PIPE

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=stderr_target
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
        prompt = self._build_prompt(payload.get("contents", []))
        return {"totalTokens": len(prompt) // 4}

gemini_client = GeminiClient()
