# Claude Code Gateway

[English](README.md) | [Русский](README.ru.md)

![Example Setup](resources/example.jpg)

A personal, lightweight gateway for **Claude Code**. It lets you use Anthropic models together with **OpenAI GPT-5.3 Codex** and **Google Gemini 3.1** from one place.

## Start Here (For Complete Beginners)

If you are new and just want it working, run one command in Terminal:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/EgorYolkin/ClaudeCodeGateway/refs/heads/main/bootstrap.sh)
```

Then follow the prompts. If asked, paste your `ANTHROPIC_API_KEY`.

After install finishes:

```bash
source ~/.zshrc
claude
```

That is all.

## Quick Check

- Open Claude Code and run `/model`
- You should see:
  - Sonnet (Original)
  - Opus (Original)
  - GPT-5.3 Codex (Haiku slot)
  - Gemini 3.1 (Custom slot)

## Features

- macOS native `LaunchAgent` setup (no Docker required)
- Hybrid routing to Anthropic + Codex CLI + Gemini CLI
- Effort-aware model behavior for Codex and Gemini
- Local gateway with token/accounting logic

## Model Mapping

| Slot in Claude Code | Model Provided | Backend |
| :--- | :--- | :--- |
| Sonnet | Claude 3.5 Sonnet | Anthropic Proxy |
| Opus | Claude 3 Opus | Anthropic Proxy |
| Haiku (renamed) | GPT-5.3 Codex | `codex` CLI |
| Custom (Item 5) | Gemini 3.1 | `gemini` CLI |

## Installation Options

### Recommended

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/EgorYolkin/ClaudeCodeGateway/refs/heads/main/bootstrap.sh)
```

### Manual

```bash
git clone git@github.com:EgorYolkin/ClaudeCodeGateway.git
cd ClaudeCodeGateway
chmod +x install.sh
./install.sh
```

## Configuration Notes

- Local URL: `http://127.0.0.1:8080`
- Logs: `/tmp/claude-gateway.log`
- Errors: `/tmp/claude-gateway.err`
- LaunchAgent plist: `~/Library/LaunchAgents/com.user.claude-gateway.plist`

Useful env overrides for bootstrap:

- `CCG_INSTALL_DIR` — custom install path
- `CCG_BRANCH` — install a non-main branch
- `CCG_REPO_URL` — custom repository URL

## Troubleshooting

If something does not start:

1. Check logs in `/tmp/claude-gateway.err`
2. Verify `.env` contains `ANTHROPIC_API_KEY`
3. Reload shell: `source ~/.zshrc`
4. Re-run install script

## Project Docs

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Support](SUPPORT.md)

## License

No license file is currently published in this repository.
