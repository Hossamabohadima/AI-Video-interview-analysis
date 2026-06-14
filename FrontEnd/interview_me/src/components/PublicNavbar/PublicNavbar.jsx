import { useState } from "react";
import { Link } from "react-router-dom";
import polygon1 from "../../assets/polygon.svg";

/**
 * PublicNavbar
 * Used on all public-facing pages (HomePage, SignUp).
 *
 * Props:
 * - activePage (string): matches a nav item label to highlight it
 */

const NAV_ITEMS = [
  { label: "Home",         href: "/"       },
  { label: "How it works", href: "how-it-works"    },
  { label: "Products",     href: "/", hasDropdown: true },
];

const PublicNavbar = ({ activePage = "" }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="w-full px-6 py-4 flex items-center justify-between relative">

      {/* Logo */}
      <Link
        to="/"
        aria-label="Interview me home"
        className="font-['Pacifico'] text-[#009986] text-2xl md:text-3xl whitespace-nowrap"
      >
        Interview me
      </Link>

      {/* Desktop Nav */}
      <nav className="hidden md:flex items-center gap-8" aria-label="Primary navigation">
        {NAV_ITEMS.map((item) => (
          <div key={item.label} className="relative flex flex items-center gap-1">
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
            {item.hasDropdown && (
              <img
                src={polygon1}
                alt=""
                className="w-2.5 h-2 mt-1"
                aria-hidden="true"
              />
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
          {NAV_ITEMS.map((item) => (
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
          ))}
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