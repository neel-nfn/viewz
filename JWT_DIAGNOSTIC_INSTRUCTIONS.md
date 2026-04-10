# 🔍 JWT Diagnostic Instructions

## Step 1: Start Backend Server

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 2: Test Secret Loading

```bash
curl "http://localhost:8000/api/v1/debug/jwt"
```

**Expected output:**
```json
{
  "SUPABASE_JWT_SECRET_len": 64,
  "SUPABASE_JWT_SECRET_start": "eyJhbGc...",
  "SUPABASE_JWT_SECRET_end": "...9uQ=="
}
```

If `SUPABASE_JWT_SECRET_len` is 0, the secret isn't loading from `.env`.

## Step 3: Get Token from Browser

1. Start frontend: `cd frontend && npm run dev`
2. Open http://localhost:5173/auth-debug
3. Log in with Supabase credentials
4. Open browser console (F12)
5. Run: `debugAuth()`
6. Copy the token (starts with `eyJhbGciOiJI...`)

## Step 4: Test Token Decoding

```bash
curl "http://localhost:8000/api/v1/debug/jwt?token=YOUR_TOKEN_HERE"
```

**Success output:**
```json
{
  "SUPABASE_JWT_SECRET_len": 64,
  "SUPABASE_JWT_SECRET_start": "eyJhbGc...",
  "SUPABASE_JWT_SECRET_end": "...9uQ==",
  "decoded_payload": {
    "aud": "authenticated",
    "email": "test@example.com",
    "role": "authenticated",
    "exp": 1730660000,
    "sub": "uuid-here"
  }
}
```

**Failure output (secret mismatch):**
```json
{
  "error": "Signature verification failed"
}
```

## Troubleshooting

- **Secret length is 0**: Check `backend/.env` has `SUPABASE_JWT_SECRET=...` (no quotes)
- **Signature verification failed**: Secret in `.env` doesn't match Supabase dashboard → Settings → API → JWT Secret
- **Token expired**: Get a fresh token by logging in again

