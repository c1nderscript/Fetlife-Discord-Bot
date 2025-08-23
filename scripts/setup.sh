#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=".env"

usage() {
  cat <<'EOF'
Usage: $0 [--dry-run|--confirm]
Gather credentials, optionally create config.yaml, apply migrations, and start the bot.
Defaults to --dry-run and prints actions without changing files. Pass --confirm to apply changes.
EOF
}

DRY_RUN=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --confirm)
      DRY_RUN=0
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

prompt() {
  local msg="$1" default="${2-}"
  local val
  read -r -p "$msg" val
  if [[ -z "$val" && -n "$default" ]]; then
    val="$default"
  fi
  printf '%s' "$val"
}

write_env() {
  local key="$1" value="$2"
  if (( DRY_RUN )); then
    echo "Would write $key=$value to $ENV_FILE"
    return
  fi
  if [[ -f "$ENV_FILE" ]] && grep -q "^${key}=" "$ENV_FILE"; then
    echo "$key already set in $ENV_FILE; skipping."
  else
    echo "$key=$value" >> "$ENV_FILE"
  fi
}

current_env() {
  local key="$1"
  if [[ -f "$ENV_FILE" ]] && grep -q "^${key}=" "$ENV_FILE"; then
    grep "^${key}=" "$ENV_FILE" | cut -d'=' -f2-
  fi
}

# Ensure .env exists
if [[ ! -f "$ENV_FILE" ]]; then
  if (( DRY_RUN )); then
    if [[ -f ".env.example" ]]; then
      echo "Would copy .env.example to $ENV_FILE"
    else
      echo "Would create $ENV_FILE"
    fi
  else
    if [[ -f ".env.example" ]]; then
      cp .env.example "$ENV_FILE"
      echo "Copied .env.example to $ENV_FILE"
    else
      touch "$ENV_FILE"
      echo "Created $ENV_FILE"
    fi
  fi
fi

# Gather credentials and DB parameters
FETLIFE_USERNAME=$(prompt "FETLIFE_USERNAME: ")
FETLIFE_PASSWORD=$(prompt "FETLIFE_PASSWORD: ")
DISCORD_TOKEN=$(prompt "DISCORD_TOKEN: ")
DB_HOST=$(prompt "DB_HOST [localhost]: " "localhost")
DB_PORT=$(prompt "DB_PORT [5432]: " "5432")
DB_NAME=$(prompt "DB_NAME [bot]: " "bot")
DB_USER=$(prompt "DB_USER [bot]: " "bot")
DB_PASSWORD=$(prompt "DB_PASSWORD: ")

ADAPTER_AUTH_TOKEN_DEFAULT=$(current_env ADAPTER_AUTH_TOKEN)
ADAPTER_AUTH_TOKEN=$(prompt "ADAPTER_AUTH_TOKEN [${ADAPTER_AUTH_TOKEN_DEFAULT}]: " "$ADAPTER_AUTH_TOKEN_DEFAULT")
ADAPTER_BASE_URL_DEFAULT=$(current_env ADAPTER_BASE_URL)
ADAPTER_BASE_URL=$(prompt "ADAPTER_BASE_URL [${ADAPTER_BASE_URL_DEFAULT}]: " "$ADAPTER_BASE_URL_DEFAULT")
TELEGRAM_API_ID_DEFAULT=$(current_env TELEGRAM_API_ID)
TELEGRAM_API_ID=$(prompt "TELEGRAM_API_ID [${TELEGRAM_API_ID_DEFAULT}]: " "$TELEGRAM_API_ID_DEFAULT")
TELEGRAM_API_HASH_DEFAULT=$(current_env TELEGRAM_API_HASH)
TELEGRAM_API_HASH=$(prompt "TELEGRAM_API_HASH [${TELEGRAM_API_HASH_DEFAULT}]: " "$TELEGRAM_API_HASH_DEFAULT")

write_env FETLIFE_USERNAME "$FETLIFE_USERNAME"
write_env FETLIFE_PASSWORD "$FETLIFE_PASSWORD"
write_env DISCORD_TOKEN "$DISCORD_TOKEN"
write_env DB_HOST "$DB_HOST"
write_env DB_PORT "$DB_PORT"
write_env DB_NAME "$DB_NAME"
write_env DB_USER "$DB_USER"
write_env DB_PASSWORD "$DB_PASSWORD"
write_env ADAPTER_AUTH_TOKEN "$ADAPTER_AUTH_TOKEN"
write_env ADAPTER_BASE_URL "$ADAPTER_BASE_URL"
write_env TELEGRAM_API_ID "$TELEGRAM_API_ID"
write_env TELEGRAM_API_HASH "$TELEGRAM_API_HASH"

# Optionally create config.yaml
read -r -p "Create config.yaml? (y/N): " cfg
if [[ "$cfg" =~ ^[Yy]$ ]]; then
  if (( DRY_RUN )); then
    if [[ -f "config.yaml" ]]; then
      echo "Would leave existing config.yaml as is"
    else
      echo "Would write config.yaml"
    fi
  else
    if [[ -f "config.yaml" ]]; then
      echo "config.yaml already exists; leaving as is."
    else
      cat > config.yaml <<'EOC'
# Default settings applied to all channels
defaults:
  thread_per_event: false
EOC
      echo "Wrote config.yaml"
    fi
  fi
fi

if (( DRY_RUN )); then
  echo "Would export environment from $ENV_FILE"
  echo "Would apply database migrations"
  echo "Would start bot"
  exit 0
fi

# Export environment
set -a
source "$ENV_FILE"
set +a

echo "Applying database migrations..."
alembic upgrade head

trap 'echo "Interrupt received, shutting down..."; kill $BOT_PID 2>/dev/null; wait $BOT_PID 2>/dev/null; exit 0' INT

echo "Starting bot. Press Ctrl-C to stop."
python -m bot.main &
BOT_PID=$!
wait $BOT_PID
