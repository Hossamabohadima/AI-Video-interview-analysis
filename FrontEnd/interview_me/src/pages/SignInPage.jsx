import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function SignInPage() {
  const navigate = useNavigate();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [productsOpen, setProductsOpen] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const productsRef = useRef(null);
  const closeTimeoutRef = useRef(null);

  const openProductsMenu = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
    }
    setProductsOpen(true);
  };

  const closeProductsMenu = () => {
    closeTimeoutRef.current = setTimeout(() => {
      setProductsOpen(false);
    }, 220);
  };

  useEffect(() => {
    function handleClickOutside(event) {
      if (productsRef.current && !productsRef.current.contains(event.target)) {
        setProductsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current);
      }
    };
  }, []);

  const handleAnalyzeInterviewNavigation = () => {
    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
      navigate("/signup");
      return;
    }

    navigate("/process-video");
  };

  const handleViewReportNavigation = () => {
    const accessToken = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");

    if (!accessToken) {
      navigate("/signup");
      return;
    }

    if (role === "RECRUITER") {
      navigate("/recruiter-history");
      return;
    }

    navigate("/candidate-history");
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/users/auth/login", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string" ? data.detail : "Login failed",
        );
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("token_type", data.token_type);
      localStorage.setItem("user_id", String(data.user_id));
      localStorage.setItem("role", data.role);
      localStorage.setItem("name", data.name);

      navigate("/process-video");
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const navItems = [
    { label: "Home", href: "/", active: false },
    { label: "How it works", href: "/how-it-works", active: false },
  ];

  return (
    <div className="min-h-screen w-full bg-[#E8E6E2] flex flex-col">
      <header className="w-full px-6 py-4 flex items-center justify-between relative z-30">
        <span
          style={{ fontFamily: "Pacifico" }}
          className="text-[#009986] text-3xl whitespace-nowrap"
        >
          Interview me
        </span>

        <nav className="hidden md:flex items-center gap-8">
          {navItems.map((item) => (
            <div key={item.label} className="relative flex items-center gap-1">
              <Link
                to={item.href}
                aria-current={item.active ? "page" : undefined}
                className={`font-bold text-lg transition-colors ${
                  item.active
                    ? "text-[#009986]"
                    : "text-[#566068] hover:text-[#009986]"
                }`}
              >
                {item.label}
              </Link>
            </div>
          ))}

          <div
            ref={productsRef}
            className="relative"
            onMouseEnter={openProductsMenu}
            onMouseLeave={closeProductsMenu}
          >
            <button
              type="button"
              onClick={() => setProductsOpen((prev) => !prev)}
              className={`flex items-center gap-1 font-bold text-lg transition-colors focus:outline-none ${
                productsOpen
                  ? "text-[#009986]"
                  : "text-[#566068] hover:text-[#009986]"
              }`}
            >
              <span>Products</span>
              <svg
                className={`w-2.5 h-2 transition-transform duration-200 ${
                  productsOpen ? "rotate-180" : ""
                }`}
                viewBox="0 0 13 11"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  d="M6.5 11L0.00480938 0.5L12.9952 0.5L6.5 11Z"
                  fill={productsOpen ? "#009986" : "#566068"}
                />
              </svg>
            </button>

            {productsOpen && (
              <div
                className="absolute top-full left-1/2 mt-3 z-40 w-[340px] -translate-x-1/2 rounded-[20px] bg-[#E6F7F5] px-5 py-5 shadow-[0_6px_14px_rgba(0,0,0,0.12)]"
                onMouseEnter={openProductsMenu}
                onMouseLeave={closeProductsMenu}
              >
                <div className="flex flex-col gap-4">
                  <button
                    type="button"
                    onClick={handleAnalyzeInterviewNavigation}
                    className="flex items-center gap-3 text-[#009986] transition-opacity hover:opacity-80 text-left"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="-3 0 30 24"
                      fill="none"
                      stroke="#0FA99D"
                      strokeWidth="2.4"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="h-10 w-10 shrink-0"
                    >
                      <path d="M20 16.5A4.5 4.5 0 0 0 17 8h-1.26A8 8 0 1 0 4 15.25" />
                      <path d="M12 20V11" />
                      <path d="m8.8 14.2 3.2-3.2 3.2 3.2" />
                    </svg>
                    <span className="text-[18px] font-bold leading-none">
                      Analyze my interview
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={handleViewReportNavigation}
                    className="flex items-center gap-3 text-[#009986] transition-opacity hover:opacity-80 text-left"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#009986"
                      strokeWidth="2.1"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="h-8 w-8 shrink-0"
                    >
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <path d="M14 2v6h6" />
                      <path d="M8 13h8" />
                      <path d="M8 17h5" />
                    </svg>
                    <span className="text-[18px] font-bold leading-none">
                      View my report
                    </span>
                  </button>
                </div>
              </div>
            )}
          </div>

          <Link to="/signup">
            <button
              type="button"
              className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl hover:bg-[#007a6e] transition-colors"
            >
              Sign up
            </button>
          </Link>
        </nav>

        <button
          type="button"
          className="md:hidden text-[#566068] focus:outline-none"
          aria-label="Toggle menu"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          <svg
            className="w-7 h-7"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {mobileMenuOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            )}
          </svg>
        </button>
      </header>

      {mobileMenuOpen && (
        <div className="md:hidden bg-white shadow-md px-6 py-4 flex flex-col gap-4">
          {navItems.map((item) => (
            <Link
              key={item.label}
              to={item.href}
              className={`text-left font-semibold text-lg ${
                item.active ? "text-[#009986]" : "text-[#566068]"
              }`}
            >
              {item.label}
            </Link>
          ))}

          <button
            type="button"
            onClick={() => setProductsOpen((prev) => !prev)}
            className={`flex items-center gap-2 text-left font-semibold text-lg transition-colors ${
              productsOpen ? "text-[#009986]" : "text-[#566068]"
            }`}
          >
            <span>Products</span>
            <svg
              className={`w-2.5 h-2 transition-transform duration-200 ${
                productsOpen ? "rotate-180" : ""
              }`}
              viewBox="0 0 13 11"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M6.5 11L0.00480938 0.5L12.9952 0.5L6.5 11Z"
                fill={productsOpen ? "#009986" : "#566068"}
              />
            </svg>
          </button>

          {productsOpen && (
            <div className="ml-4 flex flex-col gap-3 rounded-xl bg-[#E6F7F5] p-4">
              <button
                type="button"
                onClick={handleAnalyzeInterviewNavigation}
                className="text-[#009986] font-semibold text-left"
              >
                Analyze my interview
              </button>
              <button
                type="button"
                onClick={handleViewReportNavigation}
                className="text-[#009986] font-semibold text-left"
              >
                View my report
              </button>
            </div>
          )}

          <Link
            to="/signup"
            className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl w-fit hover:bg-[#007a6e] transition-colors inline-flex items-center justify-center"
          >
            Sign up
          </Link>
        </div>
      )}

      <main className="flex flex-1 items-center justify-center px-4 py-10">
        <div className="w-full max-w-[500px] rounded-[20px] bg-white px-10 py-12 shadow-[0_4px_12px_rgba(0,0,0,0.12)]">
          <h1 className="mb-10 text-center text-[40px] font-bold text-[#555555]">
            Welcome Back
          </h1>

          <form className="flex flex-col gap-5" onSubmit={handleLogin}>
            <div>
              <label className="mb-2 block text-[14px] font-semibold uppercase text-[#8B8B8B]">
                Email Address
              </label>
              <div className="flex h-[44px] items-center rounded-md border border-[#E5E7EB] bg-[#F3F4F6] px-3">
                <span className="mr-2 inline-flex h-5 w-5 items-center justify-center rounded-[4px] bg-[#0FA99D]">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-3 w-3"
                  >
                    <rect x="3" y="5" width="18" height="14" rx="2" />
                    <path d="M3 7l9 6 9-6" />
                  </svg>
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-transparent text-[14px] text-[#374151] outline-none"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-[14px] font-semibold uppercase text-[#8B8B8B]">
                Password
              </label>
              <div className="flex h-[44px] items-center rounded-md border border-[#E5E7EB] bg-[#F3F4F6] px-3">
                <span className="mr-2 inline-flex h-5 w-5 items-center justify-center rounded-[4px] bg-[#0FA99D]">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-3 w-3"
                  >
                    <rect x="3" y="11" width="18" height="11" rx="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-transparent text-[14px] text-[#374151] outline-none"
                />
              </div>
            </div>

            {error && <p className="text-sm text-red-500">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="mt-2 h-[46px] rounded-full bg-[#0FA99D] text-[18px] font-bold text-white hover:bg-[#0c8f85] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? "Logging in..." : "Log in"}
            </button>

            <button
              type="button"
              className="text-center text-[14px] text-[#8B8B8B] hover:text-[#0FA99D]"
            >
              Forgotten password?
            </button>

            <Link
              to="/signup"
              className="mt-2 inline-flex h-[46px] w-full items-center justify-center rounded-full border-2 border-[#0FA99D] bg-white text-[18px] font-bold text-[#0FA99D] hover:bg-[#F0FDFA]"
            >
              Create new account
            </Link>
          </form>
        </div>
      </main>

      <footer className="pb-4 text-center text-[11px] text-[#9CA3AF]">
        © 2026 Interview Me. All rights reserved.
      </footer>
    </div>
  );
}

export default SignInPage;
