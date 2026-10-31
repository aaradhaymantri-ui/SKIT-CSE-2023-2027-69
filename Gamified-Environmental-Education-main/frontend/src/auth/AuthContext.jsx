import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { restoreSession, signIn as authenticate, signOut as endSession } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const expireSession = () => setUser(null);
    window.addEventListener("ecoquest:session-expired", expireSession);
    restoreSession().then((sessionUser) => {
      if (active) {
        setUser(sessionUser);
        setLoading(false);
      }
    });
    return () => {
      active = false;
      window.removeEventListener("ecoquest:session-expired", expireSession);
    };
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    signIn: async (email, password) => {
      const signedInUser = await authenticate(email, password);
      setUser(signedInUser);
      return signedInUser;
    },
    signOut: async () => {
      await endSession();
      setUser(null);
    },
  }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
