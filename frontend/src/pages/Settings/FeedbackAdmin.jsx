import { useEffect, useState } from "react";
import { listFeedback, updateFeedback } from "../../services/feedbackService";
import { useAuth } from "../../context/AuthContext";

export default function FeedbackAdmin() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  
  // Get org_id from localStorage or use default
  const orgId = localStorage.getItem('viewz_org_id') || '00000000-0000-0000-0000-000000000000';

  useEffect(() => {
    if (user?.role === "admin" || user?.role === "manager") {
      loadFeedback();
    }
  }, [status, user]);

  async function loadFeedback() {
    setLoading(true);
    try {
      const data = await listFeedback(status ? { status } : {});
      setItems(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error("Failed to load feedback:", e);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  async function mark(id, s) {
    try {
      const updated = await updateFeedback(id, s);
      setItems(prev => prev.map(x => x.id === id ? updated : x));
    } catch (e) {
      alert(`Failed to update: ${e.message}`);
    }
  }

  // Allow all users for now, but in production check role
  // if (!(user?.role === "admin" || user?.role === "manager")) return null;

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">Feedback Reports</h2>
      <div className="flex gap-3 mb-3">
        <select
          className="select select-bordered"
          value={status}
          onChange={e => setStatus(e.target.value)}
        >
          <option value="">All</option>
          <option value="open">open</option>
          <option value="triaged">triaged</option>
          <option value="resolved">resolved</option>
          <option value="rejected">rejected</option>
        </select>
        <button className="btn btn-sm" onClick={loadFeedback} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>
      {loading && items.length === 0 ? (
        <div className="text-center py-8">Loading...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-8 opacity-60">No feedback reports found</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>When</th>
                <th>Title</th>
                <th>Category</th>
                <th>Severity</th>
                <th>Status</th>
                <th>URL</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map(x => (
                <tr key={x.id}>
                  <td>{new Date(x.created_at).toLocaleString()}</td>
                  <td>{x.title}</td>
                  <td>{x.category}</td>
                  <td>
                    <span className={`badge ${
                      x.severity === 'critical' ? 'badge-error' :
                      x.severity === 'high' ? 'badge-warning' :
                      'badge-info'
                    }`}>
                      {x.severity}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${
                      x.status === 'resolved' ? 'badge-success' :
                      x.status === 'rejected' ? 'badge-error' :
                      'badge-info'
                    }`}>
                      {x.status}
                    </span>
                  </td>
                  <td>
                    {x.url ? (
                      <a className="link" href={x.url} target="_blank" rel="noreferrer">open</a>
                    ) : (
                      <span className="opacity-60">—</span>
                    )}
                  </td>
                  <td className="flex gap-2">
                    <button
                      className="btn btn-xs"
                      onClick={() => mark(x.id, "triaged")}
                      disabled={x.status === "triaged"}
                    >
                      Triaged
                    </button>
                    <button
                      className="btn btn-xs btn-success"
                      onClick={() => mark(x.id, "resolved")}
                      disabled={x.status === "resolved"}
                    >
                      Resolve
                    </button>
                    <button
                      className="btn btn-xs btn-error"
                      onClick={() => mark(x.id, "rejected")}
                      disabled={x.status === "rejected"}
                    >
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

