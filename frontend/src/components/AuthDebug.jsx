import React, { useState } from "react";
import { supabase } from "../lib/supabaseClient";

export default function AuthDebug() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setMsg("Signing in...");
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) return setMsg(`❌ ${error.message}`);
    setMsg(`✅ Logged in as ${data.user.email}`);
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    setMsg("Signed out.");
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>🔐 Supabase Auth Debug</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ display: "block", margin: "8px 0", padding: "6px 10px" }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ display: "block", margin: "8px 0", padding: "6px 10px" }}
        />
        <button type="submit">Login</button>
      </form>
      <button onClick={handleLogout} style={{ marginTop: 10 }}>Logout</button>
      <p>{msg}</p>
    </div>
  );
}

