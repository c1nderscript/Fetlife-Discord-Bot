#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo "Refusing to run as root" >&2
  exit 1
fi

confirm=false
if [[ "${1:-}" == "--confirm" ]]; then
  confirm=true
  shift
fi

cmd="${1:-help}"

dry_run=true
$confirm && dry_run=false

run() {
  if $dry_run; then
    echo "[dry-run] $*"
  else
    eval "$@"
  fi
}

case "$cmd" in
  bootstrap)
    run echo bootstrap
    ;;
  fast-validate)
    run echo fast-validate
    ;;
  cache-warm)
    run echo cache-warm
    ;;
  daemon:status)
    run echo daemon status
    ;;
  daemon:start)
    run echo daemon start
    ;;
  daemon:stop)
    run echo daemon stop
    ;;
  codex:repair)
    run echo codex repair
    ;;
  *)
    echo "Usage: $0 [--confirm] <bootstrap|fast-validate|cache-warm|daemon:{status|start|stop}|codex:repair>" >&2
    exit 1
    ;;
 esac
