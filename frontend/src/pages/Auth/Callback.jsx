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
        const result = await completeOAuthCallback(search);

        if (result?.success === false) {
          const q = new URLSearchParams(search);
          const err = q.get("error") || result.error || "oauth_failed";
          nav(`/auth/fail?error=${encodeURIComponent(err)}`, { replace: true });
          return;
        }

        const q = new URLSearchParams(search);
        const next = q.get("state");
        const target = (next && next.startsWith("/")) ? next : "/app/settings/team-roles";
        nav(target, { replace: true });
      } catch {
        nav("/login", { replace: true });
      }
    };
    run();
  }, [search, nav]);

  return <div className="p-6">Completing sign in…</div>;
}
