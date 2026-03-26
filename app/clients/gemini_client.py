import asyncio
import os
import time
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        # Команда системного CLI
        self.cli_cmd = "/opt/homebrew/bin/gemini"
        self.cli_workdir = os.getenv("CCG_CLI_WORKDIR", "/tmp")
        self._drain_tasks: set[asyncio.Task] = set()

    def _drain_stream(self, stream: asyncio.StreamReader | None) -> None:
        if stream is None:
            return

        async def _drain() -> None:
            while True:
                chunk = await stream.read(1024)
                if not chunk:
                    break

        task = asyncio.create_task(_drain())
        self._drain_tasks.add(task)
        task.add_done_callback(self._drain_tasks.discard)

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
        started_at = time.perf_counter()
        contents = payload.get("contents", [])
        prompt = self._build_prompt(contents)

        # Формируем команду для CLI: gemini -m model -p "текст"
        cmd = [self.cli_cmd, "-m", model, "-p", prompt]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cli_workdir,
        )
        
        if stream:
            self._drain_stream(process.stderr)
            logger.info(
                "gemini stream spawned prompt_chars=%s cwd=%s spawn_ms=%.1f",
                len(prompt),
                self.cli_workdir,
                (time.perf_counter() - started_at) * 1000,
            )
            return process.stdout
        else:
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Gemini CLI error: {stderr.decode()}")
            logger.info(
                "gemini nonstream prompt_chars=%s cwd=%s total_ms=%.1f",
                len(prompt),
                self.cli_workdir,
                (time.perf_counter() - started_at) * 1000,
            )
            
            return {
                "id": f"gemini_{os.urandom(4).hex()}",
                "candidates": [{"content": {"parts": [{"text": stdout.decode().strip()}]}}],
                "usageMetadata": {"promptTokenCount": 0, "candidatesTokenCount": 0}
            }

    async def count_tokens(self, model: str, payload: dict):
        prompt = self._build_prompt(payload.get("contents", []))
        return {"totalTokens": len(prompt) // 4}

gemini_client = GeminiClient()
