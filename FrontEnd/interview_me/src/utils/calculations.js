// ── GENERIC HELPERS ───────────────────────────────────────────────────────────

/**
 * Calculate the simple average of a number array.
 * Returns 0 for empty arrays.
 */
export const avg = (arr) =>
  arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : 0;

/**
 * Clamp a number between min and max.
 */
export const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

/**
 * Format a number as a percentage string. e.g. 72 → "72%"
 */
export const toPercent = (value) => `${value}%`;

/**
 * Calculate percentage ratio of part over total.
 * Returns "0.0" for zero total to avoid division by zero.
 */
export const calcRate = (part, total) =>
  total ? ((part / total) * 100).toFixed(1) : "0.0";

// ── CANDIDATE CALCULATIONS ────────────────────────────────────────────────────

/**
 * Enrich raw candidates with:
 * - overall: simple average of all module scores
 * - rank: position after sorting by overall descending
 * - status: "PASS" if overall >= threshold, else "FAIL"
 */
export const enrichCandidates = (rawCandidates, threshold) =>
  rawCandidates
    .map((c) => ({ ...c, overall: avg(c.scores) }))
    .sort((a, b) => b.overall - a.overall)
    .map((c, i) => ({
      ...c,
      rank:   i + 1,
      status: c.overall >= threshold ? "PASS" : "FAIL",
    }));

/**
 * Calculate batch-level summary stats from enriched candidates.
 * All numbers here are derived — nothing is hardcoded.
 */
export const calcBatchStats = (candidates) => {
  const total        = candidates.length;
  const passed       = candidates.filter((c) => c.status === "PASS");
  const batchAvg     = avg(candidates.map((c) => c.overall));
  const top          = candidates[0]; // already sorted descending
  const passRate     = calcRate(passed.length, total);
  const failRate     = calcRate(total - passed.length, total);

  return {
    total,
    passedCount: passed.length,
    failedCount: total - passed.length,
    passRate,
    failRate,
    batchAvg,
    topScore: top?.overall ?? 0,
    topName:  top?.name    ?? "—",
  };
};

/**
 * Calculate average score per module across all candidates.
 * @param {Array} candidates - enriched candidates
 * @param {Array} moduleLabels - label for each score index
 */
export const calcModuleAverages = (candidates, moduleLabels) =>
  moduleLabels.map((label, i) => ({
    label,
    value: avg(candidates.map((c) => c.scores[i])),
  }));

/**
 * Distribute candidate overall scores into buckets:
 * 0–20, 20–40, 40–60, 60–80, 80–100
 */
export const calcScoreDistribution = (candidates) => {
  const BUCKET_LABELS = ["0–20", "20–40", "40–60", "60–80", "80–100"];
  const buckets = [0, 0, 0, 0, 0];

  candidates.forEach(({ overall }) => {
    const idx = clamp(Math.floor(overall / 20), 0, 4);
    buckets[idx]++;
  });

  return BUCKET_LABELS.map((range, i) => ({ range, count: buckets[i] }));
};

// ── DASHBOARD STAT CALCULATIONS ───────────────────────────────────────────────

/**
 * Calculate recruiter dashboard overview stats from a list of batches.
 * Each batch: { candidates: [], passed: number, timeSavedHrs: number }
 */
export const calcDashboardStats = (batches) => {
  const totalCandidates = batches.reduce((sum, b) => sum + b.candidates.length, 0);
  const totalPassed     = batches.reduce((sum, b) => sum + b.passed, 0);
  const allScores       = batches.flatMap((b) => b.candidates.map((c) => c.overall));
  const avgScore        = avg(allScores);
  const timeSaved       = batches.reduce((sum, b) => sum + b.timeSavedHrs, 0);

  return { totalCandidates, totalPassed, avgScore, timeSaved };
};