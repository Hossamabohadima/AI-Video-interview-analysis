import { Link, useLocation } from "react-router-dom";
import uploadIcon  from "../../assets/upload.svg";
import historyIcon from "../../assets/history.svg";

/**
 * DashboardSidebar
 * Left sidebar used across all dashboard pages.
 * Active item is auto-detected from the current URL via useLocation.
 *
 * Props:
 * - isOpen  (bool): whether mobile sidebar is open
 * - onClose (fn):   called when close button or backdrop is clicked
 */

const NAV_ITEMS = [
  { id: "analyze-interview", label: "Analyze Interview", href: "/process-video", icon: uploadIcon  },
  { id: "history",           label: "History",           href: "/recruiter-history", icon: historyIcon },
];

const DashboardSidebar = ({ isOpen, onClose }) => {
  const { pathname } = useLocation();

  return (
    <>
      {/* Sidebar panel */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:flex shrink-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Dashboard navigation"
      >
        {/* Logo */}
        <div className="h-[73px] border-b border-gray-200 flex items-center justify-between px-6 shrink-0">
          <Link
            to="/"
            className="font-['Pacifico'] text-[#009986] text-3xl whitespace-nowrap"
            aria-label="Interview me home"
          >
            Interview me
          </Link>

          {/* Close button — mobile only */}
          <button
            type="button"
            className="md:hidden text-gray-500 hover:text-gray-700 focus:outline-none"
            onClick={onClose}
            aria-label="Close menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Nav items */}
        <nav className="p-4 space-y-1 flex-1 overflow-y-auto" aria-label="Primary">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href ||
              (item.href === "/recruiter-history" && pathname === "/recruiter-report");
            return (
              <Link
                key={item.id}
                to={item.href}
                aria-current={isActive ? "page" : undefined}
                onClick={onClose}
                className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all font-semibold text-base focus:outline-none focus-visible:ring-2 focus-visible:ring-[#009986] ${
                  isActive
                    ? "bg-teal-50 text-[#009986]"
                    : "text-gray-600 hover:bg-gray-50 hover:text-[#009986]"
                }`}
              >
                <img src={item.icon} className="w-5 h-5 shrink-0" alt="" aria-hidden="true" />
                <span className="whitespace-nowrap">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
    </>
  );
};

export default DashboardSidebar;