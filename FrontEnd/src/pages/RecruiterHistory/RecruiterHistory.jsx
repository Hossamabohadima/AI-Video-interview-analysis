import { useState, useEffect, useMemo, useId } from "react";

import DashboardSidebar from "../../components/DashboardSidebar/DashboardSidebar";
import DashboardHeader  from "../../components/DashboardHeader/DashboardHeader";
import Pagination       from "../../components/UI/Pagination";

import useMobileMenu    from "../../hooks/useMobileMenu";
import usePagination    from "../../hooks/usePagination";
import { useAuth }      from "../../context/AuthContext";
import { getBatches }   from "../../services/api";

const TABLE_HEADERS = [
  "Applied Role", "Batch Size", "Date",
  "Passed", "Avg. Score", "Top Score", "Action",
];

const SortIcon = () => (
  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9M3 12h5m8 0l4-4m0 0l4 4m-4-4v12" />
  </svg>
);

const sortBatches = (batches, sortBy) => {
  const copy = [...batches];
  switch (sortBy) {
    case "newest":     return copy.sort((a, b) => new Date(b.date.replace(/\//g, "-")) - new Date(a.date.replace(/\//g, "-")));
    case "oldest":     return copy.sort((a, b) => new Date(a.date.replace(/\//g, "-")) - new Date(b.date.replace(/\//g, "-")));
    case "role":       return copy.sort((a, b) => a.role.localeCompare(b.role));
    case "score-high": return copy.sort((a, b) => b.avgScore - a.avgScore);
    case "score-low":  return copy.sort((a, b) => a.avgScore - b.avgScore);
    default:           return copy;
  }
};

export const RecruiterHistory = () => {
  const { user }                  = useAuth();
  const { isOpen, toggle, close } = useMobileMenu();
  const innerSearchId             = useId();
  const sortSelectorId            = useId();

  const [batches,    setBatches]    = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const [roleSearch, setRoleSearch] = useState("");
  const [sortBy,     setSortBy]     = useState("default");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getBatches();
        setBatches(data);
      } catch (err) {
        setError(err.message || "Failed to load history");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Filter → Sort → Paginate
  const filtered = useMemo(() => {
    const q = roleSearch.trim().toLowerCase();
    return q ? batches.filter((b) => b.role.toLowerCase().includes(q)) : batches;
  }, [batches, roleSearch]);

  const sorted = useMemo(() => sortBatches(filtered, sortBy), [filtered, sortBy]);

  const { paginated, currentPage, totalPages, hasNext, hasPrev, next, prev, goTo, resetPage } =
    usePagination(sorted, 5);

  const handleRoleSearch = (val) => { setRoleSearch(val); resetPage(); };
  const handleSort       = (val) => { setSortBy(val);     resetPage(); };

  const headerUser = user
    ? { name: user.name, role: user.role, initials: user.initials }
    : { name: "Sarah Ahmed", role: "Recruiter Admin", initials: "SA" };

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex font-sans">
      <DashboardSidebar isOpen={isOpen} onClose={close} />

      <div className="flex-1 flex flex-col min-w-0">
        <DashboardHeader onMenuToggle={toggle} user={headerUser} />

        <main className="flex-1 p-4 md:p-8 space-y-6 overflow-y-auto max-w-7xl w-full mx-auto">

          <section aria-labelledby="history-heading">
            <h1 id="history-heading" className="text-2xl md:text-3xl font-bold text-[#009986]">
              Reports History
            </h1>
          </section>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 rounded-2xl px-6 py-4 text-sm font-medium">
              {error}
            </div>
          )}

          <section className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100 flex flex-col" aria-label="Reports list">

            {/* Filter toolbar */}
            <div className="p-4 md:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <form className="relative w-full sm:max-w-xs" role="search" aria-label="Search by role">
                <label htmlFor={innerSearchId} className="sr-only">Search by Role Name</label>
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  id={innerSearchId}
                  type="search"
                  value={roleSearch}
                  onChange={(e) => handleRoleSearch(e.target.value)}
                  placeholder="Search by Role Name"
                  className="w-full h-[37px] bg-gray-50 rounded-xl pl-10 pr-4 text-xs border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#009986] focus:border-[#009986]"
                />
              </form>

              <div className="relative inline-flex items-center gap-2 bg-white border border-gray-200 rounded-lg h-[37px] px-3 hover:border-gray-300 transition-colors self-end sm:self-auto">
                <SortIcon />
                <label htmlFor={sortSelectorId} className="sr-only">Sort reports</label>
                <select
                  id={sortSelectorId}
                  value={sortBy}
                  onChange={(e) => handleSort(e.target.value)}
                  className="bg-transparent text-sm font-medium text-gray-500 cursor-pointer focus:outline-none pr-1"
                >
                  <option value="default">Sort by</option>
                  <option value="newest">Newest</option>
                  <option value="oldest">Oldest</option>
                  <option value="role">Role (A–Z)</option>
                  <option value="score-high">Score (High–Low)</option>
                  <option value="score-low">Score (Low–High)</option>
                </select>
              </div>
            </div>

            {/* Table */}
            <div className="w-full overflow-x-auto">
              {loading ? (
                <div className="p-8 space-y-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="h-10 bg-gray-100 rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : (
                <table className="w-full min-w-[850px] text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200">
                      {TABLE_HEADERS.map((h) => (
                        <th key={h} scope="col" className="py-3.5 px-6 font-semibold text-sm text-[#566068] text-center whitespace-nowrap first:text-left">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {paginated.length > 0 ? paginated.map((row) => (
                      <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-6 font-medium text-sm text-gray-900">{row.role}</td>
                        <td className="py-4 px-6 text-sm text-gray-600 text-center">{row.batchSize}</td>
                        <td className="py-4 px-6 text-sm text-gray-600 text-center">
                          <time dateTime={row.date.replace(/\//g, "-")}>{row.date}</time>
                        </td>
                        <td className="py-4 px-6 text-sm text-gray-600 text-center">{row.passed}</td>
                        <td className="py-4 px-6 text-sm text-center">
                          <div className="flex items-center justify-center gap-3">
                            <span className="min-w-[32px] font-medium">{row.avgScore}%</span>
                            <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden" aria-hidden="true">
                              <div className="h-full bg-[#009986] rounded-full transition-all duration-500" style={{ width: `${row.avgScore}%` }} />
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-6 text-sm font-bold text-center text-[#33b278]">{row.topScore}</td>
                        <td className="py-4 px-6 text-center">
                          <button
                            type="button"
                            className="h-8 px-4 rounded-full border border-gray-200 bg-white text-sm font-medium text-teal-600 hover:bg-teal-50 hover:border-teal-300 transition-all focus:outline-none focus:ring-2 focus:ring-teal-500"
                            aria-label={`View report for ${row.role}`}
                          >
                            View Report
                          </button>
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan={7} className="py-12 text-center text-gray-400 text-sm">
                          No reports found matching &quot;{roleSearch}&quot;
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>

            {!loading && sorted.length > 0 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                hasNext={hasNext}
                hasPrev={hasPrev}
                onNext={next}
                onPrev={prev}
                onGoTo={goTo}
                summary={`Page ${currentPage} of ${totalPages} · ${sorted.length} result${sorted.length !== 1 ? "s" : ""}`}
                label="Reports pagination"
              />
            )}
          </section>
        </main>

        <footer className="py-5 px-8 text-center shrink-0">
          <p className="text-xs text-gray-400">&copy; {new Date().getFullYear()} Interview Me. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default RecruiterHistory;