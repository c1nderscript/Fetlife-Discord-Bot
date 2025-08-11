#!/usr/bin/env bash
set -euo pipefail

# Ensure development spec exists
if [ ! -f Agents.md ]; then
  echo "Agents.md missing" >&2
  exit 1
fi

# Example drift check
if grep -q "pnpm" Agents.md && ! grep -Rq "pnpm" .; then
  echo "Agents.md mentions pnpm but repo doesn't use it." >&2
  exit 1
fi

# Verify tool references
if grep -qi "docker" Agents.md; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "Agents.md references docker but docker is not installed." >&2
    exit 1
  fi
fi

if grep -qi "make check" Agents.md; then
  if ! command -v make >/dev/null 2>&1; then
    echo "Agents.md references make but make is not installed." >&2
    exit 1
  fi
  if ! grep -qE '^check:' Makefile; then
    echo "Agents.md references make check but no 'check' target found in Makefile." >&2
    exit 1
  fi
fi

if grep -qi "flake8" Agents.md; then
  if ! command -v flake8 >/dev/null 2>&1; then
    echo "Agents.md references flake8 but flake8 is not installed." >&2
    exit 1
  fi
fi

if grep -qi "phpunit" Agents.md; then
  if command -v phpunit >/dev/null 2>&1 || [ -f vendor/bin/phpunit ]; then
    :
  else
    echo "Agents.md references phpunit but phpunit is not installed." >&2
    exit 1
  fi
fi

if grep -qi "phpstan" Agents.md; then
  if command -v phpstan >/dev/null 2>&1 || [ -f vendor/bin/phpstan ]; then
    :
  else
    echo "Agents.md references phpstan but phpstan is not installed." >&2
    exit 1
  fi
fi

echo "Agents.md passes basic drift check."
