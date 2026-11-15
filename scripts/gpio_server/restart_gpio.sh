#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
./scripts/gpio_server/stop_gpio.sh
sleep 0.3
./scripts/gpio_server/start_gpio.sh
