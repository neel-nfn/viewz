import { apiGet } from "./apiClient";

export async function getUsage(){
  const r = await apiGet("/api/v1/billing/usage");
  return r;
}

export async function getPlanLimit(){
  const r = await apiGet("/api/v1/billing/plan_limit");
  return r?.ai_credit_limit || 100;
}

