// src/pages/Auth/Callback.jsx
import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { completeOAuthCallback } from "../../services/authService";

export default function AuthCallback() {
  const nav = useNavigate();
  const { search } = useLocation();

  useEffect(() => {
    const run = async () => {
      try {
        await completeOAuthCallback(search);
        const q = new URLSearchParams(search);
        const next = q.get("state");
        const target = (next && next.startsWith("/")) ? next : "/settings/team-roles";
        nav(target, { replace: true });
      } catch {
        nav("/login", { replace: true });
      }
    };
    run();
  }, [search, nav]);

  return <div className="p-6">Completing sign in…</div>;
}

