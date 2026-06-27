import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { login as apiLogin, signUp as apiSignUp, logoutApi } from "../services/api";

const AuthContext = createContext(null);

// ── HELPERS ───────────────────────────────────────────────────────────────────

const getInitials = (name = "") =>
  name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);

const getRoleLabel = (role = "") => {
  if (role === "RECRUITER") return "Recruiter Admin";
  if (role === "USER")      return "Candidate";
  return role;
};

const persistAuth = (user, token) => {
  localStorage.setItem("access_token", token);
  localStorage.setItem("token",        token); // keep for compatibility
  localStorage.setItem("user",         JSON.stringify(user));
  localStorage.setItem("name",         user.name);
  localStorage.setItem("role",         user.role);
  localStorage.setItem("user_id",      String(user.user_id));
};

const clearAuth = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("name");
  localStorage.removeItem("role");
  localStorage.removeItem("user_id");
  localStorage.removeItem("token_type");
};

const loadPersistedUser = () => {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

// ── PROVIDER ──────────────────────────────────────────────────────────────────

export const AuthProvider = ({ children }) => {
  const [user,      setUser]      = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error,     setError]     = useState(null);

  // Rehydrate from localStorage on mount
  useEffect(() => {
    const token      = localStorage.getItem("access_token") || localStorage.getItem("token");
    const cachedUser = loadPersistedUser();
    if (token && cachedUser) setUser(cachedUser);
    setIsLoading(false);
  }, []);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    setError(null);
    setIsLoading(true);
    try {
      const tokenData = await apiLogin({ email, password });

      const user = {
        user_id:   tokenData.user_id,
        role:      tokenData.role,
        roleLabel: getRoleLabel(tokenData.role),
        name:      tokenData.name || localStorage.getItem("name") || email.split("@")[0],
        email,
        initials:  getInitials(tokenData.name || email.split("@")[0]),
      };

      persistAuth(user, tokenData.access_token);
      setUser(user);
      return user;
    } catch (err) {
      setError(err.message || "Login failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ── Sign Up ───────────────────────────────────────────────────────────────
  const signUp = useCallback(async (userData) => {
    setError(null);
    setIsLoading(true);
    try {
      const payload = {
        name:         userData.fullName  || userData.name,
        email:        userData.email,
        password:     userData.password,
        phone_number: userData.phone     || userData.phone_number || null,
        role:         userData.userType === "Company" ? "RECRUITER" : "USER",
      };

      const newUser = await apiSignUp(payload);

      // Auto-login after signup to get token
      const tokenData = await apiLogin({
        email:    payload.email,
        password: payload.password,
      });

      const user = {
        user_id:   newUser.user_id,
        name:      newUser.name,
        email:     newUser.email,
        role:      newUser.role,
        roleLabel: getRoleLabel(newUser.role),
        initials:  getInitials(newUser.name),
        created_date: newUser.created_date,
      };

      persistAuth(user, tokenData.access_token);
      setUser(user);
      return user;
    } catch (err) {
      setError(err.message || "Sign up failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ── Logout ────────────────────────────────────────────────────────────────
  const logout = useCallback(async () => {
    setError(null);
    try {
      // Blacklist token on backend
      await logoutApi();
    } catch {
      // Even if backend call fails, clear local auth
    } finally {
      clearAuth();
      setUser(null);
    }
  }, []);

  const value = {
    user,
    isLoading,
    error,
    isAuth: !!user,
    login,
    signUp,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>");
  return context;
};

export default AuthContext;