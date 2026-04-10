import { useEffect, useState } from "react";
import { listStorageObjects } from "../../services/phase4Service";

export default function StorageObjectsPage() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listStorageObjects();
      setItems(data.items || []);
    } catch (err) {
      setError(err.message || "Failed to load storage objects");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Storage Objects</h1>
        <p className="text-sm opacity-70">Registered storage metadata for managed assets.</p>
      </div>

      {error ? <div className="rounded border border-red-400 bg-red-50 p-3 text-red-700">{error}</div> : null}
      {loading ? <div className="text-sm opacity-70">Loading...</div> : null}

      <div className="space-y-3">
        {(items || []).map((item) => (
          <div key={item.storage_object_id} className="rounded border p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold">{item.object_key}</div>
                <div className="text-xs opacity-70">{item.provider}</div>
              </div>
              <div className="text-xs opacity-70">{item.byte_size ?? 0} bytes</div>
            </div>
            <div className="mt-3 grid gap-2 text-sm md:grid-cols-2">
              <div>Asset: {item.asset_id || "none"}</div>
              <div>Bucket/Drive: {item.bucket_or_drive_id || "n/a"}</div>
              <div>Public URL: {item.public_url || "n/a"}</div>
              <div>Checksum: {item.checksum || "n/a"}</div>
              <div>MIME type: {item.mime_type || "n/a"}</div>
              <div>Created: {item.created_at}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
