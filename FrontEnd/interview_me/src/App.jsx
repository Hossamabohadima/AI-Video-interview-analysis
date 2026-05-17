import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import HowItWorksPage from "./pages/HowItWorksPage";
import CandidateHistoryPage from "./pages/CandidateHistoryPage";
import SignInPage from "./pages/SignInPage";
import CandidateReportPage from "./pages/CandidateReportPage";
import ProcessVideoPage from "./pages/ProcessVideoPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/sign-in" replace />} />
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/how-it-works" element={<HowItWorksPage />} />
        <Route path="/history" element={<CandidateHistoryPage />} />
        <Route path="/report" element={<CandidateReportPage />} />
        <Route path="/process-video" element={<ProcessVideoPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
