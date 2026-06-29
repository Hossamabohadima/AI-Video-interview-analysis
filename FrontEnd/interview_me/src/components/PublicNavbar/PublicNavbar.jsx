import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import polygon1 from "../../assets/polygon.svg";
import uploadIcon from "../../assets/upload.svg";
import historyIcon from "../../assets/history.svg";

/**
 * PublicNavbar
 * Used on all public-facing pages (HomePage, SignUp).
 *
 * Props:
 * - activePage (string): matches a nav item label to highlight it
 */

const DROPDOWN_ITEMS = [
  {
    label: "Analyze my interview",
    href:  "/sign-in",
    icon:  uploadIcon,
  },
  {
    label: "View my report",
    href:  "/sign-in",
    icon:  historyIcon,
  },
];

const NAV_ITEMS = [
  { label: "Home",         href: "/"            },
  { label: "How it works", href: "/how-it-works" },
  { label: "Products",     href: "#",  hasDropdown: true },
];

const PublicNavbar = ({ activePage = "" }) => {
  const [mobileMenuOpen,   setMobileMenuOpen]   = useState(false);
  const [dropdownOpen,     setDropdownOpen]     = useState(false);
  const dropdownRef = useRef(null);
  const navigate    = useNavigate();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="w-full px-6 py-4 flex items-center justify-between relative z-50">

      {/* Logo */}
      <span
        to="/"
        aria-label="Interview me home"
        className="font-['Pacifico'] text-[#009986] text-2xl md:text-3xl whitespace-nowrap"
      >
        Interview me
      </span>

      {/* Desktop Nav */}
      <nav className="hidden md:flex items-center gap-8" aria-label="Primary navigation">
        {NAV_ITEMS.map((item) => (
          <div key={item.label} className="relative" ref={item.hasDropdown ? dropdownRef : null}>
            {item.hasDropdown ? (
              <>
                {/* Products button */}
                <button
                  type="button"
                  onClick={() => setDropdownOpen((prev) => !prev)}
                  onMouseEnter={() => setDropdownOpen(true)}
                  className={`flex flex-row gap-1 items-center font-bold text-lg transition-colors ${
                    activePage === item.label
                      ? "text-[#009986]"
                      : "text-[#566068] hover:text-[#009986]"
                  }`}
                  aria-expanded={dropdownOpen}
                  aria-haspopup="menu"
                >
                  {item.label}
                  <img
                    src={polygon1}
                    alt=""
                    className={`w-2.5 h-2  mt-1 transition-transform duration-200 ${dropdownOpen ? "rotate-180" : ""}`}
                    aria-hidden="true"
                  />
                </button>

                {/* Dropdown menu */}
                {dropdownOpen && (
                  <div
                    className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-56 bg-white rounded-2xl shadow-lg border border-gray-100 py-2 z-50"
                    role="menu"
                    onMouseLeave={() => setDropdownOpen(false)}
                  >
                    {/* Triangle pointer */}
                    <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-2 overflow-hidden">
                      <div className="w-3 h-3 bg-white border-l border-t border-gray-100 rotate-45 translate-y-1 mx-auto" />
                    </div>

                    {DROPDOWN_ITEMS.map((dItem) => (
                      <Link
                        key={dItem.label}
                        to={dItem.href}
                        role="menuitem"
                        onClick={() => setDropdownOpen(false)}
                        className="flex items-center gap-3 px-5 py-3 text-[#009986] font-semibold text-sm hover:bg-teal-50 transition-colors"
                      >
                        <img src={dItem.icon} className="w-5 h-5" alt="" aria-hidden="true" />
                        {dItem.label}
                      </Link>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <Link
                to={item.href}
                aria-current={activePage === item.label ? "page" : undefined}
                className={`font-bold text-lg transition-colors ${
                  activePage === item.label
                    ? "text-[#009986]"
                    : "text-[#566068] hover:text-[#009986]"
                }`}
              >
                {item.label}
              </Link>
            )}
          </div>
        ))}

        <Link
          to="/signup"
          className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl hover:bg-[#007a6e] transition-colors"
        >
          Sign up
        </Link>
      </nav>

      {/* Mobile Hamburger */}
      <button
        type="button"
        className="md:hidden text-[#566068] focus:outline-none"
        aria-label="Toggle menu"
        aria-expanded={mobileMenuOpen}
        onClick={() => setMobileMenuOpen((prev) => !prev)}
      >
        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {mobileMenuOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-white shadow-md px-6 py-4 flex flex-col gap-4 z-50">
          {NAV_ITEMS.map((item) =>
            item.hasDropdown ? (
              <div key={item.label}>
                <p className="font-semibold text-lg text-[#566068] mb-2">{item.label}</p>
                {DROPDOWN_ITEMS.map((dItem) => (
                  <Link
                    key={dItem.label}
                    to={dItem.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-3 pl-4 py-2 text-[#009986] font-semibold text-sm"
                  >
                    <img src={dItem.icon} className="w-4 h-4" alt="" aria-hidden="true" />
                    {dItem.label}
                  </Link>
                ))}
              </div>
            ) : (
              <Link
                key={item.label}
                to={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`font-semibold text-lg ${
                  activePage === item.label ? "text-[#009986]" : "text-[#566068]"
                }`}
              >
                {item.label}
              </Link>
            )
          )}
          <Link
            to="/signup"
            onClick={() => setMobileMenuOpen(false)}
            className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl w-fit hover:bg-[#007a6e] transition-colors"
          >
            Sign up
          </Link>
        </div>
      )}
    </header>
  );
};

export default PublicNavbar;