import { useState, useEffect, useMemo, useId } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

import DashboardSidebar  from "../../components/DashboardSidebar/DashboardSidebar";
import DashboardHeader   from "../../components/DashboardHeader/DashboardHeader";
import ScoreBar          from "../../components/ui/ScoreBar";
import StatCard          from "../../components/ui/StatCard";
import Pagination        from "../../components/ui/Pagination";
import Spinner from "../../components/UI/Spinner";

import useMobileMenu     from "../../hooks/useMobileMenu";
import usePagination     from "../../hooks/usePagination";
import { useAuth }       from "../../context/AuthContext";
import { getMultipleVideoScores, getReports} from "../../services/api";

// ── CONSTANTS ─────────────────────────────────────────────────────────────────

const DEFAULT_THRESHOLD = 70;

const MODULE_LABELS = [
  { key: "fillers_score",     label: "Fillers"     },
  { key: "pause_rate_score",  label: "Pause Rate"  },
  { key: "emotion_score",     label: "Emotion"     },
  { key: "energy_score",      label: "Energy"      },
  { key: "eye_contact_score", label: "Eye Contact" },
  { key: "grammar_score",     label: "Grammar"     },
];

const TABLE_COLUMNS = ["#", "Candidate", "Overall", "Fillers", "Pause", "Emotion", "Energy", "Eye Contact", "Grammar", "Status"];

const SCORE_BUCKETS = ["0–20", "20–40", "40–60", "60–80", "80–100"];

// ── PURE CALCULATIONS ─────────────────────────────────────────────────────────

const avg = (arr) => arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : 0;

const enrichCandidates = (rawScores, videoNames, threshold) =>
  rawScores
    .map((s, i) => ({
      id:      s.video_id,
      name:    videoNames[i] || `Candidate ${i + 1}`,
      overall: Math.round((s.total_score || 0) * 100),
      scores:  MODULE_LABELS.map((m) => Math.round((s[m.key] || 0) * 100)),
      status:  Math.round((s.total_score || 0) * 100) >= threshold ? "PASS" : "FAIL",
    }))
    .sort((a, b) => b.overall - a.overall)
    .map((c, i) => ({ ...c, rank: i + 1 }));

const calcDistribution = (candidates) => {
  const buckets = [0, 0, 0, 0, 0];
  candidates.forEach(({ overall }) => {
    const idx = Math.min(Math.floor(overall / 20), 4);
    buckets[idx]++;
  });
  return SCORE_BUCKETS.map((range, i) => ({ range, count: buckets[i] }));
};

// ── PAGE ──────────────────────────────────────────────────────────────────────

