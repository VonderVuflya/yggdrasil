#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-fallback}"

export MUNINN_SERVER_AUTH_TOKEN="${MUNINN_SERVER_AUTH_TOKEN:-yggdrasil-demo-token}"
export MUNINN_AUTH_TOKEN="${MUNINN_AUTH_TOKEN:-$MUNINN_SERVER_AUTH_TOKEN}"
export MUNINN_HOST="${MUNINN_HOST:-127.0.0.1}"
export MUNINN_PORT="${MUNINN_PORT:-42069}"
export MUNINN_PROJECT_SCOPE_STRICT=1
export MUNINN_CONSOLIDATION_ENABLED=false
export MUNINN_RERANKER_ENABLED=false
export MUNINN_XLAM_ENABLED=false
export MUNINN_INSTRUCTOR_ENABLED=false
export MUNINN_LEGACY_DISCOVERY_ENABLED=false
export MUNINN_PERIODIC_INGESTION_ENABLED=false
export HF_HOME="$ROOT_DIR/.cache/huggingface"
export XDG_CACHE_HOME="$ROOT_DIR/.cache"
export HF_HUB_DISABLE_XET="${HF_HUB_DISABLE_XET:-1}"

case "$MODE" in
  fallback)
    export MUNINN_DATA_DIR="$ROOT_DIR/muninn-data-fallback"
    export MUNINN_EMBEDDING_MODEL="${MUNINN_EMBEDDING_MODEL:-BAAI/bge-small-en-v1.5}"
    export MUNINN_EMBEDDING_DIMS="${MUNINN_EMBEDDING_DIMS:-384}"
    ;;
  dense-small)
    export MUNINN_DATA_DIR="$ROOT_DIR/muninn-data-dense-small"
    export MUNINN_EMBEDDING_MODEL="${MUNINN_EMBEDDING_MODEL:-BAAI/bge-small-en-v1.5}"
    export MUNINN_EMBEDDING_DIMS="${MUNINN_EMBEDDING_DIMS:-384}"
    ;;
  *)
    echo "Usage: $0 [fallback|dense-small]" >&2
    exit 2
    ;;
esac

cd "$ROOT_DIR/Muninn"
exec "$ROOT_DIR/.venv/bin/python" server.py
