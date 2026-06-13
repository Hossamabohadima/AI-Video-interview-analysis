import { useId, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import polygon1 from "../../assets/polygon.svg";

const navItems = [
  { label: "Home", href: "/" },
  { label: "How it works", href: "/how-it-works" },
  { label: "Products", href: "/process-video", hasDropdown: true },
];

const fieldDefinitions = [
  {
    key: "fullName",
    label: "Full Name",
    type: "text",
    autoComplete: "name",
    placeholder: "John Doe",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
  },
  {
    key: "email",
    label: "Email Address",
    type: "email",
    autoComplete: "email",
    placeholder: "you@example.com",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    key: "phone",
    label: "Phone Number",
    type: "tel",
    autoComplete: "tel",
    placeholder: "+1 234 567 8900",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
    ),
  },
  {
    key: "password",
    label: "Password",
    type: "password",
    autoComplete: "new-password",
    placeholder: "••••••••",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
  },
  {
    key: "confirmPassword",
    label: "Confirm Password",
    type: "password",
    autoComplete: "new-password",
    placeholder: "••••••••",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
  },
];

const initialFormState = {
  fullName: "",
  email: "",
  phone: "",
  password: "",
  confirmPassword: "",
};

export const SignUp = () => {
  const [userType, setUserType] = useState("Candidate");
  const [formState, setFormState] = useState(initialFormState);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const formId = useId();

  const fieldIds = useMemo(() => ({
    fullName: `${formId}-full-name`,
    email: `${formId}-email`,
    phone: `${formId}-phone`,
    password: `${formId}-password`,
    confirmPassword: `${formId}-confirm-password`,
  }), [formId]);

  const handleInputChange = (field) => (e) => {
    setFormState((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
  };

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex flex-col">

      {/* ── NAVBAR ── */}
      <header className="w-full px-6 py-4 flex items-center justify-between">
        <Link to="/" aria-label="Interview me home" className="font-['Pacifico'] text-[#009986] text-2xl md:text-3xl whitespace-nowrap">
          Interview me
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8" aria-label="Primary navigation">
          {navItems.map((item) => (
            <div key={item.label} className="relative flex flex items-center gap-1">
              <Link
                to={item.href}
                className="font-bold text-lg text-[#566068] hover:text-[#009986] transition-colors"
              >
                {item.label}
              </Link>
              {item.hasDropdown && (
                <img src={polygon1} alt="" className="w-2.5 h-2 mt-1" aria-hidden="true" />
              )}
            </div>
          ))}
          <a
            href="#signup-form"
            className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl hover:bg-[#007a6e] transition-colors"
            aria-current="page"
          >
            Sign up
          </a>
        </nav>

        {/* Mobile Hamburger */}
        <button
          type="button"
          className="md:hidden text-[#566068]"
          aria-label="Toggle menu"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {mobileMenuOpen
              ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            }
          </svg>
        </button>
      </header>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white shadow-md px-6 py-4 flex flex-col gap-4">
          {navItems.map((item) => (
            <a key={item.label} href={item.href} className="font-semibold text-lg text-[#566068]">
              {item.label}
            </a>
          ))}
          <a href="#signup-form" className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl w-fit hover:bg-[#007a6e] transition-colors">
            Sign up
          </a>
        </div>
      )}

      {/* ── MAIN CONTENT ── */}
      <main className="flex-1 flex items-center justify-center px-4 py-10">
        <section
          id="signup-form"
          aria-labelledby="signup-title"
          className="bg-white rounded-3xl shadow-md w-full max-w-md px-8 py-10"
        >
          {/* Title */}
          <h1 id="signup-title" className="text-2xl sm:text-3xl font-bold text-[#494949] text-center mb-1">
            Create your account
          </h1>
          <p className="text-[#808080] text-sm text-center mb-6">
            Join the next generation of interview preparation
          </p>

          {/* User Type Toggle */}
          <div
            role="tablist"
            aria-label="Account type"
            className="relative flex bg-[#ececec] rounded-xl p-1 mb-6"
          >
            <div
              className={`absolute top-1 bottom-1 bg-white rounded-[10px] transition-all duration-200 ${
                userType === "Candidate" ? "left-1 right-1/2" : "left-1/2 right-1"
              }`}
            />
            <button
              type="button"
              role="tab"
              aria-selected={userType === "Candidate"}
              onClick={() => setUserType("Candidate")}
              className={`relative z-10 flex-1 py-1.5 text-base font-semibold rounded-[10px] transition-colors ${
                userType === "Candidate" ? "text-[#009986]" : "text-[#888]"
              }`}
            >
              Candidate
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={userType === "Company"}
              onClick={() => setUserType("Company")}
              className={`relative z-10 flex-1 py-1.5 text-base font-semibold rounded-[10px] transition-colors ${
                userType === "Company" ? "text-[#009986]" : "text-[#888]"
              }`}
            >
              Company
            </button>
          </div>

          {/* Form Fields */}
          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
            {fieldDefinitions.map((field) => (
              <div key={field.key} className="flex flex-col gap-1">
                <label
                  htmlFor={fieldIds[field.key]}
                  className="text-xs font-semibold text-[#808080] uppercase tracking-wider"
                >
                  {field.label}
                </label>
                <div className="flex items-center gap-3 bg-[#f2f2f2] border border-[#d3d3d3] rounded-xl px-3 h-11 focus-within:border-[#009986] transition-colors">
                  {field.icon}
                  <input
                    id={fieldIds[field.key]}
                    name={field.key}
                    type={field.type}
                    autoComplete={field.autoComplete}
                    placeholder={field.placeholder}
                    value={formState[field.key]}
                    onChange={handleInputChange(field.key)}
                    className="flex-1 bg-transparent text-sm text-[#494949] placeholder:text-[#b0b0b0] focus:outline-none"
                  />
                </div>
              </div>
            ))}

            {/* Submit */}
            <button
              type="submit"
              className="mt-2 w-full bg-[#009986] text-white font-bold text-lg py-2.5 rounded-2xl hover:bg-[#007a6e] transition-colors"
            >
              Create Account
            </button>

            <div className="text-center text-[#d9d9d9] font-bold text-lg">or</div>

            <Link
              to="/sign-in"
              className="w-full border-2 border-[#009986] text-[#009986] font-bold text-lg py-2.5 rounded-2xl text-center hover:bg-[#e5e4e2] transition-colors"
            >
              Log in
            </Link>
          </form>
        </section>
      </main>

      {/* ── FOOTER ── */}
      <footer className="py-6 text-center">
        <p className="text-[#888888] text-xs">
          © 2026 Interview Me. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default SignUp;