#!/bin/bash
# BYOK + Batch-12 Verification Script
set -e

echo "🔍 Viewz — BYOK Encryption + Batch-12 Verification"
echo "=================================================="
echo ""

# Check backend files
echo "📦 Backend File Check:"
test -f backend/migrations/006_ai_provider_keys_encrypt.sql && echo "  ✅ Migration 006 exists" || echo "  ❌ Migration 006 missing"
test -f backend/app/utils/crypto_keys.py && echo "  ✅ crypto_keys.py exists" || echo "  ❌ crypto_keys.py missing"
test -f backend/app/services/integration_service.py && echo "  ✅ integration_service.py exists" || echo "  ❌ integration_service.py missing"
test -f backend/app/api/integrations.py && echo "  ✅ integrations.py API exists" || echo "  ❌ integrations.py missing"
echo ""

# Check frontend files
echo "📦 Frontend File Check:"
test -f frontend/src/pages/Settings/Integrations.jsx && echo "  ✅ Integrations page exists" || echo "  ❌ Integrations page missing"
test -f frontend/src/services/integrationService.js && echo "  ✅ integrationService.js exists" || echo "  ❌ integrationService.js missing"
test -f frontend/src/pages/DashboardToday.jsx && echo "  ✅ DashboardToday wired" || echo "  ❌ DashboardToday missing"
test -f frontend/src/services/analyticsService.js && echo "  ✅ analyticsService.js exists" || echo "  ❌ analyticsService.js missing"
echo ""

# Check dependencies
echo "📚 Dependencies:"
cd backend
grep -q "cryptography" requirements.txt && echo "  ✅ cryptography in requirements.txt" || echo "  ❌ cryptography missing from requirements.txt"
cd ..
echo ""

# Check environment
echo "⚙️  Environment Variables:"
if [ -f backend/.env ]; then
  grep -q "AI_KEY_KEK_B64" backend/.env && echo "  ✅ AI_KEY_KEK_B64 in backend/.env" || echo "  ⚠️  AI_KEY_KEK_B64 not found (generate with: openssl rand -base64 32)"
  grep -q "SUPABASE_DB_URL" backend/.env && echo "  ✅ SUPABASE_DB_URL configured" || echo "  ⚠️  SUPABASE_DB_URL not found"
else
  echo "  ⚠️  backend/.env not found"
fi

if [ -f frontend/.env ]; then
  grep -q "VITE_API_BASE_URL" frontend/.env && echo "  ✅ VITE_API_BASE_URL in frontend/.env" || echo "  ⚠️  VITE_API_BASE_URL not found"
else
  echo "  ⚠️  frontend/.env not found"
fi
echo ""

# Check backend server
echo "🌐 Backend Server Check:"
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
  echo "  ✅ Backend running on port 8000"
  curl -s http://localhost:8000/api/v1/integrations > /dev/null 2>&1 && echo "  ✅ /api/v1/integrations endpoint accessible" || echo "  ⚠️  /api/v1/integrations endpoint not accessible"
  curl -s http://localhost:8000/metrics > /dev/null 2>&1 && echo "  ✅ /metrics endpoint accessible" || echo "  ⚠️  /metrics endpoint not accessible"
else
  echo "  ⚠️  Backend not running (expected if not started yet)"
fi
echo ""

# Check frontend server
echo "🌐 Frontend Server Check:"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
  echo "  ✅ Frontend running on port 5173"
else
  echo "  ⚠️  Frontend not running (expected if not started yet)"
fi
echo ""

# Database migration check
echo "🗄️  Database Migration Status:"
if [ -n "$SUPABASE_DB_URL" ] || [ -f backend/.env ]; then
  DB_URL=$(grep "SUPABASE_DB_URL" backend/.env 2>/dev/null | cut -d'=' -f2- | tr -d '"' || echo "")
  if [ -n "$DB_URL" ]; then
    if psql "$DB_URL" -c "\d ai_provider_keys" > /dev/null 2>&1; then
      echo "  ✅ ai_provider_keys table exists"
      # Check for encrypted columns
      psql "$DB_URL" -c "\d ai_provider_keys" 2>/dev/null | grep -q "enc_key_base64" && echo "  ✅ Encryption columns present" || echo "  ⚠️  Encryption columns may be missing (run migration 006)"
    else
      echo "  ⚠️  ai_provider_keys table not found (run migration 005 first)"
    fi
  else
    echo "  ⚠️  Cannot determine DB URL from .env"
  fi
else
  echo "  ⚠️  SUPABASE_DB_URL not set"
fi
echo ""

echo "✅ Verification Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Generate KEK: openssl rand -base64 32"
echo "  2. Add to backend/.env: AI_KEY_KEK_B64=<key>"
echo "  3. Run migration: psql \"\$SUPABASE_DB_URL\" -f backend/migrations/006_ai_provider_keys_encrypt.sql"
echo "  4. Start backend: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  5. Start frontend: npm run dev"
echo "  6. Test integration flow in browser"

