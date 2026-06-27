import { useState, useId, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import PublicNavbar from "../../components/PublicNavbar/PublicNavbar";
import { useAuth }  from "../../context/AuthContext";
import { useSearchParams } from "react-router-dom";

const FIELD_DEFINITIONS = [
  {
    key: "fullName", label: "Full Name", type: "text",
    autoComplete: "name", placeholder: "John Doe",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
  },
  {
    key: "email", label: "Email Address", type: "email",
    autoComplete: "email", placeholder: "you@example.com",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    key: "phone", label: "Phone Number", type: "tel",
    autoComplete: "tel", placeholder: "+1 234 567 8900",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
    ),
  },
  {
    key: "password", label: "Password", type: "password",
    autoComplete: "new-password", placeholder: "Min. 8 characters",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
  },
  {
    key: "confirmPassword", label: "Confirm Password", type: "password",
    autoComplete: "new-password", placeholder: "••••••••",
    icon: (
      <svg className="w-4 h-4 text-[#009986]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
  },
];

const INITIAL_FORM = {
  fullName: "", email: "", phone: "", password: "", confirmPassword: "",
};

const validate = (form) => {
  const errors = {};
  if (!form.fullName.trim())          errors.fullName        = "Full name is required";
  if (form.fullName.trim().length > 50) errors.fullName      = "Name must be under 50 characters";
  if (!form.email || !form.email.includes("@")) errors.email = "Enter a valid email address";
  if (form.phone && form.phone.length > 20)     errors.phone = "Phone number is too long";
  if (form.password.length < 8)       errors.password        = "Password must be at least 8 characters";
  if (form.password !== form.confirmPassword)
    errors.confirmPassword = "Passwords do not match";
  return errors;
};

export const SignUp = () => {
  const { signUp, isLoading, error: authError } = useAuth();
  const navigate  = useNavigate();
  const formId    = useId();
  const [searchParams] = useSearchParams();


const [userType, setUserType] = useState(
  searchParams.get("role") === "Company" ? "Company" : "Candidate");
  const [formState,   setFormState]   = useState(INITIAL_FORM);
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitted,   setSubmitted]   = useState(false);

  const fieldIds = useMemo(() => ({
    fullName:        `${formId}-full-name`,
    email:           `${formId}-email`,
    phone:           `${formId}-phone`,
    password:        `${formId}-password`,
    confirmPassword: `${formId}-confirm-password`,
  }), [formId]);

  const handleChange = (field) => (e) => {
    setFormState((prev) => ({ ...prev, [field]: e.target.value }));
    if (fieldErrors[field]) setFieldErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitted(true);

    const errors = validate(formState);
    if (Object.keys(errors).length > 0) { setFieldErrors(errors); return; }

    try {
      await signUp({ ...formState, userType });
      // Redirect to history page after successful signup
      navigate("/sign-in");
    } catch {
      // authError from context handles display
    }
  };

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex flex-col">
      <PublicNavbar activePage="" />

      <main className="flex-1 flex items-center justify-center px-4 py-10">
        <section
          id="signup-form"
          aria-labelledby="signup-title"
          className="bg-white rounded-3xl shadow-md w-full max-w-md px-8 py-10"
        >
          <h1 id="signup-title" className="text-2xl sm:text-3xl font-bold text-[#494949] text-center mb-1">
            Create your account
          </h1>
          <p className="text-[#808080] text-sm text-center mb-6">
            Join the next generation of interview preparation
          </p>

          {authError && submitted && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 rounded-xl px-4 py-3 text-sm font-medium" role="alert">
              {authError}
            </div>
          )}

          {/* User type toggle */}
          <div role="tablist" aria-label="Account type" className="relative flex bg-[#ececec] rounded-xl p-1 mb-6">
            <div className={`absolute top-1 bottom-1 bg-white rounded-[10px] transition-all duration-200 ${
              userType === "Candidate" ? "left-1 right-1/2" : "left-1/2 right-1"
            }`} />
            {["Candidate", "Company"].map((type) => (
              <button
                key={type}
                type="button"
                role="tab"
                aria-selected={userType === type}
                onClick={() => setUserType(type)}
                className={`relative z-10 flex-1 py-1.5 text-base font-semibold rounded-[10px] transition-colors ${
                  userType === type ? "text-[#009986]" : "text-[#888]"
                }`}
              >
                {type}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
            {FIELD_DEFINITIONS.map((field) => (
              <div key={field.key} className="flex flex-col gap-1">
                <label
                  htmlFor={fieldIds[field.key]}
                  className="text-xs font-semibold text-[#808080] uppercase tracking-wider"
                >
                  {field.label}
                </label>
                <div className={`flex items-center gap-3 bg-[#f2f2f2] border rounded-xl px-3 h-11 focus-within:border-[#009986] transition-colors ${
                  fieldErrors[field.key] ? "border-red-400" : "border-[#d3d3d3]"
                }`}>
                  {field.icon}
                  <input
                    id={fieldIds[field.key]}
                    name={field.key}
                    type={field.type}
                    autoComplete={field.autoComplete}
                    placeholder={field.placeholder}
                    value={formState[field.key]}
                    onChange={handleChange(field.key)}
                    className="flex-1 bg-transparent text-sm text-[#494949] placeholder:text-[#b0b0b0] focus:outline-none"
                    aria-invalid={!!fieldErrors[field.key]}
                    aria-describedby={fieldErrors[field.key] ? `${fieldIds[field.key]}-error` : undefined}
                  />
                </div>
                {fieldErrors[field.key] && (
                  <span id={`${fieldIds[field.key]}-error`} className="text-xs text-red-500 font-medium" role="alert">
                    {fieldErrors[field.key]}
                  </span>
                )}
              </div>
            ))}

            <button
              type="submit"
              disabled={isLoading}
              className="mt-2 w-full bg-[#009986] text-white font-bold text-lg py-2.5 rounded-2xl hover:bg-[#007a6e] transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating account...
                </>
              ) : "Create Account"}
            </button>

            <div className="text-center text-[#d9d9d9] font-bold text-lg">or</div>

            <button
              type="button"
              onClick={() => navigate("/sign-in")}
              className="w-full border-2 border-[#009986] text-[#009986] font-bold text-lg py-2.5 rounded-2xl text-center hover:bg-[#e5e4e2] transition-colors"
            >
              Log in
            </button>
          </form>
        </section>
      </main>

      <footer className="py-6 text-center">
        <p className="text-[#888888] text-xs">
          &copy; {new Date().getFullYear()} Interview Me. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default SignUp;