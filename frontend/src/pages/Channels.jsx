import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../services/apiClient";
import toast from "react-hot-toast";

export default function Channels() {
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);

  async function refresh() {
    setLoading(true);
    try {
      const data = await apiGet("/api/v1/channels/list");
      setChannels(data.channels || []);
    } catch (e) {
      setChannels([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { refresh(); }, []);

  async function connect() {
    const res = await apiPost("/api/v1/channels/connect", {});
    if (res.oauth_redirect_url) { 
      toast.success("Redirecting to Google…"); 
      window.location.href = res.oauth_redirect_url; 
    }
  }

  async function revoke(id) {
    setBusyId(id);
    try {
      await apiPost("/api/v1/channels/revoke", { channel_id: id });
      await refresh();
      toast.success("Channel revoked");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-xl font-semibold">Channels</div>
        <button className="btn btn-primary" onClick={connect}>Connect YouTube</button>
      </div>

      <div className="rounded-xl bg-base-100 border">
        {loading ? (
          <div className="p-6">Loading…</div>
        ) : channels.length === 0 ? (
          <div className="p-6 opacity-70">No channels connected yet.</div>
        ) : (
          <ul className="menu p-4">
            {channels.map((c) => (
              <li key={c.id} className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <div className="avatar placeholder">
                    <div className="bg-neutral text-neutral-content rounded-full w-10">
                      <span>{(c.title || "YT").slice(0,2).toUpperCase()}</span>
                    </div>
                  </div>
                  <div>
                    <div className="font-medium">{c.title || "Untitled Channel"}</div>
                    <div className="text-xs opacity-70">{c.handle || c.channel_id}</div>
                  </div>
                </div>
                <button
                  className="btn btn-outline btn-error"
                  onClick={() => revoke(c.id)}
                  disabled={busyId === c.id}
                >
                  {busyId === c.id ? "Revoking…" : "Revoke"}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
