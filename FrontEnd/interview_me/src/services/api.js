/**
 * api.js — Service Layer
 * All API calls live here. Pages never call fetch() directly.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// ── HELPERS ───────────────────────────────────────────────────────────────────

const getToken = () =>
  localStorage.getItem("access_token") || localStorage.getItem("token");

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

export const logoutApi = async () => {
  return request("/users/auth/logout", { method: "POST" });
};

export const forgotPassword = async (email) => {
  return request("/users/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
};

export const resetPassword = async (token, newPassword) => {
  return request("/users/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
  });
};

// ── REPORTS ───────────────────────────────────────────────────────────────────

export const getReports = async () => {
  return request("/users/reports");
};

export const compareReports = async (video1, video2) => {
  return request(`/users/reports/compare?video1=${video1}&video2=${video2}`, {
    method: "POST",
  });
};

// ── THRESHOLD ─────────────────────────────────────────────────────────────────

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

export const getVideoScores = async (videoId) => {
  return request(`/scores/${videoId}`);
};

export const getMultipleVideoScores = async (videoIds) => {
  const results = await Promise.all(
    videoIds.map((id) => getVideoScores(id).catch(() => null))
  );
  return results.filter(Boolean);
};

export const getCandidatesByBatch = async (batchId) => {
  const scores = await getVideoScores(batchId);
  return [scores];
};

// ── METRIC WEIGHTS ────────────────────────────────────────────────────────────

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

export const getBatches = async () => {
  const { reports } = await getReports();
  if (!reports || reports.length === 0) return [];

  // Persistent map of videoId → role name
  const batchRoleMap = JSON.parse(localStorage.getItem("batchRoleMap") || "{}");

  const groups = {};

  reports.forEach((r) => {
    const date     = new Date(r.uploaddate);
    const roleName = batchRoleMap[String(r.videoid)] || "";

    // If video has a role name → group by "role_<roleName>_<date>"
    // so different batches with different role names never merge.
    // If no role name → group by exact minute as fallback.
    const key = roleName
      ? `role_${roleName}_${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
      : `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}-${date.getMinutes()}`;

    if (!groups[key]) {
      groups[key] = {
        batchKey:   key,
        batchRole:  roleName,
        date:       date.toLocaleDateString("en-CA").replace(/-/g, "/"),
        time:       date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        videoIds:   [],
        videoNames: [],
        scores:     [],
        statuses:   [],
      };
    }

    // If group doesn't have a role yet but this video does, assign it
    if (!groups[key].batchRole && roleName) {
      groups[key].batchRole = roleName;
    }

    // Clean candidate name — strip UUID and extension
    const cleanName = r.videoname
      .replace(/_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.*$/i, "")
      .replace(/_video$/, "")
      .trim();

    groups[key].videoIds.push(r.videoid);
    groups[key].videoNames.push(cleanName);
    groups[key].scores.push(r.total_score || 0);
    groups[key].statuses.push(r.status);
  });

  return Object.values(groups).map((batch) => {
    const avgScore  = Math.round(
      (batch.scores.reduce((a, b) => a + b, 0) / batch.scores.length) * 100
    );
    const topScore  = Math.round(Math.max(...batch.scores) * 100);
    const allDone   = batch.statuses.every((s) => s === "DONE");
    const anyFailed = batch.statuses.some((s) => s === "FAILED");

    return {
      batchKey:   batch.batchKey,
      batchRole:  batch.batchRole,
      date:       batch.date,
      time:       batch.time,
      videoIds:   batch.videoIds,
      videoNames: batch.videoNames,
      count:      batch.videoIds.length,
      avgScore,
      topScore:   `${topScore}%`,
      status:     anyFailed ? "FAILED" : allDone ? "DONE" : "PENDING",
      idsParam:   batch.videoIds.join(","),
    };
  }).sort((a, b) => new Date(b.date) - new Date(a.date));
};

export const getDashboardStats = async () => {
  const { reports } = await getReports();
  if (!reports || reports.length === 0) {
    return { totalCandidates: 0, passedThreshold: 0, avgAiMatchScore: 0, timeSavedHrs: 0 };
  }
  const totalCandidates = reports.length;
  const avgAiMatchScore = Math.round(
    (reports.reduce((sum, r) => sum + (r.total_score || 0), 0) / reports.length) * 100
  );
  return {
    totalCandidates,
    passedThreshold: 0,
    avgAiMatchScore,
    timeSavedHrs: Math.round(totalCandidates * 0.5),
  };
};