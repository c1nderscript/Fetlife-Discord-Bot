#!/usr/bin/env bash
set -euo pipefail

confirm=false
if [[ "${1:-}" == "--confirm" ]]; then
  confirm=true
  shift
fi

cmd="${1:-help}"

dry_run=true
$confirm && dry_run=false

# Allow a limited command set when running as root to prevent destructive actions.
# Unsafe commands exit immediately; safe ones continue after a warning.
safe_root_cmds=(fast-validate daemon:status)
if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  if [[ " ${safe_root_cmds[*]} " == *" ${cmd} "* ]]; then
    echo "Warning: running '${cmd}' as root" >&2
  else
    echo "Refusing to run '${cmd}' as root" >&2
    exit 1
  fi
fi

run() {
  if $dry_run; then
    printf '[dry-run] %q ' "$@"
    echo
  else
    "$@"
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
