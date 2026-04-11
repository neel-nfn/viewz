import { useEffect, useState } from "react";
import { listResearchRequests, submitResearch } from "../../services/phase1Service";

export default function ResearchInboxPage() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({});

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listResearchRequests();
      setItems(data.items || []);
    } catch (err) {
      setError(err.message || "Failed to load research requests");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSubmit(requestId) {
    const row = form[requestId] || {};
    setLoading(true);
    setError("");
    try {
      await submitResearch({
        research_request_id: requestId,
        source_url: row.source_url,
        start_time: Number(row.start_time),
        end_time: Number(row.end_time),
        relevance_type: row.relevance_type,
        notes: row.notes || "",
      });
      await load();
    } catch (err) {
      setError(err.message || "Failed to submit research");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Research Inbox</h1>
        <p className="text-sm opacity-70">Submit the source metadata for each requested line.</p>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.research_request_id} className="rounded border p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <div className="text-sm font-semibold">{item.script_title}</div>
                <div className="text-xs opacity-70">Line {item.line_number}</div>
              </div>
              <div className="text-xs uppercase tracking-wide opacity-70">{item.status}</div>
            </div>
            <div className="mt-2 text-sm">{item.raw_text}</div>
            <div className="mt-4 grid gap-2 md:grid-cols-5">
              <input
                className="rounded border px-3 py-2"
                placeholder="Source URL"
                value={form[item.research_request_id]?.source_url || ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [item.research_request_id]: {
                      ...(prev[item.research_request_id] || {}),
                      source_url: e.target.value,
                    },
                  }))
                }
              />
              <input
                className="rounded border px-3 py-2"
                placeholder="Start"
                type="number"
                step="0.01"
                value={form[item.research_request_id]?.start_time || ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [item.research_request_id]: {
                      ...(prev[item.research_request_id] || {}),
                      start_time: e.target.value,
                    },
                  }))
                }
              />
              <input
                className="rounded border px-3 py-2"
                placeholder="End"
                type="number"
                step="0.01"
                value={form[item.research_request_id]?.end_time || ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [item.research_request_id]: {
                      ...(prev[item.research_request_id] || {}),
                      end_time: e.target.value,
                    },
                  }))
                }
              />
              <select
                className="rounded border px-3 py-2"
                value={form[item.research_request_id]?.relevance_type || "DIRECT_MATCH"}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [item.research_request_id]: {
                      ...(prev[item.research_request_id] || {}),
                      relevance_type: e.target.value,
                    },
                  }))
                }
              >
                <option value="DIRECT_MATCH">DIRECT_MATCH</option>
                <option value="RELATED_MATCH">RELATED_MATCH</option>
              </select>
              <input
                className="rounded border px-3 py-2"
                placeholder="Notes"
                value={form[item.research_request_id]?.notes || ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    [item.research_request_id]: {
                      ...(prev[item.research_request_id] || {}),
                      notes: e.target.value,
                    },
                  }))
                }
              />
            </div>
            <div className="mt-3">
              <button
                className="rounded bg-black px-4 py-2 text-white"
                type="button"
                onClick={() => handleSubmit(item.research_request_id)}
              >
                Submit Research
              </button>
            </div>
            {item.latest_submission ? (
              <div className="mt-3 rounded bg-gray-50 p-3 text-sm">
                Latest submission: {item.latest_submission.source_url} [{item.latest_submission.start_time} - {item.latest_submission.end_time}]
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
