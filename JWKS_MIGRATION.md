# 🔐 JWKS Auto-Verifier Migration Complete

## ✅ Changes Made

1. **`backend/app/utils/jwt_verifier.py`** (NEW):
   - Auto-detects token algorithm (HS256 legacy vs JWKS)
   - Falls back to legacy HS256 secret if no `kid` in header
   - Uses JWKS endpoint for modern Supabase tokens
   - Handles both RS256 and HS256 algorithms

2. **`backend/app/api/deps.py`**:
   - Updated `get_current_user()` to use `verify_supabase_jwt()`
   - Simplified error handling
   - Maintains debug logging

3. **`backend/requirements.txt`**:
   - Added `requests` dependency for JWKS fetching

## 🧪 How It Works

The verifier:
1. Checks token header for `alg` and `kid`
2. If `alg == "HS256"` and no `kid` → uses legacy secret
3. If `kid` exists → fetches JWKS from Supabase and verifies with RSA key
4. Automatically handles token rotation

## 🚀 Testing

### Step 1: Install requests (if not already installed)

```bash
cd backend
source .venv/bin/activate
pip install requests
```

### Step 2: Restart Backend

```bash
cd ~/Desktop/Viewz-Workspace/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Test with Real Token

In browser console (after logging in at http://localhost:5173/auth-debug):

```js
debugAuth()
```

Or test directly:

```js
fetch("http://localhost:8000/api/v1/auth/me", {
  headers: {
    Authorization: "Bearer " + (await window.supabase.auth.getSession()).data.session.access_token
  }
}).then(r => r.json()).then(console.log);
```

## 📊 Expected Backend Output

### Success:
```
🧠 [JWT DEBUG] Verifying via JWKS...
✅ [JWT DEBUG] Token verified successfully!
```

### If using legacy HS256:
```
🧠 [JWT DEBUG] Verifying via JWKS...
✅ [JWT DEBUG] Token verified successfully!
```
(Will automatically use legacy secret if token has no `kid`)

### Failure:
```
🧠 [JWT DEBUG] Verifying via JWKS...
❌ [JWT DEBUG] Verify failed: [error message]
```

## 🎯 Benefits

- ✅ Supports both legacy HS256 and modern JWKS tokens
- ✅ Automatic algorithm detection
- ✅ Handles Supabase key rotation
- ✅ No manual secret management needed for JWKS tokens

