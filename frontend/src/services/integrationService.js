import { apiGet, apiPost, apiDelete } from "./apiClient";

export async function getIntegrations() {
  return await apiGet("/api/v1/integrations");
}

export async function getYouTubeStatus() {
  return await apiGet("/api/v1/integrations/youtube/status");
}

export async function getYouTubeHealth() {
  return await apiGet("/api/v1/integrations/youtube/health");
}

export async function saveAIKey(apiKey, provider = "gemini") {
  return await apiPost("/api/v1/integrations/ai_key", { api_key: apiKey, provider });
}

export async function deleteAIKey(provider = "gemini") {
  return await apiDelete(`/api/v1/integrations/ai_key?provider=${provider}`);
}

