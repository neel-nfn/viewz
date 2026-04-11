import { apiGet, apiPost } from "./apiClient";
import { getApiBase } from "../lib/apiBase";

const API_BASE = getApiBase();

export async function listChannels() {
  const r = await apiGet("/api/v1/channels/list");
  const d = r?.data || r; // Handle both {data: []} and [] formats
  return Array.isArray(d) ? d : [];
}

export async function revokeChannel(channelId) {
  const r = await apiPost("/api/v1/channels/revoke", { channel_id: channelId });
  return r;
}

export async function reconnect(state = "/app") {
  console.log("[AUTH-DEBUG] reconnect called with state:", state);
  const url = `${API_BASE}/api/v1/auth/login${state ? `?state=${encodeURIComponent(state)}` : ""}`;
  console.log("[AUTH-DEBUG] Checking OAuth status before redirect...");
  
  // First check if OAuth is enabled (try to get response as JSON first)
  try {
    const response = await fetch(url, {
      method: 'GET',
      redirect: 'manual', // Don't follow redirects automatically
    });
    
    // If it's a redirect (3xx), follow it
    if (response.status >= 300 && response.status < 400) {
      const redirectUrl = response.headers.get('Location');
      if (redirectUrl) {
        console.log("[AUTH-DEBUG] Redirecting to:", redirectUrl);
        window.location.href = redirectUrl;
        return;
      }
    }
    
    // If it's JSON (OAuth disabled), handle it
    if (response.headers.get('content-type')?.includes('application/json')) {
      const data = await response.json();
      if (data.oauth_skipped_in_local) {
        alert(`OAuth is disabled in local development.\n\nTo enable:\n1. Set OAUTH_ENABLED=true in backend/.env\n2. Add Google OAuth credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)\n3. Restart backend`);
        console.warn("[AUTH-DEBUG] OAuth skipped in local:", data);
        return;
      }
    }
    
    // Fallback: if we get here, just redirect
    console.log("[AUTH-DEBUG] Redirecting browser to:", url);
    window.location.href = url;
  } catch (error) {
    // If fetch fails, fall back to direct redirect
    console.warn("[AUTH-DEBUG] Fetch check failed, using direct redirect:", error);
    window.location.href = url;
  }
}
