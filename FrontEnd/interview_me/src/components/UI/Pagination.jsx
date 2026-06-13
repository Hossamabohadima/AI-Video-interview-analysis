/**
 * Pagination
 * Reusable pagination controls — works with usePagination hook.
 *
 * Props:
 * - currentPage (number)
 * - totalPages  (number)
 * - hasNext     (bool)
 * - hasPrev     (bool)
 * - onNext      (fn)
 * - onPrev      (fn)
 * - onGoTo      (fn): called with page number
 * - label       (string): optional accessible label, default "Pagination"
 * - summary     (string): optional left-side text e.g. "Page 1 of 3"
 */

const ChevronLeft = () => (
  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

const ChevronRight = () => (
  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const Pagination = ({
  currentPage,
  totalPages,
  hasNext,
  hasPrev,
  onNext,
  onPrev,
  onGoTo,
  label = "Pagination",
  summary,
}) => (
  <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between flex-wrap gap-3">
    {summary && (
      <span className="text-xs text-gray-400">{summary}</span>
    )}

    <nav className="flex items-center gap-2 ml-auto" aria-label={label}>
      {/* Prev */}
      <button
        type="button"
        disabled={!hasPrev}
        onClick={onPrev}
        aria-label="Previous page"
        className="w-8 h-8 flex items-center justify-center bg-white rounded-lg border border-gray-200 text-gray-500 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50 transition-all"
      >
        <ChevronLeft />
      </button>

      {/* Page numbers */}
      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
        <button
          key={page}
          type="button"
          onClick={() => onGoTo(page)}
          aria-current={page === currentPage ? "page" : undefined}
          className={`w-8 h-8 rounded-lg text-sm font-semibold transition-all ${
            page === currentPage
              ? "bg-[#009986] text-white shadow-sm"
              : "text-gray-500 hover:bg-gray-100"
          }`}
        >
          {page}
        </button>
      ))}

      {/* Next */}
      <button
        type="button"
        disabled={!hasNext}
        onClick={onNext}
        aria-label="Next page"
        className="w-8 h-8 flex items-center justify-center bg-white rounded-lg border border-gray-200 text-gray-500 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50 transition-all"
      >
        <ChevronRight />
      </button>
    </nav>
  </div>
);

export default Pagination;