import { createContext, useContext, useEffect, useState } from "react";
import { getMe } from "../services/authService";
import { DEMO_MODE, DEMO_ROLE } from "../utils/constants";

const AuthContext = createContext(null);

function buildDemoUser() {
  return {
    id: localStorage.getItem("viewz_user_id") || "demo_user",
    email: "demo@viewz.local",
    role: (localStorage.getItem("viewz_user_role") || DEMO_ROLE || "manager").toLowerCase(),
    name: "Viewz Demo",
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        if (DEMO_MODE) {
          setUser(buildDemoUser());
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
