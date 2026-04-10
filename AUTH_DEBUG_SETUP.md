# 🔐 Supabase Auth Debug Setup - Complete

## ✅ What Was Added

1. **`frontend/src/components/AuthDebug.jsx`** - React component for Supabase sign-in testing
2. **Route added**: `/auth-debug` in `AppRouter.jsx`

## 🧪 How to Test

### Step 1: Start the Frontend
```bash
cd frontend
npm run dev
```

### Step 2: Visit the Auth Debug Page
Navigate to: **http://localhost:5173/auth-debug**

### Step 3: Log In with Supabase Credentials
1. Enter an email/password that exists in your Supabase Auth dashboard
2. Click "Login"
3. You should see: `✅ Logged in as [email]`

### Step 4: Test debugAuth() in Console
After logging in, open browser console and run:
```js
debugAuth()
```

### Expected Output (Success):
```
🧠 Supabase Auth Debug
✅ Supabase session found
user: {id: "...", email: "..."}
token (first 40): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
✅ Backend authorized response: {user: {...}}
```

### Expected Output (If Not Logged In):
```
🧠 Supabase Auth Debug
⚠️ No active Supabase session — log in first.
```

### Expected Output (If Backend JWT Secret Mismatch):
```
🧠 Supabase Auth Debug
✅ Supabase session found
user: {id: "...", email: "..."}
token (first 40): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
❌ Backend rejected token: 401 {detail: "Not authenticated"}
```

## ✅ Verification Checklist

- [x] `AuthDebug.jsx` component created
- [x] Route `/auth-debug` added to router
- [x] `debugAuth()` still available globally (check main.jsx)
- [x] Component uses `signInWithPassword()` for email/password auth
- [x] Component has logout functionality

## 📝 Notes

- Make sure you have a user created in Supabase Auth dashboard
- The JWT secret in backend `.env` must match your Supabase project's JWT secret
- Session persists across tabs (Supabase client configured with `persistSession: true`)

