// src/pages/Auth/AcceptInvite.jsx
import { useEffect, useState } from "react";
import { acceptInvite } from "../../services/teamService";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { apiPost } from "../../services/apiClient";

export default function AcceptInvite() {
  const { token } = useParams();
  const [state, setState] = useState("loading");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const { user } = useAuth();

  async function redirectToLogin() {
    try {
      const next = `/invite/accept/${token}`;
      const res = await apiPost("/api/v1/auth/login", { provider: "google", state: next });
      
      // Check for oauth_skipped_in_local response
      if (res.status === "oauth_skipped_in_local") {
        setMessage(res.message || "Google OAuth is not configured in local development. Using Supabase auth only.");
        console.warn("[OAuth] OAuth skipped in local dev:", res.reason);
        return;
      }
      
      const url = res.oauth_redirect_url || res.url || res.redirect || "";
      if (url) {
        window.location.href = url;
      } else {
        setMessage("Login redirect not available.");
      }
    } catch (error) {
      console.error("[OAuth] Login error:", error);
      setMessage("Login failed to start.");
      setState("error");
    }
  }

  useEffect(() => {
    const run = async () => {
      try {
        if (!user) {
          setState("auth");
          return;
        }
        const res = await acceptInvite(token);
        if (res.accepted) {
          setState("success");
          setTimeout(() => navigate("/app/settings/team-roles"), 1200);
        } else {
          setState("error");
          setMessage("Could not accept invite.");
        }
      } catch (e) {
        setMessage("Invite failed");
        setState("error");
      }
    };
    run();
  }, [token, user, navigate]);

  if (state === "loading") return <div className="p-6">Accepting invite…</div>;
  if (state === "auth") {
    return (
      <div className="p-6 space-y-3">
        <div className="text-lg font-semibold">Please log in to accept your invite.</div>
        <button className="btn btn-primary" onClick={redirectToLogin}>
          Log in
        </button>
      </div>
    );
  }
  if (state === "success") return <div className="p-6 text-green-600">Invite accepted. Redirecting…</div>;
  return <div className="p-6 text-red-600">Invite failed: {message || "Try again or contact admin."}</div>;
}

