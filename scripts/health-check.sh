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
  else
    "$@"
  fi
}

run docker-compose exec bot curl -fsS -o /dev/null http://localhost:8000/ready
run docker-compose exec bot curl -fsS -o /dev/null http://localhost:8000/metrics
run docker-compose exec adapter curl -fsS -o /dev/null http://localhost:8000/healthz
run docker-compose exec adapter curl -fsS -o /dev/null http://localhost:8000/metrics

echo "health checks passed"
