import asyncio
import os
import time
import logging
import json
import httpx
from typing import AsyncGenerator
from app.settings import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        # Команда системного CLI
        self.cli_cmd = "/opt/homebrew/bin/gemini"
        self.cli_workdir = os.getenv("CCG_CLI_WORKDIR", "/tmp")
        self._drain_tasks: set[asyncio.Task] = set()
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.api_base = "https://generativelanguage.googleapis.com/v1beta/models"

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
        if self.api_key:
            if stream:
                raise ValueError("Use stream_content() for streaming Gemini API calls")
            started_at = time.perf_counter()
            url = f"{self.api_base}/{model}:generateContent?key={self.api_key}"
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info(
                "gemini api nonstream total_ms=%.1f model=%s",
                (time.perf_counter() - started_at) * 1000,
                model,
            )
            return response.json()

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

    async def stream_content(self, model: str, payload: dict) -> AsyncGenerator[str, None]:
        if self.api_key:
            started_at = time.perf_counter()
            url = f"{self.api_base}/{model}:streamGenerateContent?alt=sse&key={self.api_key}"
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if not data or data == "[DONE]":
                            continue
                        try:
                            chunk_json = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        parts = chunk_json.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                        text = "".join([str(part.get("text", "")) for part in parts if isinstance(part, dict)])
                        if text:
                            yield text
            logger.info(
                "gemini api stream completed total_ms=%.1f model=%s",
                (time.perf_counter() - started_at) * 1000,
                model,
            )
            return

        stdout_stream = await self.generate_content(model, payload, stream=True)
        while True:
            chunk = await stdout_stream.read(256)
            if not chunk:
                break
            text = chunk.decode(errors="replace")
            if text:
                yield text

    async def count_tokens(self, model: str, payload: dict):
        prompt = self._build_prompt(payload.get("contents", []))
        return {"totalTokens": len(prompt) // 4}

gemini_client = GeminiClient()
