# BYOK Encryption + Batch-12 Verification Guide

## ✅ Setup Verification Status

All required files are in place and servers are running.

### Files Verified ✅
- ✅ `backend/migrations/006_ai_provider_keys_encrypt.sql`
- ✅ `backend/app/utils/crypto_keys.py`
- ✅ `backend/app/services/integration_service.py` (with `load_ai_key_for_org`)
- ✅ `backend/app/api/integrations.py` (role guards + hints)
- ✅ `frontend/src/pages/Settings/Integrations.jsx`
- ✅ `frontend/src/services/integrationService.js`
- ✅ `frontend/src/pages/DashboardToday.jsx` (wired to live APIs)
- ✅ `backend/requirements.txt` (cryptography>=42.0.0)

### Servers Running ✅
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:5173
- ✅ Endpoints accessible: `/api/v1/integrations`, `/metrics`

---

## 🔐 Step 1: Generate & Set KEK

Run:
```bash
openssl rand -base64 32
```

Copy the output and add to `backend/.env`:
```
AI_KEY_KEK_B64=<paste_generated_key_here>
```

**Example:**
```
AI_KEY_KEK_B64=K8jLmN3pQ9rF2xV5wZ8bY1cD4eG7hJ0kM3nP6qS9tU2vW5xZ8aB1cD4eG7hJ0k=
```

**⚠️ Important:** Keep this key secure. If lost, encrypted keys cannot be decrypted.

---

## 🗄️ Step 2: Run Migrations

Ensure base table exists first:
```bash
psql "$SUPABASE_DB_URL" -f backend/migrations/005_ai_provider_keys.sql
```

Then run encryption migration:
```bash
psql "$SUPABASE_DB_URL" -f backend/migrations/006_ai_provider_keys_encrypt.sql
```

Verify columns:
```bash
psql "$SUPABASE_DB_URL" -c "\d ai_provider_keys"
```

Should show: `enc_key_base64`, `iv_base64`, `tag_base64`, `key_hint`

---

## 🧪 Step 3: End-to-End Test Flow

### A. Test Integration API

```bash
# Check status
curl -s http://localhost:8000/api/v1/integrations | jq .

# Expected: {"youtube_connected": false, "ai_key_configured": false, "provider": "gemini", "key_hint": null}

# Save a test key (admin/manager only)
curl -X POST http://localhost:8000/api/v1/integrations/ai_key \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini", "api_key": "AIzaSyTest123456789012345678901234567890"}' \
  -H "Cookie: viewz_session=your_session" \
  | jq .

# Expected: {"saved": true, "provider": "gemini", "hint": "Gemini · …7890"}

# Verify status updated
curl -s http://localhost:8000/api/v1/integrations | jq .

# Expected: {"ai_key_configured": true, "key_hint": "Gemini · …7890"}
```

### B. Verify Encryption in DB

```bash
psql "$SUPABASE_DB_URL" -c "
  select 
    provider,
    length(enc_key_base64) as enc_length,
    length(iv_base64) as iv_length,
    length(tag_base64) as tag_length,
    key_hint
  from ai_provider_keys
  where provider = 'gemini'
  order by updated_at desc limit 1;
"
```

Should show:
- `enc_length` > 0 (ciphertext)
- `iv_length` > 0 (12-byte IV = 16 base64 chars)
- `tag_length` > 0 (16-byte tag = 24 base64 chars)
- `key_hint` = "Gemini · …7890" (last 4 chars)

**Critical:** No plaintext key should be stored anywhere.

### C. Test Decryption (Runtime)

```python
# In Python shell or test script
from app.services.integration_service import load_ai_key_for_org
from uuid import UUID

org_id = UUID("00000000-0000-0000-0000-000000000000")  # Your test org
key = load_ai_key_for_org(org_id, "gemini")

if key:
    print(f"✅ Decryption successful: {key[:10]}...{key[-4:]}")
else:
    print("❌ No key found or decryption failed")
```

### D. Frontend Integration Test

1. **Open:** http://localhost:5173/app/settings/integrations

