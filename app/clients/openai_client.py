import asyncio
import os

class OpenAIClient:
    def __init__(self):
        # Используем полный путь к бинарнику
        self.cli_cmd = "/opt/homebrew/bin/codex"

    async def create_response(self, payload: dict, stream: bool = False):
        # Извлекаем последний промпт из сообщений
        messages = payload.get("messages", [])
        prompt = messages[-1].get("content", "") if messages else ""
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
        # Если у CLI нет встроенного счетчика, возвращаем примерную длину
        # Или вызываем специфичную команду, если она есть
        prompt = payload.get("messages", [{}])[-1].get("content", "")
        return {"input_tokens": len(prompt) // 4}

openai_client = OpenAIClient()
