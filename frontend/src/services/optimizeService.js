import { apiGet } from "./apiClient";

export async function getRecommendations(){
  const r = await apiGet("/api/v1/optimize/recommendations");
  return r || [];
}

