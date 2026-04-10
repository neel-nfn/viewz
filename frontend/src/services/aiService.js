import { apiPost, apiGet } from './apiClient';

export async function generateSEO({ orgId, taskId, topic, persona = "Max" }) {
  const data = await apiPost('/api/v1/ai/seo', {
    org_id: orgId,
    task_id: taskId,
    mode: "seo",
    topic,
    persona
  });
  return data;
}

export async function getAIUsage() {
  const data = await apiGet('/api/v1/ai/usage');
  return data;
}