2. **Verify UI shows:**
   - YouTube connection status
   - Gemini key input field (if not configured) OR "Configured" badge with hint (if configured)
   - "Save Key" or "Delete Key" button

3. **Save a key:**
   - Paste your Gemini API key
   - Click "Save Key"
   - Verify success message
   - Check hint appears (e.g., "Gemini · …abcd")

4. **Refresh page:**
   - Status should persist
   - Hint should display correctly

### E. Dashboard Live Data Test

1. **Open:** http://localhost:5173/app

2. **Verify:**
   - **Channel Snapshot:** Shows views/CTR (not placeholder)
   - **Topic Explorer:** Can search keywords, shows metrics
   - **Daily Tasks:** List populated (not empty)
   - **AI Recommendations:** List visible
   - **Badge:** "Live Data" (not "Demo Mode")

3. **Keyword Search Test:**
   - Enter a term in Topic Explorer
   - Click "Search"
   - Verify metrics appear (reach_score, competition_level, suggested_length)

### F. Feedback Modal Test

1. Click "Feedback" button in topbar
2. Fill form:
   - Title: "Test feedback"
   - Category: "bug"
   - Severity: "low"
   - Description: "Testing feedback system"
3. Submit
4. Verify success toast
5. Check in Settings → Feedback tab (admin only)

### G. Prometheus Metrics Test

```bash
curl -s http://localhost:8000/metrics | grep -E "(http_requests_total|auth_failures_total|http_5xx_total)" | head -10
```

Should see:
```
http_requests_total{path="/api/v1/integrations",method="GET"} 2.0
auth_failures_total 0.0
http_5xx_total 0.0
```

---

## 🔒 Security Verification

### Role-Based Access

Test that non-admin users cannot save keys:

```bash
# Without admin role (should fail with 403)
curl -X POST http://localhost:8000/api/v1/integrations/ai_key \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini", "api_key": "test123"}' \
  -v

# Expected: 403 Forbidden
```

### Encryption Strength

1. **Verify no plaintext in DB:**
   ```bash
   psql "$SUPABASE_DB_URL" -c "select * from ai_provider_keys;" | grep -i "api_key"
   ```
   Should find NO plaintext keys.

2. **Verify KEK required:**
   - Temporarily remove `AI_KEY_KEK_B64` from `.env`
   - Restart backend
   - Try saving a key → Should fail with "AI_KEY_KEK_B64 missing"

---

## 🧾 Acceptance Checklist

| Check | Verification Command | Expected Result |
|-------|---------------------|-----------------|
| **Integration page** | Open `/app/settings/integrations` | Shows status + key hint |
| **Encryption** | `psql ... -c "select enc_key_base64 from ai_provider_keys"` | Non-null ciphertext |
| **Decryption** | `load_ai_key_for_org(org_id, "gemini")` | Returns decrypted key |
| **Dashboard data** | Open `/app` | Live stats, not placeholders |
| **Feedback modal** | Submit feedback → Check Settings | Record appears |
| **Metrics** | `curl localhost:8000/metrics` | Prometheus format |
| **Security** | POST without admin role | 403 Forbidden |

---

## 🐛 Troubleshooting

### "AI_KEY_KEK_B64 missing"
- Generate: `openssl rand -base64 32`
- Add to `backend/.env`
- Restart backend

### "Decryption failed"
- Verify KEK matches the one used for encryption
- Check DB has all three columns (enc_key, iv, tag)
- Verify `cryptography>=42.0.0` installed

### "Migration fails"
- Ensure migration 005 ran first (base table exists)
- Check Postgres connection: `psql "$SUPABASE_DB_URL" -c "select 1"`

### "Frontend shows 'Demo Mode'"
- Check `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env`
- Verify backend is running
- Check browser console for API errors

---

## ✅ Success Criteria

All checks pass:
- ✅ Gemini key encrypted (AES-GCM) in DB
- ✅ Decryption works at runtime
- ✅ Integration page shows live status + hint
- ✅ Dashboard displays real analytics
- ✅ Feedback modal submits successfully
- ✅ Prometheus metrics export correctly
- ✅ Role-based access enforced

**Ready for production!** 🚀

