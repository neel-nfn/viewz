import { apiGet } from "./apiClient";

export async function getChannelSnapshot(params={}) {
  const days = params.days || params.window || 7;
  const forceRefresh = params.forceRefresh || false;
  const url = `/api/v1/analytics/channel_snapshot?days=${days}${forceRefresh ? '&force_refresh=true' : ''}`;
  return await apiGet(url);
}

export async function getTrends(days = 7, forceRefresh = false) {
  const url = `/api/v1/analytics/trends?days=${days}${forceRefresh ? '&force_refresh=true' : ''}`;
  const result = await apiGet(url);
  return result;
}

export async function getTopVideos(limit = 5, forceRefresh = false) {
  const url = `/api/v1/analytics/top_videos?limit=${limit}${forceRefresh ? '&force_refresh=true' : ''}`;
  const result = await apiGet(url);
  return result;
}

export async function getAIInsights() {
  const result = await apiGet("/api/v1/analytics/ai_insights");
  return result;
}

export async function getKeywords(q) {
  return await apiGet(`/api/v1/analytics/keywords?q=${encodeURIComponent(q)}`);
}

export async function getRecommendations(params={}) {
  const result = await apiGet("/api/v1/analytics/recommendations");
  // Handle new structure: { mock, source, data } or old array format
  if (result && typeof result === 'object' && 'data' in result) {
    return result.data || [];
  }
  return Array.isArray(result) ? result : [];
}

export async function getTasksToday() {
  return await apiGet("/api/v1/tasks/today");
}
