#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: $0 [-u username] [-p password] [-t token] [--compose]
Prompts for any missing values and writes .env, installs dependencies,
runs alembic upgrade head, and optionally launches docker compose.
USAGE
}

ENV_FILE=".env"
COMPOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -u|--username)
      FETLIFE_USERNAME="$2"
      shift 2
      ;;
    -p|--password)
      FETLIFE_PASSWORD="$2"
      shift 2
      ;;
    -t|--token)
      DISCORD_TOKEN="$2"
      shift 2
      ;;
    --compose)
      COMPOSE=1
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
  local name="$1" default="${2-}"
  local val
  read -r -p "$name${default:+ [$default]}: " val
  if [[ -z "$val" ]]; then
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

if [[ ! -f "$ENV_FILE" ]]; then
  touch "$ENV_FILE"
  echo "Created $ENV_FILE"
fi

: "${FETLIFE_USERNAME:=$(prompt FETLIFE_USERNAME)}"
: "${FETLIFE_PASSWORD:=$(prompt FETLIFE_PASSWORD)}"
: "${DISCORD_TOKEN:=$(prompt DISCORD_TOKEN)}"

DB_HOST=$(prompt DB_HOST "localhost")
DB_PORT=$(prompt DB_PORT "5432")
DB_NAME=$(prompt DB_NAME "bot")
DB_USER=$(prompt DB_USER "bot")
DB_PASSWORD=$(prompt DB_PASSWORD)

write_env FETLIFE_USERNAME "$FETLIFE_USERNAME"
write_env FETLIFE_PASSWORD "$FETLIFE_PASSWORD"
write_env DISCORD_TOKEN "$DISCORD_TOKEN"
write_env DB_HOST "$DB_HOST"
write_env DB_PORT "$DB_PORT"
write_env DB_NAME "$DB_NAME"
write_env DB_USER "$DB_USER"
write_env DB_PASSWORD "$DB_PASSWORD"

echo "Installing Python dependencies..."
pip install -r requirements.txt

if command -v composer >/dev/null 2>&1; then
  echo "Installing PHP dependencies..."
  composer install --no-interaction
else
  echo "composer not found; skipping PHP dependencies."
fi

echo "Applying database migrations..."
alembic upgrade head

if [[ $COMPOSE -eq 1 ]]; then
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    echo "Starting services via docker compose..."
    docker compose up -d
  else
    echo "Docker Compose not available; skipping."
  fi
else
  read -r -p "Launch docker compose now? (y/N): " launch
  if [[ "$launch" =~ ^[Yy]$ ]]; then
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
      docker compose up -d
    else
      echo "Docker Compose not available; skipping."
    fi
  fi
fi

cat <<'EON'
Next steps:
1. Invite the bot via the Discord Developer Portal.
2. Run /fl login in your Discord server to verify connectivity.
3. Add subscriptions with /fl subscribe.
EON
