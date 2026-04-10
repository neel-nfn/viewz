#!/bin/bash

echo "=== OAuth Flow Complete Test ==="
echo ""

# 1. Health check
echo "1️⃣ Health Check:"
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
echo ""

# 2. Channels list (after OAuth)
echo "2️⃣ Channels List:"
CHANNELS=$(curl -s http://localhost:8000/api/v1/channels/list)
echo "$CHANNELS" | python3 -m json.tool
echo ""

if [ "$CHANNELS" != "[]" ] && [ -n "$CHANNELS" ]; then
    echo "✅ Channel found!"
    echo ""
    echo "3️⃣ Plan Limit:"
    curl -s http://localhost:8000/api/v1/billing/plan_limit | python3 -m json.tool
    echo ""
    echo "4️⃣ Optional - Force Rollup:"
    curl -s -X POST http://localhost:8000/api/v1/billing/rollup_ai_usage | python3 -m json.tool
    echo ""
    echo "🎉 OAuth Flow Complete! Grid Pulse channel is connected."
else
    echo "⚠️  No channels yet. Complete OAuth flow first:"
    echo "   open http://localhost:8000/api/v1/auth/login"
fi

