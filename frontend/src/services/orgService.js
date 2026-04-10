import { apiPost } from "./apiClient";

export async function switchOrg(orgId){
  const r = await apiPost("/api/v1/org/switch", { org_id: orgId });
  return r;
}

