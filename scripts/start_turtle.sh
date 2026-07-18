#!/bin/bash

cd "$(dirname "$0")/.."

source .venv/bin/activate

python -m robot.startup.main