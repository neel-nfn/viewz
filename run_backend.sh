#!/usr/bin/env bash
set -euo pipefail
cd backend
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
