import api, { apiGet, apiPost, apiDelete } from './apiClient';

/**
 * Add a competitor channel
 * @param {string} youtubeChannelUrlOrId - YouTube channel URL or ID
 * @returns {Promise<Object>} Competitor details
 */
export async function addCompetitor(youtubeChannelUrlOrId) {
  return await apiPost('/api/v1/competitors/add', {
    youtube_channel_url_or_id: youtubeChannelUrlOrId
  });
}

/**
 * Get list of all competitors
 * @returns {Promise<Object>} List of competitors
 */
export async function listCompetitors() {
  return await apiGet('/api/v1/competitors/list');
}

/**
 * Delete a competitor
 * @param {string} competitorId - Competitor ID
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteCompetitor(competitorId) {
  return await apiDelete(`/api/v1/competitors/${competitorId}`);
}

/**
 * Get top videos for a competitor
 * @param {string} competitorId - Competitor ID
 * @param {number} days - Time range in days (7, 30, or 90)
 * @returns {Promise<Object>} List of top videos
 */
export async function getCompetitorVideos(competitorId, days = 30) {
  return await apiGet(`/api/v1/competitors/${competitorId}/videos?days=${days}`);
}

/**
 * Save a video as a topic idea
 * @param {Object} videoData - Video details
 * @returns {Promise<Object>} Saved topic idea
 */
export async function saveTopicIdea(videoData) {
  return await apiPost('/api/v1/competitors/topic-ideas/save', videoData);
}

/**
 * List all saved topic ideas
 * @param {string} status - Optional status filter
 * @returns {Promise<Object>} List of topic ideas
 */
export async function listTopicIdeas(status = null) {
  const url = status
    ? `/api/v1/competitors/topic-ideas/list?status=${status}`
    : '/api/v1/competitors/topic-ideas/list';
  return await apiGet(url);
}

/**
 * Update topic idea status
 * @param {string} ideaId - Topic idea ID
 * @param {string} status - New status ('saved', 'to_script', 'in_progress', 'ignore')
 * @returns {Promise<Object>} Update result
 */
export async function updateTopicIdeaStatus(ideaId, status) {
  const { data } = await api.patch(`/api/v1/competitors/topic-ideas/${ideaId}/status`, { status });
  return data;
}

/**
 * Delete a topic idea
 * @param {string} ideaId - Topic idea ID
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteTopicIdea(ideaId) {
  return await apiDelete(`/api/v1/competitors/topic-ideas/${ideaId}`);
}

