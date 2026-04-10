import { supabase } from "../lib/supabaseClient";
import api from "../services/apiClient";

export default async function debugAuth() {
  console.log("🧠 Supabase Auth Debug");

  const { data, error } = await supabase.auth.getSession();

  if (error) {
    console.error("❌ supabase.auth.getSession() error:", error);
    return;
  }

  if (!data?.session) {
    console.warn("⚠️ No active Supabase session — log in first.");
    return;
  }

  const token = data.session.access_token;
  console.log("✅ Supabase session found");
  console.log("user:", data.session.user);
  console.log("token (first 40):", token.slice(0, 40) + "...");

  try {
    const me = await api.get("/api/v1/auth/me");
    console.log("✅ Backend authorized response:", me.data);
  } catch (e) {
    console.error("❌ Backend rejected token:", e?.response?.status, e?.response?.data);
  }
}

