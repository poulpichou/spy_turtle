#!/bin/bash
source .venv/bin/activate
uvicorn robot.api.server:app --reload