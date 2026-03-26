import asyncio
import os

class OpenAIClient:
    def __init__(self):
        # Используем полный путь к бинарнику
        self.cli_cmd = "/opt/homebrew/bin/codex"

    @staticmethod
    def _build_prompt(messages: list[dict]) -> str:
        lines: list[str] = []
        for msg in messages:
            role = str(msg.get("role", "user")).upper()
            content = str(msg.get("content", ""))
            if content:
                lines.append(f"{role}: {content}")
        lines.append("ASSISTANT:")
        return "\n\n".join(lines)

    async def create_response(self, payload: dict, stream: bool = False):
        messages = payload.get("messages", [])
        prompt = self._build_prompt(messages)
        model = payload.get("model", "gpt-5.3-codex")
        effort = payload.get("reasoning_effort", "medium")

        # Формируем команду для CLI
        # Помощь показала: -c key=value для переопределения конфига
        # Модель через -m
        cmd = [self.cli_cmd, "-m", model, "-c", f"reasoning_effort=\"{effort}\"", "exec", prompt]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if stream:
            # Для CLI имитируем стриминг, читая строки по мере появления
            return process.stdout
        else:
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Codex CLI error: {stderr.decode()}")
            
            # Возвращаем структуру, похожую на ответ API для адаптера
            return {
                "id": f"codex_{os.urandom(4).hex()}",
                "choices": [{"message": {"content": stdout.decode().strip()}}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0} # CLI не всегда дает токены
            }

    async def count_tokens(self, payload: dict):
        prompt = self._build_prompt(payload.get("messages", []))
        return {"input_tokens": len(prompt) // 4}

openai_client = OpenAIClient()
