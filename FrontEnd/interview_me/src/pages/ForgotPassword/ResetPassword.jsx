import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import PublicNavbar  from "../../components/PublicNavbar/PublicNavbar";
import { resetPassword } from "../../services/api";

// ── STEP INDICATOR ────────────────────────────────────────────────────────────

const StepIndicator = ({ current }) => (
  <div className="flex items-center justify-center gap-2 mb-8">
    {[1, 2, 3].map((step) => (
      <div
        key={step}
        className={`h-1 w-10 rounded-full transition-all duration-300 ${
          step <= current ? "bg-[#009986]" : "bg-gray-200"
        }`}
      />
    ))}
  </div>
);

// ── PAGE ──────────────────────────────────────────────────────────────────────

const ResetPassword = () => {
  const navigate              = useNavigate();
  const [searchParams]        = useSearchParams();
  const token                 = searchParams.get("token") || "";

  const [newPassword, setNewPassword] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState("");
  const [success,     setSuccess]     = useState(false);

  // No token in URL
  if (!token) {
    return (
      <div className="min-h-screen bg-[#e5e4e2] flex flex-col">
        <PublicNavbar activePage="" />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="bg-white rounded-3xl shadow-md w-full max-w-md px-8 py-10 text-center">
            <h1 className="text-xl font-bold text-gray-700 mb-4">Invalid Reset Link</h1>
            <p className="text-gray-400 text-sm mb-6">
              This password reset link is invalid or has expired.
            </p>
            <button
              type="button"
              onClick={() => navigate("/forgot-password")}
              className="w-full h-12 bg-[#009986] text-white font-bold rounded-2xl hover:bg-[#007a6e] transition-colors"
            >
              Request a new link
            </button>
          </div>
        </main>
      </div>
    );
  }

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError("");

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirmPass) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, newPassword);
      setSuccess(true);
      setTimeout(() => navigate("/sign-in"), 3000);
    } catch (err) {
      setError(err.message || "Failed to reset password. The link may have expired.");
    } finally {
      setLoading(false);
    }
  };

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-[#e5e4e2] flex flex-col">
        <PublicNavbar activePage="" />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="bg-white rounded-3xl shadow-md w-full max-w-md px-8 py-10 text-center">
            <StepIndicator current={3} />
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <h1 className="text-2xl font-bold text-[#333] mb-2">Password Reset!</h1>
            <p className="text-gray-400 text-sm mb-6">
              Your password has been reset successfully. Redirecting you to login...
            </p>
            <div className="w-6 h-6 border-2 border-[#009986] border-t-transparent rounded-full animate-spin mx-auto" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex flex-col">
      <PublicNavbar activePage="" />

      <main className="flex-1 flex items-center justify-center px-4 py-10">
        <div className="bg-white rounded-3xl shadow-md w-full max-w-md px-8 py-10">

          <StepIndicator current={3} />

          <h1 className="text-2xl sm:text-3xl font-bold text-[#333] text-center mb-2">
            Create new password
          </h1>
          <p className="text-gray-400 text-sm text-center mb-8">
            Your new password must be different from your previous password.
          </p>

          <form onSubmit={handleResetPassword} className="flex flex-col gap-5">

            {/* New password */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                New Password
              </label>
              <div className={`flex items-center gap-3 bg-gray-100 border rounded-xl px-4 h-12 focus-within:border-[#009986] transition-colors ${
                error && newPassword.length < 8 ? "border-red-400" : "border-gray-200"
              }`}>
                <svg className="w-4 h-4 text-[#009986] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => { setNewPassword(e.target.value); setError(""); }}
                  placeholder="Min. 8 characters"
                  className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 focus:outline-none"
                  autoComplete="new-password"
                  required
                />
              </div>
            </div>

            {/* Confirm password */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                Confirm Password
              </label>
              <div className={`flex items-center gap-3 bg-gray-100 border rounded-xl px-4 h-12 focus-within:border-[#009986] transition-colors ${
                error && newPassword !== confirmPass ? "border-red-400" : "border-gray-200"
              }`}>
                <svg className="w-4 h-4 text-[#009986] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <input
                  type="password"
                  value={confirmPass}
                  onChange={(e) => { setConfirmPass(e.target.value); setError(""); }}
                  placeholder="Re-enter new password"
                  className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 focus:outline-none"
                  autoComplete="new-password"
                  required
                />
              </div>
            </div>

            {error && <p className="text-red-500 text-sm text-center">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-[#009986] text-white font-bold text-base rounded-2xl hover:bg-[#007a6e] transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Resetting...
                </>
              ) : "Reset password"}
            </button>

            <button
              type="button"
              onClick={() => navigate("/sign-in")}
              className="text-center text-sm text-[#009986] font-semibold hover:underline"
            >
              ← Back to log in
            </button>
          </form>
        </div>
      </main>

      <footer className="py-6 text-center">
        <p className="text-[#888888] text-xs">
          &copy; {new Date().getFullYear()} Interview Me. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default ResetPassword;