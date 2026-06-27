import { useEffect, useMemo, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import Spinner from "../components/UI/Spinner";


function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDuration(seconds) {
  if (seconds == null || Number.isNaN(seconds)) return "00:00";

  const totalSeconds = Math.floor(seconds);
  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;

  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function ProgressRow({ label, value }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-12 text-[9px] text-[#9CA3AF]">{label}</div>
      <div className="h-[3px] w-[62px] overflow-hidden rounded-full bg-[#DDEDEA]">
        <div
          className="h-full rounded-full bg-[#12B3A6]"
          style={{ width: `${value}%` }}
        />
      </div>
      <div className="w-8 text-[9px] font-medium text-[#12B3A6]">{value}%</div>
    </div>
  );
}

function SessionCard({ session }) {
  const faded = session.first;

  return (
    <div
      className={`flex items-center gap-4 rounded-[16px] border border-[#ECECEC] bg-white px-4 py-3 shadow-[0_2px_8px_rgba(0,0,0,0.03)] ${
        faded ? "opacity-80" : ""
      }`}
    >
      <div
        className={`flex h-8 w-8 items-center justify-center rounded-full text-[11px] font-bold ${
          session.latest
            ? "bg-[#0FA99D] text-white"
            : "bg-[#E6FAF7] text-[#0FA99D]"
        }`}
      >
        {session.sessionNumber}
      </div>

      <div className="min-w-[240px] flex-1">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <span className="text-[12px] font-bold text-[#1F2937]">
            Session {session.sessionNumber}
          </span>

          {session.latest && (
            <span className="rounded-md bg-[#0FA99D] px-1.5 py-0.5 text-[8px] font-bold text-white">
              Latest
            </span>
          )}

          {session.best && (
            <span className="rounded-md bg-[#FFF4D9] px-1.5 py-0.5 text-[8px] font-bold text-[#B78103]">
              🏆 Best score
            </span>
          )}

          {session.first && (
            <span className="rounded-md bg-[#F3F4F6] px-1.5 py-0.5 text-[8px] font-bold text-[#9CA3AF]">
              First session
            </span>
          )}

          <span
            className={`rounded-md px-1.5 py-0.5 text-[8px] font-bold ${
              session.status === "DONE"
                ? "bg-[#ECFDF3] text-[#16A34A]"
                : "bg-[#FEF3C7] text-[#B45309]"
            }`}
          >
            {session.status}
          </span>
        </div>

        <div className="flex flex-wrap gap-3 text-[10px] text-[#A1A1AA]">
          <span>📅 {session.date}</span>
          <span>⏱ {session.duration} duration</span>
          {/* <span>🎯 {session.role}</span> */}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        {session.metrics.map((metric) => (
          <ProgressRow key={metric.label} {...metric} />
        ))}
      </div>

      <div className="ml-2 rounded-xl bg-[#F5F7F7] px-3 py-2 text-center">
        <div
          className={`text-[18px] font-bold ${
            session.first ? "text-[#9CA3AF]" : "text-[#0FA99D]"
          }`}
        >
          {Math.round(session.overall * 100)}%
        </div>
        <div className="text-[9px] text-[#A1A1AA]">Overall</div>
      </div>

      <div className="flex min-w-[90px] flex-col items-end gap-2">
        <Link
          to={`/candidate-report/${session.id}`}
          state={{ session }}
          className="rounded-full border border-[#0FA99D] bg-white px-3 py-1.5 text-[10px] font-bold text-[#0FA99D] hover:bg-[#F0FDFA]"
        >
          View Report
        </Link>

        {/* {session.first ? (
          <span className="text-[9px] font-bold text-[#9CA3AF]">
            Starting point
          </span>
        ) : (
          <span className="text-[9px] font-bold text-[#0FA99D]">
            {session.delta}
          </span>
        )} */}
      </div>
    </div>
  );
}

function InfoCard({ title, value, subtitle, accent = false }) {
  return (
    <div className="h-[102px] w-[230px] rounded-[22px] border border-[#E9E9E9] bg-white px-5 pt-3 shadow-sm">
      <div className="text-[11px] font-medium text-[#A3A3A3]">{title}</div>

      {value && (
        <div
          className={`mt-2 text-[22px] font-bold leading-none ${
            accent ? "text-[#0FA99D]" : "text-[#111827]"
          }`}
        >
          {value}
        </div>
      )}

      <div className="mt-2 text-[10px] text-[#B4B4B4]">{subtitle}</div>
    </div>
  );
}

function CandidateHistoryPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [filterBy, setFilterBy] = useState("all");
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const role = localStorage.getItem("role");
  const name = localStorage.getItem("name");
  const profileChar =
    name.trim().split(" ").length >= 2
      ? name
          .trim()
          .split(" ")
          .slice(0, 2)
          .map((n) => n[0])
          .join("")
          .toUpperCase()
      : name.trim().slice(0, 2).toUpperCase();
  const isRecruiter = role === "RECRUITER";

  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef(null);
  const handleLogout = () => {
    localStorage.clear();
    navigate("/signin");
  };

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        profileMenuRef.current &&
        !profileMenuRef.current.contains(event.target)
      ) {
        setProfileMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const fetchReports = async () => {
      setLoading(true);
      setError("");

      try {
        const token = localStorage.getItem("access_token");

        const response = await fetch("http://127.0.0.1:8000/users/reports", {
          method: "GET",
          headers: {
            accept: "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });

        const data = await response.json();

        console.log("Fetched reports:", data);

        if (!response.ok) {
          throw new Error(
            typeof data?.detail === "string"
              ? data.detail
              : "Failed to fetch reports",
          );
        }

        const reports = Array.isArray(data?.reports) ? data.reports : [];

        const sortedReports = [...reports].sort(
          (a, b) => new Date(b.uploaddate) - new Date(a.uploaddate),
        );

        const bestScore = Math.max(
          ...sortedReports.map((r) => r.total_score),
          0,
        );
        const firstVideoId =
          sortedReports.length > 0
            ? sortedReports[sortedReports.length - 1].videoid
            : null;
        const latestVideoId =
          sortedReports.length > 0 ? sortedReports[0].videoid : null;

        const mappedSessions = sortedReports.map((report, index) => {
          const previous = sortedReports[index + 1];
          const deltaValue =
            previous && typeof previous.total_score === "number"
              ? report.total_score - previous.total_score
              : null;

          return {
            id: report.videoid,
            sessionNumber: index + 1,
            date: formatDate(report.uploaddate),
            rawDate: report.uploaddate,
            duration: formatDuration(report.duration),
            role: report.videoname,
            overall: report.total_score,
            latest: report.videoid === latestVideoId,
            best: report.total_score === bestScore,
            first: report.videoid === firstVideoId,
            status: report.status,
            delta:
              deltaValue == null
                ? ""
                : `${deltaValue >= 0 ? "+" : ""}${deltaValue} vs prev`,
            metrics: [
              {
                label: "Grammar",
                value: Math.round(report.grammar_score * 100) ?? 0,
              },
              {
                label: "Fillers",
                value: Math.round(report.fillers_score * 100) ?? 0,
              },
              {
                label: "Pause Rate",
                value: Math.round(report.pause_rate_score * 100) ?? 0,
              },
              {
                label: "Energy",
                value: Math.round(report.energy_score * 100) ?? 0,
              },
              {
                label: "Eye Contact",
                value: Math.round(report.eye_contact_score * 100) ?? 0,
              },
              {
                label: "Emotion",
                value: Math.round(report.emotion_score * 100) ?? 0,
              },
            ],
          };
        });

        setSessions(mappedSessions);
      } catch (err) {
        console.error("Fetch reports error:", err);
        setError(err.message || "Something went wrong");
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const filteredAndSortedSessions = useMemo(() => {
    let result = [...sessions];

    if (filterBy === "latest") {
      result = result.filter((session) => session.latest);
    } else if (filterBy === "best") {
      result = result.filter((session) => session.best);
    } else if (filterBy === "first") {
      result = result.filter((session) => session.first);
    } else if (filterBy.startsWith("role:")) {
      const role = filterBy.replace("role:", "");
      result = result.filter((session) => session.role === role);
    }

    const query = searchTerm.trim().toLowerCase();
    if (query) {
      result = result.filter((session) => {
        return (
          session.date.toLowerCase().includes(query) ||
          session.role.toLowerCase().includes(query) ||
          String(session.id).includes(query) ||
          String(session.overall).includes(query) ||
          `session ${session.sessionNumber}`.toLowerCase().includes(query) ||
          session.status.toLowerCase().includes(query)
        );
      });
    }

    result.sort((a, b) => {
      if (sortBy === "newest") return new Date(b.rawDate) - new Date(a.rawDate);
      if (sortBy === "oldest") return new Date(a.rawDate) - new Date(b.rawDate);
      if (sortBy === "highest") return b.overall - a.overall;
      if (sortBy === "lowest") return a.overall - b.overall;
      return 0;
    });

    return result;
  }, [searchTerm, sortBy, filterBy, sessions]);

  const uniqueRoles = [...new Set(sessions.map((session) => session.role))];

  const totalSessions = sessions.length;

  const bestSession =
    sessions.length > 0
      ? sessions.reduce((best, current) =>
          current.overall > best.overall ? current : best,
        )
      : null;

  const averageOverall =
    sessions.length > 0
      ? Math.round(
          sessions.reduce((sum, session) => sum + session.overall, 0) /
            sessions.length,
        )
      : 0;
  const metricImprovements =
    sessions.length >= 2
      ? (() => {
          const newest = [...sessions].sort(
            (a, b) => new Date(b.rawDate) - new Date(a.rawDate),
          )[0];

          const oldest = [...sessions].sort(
            (a, b) => new Date(a.rawDate) - new Date(b.rawDate),
          )[0];

          const oldestMetricsMap = new Map(
            oldest.metrics.map((metric) => [metric.label, metric.value]),
          );

          const diffs = newest.metrics
            .filter((metric) => oldestMetricsMap.has(metric.label))
            .map((metric) => {
              const diff = metric.value - oldestMetricsMap.get(metric.label);

              console.log(
                `${metric.label}: ${metric.value} - ${oldestMetricsMap.get(metric.label)} = ${diff}`,
              );

              return {
                label: metric.label,
                diff,
              };
            });

          console.log("All diffs:", diffs);

          const best = diffs.reduce((best, current) =>
            current.diff > best.diff ? current : best,
          );

          console.log("Most improved metric:", best);

          return best;
        })()
      : null;

  return (
    <div className="min-h-screen w-full bg-[#E8E6E2]">
      {/* Header */}
      <header className="flex h-[72px] items-center justify-between border-b border-[#D8D8D8] bg-white px-6">
        <div className="flex items-center gap-10">
          <div className="text-[34px] font-normal text-[#0FA99D] [font-family:'Pacifico',Helvetica]">
            Interview me
          </div>

          {/* <div className="relative w-[360px]">
            <input
              className="h-[36px] w-full rounded-full bg-[#EFEFEF] pl-10 pr-4 text-[11px] text-gray-700 outline-none placeholder:text-[#9CA3AF]"
              placeholder="Search candidates, reports ..etc"
            />
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[12px] text-[#9CA3AF]">
              🔍
            </span>
          </div> */}
        </div>

        <div className="flex items-center gap-4">
          <div className="border-r border-[#E5E7EB] pr-3 text-right">
            <div className="text-[12px] font-semibold text-[#374151]">
              {name}
            </div>
            <div className="text-[10px] text-[#9CA3AF]">
              {isRecruiter ? "Recruiter Admin" : "User"}
            </div>
          </div>
          <div ref={profileMenuRef} className="relative">
            <button
              type="button"
              onClick={() => setProfileMenuOpen((prev) => !prev)}
              className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-[#DDF8F2] text-[10px] font-bold text-[#0FA99D] transition hover:opacity-80"
            >
              {profileChar || "NA"}
            </button>

            {profileMenuOpen && (
              <div className="absolute right-0 mt-2 w-[170px] rounded-[14px] border border-[#E5E7EB] bg-white py-2 shadow-lg z-50">
                <button
                  type="button"
                  onClick={handleLogout}
                  className="block w-full px-4 py-2 text-left text-[14px] font-medium text-[#374151] hover:bg-[#F3F4F6]"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="min-h-[calc(100vh-72px)] w-[240px] bg-white">
          <nav className="mt-8 flex flex-col gap-2 px-3">
            {/* <Link
              to="/"
              className="flex items-center gap-2 rounded-full px-4 py-3 text-[18px] font-medium text-[#0FA99D]"
            >
              <span className="inline-flex h-6 w-6 items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#0FA99D"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-3.5 w-3.5 shrink-0"
                >
                  <rect x="3" y="3" width="7" height="7" rx="1.5" />
                  <rect x="14" y="3" width="7" height="7" rx="1.5" />
                  <rect x="3" y="14" width="7" height="7" rx="1.5" />
                  <rect x="14" y="14" width="7" height="7" rx="1.5" />
                </svg>
              </span>
              <span>Dashboard</span>
            </Link> */}

            <Link
              to="/process-video"
              className="flex items-center gap-2 rounded-full px-4 py-3 text-[18px] font-medium text-[#0FA99D]"
            >
              <span className="inline-flex items-center justify-center p-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="-3 0 30 24"
                  fill="none"
                  stroke="#0FA99D"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5 shrink-0"
                >
                  <path d="M20 16.5A4.5 4.5 0 0 0 17 8h-1.26A8 8 0 1 0 4 15.25" />
                  <path d="M12 20V11" />
                  <path d="m8.8 14.2 3.2-3.2 3.2 3.2" />
                </svg>
              </span>
              <span>Analyze Interview</span>
            </Link>

            <Link
              to="/candidate-history"
              className="flex w-full items-center gap-2 rounded-full bg-[#E8FBF7] px-4 py-3 text-[18px] font-medium text-[#0FA99D]"
            >
              <span className="inline-flex h-6 w-6 items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#0FA99D"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-4 w-4 shrink-0"
                >
                  <path d="M3 12a9 9 0 1 0 3-6.7" />
                  <path d="M3 4v5h5" />
                  <path d="M12 7v5l3 2" />
                </svg>
              </span>
              <span>History</span>
            </Link>
          </nav>
        </aside>

        <main className="flex-1 bg-[#E8E6E2]">
          <div className="px-6 py-8">
            <div className="flex flex-wrap items-center gap-4">
              <InfoCard
                title="Total sessions"
                value={String(totalSessions)}
                subtitle={
                  totalSessions ? "From your reports" : "No sessions yet"
                }
              />
              <InfoCard
                title="Best score"
                value={
                  bestSession
                    ? `${Math.round(bestSession.overall * 100)}%`
                    : "0%"
                }
                subtitle={
                  bestSession
                    ? `${bestSession.date} · Session ${bestSession.sessionNumber}`
                    : "No best score yet"
                }
                accent
              />
              <InfoCard
                title="Avg. overall score"
                value={`${Math.round(averageOverall * 100)}%`}
                subtitle="Across all sessions"
              />
              {/* <InfoCard
                title="Most improved"
                value={metricImprovements ? metricImprovements.label : "-"}
                subtitle={
                  metricImprovements
                    ? `${metricImprovements.diff >= 0 ? "+" : ""}${metricImprovements.diff} pts improvement`
                    : "Need at least 2 sessions"
                }
                accent
              /> */}
            </div>

            <section className="mt-6">
              <div className="rounded-[14px] border border-[#E8E8E8] bg-white px-4 py-3 shadow-[0_2px_8px_rgba(0,0,0,0.02)]">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="relative min-w-[360px] flex-1">
                    <input
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="h-[34px] w-full rounded-lg border border-[#EFEFEF] bg-[#FAFAFA] py-2 pl-8 pr-3 text-[11px] outline-none placeholder:text-[#B0B0B0]"
                      placeholder="Search by date, score, or session..."
                    />
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[11px] text-[#B0B0B0]">
                      🔍
                    </span>
                  </div>

                  <span className="text-[10px] text-[#B0B0B0]">Sort by</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="h-[32px] rounded-lg border border-[#ECECEC] bg-[#FAFAFA] px-4 text-[10px] text-[#6B7280] outline-none"
                  >
                    <option value="newest">Newest first</option>
                    <option value="oldest">Oldest first</option>
                    <option value="highest">Highest score</option>
                    <option value="lowest">Lowest score</option>
                  </select>

                  <span className="text-[10px] text-[#B0B0B0]">Filter</span>
                  <select
                    value={filterBy}
                    onChange={(e) => setFilterBy(e.target.value)}
                    className="h-[32px] rounded-lg border border-[#ECECEC] bg-[#FAFAFA] px-4 text-[10px] text-[#6B7280] outline-none"
                  >
                    <option value="all">All sessions</option>
                    <option value="latest">Latest</option>
                    <option value="best">Best score</option>
                    <option value="first">First session</option>
                    {uniqueRoles.map((role) => (
                      <option key={role} value={`role:${role}`}>
                        {role}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mt-4 flex flex-col gap-3">
                {loading ? (
                  <Spinner
                    message="Processing your videos..."
                    submessage="This may take a few minutes depending on video length"
                  />
                ) : error ? (
                  <div className="rounded-[16px] border border-[#FECACA] bg-white px-6 py-10 text-center text-[12px] text-red-500">
                    {error}
                  </div>
                ) : filteredAndSortedSessions.length > 0 ? (
                  filteredAndSortedSessions.map((session) => (
                    <SessionCard
                      key={session.sessionNumber}
                      session={session}
                    />
                  ))
                ) : (
                  <div className="rounded-[16px] border border-[#ECECEC] bg-white px-6 py-10 text-center text-[12px] text-[#9CA3AF]">
                    No sessions found.
                  </div>
                )}
              </div>

              <div className="mt-4 flex items-center justify-between">
                <span className="text-[12px] text-[#9CA3AF]">
                  Showing {filteredAndSortedSessions.length} of{" "}
                  {sessions.length} sessions
                </span>

                <div className="flex items-center gap-2">
                  <button className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#D9F3EE] bg-white text-[#0FA99D] opacity-40">
                    ←
                  </button>
                  <button className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#0FA99D] bg-[#0FA99D] text-white">
                    1
                  </button>
                  <button className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#D9F3EE] bg-white text-[#0FA99D] opacity-40">
                    →
                  </button>
                </div>
              </div>
            </section>

            <footer className="mt-14 text-center text-[11px] text-[#9CA3AF]">
              © 2026 Interview Me. All rights reserved.
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
}

export default CandidateHistoryPage;
