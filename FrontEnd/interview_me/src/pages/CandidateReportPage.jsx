import { Link, useParams, useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import Spinner from "../components/UI/Spinner";


function SidebarItem({ active = false, icon, label, to = "#" }) {
  return (
    <Link
      to={to}
      className={`flex w-full items-center gap-2 rounded-full px-4 py-3 text-[18px] font-medium ${
        active ? "bg-[#E8FBF7] text-[#0FA99D]" : "text-[#0FA99D]"
      }`}
    >
      <span className="inline-flex h-6 w-6 items-center justify-center">
        {icon}
      </span>
      <span>{label}</span>
    </Link>
  );
}

function ScoreRingCard({ title, score, subtitle }) {
  const size = 40;
  const strokeWidth = 5;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = ((score || 0) / 100) * circumference;
  const offset = circumference - progress;

  const getColor = (score) => {
    if (score >= 80) return "#0FA99D";
    if (score >= 60) return "#F59E0B";
    return "#EF4444";
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

function HistoryIcon() {
  return (
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
  );
}

function AnalyzeIcon() {
  return (
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
  );
}

function CandidateReportPage() {
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const profileMenuRef = useRef(null);

  const { id } = useParams();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    navigate("/signin");
  };

  const role = localStorage.getItem("role");
  const name = localStorage.getItem("name") || "User";
  const token = localStorage.getItem("access_token");
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
    const fetchReport = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `http://127.0.0.1:8000/users/reports/${id}`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${token}`,
            },
          },
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch report: ${response.status}`);
        }

        const data = await response.json();
        setReportData(data);
      } catch (err) {
        console.error("Error fetching report:", err);
        setError(err.message || "Failed to load report");
      } finally {
        setLoading(false);
      }
    };

    if (id && token) {
      fetchReport();
    } else {
      setError("Missing video id or authentication token");
      setLoading(false);
    }
  }, [id, token]);

  const toPercent = (value) => Math.round((value || 0) * 100);

  const getMetric = (key) => {
    if (!reportData?.score) return 0;
    return toPercent(reportData.score[key]);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E8E6E2]">
        <Spinner
          message="Loading Report.."
          submessage="Fetching scores and feedback for your video"
        />
      </div>
    );
  }

  if (error || !reportData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E8E6E2]">
        <div className="rounded-xl bg-white px-6 py-4 text-sm text-red-500 shadow">
          {error || `Report not found for video ${id}`}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-[#E8E6E2]">
      <header className="flex h-[72px] items-center justify-between border-b border-[#D8D8D8] bg-white px-6">
        <div className="flex items-center gap-10">
          <div className="text-[34px] font-normal text-[#0FA99D] [font-family:'Pacifico',Helvetica]">
            Interview me
          </div>
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
              <div className="absolute right-0 z-50 mt-2 w-[170px] rounded-[14px] border border-[#E5E7EB] bg-white py-2 shadow-lg">
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

      <div className="flex">
        <aside className="min-h-[calc(100vh-72px)] w-[240px] bg-white">
          <nav className="mt-8 flex flex-col gap-2 px-3">
            <SidebarItem
              active
              icon={<AnalyzeIcon />}
              label="Analyze Interview"
              to="/process-video"
            />
            <SidebarItem
              icon={<HistoryIcon />}
              label="History"
              to="/candidate-history"
            />
          </nav>
        </aside>

        <main className="flex-1 bg-[#E8E6E2] px-4 py-6">
          <section className="rounded-[20px] bg-white px-6 py-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[#0FA99D] bg-[#DDF8F2] text-[20px] font-bold text-[#0FA99D]">
                  {id}
                </div>

                <div>
                  <div className="text-[28px] font-semibold text-[#222]">
                    Video Report #{id}
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
              <ScoreRingCard
                title="Grammar"
                score={getMetric("grammar_score")}
              />
              <ScoreRingCard
                title="Fillers"
                score={getMetric("fillers_score")}
              />
              <ScoreRingCard
                title="Pause Rate"
                score={getMetric("pause_rate_score")}
              />
              <ScoreRingCard title="Energy" score={getMetric("energy_score")} />
              <ScoreRingCard
                title="Eye Contact"
                score={getMetric("eye_contact_score")}
              />
              <ScoreRingCard
                title="Emotion"
                score={getMetric("emotion_score")}
              />
              <ScoreRingCard
                title="Overall Score"
                score={getMetric("total_score")}
              />
            </div>
          </section>

          <section className="mt-5 rounded-[20px] bg-white px-6 py-5 shadow-sm">
            <h1 className="text-[32px] font-semibold text-[#222]">
              Feedback Report
            </h1>
            <div className="mt-6 space-y-6">
              {reportData.report
                ?.split("\n\n")
                .filter(Boolean)
                .map((section, index) => {
                  const lines = section.split("\n");
                  const heading = lines[0]?.trim();
                  const content = lines.slice(1).join(" ").trim();

                  const isMainHeading =
                    heading === "Performance Overview" ||
                    heading === "Key Strengths" ||
                    heading === "Actionable Tips";

                  return (
                    <div
                      key={index}
                      className="rounded-[16px] border border-[#E5E7EB] bg-[#F9FAFB] px-5 py-4 shadow-sm"
                    >
                      {isMainHeading ? (
                        <h3 className="mb-3 text-[26px] font-bold text-[#0FA99D] leading-tight">
                          {heading}
                        </h3>
                      ) : (
                        <h4 className="mb-2 text-[20px] font-semibold text-[#374151]">
                          {heading}
                        </h4>
                      )}

                      <p className="text-[17px] leading-8 text-[#4B5563]">
                        {content}
                      </p>
                    </div>
                  );
                })}
            </div>
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