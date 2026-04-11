function trimSlash(value) {
  return typeof value === "string" ? value.replace(/\/+$/, "") : "";
}

function stripApiVersionSuffix(value) {
  return trimSlash(value).replace(/\/api\/v1$/, "");
}

function getRuntimeApiBase() {
  if (typeof window === "undefined") {
    return "";
  }

  const runtimeBase = stripApiVersionSuffix(window.__VIEWZ_API_BASE_URL__);
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
    stripApiVersionSuffix(import.meta.env.VITE_API_BASE_URL) ||
    getRuntimeApiBase() ||
    "http://localhost:8000"
  );
}
