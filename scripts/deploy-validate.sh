#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo "Refusing to run deploy validation as root" >&2
  exit 1
fi

confirm=false
if [[ "${1:-}" == "--confirm" ]]; then
  confirm=true
  shift
fi

dry_run=true
$confirm && dry_run=false

run() {
  if $dry_run; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

missing=false
for var in SESSION_SECRET ADAPTER_AUTH_TOKEN ADMIN_IDS DATABASE_URL ADAPTER_BASE_URL; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing required env var: $var" >&2
    missing=true
  fi
done
if $missing; then
  exit 1
fi

if [[ $ADAPTER_BASE_URL != https://* ]]; then
  echo "ADAPTER_BASE_URL must start with https://" >&2
  exit 1
fi

check_endpoint() {
  local url=$1
  shift || true
  local args=("$@")
  local max=5
  local attempt=1
  while (( attempt <= max )); do
    if $dry_run; then
      echo "[dry-run] curl -fsS -o /dev/null -w \"%{http_code}\" ${args[*]} \"$url\""
      return 0
    fi
    status=$(curl -fsS -o /dev/null -w "%{http_code}" "${args[@]}" "$url" || true)
    if [[ "$status" == 200 ]]; then
      return 0
    fi
    sleep $((attempt))
    attempt=$((attempt + 1))
  done
  echo "Endpoint $url failed after $max attempts" >&2
  return 1
}

check_endpoint "$ADAPTER_BASE_URL/healthz"
check_endpoint "$ADAPTER_BASE_URL/login" -H "Authorization: Bearer $ADAPTER_AUTH_TOKEN"

run psql "$DATABASE_URL" -c 'select 1' >/dev/null

cert_path=${TLS_CERT_PATH:-certs/tls.crt}
if [[ ! -f "$cert_path" ]]; then
  echo "TLS certificate not found at $cert_path" >&2
  exit 1
fi

echo "deploy validation passed"
