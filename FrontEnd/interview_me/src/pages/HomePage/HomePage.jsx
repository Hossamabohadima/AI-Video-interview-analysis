import { useNavigate } from "react-router-dom";
import PublicNavbar from "../../components/PublicNavbar/PublicNavbar";
import biasIcon  from "../../assets/bias-icon.svg";
import robotIcon from "../../assets/robot-icon.svg";
import timeIcon  from "../../assets/time-icon.svg";
import vector    from "../../assets/ai-icon.svg";

// ── DATA ──────────────────────────────────────────────────────────────────────

const FEATURE_CARDS = [
  {
    id:          "eliminate-bias",
    title:       "Eliminate Bias",
    description: "Our AI evaluates candidates based on standardized metrics, removing unconscious human bias.",
    icon:        biasIcon,
    alt:         "Bias icon",
  },
  {
    id:          "multi-modal",
    title:       "Multi-modal Analysis",
    description: "Capturing Audio Tone, Facial Expressions, Verbal Content and more.",
    icon:        vector,
    alt:         "AI icon",
  },
  {
    id:          "rapid-processing",
    title:       "Rapid Processing",
    description: "Our system processes more than 100 interview videos at once and ranks candidates automatically.",
    icon:        timeIcon,
    alt:         "Time icon",
  },
];

// ── PAGE ──────────────────────────────────────────────────────────────────────

export const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex flex-col">

      <PublicNavbar activePage="Home" />

      {/* ── HERO ── */}
      <section
        aria-labelledby="hero-heading"
        className="flex flex-col-reverse lg:flex-row items-center justify-center gap-8 px-6 py-16 md:py-24 max-w-6xl mx-auto w-full"
      >
        {/* Text */}
        <div className="flex flex-col items-center lg:items-start text-center lg:text-left gap-6 max-w-xl">
          <h1
            id="hero-heading"
            className="text-3xl sm:text-4xl md:text-5xl font-bold text-[#494949] leading-tight"
          >
            Master the Interview.{" "}
            <span className="text-[#009986]">Hire the Best.</span>
          </h1>
          <p className="text-[#566068] text-base sm:text-lg leading-relaxed">
            The world&apos;s first Multi-modal AI Interview Assistant. We analyze
            voice, text, and facial expressions to deliver objective,
            data-driven insights for candidates and recruiters.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => navigate("/signup?role=Candidate")}
              className="bg-[#009986] text-white font-bold text-lg px-8 py-3 rounded-2xl hover:bg-[#007a6e] transition-colors w-full sm:w-auto"
            >
              I&apos;m a Candidate
            </button>
            <button
              type="button"
              onClick={() => navigate("/signup?role=Company")}
              className="bg-white border-2 border-[#009986] text-[#009986] font-bold text-lg px-8 py-3 rounded-2xl hover:bg-[#e5e4e2] transition-colors w-full sm:w-auto"
            >
              I&apos;m a Recruiter
            </button>
          </div>
        </div>

        {/* Robot image */}
        <div className="flex-shrink-0">
          <img
            src={robotIcon}
            alt="AI Interview Assistant illustration"
            className="w-48 sm:w-64 md:w-72 lg:w-80"
          />
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section
        aria-labelledby="features-heading"
        className="px-6 pb-20 max-w-6xl mx-auto w-full"
      >
        <div className="bg-white rounded-[80px] md:rounded-[120px] px-6 py-12 md:py-16">
          <h2
            id="features-heading"
            className="text-2xl sm:text-3xl md:text-4xl font-bold text-[#494949] text-center mb-12"
          >
            The Future of Talent Assessment
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 max-w-4xl mx-auto">
            {FEATURE_CARDS.map((card) => (
              <article
                key={card.id}
                className="bg-[#e5e4e2] rounded-2xl p-6 flex flex-col items-center text-center gap-4 hover:shadow-md transition-shadow"
              >
                <img
                  src={card.icon}
                  alt={card.alt}
                  className="w-20 h-20 object-contain"
                />
                <h3 className="font-bold text-black text-xl">{card.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  {card.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="mt-auto py-6 text-center">
        <p className="text-[#888888] text-xs">
          &copy; {new Date().getFullYear()} Interview Me. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default HomePage;