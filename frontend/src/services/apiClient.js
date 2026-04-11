import axios from "axios";
import { supabase } from "../lib/supabaseClient";
import { getApiBase } from "../lib/apiBase";

const API_BASE = getApiBase();

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // 👈 MUST be true for cookies to be sent
});

api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession();
  const token = data?.session?.access_token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to log all requests and errors
api.interceptors.response.use(
  (res) => {
    const url = res.config?.url || "";
    if (url.includes("/api/v1/auth/login") || url.includes("/api/v1/auth/callback")) {
      console.warn("[AUTH-DEBUG] OAuth endpoint was called:", {
        url,
        status: res.status,
        data: res.data,
        method: res.config?.method,
        caller: res.config?.headers?.["X-Debug-Caller"] || "unknown",
      });
    }
    return res;
  },
  (error) => {
    const url = error.config?.url || "";
    const fullUrl = error.config?.baseURL + url;
    
    console.log("[AUTH-DEBUG] request failed", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      withCredentials: error.config?.withCredentials,
      baseURL: error.config?.baseURL,
    });
    
    // Collect errors for audit
    window.__APP_ERRORS__ = window.__APP_ERRORS__ || [];
    window.__APP_ERRORS__.push({
      ts: Date.now(),
      url: fullUrl,
      method: error.config?.method || "GET",
      message: error.message,
      status: error.response?.status || 0,
      data: error.response?.data,
    });
    
    // Keep only last 50 errors
    if (window.__APP_ERRORS__.length > 50) {
      window.__APP_ERRORS__ = window.__APP_ERRORS__.slice(-50);
    }
    
    if (
      url.includes("/api/v1/auth/login") ||
      url.includes("/api/v1/auth/callback") ||
      error?.response?.status === 401
    ) {
      console.warn("[AUTH-DEBUG] 401 or OAuth call:", {
        url,
        status: error.response?.status,
        data: error.response?.data,
        method: error.config?.method,
        caller: error.config?.headers?.["X-Debug-Caller"] || "unknown",
      });
    }
    return Promise.reject(error);
  }
);

// Add convenience methods to api object
api.getTask = async (taskId) => {
  const { data } = await api.get(`/api/v1/tasks/${taskId}`, { withCredentials: true });
  return data;
};

api.updateTaskTitle = async (taskId, title) => {
  const { data } = await api.put(`/api/v1/tasks/${taskId}/title`, { title }, { withCredentials: true });
  return data;
};

export default api;
export { api }; // Named export for backward compatibility

// Helper functions - ensure withCredentials is always true
export async function apiGet(path, config = {}) {
  const { data } = await api.get(path, { withCredentials: true, ...config });
  return data;
}

export async function apiPost(path, body, config = {}) {
  const { data } = await api.post(path, body, { withCredentials: true, ...config });
  return data;
}

export async function apiPut(path, body, config = {}) {
  const { data } = await api.put(path, body, { withCredentials: true, ...config });
  return data;
}

export async function apiDelete(path, config = {}) {
  const { data } = await api.delete(path, { withCredentials: true, ...config });
  return data;
}
