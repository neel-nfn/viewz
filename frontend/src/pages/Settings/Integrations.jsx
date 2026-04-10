import { useState, useEffect } from "react";
import { getIntegrations, getYouTubeStatus, getYouTubeHealth, saveAIKey, deleteAIKey } from "../../services/integrationService";
import { useAuth } from "../../context/AuthContext";
import { startGoogleLogin } from "../../services/authService";
import DataBanner from "../../components/common/DataBanner";

export default function Integrations() {
  const { user } = useAuth();
  const [integrations, setIntegrations] = useState(null);
  const [youtubeStatus, setYoutubeStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiKey, setAIKey] = useState("");
  const [savingAI, setSavingAI] = useState(false);
  const [deletingAI, setDeletingAI] = useState(false);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const [youtubeHealth, setYoutubeHealth] = useState(null);

  async function loadIntegrations() {
    setLoading(true);
    try {
      const [integrationsData, youtubeData, healthData] = await Promise.all([
        getIntegrations(),
        getYouTubeStatus().catch(() => ({ connected: false })), // Graceful fallback
        getYouTubeHealth().catch(() => ({ ok: false, connected: false })), // Graceful fallback
      ]);
      setIntegrations(integrationsData);
      setYoutubeStatus(youtubeData);
      setYoutubeHealth(healthData);
    } catch (e) {
      console.error("Failed to load integrations:", e);
      setIntegrations({ youtube_connected: false, ai_key_configured: false, provider: "gemini" });
      setYoutubeStatus({ connected: false });
      setYoutubeHealth({ ok: false, connected: false });
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveAIKey() {
    if (!aiKey.trim()) return;
    setSavingAI(true);
    try {
      await saveAIKey(aiKey.trim());
      setAIKey("");
      await loadIntegrations();
      alert("AI key saved successfully!");
    } catch (e) {
      alert(`Failed to save: ${e.message}`);
    } finally {
      setSavingAI(false);
    }
  }

  async function handleDeleteAIKey() {
    if (!confirm("Delete AI key? This will disable AI features.")) return;
    setDeletingAI(true);
    try {
      await deleteAIKey();
      await loadIntegrations();
      alert("AI key deleted.");
    } catch (e) {
      alert(`Failed to delete: ${e.message}`);
    } finally {
      setDeletingAI(false);
    }
  }

  function handleConnectYouTube() {
    console.log("[AUTH-DEBUG] handleConnectYouTube called from Settings/Integrations.jsx");
    startGoogleLogin();
  }

  if (loading) {
    return <div className="p-4">Loading integrations…</div>;
  }

  const int = integrations || { youtube_connected: false, ai_key_configured: false, provider: "gemini" };
  const isDemo = localStorage.getItem('viewz_demo') === '1' || !int.youtube_connected;
  
  // Empty state: if integrations is null/empty, show empty state
  if (!integrations || (integrations && typeof integrations === 'object' && Object.keys(integrations).length === 0)) {
    return (
      <div className="p-4 space-y-6">
        <h2 className="text-xl font-semibold">Integrations</h2>
        <div className="card bg-base-100 border border-base-300">
          <div className="card-body text-center py-12">
            <p className="text-sm opacity-70 mb-4">No integrations configured yet.</p>
            <button className="btn btn-primary btn-sm" onClick={handleConnectYouTube}>
              Connect YouTube
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Create data object for banner
  const integrationsData = {
    mock: !youtubeStatus?.connected,
    source: youtubeStatus?.connected ? 'youtube' : 'demo-fixture',
    fallback_reason: youtubeHealth && !youtubeHealth.ok ? youtubeHealth.reason : null,
  };

  return (
    <div className="p-4 space-y-6">
      <h2 className="text-xl font-semibold">Integrations</h2>
      <DataBanner data={integrationsData} page="integrations" />

      {/* YouTube Integration Card */}
      <div className="card bg-base-100 border border-base-300">
        <div className="card-body">
          <h3 className="card-title">YouTube Integration</h3>
          <p className="text-sm opacity-70">
            Connect your YouTube channel to sync analytics and manage content.
          </p>
          {youtubeStatus && youtubeStatus.connected ? (
            <div className="mt-4 space-y-3">
              <div className="flex items-center gap-3">
                {youtubeStatus.logo_url && (
                  <img 
                    src={youtubeStatus.logo_url} 
                    alt={youtubeStatus.title || "Channel"} 
                    className="w-12 h-12 rounded-full"
                  />
                )}
                <div>
                  <div className="font-semibold">✓ Connected as {youtubeStatus.title || "YouTube Channel"}</div>
                  {youtubeStatus.youtube_channel_id && (
                    <div className="text-xs opacity-60">{youtubeStatus.youtube_channel_id}</div>
                  )}
                </div>
              </div>
              {!youtubeStatus.has_token && (
                <div className="alert alert-warning">
                  <span>Token missing. Please reconnect to refresh access.</span>
                </div>
              )}
              {youtubeHealth && youtubeStatus.connected && !youtubeHealth.ok && (
                <div className="alert alert-error">
                  <div className="flex flex-col gap-2">
                    <span className="font-semibold">
                      Connected but not usable: {youtubeHealth.reason || "Unknown error"}
                    </span>
                    {youtubeHealth.reason === "MISSING_SCOPE" && (
                      <div className="text-sm opacity-90">
                        <p className="mb-1">Your YouTube connection is missing required permissions:</p>
                        <ul className="list-disc list-inside space-y-1 ml-2">
                          <li>YouTube Data API (read-only)</li>
                          <li>YouTube Analytics API (read-only)</li>
                        </ul>
                        <p className="mt-2 font-medium">Click "Re-connect" below to grant these permissions.</p>
                      </div>
                    )}
                    {youtubeHealth.reason === "TOKEN_EXPIRED" && (
                      <p className="text-sm opacity-90">Your access token has expired. Click "Re-connect" to refresh it.</p>
                    )}
                    {youtubeHealth.reason === "PROVIDER_ERROR" && (
                      <p className="text-sm opacity-90">There was an error communicating with YouTube API. Please try again later.</p>
                    )}
                  </div>
                </div>
              )}
              {youtubeHealth && youtubeStatus.connected && youtubeHealth.ok && (
                <div className="alert alert-success">
                  <span>✓ Connection is healthy and all required permissions are granted.</span>
                </div>
              )}
              <div className="flex gap-2">
                <button className="btn btn-sm btn-primary" onClick={handleConnectYouTube}>
                  Re-connect
                </button>
                <button className="btn btn-sm btn-ghost" onClick={() => window.location.href = "/app/settings/channels"}>
                  Manage Channels
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-4 flex items-center justify-between">
              <div>
                <span className="badge badge-warning">Not Connected</span>
              </div>
              <button className="btn btn-sm btn-primary" onClick={handleConnectYouTube}>
                Connect YouTube
              </button>
            </div>
          )}
        </div>
      </div>

      {/* AI Provider Card */}
      <div className="card bg-base-100 border border-base-300">
        <div className="card-body">
          <h3 className="card-title">AI Provider (Gemini)</h3>
          <p className="text-sm opacity-70">
            Configure your Google Gemini API key for AI-powered content generation.
          </p>
          <div className="mt-4">
            <div className="mb-3">
              <span className={`badge ${int.ai_key_configured ? 'badge-success' : 'badge-warning'}`}>
                {int.ai_key_configured ? "Configured" : "Not Configured"}
              </span>
              {int.ai_key_configured && (
                <span className="ml-2 text-xs opacity-60">
                  Provider: {int.provider}
                </span>
              )}
            </div>
            {int.ai_key_configured ? (
              <div className="flex gap-2">
                <button
                  className="btn btn-sm btn-error"
                  onClick={handleDeleteAIKey}
                  disabled={deletingAI}
                >
                  {deletingAI ? "Deleting..." : "Delete Key"}
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <input
                  type="password"
                  className="input input-bordered w-full"
                  placeholder="Enter Gemini API key"
                  value={aiKey}
                  onChange={e => setAIKey(e.target.value)}
                />
                <button
                  className="btn btn-sm btn-primary"
                  onClick={handleSaveAIKey}
                  disabled={savingAI || !aiKey.trim()}
                >
                  {savingAI ? "Saving..." : "Save Key"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Status Summary */}
      <div className="card bg-base-100 border border-base-300">
        <div className="card-body">
          <h3 className="card-title text-sm">Status Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Data Source:</span>
              <span className={`badge ${isDemo ? 'badge-warning' : 'badge-success'}`}>
                {isDemo ? "Demo Mode" : "Live"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Last Sync:</span>
              <span className="opacity-60">
                {int.last_sync_at ? new Date(int.last_sync_at).toLocaleString() : "Never"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>AI Provider:</span>
              <span className="opacity-60">{int.provider || "gemini"}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

