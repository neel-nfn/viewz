import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.trim();
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY?.trim();
export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

function createDisabledSupabaseClient() {
  const disabledError = new Error("Supabase is not configured for this deployment.");

  return {
    auth: {
      async getSession() {
        return { data: { session: null }, error: null };
      },
      async getUser() {
        return { data: { user: null }, error: disabledError };
      },
      async signInWithPassword() {
        return { data: { user: null, session: null }, error: disabledError };
      },
      async signOut() {
        return { data: null, error: null };
      },
      async signInWithOAuth() {
        return { data: null, error: disabledError };
      },
      onAuthStateChange() {
        return {
          data: {
            subscription: {
              unsubscribe() {},
            },
          },
          error: null,
        };
      },
    },
  };
}

if (!isSupabaseConfigured) {
  console.info("Supabase env vars missing in frontend. Demo auth fallback is active.");
}

export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
      },
    })
  : createDisabledSupabaseClient();

if (typeof window !== "undefined") {
  window.supabase = supabase;
}
