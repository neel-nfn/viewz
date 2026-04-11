import { getApiBase } from "../lib/apiBase";

const BASE = getApiBase();

const p = window.location.pathname;

if (p.startsWith('/api/')) {
  const q = window.location.search || '';
  const h = window.location.hash || '';
  window.location.replace(`${BASE}${p}${q}${h}`);
}
