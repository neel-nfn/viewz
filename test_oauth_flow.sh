#!/bin/bash

echo "=== Viewz OAuth Flow Test ==="
echo ""

# Check if backend is running
echo "1️⃣ Checking backend..."
BACKEND_OK=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print('ok' if d.get('ok') else 'fail')" 2>/dev/null)
if [ "$BACKEND_OK" = "ok" ]; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend not responding"
    echo "   Make sure: cd backend && uvicorn app.main:app --reload --port 8000"
    exit 1
fi

# Check if frontend is running
echo ""
echo "2️⃣ Checking frontend..."
FRONTEND_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 2>/dev/null)
if [ "$FRONTEND_OK" = "200" ]; then
    echo "   ✅ Frontend is running"
else
    echo "   ⚠️  Frontend may not be ready (HTTP $FRONTEND_OK)"
    echo "   Make sure: cd frontend && npm run dev"
fi

# Check OAuth credentials
echo ""
echo "3️⃣ Checking OAuth configuration..."
OAUTH_CONFIG=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print('configured' if d.get('oauth_client') else 'missing')" 2>/dev/null)
if [ "$OAUTH_CONFIG" = "configured" ]; then
    echo "   ✅ OAuth credentials configured"
else
    echo "   ⚠️  OAuth credentials not set"
    echo "   Edit backend/.env and set:"
    echo "   GOOGLE_CLIENT_ID=your_actual_client_id"
    echo "   GOOGLE_CLIENT_SECRET=your_actual_secret"
fi

# Check channels
echo ""
echo "4️⃣ Current channels:"
CHANNELS=$(curl -s http://localhost:8000/api/v1/channels/list 2>/dev/null)
if [ -n "$CHANNELS" ] && [ "$CHANNELS" != "[]" ]; then
    echo "$CHANNELS" | python3 -m json.tool 2>/dev/null || echo "$CHANNELS"
else
    echo "   ⚠️  No channels connected yet"
fi

# Check plan limit
echo ""
echo "5️⃣ Plan limit:"
PLAN_LIMIT=$(curl -s http://localhost:8000/api/v1/billing/plan_limit 2>/dev/null)
echo "$PLAN_LIMIT" | python3 -m json.tool 2>/dev/null || echo "$PLAN_LIMIT"

echo ""
echo "=== Next Steps ==="
echo ""
echo "If OAuth credentials are configured:"
echo "  1. Visit: http://localhost:8000/api/v1/auth/login"
echo "  2. Complete Google consent"
echo "  3. Should redirect to: http://localhost:5173/auth/success"
echo "  4. Verify channel at: http://localhost:5173/settings/channels"
echo ""
echo "Success criteria:"
echo "  ✓ GET /api/v1/health shows oauth_client: true"
echo "  ✓ Channel appears in /settings/channels"
echo "  ✓ sched_last_run populated after 15 minutes"

