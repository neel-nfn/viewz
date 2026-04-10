import { apiGet, apiPost } from "./apiClient";

export async function voiceGenerate({ task_id, channel_id, voice_id, text }) {
  if (import.meta.env.VITE_AI_DEV === "1") {
    return { job_id: "voice-dev", status: "queued" };
  }
  return await apiPost("/api/v1/voice/generate", { task_id, channel_id, voice_id, text });
}

export async function voiceStatus(job_id) {
  if (import.meta.env.VITE_AI_DEV === "1") {
    return { job_id, status: "succeeded", output_url: "https://storage.local/voice/dev.mp3" };
  }
  return await apiGet(`/api/v1/voice/status/${job_id}`);
}

