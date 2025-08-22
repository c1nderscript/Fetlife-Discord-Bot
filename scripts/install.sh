#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=1

usage() {
  cat <<'USAGE'
Usage: scripts/install.sh [--confirm] [--dry-run] [--help]

Options:
  --dry-run   Print actions without executing (default)
  --confirm   Execute install, reinstall, and uninstall operations
  -h, --help  Show this help message
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --confirm) DRY_RUN=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
  shift
done

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Running in dry-run mode. Use --confirm to perform actions."
fi

run_cmd() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'DRY RUN:'
    for arg in "$@"; do
      printf ' %q' "$arg"
    done
    echo
  else
    "$@"
  fi
}

ensure_gitignore() {
  if [[ ! -f .gitignore ]] || ! grep -qxF '.venv/' .gitignore; then
    run_cmd bash -c "echo '.venv/' >> .gitignore"
  fi
}

install() {
  if [[ ! -d .venv ]]; then
    run_cmd python3 -m venv .venv
  else
    echo ".venv already exists; using existing environment."
  fi
  run_cmd bash -c "source .venv/bin/activate && pip install -r requirements.lock -r requirements-dev.txt"
}

reinstall() {
  if [[ -d .venv ]]; then
    run_cmd rm -rf .venv
  fi
  install
}

uninstall() {
  if [[ -d .venv ]]; then
    run_cmd rm -rf .venv
    echo ".venv removed."
  else
    echo "No .venv found."
  fi
}

ensure_gitignore

PS3='Select an option: '
select opt in Install Reinstall Uninstall Exit; do
  case "$opt" in
    Install)
      install
      ;;
    Reinstall)
      reinstall
      ;;
    Uninstall)
      uninstall
      ;;
    Exit)
      break
      ;;
    *)
      echo "Invalid option"
      ;;
  esac
  echo
done
