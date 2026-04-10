import { useEffect, useState } from "react";
import { getActiveFilenameRule, listFilenameRules, previewFilename, validateFilename } from "../../services/phase4Service";

export default function FilenameRulesPage() {
  const [activeRule, setActiveRule] = useState(null);
  const [rules, setRules] = useState([]);
  const [preview, setPreview] = useState(null);
  const [validation, setValidation] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    script_title: "",
    line_number: 1,
    keyword: "",
    asset_id: "",
    source_url: "",
    extension: "mp4",
    candidate_filename: "",
  });

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [active, allRules] = await Promise.all([getActiveFilenameRule(), listFilenameRules()]);
      setActiveRule(active);
      setRules(allRules.items || []);
    } catch (err) {
      setError(err.message || "Failed to load filename rules");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handlePreview() {
    setLoading(true);
    setError("");
    try {
      const data = await previewFilename({
        script_title: form.script_title,
        line_number: Number(form.line_number || 0),
        keyword: form.keyword,
        asset_id: form.asset_id,
        source_url: form.source_url,
        extension: form.extension || "mp4",
      });
      setPreview(data);
      setValidation(null);
      setForm((current) => ({
        ...current,
        candidate_filename: data.normalized_filename,
      }));
    } catch (err) {
      setError(err.message || "Preview failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleValidate() {
    setLoading(true);
    setError("");
    try {
      const data = await validateFilename({
        script_title: form.script_title,
        line_number: Number(form.line_number || 0),
        keyword: form.keyword,
        asset_id: form.asset_id,
        source_url: form.source_url,
        extension: form.extension || "mp4",
        candidate_filename: form.candidate_filename || preview?.normalized_filename || "",
      });
      setValidation(data);
    } catch (err) {
      setError(err.message || "Validation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Filename Rules</h1>
        <p className="text-sm opacity-70">Preview and validate the active naming convention.</p>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border p-4 space-y-3">
          <div className="text-sm font-semibold">Active Rule</div>
          {activeRule ? (
            <>
              <div className="text-sm">Name: {activeRule.rule_name}</div>
              <div className="text-sm break-all">Pattern: {activeRule.pattern_template}</div>
              <div className="text-xs uppercase tracking-wide opacity-70">{activeRule.is_active ? "ACTIVE" : "INACTIVE"}</div>
            </>
          ) : (
            <div className="text-sm opacity-70">No active rule found.</div>
          )}

          <div className="pt-3 border-t space-y-2">
            <div className="text-sm font-semibold">Available Rules</div>
            <div className="space-y-2">
              {(rules || []).map((rule) => (
                <div key={rule.rule_id} className="rounded bg-gray-50 p-3 text-sm">
                  <div className="font-medium">{rule.rule_name}</div>
                  <div className="break-all opacity-80">{rule.pattern_template}</div>
                  <div className="text-xs opacity-70">{rule.is_active ? "active" : "inactive"}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded border p-4 space-y-3">
          <div className="text-sm font-semibold">Preview / Validate</div>
          <div className="grid gap-3 md:grid-cols-2">
            <input className="rounded border px-3 py-2" placeholder="Script title" value={form.script_title} onChange={(e) => setForm((c) => ({ ...c, script_title: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Line number" type="number" value={form.line_number} onChange={(e) => setForm((c) => ({ ...c, line_number: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Keyword" value={form.keyword} onChange={(e) => setForm((c) => ({ ...c, keyword: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Asset ID" value={form.asset_id} onChange={(e) => setForm((c) => ({ ...c, asset_id: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Source URL" value={form.source_url} onChange={(e) => setForm((c) => ({ ...c, source_url: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Extension" value={form.extension} onChange={(e) => setForm((c) => ({ ...c, extension: e.target.value }))} />
          </div>
          <input
            className="w-full rounded border px-3 py-2"
            placeholder="Candidate filename"
            value={form.candidate_filename}
            onChange={(e) => setForm((c) => ({ ...c, candidate_filename: e.target.value }))}
          />
          <div className="flex flex-wrap gap-2">
            <button className="rounded bg-black px-4 py-2 text-white" type="button" onClick={handlePreview} disabled={loading}>
              Preview
            </button>
            <button className="rounded border px-4 py-2" type="button" onClick={handleValidate} disabled={loading}>
              Validate
            </button>
          </div>

          {preview ? (
            <div className="rounded bg-gray-50 p-3 text-sm space-y-1">
              <div>Preview filename: <span className="font-semibold break-all">{preview.normalized_filename}</span></div>
              <div>Rule: {preview.rule_name}</div>
            </div>
          ) : null}

          {validation ? (
            <div className="rounded bg-gray-50 p-3 text-sm space-y-1">
              <div>Status: <span className="font-semibold">{validation.is_valid ? "VALID" : "INVALID"}</span></div>
              <div>Candidate: {validation.candidate_filename}</div>
              <div>Rule: {validation.rule_name}</div>
              {validation.reasons && validation.reasons.length ? (
                <div className="text-red-700">Reasons: {validation.reasons.join(", ")}</div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
