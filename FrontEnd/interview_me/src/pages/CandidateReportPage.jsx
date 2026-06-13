import { Link, useLocation, useParams, useNavigate } from "react-router-dom";

function ScoreRingCard({ title, score, subtitle }) {
  const size = 40;
  const strokeWidth = 5;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = ((score || 0) / 100) * circumference;
  const offset = circumference - progress;

  // Dynamic color based on score
  const getColor = (score) => {
    if (score >= 80) return "#0FA99D"; // green/teal
    if (score >= 60) return "#F59E0B"; // yellow/orange
    return "#EF4444"; // red
  };

  const strokeColor = getColor(score);

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
          <svg width={size} height={size} className="transform -rotate-90">
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="#DDF4F0"
              strokeWidth={strokeWidth}
            />
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={strokeColor}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-500 ease-out"
            />
          </svg>
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
  const { state } = useLocation();
  const { id } = useParams();
  const navigate = useNavigate();

  const session = state?.session;

  const role = localStorage.getItem("role");
  const name = localStorage.getItem("name") || "User";
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

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E8E6E2]">
        <div className="rounded-xl bg-white px-6 py-4 text-sm text-red-500 shadow">
          Report not found for session {id}
        </div>
      </div>
    );
  }

  const getMetric = (label) =>
    session.metrics.find((m) => m.label === label)?.value ?? 0;

  return (
    <div className="min-h-screen w-full bg-[#E8E6E2]">
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
          <button
            type="button"
            onClick={() => navigate("/history")}
            className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-[#DDF8F2] text-[10px] font-bold text-[#0FA99D] transition hover:opacity-80"
          >
            {profileChar || "NA"}
          </button>
        </div>
      </header>

      <div className="flex">
        <aside className="min-h-[calc(100vh-72px)] w-[240px] bg-white">
          <nav className="mt-8 flex flex-col gap-2 px-3">
            <Link
              to="/"
              className="flex items-center gap-2 rounded-full px-4 py-3 text-[18px] font-medium text-[#0FA99D]"
            >
              <span>Dashboard</span>
            </Link>

            <Link
              to="/process-video"
              className="flex items-center gap-2 rounded-full px-4 py-3 text-[18px] font-medium text-[#0FA99D]"
            >
              <span>Analyze Interview</span>
            </Link>

            <Link
              to="/history"
              className="flex w-full items-center gap-2 rounded-full bg-[#E8FBF7] px-4 py-3 text-[18px] font-medium text-[#0FA99D]"
            >
              <span>History</span>
            </Link>
          </nav>
        </aside>

        <main className="flex-1 bg-[#E8E6E2] px-4 py-6">
          <section className="rounded-[20px] bg-white px-6 py-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[#0FA99D] bg-[#DDF8F2] text-[20px] font-bold text-[#0FA99D]">
                  {session.sessionNumber}
                </div>

                <div>
                  <div className="text-[28px] font-semibold text-[#222]">
                    Session {session.sessionNumber}
                  </div>
                  <div className="text-[10px] text-[#B0B0B0]">
                    Analyzed: {session.date} · {session.role}
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
              <ScoreRingCard title="Grammar" score={getMetric("Grammar")} />
              <ScoreRingCard title="Fillers" score={getMetric("Fillers")} />
              <ScoreRingCard
                title="Pause Rate"
                score={getMetric("Pause Rate")}
              />
              <ScoreRingCard title="Energy" score={getMetric("Energy")} />
              <ScoreRingCard
                title="Eye Contact"
                score={getMetric("Eye Contact")}
              />
              <ScoreRingCard
                title="Emotion"
                score={getMetric("Emotion")}
                // subtitle="Emotional expression"
              />
              <ScoreRingCard
                title="Overall Score"
                score={session.overall}
                // subtitle={session.status}
              />
            </div>
          </section>

          <section className="mt-5 grid grid-cols-2 gap-4">
            {/* <ReportCard
              icon="🗣"
              title="Language & Clarity"
              subtitle="Grammar performance"
              score={getMetric("Grammar")}
              rows={[
                { label: "Grammar score", value: `${getMetric("Grammar")}%` },
                { label: "Session status", value: session.status },
                { label: "Duration", value: session.duration },
                { label: "Role", value: session.role },
              ]}
            />

            <ReportCard
              icon="🧠"
              title="Speech Fluency"
              subtitle="Fillers · Pauses"
              score={Math.round(
                (getMetric("Fillers") + getMetric("Pause Rate")) / 2,
              )}
              rows={[
                { label: "Fillers score", value: `${getMetric("Fillers")}%` },
                {
                  label: "Pause rate score",
                  value: `${getMetric("Pause Rate")}%`,
                },
                { label: "Overall score", value: `${session.overall}%` },
                { label: "Date", value: session.date },
              ]}
            />

            <ReportCard
              icon="🗣"
              title="Vocal Expressiveness"
              subtitle="Energy analysis"
              score={getMetric("Energy")}
              rows={[
                { label: "Energy score", value: `${getMetric("Energy")}%` },
                { label: "Status", value: session.status },
                { label: "Duration", value: session.duration },
                { label: "Delta", value: session.delta || "—" },
              ]}
            />

            <ReportCard
              icon="👁"
              title="Visual Engagement"
              subtitle="Eye contact"
              score={getMetric("Eye Contact")}
              rows={[
                {
                  label: "Eye contact score",
                  value: `${getMetric("Eye Contact")}%`,
                },
                { label: "Session", value: `Session ${session.sessionNumber}` },
                { label: "Role", value: session.role },
                { label: "Date", value: session.date },
              ]}
            />

            <ReportCard
              icon="🙂"
              title="Emotional Expression"
              subtitle="Emotion analysis"
              score={getMetric("Emotion")}
              accent="yellow"
              rows={[
                { label: "Emotion score", value: `${getMetric("Emotion")}%` },
                { label: "Status", value: session.status },
                { label: "Overall", value: `${session.overall}%` },
                { label: "Progress", value: session.delta || "—" },
              ]}
            /> */}
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
