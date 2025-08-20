#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo "Refusing to run health check as root" >&2
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
    return 0
  else
    "$@"
  fi
}

retries=${HEALTH_RETRIES:-5}
interval=${HEALTH_INTERVAL:-2}

check() {
  local container=$1
  local url=$2
  local attempt=1
  until run docker-compose exec "$container" curl -fsS -o /dev/null "$url"; do
    if (( attempt >= retries )); then
      echo "health check failed: $container $url" >&2
      return 1
    fi
    attempt=$((attempt + 1))
    sleep "$interval"
  done
}

check bot http://localhost:8000/ready
check bot http://localhost:8000/metrics
check adapter http://localhost:8000/healthz
check adapter http://localhost:8000/metrics

echo "health checks passed"
