import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import DashboardSidebar from "../../components/DashboardSidebar/DashboardSidebar";
import DashboardHeader  from "../../components/DashboardHeader/DashboardHeader";
import StatCard         from "../../components/UI/StatCard";
import Pagination       from "../../components/UI/Pagination";

import useMobileMenu    from "../../hooks/useMobileMenu";
import usePagination    from "../../hooks/usePagination";
import { useAuth }      from "../../context/AuthContext";
import { getDashboardStats, getBatches } from "../../services/api";

import people     from "../../assets/people.svg";
import statistics from "../../assets/statistics.svg";
import passed     from "../../assets/passed.svg";
import time       from "../../assets/time.svg";

const TABLE_HEADERS = [
  "Applied Role", "Batch Size", "Date",
  "Passed", "Avg. Score", "Top Score", "Action",
];

export const CandidateDashboard = () => {
  const { user }                  = useAuth();
  const { isOpen, toggle, close } = useMobileMenu();
  const navigate                  = useNavigate();

  const [stats,   setStats]   = useState(null);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashStats, batchList] = await Promise.all([
          getDashboardStats(),
          getBatches(),
        ]);
        setStats(dashStats);
        setBatches(batchList);
      } catch (err) {
        setError(err.message || "Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const { paginated, currentPage, totalPages, hasNext, hasPrev, next, prev, goTo } =
    usePagination(batches, 5);

  const statCards = stats ? [
    { id: "total-candidates",  title: "Total Candidates",   value: stats.totalCandidates.toLocaleString(), trend: "+12% this week", icon: <img className="w-7 h-7" src={people}     alt="" aria-hidden="true" /> },
    { id: "passed-threshold",  title: "Passed Threshold",   value: String(stats.passedThreshold),          trend: "+2% this week",  icon: <img className="w-7 h-7" src={passed}     alt="" aria-hidden="true" /> },
    { id: "avg-ai-match",      title: "Avg. AI Match Score",value: `${stats.avgAiMatchScore}%`,            trend: "+22% this week", icon: <img className="w-7 h-7" src={statistics} alt="" aria-hidden="true" /> },
    { id: "time-saved",        title: "Time Saved (Hrs)",   value: String(stats.timeSavedHrs),             trend: "+18% this week", icon: <img className="w-7 h-7" src={time}       alt="" aria-hidden="true" /> },
  ] : [];

  const headerUser = user
    ? { name: user.name, role: user.role, initials: user.initials }
    : { name: "Sarah Ahmed", role: "Recruiter Admin", initials: "SA" };

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex font-sans">
      <DashboardSidebar isOpen={isOpen} onClose={close} />

      <div className="flex-1 flex flex-col min-w-0">
        <DashboardHeader onMenuToggle={toggle} user={headerUser} />

        <main className="flex-1 p-4 md:p-8 space-y-8 overflow-y-auto max-w-7xl w-full mx-auto">

          <section aria-labelledby="welcome-heading">
            <h1 id="welcome-heading" className="text-2xl md:text-3xl font-bold text-[#009986]">
              Welcome back, {user?.name?.split(" ")[0] ?? "Sarah"} 👋
            </h1>
          </section>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 rounded-2xl px-6 py-4 text-sm font-medium">
              {error}
            </div>
          )}

          {/* Stat Cards */}
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="bg-white rounded-3xl p-5 h-[115px] animate-pulse" />
              ))}
            </div>
          ) : (
            <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6" aria-label="Overview statistics">
              {statCards.map((card) => (
                <StatCard key={card.id} title={card.title} value={card.value} trend={card.trend} icon={card.icon} />
              ))}
            </section>
          )}

          {/* Evaluations Table */}
          <section aria-labelledby="recent-evaluation-heading" className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100">
            <div className="p-6 border-b border-gray-100">
              <h2 id="recent-evaluation-heading" className="text-xl font-bold text-[#009986]">
                Recent Evaluations
              </h2>
            </div>

            <div className="w-full overflow-x-auto">
              {loading ? (
                <div className="p-8 space-y-4">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="h-10 bg-gray-100 rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : (
                <table className="w-full min-w-[800px] text-left border-collapse">
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
                    {paginated.map((row) => (
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
                        <td className="py-4 px-6 text-sm font-bold text-red-500 text-center">{row.topScore}</td>
                        <td className="py-4 px-6 text-center">
                          <button
                            type="button"
                            onClick={() => navigate("/recruiter-report")}
                            className="h-8 px-4 rounded-full border border-gray-200 bg-white text-sm font-medium text-teal-600 hover:bg-teal-50 hover:border-teal-300 transition-all focus:outline-none focus:ring-2 focus:ring-teal-500"
                            aria-label={`View report for ${row.role}`}
                          >
                            View Report
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {!loading && batches.length > 0 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                hasNext={hasNext}
                hasPrev={hasPrev}
                onNext={next}
                onPrev={prev}
                onGoTo={goTo}
                summary={`Page ${currentPage} of ${totalPages} · ${batches.length} batches total`}
                label="Evaluations pagination"
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

export default CandidateDashboard;