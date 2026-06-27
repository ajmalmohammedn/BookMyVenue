import { createContext, useContext, useState } from "react";
import * as authApi from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useState(() => {
    try { return JSON.parse(localStorage.getItem("bmv_tokens")); }
    catch { return null; }
  });

  const saveLogin = (userData, tokenData) => {
    setUser(userData);
    setTokens(tokenData);
    localStorage.setItem("bmv_tokens", JSON.stringify(tokenData));
  };

  const doLogout = async () => {
    try {
      if (tokens?.refresh) await authApi.logout(tokens.refresh);
    } catch {}
    setUser(null);
    setTokens(null);
    localStorage.removeItem("bmv_tokens");
  };

  return (
    <AuthContext.Provider value={{ user, tokens, saveLogin, doLogout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
