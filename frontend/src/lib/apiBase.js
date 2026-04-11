function trimSlash(value) {
  return typeof value === "string" ? value.replace(/\/+$/, "") : "";
}

function getRuntimeApiBase() {
  if (typeof window === "undefined") {
    return "";
  }

  const runtimeBase = trimSlash(window.__VIEWZ_API_BASE_URL__);
  if (runtimeBase) {
    return runtimeBase;
  }

  const { protocol, hostname, port } = window.location;
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return `${protocol}//localhost:8000`;
  }

  const apiHost = hostname.startsWith("viewz.") ? hostname.replace(/^viewz\./, "api.viewz.") : `api.${hostname}`;
  return `${protocol}//${apiHost}${port ? `:${port}` : ""}`.replace(/\/+$/, "");
}

export function getApiBase() {
  return (
    trimSlash(import.meta.env.VITE_API_BASE_URL) ||
    getRuntimeApiBase() ||
    "http://localhost:8000"
  );
}
