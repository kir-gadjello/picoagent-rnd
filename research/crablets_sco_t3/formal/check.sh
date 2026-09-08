#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if grep -REn '\b(sorry|admit|axiom)\b' ScoT3*.lean ScoT3/*.lean | grep -vE '^.*(--|/-)'; then
  echo 'placeholder/axiom token found' >&2
  exit 2
fi
lake update
lake exe cache get
lake build
