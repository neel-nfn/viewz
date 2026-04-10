import { useEffect, useState } from "react";
import { approveResearch, listResearchRequests, rejectResearch } from "../../services/phase1Service";

export default function ApprovalQueuePage() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listResearchRequests();
      setItems((data.items || []).filter((item) => item.latest_submission?.status === "PENDING_REVIEW"));
    } catch (err) {
      setError(err.message || "Failed to load approval queue");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAction(item, action) {
    setLoading(true);
    setError("");
    try {
      if (action === "approve") {
        await approveResearch(item.latest_submission.submission_id);
      } else {
        await rejectResearch(item.latest_submission.submission_id);
      }
      await load();
    } catch (err) {
      setError(err.message || "Approval action failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Approval Queue</h1>
        <p className="text-sm opacity-70">Review submissions before assets enter validation.</p>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.research_request_id} className="rounded border p-4">
            <div className="text-sm font-semibold">{item.script_title} - Line {item.line_number}</div>
            <div className="mt-1 text-sm">{item.raw_text}</div>
            <div className="mt-3 rounded bg-gray-50 p-3 text-sm space-y-1">
              <div>URL: {item.latest_submission.source_url}</div>
              <div>Range: {item.latest_submission.start_time} - {item.latest_submission.end_time}</div>
              <div>Relevance: {item.latest_submission.relevance_type}</div>
              <div>Notes: {item.latest_submission.notes || ""}</div>
            </div>
            <div className="mt-3 flex gap-2">
              <button className="rounded bg-black px-4 py-2 text-white" type="button" onClick={() => handleAction(item, "approve")}>
                Approve
              </button>
              <button className="rounded border px-4 py-2" type="button" onClick={() => handleAction(item, "reject")}>
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
