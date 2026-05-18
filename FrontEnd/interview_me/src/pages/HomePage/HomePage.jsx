import "@fontsource/pacifico";
import biasIcon from "../../assets/bias-icon.svg";
import polygon1 from "../../assets/polygon.svg";
import robotIcon from "../../assets/robot-icon.svg";
import timeIcon from "../../assets/time-icon.svg";
import vector from "../../assets/ai-icon.svg";
import { useState } from "react";
import { Link } from "react-router-dom";

const navItems = [
  { label: "Home", href: "/", active: true },
  { label: "How it works", href: "/how-it-works", active: false },
  { label: "Products", href: "/process-video", active: false, hasDropdown: true },
];

const featureCards = [
  {
    title: "Eliminate Bias",
    description:
      "Our AI evaluates candidates based on standardized metrics, removing unconscious human bias.",
    icon: biasIcon,
    alt: "Bias icon",
  },
  {
    title: "Multi-modal Analysis",
    description:
      "Capturing Audio Tone, Facial Expressions, Verbal Content and more.",
    icon: vector,
    alt: "AI icon",
  },
  {
    title: "Rapid Processing",
    description:
      "Our system processes more than 100 interview videos at once and ranks candidates automatically.",
    icon: timeIcon,
    alt: "Time icon",
  },
];

export const HomePage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#e5e4e2] flex flex-col">

      {/* ── NAVBAR ── */}
      <header className="w-full px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <span style={{ fontFamily: 'Pacifico' }} className="font-Pacifico text-[#009986] text-3xl md:text-3xl whitespace-nowrap">
          Interview me
        </span>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navItems.map((item) => (
            <div key={item.label} className="relative flex flex items-center gap-1">
              <Link
                to={item.href}
                aria-current={item.active ? "page" : undefined}
                className={`font-bold text-lg transition-colors ${
                  item.active ? "text-[#009986]" : "text-[#566068] hover:text-[#009986]"
                }`}
              >
                {item.label}
              </Link>
              {item.hasDropdown && (
                <img
                  src={polygon1}
                  alt=""
                  className="w-2.5 h-2 mt-1"
                  aria-hidden="true"
                />
              )}
            </div>
          ))}
          <Link
            to="/signup"
          >
          <button
            type="button"
            className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl hover:bg-[#007a6e] transition-colors"
          >
            Sign up
          </button>
          </Link>
        </nav>

        {/* Mobile Hamburger */}
        <button
          type="button"
          className="md:hidden text-[#566068] focus:outline-none"
          aria-label="Toggle menu"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {mobileMenuOpen
              ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            }
          </svg>
        </button>
      </header>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white shadow-md px-6 py-4 flex flex-col gap-4">
          {navItems.map((item) => (
            <Link
              key={item.label}
              to={item.href}
              className={`text-left font-semibold text-lg ${
                item.active ? "text-[#009986]" : "text-[#566068]"
              }`}
            >
              {item.label}
            </Link>
          ))}
          <Link
            to="/signup"
            className="bg-[#009986] text-white font-semibold text-base px-6 py-2 rounded-2xl w-fit hover:bg-[#007a6e] transition-colors inline-flex items-center justify-center"
          >
            Sign up
          </Link>
        </div>
      )}

      {/* ── HERO SECTION ── */}
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
            <Link to="/signup">
              <button
                type="button"
                className="bg-[#009986] text-white font-bold text-lg px-8 py-3 rounded-2xl hover:bg-[#007a6e] transition-colors w-full sm:w-auto"
              >
                I&apos;m a Candidate
              </button>
            </Link>
            <Link to="/signup">
              <button
                type="button"
                className="bg-white border-2 border-[#009986] text-[#009986] font-bold text-lg px-8 py-3 rounded-2xl hover:bg-[#e5e4e2] transition-colors w-full sm:w-auto"
              >
                I&apos;m a Recruiter
              </button>
            </Link>
          </div>
        </div>

        {/* Robot Image */}
        <div className="flex-shrink-0">
          <img
            src={robotIcon}
            alt="AI Interview Assistant"
            className="w-48 sm:w-64 md:w-72 lg:w-80"
          />
        </div>
      </section>

      {/* ── FEATURES SECTION ── */}
      <section
        aria-labelledby="features-heading"
        className="px-6 pb-20 max-w-7xl mx-auto w-full"
      >
        <div className="bg-white rounded-[80px] md:rounded-[120px] px-6 py-12 md:py-16">
          <h2
            id="features-heading"
            className="text-2xl sm:text-3xl md:text-4xl font-bold text-[#494949] text-center mb-24 mt-0"
          >
            The Future of Talent Assessment
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 max-w-4xl mx-auto">
            {featureCards.map((card) => (
              <article
                key={card.title}
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
          © 2026 Interview Me. All rights reserved.
        </p>
      </footer>
    </div>
  );
};