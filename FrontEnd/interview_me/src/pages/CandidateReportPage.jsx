import { Link } from "react-router-dom";

function ScoreRingCard({ title, score, subtitle }) {
  return (
    <div className="flex h-[84px] w-[135px] flex-col justify-between rounded-[18px] border border-[#D9EDEA] bg-white px-3 py-2 shadow-sm">
      <div className="text-[8px] leading-tight text-[#A1A1AA]">{title}</div>

      <div className="flex items-center justify-between">
        <div>
          <div className="text-[24px] font-bold leading-none text-[#222]">
            {score}%
          </div>
        </div>

        <div className="relative flex h-10 w-10 items-center justify-center">
          <div className="h-8 w-8 rounded-full border-[5px] border-[#0FA99D] border-t-[#DDF4F0]" />
        </div>
      </div>

      {subtitle && <div className="text-[7px] text-[#C0C0C0]">{subtitle}</div>}
    </div>
  );
}

function MetricRow({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between gap-3 py-1">
      <span className="text-[9px] text-[#8C8C8C]">{label}</span>

      <div className="flex items-center gap-2">
        <span
          className={`text-[9px] font-bold ${
            highlight ? "text-[#F59E0B]" : "text-[#0FA99D]"
          }`}
        >
          {value}
        </span>
        <div className="h-[2px] w-[40px] rounded-full bg-[#DDEDEA]">
          <div className="h-[2px] w-[28px] rounded-full bg-[#0FA99D]" />
        </div>
      </div>
    </div>
  );
}

function ReportCard({ icon, title, subtitle, score, rows, accent = "teal" }) {
  return (
    <div className="rounded-[14px] border border-[#0FA99D] bg-white px-4 py-3 shadow-sm">
      <div className="mb-3 flex items-start justify-between">
        <div>
          <div className="text-[11px] font-bold text-[#374151]">
            <span className="mr-1">{icon}</span>
            {title}
          </div>
          <div className="text-[8px] text-[#B0B0B0]">{subtitle}</div>
        </div>

        <div className="text-right">
          <div
            className={`text-[18px] font-bold ${
              accent === "yellow" ? "text-[#F59E0B]" : "text-[#0FA99D]"
            }`}
          >
            {score}%
          </div>
          <div className="text-[7px] text-[#B0B0B0]">module score</div>
        </div>
      </div>

      <div className="space-y-1">
        {rows.map((row, index) => (
          <MetricRow
            key={index}
            label={row.label}
            value={row.value}
            highlight={row.highlight}
          />
        ))}
      </div>
    </div>
  );
}

function CandidateReportPage() {
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

        {/* Main */}
        <main className="flex-1 bg-[#E8E6E2] px-4 py-6">
          <section className="rounded-[20px] bg-white px-6 py-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[#0FA99D] bg-[#DDF8F2] text-[20px] font-bold text-[#0FA99D]">
                  SA
                </div>

                <div>
                  <div className="text-[28px] font-semibold text-[#222]">
                    Sara Ahmed
                  </div>
                  <div className="text-[10px] text-[#B0B0B0]">
                    Analyzed: 2026/04/22
                  </div>
                </div>
              </div>

              <button
                onClick={() => window.print()}
                className="rounded-full border border-[#DDEDEA] bg-white px-4 py-2 text-[10px] font-bold text-[#0FA99D] shadow-sm"
              >
                ⭳ Export PDF
              </button>
            </div>

            <div className="mt-5 flex flex-wrap gap-4">
              <ScoreRingCard title="Lang & Clarity" score={98} />
              <ScoreRingCard title="Speech Fluency" score={87} />
              <ScoreRingCard title="Vocal Express." score={96} />
              <ScoreRingCard title="Visual Eng." score={90} />
              <ScoreRingCard title="Facial Pos." score={86} />
              <ScoreRingCard
                title="Overall Score"
                score={92}
                subtitle="Uploaded in batch"
              />
            </div>
          </section>

          <section className="mt-5 grid grid-cols-2 gap-4">
            <ReportCard
              icon="🗣"
              title="Language & Clarity"
              subtitle="Grammar · Vocabulary · Structure"
              score={88}
              rows={[
                { label: "Grammar accuracy", value: "94%" },
                { label: "Vocabulary richness", value: "86%" },
                { label: "Response structure", value: "82%" },
                { label: "Errors detected", value: "3 errors" },
              ]}
            />

            <ReportCard
              icon="🧠"
              title="Speech Fluency"
              subtitle="Rate · Pauses · Filler words"
              score={91}
              rows={[
                { label: "Speaking rate", value: "142 wpm" },
                {
                  label: "Filler words",
                  value: "8 total · 2/min",
                  highlight: true,
                },
                { label: "Awkward pauses", value: "2 pauses" },
                { label: "Rhythm score", value: "90%" },
              ]}
            />

            <ReportCard
              icon="🗣"
              title="Vocal Expressiveness"
              subtitle="Pitch · Energy · Loudness"
              score={94}
              rows={[
                { label: "Pitch variation", value: "High" },
                { label: "Vocal energy", value: "96%" },
                { label: "Loudness consistency", value: "91%" },
                { label: "Monotone detected", value: "No" },
              ]}
            />

            <ReportCard
              icon="👁"
              title="Visual Engagement"
              subtitle="Eye contact · Head posture"
              score={90}
              rows={[
                { label: "Eye contact ratio", value: "82%" },
                { label: "Head posture stability", value: "94%" },
                { label: "Looked away", value: "18% of time" },
                { label: "Distraction events", value: "2 events" },
              ]}
            />

            <ReportCard
              icon="🙂"
              title="Facial Positivity"
              subtitle="Smile · Expression · Warmth"
              score={96}
              accent="yellow"
              rows={[
                { label: "Smile frequency", value: "High" },
                { label: "Positive expressions", value: "92%" },
                { label: "Anxiety detected", value: "Low (4%)" },
                { label: "Neutral expression", value: "24% of time" },
              ]}
            />
          </section>

          <footer className="mt-6 text-center text-[11px] text-[#9CA3AF]">
            © 2026 Interview Me. All rights reserved.
          </footer>
        </main>
      </div>
    </div>
  );
}

export default CandidateReportPage;
