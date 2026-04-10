#!/bin/bash
# BYOK Quick Setup Script
set -e

echo "🔐 BYOK Encryption Setup"
echo "======================="
echo ""

# Check if KEK exists
if grep -q "AI_KEY_KEK_B64=" backend/.env 2>/dev/null; then
  echo "✅ AI_KEY_KEK_B64 already in backend/.env"
else
  echo "🔑 Generating new KEK..."
  KEK=$(openssl rand -base64 32)
  echo "" >> backend/.env
  echo "AI_KEY_KEK_B64=$KEK" >> backend/.env
  echo "✅ KEK generated and added to backend/.env"
  echo "   Keep this key secure! If lost, encrypted keys cannot be decrypted."
fi

# Check database connection
if [ -n "$SUPABASE_DB_URL" ] || [ -f backend/.env ]; then
  DB_URL=$(grep "SUPABASE_DB_URL" backend/.env 2>/dev/null | cut -d'=' -f2- | tr -d '"' || echo "")
  
  if [ -n "$DB_URL" ]; then
    echo ""
    echo "🗄️  Running migrations..."
    
    # Check if base table exists
    if psql "$DB_URL" -c "\d ai_provider_keys" > /dev/null 2>&1; then
      echo "  ✅ ai_provider_keys table exists"
    else
      echo "  ⚠️  Running base migration 005..."
      psql "$DB_URL" -f backend/migrations/005_ai_provider_keys.sql || echo "  ⚠️  Migration 005 may have errors (non-fatal if already exists)"
    fi
    
    # Run encryption migration
    echo "  📝 Running encryption migration 006..."
    psql "$DB_URL" -f backend/migrations/006_ai_provider_keys_encrypt.sql && echo "  ✅ Migration 006 complete" || echo "  ⚠️  Migration 006 had errors (check if columns already exist)"
    
    # Verify columns
    echo ""
    echo "🔍 Verifying encryption columns..."
    psql "$DB_URL" -c "\d ai_provider_keys" | grep -q "enc_key_base64" && echo "  ✅ Encryption columns present" || echo "  ⚠️  Encryption columns missing"
  else
    echo "⚠️  SUPABASE_DB_URL not found in backend/.env"
    echo "   Please set it before running migrations"
  fi
else
  echo "⚠️  Cannot find backend/.env or SUPABASE_DB_URL"
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Restart backend to load KEK: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  2. Test: curl http://localhost:8000/api/v1/integrations"
echo "  3. Open frontend: http://localhost:5173/app/settings/integrations"
echo "  4. Save a Gemini key and verify encryption in DB"

