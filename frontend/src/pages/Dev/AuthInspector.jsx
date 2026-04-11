import React from "react";

export default function AuthInspector() {
  return (
    <div style={{ padding: 24 }}>
      <h2>🔍 Auth Inspector</h2>
      <p>Last /api/v1/auth/me call result:</p>
      <pre style={{ 
        background: "#f5f5f5", 
        padding: 16, 
        borderRadius: 8,
        overflow: "auto",
        maxHeight: "80vh"
      }}>
        {JSON.stringify(window.__AUTH_DEBUG || { msg: "no auth debug yet" }, null, 2)}
      </pre>
      <p style={{ marginTop: 16, fontSize: "0.9em", opacity: 0.7 }}>
        Check browser console for "[AUTH-DEBUG]" logs to see all OAuth endpoint calls.
      </p>
    </div>
  );
}

