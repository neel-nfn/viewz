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

export function createOperatorJob(payload) {
  return request("/operator/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createOperatorJobFromApprovedSubmissions(payload) {
  return request("/operator/jobs/from-approved-submissions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listOperatorJobs() {
  return request("/operator/jobs");
}

export function getOperatorJob(jobId) {
  return request(`/operator/jobs/${jobId}`);
}

export function startOperatorJob(jobId) {
  return request(`/operator/jobs/${jobId}/start`, {
    method: "POST",
  });
}

export function processOperatorJobItem(jobId, operatorJobItemId, storageProvider) {
  return request(`/operator/jobs/${jobId}/process-item`, {
    method: "POST",
    body: JSON.stringify({
      operator_job_item_id: operatorJobItemId,
      storage_provider: storageProvider || null,
    }),
  });
}

export function completeOperatorJob(jobId) {
  return request(`/operator/jobs/${jobId}/complete`, {
    method: "POST",
  });
}

export function retryFailedOperatorJob(jobId) {
  return request(`/operator/jobs/${jobId}/retry-failed`, {
    method: "POST",
  });
}

export function testStorageProvider(provider, objectName = "probe.mp4") {
  return request("/storage/test-provider", {
    method: "POST",
    body: JSON.stringify({ provider, object_name: objectName }),
  });
}

export function listStorageObjects() {
  return request("/storage/objects");
}

export function getActiveFilenameRule() {
  return request("/filename/rules/active");
}

export function listFilenameRules() {
  return request("/filename/rules");
}

export function previewFilename(payload) {
  return request("/filename/preview", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function validateFilename(payload) {
  return request("/filename/validate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function registerAssetFingerprint(assetId, payload) {
  return request(`/assets/${assetId}/fingerprint`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAssetIntegrity(assetId) {
  return request(`/assets/${assetId}/integrity`);
}

export function startWorker() {
  return request("/worker/start", {
    method: "POST",
  });
}

export function stopWorker() {
  return request("/worker/stop", {
    method: "POST",
  });
}

export function getWorkerStatus() {
  return request("/worker/status");
}
