#!/bin/bash

echo "=== Viewz Setup Verification Script ==="
echo ""

# Check backend
echo "🔍 Backend Health Check:"
BACKEND_HEALTH=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$BACKEND_HEALTH" | python3 -m json.tool 2>/dev/null || echo "$BACKEND_HEALTH"
else
    echo "❌ Backend not responding on port 8000"
    echo "   Make sure: uvicorn app.main:app --reload --port 8000"
fi
echo ""

# Check frontend
echo "🔍 Frontend Status:"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend is running on port 5173"
else
    echo "⚠️  Frontend may not be ready (HTTP $FRONTEND_STATUS)"
    echo "   Make sure: npm run dev (in frontend directory)"
fi
echo ""

# Test endpoints
echo "📋 API Endpoint Tests:"
echo ""
echo "1️⃣  Channels List:"
curl -s http://localhost:8000/api/v1/channels/list 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "   ⚠️  No channels or endpoint not ready"
echo ""

echo "2️⃣  Plan Limit:"
curl -s http://localhost:8000/api/v1/billing/plan_limit 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "   ⚠️  Plan limit endpoint not ready"
echo ""

echo "3️⃣  Manual Rollup (optional):"
curl -s -X POST http://localhost:8000/api/v1/billing/rollup_ai_usage 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "   ⚠️  Rollup endpoint not ready"
echo ""

echo "=== OAuth Flow Test ==="
echo ""
echo "🔗 To test OAuth connection:"
echo "   1. Visit: http://localhost:8000/api/v1/auth/login"
echo "   2. Complete Google consent"
echo "   3. Should redirect to: http://localhost:5173/auth/success"
echo "   4. Verify channel at: http://localhost:5173/settings/channels"
echo ""
echo "📋 Prerequisites:"
echo "   [ ] GOOGLE_CLIENT_ID set in backend/.env"
echo "   [ ] GOOGLE_CLIENT_SECRET set in backend/.env"
echo "   [ ] Google Cloud Console configured:"
echo "       - Redirect URI: http://localhost:8000/api/v1/auth/callback"
echo "       - YouTube Data API v3 enabled"
echo "       - OAuth consent screen configured"
echo ""

