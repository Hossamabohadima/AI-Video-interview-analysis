import { useState, useMemo } from "react";

/**
 * Manages pagination logic for any list.
 * @param {Array}  items        - full list to paginate
 * @param {number} itemsPerPage - how many items per page
 *
 * Returns:
 * - paginated    : current page's slice of items
 * - currentPage  : active page number (1-based)
 * - totalPages   : total number of pages
 * - goTo(n)      : jump to page n
 * - next()       : go to next page
 * - prev()       : go to previous page
 * - resetPage()  : jump back to page 1 (call when filter/sort changes)
 * - hasNext      : boolean
 * - hasPrev      : boolean
 */
const usePagination = (items, itemsPerPage = 5) => {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(items.length / itemsPerPage));

  // Keep current page in valid range when items change
  const safePage = Math.min(currentPage, totalPages);

  const paginated = useMemo(
    () => items.slice((safePage - 1) * itemsPerPage, safePage * itemsPerPage),
    [items, safePage, itemsPerPage]
  );

  const goTo      = (n)  => setCurrentPage(Math.min(Math.max(1, n), totalPages));
  const next      = ()   => goTo(safePage + 1);
  const prev      = ()   => goTo(safePage - 1);
  const resetPage = ()   => setCurrentPage(1);

  return {
    paginated,
    currentPage: safePage,
    totalPages,
    goTo,
    next,
    prev,
    resetPage,
    hasNext: safePage < totalPages,
    hasPrev: safePage > 1,
  };
};

export default usePagination;