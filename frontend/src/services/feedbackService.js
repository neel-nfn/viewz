import { apiPost, apiGet, apiPut } from "./apiClient";

export async function submitFeedback(payload) {
  return await apiPost("/api/v1/feedback_reports", payload);
}

export async function listFeedback(params = {}) {
  const query = new URLSearchParams();
  if (params.status) query.append("status", params.status);
  if (params.limit) query.append("limit", params.limit);
  if (params.offset) query.append("offset", params.offset);
  const qs = query.toString();
  return await apiGet(`/api/v1/feedback_reports${qs ? `?${qs}` : ""}`);
}

export async function updateFeedback(id, status) {
  return await apiPut(`/api/v1/feedback_reports/${id}`, { status });
}
