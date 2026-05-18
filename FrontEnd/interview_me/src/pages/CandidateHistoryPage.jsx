import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

const sessions = [
  {
    id: 7,
    date: "Apr 22, 2026",
    duration: "18:42",
    role: "Software Engineer",
    overall: 72,
    latest: true,
    best: true,
    delta: "+2 vs prev",
    metrics: [
      { label: "Language", value: 81 },
      { label: "Fluency", value: 76 },
      { label: "Vocal", value: 68 },
      { label: "Visual", value: 64 },
      { label: "Facial", value: 58 },
    ],
  },
  {
    id: 6,
    date: "Apr 10, 2026",
    duration: "15:30",
    role: "Product Manager",
    overall: 70,
    delta: "+3 vs prev",
    metrics: [
      { label: "Language", value: 78 },
      { label: "Fluency", value: 72 },
      { label: "Vocal", value: 65 },
      { label: "Visual", value: 62 },
      { label: "Facial", value: 55 },
    ],
  },
  {
    id: 5,
    date: "Mar 28, 2026",
    duration: "12:18",
    role: "Data Analyst",
    overall: 67,
    delta: "+3 vs prev",
    metrics: [
      { label: "Language", value: 74 },
      { label: "Fluency", value: 68 },
      { label: "Vocal", value: 60 },
      { label: "Visual", value: 58 },
      { label: "Facial", value: 52 },
    ],
  },
  {
    id: 4,
    date: "Mar 14, 2026",
    duration: "11:05",
    role: "Software Engineer",
    overall: 64,
    delta: "+3 vs prev",
    metrics: [
      { label: "Language", value: 70 },
      { label: "Fluency", value: 62 },
      { label: "Vocal", value: 58 },
      { label: "Visual", value: 55 },
      { label: "Facial", value: 48 },
    ],
  },
  {
    id: 3,
    date: "Feb 28, 2026",
    duration: "09:44",
    role: "Frontend Developer",
    overall: 61,
    delta: "+4 vs prev",
    metrics: [
      { label: "Language", value: 65 },
      { label: "Fluency", value: 60 },
      { label: "Vocal", value: 55 },
      { label: "Visual", value: 52 },
      { label: "Facial", value: 44 },
    ],
  },
  {
    id: 2,
    date: "Feb 10, 2026",
    duration: "08:22",
    role: "General practice",
    overall: 57,
    delta: "+3 vs prev",
    metrics: [
      { label: "Language", value: 60 },
      { label: "Fluency", value: 55 },
      { label: "Vocal", value: 52 },
      { label: "Visual", value: 50 },
      { label: "Facial", value: 38 },
    ],
  },
  {
    id: 1,
    date: "Jan 15, 2026",
    duration: "06:55",
    role: "General practice",
    overall: 54,
    first: true,
    metrics: [
      { label: "Language", value: 58 },
      { label: "Fluency", value: 52 },
      { label: "Vocal", value: 48 },
      { label: "Visual", value: 45 },
      { label: "Facial", value: 34 },
    ],
  },
];

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
        {session.id}
      </div>

      <div className="min-w-[240px] flex-1">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <span className="text-[12px] font-bold text-[#1F2937]">
            Session {session.id}
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
        </div>

        <div className="flex flex-wrap gap-3 text-[10px] text-[#A1A1AA]">
          <span>📅 {session.date}</span>
          <span>⏱ {session.duration} duration</span>
          <span>🎯 {session.role} role</span>
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
          {session.overall}%
        </div>
        <div className="text-[9px] text-[#A1A1AA]">Overall</div>
      </div>

      <div className="flex min-w-[90px] flex-col items-end gap-2">
        <Link
          to="/report"
          className="rounded-full border border-[#0FA99D] bg-white px-3 py-1.5 text-[10px] font-bold text-[#0FA99D] hover:bg-[#F0FDFA]"
        >
          View Report
        </Link>

        {session.first ? (
          <span className="text-[9px] font-bold text-[#9CA3AF]">
            Starting point
          </span>
        ) : (
          <span className="text-[9px] font-bold text-[#0FA99D]">
            {session.delta}
          </span>
        )}
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
          `session ${session.id}`.toLowerCase().includes(query)
        );
      });
    }

    result.sort((a, b) => {
      if (sortBy === "newest") return new Date(b.date) - new Date(a.date);
      if (sortBy === "oldest") return new Date(a.date) - new Date(b.date);
      if (sortBy === "highest") return b.overall - a.overall;
      if (sortBy === "lowest") return a.overall - b.overall;
      return 0;
    });

    return result;
  }, [searchTerm, sortBy, filterBy]);

  const uniqueRoles = [...new Set(sessions.map((session) => session.role))];

  return (
    <div className="min-h-screen w-full bg-[#E8E6E2]">
      {/* Header */}
      <header className="flex h-[72px] items-center justify-between border-b border-[#D8D8D8] bg-white px-6">
        <div className="flex items-center gap-10">
          <div className="text-[34px] font-normal text-[#0FA99D] [font-family:'Pacifico',Helvetica]">
            Interview me
          </div>

          <div className="relative w-[360px]">
            <input
              className="h-[36px] w-full rounded-full bg-[#EFEFEF] pl-10 pr-4 text-[11px] text-gray-700 outline-none placeholder:text-[#9CA3AF]"
              placeholder="Search candidates, reports ..etc"
            />
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[12px] text-[#9CA3AF]">
              🔍
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="border-r border-[#E5E7EB] pr-3 text-right">
            <div className="text-[12px] font-semibold text-[#374151]">
              Sarah Ahmed
            </div>
            <div className="text-[10px] text-[#9CA3AF]">Recruiter Admin</div>
          </div>
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#DDF8F2] text-[10px] font-bold text-[#0FA99D]">
            SA
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="min-h-[calc(100vh-72px)] w-[240px] bg-white">
          <nav className="mt-8 flex flex-col gap-2 px-3">
            <Link
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
            </Link>

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
              to="/history"
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
                value="7"
                subtitle="Since Jan 2026"
              />
              <InfoCard
                title="Best score"
                value="72%"
                subtitle="Apr 2026 · Session 7"
                accent
              />
              <InfoCard
                title="Avg. overall score"
                value="65%"
                subtitle="Across all sessions"
              />
              <InfoCard
                title="Most improved"
                value="Fluency"
                subtitle="+24 pts improvement"
                accent
              />
            </div>

            <section className="mt-6">
              <div className="rounded-[14px] border border-[#E8E8E8] bg-white px-4 py-3 shadow-[0_2px_8px_rgba(0,0,0,0.02)]">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="relative min-w-[360px] flex-1">
                    <input
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="h-[34px] w-full rounded-lg border border-[#EFEFEF] bg-[#FAFAFA] py-2 pl-8 pr-3 text-[11px] outline-none placeholder:text-[#B0B0B0]"
                      placeholder="Search by date, role, score, or session..."
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
                {filteredAndSortedSessions.length > 0 ? (
                  filteredAndSortedSessions.map((session) => (
                    <SessionCard key={session.id} session={session} />
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
