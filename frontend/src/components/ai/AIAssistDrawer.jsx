import React, { useState } from "react";
import { aiGenerate, aiHistory } from "../../services/aiService";
import Loader from "../ui/Loader";

export default function AIAssistDrawer({ open, onClose, taskId, channelId, role }) {
  const [persona, setPersona] = useState("max");
  const [mode, setMode] = useState("script");
  const [prompt, setPrompt] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [history, setHistory] = useState([]);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const canGenerate = role === "admin" || role === "manager" || role === "writer";

  async function loadHistory() {
    const res = await aiHistory(taskId || "dev-task");
    setHistory(res.items || []);
  }

  async function onGenerate() {
    setSuccessMsg(""); setErrorMsg("");
    if (!prompt || prompt.trim().length < 10) {
      setErrorMsg("Please provide at least 10 characters of context.");
      return;
    }
    if (!canGenerate) return;
    setSubmitting(true);
    try {
      const res = await aiGenerate({ task_id: taskId, channel_id: channelId, persona, mode, prompt });
      setSubmitting(false);
      if (res && res.status === "succeeded") {
        setSuccessMsg("Generated successfully.");
      } else {
        setErrorMsg("Generation failed.");
      }
      await loadHistory();
    } catch (err) {
      setSubmitting(false);
      setErrorMsg("Generation failed.");
    }
  }

  React.useEffect(() => {
    if (open) loadHistory();
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex justify-end" aria-modal="true" role="dialog" data-drawer>
      <div className="w-full max-w-md bg-base-100 h-full p-4 overflow-y-auto transition-transform duration-200 ease-out translate-x-0">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">AI Assist</h2>
          <button className="btn btn-sm" onClick={onClose}>Close</button>
        </div>
        <div className="space-y-3">
          <div className="form-control">
            <label className="label"><span className="label-text">Persona</span></label>
            <select className="select select-bordered" value={persona} onChange={e=>setPersona(e.target.value)}>
              <option value="max">Max (Narrator)</option>
              <option value="lolo">Lolo (Hype)</option>
              <option value="loki">Loki (Analyst)</option>
            </select>
          </div>
          <div className="form-control">
            <label className="label"><span className="label-text">Mode</span></label>
            <select className="select select-bordered" value={mode} onChange={e=>setMode(e.target.value)}>
              <option value="script">Script</option>
              <option value="seo">SEO</option>
              <option value="thumbnail_prompt">Thumbnail Prompt</option>
            </select>
          </div>
          <textarea className="textarea textarea-bordered w-full" rows="5" placeholder="Describe the video context…" value={prompt} onChange={e=>setPrompt(e.target.value)} />
          <div className="space-y-2">
            {successMsg ? <div className="alert alert-success py-2">{successMsg}</div> : null}
            {errorMsg ? <div className="alert alert-warning py-2">{errorMsg}</div> : null}
          </div>
          <button className="btn btn-primary w-full" disabled={!canGenerate || submitting} onClick={onGenerate}>
            {submitting ? (
              <span className="inline-flex items-center gap-2">
                <span className="loading loading-spinner loading-xs" />
                Generating…
              </span>
            ) : "Generate"}
          </button>
          <div className="divider">History</div>
          <ul className="space-y-2">
            {history.map(h => (
              <li key={h.id} className="p-2 border rounded">
                <div className="text-sm opacity-70">{h.created_at} • {h.persona.toUpperCase()} • {h.mode}</div>
                <div className="truncate">{h.prompt_preview}</div>
                <div className="text-xs opacity-70">Model: {h.model_used || "unknown"} • Status: {h.status}</div>
                {h.output_url ? <a className="link" href={h.output_url} target="_blank" rel="noopener noreferrer">Open Output</a> : null}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

