import { useEffect, useState } from "react";
import { listAssets, validateAsset } from "../../services/phase1Service";

export default function AssetValidationPanelPage() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listAssets();
      setItems(data.items || []);
    } catch (err) {
      setError(err.message || "Failed to load assets");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleValidate(assetId) {
    setLoading(true);
    setError("");
    try {
      await validateAsset(assetId, "manual", "Validated from operator panel");
      await load();
    } catch (err) {
      setError(err.message || "Validation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Asset Validation Panel</h1>
        <p className="text-sm opacity-70">Approve or reject assets before linking.</p>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.asset_id} className="rounded border p-4">
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-semibold">{item.filename}</div>
              <div className="text-xs uppercase tracking-wide opacity-70">{item.status}</div>
            </div>
            <div className="mt-2 text-sm">URL: {item.source_url}</div>
            <div className="text-sm">Range: {item.start_time} - {item.end_time}</div>
            <div className="text-xs opacity-70">
              Submission: {item.research_submission_id || "none"} | Validations: {item.validation_count}
            </div>
            {item.last_validation_result ? (
              <div className="mt-2 rounded bg-gray-50 p-3 text-sm">
                Result: {item.last_validation_result} | Notes: {item.last_validation_notes || ""}
              </div>
            ) : null}
            <div className="mt-3">
              <button
                className="rounded border px-4 py-2"
                type="button"
                onClick={() => handleValidate(item.asset_id)}
                disabled={loading || item.status === "READY"}
              >
                Validate
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
