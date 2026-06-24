/**
 * api.js — Service Layer
 * All API calls live here. Pages never call fetch() directly.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// ── HELPERS ───────────────────────────────────────────────────────────────────

const getToken = () => localStorage.getItem("access_token") || localStorage.getItem("token");

const request = async (endpoint, options = {}) => {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };
  const response = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
};

const requestFormData = async (endpoint, formData) => {
  const token = getToken();
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Upload failed: ${response.status}`);
  }
  return response.json();
};

// ── AUTH ──────────────────────────────────────────────────────────────────────

export const signUp = async (userData) => {
  return request("/users/auth/signup", {
    method: "POST",
    body: JSON.stringify({
      name:         userData.name,
      email:        userData.email,
      password:     userData.password,
      phone_number: userData.phone_number || null,
      role:         userData.role || "USER",
    }),
  });
};

export const login = async ({ email, password }) => {
  return request("/users/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
};

// ── REPORTS ───────────────────────────────────────────────────────────────────

/**
 * Get all video reports for the authenticated user.
 * GET /users/reports
 * Returns: { reports: [{ videoid, uploaddate, duration, status, videoname,
 *   fillers_score, pause_rate_score, emotion_score, energy_score,
 *   eye_contact_score, grammar_score, total_score }] }
 */
export const getReports = async () => {
  return request("/users/reports");
};

export const compareReports = async (video1, video2) => {
  return request(`/users/reports/compare?video1=${video1}&video2=${video2}`, {
    method: "POST",
  });
};

// ── THRESHOLD ─────────────────────────────────────────────────────────────────

/**
 * Update pass threshold.
 * Frontend sends 0–100, divided by 100 here → backend receives 0.0–1.0
 */
export const updateThreshold = async (scorePercent) => {
  const score = scorePercent / 100;
  return request(`/users/threshold?score=${score}`, { method: "PUT" });
};

// ── VIDEOS ────────────────────────────────────────────────────────────────────

export const uploadVideos = async (files, videoNames, weights) => {
  const formData = new FormData();
  files.forEach((file)      => formData.append("files",        file));
  videoNames.forEach((name) => formData.append("video_names",  name));
  formData.append("fillers_weight",     weights.fillers_weight);
  formData.append("pause_rate_weight",  weights.pause_rate_weight);
  formData.append("emotion_weight",     weights.emotion_weight);
  formData.append("energy_weight",      weights.energy_weight);
  formData.append("eye_contact_weight", weights.eye_contact_weight);
  formData.append("grammar_weight",     weights.grammar_weight);
  return requestFormData("/users/videos/upload", formData);
};

// ── SCORES ────────────────────────────────────────────────────────────────────

/**
 * Get scores for a single video.
 * GET /scores/{video_id}
 * Returns all scores as 0.0–1.0 floats.
 */
export const getVideoScores = async (videoId) => {
  return request(`/scores/${videoId}`);
};

/**
 * Get scores for multiple videos at once.
 * Fetches each video's scores in parallel.
 * @param {number[]} videoIds
 * @returns {Promise<Array>} array of score objects with video metadata
 */
export const getMultipleVideoScores = async (videoIds) => {
  const results = await Promise.all(
    videoIds.map((id) => getVideoScores(id).catch(() => null))
  );
  return results.filter(Boolean); // remove any failed fetches
};

export const getMetricWeights = async () => {
  return request("/metrics/weights");
};

export const setMetricWeights = async (weights) => {
  return request("/metrics/weights", {
    method: "PUT",
    body: JSON.stringify(weights),
  });
};

// ── DERIVED DATA ──────────────────────────────────────────────────────────────

/**
 * Get all reports and group them by upload batch.
 * Since the backend has no batch_id, we group by upload minute —
 * videos uploaded within the same minute = same batch.
 *
 * Returns array of batches:
 * [{
 *   batchKey: "2026-06-12T10:30",
 *   date: "2026/06/12",
 *   time: "10:30",
 *   videoIds: [1, 2, 3, 4],
 *   videoNames: ["Ahmed", "Sara", "Omar", "Lina"],
 *   count: 4,
 *   avgScore: 72,
 *   status: "DONE"
 * }]
 */
export const getBatches = async () => {
  const { reports } = await getReports();
  if (!reports || reports.length === 0) return [];

  // Group by upload minute
  const groups = {};
  reports.forEach((r) => {
    const date= new Date(r.uploaddate);
    // const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}-${date.getMinutes()}`;
    const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
    if (!groups[key]) {
      groups[key] = {
        batchKey:   key,
        date:       date.toLocaleDateString("en-CA").replace(/-/g, "/"),
        time:       date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        videoIds:   [],
        videoNames: [],
        scores:     [],
        statuses:   [],
      };
    }

    groups[key].videoIds.push(r.videoid);
    // groups[key].videoNames.push(r.videoname);
    const cleanName = r.videoname.replace(/_[0-9a-f-]{36}\.[^.]+$/, "");
    groups[key].videoNames.push(cleanName);
    groups[key].scores.push(r.total_score || 0);
    groups[key].statuses.push(r.status);
  });

  // Convert to array and calculate batch-level stats
  return Object.values(groups).map((batch) => {
    const avgScore  = Math.round(
      (batch.scores.reduce((a, b) => a + b, 0) / batch.scores.length) * 100
    );
    const topScore  = Math.round(Math.max(...batch.scores) * 100);
    const allDone   = batch.statuses.every((s) => s === "DONE");
    const anyFailed = batch.statuses.some((s) => s === "FAILED");

    return {
      batchKey:   batch.batchKey,
      date:       batch.date,
      time:       batch.time,
      videoIds:   batch.videoIds,
      videoNames: batch.videoNames,
      count:      batch.videoIds.length,
      avgScore,
      topScore:   `${topScore}%`,
      status:     anyFailed ? "FAILED" : allDone ? "DONE" : "PENDING",
      // pass IDs as comma-separated string for URL
      idsParam:   batch.videoIds.join(","),
    };
  }).sort((a, b) => new Date(b.date) - new Date(a.date)); // newest first
};