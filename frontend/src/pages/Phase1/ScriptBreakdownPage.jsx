import { useState } from "react";
import {
  createScript,
  autoMatchLine,
  generateResearchRequests,
  getScript,
  getScriptLines,
} from "../../services/phase1Service";

export default function ScriptBreakdownPage() {
  const [title, setTitle] = useState("");
  const [sourceText, setSourceText] = useState("");
  const [scriptIdInput, setScriptIdInput] = useState("");
  const [script, setScript] = useState(null);
  const [lines, setLines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadScript(scriptId) {
    if (!scriptId) return;
    setLoading(true);
    setError("");
    try {
      const data = await getScript(scriptId);
      setScript(data);
      const lineData = await getScriptLines(scriptId);
      setLines(lineData);
    } catch (err) {
      setError(err.message || "Failed to load script");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const created = await createScript({ title, source_text: sourceText });
      setScriptIdInput(created.script_id);
      await loadScript(created.script_id);
    } catch (err) {
      setError(err.message || "Failed to create script");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate() {
    if (!script?.script_id) return;
    setLoading(true);
    setError("");
    try {
      await generateResearchRequests(script.script_id);
      await loadScript(script.script_id);
    } catch (err) {
      setError(err.message || "Failed to generate research requests");
    } finally {
      setLoading(false);
    }
  }

  async function handleAutoMatch(lineId) {
    setLoading(true);
    setError("");
    try {
      await autoMatchLine(lineId);
      if (script?.script_id) {
        await loadScript(script.script_id);
      }
    } catch (err) {
      setError(err.message || "Failed to auto-match line");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Script Breakdown</h1>
        <p className="text-sm opacity-70">Source text drives the rest of the workflow.</p>
      </div>

      <form onSubmit={handleCreate} className="space-y-3 rounded border p-4">
        <div className="grid gap-3 md:grid-cols-2">
          <input
            className="rounded border px-3 py-2"
            placeholder="Script title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input
            className="rounded border px-3 py-2"
            placeholder="Load script by ID"
            value={scriptIdInput}
            onChange={(e) => setScriptIdInput(e.target.value)}
          />
        </div>
        <textarea
          className="min-h-40 w-full rounded border px-3 py-2"
          placeholder="Paste the full script here"
          value={sourceText}
          onChange={(e) => setSourceText(e.target.value)}
        />
        <div className="flex gap-3">
          <button className="rounded bg-black px-4 py-2 text-white" type="submit" disabled={loading}>
            Create Script
          </button>
          <button
            className="rounded border px-4 py-2"
            type="button"
            onClick={() => loadScript(scriptIdInput)}
            disabled={loading || !scriptIdInput}
          >
            Load Script
          </button>
          <button
            className="rounded border px-4 py-2"
            type="button"
            onClick={handleGenerate}
            disabled={loading || !script?.script_id}
          >
            Generate Research Requests
          </button>
        </div>
      </form>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}

      {script ? (
        <div className="space-y-3 rounded border p-4">
          <div>
            <div className="text-lg font-semibold">{script.title}</div>
            <div className="text-xs opacity-70">ID: {script.script_id}</div>
          </div>
          <div className="space-y-2">
            {(script.lines || lines || []).map((line) => (
              <div key={line.id} className="rounded border p-3">
              <div className="text-xs opacity-70">Line {line.line_number}</div>
              <div className="font-medium">{line.raw_text}</div>
              <div className="mt-2 text-sm">
                Status: <span className="font-semibold">{line.status}</span>
              </div>
              <div className="text-xs opacity-70">
                Request: {line.research_request_id || "none"} | Asset: {line.matched_asset_id || "none"}
              </div>
              <div className="text-xs opacity-70">
                Suggested asset: {line.suggested_asset_id || "none"} | Confidence: {line.suggested_match_confidence ?? "n/a"}
              </div>
              {line.suggestion_notes ? <div className="mt-1 text-xs opacity-70">{line.suggestion_notes}</div> : null}
              <div className="mt-3">
                <button
                  className="rounded border px-3 py-1 text-sm"
                  type="button"
                  onClick={() => handleAutoMatch(line.id)}
                  disabled={loading}
                >
                  Auto-match
                </button>
              </div>
            </div>
          ))}
        </div>
        </div>
      ) : null}

      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}
    </div>
  );
}
