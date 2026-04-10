const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const p = window.location.pathname;

if (p.startsWith('/api/')) {
  const q = window.location.search || '';
  const h = window.location.hash || '';
  window.location.replace(`${BASE}${p}${q}${h}`);
}

