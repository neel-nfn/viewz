# 🔐 JWT Debug Testing Instructions

## ✅ Changes Made

1. **`backend/app/api/deps.py`**: Added detailed debug logging to `get_current_user()`:
   - Logs secret length and type
   - Logs verification success/failure with specific error types
   - Handles expired tokens, invalid signatures, and other errors separately

2. **`.env` files cleanup**: Extra `.env` files renamed to `.bak2`:
   - `.env.backup` → `.env.backup.bak2`
   - `.env.bak` → `.env.bak2`
   - `.env.prod` → `.env.prod.bak2`
   - Only `.env` remains active

## 🧪 Testing Steps

### Step 1: Restart Backend (Required)

The backend needs to be restarted to pick up the new debug logging:

```bash
cd ~/Desktop/Viewz-Workspace/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Start Frontend and Login

```bash
cd ~/Desktop/Viewz-Workspace/frontend
npm run dev
```

Then:
1. Visit **http://localhost:5173/auth-debug**
2. Log in with your Supabase test credentials (email + password)
3. Once logged in, open browser console (F12)
4. Run: `debugAuth()`

### Step 3: Test Real Endpoint

In browser console, run:

```js
fetch("http://localhost:8000/api/v1/auth/me", {
  headers: {
    Authorization: "Bearer " + (await window.supabase.auth.getSession()).data.session.access_token
  }
}).then(r => r.json()).then(console.log);
```

## 📊 Expected Backend Terminal Output

### ✅ Success Case:
```
🧠 [JWT DEBUG] Verifying Supabase token...
🧠 [JWT DEBUG] SUPABASE_JWT_SECRET length: 64
🧠 [JWT DEBUG] Secret type: bytes
✅ [JWT DEBUG] Token verified successfully!
```

### ❌ Signature Verification Failed:
```
🧠 [JWT DEBUG] Verifying Supabase token...
🧠 [JWT DEBUG] SUPABASE_JWT_SECRET length: 64
🧠 [JWT DEBUG] Secret type: bytes
❌ [JWT DEBUG] Signature verification failed.
```

### ❌ Token Expired:
```
🧠 [JWT DEBUG] Verifying Supabase token...
🧠 [JWT DEBUG] SUPABASE_JWT_SECRET length: 64
🧠 [JWT DEBUG] Secret type: bytes
❌ [JWT DEBUG] Token expired.
```

## 🔍 What to Look For

1. **Secret length**: Should be 64 (decoded bytes)
2. **Secret type**: Should be `bytes`
3. **Verification result**: Should show `✅ Token verified successfully!`

If you see `❌ Signature verification failed`, check:
- Supabase Dashboard → Settings → API → JWT Secret
- Compare with `backend/.env` → `SUPABASE_JWT_SECRET`
- Ensure no extra whitespace/newlines in `.env`

## 📝 Next Steps

After testing, copy the backend terminal output and share it to confirm:
- Which secret length is being used
- Whether verification succeeds or fails
- What specific error occurs (if any)

