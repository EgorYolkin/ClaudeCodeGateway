#!/usr/bin/env bash
set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BRANCH="${CCG_BRANCH:-main}"
REPO_URL="${CCG_REPO_URL:-${CLAUDE_GATEWAY_REPO_URL:-https://github.com/EgorYolkin/ClaudeCodeGateway.git}}"
INSTALL_DIR="${CCG_INSTALL_DIR:-${CLAUDE_GATEWAY_DIR:-$HOME/.claude-code-gateway}}"

log() {
  printf "%b%s%b\n" "$BLUE" "$1" "$NC"
}

warn() {
  printf "%b%s%b\n" "$YELLOW" "$1" "$NC"
}

success() {
  printf "%b%s%b\n" "$GREEN" "$1" "$NC"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

ensure_env_key() {
  local env_file="$1"
  local current_key
  local key="${CCG_ANTHROPIC_API_KEY:-${ANTHROPIC_API_KEY:-}}"
  current_key="$(grep -E '^ANTHROPIC_API_KEY=' "$env_file" | sed 's/^ANTHROPIC_API_KEY=//' || true)"

  if [ -n "$current_key" ]; then
    return
  fi

  if [ -z "$key" ]; then
    warn "ANTHROPIC_API_KEY is missing in $env_file."

    if [ -r /dev/tty ] && [ -w /dev/tty ]; then
      printf "Enter ANTHROPIC_API_KEY (input hidden): " > /dev/tty
      IFS= read -r -s key < /dev/tty
      printf "\n" > /dev/tty
    else
      echo "ANTHROPIC_API_KEY is required for non-interactive install." >&2
      echo "Run with env var: ANTHROPIC_API_KEY=... bash <(curl -fsSL https://raw.githubusercontent.com/EgorYolkin/ClaudeCodeGateway/refs/heads/main/bootstrap.sh)" >&2
      exit 1
    fi
  fi

  if [ -z "${key:-}" ]; then
    echo "ANTHROPIC_API_KEY cannot be empty." >&2
    exit 1
  fi

  # Rewrite via awk to avoid sed replacement pitfalls with key chars like '&' and '\'.
  awk -v key="$key" '
    BEGIN { updated = 0 }
    /^ANTHROPIC_API_KEY=/ {
      print "ANTHROPIC_API_KEY=" key
      updated = 1
      next
    }
    { print }
    END {
      if (!updated) {
        print "ANTHROPIC_API_KEY=" key
      }
    }
  ' "$env_file" > "$env_file.tmp"
  mv "$env_file.tmp" "$env_file"
}

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This installer supports macOS only." >&2
  exit 1
fi

require_command git
require_command python3
require_command launchctl

log "Installing Claude Code Gateway into: $INSTALL_DIR"

if [ -d "$INSTALL_DIR/.git" ]; then
  log "Existing install found, updating repository..."
  git -C "$INSTALL_DIR" fetch origin "$BRANCH"
  git -C "$INSTALL_DIR" checkout "$BRANCH"
  git -C "$INSTALL_DIR" pull --ff-only origin "$BRANCH"
elif [ -d "$INSTALL_DIR" ] && [ "$(ls -A "$INSTALL_DIR" 2>/dev/null | wc -l | tr -d ' ')" -gt 0 ]; then
  echo "Directory exists and is not empty: $INSTALL_DIR" >&2
  echo "Set CLAUDE_GATEWAY_DIR to another path and retry." >&2
  exit 1
else
  log "Cloning repository..."
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp ".env.example" ".env"
fi

if [ ! -f ".env" ]; then
  : > ".env"
fi

ensure_env_key ".env"

chmod +x ./install.sh
./install.sh

success "Bootstrap complete."
echo "Gateway source path: $INSTALL_DIR"
