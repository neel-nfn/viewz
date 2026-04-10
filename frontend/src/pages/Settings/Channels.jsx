import { useEffect, useState } from "react";
import { listChannels, revokeChannel, reconnect } from "../../services/channelService";
import { getPlanLimit } from "../../services/billingService";

export default function Channels(){
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState("");
  const [planLimit, setPlanLimit] = useState(100);

  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      setError(false);
      setLoading(true);
      const channels = await listChannels();
      setItems(Array.isArray(channels) ? channels : []);
    } catch (e) {
      console.error("Channels load error:", e);
      setError(true);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    (async () => {
      try {
        setPlanLimit(await getPlanLimit());
      } catch (e) {
        console.error("Plan limit error:", e);
      }
      await load();
    })();
  }, []);

  const revoke = async (id) => {
    setBusy(id);
    await revokeChannel(id);
    await load();
    setBusy("");
  };

  if (loading) {
    return <div className="p-6">Loading channels…</div>;
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Channel Connections</h1>
        <div className="alert alert-error">
          Failed to load channels. Please try again later.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Channel Connections</h1>
      {!items.length && (
        <div className="rounded-2xl p-6 bg-base-200">
          <p className="text-sm opacity-70 mb-2">No channels connected yet.</p>
          <p className="text-xs opacity-60">Connect your YouTube channel in Settings → Integrations.</p>
        </div>
      )}
      <div className="grid gap-3">
        {items.map(ch => (
          <div key={ch.id || ch.youtube_channel_id} className="rounded-2xl p-4 shadow bg-base-100 grid gap-3 md:grid-cols-[1fr_auto]">
            <div>
              <div className="flex items-center gap-3 mb-3">
                {ch.logo_url ? (
                  <img src={ch.logo_url} alt="" className="w-10 h-10 rounded-full" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-base-200" />
                )}
                <div>
                  <div className="font-semibold">{ch.title}</div>
                  <div className="text-xs opacity-70">{ch.youtube_channel_id}</div>
                </div>
              </div>
              <div className="mt-2 text-xs opacity-80">AI usage: {ch.ai_credits_used || 0} of {planLimit}</div>
              <progress className="progress w-56 mt-1" value={Math.min(100, Math.round(((ch.ai_credits_used || 0) / (planLimit || 100)) * 100))} max="100" />
              <div className="text-xs opacity-70 mt-2">Last sync: {ch.last_synced_at ? new Date(ch.last_synced_at).toLocaleString() : '—'}</div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`badge ${(ch.status || 'connected') === 'connected' ? 'badge-success' : 'badge-error'}`}>{ch.status || 'connected'}</span>
              <button className="btn btn-ghost" onClick={() => reconnect()}>Reconnect</button>
              <button className="btn btn-outline btn-error" disabled={!ch.id || busy === ch.id} onClick={() => revoke(ch.id)}>Revoke</button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6">
        <button className="btn btn-primary" onClick={() => reconnect()}>Connect New Channel</button>
      </div>
    </div>
  );
}

