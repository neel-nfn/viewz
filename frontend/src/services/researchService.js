import { apiPost } from './apiClient';

export async function scoreIdea({ orgId, channelId, title, url }) {
  const data = await apiPost('/api/v1/research/score', {
    org_id: orgId,
    channel_id: channelId,
    title,
    url
  });
  return data;
}

