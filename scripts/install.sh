#!/usr/bin/env bash
set -euo pipefail

ensure_gitignore() {
  if [[ ! -f .gitignore ]] || ! grep -qxF '.venv/' .gitignore; then
    echo '.venv/' >> .gitignore
  fi
}

install() {
  if [[ ! -d .venv ]]; then
    python3 -m venv .venv
  else
    echo ".venv already exists; using existing environment."
  fi
  # shellcheck source=/dev/null
  source .venv/bin/activate
  pip install -r requirements.lock -r requirements-dev.txt
}

reinstall() {
  if [[ -d .venv ]]; then
    read -r -p ".venv exists. Delete and reinstall? (y/N): " resp
    if [[ "$resp" =~ ^[Yy]$ ]]; then
      rm -rf .venv
      install
    else
      echo "Reinstall aborted."
    fi
  else
    install
  fi
}

uninstall() {
  if [[ -d .venv ]]; then
    read -r -p "Remove existing .venv? (y/N): " resp
    if [[ "$resp" =~ ^[Yy]$ ]]; then
      rm -rf .venv
      echo ".venv removed."
    else
      echo "Uninstall aborted."
    fi
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
