import { useId } from "react";
import searchIcon from "../../assets/search.svg";

/**
 * DashboardHeader
 * Top header bar used across all dashboard pages.
 *
 * Props:
 * - onMenuToggle (fn):     called when hamburger is clicked
 * - user         (object): { name, role, initials }
 * - showSearch   (bool):   whether to show the search bar, default true
 */

const DashboardHeader = ({
  onMenuToggle,
  user = { name: "Sarah Ahmed", role: "Recruiter Admin", initials: "SA" },
  showSearch = true,
}) => {
  const searchId = useId();

  return (
    <header className="h-[73px] bg-white border-b border-gray-200 px-4 md:px-8 flex items-center justify-between shrink-0">

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
            <label htmlFor={searchId} className="sr-only">
              Search candidates, reports
            </label>
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

      {/* Right: User info */}
      <div className="flex items-center gap-3" aria-label="Current user">
        <div className="hidden sm:block text-right">
          <div className="text-sm font-semibold text-gray-800 leading-tight">
            {user.name}
          </div>
          <div className="text-xs text-gray-500">{user.role}</div>
        </div>

        {/* Avatar */}
        <div
          className="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center font-bold text-teal-700 select-none shrink-0"
          aria-hidden="true"
        >
          {user.initials}
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;