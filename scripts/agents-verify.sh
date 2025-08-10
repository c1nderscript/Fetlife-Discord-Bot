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

echo "Agents.md passes basic drift check."
