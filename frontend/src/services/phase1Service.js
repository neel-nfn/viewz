const API_BASE = "/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const message = data?.detail || data?.message || `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return data;
}

export function createScript(payload) {
  return request("/scripts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getScript(scriptId) {
  return request(`/scripts/${scriptId}`);
}

export function getScriptLines(scriptId) {
  return request(`/scripts/${scriptId}/lines`);
}

export function generateResearchRequests(scriptId, assignedTo) {
  return request("/research/request/generate", {
    method: "POST",
    body: JSON.stringify({ script_id: scriptId, assigned_to: assignedTo || null }),
  });
}

export function listResearchRequests() {
  return request("/research/requests");
}

export function submitResearch(payload) {
  return request("/research/submit", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function approveResearch(researchSubmissionId) {
  return request("/research/approve", {
    method: "POST",
    body: JSON.stringify({ research_submission_id: researchSubmissionId }),
  });
}

export function rejectResearch(researchSubmissionId) {
  return request("/research/reject", {
    method: "POST",
    body: JSON.stringify({ research_submission_id: researchSubmissionId }),
  });
}

export function listAssets() {
  return request("/assets");
}

export function validateAsset(assetId, validationType = "manual", notes = "") {
  return request("/assets/validate", {
    method: "POST",
    body: JSON.stringify({ asset_id: assetId, validation_type: validationType, notes }),
  });
}

export function autoMatchLine(scriptLineId) {
  return request("/lines/auto-match", {
    method: "POST",
    body: JSON.stringify({ script_line_id: scriptLineId }),
  });
}

export function linkAssetToLine(payload) {
  return request("/line/link-asset", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateInstruction(scriptLineId) {
  return request("/instructions/generate", {
    method: "POST",
    body: JSON.stringify({ script_line_id: scriptLineId }),
  });
}

export function getInstruction(scriptLineId) {
  return request(`/instructions/${scriptLineId}`);
}

export function updateInstruction(payload) {
  return request("/instructions/update", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
