# Claude Code Gateway

A personal, lightweight gateway for Claude Code to route requests between OpenAI (GPT-5.3 Codex) and Google (Gemini 3.1) using the Anthropic-compatible API.

## Features

- **Anthropic-compatible endpoint** (`/v1/messages`).
- **Exact Token Counting** using provider native APIs.
- **Routing by Model ID**:
  - `codex-low`, `codex-medium`, `codex-high` -> OpenAI Responses API.
  - `gemini-pro`, `gemini-flash` -> Gemini API.

## Setup

1. **Create .env file**:
   ```bash
   OPENAI_API_KEY=your_openai_key
   GEMINI_API_KEY=your_gemini_key
   GATEWAY_AUTH_TOKEN=local-dev-token
   ```

2. **Run with Docker**:
   ```bash
   docker compose up -d
   ```

## Claude Code Configuration

### 1. Environment Variables

Set these in your shell before running `claude`:

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8080
export ANTHROPIC_AUTH_TOKEN=local-dev-token

export ANTHROPIC_DEFAULT_OPUS_MODEL=codex-high
export ANTHROPIC_DEFAULT_OPUS_MODEL_NAME="GPT-5.3 Codex High"
export ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION="Local gateway -> OpenAI Responses API"
export ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES="effort,max_effort"

export ANTHROPIC_DEFAULT_SONNET_MODEL=codex-medium
export ANTHROPIC_DEFAULT_SONNET_MODEL_NAME="GPT-5.3 Codex Medium"
export ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION="Local gateway -> OpenAI Responses API"
export ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTED_CAPABILITIES="effort,max_effort"

export ANTHROPIC_DEFAULT_HAIKU_MODEL=codex-low
export ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME="GPT-5.3 Codex Low"
export ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION="Local gateway -> OpenAI Responses API"
export ANTHROPIC_DEFAULT_HAIKU_MODEL_SUPPORTED_CAPABILITIES="effort,max_effort"

export ANTHROPIC_CUSTOM_MODEL_OPTION=gemini-pro
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Gemini 3.1 Pro Preview"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="Local gateway -> Gemini API"
```

### 2. settings.json (Claude Code)

To map the 5th model (Gemini Flash), update your Claude Code settings:

```json
{
  "modelOverrides": {
    "claude-opus-4-5-20251101": "gemini-flash"
  }
}
```

## Available Models in `/model`

- **Opus Slot**: GPT-5.3 Codex High
- **Sonnet Slot**: GPT-5.3 Codex Medium
- **Haiku Slot**: GPT-5.3 Codex Low
- **Custom Model**: Gemini 3.1 Pro Preview
- **Opus Override**: Gemini 3 Flash Preview
