import { createContext, useContext, useEffect, useState } from "react";
import { getMe } from "../services/authService";
import { isSupabaseConfigured } from "../lib/supabaseClient";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        if (!isSupabaseConfigured) {
          setUser(null);
          return;
        }

        const me = await getMe(); // expect { id, email, role } or { user: { id, email, role } }
        const userData = me.user || me;
        setUser({ id: userData.id, email: userData.email, role: userData.role });
      } catch {
        setUser(null);
      } finally {
        setReady(true);
      }
    })();
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
