import { useEffect, useState } from "react";
import { getWorkerStatus, startWorker, stopWorker } from "../../services/phase4Service";

export default function WorkerDashboardPage() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await getWorkerStatus();
      setStatus(data);
    } catch (err) {
      setError(err.message || "Failed to load worker status");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleStart() {
    setLoading(true);
    setError("");
    try {
      const data = await startWorker();
      setStatus(data);
    } catch (err) {
      setError(err.message || "Failed to start worker");
    } finally {
      setLoading(false);
    }
  }

  async function handleStop() {
    setLoading(true);
    setError("");
    try {
      const data = await stopWorker();
      setStatus(data);
    } catch (err) {
      setError(err.message || "Failed to stop worker");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Worker Dashboard</h1>
          <p className="text-sm opacity-70">Background execution and queue health.</p>
        </div>
        <div className="flex gap-2">
          <button className="rounded bg-black px-4 py-2 text-white" type="button" onClick={handleStart} disabled={loading}>
            Start Worker
          </button>
          <button className="rounded border px-4 py-2" type="button" onClick={handleStop} disabled={loading}>
            Stop Worker
          </button>
          <button className="rounded border px-4 py-2" type="button" onClick={load} disabled={loading}>
            Refresh
          </button>
        </div>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      {status ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded border p-4">
              <div className="text-xs uppercase opacity-60">Running</div>
              <div className="text-lg font-semibold">{status.running ? "Yes" : "No"}</div>
            </div>
            <div className="rounded border p-4">
              <div className="text-xs uppercase opacity-60">Queue Size</div>
              <div className="text-lg font-semibold">{status.queue_size}</div>
            </div>
            <div className="rounded border p-4">
              <div className="text-xs uppercase opacity-60">Active Jobs</div>
              <div className="text-lg font-semibold">{status.active_job_count}</div>
            </div>
            <div className="rounded border p-4">
              <div className="text-xs uppercase opacity-60">Failed Items</div>
              <div className="text-lg font-semibold">{status.failed_item_count}</div>
            </div>
          </div>

          <div className="rounded border p-4 space-y-2">
            <div className="text-sm font-semibold">Worker State</div>
            <div className="text-sm">Worker ID: {status.worker_id || "n/a"}</div>
            <div className="text-sm">Current Job: {status.current_job_id || "none"}</div>
            <div className="text-sm">Current Item: {status.current_item_id || "none"}</div>
            <div className="text-sm">Last Poll: {status.last_poll_at || "n/a"}</div>
            <div className="text-sm">Message: {status.message || "ok"}</div>
          </div>

          <div className="space-y-3">
            <div className="text-sm font-semibold">Active Jobs</div>
            {(status.active_jobs || []).map((job) => (
              <div key={job.job_id} className="rounded border p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold">{job.job_type}</div>
                    <div className="text-xs opacity-70">{job.job_id}</div>
                  </div>
                  <div className="text-xs uppercase tracking-wide opacity-70">{job.status}</div>
                </div>
                <div className="mt-3 grid gap-2 text-sm md:grid-cols-2">
                  <div>Locked by: {job.locked_by || "none"}</div>
                  <div>Locked at: {job.locked_at || "n/a"}</div>
                  <div>Total: {job.total_items}</div>
                  <div>Processed: {job.processed_items}</div>
                  <div>Failed: {job.failed_items}</div>
                  <div>Storage: {job.storage_provider}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
}
