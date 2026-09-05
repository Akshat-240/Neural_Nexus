/**
 * Central API client — single source for all fetch calls.
 * All pages import from here. No duplicated fetch logic.
 */

const BASE = "http://localhost:8000";

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

async function post(path, body) {
  const isForm = body instanceof FormData;
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: isForm ? undefined : { "Content-Type": "application/json" },
    body: isForm ? body : JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Schedule
  getActivities: () => get("/api/v1/activities"),

  // Events
  getEvents: () => get("/api/v1/events"),
  getEvent: (dbId) => get(`/api/v1/events/${dbId}`),

  // Reviews
  getReviews: () => get("/api/v1/reviews"),
  submitReview: (payload) => post("/api/v1/review", payload),

  // Dashboard
  getDashboard: () => get("/api/v1/dashboard"),

  // Insights
  getInsights: () => get("/api/v1/insights"),

  // Evidence
  getEvidence: (dbId) => get(`/api/v1/evidence/${dbId}`),

  // Process update (text + optional image file)
  processUpdate: (projectId, reportText, imageFile) => {
    const form = new FormData();
    form.append("project_id", projectId);
    form.append("report_text", reportText);
    if (imageFile) form.append("image", imageFile);
    return post("/api/v1/process-update", form);
  },

  // Voice
  transcribeVoice: (projectId, audioFile) => {
    const form = new FormData();
    form.append("project_id", projectId);
    form.append("audio", audioFile, "recording.webm");
    return post("/api/v1/voice/transcribe", form);
  },

  imageUrl: (path) => (path ? `${BASE}${path}` : null),
};
