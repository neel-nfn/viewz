import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  completeOperatorJob,
  getOperatorJob,
  processOperatorJobItem,
  retryFailedOperatorJob,
  startOperatorJob,
} from "../../services/phase4Service";

export default function OperatorJobDetailPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    if (!jobId) return;
    setLoading(true);
    setError("");
    try {
      const data = await getOperatorJob(jobId);
      setJob(data);
    } catch (err) {
      setError(err.message || "Failed to load job");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [jobId]);

  async function handleStart() {
    setLoading(true);
    setError("");
    try {
      await startOperatorJob(jobId);
      await load();
    } catch (err) {
      setError(err.message || "Failed to start job");
    } finally {
      setLoading(false);
    }
  }

  async function handleProcessItem(itemId) {
    setLoading(true);
    setError("");
    try {
      await processOperatorJobItem(jobId, itemId, job?.storage_provider || "local_stub");
      await load();
    } catch (err) {
      setError(err.message || "Failed to process item");
    } finally {
      setLoading(false);
    }
  }

  async function handleComplete() {
    setLoading(true);
    setError("");
    try {
      await completeOperatorJob(jobId);
      await load();
    } catch (err) {
      setError(err.message || "Failed to complete job");
    } finally {
      setLoading(false);
    }
  }

  async function handleRetryFailed() {
    setLoading(true);
    setError("");
    try {
      await retryFailedOperatorJob(jobId);
      await load();
    } catch (err) {
      setError(err.message || "Failed to retry failed items");
    } finally {
      setLoading(false);
    }
  }

  if (!job && !loading && !error) {
    return <div className="p-6 text-sm opacity-70">Loading...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Operator Job</h1>
          <p className="text-sm opacity-70">Job {jobId}</p>
        </div>
          <div className="flex flex-wrap gap-2">
            <button className="rounded border px-4 py-2" type="button" onClick={() => navigate("/app/operator")}>
              Back
            </button>
            <button className="rounded border px-4 py-2" type="button" onClick={handleStart} disabled={!job || job.status !== "QUEUED"}>
              Start
            </button>
            <button className="rounded border px-4 py-2" type="button" onClick={handleRetryFailed} disabled={!job}>
              Retry Failed
            </button>
            <button className="rounded bg-black px-4 py-2 text-white" type="button" onClick={handleComplete} disabled={!job}>
              Complete
            </button>
          </div>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      {job ? (
        <>
          <div className="rounded border p-4">
            <div className="grid gap-2 text-sm md:grid-cols-2">
              <div>Status: <span className="font-semibold">{job.status}</span></div>
              <div>Job type: {job.job_type}</div>
              <div>Total: {job.total_items}</div>
              <div>Processed: {job.processed_items}</div>
              <div>Failed: {job.failed_items}</div>
              <div>Storage provider: {job.storage_provider}</div>
            </div>
            <div className="mt-3 text-xs opacity-70">Result: {JSON.stringify(job.result_payload_json || {}, null, 2)}</div>
          </div>

          <div className="space-y-3">
            {(job.items || []).map((item) => (
              <div key={item.id} className="rounded border p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold">{item.normalized_filename || "unnamed"}</div>
                    <div className="text-xs opacity-70">Item {item.id}</div>
                  </div>
                  <div className="text-xs uppercase tracking-wide opacity-70">{item.status}</div>
                </div>

                <div className="mt-3 grid gap-2 text-sm md:grid-cols-2">
                  <div>Submission: {item.research_submission_id || "none"}</div>
                  <div>Asset: {item.asset_id || "none"}</div>
                  <div>Source URL: {item.source_url || "none"}</div>
                  <div>Requested range: {item.requested_start_time ?? "n/a"} - {item.requested_end_time ?? "n/a"}</div>
                  <div>Provider: {item.storage_provider}</div>
                  <div>Path: {item.storage_path || "not stored"}</div>
                  <div>Checksum: {item.checksum || "n/a"}</div>
                  <div>Completed: {item.completed_at || "pending"}</div>
                </div>

                {item.error_message ? (
                  <div className="mt-3 rounded border border-red-400 bg-red-50 p-3 text-sm text-red-700">
                    {item.error_message}
                  </div>
                ) : null}

                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    className="rounded bg-black px-4 py-2 text-white"
                    type="button"
                    onClick={() => handleProcessItem(item.id)}
                    disabled={!job || job.status !== "IN_PROGRESS" || !["PENDING", "FAILED"].includes(item.status)}
                  >
                    Process Item
                  </button>
                  <button
                    className="rounded border px-4 py-2"
                    type="button"
                    onClick={handleRetryFailed}
                    disabled={item.status !== "FAILED"}
                  >
                    Retry Failed Item
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
}
