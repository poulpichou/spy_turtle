#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
./scripts/stop_gpio.sh
sleep 0.3
./scripts/start_gpio.sh
