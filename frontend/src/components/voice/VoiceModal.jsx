import React, { useState } from "react";
import { voiceGenerate, voiceStatus } from "../../services/voiceService";
import Loader from "../ui/Loader";

export default function VoiceModal({ open, onClose, taskId, channelId, role }) {
  const [text, setText] = useState("");
  const [job, setJob] = useState(null);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [providerUnavailable, setProviderUnavailable] = useState(false);

  const canVoice = role === "admin" || role === "manager" || role === "editor";

  async function onGenerate() {
    if (!canVoice) return;
    const res = await voiceGenerate({ task_id: taskId, channel_id: channelId, voice_id: "default", text });
    setJob(res);
    if (res && res.status === "provider_unavailable") {
      setProviderUnavailable(true);
      setErr("Voice provider not configured. Add ElevenLabs key.");
    } else {
      setMsg("Voice job queued.");
    }
  }

  async function onCheck() {
    if (!job) return;
    const res = await voiceStatus(job.job_id);
    setJob(res);
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="w-full max-w-lg bg-base-100 p-4 rounded-box">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Generate Voice</h2>
          <button className="btn btn-sm" onClick={onClose}>Close</button>
        </div>
        <textarea className="textarea textarea-bordered w-full" rows="6" placeholder="Paste script text to synthesize…" value={text} onChange={e=>setText(e.target.value)} />
        <div className="text-xs opacity-70 mt-1">{(text||"").length} chars</div>
        <div className="mt-3 flex gap-2 items-center">
          <button className="btn btn-primary" onClick={onGenerate} disabled={!canVoice || !text || text.trim().length < 10}>Generate</button>
          <button className="btn" onClick={onCheck} disabled={!job}>Check Status</button>
        </div>
        {providerUnavailable ? (
          <div className="mt-3 alert alert-warning">Voice provider not configured. Add your ElevenLabs API key in backend/.env to enable voice.</div>
        ) : null}
        {msg ? <div className="mt-3 alert alert-success py-2">{msg}</div> : null}
        {err ? <div className="mt-3 alert alert-error py-2">{err}</div> : null}
        {job && job.output_url ? <audio className="mt-4 w-full" controls src={job.output_url} /> : null}
      </div>
    </div>
  );
}

