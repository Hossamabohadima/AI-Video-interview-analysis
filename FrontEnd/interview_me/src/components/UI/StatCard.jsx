/**
 * StatCard
 * Summary stat card used in dashboards and report pages.
 *
 * Props:
 * - title    (string): label above the value
 * - value    (string): main displayed number/text
 * - subtitle (string): small text below the value
 * - icon     (node):   optional icon element (dashboard variant)
 * - trend    (string): optional trend badge text e.g. "+12% this week"
 * - valueColor (string): optional Tailwind text color class
 * - topBorder  (bool): show teal top border (report variant)
 */
const StatCard = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  valueColor = "text-gray-900",
  topBorder = false,
}) => (
  <article
    className={`bg-white rounded-2xl p-5 shadow-sm flex flex-col justify-between min-h-[115px] hover:shadow-md transition-shadow ${
      topBorder ? "border-t-2 border-[#009986]" : ""
    }`}
  >
    <div className="flex items-start justify-between gap-2">
      <div className="space-y-1">
        <span className="text-xs font-bold text-gray-400 tracking-wide uppercase block">
          {title}
        </span>
        <span className={`text-2xl font-black block ${valueColor}`}>
          {value}
        </span>
      </div>
      {icon && <div className="shrink-0">{icon}</div>}
    </div>

    <div className="mt-3 flex flex-col gap-1">
      {subtitle && (
        <span className="text-xs font-semibold text-gray-400">{subtitle}</span>
      )}
      {trend && (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-50 text-teal-600 w-fit">
          {trend}
        </span>
      )}
    </div>
  </article>
);

export default StatCard;