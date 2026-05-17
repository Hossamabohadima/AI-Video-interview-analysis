/**
 * api.js — Service Layer
 *
 * All data fetching lives here. Pages and hooks never call fetch() directly.
 * When the real backend is ready, only this file needs to change.
 *
 * Pattern:
 * - Each function returns a Promise
 * - Mock data is returned now, real API calls replace it later
 * - Error handling is centralized here
 */

// ── BASE CONFIG (swap this when backend is ready) ─────────────────────────────

const BASE_URL = process.env.REACT_APP_API_URL || "";
const IS_MOCK  = !BASE_URL; // automatically uses mock when no API URL is set

// ── GENERIC FETCH WRAPPER ─────────────────────────────────────────────────────

/**
 * Centralized fetch with error handling.
 * All real API calls go through this.
 */
const request = async (endpoint, options = {}) => {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `Request failed: ${response.status}`);
  }

  return response.json();
};

// ── MOCK DATA ─────────────────────────────────────────────────────────────────

const MOCK_USER = {
  id:       "u-001",
  name:     "Sarah Ahmed",
  role:     "Recruiter Admin",
  initials: "SA",
  email:    "sarah@interviewme.com",
};

const MOCK_CANDIDATES = [
  { id: 1,  name: "Abubaker", scores: [100, 100, 100, 100, 100] },
  { id: 2,  name: "Ahmed",    scores: [88,  91,  94,  90,  96]  },
  { id: 3,  name: "Mohamed",  scores: [80,  85,  82,  88,  86]  },
  { id: 4,  name: "Farouk",   scores: [82,  78,  75,  84,  80]  },
  { id: 5,  name: "Mahmoud",  scores: [74,  79,  76,  80,  76]  },
  { id: 6,  name: "Khalid",   scores: [74,  67,  75,  68,  70]  },
  { id: 7,  name: "Lina",     scores: [76,  60,  72,  58,  60]  },
  { id: 8,  name: "Aisha",    scores: [71,  47,  50,  60,  76]  },
  { id: 9,  name: "Omar",     scores: [60,  55,  58,  62,  50]  },
  { id: 10, name: "Nour",     scores: [45,  50,  48,  52,  46]  },
  { id: 11, name: "Yara",     scores: [38,  42,  40,  35,  44]  },
  { id: 12, name: "Kareem",   scores: [30,  28,  35,  32,  25]  },
];

const MOCK_BATCHES = [
  {
    id:           1,
    role:         "Senior Frontend Engineer",
    batchSize:    300,
    date:         "2026/04/22",
    passed:       40,
    avgScore:     65,
    topScore:     "92%",
    timeSavedHrs: 48,
  },
  {
    id:           2,
    role:         "Junior Backend Developer",
    batchSize:    290,
    date:         "2026/03/12",
    passed:       29,
    avgScore:     54,
    topScore:     "72%",
    timeSavedHrs: 40,
  },
  {
    id:           3,
    role:         "Machine Learning Senior",
    batchSize:    350,
    date:         "2026/04/22",
    passed:       40,
    avgScore:     65,
    topScore:     "92%",
    timeSavedHrs: 35,
  },
  {
    id:           4,
    role:         "DevOps Developer",
    batchSize:    311,
    date:         "2026/03/12",
    passed:       29,
    avgScore:     54,
    topScore:     "72%",
    timeSavedHrs: 30,
  },
];

// Simulate network delay for realistic mock behavior
const mockDelay = (ms = 300) => new Promise((res) => setTimeout(res, ms));

// ── AUTH SERVICES ─────────────────────────────────────────────────────────────

/**
 * Log in a user.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ user, token }>}
 */
export const login = async (email, password) => {
  if (IS_MOCK) {
    await mockDelay();
    if (email && password) {
      return { user: MOCK_USER, token: "mock-token-123" };
    }
    throw new Error("Invalid credentials");
  }

  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
};

/**
 * Sign up a new user.
 * @param {object} userData - { fullName, email, phone, password, userType }
 * @returns {Promise<{ user, token }>}
 */
export const signUp = async (userData) => {
  if (IS_MOCK) {
    await mockDelay();
    return { user: { ...MOCK_USER, ...userData }, token: "mock-token-123" };
  }

  return request("/auth/signup", {
    method: "POST",
    body: JSON.stringify(userData),
  });
};

/**
 * Log out the current user.
 */
export const logout = async () => {
  if (IS_MOCK) {
    await mockDelay(100);
    return { success: true };
  }

  return request("/auth/logout", { method: "POST" });
};

/**
 * Get the currently authenticated user.
 * @returns {Promise<user>}
 */
export const getCurrentUser = async () => {
  if (IS_MOCK) {
    await mockDelay(200);
    return MOCK_USER;
  }

  return request("/auth/me");
};

// ── CANDIDATE SERVICES ────────────────────────────────────────────────────────

/**
 * Get all candidates for a specific batch.
 * @param {string|number} batchId
 * @returns {Promise<Array>}
 */
export const getCandidatesByBatch = async (batchId) => {
  if (IS_MOCK) {
    await mockDelay();
    return MOCK_CANDIDATES;
  }

  return request(`/batches/${batchId}/candidates`);
};

// ── BATCH / REPORT SERVICES ───────────────────────────────────────────────────

/**
 * Get all batches (for history page).
 * @returns {Promise<Array>}
 */
export const getBatches = async () => {
  if (IS_MOCK) {
    await mockDelay();
    return MOCK_BATCHES;
  }

  return request("/batches");
};

/**
 * Get a single batch report by ID.
 * @param {string|number} batchId
 * @returns {Promise<object>}
 */
export const getBatchReport = async (batchId) => {
  if (IS_MOCK) {
    await mockDelay();
    return MOCK_BATCHES.find((b) => b.id === batchId) ?? MOCK_BATCHES[0];
  }

  return request(`/batches/${batchId}/report`);
};

/**
 * Get dashboard overview stats.
 * @returns {Promise<object>}
 */
export const getDashboardStats = async () => {
  if (IS_MOCK) {
    await mockDelay();
    return {
      totalCandidates: 1260,
      passedThreshold: 40,
      avgAiMatchScore: 72,
      timeSavedHrs:    153,
    };
  }

  return request("/dashboard/stats");
};