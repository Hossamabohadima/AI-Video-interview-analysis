import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import { AuthProvider, useAuth } from "./context/AuthContext";

import { HomePage } from "./pages/HomePage/HomePage";
import HowItWorksPage from "./pages/HowItWorksPage";
import CandidateHistoryPage from "./pages/CandidateHistoryPage";
import CandidateReportPage from "./pages/CandidateReportPage";
import RecruiterHistory from "./pages/RecruiterHistory/RecruiterHistory";
import RecruiterReport from "./pages/RecruiterReport/RecruiterReport";
import ProcessVideoPage from "./pages/ProcessVideoPage";
import SignInPage from "./pages/SignInPage";
import { SignUp } from "./pages/SignUp/SignUp";
import CandidateDashboard from "./pages/CandidateDashboard/CandidateDashboard";

const ProtectedRoute = ({ children }) => {
  const { isAuth, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#e5e4e2] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#009986] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return isAuth || true ? children : <Navigate to="/sign-in" replace />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="/sign-in" element={<SignInPage />} />
    <Route path="/signup" element={<SignUp />} />
    <Route path="/how-it-works" element={<HowItWorksPage />} />
    <Route path="/history" element={<CandidateHistoryPage />} />
    <Route path="/report/:id" element={<CandidateReportPage />} />
    <Route path="/process-video" element={<ProcessVideoPage />} />
    <Route
      path="/dashboard"
      element={
        <ProtectedRoute>
          <CandidateDashboard />
        </ProtectedRoute>
      }
    />
    <Route
      path="/recruiter-history"
      element={
        <ProtectedRoute>
          <RecruiterHistory />
        </ProtectedRoute>
      }
    />
    <Route
      path="/recruiter-report"
      element={
        <ProtectedRoute>
          <RecruiterReport />
        </ProtectedRoute>
      }
    />
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
