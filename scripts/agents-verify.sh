#!/usr/bin/env bash
set -euo pipefail

# Ensure development spec exists
if [ ! -f AGENTS.md ]; then
  echo "AGENTS.md missing" >&2
  exit 1
fi

# Example drift check
if grep -q "pnpm" AGENTS.md && ! grep -Rq "pnpm" .; then
  echo "AGENTS.md mentions pnpm but repo doesn't use it." >&2
  exit 1
fi

# Verify tool references
if grep -qi "docker" AGENTS.md; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "AGENTS.md references docker but docker is not installed." >&2
    exit 1
  fi
fi

if grep -qi "make check" AGENTS.md; then
  if ! command -v make >/dev/null 2>&1; then
    echo "AGENTS.md references make but make is not installed." >&2
    exit 1
  fi
  if ! grep -qE '^check:' Makefile; then
    echo "AGENTS.md references make check but no 'check' target found in Makefile." >&2
    exit 1
  fi
fi

if grep -qi "flake8" AGENTS.md; then
  if ! command -v flake8 >/dev/null 2>&1; then
    echo "AGENTS.md references flake8 but flake8 is not installed." >&2
    exit 1
  fi
fi

if grep -qi "phpunit" AGENTS.md; then
  if command -v phpunit >/dev/null 2>&1 || [ -f vendor/bin/phpunit ]; then
    :
  else
    echo "AGENTS.md references phpunit but phpunit is not installed." >&2
    exit 1
  fi
fi

echo "AGENTS.md passes basic drift check."