export const RecruiterReport = () => {
  const { user }                  = useAuth();
  const { isOpen, toggle, close } = useMobileMenu();
  const [searchParams]            = useSearchParams();
  const navigate                  = useNavigate();

  const idsParam = searchParams.get("ids") || "";
  const videoIds = idsParam ? idsParam.split(",").map(Number).filter(Boolean) : [];

  const [rawScores,       setRawScores]       = useState([]);
  const [videoNames,      setVideoNames]       = useState([]);
  const [loading,         setLoading]          = useState(true);
  const [error,           setError]            = useState(null);
  const [threshold,       setThreshold]        = useState(DEFAULT_THRESHOLD);
  const [thresholdInput,  setThresholdInput]   = useState(String(DEFAULT_THRESHOLD));
  const [thresholdSaved,  setThresholdSaved]   = useState(false);

  useEffect(() => {
    if (videoIds.length === 0) {
      setError("No videos selected. Go back to history and click View Report.");
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        const scores = await getMultipleVideoScores(videoIds);
        const { reports } = await getReports();
        const nameMap = {};
        if (reports) {
          reports.forEach((r) => {
            const cleanName = r.videoname
              .replace(/_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.*$/i, "")
              .replace(/_video$/, "")
              .trim();
            nameMap[r.videoid] = cleanName;
          });
        }
        const names = videoIds.map((id) => nameMap[id] || `Candidate ${id}`);
        setRawScores(scores);
        setVideoNames(names);
      } catch (err) {
        setError(err.message || "Failed to load report data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [idsParam]);

  const candidates   = useMemo(() => enrichCandidates(rawScores, videoNames, threshold), [rawScores, videoNames, threshold]);
  const distribution = useMemo(() => calcDistribution(candidates), [candidates]);
  const maxBucket    = Math.max(...distribution.map((b) => b.count), 1);

  const passed       = candidates.filter((c) => c.status === "PASS");
  const failed       = candidates.filter((c) => c.status === "FAIL");
  const allScores    = candidates.map((c) => c.overall);
  const topCandidate = candidates[0];
  const batchAvg     = avg(allScores);
  const passRate     = candidates.length ? ((passed.length / candidates.length) * 100).toFixed(1) : "0.0";
  const failRate     = candidates.length ? (100 - parseFloat(passRate)).toFixed(1) : "100.0";

  const moduleAvgs = MODULE_LABELS.map((mod, i) => ({
    label: mod.label,
    value: avg(candidates.map((c) => c.scores[i])),
  }));

  const { paginated, currentPage, totalPages, hasNext, hasPrev, next, prev, goTo } =
    usePagination(candidates, 6);

  const applyThreshold = () => {
    const val = parseInt(thresholdInput, 10);
    if (isNaN(val) || val < 0 || val > 100) { setThresholdInput(String(threshold)); return; }
    setThreshold(val);
    setThresholdSaved(true);
    setTimeout(() => setThresholdSaved(false), 2000);
  };

  const summaryCards = [
    { id: "total",  title: "Total Candidates", value: String(candidates.length), subtitle: "In this batch",           valueColor: "text-gray-900",  topBorder: true },
    { id: "passed", title: "Passed Threshold", value: String(passed.length),     subtitle: `${passRate}% pass rate`, valueColor: "text-gray-900",  topBorder: true },
    { id: "avg",    title: "Average Score",    value: `${batchAvg}%`,            subtitle: "Batch average",          valueColor: "text-gray-900",  topBorder: true },
    { id: "top",    title: "Top Score",        value: topCandidate ? `${topCandidate.overall}%` : "—", subtitle: topCandidate?.name || "—", valueColor: "text-[#009986]", topBorder: true },
  ];

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex font-sans">
      <DashboardSidebar isOpen={isOpen} onClose={close} />

      <div className="flex-1 flex flex-col min-w-0">
        <DashboardHeader onMenuToggle={toggle} />

        <main className="flex-1 p-4 md:p-8 space-y-6 overflow-y-auto max-w-7xl w-full mx-auto relative">

          {/* Loading overlay — covers only main content */}
          {loading && (
            <Spinner
              message="Loading batch report..."
              submessage="Fetching scores for all candidates"
            />
          )}

          {/* Report header */}
          <section className="bg-white rounded-2xl px-6 py-4 flex items-center justify-between flex-wrap gap-4 shadow-sm border border-gray-100">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Batch Report</h1>
              <p className="text-xs text-gray-400 mt-0.5">{candidates.length} candidates · {videoIds.length} videos</p>
            </div>
            <div className="flex items-center gap-3">
              <button type="button" onClick={() => navigate("/recruiter-history")}
                className="h-9 px-4 rounded-full border border-gray-200 text-sm font-medium text-gray-500 hover:bg-gray-50 transition-all">
                ← Back to History
              </button>
              <button type="button" onClick={() => window.print()}
                className="flex items-center gap-2 h-9 px-4 rounded-full border border-gray-200 text-sm font-bold text-teal-600 hover:bg-teal-50 hover:border-teal-300 transition-all">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                </svg>
                Export PDF
              </button>
            </div>
          </section>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 rounded-2xl px-6 py-4 text-sm font-medium" role="alert">
              {error}
            </div>
          )}

          {videoIds.length === 0 && !loading && (
            <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-gray-100">
              <p className="text-gray-400 text-sm">No batch selected.</p>
              <button onClick={() => navigate("/recruiter-history")}
                className="text-[#009986] font-semibold text-sm mt-2 inline-block hover:underline">
                ← Go back to History
              </button>
            </div>
          )}

          {videoIds.length > 0 && (
            <>
              {/* Threshold control */}
              <section className="bg-white rounded-2xl px-6 py-4 shadow-sm border border-gray-100 flex flex-wrap items-center gap-4">
                <div className="flex flex-col gap-0.5">
                  <label htmlFor="threshold-input" className="text-xs font-bold text-gray-500 uppercase tracking-wider">Pass Threshold</label>
                  <p className="text-xs text-gray-400">Candidates at or above this score are marked PASS.</p>
                </div>
                <div className="flex items-center gap-3 ml-auto flex-wrap">
                  <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 h-10 border border-gray-200 focus-within:border-[#009986] transition-colors">
                    <input
                      id="threshold-input"
                      type="number" min="0" max="100"
                      value={thresholdInput}
                      onChange={(e) => setThresholdInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && applyThreshold()}
                      className="w-14 bg-transparent text-sm font-bold text-gray-700 focus:outline-none text-center"
                    />
                    <span className="text-sm font-bold text-gray-400">%</span>
                  </div>
                  <button type="button" onClick={applyThreshold}
                    className="h-10 px-5 bg-[#009986] text-white text-sm font-bold rounded-xl hover:bg-[#007a6e] transition-colors">
                    Apply
                  </button>
                  {thresholdSaved && <span className="text-xs text-[#009986] font-semibold">✓ Saved</span>}
                  <span className="text-xs text-gray-400">Active: <span className="font-bold text-[#009986]">{threshold}%</span></span>
                </div>
              </section>

              {/* Summary cards */}
              <section className="grid grid-cols-2 lg:grid-cols-4 gap-4" aria-label="Batch summary">
                {summaryCards.map((card) => (
                  <StatCard key={card.id} title={card.title} value={card.value} subtitle={card.subtitle} valueColor={card.valueColor} topBorder={card.topBorder} />
                ))}
              </section>

              {/* Candidate ranking table + side panels */}
              <div className="flex flex-col xl:flex-row gap-6">

                {/* Ranking table */}
                <section className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex-1 min-w-0" aria-labelledby="ranking-heading">
                  <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between flex-wrap gap-2">
                    <h2 id="ranking-heading" className="text-sm font-semibold text-gray-700">
                      All candidates ranked by overall score
                    </h2>
                    <div className="flex gap-4 text-xs font-semibold">
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-[#009986] inline-block" />
                        Pass ≥ {threshold}%: <strong>{passed.length}</strong>
                      </span>
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
                        Fail: <strong>{failed.length}</strong>
                      </span>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[800px] text-left border-collapse">
                      <thead>
                        <tr className="bg-gray-50 border-b border-gray-200">
                          {TABLE_COLUMNS.map((col) => (
                            <th key={col} scope="col" className="py-3 px-3 text-xs font-semibold text-[#566068] text-center whitespace-nowrap first:text-left">
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
                              <td className={`py-3 px-3 text-xs font-semibold ${nameColor}`}>{c.rank}</td>
                              <td className={`py-3 px-3 text-xs font-semibold whitespace-nowrap ${nameColor}`}>{c.name}</td>
                              <td className={`py-3 px-3 text-xs font-bold text-center ${scoreColor}`}>{c.overall}%</td>
                              {c.scores.map((s, i) => (
                                <td key={i} className={`py-3 px-3 text-xs font-bold text-center ${scoreColor}`}>{s}%</td>
                              ))}
                              <td className="py-3 px-3 text-center">
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
                  </div>

                  {candidates.length > 0 && (
                    <Pagination
                      currentPage={currentPage} totalPages={totalPages}
                      hasNext={hasNext} hasPrev={hasPrev}
                      onNext={next} onPrev={prev} onGoTo={goTo}
                      summary={`Page ${currentPage} of ${totalPages} · ${candidates.length} candidates`}
                      label="Candidate pagination"
                    />
                  )}
                </section>

                {/* Side panels */}
                <div className="flex flex-row xl:flex-col gap-4 xl:w-56 shrink-0">

                  {/* Score Distribution */}
                  <aside className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex-1 xl:flex-none">
                    <h3 className="text-xs font-bold text-[#009986] text-center mb-1">Score Distribution</h3>
                    <p className="text-[10px] text-gray-400 text-center mb-3">{candidates.length} candidates</p>
                      <div className="flex items-end justify-between gap-1 h-28">
                        {distribution.map((bar) => {
                          const heightPx = Math.round((bar.count / candidates.length) * 80);
                          return (
                            <div key={bar.range} className="flex flex-col items-center gap-1 flex-1" title={`${bar.range}: ${bar.count}`}>
                              <span className="text-[9px] font-bold text-gray-400">
                                {bar.count > 0 ? `${Math.round((bar.count / candidates.length) * 100)}%` : "0"}
                              </span>
                              <div
                                className="w-full rounded-t-sm bg-[#009986] transition-all duration-500"
                                style={{ height: bar.count > 0 ? `${Math.max(heightPx, 8)}px` : "0px" }}
                              />
                              <span className="text-[8px] text-gray-400 whitespace-nowrap">{bar.range}</span>
                            </div>
                          );
                        })}
                      </div>
                  </aside>

                  {/* Pass / Fail */}
                  <aside className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex-1 xl:flex-none">
                    <h3 className="text-xs font-bold text-[#009986] text-center mb-4">Pass / Fail</h3>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-xs font-semibold mb-1">
                          <span className="text-gray-600">Pass</span>
                          <span className="text-[#009986]">{passed.length} ({passRate}%)</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className="h-full bg-[#009986] rounded-full transition-all duration-500" style={{ width: `${passRate}%` }} />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-xs font-semibold mb-1">
                          <span className="text-gray-600">Fail</span>
                          <span className="text-red-400">{failed.length} ({failRate}%)</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className="h-full bg-red-400 rounded-full transition-all duration-500" style={{ width: `${failRate}%` }} />
                        </div>
                      </div>
                    </div>
                  </aside>
                </div>
              </div>

              {/* Core Module Scores */}
              <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100" aria-labelledby="core-scores-heading">
                <div className="flex items-center justify-between mb-6 flex-wrap gap-2">
                  <h2 id="core-scores-heading" className="text-lg font-semibold text-[#009986]">6 Core Module Scores</h2>
                  <span className="text-xs text-gray-400 font-semibold">Avg. across all {candidates.length} candidates</span>
                </div>
                <ul className="space-y-5">
                  {moduleAvgs.map((mod) => (
                    <li key={mod.label}>
                      <span className="text-sm font-semibold text-gray-800 block mb-1.5">{mod.label}</span>
                      <ScoreBar value={mod.value} />
                    </li>
                  ))}
                </ul>
                <div className="mt-6 pt-4 border-t border-gray-100 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                  {moduleAvgs.map((mod) => (
                    <div key={mod.label} className="bg-gray-50 rounded-xl p-3 text-center">
                      <div className="text-lg font-black text-[#009986]">{mod.value}%</div>
                      <div className="text-[10px] text-gray-400 font-semibold mt-0.5 leading-tight">{mod.label}</div>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </main>

        <footer className="py-5 px-8 text-center shrink-0">
          <p className="text-xs text-gray-400">&copy; {new Date().getFullYear()} Interview Me. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default RecruiterReport;