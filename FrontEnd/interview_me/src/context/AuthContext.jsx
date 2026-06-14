import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { login as apiLogin, signUp as apiSignUp } from "../services/api";

/**
 * AuthContext
 * Global authentication state using real JWT backend.
 *
 * Token shape from backend:
 * { access_token, token_type: "bearer", user_id, role }
 *
 * User shape stored in context:
 * { user_id, name, email, role, roleLabel, initials }
 */

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
  localStorage.setItem("token", token);
  localStorage.setItem("user",  JSON.stringify(user));
};

const clearAuth = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
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
    const token      = localStorage.getItem("token");
    const cachedUser = loadPersistedUser();
    if (token && cachedUser) setUser(cachedUser);
    setIsLoading(false);
  }, []);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    setError(null);
    setIsLoading(true);
    try {
      // POST /users/auth/login → { access_token, token_type, user_id, role }
      const tokenData = await apiLogin({ email, password });

      const user = {
        user_id:   tokenData.user_id,
        role:      tokenData.role,
        roleLabel: getRoleLabel(tokenData.role),
        name:      email.split("@")[0],
        email,
        initials:  getInitials(email.split("@")[0]),
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
      // Map frontend fields → backend Registration schema
      const payload = {
        name:         userData.fullName  || userData.name,
        email:        userData.email,
        password:     userData.password,
        phone_number: userData.phone     || userData.phone_number || null,
        role:         userData.userType === "Company" ? "RECRUITER" : "USER",
      };

      // POST /users/auth/signup → { user_id, name, email, role, created_date }
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
  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
    setError(null);
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