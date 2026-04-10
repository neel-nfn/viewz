#!/usr/bin/env bash
set -euo pipefail
cd backend
if ! grep -q '^AI_KEY_KEK_B64=' .env 2>/dev/null; then
  KEK=$(openssl rand -base64 32)
  printf "\nAI_KEY_KEK_B64=%s\n" "$KEK" >> .env
fi
psql "$SUPABASE_DB_URL" -f backend/migrations/005_ai_provider_keys.sql
psql "$SUPABASE_DB_URL" -f backend/migrations/006_ai_provider_keys_encrypt.sql
python -m pip install -r requirements.txt
