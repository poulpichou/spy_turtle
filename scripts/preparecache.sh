#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
exec "$PWD/.venv/bin/python" scripts/preparecache.py "$@"
