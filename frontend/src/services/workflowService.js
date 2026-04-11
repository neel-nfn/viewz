import { apiGet, apiPost, apiPut, apiDelete } from './apiClient';

/**
 * List all workflow cards
 * @returns {Promise<Object>} List of workflow cards
 */
export async function listWorkflowCards() {
  return await apiGet('/api/v1/workflow/cards');
}

/**
 * Create a new workflow card
 * @param {Object} cardData - Card data
 * @param {string} cardData.title - Card title
 * @param {string} [cardData.description] - Card description
 * @param {string} [cardData.meta] - Card metadata
 * @param {string} [cardData.stage='ideas'] - Initial stage
 * @param {string[]} [cardData.tags=[]] - Tags
 * @param {string} [cardData.topic_idea_id] - Linked topic idea ID
 * @returns {Promise<Object>} Created card
 */
export async function createWorkflowCard(cardData) {
  return await apiPost('/api/v1/workflow/cards', cardData);
}

/**
 * Update a workflow card
 * @param {string} cardId - Card ID
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} Updated card
 */
export async function updateWorkflowCard(cardId, updates) {
  return await apiPut(`/api/v1/workflow/cards/${cardId}`, updates);
}

/**
 * Move a workflow card to a new stage
 * @param {string} cardId - Card ID
 * @param {string} stage - New stage
 * @returns {Promise<Object>} Updated card
 */
export async function moveWorkflowCardStage(cardId, stage) {
  return await apiPut(`/api/v1/workflow/cards/${cardId}/stage`, { stage });
}

/**
 * Delete a workflow card
 * @param {string} cardId - Card ID
 * @returns {Promise<Object>} Delete result
 */
export async function deleteWorkflowCard(cardId) {
  return await apiDelete(`/api/v1/workflow/cards/${cardId}`);
}

