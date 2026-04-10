import { apiGet, apiPost } from "./apiClient";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/,"");

export async function startGoogleLogin(state) {
  // #region agent log
  fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authService.js:5',message:'startGoogleLogin called',data:{state,apiBase:API_BASE},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'LOGIN'})}).catch(()=>{});
  // #endregion
  console.log("[AUTH-DEBUG] startGoogleLogin called with state:", state);
  const url = `${API_BASE}/api/v1/auth/login${state ? `?state=${encodeURIComponent(state)}` : ""}`;
  console.log("[AUTH-DEBUG] Checking OAuth status before redirect...");
  
  // First check if OAuth is enabled (try to get response as JSON first)
  try {
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authService.js:12',message:'fetching OAuth login endpoint',data:{url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'LOGIN'})}).catch(()=>{});
    // #endregion
    const response = await fetch(url, {
      method: 'GET',
      redirect: 'manual', // Don't follow redirects automatically
    });
    
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authService.js:19',message:'OAuth login response received',data:{status:response.status,isRedirect:response.status>=300&&response.status<400,contentType:response.headers.get('content-type')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'LOGIN'})}).catch(()=>{});
    // #endregion
    
    // If it's a redirect (3xx), follow it
    if (response.status >= 300 && response.status < 400) {
      const redirectUrl = response.headers.get('Location');
      if (redirectUrl) {
        console.log("[AUTH-DEBUG] Redirecting to:", redirectUrl);
        // #region agent log
        fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authService.js:23',message:'redirecting to Google OAuth',data:{redirectUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'LOGIN'})}).catch(()=>{});
        // #endregion
        window.location.href = redirectUrl;
        return;
      }
    }
    
    // If it's JSON (OAuth disabled), handle it
    if (response.headers.get('content-type')?.includes('application/json')) {
      const data = await response.json();
      if (data.oauth_skipped_in_local) {
        // #region agent log
        fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authService.js:30',message:'OAuth disabled in local - showing alert',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'LOGIN'})}).catch(()=>{});
        // #endregion
        alert(`OAuth is disabled in local development.\n\nTo enable:\n1. Set OAUTH_ENABLED=true in backend/.env\n2. Add Google OAuth credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)\n3. Restart backend`);
        console.warn("[AUTH-DEBUG] OAuth skipped in local:", data);
        return;
      }
    }
    
    // Fallback: if we get here, just redirect
    console.log("[AUTH-DEBUG] Redirecting browser to:", url);
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authService.js:38',message:'fallback redirect to login URL',data:{url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'LOGIN'})}).catch(()=>{});
    // #endregion
    window.location.href = url;
  } catch (error) {
    // If fetch fails, fall back to direct redirect
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authService.js:41',message:'fetch failed, using direct redirect',data:{errorMessage:error.message},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'LOGIN'})}).catch(()=>{});
    // #endregion
    console.warn("[AUTH-DEBUG] Fetch check failed, using direct redirect:", error);
    window.location.href = url;
  }
}

export async function completeOAuthCallback(queryString) {
  try {
    const result = await apiGet(`/api/v1/auth/callback${queryString}`, {
      headers: {
        "X-Debug-Caller": "authService.completeOAuthCallback",
      },
    });
    // Check if OAuth was skipped in local dev
    if (result.status === "oauth_skipped_in_local") {
      console.warn("[AUTH-DEBUG] OAuth skipped in local, using Supabase session only.");
      // Return a success-like response so the callback page doesn't error
      return { 
        success: true, 
        message: result.message || "OAuth is disabled in local dev. Using Supabase auth only.",
        oauth_skipped: true 
      };
    }
    return result;
  } catch (error) {
    // If backend returns 401 or 500, check if it's OAuth-related
    if (error.response?.status === 401 || error.response?.status === 500) {
      const errorDetail = error.response?.data?.detail || "";
      if (errorDetail.includes("oauth") || errorDetail.includes("google creds") || error.response?.status === 401) {
        console.warn("[AUTH-DEBUG] OAuth not configured, skipping callback");
        return { 
          success: true, 
          message: "OAuth is disabled in local dev. Using Supabase auth only.",
          oauth_skipped: true 
        };
      }
    }
    // For any other error, still return a graceful response instead of throwing
    console.error("[AUTH-DEBUG] Callback error:", error);
    return {
      success: false,
      message: "OAuth callback failed. You are still authenticated via Supabase.",
      oauth_skipped: true,
      error: error.message
    };
  }
}

export async function fetchMe() {
  return apiGet("/api/v1/auth/me");
}

export async function getMe() {
  return await apiGet("/api/v1/auth/me");
}

export async function logout() {
  // Call backend logout endpoint first (clears session cookie)
  try {
    await apiGet("/api/v1/auth/logout");
    console.log("[AUTH] Backend logout successful");
  } catch (error) {
    // Backend logout endpoint may not exist, that's okay
    console.warn("[AUTH] Backend logout failed, continuing anyway", error);
  }
  
  // Clear Supabase session
  try {
    const { supabase } = await import("../lib/supabaseClient");
    await supabase.auth.signOut();
  } catch (error) {
    console.error("[AUTH] Error signing out from Supabase:", error);
  }
  
  // Clear local state
  localStorage.clear();
  sessionStorage.clear();
}
