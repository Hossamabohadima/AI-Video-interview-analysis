// import { useState, useEffect, useMemo, useId } from "react";
import { useState, useEffect, useMemo } from "react";

import DashboardSidebar from "../../components/DashboardSidebar/DashboardSidebar";
import DashboardHeader  from "../../components/DashboardHeader/DashboardHeader";
import StatCard         from "../../components/UI/StatCard";
import ScoreBar         from "../../components/UI/ScoreBar";
import Pagination       from "../../components/UI/Pagination";

import useMobileMenu    from "../../hooks/useMobileMenu";
import usePagination    from "../../hooks/usePagination";
import { useAuth }      from "../../context/AuthContext";
import { getCandidatesByBatch } from "../../services/api";

import {
  enrichCandidates,
  calcBatchStats,
  calcModuleAverages,
  calcScoreDistribution,
} from "../../utils/calculations";

// ── CONSTANTS ─────────────────────────────────────────────────────────────────

const DEFAULT_THRESHOLD = 70;

const MODULE_LABELS = [
  "Language & Clarity",
  "Speech Fluency",
  "Vocal Expressiveness",
  "Visual Engagement",
  "Facial Positivity",
];

const TABLE_COLUMNS = [
  "#", "Candidate", "Overall",
  "Language", "Fluency", "Vocal", "Visual", "Facial", "Status",
];

// ── PAGE ──────────────────────────────────────────────────────────────────────

