# Claude Code Gateway

A personal, lightweight gateway for **Claude Code** that enables a hybrid environment: original Anthropic models side-by-side with **OpenAI GPT-5.3 Codex** and **Google Gemini 3.1** via their respective system CLIs.

![Example Setup](resources/example.jpg)

## 🚀 Key Features

- **macOS Native**: Runs as a `LaunchAgent` (no Docker required), allowing direct access to your system CLI tools (`codex`, `gemini`).
- **Hybrid Routing**:
  - **Claude 3.5 Sonnet & Opus 3**: Proxied directly to Anthropic API.
  - **GPT-5.3 Codex**: Occupies the **Haiku** slot (renamed in menu) with full **Effort Slider** support.
  - **Gemini 3.1**: Occupies the **Custom Model** slot (Item 5) with Effort-based switching (Lite/Flash/Pro).
- **CLI Wrappers**: Leverages your existing authenticated CLI sessions for OpenAI and Google models.
- **Accurate Token Counting**: Uses provider-specific logic for precise usage tracking.

## 🛠 Model Mapping

| Slot in Claude Code | Model Provided | Backend |
| :--- | :--- | :--- |
| **Sonnet** | Claude 3.5 Sonnet | Anthropic Proxy |
| **Opus** | Claude 3 Opus | Anthropic Proxy |
| **Haiku** (Renamed) | **GPT-5.3 Codex** | `codex cli` (effort logic) |
| **Custom (Item 5)** | **Gemini 3.1** | `gemini cli` (effort logic) |

### Gemini Effort Logic:
- **Low Effort** ➔ Gemini 3 Flash Lite
- **Medium Effort** ➔ Gemini 3 Flash
- **High Effort** ➔ Gemini 3.1 Pro

## 📦 Installation (macOS)

1. **One-command install (recommended)**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/EgorYolkin/ClaudeCodeGateway/main/bootstrap.sh | bash
   ```

2. **Reload your shell**:
   ```bash
   source ~/.zshrc
   ```

3. **Start Claude Code**:
   ```bash
   claude
   ```

### Manual install (alternative)

```bash
git clone git@github.com:EgorYolkin/ClaudeCodeGateway.git
cd ClaudeCodeGateway
chmod +x install.sh
./install.sh
```

Notes:
- Default bootstrap install path: `~/.claude-code-gateway`
- Override install path: `CCG_INSTALL_DIR=~/my-gateway curl -fsSL https://raw.githubusercontent.com/EgorYolkin/ClaudeCodeGateway/main/bootstrap.sh | bash`
- Override branch: `CCG_BRANCH=dev curl -fsSL https://raw.githubusercontent.com/EgorYolkin/ClaudeCodeGateway/main/bootstrap.sh | bash`

## ⚙️ Configuration

The gateway runs locally on `http://127.0.0.1:8080`. 
- **Logs**: `/tmp/claude-gateway.log`
- **Errors**: `/tmp/claude-gateway.err`
- **Agent Config**: `~/Library/LaunchAgents/com.user.claude-gateway.plist`

## 🤝 Contributing

Feel free to open issues or PRs in the `dev` branch.
