#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

if command -v docker-compose >/dev/null 2>&1; then
  compose="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  compose="docker compose"
else
  echo "docker-compose is required" >&2
  exit 1
fi

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo "Warning: running DR validation as root" >&2
fi

service="${1:-bot}"
if [[ ! "$service" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "invalid service name" >&2
  exit 1
fi

$compose up -d "$service" >/dev/null
$compose stop "$service" >/dev/null || true
$compose up -d "$service" >/dev/null

for _ in {1..30}; do
  if curl -fsS http://localhost:8000/ready >/dev/null 2>&1; then
    echo "Service recovered"
    exit 0
  fi
  sleep 1
done

echo "Service failed to recover" >&2
exit 1