export const RecruiterReport = () => {
  const { user }                  = useAuth();
  const { isOpen, toggle, close } = useMobileMenu();
//   const searchId                  = useId();  
//   const searchId                  = useId();  

  const [rawCandidates,  setRawCandidates]  = useState([]);
  const [loading,        setLoading]        = useState(true);
  const [error,          setError]          = useState(null);
  const [threshold,      setThreshold]      = useState(DEFAULT_THRESHOLD);
  const [thresholdInput, setThresholdInput] = useState(String(DEFAULT_THRESHOLD));

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getCandidatesByBatch(1);
        setRawCandidates(data);
      } catch (err) {
        setError(err.message || "Failed to load report data");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // ── All derived data recalculates when threshold or data changes ──────────
  const candidates   = useMemo(() => enrichCandidates(rawCandidates, threshold),        [rawCandidates, threshold]);
  const stats        = useMemo(() => calcBatchStats(candidates),                         [candidates]);
  const moduleAvgs   = useMemo(() => calcModuleAverages(candidates, MODULE_LABELS),      [candidates]);
  const distribution = useMemo(() => calcScoreDistribution(candidates),                  [candidates]);
  const maxBucket    = Math.max(...distribution.map((b) => b.count), 1);

  const { paginated, currentPage, totalPages, hasNext, hasPrev, next, prev, goTo } =
    usePagination(candidates, 5);

  const applyThreshold = () => {
    const val = parseInt(thresholdInput, 10);
    if (!isNaN(val) && val >= 0 && val <= 100) {
      setThreshold(val);
    } else {
      setThresholdInput(String(threshold));
    }
  };

  const summaryCards = stats ? [
    { id: "total",   title: "Total Candidates", value: String(stats.total),       subtitle: "Uploaded in batch",            valueColor: "text-gray-900",   topBorder: true },
    { id: "passed",  title: "Passed Threshold", value: String(stats.passedCount), subtitle: `${stats.passRate}% pass rate`, valueColor: "text-gray-900",   topBorder: true },
    { id: "avg",     title: "Average Score",    value: `${stats.batchAvg}%`,      subtitle: "Batch average",                valueColor: "text-gray-900",   topBorder: true },
    { id: "top",     title: "Top Score",        value: `${stats.topScore}%`,      subtitle: stats.topName,                  valueColor: "text-[#009986]",  topBorder: true },
  ] : [];

  const headerUser = user
    ? { name: user.name, role: user.role, initials: user.initials }
    : { name: "Sarah Ahmed", role: "Recruiter Admin", initials: "SA" };

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex font-sans">
      <DashboardSidebar isOpen={isOpen} onClose={close} />

      <div className="flex-1 flex flex-col min-w-0">
        <DashboardHeader onMenuToggle={toggle} user={headerUser} />

        <main className="flex-1 p-4 md:p-8 space-y-6 overflow-y-auto max-w-7xl w-full mx-auto">

          {/* Batch header */}
          <section className="bg-white rounded-2xl px-6 py-4 flex items-center justify-between flex-wrap gap-4 shadow-sm border border-gray-100">
            <h1 className="text-lg font-semibold text-gray-900">
              Senior Frontend Engineer — Batch Report
            </h1>
            <button
              type="button"
              onClick={() => window.print()}
              className="flex items-center gap-2 h-9 px-4 rounded-full border border-gray-200 text-sm font-bold text-teal-600 hover:bg-teal-50 hover:border-teal-300 transition-all focus:outline-none"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              Export PDF
            </button>
          </section>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 rounded-2xl px-6 py-4 text-sm font-medium">
              {error}
            </div>
          )}

          {/* Threshold control */}
          <section className="bg-white rounded-2xl px-6 py-4 shadow-sm border border-gray-100 flex flex-wrap items-center gap-4" aria-label="Pass threshold setting">
            <div className="flex flex-col gap-0.5">
              <label htmlFor="threshold-input" className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                Pass Threshold
              </label>
              <p className="text-xs text-gray-400">Candidates at or above this score are marked PASS. All stats update instantly.</p>
            </div>
            <div className="flex items-center gap-3 ml-auto flex-wrap">
              <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 h-10 border border-gray-200 focus-within:border-[#009986] transition-colors">
                <input
                  id="threshold-input"
                  type="number"
                  min="0"
                  max="100"
                  value={thresholdInput}
                  onChange={(e) => setThresholdInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && applyThreshold()}
                  className="w-14 bg-transparent text-sm font-bold text-gray-700 focus:outline-none text-center"
                />
                <span className="text-sm font-bold text-gray-400">%</span>
              </div>
              <button type="button" onClick={applyThreshold}
                className="h-10 px-5 bg-[#009986] text-white text-sm font-bold rounded-xl hover:bg-[#007a6e] transition-colors focus:outline-none focus:ring-2 focus:ring-[#009986]">
                Apply
              </button>
              <span className="text-xs text-gray-400">
                Active: <span className="font-bold text-[#009986]">{threshold}%</span>
              </span>
            </div>
          </section>

          {/* Summary cards */}
          {loading ? (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="bg-white rounded-2xl p-5 h-[115px] animate-pulse" />
              ))}
            </div>
          ) : (
            <section className="grid grid-cols-2 lg:grid-cols-4 gap-4" aria-label="Batch summary statistics">
              {summaryCards.map((card) => (
                <StatCard key={card.id} title={card.title} value={card.value} subtitle={card.subtitle} valueColor={card.valueColor} topBorder={card.topBorder} />
              ))}
            </section>
          )}

          {/* Table + side panels */}
          <div className="flex flex-col xl:flex-row gap-6">

            {/* Candidate ranking table */}
            <section className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex-1 min-w-0" aria-labelledby="ranking-heading">
              <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between flex-wrap gap-2">
                <h2 id="ranking-heading" className="text-sm font-semibold text-gray-700">
                  All candidates ranked by overall score
                </h2>
                <div className="flex gap-4 text-xs font-semibold">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#009986] inline-block" />
                    Pass ≥ {threshold}%: <strong>{stats?.passedCount ?? 0}</strong>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
                    Fail: <strong>{stats?.failedCount ?? 0}</strong>
                  </span>
                </div>
              </div>

              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-8 space-y-4">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <div key={i} className="h-10 bg-gray-100 rounded-xl animate-pulse" />
                    ))}
                  </div>
                ) : (
                  <table className="w-full min-w-[700px] text-left border-collapse">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-200">
                        {TABLE_COLUMNS.map((col) => (
                          <th key={col} scope="col" className="py-3 px-4 text-xs font-semibold text-[#566068] text-center whitespace-nowrap first:text-left">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {paginated.map((c) => {
                        const pass       = c.status === "PASS";
                        const scoreColor = pass ? "text-[#009986]" : "text-gray-300";
                        const nameColor  = pass ? "text-gray-700"  : "text-gray-300";
                        return (
                          <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                            <td className={`py-3 px-4 text-xs font-semibold ${nameColor}`}>{c.rank}</td>
                            <td className={`py-3 px-4 text-xs font-semibold whitespace-nowrap ${nameColor}`}>{c.name}</td>
                            <td className={`py-3 px-4 text-xs font-bold text-center ${scoreColor}`}>{c.overall}%</td>
                            {c.scores.map((s, i) => (
                              <td key={i} className={`py-3 px-4 text-xs font-bold text-center ${scoreColor}`}>{s}%</td>
                            ))}
                            <td className="py-3 px-4 text-center">
                              <span className={`inline-flex items-center justify-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                                pass ? "bg-teal-50 text-[#009986]" : "bg-red-50 text-[#dc143c]"
                              }`}>
                                {c.status}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>

              {!loading && candidates.length > 0 && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  hasNext={hasNext}
                  hasPrev={hasPrev}
                  onNext={next}
                  onPrev={prev}
                  onGoTo={goTo}
                  summary={`Page ${currentPage} of ${totalPages} · ${candidates.length} candidates`}
                  label="Candidate pagination"
                />
              )}
            </section>

            {/* Side panels */}
            <div className="flex flex-row xl:flex-col gap-4 xl:w-56 shrink-0">

              {/* Score Distribution */}
              <aside className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex-1 xl:flex-none" aria-label="Score distribution">
                <h3 className="text-xs font-bold text-[#009986] text-center mb-1">Score Distribution</h3>
                <p className="text-[10px] text-gray-400 text-center mb-3">{candidates.length} candidates</p>
                <div className="flex items-end justify-between gap-1 h-20">
                  {distribution.map((bar) => {
                    const heightPct = Math.round((bar.count / maxBucket) * 100);
                    return (
                      <div key={bar.range} className="flex flex-col items-center gap-1 flex-1"
                        title={`${bar.range}: ${bar.count} candidate${bar.count !== 1 ? "s" : ""}`}>
                        <span className="text-[9px] font-bold text-gray-400">{bar.count}</span>
                        <div className="w-full rounded-t-sm bg-[#009986] transition-all duration-500"
                          style={{ height: `${Math.max(heightPct, bar.count > 0 ? 8 : 0)}%`, minHeight: bar.count > 0 ? "6px" : "0" }} />
                        <span className="text-[8px] text-gray-400 whitespace-nowrap">{bar.range}</span>
                      </div>
                    );
                  })}
                </div>
              </aside>

              {/* Pass / Fail */}
              <aside className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex-1 xl:flex-none" aria-label="Pass fail breakdown">
                <h3 className="text-xs font-bold text-[#009986] text-center mb-4">Pass / Fail</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs font-semibold mb-1">
                      <span className="text-gray-600">Pass</span>
                      <span className="text-[#009986]">{stats?.passedCount ?? 0} ({stats?.passRate ?? "0.0"}%)</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full bg-[#009986] rounded-full transition-all duration-500"
                        style={{ width: `${stats?.passRate ?? 0}%` }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs font-semibold mb-1">
                      <span className="text-gray-600">Fail</span>
                      <span className="text-red-400">{stats?.failedCount ?? 0} ({stats?.failRate ?? "0.0"}%)</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full bg-red-400 rounded-full transition-all duration-500"
                        style={{ width: `${stats?.failRate ?? 0}%` }} />
                    </div>
                  </div>
                </div>
              </aside>
            </div>
          </div>

          {/* Core Module Scores */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100" aria-labelledby="core-scores-heading">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-2">
              <h2 id="core-scores-heading" className="text-lg font-semibold text-[#009986]">
                5 Core Module Scores
              </h2>
              <span className="text-xs text-gray-400 font-semibold">
                Avg. across all {candidates.length} candidates
              </span>
            </div>
            <ul className="space-y-5">
              {moduleAvgs.map((mod) => (
                <li key={mod.label}>
                  <span className="text-sm font-semibold text-gray-800 block mb-1.5">{mod.label}</span>
                  <ScoreBar value={mod.value} />
                </li>
              ))}
            </ul>
            <div className="mt-6 pt-4 border-t border-gray-100 grid grid-cols-2 sm:grid-cols-5 gap-3">
              {moduleAvgs.map((mod) => (
                <div key={mod.label} className="bg-gray-50 rounded-xl p-3 text-center">
                  <div className="text-lg font-black text-[#009986]">{mod.value}%</div>
                  <div className="text-[10px] text-gray-400 font-semibold mt-0.5 leading-tight">{mod.label}</div>
                </div>
              ))}
            </div>
          </section>
        </main>

        <footer className="py-5 px-8 text-center shrink-0">
          <p className="text-xs text-gray-400">&copy; {new Date().getFullYear()} Interview Me. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default RecruiterReport;