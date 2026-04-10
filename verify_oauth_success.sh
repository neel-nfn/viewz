#!/bin/bash

echo "=== OAuth Flow Verification Report ==="
echo ""

# Health check
echo "1️⃣ Health Status:"
HEALTH=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
    echo "$HEALTH" | python3 -m json.tool
    OAUTH_CLIENT=$(echo "$HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin).get('oauth_client', False))" 2>/dev/null)
    if [ "$OAUTH_CLIENT" = "True" ]; then
        echo "   ✓ OAuth credentials configured"
    else
        echo "   ⚠️  OAuth credentials not set"
    fi
else
    echo "   ❌ Backend not responding"
fi
echo ""

# Channels list
echo "2️⃣ Channels List:"
CHANNELS=$(curl -s http://localhost:8000/api/v1/channels/list 2>/dev/null)
if [ -n "$CHANNELS" ]; then
    echo "$CHANNELS" | python3 -m json.tool
    CHANNEL_COUNT=$(echo "$CHANNELS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d) if isinstance(d, list) else 0)" 2>/dev/null)
    if [ "$CHANNEL_COUNT" -gt 0 ]; then
        echo "   ✅ Channel(s) found!"
    else
        echo "   ⚠️  No channels yet"
    fi
else
    echo "   ❌ Endpoint not responding"
fi
echo ""

# Plan limit
echo "3️⃣ Plan Limit:"
PLAN=$(curl -s http://localhost:8000/api/v1/billing/plan_limit 2>/dev/null)
if [ -n "$PLAN" ]; then
    echo "$PLAN" | python3 -m json.tool
else
    echo "   ⚠️  Endpoint not responding"
fi
echo ""

# Local dev store check
echo "4️⃣ Local Dev Store (if Supabase not configured):"
if [ -f "backend/local_dev_store/channels.json" ]; then
    echo "   ✅ channels.json exists"
    echo "   Content:"
    cat backend/local_dev_store/channels.json | python3 -m json.tool 2>/dev/null | head -15 || cat backend/local_dev_store/channels.json | head -5
else
    echo "   ⚠️  channels.json not found"
fi
echo ""

if [ -f "backend/local_dev_store/oauth_token.json" ]; then
    echo "   ✅ oauth_token.json exists"
    echo "   (Token encrypted, content hidden)"
else
    echo "   ⚠️  oauth_token.json not found"
fi
echo ""

# Summary
echo "=== Summary ==="
echo ""

if [ -f "backend/local_dev_store/channels.json" ] || [ "$CHANNEL_COUNT" -gt 0 ] 2>/dev/null; then
    echo "✅ OAuth Flow: COMPLETED"
    echo "   Channel data saved (local dev store or Supabase)"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Visit: http://localhost:5173/settings/channels"
    echo "   2. Verify Grid Pulse appears with 'connected' badge"
    echo "   3. Run rollup (optional): curl -s -X POST http://localhost:8000/api/v1/billing/rollup_ai_usage"
else
    echo "⏳ OAuth Flow: NOT COMPLETED YET"
    echo ""
    echo "📋 To start OAuth:"
    echo "   open http://localhost:8000/api/v1/auth/login"
    echo ""
    echo "After completing Google consent, run this script again to verify."
fi

