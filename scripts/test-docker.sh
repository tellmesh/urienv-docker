#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose --profile test up --build --abort-on-container-exit --exit-code-from e2e e2e
