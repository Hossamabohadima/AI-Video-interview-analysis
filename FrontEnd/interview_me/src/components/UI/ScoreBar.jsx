/**
 * ScoreBar
 * Displays a labeled progress bar for a score value.
 *
 * Props:
 * - value (number): score 0–100
 * - color (string): optional Tailwind bg class, defaults to brand teal
 */
const ScoreBar = ({ value, color = "bg-[#009986]" }) => (
  <div className="flex items-center gap-3">
    <span className="text-sm font-semibold text-[#009986] w-10 text-right">
      {value}%
    </span>
    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
      <div
        className={`h-full ${color} rounded-full transition-all duration-500`}
        style={{ width: `${value}%` }}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={100}
      />
    </div>
  </div>
);

export default ScoreBar;