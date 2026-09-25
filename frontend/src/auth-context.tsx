import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { CurrentUser, getUser, saveUser, clearUser } from "./api";

type Ctx = {
  user: CurrentUser | null;
  loading: boolean;
  setUser: (u: CurrentUser | null) => Promise<void>;
};

const AuthContext = createContext<Ctx>({ user: null, loading: true, setUser: async () => {} });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const u = await getUser();
      setUserState(u);
      setLoading(false);
    })();
  }, []);

  const setUser = useCallback(async (u: CurrentUser | null) => {
    if (u) {
      await saveUser(u);
    } else {
      await clearUser();
    }
    setUserState(u);
  }, []);

  return <AuthContext.Provider value={{ user, loading, setUser }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
