import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PublicNavbar    from "../../components/PublicNavbar/PublicNavbar";
import { forgotPassword } from "../../services/api";

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

const ForgotPassword = () => {
  const navigate = useNavigate();

  const [step,    setStep]    = useState(1);
  const [email,   setEmail]   = useState("");
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");

  // ── Step 1: Send reset email ───────────────────────────────────────────────
  const handleSendEmail = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !email.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);
    try {
      await forgotPassword(email);
      setStep(2);
    } catch (err) {
      setError(err.message || "Failed to send reset email. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex flex-col">
      <PublicNavbar activePage="" />

      <main className="flex-1 flex items-center justify-center px-4 py-10">
        <div className="bg-white rounded-3xl shadow-md w-full max-w-md px-8 py-10">

          <StepIndicator current={step} />

          {/* ── STEP 1: Enter Email ── */}
          {step === 1 && (
            <>
              <h1 className="text-2xl sm:text-3xl font-bold text-[#333] text-center mb-2">
                Forgot password?
              </h1>
              <p className="text-gray-400 text-sm text-center mb-8">
                No worries — enter your email address and we'll send you a reset link.
              </p>

              <form onSubmit={handleSendEmail} className="flex flex-col gap-5">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                    Email Address
                  </label>
                  <div className={`flex items-center gap-3 bg-gray-100 border rounded-xl px-4 h-12 focus-within:border-[#009986] transition-colors ${
                    error ? "border-red-400" : "border-gray-200"
                  }`}>
                    <svg className="w-4 h-4 text-[#009986] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => { setEmail(e.target.value); setError(""); }}
                      placeholder="name@example.com"
                      className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 focus:outline-none"
                      autoComplete="email"
                      required
                    />
                  </div>
                  {error && <p className="text-red-500 text-xs">{error}</p>}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 bg-[#009986] text-white font-bold text-base rounded-2xl hover:bg-[#007a6e] transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Sending...
                    </>
                  ) : "Send reset link"}
                </button>

                <div className="text-center text-gray-300 text-sm">or</div>

                <button
                  type="button"
                  onClick={() => navigate("/sign-in")}
                  className="text-center text-sm text-[#009986] font-semibold hover:underline"
                >
                  ← Back to log in
                </button>
              </form>
            </>
          )}

          {/* ── STEP 2: Check Email ── */}
          {step === 2 && (
            <>
              {/* Email icon */}
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4" />
                  </svg>
                </div>
              </div>

              <h1 className="text-2xl sm:text-3xl font-bold text-[#333] text-center mb-2">
                Check your email
              </h1>
              <p className="text-gray-400 text-sm text-center mb-8">
                We sent a password reset link to <span className="font-semibold text-gray-600">{email}</span>.
                Click the link in the email to reset your password.
              </p>

              <div className="flex flex-col gap-4">
                <p className="text-xs text-gray-400 text-center">
                  Didn't receive the email? Check your spam folder or
                </p>

                <button
                  type="button"
                  onClick={() => { setStep(1); setError(""); }}
                  className="w-full h-12 bg-white border-2 border-[#009986] text-[#009986] font-bold text-base rounded-2xl hover:bg-gray-50 transition-colors"
                >
                  Try a different email
                </button>

                <button
                  type="button"
                  onClick={() => navigate("/sign-in")}
                  className="text-center text-sm text-[#009986] font-semibold hover:underline"
                >
                  ← Back to log in
                </button>
              </div>
            </>
          )}
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

export default ForgotPassword;