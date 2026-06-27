import { useId, useState } from "react";
import { useNavigate } from "react-router-dom";
import searchIcon from "../../assets/search.svg";
import { useAuth } from "../../context/AuthContext";

/**
 * DashboardHeader
 * Top header bar used across all dashboard pages.
 * Includes search, user info, and logout button.
 *
 * Props:
 * - onMenuToggle (fn):     called when hamburger is clicked
 * - user         (object): { name, role, initials } — optional, falls back to localStorage
 * - showSearch   (bool):   whether to show the search bar, default true
 */

// ── Read user from localStorage as fallback ───────────────────────────────────
// Needed because SignInPage doesn't use AuthContext — it writes directly to localStorage.

const getLocalStorageUser = () => {
  const name   = localStorage.getItem("name") || "User";
  const role   = localStorage.getItem("role") || "USER";
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return {
    name,
    role:     role === "RECRUITER" ? "Recruiter Admin" : "Candidate",
    initials,
  };
};

const DashboardHeader = ({
  onMenuToggle,
  user,
  showSearch = true,
}) => {
  const searchId               = useId();
  const { logout }             = useAuth();
  const navigate               = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [loggingOut,   setLoggingOut]   = useState(false);

  // Use passed user prop, fall back to localStorage, then hardcoded default
  const displayUser = user || getLocalStorageUser();

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
      navigate("/sign-in");
    } catch {
      navigate("/sign-in");
    } finally {
      setLoggingOut(false);
    }
  };

  return (
    <header className="h-[73px] bg-white border-b border-gray-200 px-4 md:px-8 flex items-center justify-between shrink-0 relative">

      {/* Left: Hamburger + Search */}
      <div className="flex items-center gap-4 flex-1 max-w-md">

        {/* Mobile hamburger */}
        <button
          type="button"
          className="md:hidden text-[#566068] hover:text-[#009986] focus:outline-none"
          aria-label="Toggle navigation menu"
          onClick={onMenuToggle}
        >
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {/* Search */}
        {showSearch && (
          <form className="relative w-full hidden sm:block" role="search" aria-label="Search dashboard">
            <label htmlFor={searchId} className="sr-only">Search candidates, reports</label>
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <img className="w-4 h-4" src={searchIcon} alt="" aria-hidden="true" />
            </div>
            <input
              id={searchId}
              type="search"
              placeholder="Search candidates, reports ..etc"
              className="w-full h-[42px] bg-gray-100 rounded-full pl-11 pr-4 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#009986] border border-transparent transition-all"
            />
          </form>
        )}
      </div>

      {/* Right: User info + dropdown */}
      <div className="relative flex items-center gap-3">
        <div className="hidden sm:block text-right">
          <div className="text-sm font-semibold text-gray-800 leading-tight">{displayUser.name}</div>
          <div className="text-xs text-gray-500">{displayUser.role}</div>
        </div>

        {/* Avatar — click to open dropdown */}
        <button
          type="button"
          onClick={() => setDropdownOpen((prev) => !prev)}
          className="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center font-bold text-teal-700 select-none hover:bg-teal-200 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#009986]"
          aria-label="User menu"
          aria-expanded={dropdownOpen}
          aria-haspopup="menu"
        >
          {displayUser.initials}
        </button>

        {/* Dropdown */}
        {dropdownOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setDropdownOpen(false)}
              aria-hidden="true"
            />

            {/* Menu */}
            <div
              className="absolute right-0 top-full mt-2 w-48 bg-white rounded-2xl shadow-lg border border-gray-100 py-2 z-50"
              role="menu"
            >
              {/* User info */}
              <div className="px-4 py-2 border-b border-gray-100 mb-1">
                <p className="text-sm font-semibold text-gray-800 truncate">{displayUser.name}</p>
                <p className="text-xs text-gray-400 truncate">{displayUser.role}</p>
              </div>

              {/* Logout */}
              <button
                type="button"
                role="menuitem"
                onClick={handleLogout}
                disabled={loggingOut}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-red-500 hover:bg-red-50 transition-colors disabled:opacity-60"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                {loggingOut ? "Logging out..." : "Log out"}
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  );
};

export default DashboardHeader;