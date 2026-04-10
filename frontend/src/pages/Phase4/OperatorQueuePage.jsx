import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  createOperatorJob,
  createOperatorJobFromApprovedSubmissions,
  listOperatorJobs,
  startOperatorJob,
} from "../../services/phase4Service";

export default function OperatorQueuePage() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listOperatorJobs();
      setItems(data.items || []);
    } catch (err) {
      setError(err.message || "Failed to load operator jobs");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreateFromApproved() {
    setCreating(true);
    setError("");
    try {
      const job = await createOperatorJobFromApprovedSubmissions({
        job_type: "INGEST",
        storage_provider: "local_stub",
      });
      await load();
      navigate(`/app/operator/jobs/${job.job_id}`);
    } catch (err) {
      setError(err.message || "Failed to create operator job");
    } finally {
      setCreating(false);
    }
  }

  async function handleCreateEmpty() {
    setCreating(true);
    setError("");
    try {
      const job = await createOperatorJob({
        job_type: "INGEST",
        storage_provider: "local_stub",
        submission_ids: [],
      });
      await load();
      navigate(`/app/operator/jobs/${job.job_id}`);
    } catch (err) {
      setError(err.message || "Failed to create operator job");
    } finally {
      setCreating(false);
    }
  }

  async function handleStart(jobId) {
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

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Operator Queue</h1>
        <p className="text-sm opacity-70">Batch jobs for approved submissions and storage execution.</p>
      </div>

      <div className="flex flex-wrap gap-2">
        <button className="rounded bg-black px-4 py-2 text-white" type="button" onClick={handleCreateFromApproved} disabled={creating}>
          Queue Approved Submissions
        </button>
        <button className="rounded border px-4 py-2" type="button" onClick={handleCreateEmpty} disabled={creating}>
          Create Empty Job
        </button>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      <div className="space-y-3">
        {(items || []).map((job) => (
          <div key={job.job_id} className="rounded border p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold">{job.job_type}</div>
                <div className="text-xs opacity-70">Job ID: {job.job_id}</div>
              </div>
              <div className="text-xs uppercase tracking-wide opacity-70">{job.status}</div>
            </div>
            <div className="mt-3 grid gap-2 text-sm md:grid-cols-2">
              <div>Requested by: {job.requested_by || "unknown"}</div>
              <div>Assigned to: {job.assigned_to || "unassigned"}</div>
              <div>Total items: {job.total_items}</div>
              <div>Processed: {job.processed_items}</div>
              <div>Failed: {job.failed_items}</div>
              <div>Storage provider: {job.storage_provider}</div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                className="rounded border px-4 py-2"
                type="button"
                onClick={() => navigate(`/app/operator/jobs/${job.job_id}`)}
              >
                Open Job
              </button>
              <button
                className="rounded bg-black px-4 py-2 text-white"
                type="button"
                onClick={() => handleStart(job.job_id)}
                disabled={job.status !== "QUEUED"}
              >
                Start
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
