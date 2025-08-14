#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=".env"

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
  if [[ -f "$ENV_FILE" ]] && grep -q "^${key}=" "$ENV_FILE"; then
    echo "$key already set in $ENV_FILE; skipping."
  else
    echo "$key=$value" >> "$ENV_FILE"
  fi
}

# Ensure .env exists
if [[ ! -f "$ENV_FILE" ]]; then
  if [[ -f ".env.example" ]]; then
    cp .env.example "$ENV_FILE"
    echo "Copied .env.example to $ENV_FILE"
  else
    touch "$ENV_FILE"
    echo "Created $ENV_FILE"
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

write_env FETLIFE_USERNAME "$FETLIFE_USERNAME"
write_env FETLIFE_PASSWORD "$FETLIFE_PASSWORD"
write_env DISCORD_TOKEN "$DISCORD_TOKEN"
write_env DB_HOST "$DB_HOST"
write_env DB_PORT "$DB_PORT"
write_env DB_NAME "$DB_NAME"
write_env DB_USER "$DB_USER"
write_env DB_PASSWORD "$DB_PASSWORD"

# Optionally create config.yaml
read -r -p "Create config.yaml? (y/N): " cfg
if [[ "$cfg" =~ ^[Yy]$ ]]; then
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
