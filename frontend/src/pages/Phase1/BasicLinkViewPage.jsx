import { useEffect, useState } from "react";
import { linkAssetToLine, listResearchRequests } from "../../services/phase1Service";

export default function BasicLinkViewPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listResearchRequests();
      setItems((data.items || []).filter((item) => item.latest_submission));
    } catch (err) {
      setError(err.message || "Failed to load link view");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleLink(item) {
    const row = form[item.research_request_id] || {};
    setLoading(true);
    setError("");
    try {
      await linkAssetToLine({
        script_line_id: item.script_line_id,
        research_submission_id: item.latest_submission.submission_id,
        selected_start: Number(row.selected_start || item.latest_submission.start_time || 0),
        duration: Number(row.duration || Math.max(0, (item.latest_submission.end_time || 0) - (item.latest_submission.start_time || 0))),
      });
      await load();
    } catch (err) {
      setError(err.message || "Failed to link asset");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Basic Link View</h1>
        <p className="text-sm opacity-70">Approve the submission and attach the asset to the line.</p>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.research_request_id} className="rounded border p-4">
            <div className="text-sm font-semibold">{item.script_title} - Line {item.line_number}</div>
            <div className="mt-1 text-sm">{item.raw_text}</div>
            <div className="mt-3 rounded bg-gray-50 p-3 text-sm">
              <div>Submission: {item.latest_submission.source_url}</div>
              <div>
                Range: {item.latest_submission.start_time} - {item.latest_submission.end_time}
              </div>
              <div>Relevance: {item.latest_submission.relevance_type}</div>
            </div>
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              <input
                className="rounded border px-3 py-2"
                placeholder="Selected start"
                type="number"
                step="0.01"
                value={form[item.research_request_id]?.selected_start || ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [item.research_request_id]: {
                      ...(prev[item.research_request_id] || {}),
                      selected_start: e.target.value,
                    },
                  }))
                }
              />
              <input
                className="rounded border px-3 py-2"
                placeholder="Duration"
                type="number"
                step="0.01"
                value={form[item.research_request_id]?.duration || ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [item.research_request_id]: {
                      ...(prev[item.research_request_id] || {}),
                      duration: e.target.value,
                    },
                  }))
                }
              />
            </div>
            <div className="mt-3">
              <button className="rounded bg-black px-4 py-2 text-white" type="button" onClick={() => handleLink(item)}>
                Approve &amp; Link
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
