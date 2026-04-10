#!/usr/bin/env bash
set -euo pipefail
cd frontend
if [ ! -f ".env" ]; then
  echo 'VITE_API_BASE_URL=http://localhost:8000' > .env
fi
npm install
npm run dev
