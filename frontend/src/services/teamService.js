// src/services/teamService.js
import { apiGet, apiPost } from "./apiClient";

export async function fetchTeam() {
  const data = await apiGet("/api/v1/team/list");
  return data.team ?? [];
}

export async function inviteUser({ email, role, assigned_channel_ids = [] }) {
  return await apiPost("/api/v1/team/invite", { email, role, assigned_channel_ids });
}

export async function acceptInvite(token) {
  return await apiPost("/api/v1/team/invite/accept", { token });
}
