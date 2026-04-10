import { Link, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

export default function Settings() {
  const location = useLocation();
  // Match both /settings and /app/settings paths
  const isGeneral = location.pathname === "/app/settings" || location.pathname === "/settings";
  const isChannels = location.pathname.includes("/channels");
  const isTeamRoles = location.pathname.includes("/team-roles");
  const isFeedback = location.pathname.includes("/feedback");
  const isIntegrations = location.pathname.includes("/integrations");
  const [theme, setTheme] = useState(localStorage.getItem("viewz_theme") || "light");
  
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("viewz_theme", theme);
  }, [theme]);
  
  const toggleTheme = () => setTheme(t => t === "light" ? "dark" : "light");

  return (
    <div className="space-y-4">
      <div className="tabs tabs-boxed">
        <Link className={`tab ${isGeneral ? "tab-active" : ""}`} to="/app/settings">General</Link>
        <Link className={`tab ${isChannels ? "tab-active" : ""}`} to="/app/settings/channels">Channels</Link>
        <Link className={`tab ${isIntegrations ? "tab-active" : ""}`} to="/app/settings/integrations">Integrations</Link>
        <Link className={`tab ${isTeamRoles ? "tab-active" : ""}`} to="/app/settings/team-roles">Team & Roles</Link>
        <Link className={`tab ${isFeedback ? "tab-active" : ""}`} to="/app/settings/feedback">Feedback</Link>
      </div>
      <div className="rounded-xl p-4 bg-base-100 border">
        <Outlet />
        {isGeneral && (
          <div className="mt-4">
            <p className="opacity-80 mb-2">Theme / Language / Timezone</p>
            <button className="btn" onClick={toggleTheme}>Toggle Theme</button>
          </div>
        )}
      </div>
    </div>
  );
}
