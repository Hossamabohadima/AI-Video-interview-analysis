import "./index.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";

import { HomePage }           from "./pages/HomePage/HomePage";
import { SignUp }             from "./pages/SignUp/SignUp";
import { CandidateDashboard } from "./pages/CandidateDashboard/CandidateDashboard";
import { RecruiterHistory }   from "./pages/RecruiterHistory/RecruiterHistory";
import { RecruiterReport }    from "./pages/RecruiterReport/RecruiterReport";

/**
 * ProtectedRoute
 * Wraps any route that requires authentication.
 *
 * Current behavior (mock mode):
 * - Allows all access since there's no real auth yet.
 *
 * When backend is ready:
 * - Add REACT_APP_API_URL to your .env file
 * - Remove the `|| true` on the isAuth check below
 * - Real auth will kick in automatically via AuthContext
 */
const ProtectedRoute = ({ children }) => {
  const { isAuth, isLoading } = useAuth();

  // Show spinner while checking auth status
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#e5e4e2] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#009986] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // TODO: when backend is ready, remove `|| true` below
  return isAuth || true ? children : <Navigate to="/signup" replace />;
};

const AppRoutes = () => (
  <Routes>
    {/* Public routes */}
    <Route path="/"       element={<HomePage />} />
    <Route path="/signup" element={<SignUp />}   />

    {/* Protected routes */}
    <Route path="/dashboard" element={
      <ProtectedRoute><CandidateDashboard /></ProtectedRoute>
    } />
    <Route path="/recruiter-history" element={
      <ProtectedRoute><RecruiterHistory /></ProtectedRoute>
    } />
    <Route path="/recruiter-report" element={
      <ProtectedRoute><RecruiterReport /></ProtectedRoute>
    } />

    {/* Fallback — redirect unknown routes to home */}
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

const App = () => (
  <BrowserRouter>
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  </BrowserRouter>
);

export default App;