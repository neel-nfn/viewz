import { apiGet } from "./apiClient";
import { getApiBase } from "../lib/apiBase";
import { DEMO_MODE } from "../utils/constants";
import { isSupabaseConfigured } from "../lib/supabaseClient";

const API_BASE = getApiBase();

export async function startGoogleLogin(state) {
  console.log("[AUTH-DEBUG] startGoogleLogin called with state:", state);

  if (DEMO_MODE || !isSupabaseConfigured) {
    if (window.location.pathname === "/login") {
      window.location.href = "/app";
      return;
    }

    alert("Google OAuth is unavailable because Supabase env vars are missing in this deployment. Demo auth is active.");
    return;
  }

  const url = `${API_BASE}/api/v1/auth/login${state ? `?state=${encodeURIComponent(state)}` : ""}`;
  console.log("[AUTH-DEBUG] Checking OAuth status before redirect...");

  try {
    const response = await fetch(url, {
      method: "GET",
      redirect: "manual",
    });

    if (response.status >= 300 && response.status < 400) {
      const redirectUrl = response.headers.get("Location");
      if (redirectUrl) {
        console.log("[AUTH-DEBUG] Redirecting to:", redirectUrl);
        window.location.href = redirectUrl;
        return;
      }
    }

    if (response.headers.get("content-type")?.includes("application/json")) {
      const data = await response.json();
      if (data.oauth_skipped_in_local) {
        alert(`OAuth is disabled in local development.\n\nTo enable:\n1. Set OAUTH_ENABLED=true in backend/.env\n2. Add Google OAuth credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)\n3. Restart backend`);
        console.warn("[AUTH-DEBUG] OAuth skipped in local:", data);
        return;
      }
    }

    console.log("[AUTH-DEBUG] Redirecting browser to:", url);
    window.location.href = url;
  } catch (error) {
    console.warn("[AUTH-DEBUG] Fetch check failed, using direct redirect:", error);
    window.location.href = url;
  }
}

export async function completeOAuthCallback(queryString) {
  const params = new URLSearchParams(queryString);
  const callbackError = params.get("error");
  const callbackMessage = params.get("error_description") || callbackError || "oauth_callback_failed";

  if (callbackError) {
    return {
      success: false,
      oauth_skipped: true,
      error: callbackError,
      message: callbackMessage,
    };
  }

  try {
    const result = await apiGet(`/api/v1/auth/callback${queryString}`, {
      headers: {
        "X-Debug-Caller": "authService.completeOAuthCallback",
      },
    });

    if (result.status === "oauth_skipped_in_local") {
      console.warn("[AUTH-DEBUG] OAuth skipped in local, using Supabase session only.");
      return {
        success: true,
        message: result.message || "OAuth is disabled in local dev. Using Supabase auth only.",
        oauth_skipped: true,
      };
    }

    return result;
  } catch (error) {
    if (error.response?.status === 401 || error.response?.status === 500) {
      const errorDetail = error.response?.data?.detail || "";
      if (errorDetail.includes("oauth") || errorDetail.includes("google creds") || error.response?.status === 401) {
        console.warn("[AUTH-DEBUG] OAuth not configured, skipping callback");
        return {
          success: false,
          message: "OAuth is disabled in local dev. Using Supabase auth only.",
          oauth_skipped: true,
          error: errorDetail || "oauth_not_configured",
        };
      }
    }

    console.error("[AUTH-DEBUG] Callback error:", error);
    return {
      success: false,
      message: "OAuth callback failed. You are still authenticated via Supabase.",
      oauth_skipped: true,
      error: error.message,
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
  try {
    await apiGet("/api/v1/auth/logout");
    console.log("[AUTH] Backend logout successful");
  } catch (error) {
    console.warn("[AUTH] Backend logout failed, continuing anyway", error);
  }

  try {
    const { supabase } = await import("../lib/supabaseClient");
    await supabase.auth.signOut();
  } catch (error) {
    console.error("[AUTH] Error signing out from Supabase:", error);
  }

  localStorage.clear();
  sessionStorage.clear();
}
