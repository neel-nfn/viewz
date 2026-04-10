# 🔐 Base64-Aware JWT Testing Guide

## ✅ Changes Made

1. **`backend/app/api/deps.py`**: Added `_load_supabase_secret()` function that:
   - Tries to base64-decode the secret first
   - Falls back to raw string if base64 decode fails
   - Returns bytes for JWT decoding

2. **`backend/app/main.py`**: Enhanced debug endpoint to show:
   - `raw_len`: Length of raw secret from env
   - `used_decoded`: Whether base64 decoding was used
   - `decoded_len`: Length of decoded secret (if decoded)

## 🧪 Testing Steps

### Step 1: Restart Backend (if not already restarted)

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Check Secret Loading

```bash
curl "http://localhost:8000/api/v1/debug/jwt"
```

**Expected output:**
```json
{
  "raw_len": 88,
  "raw_start": "1IS39ThS",
  "raw_end": "7arzuQ==",
  "used_decoded": true,
  "decoded_len": 64
}
```

If `used_decoded: true` → Secret is base64-encoded (correct!)
If `used_decoded: false` → Secret is raw string

### Step 3: Get Fresh Token from Browser

1. Ensure frontend is running: `cd frontend && npm run dev`
2. Open http://localhost:5173/auth-debug
3. Log in with Supabase credentials
4. Open browser console (F12)
5. Run: `debugAuth()`
6. Copy the token (starts with `eyJhbGciOiJI...`)

### Step 4: Test Token Decoding (Browser Console)

```js
const t = "PASTE_YOUR_TOKEN_HERE";
fetch("http://localhost:8000/api/v1/debug/jwt?token=" + t)
  .then(r => r.json())
  .then(console.log);
```

**Success output:**
```json
{
  "raw_len": 88,
  "raw_start": "1IS39ThS",
  "raw_end": "7arzuQ==",
  "used_decoded": true,
  "decoded_len": 64,
  "decoded_payload": {
    "aud": "authenticated",
    "email": "test@viewz.local",
    "role": "authenticated",
    "exp": 1730660000,
    "sub": "user-uuid-here"
  }
}
```

If you see `decoded_payload` → 🎉 **Success!** JWT verification is working.

### Step 5: Test Real Endpoint

```js
fetch("http://localhost:8000/api/v1/auth/me", {
  headers: {
    Authorization: "Bearer " + (await supabase.auth.getSession()).data.session.access_token
  }
}).then(r => r.json()).then(console.log);
```

**Expected output:**
```json
{
  "user": {
    "aud": "authenticated",
    "email": "test@viewz.local",
    "role": "authenticated",
    "sub": "user-uuid-here"
  }
}
```

## 🔍 Troubleshooting

- **`used_decoded: false`**: Your secret in `.env` is not base64-encoded. This is OK if it's a raw string.
- **`error: "Signature verification failed"`**: The secret still doesn't match. Check:
  - Supabase Dashboard → Settings → API → JWT Secret
  - Compare with `backend/.env` → `SUPABASE_JWT_SECRET`
- **`error: "Token has expired"`**: Get a fresh token by logging in again

