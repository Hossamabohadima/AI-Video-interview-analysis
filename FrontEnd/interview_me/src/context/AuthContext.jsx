import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { getCurrentUser, login as apiLogin, logout as apiLogout, signUp as apiSignUp } from "../services/api";

/**
 * AuthContext
 * Global authentication state — user, loading, error.
 * Any component can access this via useAuth().
 *
 * Provides:
 * - user       : current user object or null
 * - isLoading  : true while checking auth status
 * - error      : last auth error message or null
 * - isAuth     : true if user is logged in
 * - login(email, password)
 * - signUp(userData)
 * - logout()
 */

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user,      setUser]      = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error,     setError]     = useState(null);

  // ── Check if user is already logged in on mount ───────────────────────────
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        localStorage.removeItem("token");
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    setError(null);
    setIsLoading(true);
    try {
      const { user: loggedInUser, token } = await apiLogin(email, password);
      localStorage.setItem("token", token);
      setUser(loggedInUser);
      return loggedInUser;
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
      const { user: newUser, token } = await apiSignUp(userData);
      localStorage.setItem("token", token);
      setUser(newUser);
      return newUser;
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
      await apiLogout();
    } finally {
      localStorage.removeItem("token");
      setUser(null);
    }
  }, []);

  const value = {
    user,
    isLoading,
    error,
    isAuth:  !!user,
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

/**
 * useAuth
 * Hook to access auth context anywhere in the app.
 * Throws if used outside AuthProvider.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }
  return context;
};

export default AuthContext;