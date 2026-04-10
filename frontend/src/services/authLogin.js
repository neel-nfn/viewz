const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/,"");

export async function authLogin(state = "/app") {
  console.log("[AUTH-DEBUG] authLogin called with state:", state);
  const url = `${API_BASE}/api/v1/auth/login${state ? `?state=${encodeURIComponent(state)}` : ""}`;
  console.log("[AUTH-DEBUG] Redirecting browser to:", url);
  // Direct browser redirect - let the backend handle the 307 to Google
  window.location.href = url;
}
