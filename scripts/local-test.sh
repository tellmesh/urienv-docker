#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/paths.sh
source "$ROOT/../scripts/paths.sh"
PYPATH="packages/python/urisysedge/src:packages/python/urienv/src"
if up="$(uricore_pythonpath 2>/dev/null)"; then
  PYPATH="${up}:${PYPATH}"
fi
PYTHONPATH="$PYPATH" python -m pytest tests/test_urienv.py -q
