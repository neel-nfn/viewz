import { useEffect, useState } from "react";
import { getApiBase } from "../../lib/apiBase";

const API_BASE = getApiBase();

export default function EnvIndicator() {
  const [envInfo, setEnvInfo] = useState(null);

  useEffect(() => {
    async function fetchEnv() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/env`);
        const data = await res.json();
        setEnvInfo(data);
      } catch (e) {
        console.error("Failed to fetch env info:", e);
        setEnvInfo({ env: "unknown", service: "viewz-frontend" });
      }
    }
    fetchEnv();
  }, []);

  const env = envInfo?.env || "local";
  const service = envInfo?.service || "viewz";
  const apiBase = API_BASE.includes("localhost") ? "local" : "prod";

  return (
    <div className="text-xs opacity-50 flex items-center gap-2">
      <span>{env}</span>
      <span>•</span>
      <span>API: {apiBase}</span>
      <span>•</span>
      <span>{service}</span>
    </div>
  );
}
