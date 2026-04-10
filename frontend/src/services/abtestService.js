import { apiPost } from "./apiClient";

export async function startABTest(payload){
  const r = await apiPost("/api/v1/abtest/start", payload);
  return r;
}

