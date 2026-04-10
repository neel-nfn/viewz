import { useState } from "react";
import {
  generateInstruction,
  getInstruction,
  getScript,
  getScriptLines,
  updateInstruction,
} from "../../services/phase1Service";

function prettyJson(value) {
  try {
    return JSON.stringify(value ?? {}, null, 2);
  } catch {
    return "{}";
  }
}

export default function EditorInstructionsPage() {
  const [scriptIdInput, setScriptIdInput] = useState("");
  const [script, setScript] = useState(null);
  const [lines, setLines] = useState([]);
  const [bundles, setBundles] = useState({});
  const [drafts, setDrafts] = useState({});
  const [lineErrors, setLineErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadScript(scriptId) {
    if (!scriptId) return;
    setLoading(true);
    setError("");
    try {
      const scriptData = await getScript(scriptId);
      const lineData = await getScriptLines(scriptId);
      setScript(scriptData);
      setLines(lineData || []);

      const results = await Promise.all(
        (lineData || []).map(async (line) => {
          try {
            const instruction = await getInstruction(line.id);
            return [line.id, instruction];
          } catch {
            return [line.id, null];
          }
        }),
      );

      const nextBundles = {};
      const nextDrafts = {};
      for (const [lineId, bundle] of results) {
        if (bundle) {
          nextBundles[lineId] = bundle;
          nextDrafts[lineId] = prettyJson(bundle.instruction_json);
        }
      }
      setBundles(nextBundles);
      setDrafts(nextDrafts);
      setLineErrors({});
    } catch (err) {
      setError(err.message || "Failed to load script");
    } finally {
      setLoading(false);
    }
  }

  function syncBundle(lineId, bundle) {
    setBundles((current) => ({ ...current, [lineId]: bundle }));
    setDrafts((current) => ({
      ...current,
      [lineId]: prettyJson(bundle.instruction_json),
    }));
    setLineErrors((current) => ({ ...current, [lineId]: "" }));
  }

  async function handleGenerate(lineId) {
    setLoading(true);
    setError("");
    try {
      const bundle = await generateInstruction(lineId);
      syncBundle(lineId, bundle);
    } catch (err) {
      setLineErrors((current) => ({ ...current, [lineId]: err.message || "Generate failed" }));
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(lineId, nextStatus = "OVERRIDDEN") {
    setLoading(true);
    setError("");
    setLineErrors((current) => ({ ...current, [lineId]: "" }));
    try {
      const bundle = bundles[lineId];
      if (!bundle?.instruction_id) {
        throw new Error("Generate the instruction first");
      }
      const parsed = JSON.parse(drafts[lineId] || "{}");
      const updated = await updateInstruction({
        instruction_id: bundle.instruction_id,
        instruction_json: parsed,
        instruction_text: null,
        status: nextStatus,
      });
      syncBundle(lineId, updated);
    } catch (err) {
      setLineErrors((current) => ({ ...current, [lineId]: err.message || "Save failed" }));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Editor Instructions</h1>
        <p className="text-sm opacity-70">Generate and approve editor-ready instructions per linked line.</p>
      </div>

      <form
        className="rounded border p-4 space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          loadScript(scriptIdInput);
        }}
      >
        <div className="flex gap-3">
          <input
            className="flex-1 rounded border px-3 py-2"
            placeholder="Script ID"
            value={scriptIdInput}
            onChange={(e) => setScriptIdInput(e.target.value)}
          />
          <button className="rounded bg-black px-4 py-2 text-white" type="submit" disabled={loading}>
            Load Script
          </button>
        </div>
      </form>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      {script ? (
        <div className="space-y-4">
          <div className="rounded border p-4">
            <div className="text-lg font-semibold">{script.title}</div>
            <div className="text-xs opacity-70">ID: {script.script_id}</div>
          </div>

          <div className="space-y-4">
            {(lines || []).map((line) => {
              const bundle = bundles[line.id];
              const draft = drafts[line.id] ?? "";
              const lineError = lineErrors[line.id];
              return (
                <div key={line.id} className="rounded border p-4 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-xs uppercase tracking-wide opacity-70">Line {line.line_number}</div>
                      <div className="font-medium">{line.raw_text}</div>
                    </div>
                    <div className="text-xs uppercase tracking-wide opacity-70">{line.status}</div>
                  </div>

                  <div className="text-sm opacity-80">
                    Linked asset: {bundle?.asset_filename || line.matched_asset_id || "none"}
                  </div>

                  {bundle ? (
                    <div className="space-y-3">
                      <div className="rounded bg-gray-50 p-3 text-sm space-y-1">
                        <div><span className="font-semibold">Instruction status:</span> {bundle.status}</div>
                        <div><span className="font-semibold">Readable:</span> {bundle.instruction_text}</div>
                        <div><span className="font-semibold">Clip:</span> {bundle.clip_start}s for {bundle.clip_duration}s</div>
                      </div>

                      <textarea
                        className="min-h-44 w-full rounded border px-3 py-2 font-mono text-sm"
                        value={draft}
                        onChange={(e) => setDrafts((current) => ({ ...current, [line.id]: e.target.value }))}
                      />

                      {lineError ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700 text-sm">{lineError}</div> : null}

                      <div className="flex flex-wrap gap-2">
                        <button
                          className="rounded border px-4 py-2"
                          type="button"
                          onClick={() => handleGenerate(line.id)}
                          disabled={loading || line.status !== "LINKED"}
                        >
                          Regenerate
                        </button>
                        <button
                          className="rounded border px-4 py-2"
                          type="button"
                          onClick={() => handleSave(line.id, "OVERRIDDEN")}
                          disabled={loading}
                        >
                          Save Manual Edit
                        </button>
                        <button
                          className="rounded bg-black px-4 py-2 text-white"
                          type="button"
                          onClick={() => handleSave(line.id, "APPROVED")}
                          disabled={loading}
                        >
                          Approve
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="rounded bg-gray-50 p-3 text-sm">
                      No instruction yet.
                      <div className="mt-2">
                        <button
                          className="rounded bg-black px-4 py-2 text-white"
                          type="button"
                          onClick={() => handleGenerate(line.id)}
                          disabled={loading || line.status !== "LINKED"}
                        >
                          Generate Instruction
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
}
