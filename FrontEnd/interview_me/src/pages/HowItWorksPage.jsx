import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function HowItWorksPage() {
  const navigate = useNavigate();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [productsOpen, setProductsOpen] = useState(false);

  const productsRef = useRef(null);
  const closeTimeoutRef = useRef(null);

  const openProductsMenu = () => {
    if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current);
    setProductsOpen(true);
  };

  const closeProductsMenu = () => {
    closeTimeoutRef.current = setTimeout(() => setProductsOpen(false), 220);
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
      if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current);
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

    navigate("/history");
  };

  const navItems = [
    { label: "Home", href: "/", active: false },
    { label: "How it works", href: "/how-it-works", active: true },
  ];

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex flex-col">
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

      <main className="flex-1">
        <section
          aria-labelledby="how-it-works-heading"
          className="w-full max-w-[1200px] mx-auto px-6 pt-20"
        >
          <h1
            id="how-it-works-heading"
            className="text-center text-[40px] font-bold text-[#009986]"
          >
            How It works ?
          </h1>

          <div className="relative mt-32">
            <div className="hidden md:block absolute left-[12.5%] right-[12.5%] top-[52px] h-[2px] bg-[#009986]" />

            <div className="relative z-10 grid grid-cols-1 md:grid-cols-4 gap-12 md:gap-0 items-start text-center">
              <div className="flex flex-col items-center">
                <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-[#E5E4E2]">
                  <img
                    src="https://c.animaapp.com/zou3Gdv0/img/group-7@2x.png"
                    alt="Upload video icon"
                    className="h-[100px] w-[100px] object-contain"
                  />
                </div>
                <div className="mt-10 text-[25px] font-bold text-[#808080] leading-tight">
                  Upload
                  <br />
                  Video
                </div>
              </div>

              <div className="flex flex-col items-center">
                <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-neutral-200">
                  <img
                    src="https://c.animaapp.com/zou3Gdv0/img/extraction-icon.svg"
                    alt="Extraction icon"
                    className="h-[67px] w-[67px]"
                  />
                </div>
                <div className="mt-10 text-[25px] font-bold text-[#808080] leading-tight">
                  Extract Streams
                  <br />
                  (Audio, Text, Visual)
                </div>
              </div>

              <div className="flex flex-col items-center">
                <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-neutral-200">
                  <img
                    src="https://c.animaapp.com/zou3Gdv0/img/ai-engine-icon.svg"
                    alt="AI engine icon"
                    className="h-[85px] w-[85px]"
                  />
                </div>
                <div className="mt-10 text-[25px] font-bold text-[#808080] leading-tight">
                  Ai Engine
                  <br />
                  Analysis
                </div>
              </div>

              <div className="flex flex-col items-center">
                <div className="flex h-[100px] w-[100px] items-center justify-center rounded-full border-2 border-[#009986] bg-neutral-200">
                  <img
                    src="https://c.animaapp.com/zou3Gdv0/img/report.svg"
                    alt="Report"
                    className="h-[65px] w-[65px]"
                  />
                </div>
                <div className="mt-10 text-[25px] font-bold text-[#808080] leading-tight">
                  Get Practical
                  <br />
                  Report
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="py-6">
        <p className="text-xs font-normal text-[#888888] text-center">
          © 2026 Interview Me. All rights reserved.
        </p>
      </footer>
    </div>
  );
}

export default HowItWorksPage;
