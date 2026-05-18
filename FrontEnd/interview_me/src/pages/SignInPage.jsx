import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

function SignInPage() {
  const [productsOpen, setProductsOpen] = useState(false);
  const productsRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (productsRef.current && !productsRef.current.contains(event.target)) {
        setProductsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="min-h-screen w-full bg-[#E8E6E2] flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between bg-[#E8E6E2] px-8 py-5">
        <div className="text-[32px] font-normal text-[#0FA99D] [font-family:'Pacifico',Helvetica]">
          Interview me
        </div>

        <nav className="flex items-center gap-10">
          <Link
            to="/"
            className="text-[18px] font-semibold text-[#56606B] hover:text-[#0FA99D]"
          >
            Home
          </Link>

          <Link
            to="/how-it-works"
            className="text-[18px] font-semibold text-[#56606B] hover:text-[#0FA99D]"
          >
            How it works
          </Link>

          <div
            ref={productsRef}
            className="relative flex flex-col items-center"
          >
            <button
              type="button"
              onClick={() => setProductsOpen((prev) => !prev)}
              className="flex flex-col items-center"
            >
              <span className="text-[18px] font-semibold text-[#56606B] hover:text-[#0FA99D]">
                Products
              </span>
              <span
                className={`text-[10px] text-[#56606B] transition-transform duration-200 ${
                  productsOpen ? "rotate-180" : ""
                }`}
              >
                ▼
              </span>
            </button>

            {productsOpen && (
              <div className="absolute top-[42px] left-1/2 z-30 w-[340px] -translate-x-1/2 rounded-[20px] bg-[#E6F7F5] px-5 py-5 shadow-[0_6px_14px_rgba(0,0,0,0.12)]">
                <div className="flex flex-col gap-4">
                  <Link
                    to="/process-video"
                    className="flex items-center gap-3 text-[#009986] transition-opacity hover:opacity-80"
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
                    <span className="[font-family:'Alegreya_Sans',Helvetica] text-[18px] font-bold leading-none">
                      Analyze my interview
                    </span>
                  </Link>

                  <Link
                    to="/report"
                    className="flex items-center gap-3 text-[#009986] transition-opacity hover:opacity-80"
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
                    <span className="[font-family:'Alegreya_Sans',Helvetica] text-[18px] font-bold leading-none">
                      View my report
                    </span>
                    </Link>
                </div>
              </div>
            )}
          </div>

          <Link
            to="/signup"
            className="rounded-full bg-[#0FA99D] px-6 py-2 text-[16px] font-semibold text-white hover:bg-[#0c8f85]"
          >
            Sign up
          </Link>
        </nav>
      </header>

      {/* Main */}
      <main className="flex flex-1 items-center justify-center px-4 py-10">
        <div className="w-full max-w-[500px] rounded-[20px] bg-white px-10 py-12 shadow-[0_4px_12px_rgba(0,0,0,0.12)]">
          <h1 className="mb-10 text-center text-[40px] font-bold text-[#555555]">
            Welcome Back
          </h1>

          <form className="flex flex-col gap-5">
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
                  placeholder=""
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
                  placeholder=""
                  className="w-full bg-transparent text-[14px] text-[#374151] outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              className="mt-2 h-[46px] rounded-full bg-[#0FA99D] text-[18px] font-bold text-white hover:bg-[#0c8f85]"
            >
              Log in
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

      {/* Footer */}
      <footer className="pb-4 text-center text-[11px] text-[#9CA3AF]">
        © 2026 Interview Me. All rights reserved.
      </footer>
    </div>
  );
}

export default SignInPage;
