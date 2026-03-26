#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Claude Code Gateway Hybrid Installer (macOS) ===${NC}"

# 1. Проверка ANTHROPIC_API_KEY (только он нужен в .env для прокси)
if [ ! -f .env ] || ! grep -q "ANTHROPIC_API_KEY" .env; then
    echo -e "${BLUE}Настройка прокси для оригинальных моделей Claude...${NC}"
    read -p "Введите Anthropic API Key (для Sonnet/Opus/Haiku): " anthropic_key
    echo "ANTHROPIC_API_KEY=$anthropic_key" >> .env
    echo "GATEWAY_AUTH_TOKEN=local-dev-token" >> .env
fi

# 2. Настройка виртуального окружения
if [ ! -d venv ]; then
    python3 -m venv venv
fi
./venv/bin/pip install -r requirements.txt

# 3. Настройка LaunchAgent
PLIST_PATH="$HOME/Library/LaunchAgents/com.user.claude-gateway.plist"
cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.claude-gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/venv/bin/python3</string>
        <string>-m</string>
        <string>uvicorn</string>
        <string>app.main:app</string>
        <string>--host</string>
        <string>127.0.0.1</string>
        <string>--port</string>
        <string>8080</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>StandardOutPath</key>
    <string>/tmp/claude-gateway.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/claude-gateway.err</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH</string>
        <key>ANTHROPIC_API_KEY</key>
        <string>$(grep ANTHROPIC_API_KEY .env | cut -d'=' -f2)</string>
    </dict>
</dict>
</plist>
EOF

launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

# 4. Настройка переменных окружения
ENV_SCRIPT_PATH="$HOME/.claude_gateway_env"
cat <<EOF > "$ENV_SCRIPT_PATH"
# Claude Code Gateway Hybrid Environment
export ANTHROPIC_BASE_URL=http://127.0.0.1:8080
export ANTHROPIC_AUTH_TOKEN=local-dev-token

# Default слот отдаем под Codex
export ANTHROPIC_DEFAULT_SONNET_MODEL=codex
export ANTHROPIC_DEFAULT_SONNET_MODEL_NAME="GPT-5.3 Codex"

export ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION="Local gateway -> OpenAI Codex CLI"
export ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTED_CAPABILITIES="effort,max_effort"

# Custom слот (пункт 5) отдаем под Gemini
export ANTHROPIC_CUSTOM_MODEL_OPTION=gemini
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Gemini 3.1"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="Local gateway -> Gemini CLI (Effort logic)"
EOF

SHELL_PROFILE="$HOME/.zshrc"
[ ! -f "$SHELL_PROFILE" ] && SHELL_PROFILE="$HOME/.bash_profile"
if ! grep -q "source $ENV_SCRIPT_PATH" "$SHELL_PROFILE"; then
    echo "" >> "$SHELL_PROFILE"
    echo "source $ENV_SCRIPT_PATH" >> "$SHELL_PROFILE"
fi

# 5. Очистка оверрайдов для Opus и Haiku в Claude Code
CONFIG_PATHS=("$HOME/.claude/settings.json" "$HOME/.claudecode/settings.json")
for P in "${CONFIG_PATHS[@]}"; do
    if [ -f "$P" ]; then
        python3 -c "
import json
path = '$P'
with open(path, 'r') as f:
    try: data = json.load(f)
    except: data = {}
if 'modelOverrides' in data:
    # Удаляем оверрайды для Opus и Haiku, чтобы они стали стандартными
    data['modelOverrides'].pop('claude-3-opus-20240229', None)
    data['modelOverrides'].pop('claude-3-haiku-20240307', None)
    data['modelOverrides'].pop('claude-3-5-sonnet-latest', None)
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
"
    fi
done

echo -e "\n${GREEN}=== Гибридная установка завершена! ===${NC}"
echo -e "Выполни: ${BLUE}source $SHELL_PROFILE${NC} и затем ${BLUE}claude${NC}"
