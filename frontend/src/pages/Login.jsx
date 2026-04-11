import { useMemo } from "react";
import { startGoogleLogin } from "../services/authService";
import { DEMO_MODE } from "../utils/constants";

export default function Login() {
  const params = new URLSearchParams(window.location.search);
  const rawState = params.get("state");
  
  // Only accept valid absolute paths
  const state = useMemo(() => (rawState && rawState.startsWith("/")) ? rawState : null, [rawState]);

  async function handleLogin() {
    await startGoogleLogin(state ?? "/app/settings/team-roles");
  }

  return (
    <div className="p-6 flex flex-col items-center justify-center h-screen space-y-4">
      <h2 className="text-2xl font-semibold">Sign in to Viewz</h2>
      <button className="btn btn-primary" onClick={handleLogin}>
        {DEMO_MODE ? "Continue in Demo" : "Continue with Google"}
      </button>
    </div>
  );
}
