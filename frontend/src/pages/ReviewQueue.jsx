import React, { useEffect, useState } from "react";
import { api } from "../api/client";

function ReviewCard({ review, activities, onDecision }) {
  const [correctedId, setCorrectedId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (decision) => {
    if (decision === "correct" && !correctedId) {
      alert("Select an activity to correct to.");
      return;
    }
    setSubmitting(true);
    try {
      await onDecision(review.db_id, decision, decision === "correct" ? correctedId : undefined);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{
      background: "#fff", border: "1px solid #e2e8f0", borderRadius: "8px",
      padding: "1.5rem", marginBottom: "1.5rem", borderLeft: "4px solid #f59e0b"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.75rem" }}>
        <strong style={{ color: "#0f172a" }}>{review.event_id}</strong>
        <span style={{ fontSize: "0.8rem", background: "#fef3c7", color: "#92400e", padding: "0.2rem 0.6rem", borderRadius: "4px" }}>
          Pending Review
        </span>
      </div>

      <div style={{ background: "#f8fafc", borderRadius: "6px", padding: "1rem", marginBottom: "1rem", fontStyle: "italic", color: "#334155" }}>
        "{review.report_text}"
      </div>

      <div style={{ marginBottom: "0.5rem", fontSize: "0.85rem", color: "#64748b" }}>
        <strong>Proposed match:</strong> {review.proposed_activity_id} — {review.proposed_activity_name}
        &nbsp;({review.confidence != null ? `${(review.confidence * 100).toFixed(0)}% confidence` : "—"})
      </div>

      <div style={{ marginBottom: "0.5rem", fontSize: "0.85rem", color: "#ef4444" }}>
        <strong>Reason:</strong> {review.reason}
      </div>

      {/* Correct: pick a different activity */}
      <div style={{ marginTop: "1rem" }}>
        <label style={{ fontSize: "0.85rem", color: "#475569", display: "block", marginBottom: "0.25rem" }}>
          Correct to activity:
        </label>
        <select
          value={correctedId}
          onChange={e => setCorrectedId(e.target.value)}
          style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "0.9rem" }}
        >
          <option value="">— keep proposed —</option>
          {activities.map(a => (
            <option key={a.activity_id} value={a.activity_id}>
              {a.activity_id} · {a.activity_name}
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.25rem" }}>
        <button
          disabled={submitting}
          onClick={() => submit("approve")}
          style={{ flex: 1, padding: "0.6rem", background: "#16a34a", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600 }}
        >
          Approve
        </button>
        <button
          disabled={submitting || !correctedId}
          onClick={() => submit("correct")}
          style={{ flex: 1, padding: "0.6rem", background: "#3b82f6", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600, opacity: correctedId ? 1 : 0.5 }}
        >
          Correct Match
        </button>
        <button
          disabled={submitting}
          onClick={() => submit("reject")}
          style={{ flex: 1, padding: "0.6rem", background: "white", color: "#ef4444", border: "1px solid #ef4444", borderRadius: "6px", cursor: "pointer", fontWeight: 600 }}
        >
          Reject
        </button>
      </div>
    </div>
  );
}

export default function ReviewQueue() {
  const [reviews, setReviews]     = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const load = () => {
    setLoading(true);
    Promise.all([api.getReviews(), api.getActivities()])
      .then(([r, a]) => { setReviews(r); setActivities(a); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDecision = async (dbId, decision, activityId) => {
    await api.submitReview({ db_id: dbId, decision, activity_id: activityId });
    load(); // Refresh queue after decision
  };

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "2rem" }}>
        <div>
          <h1>Review Queue</h1>
          <p style={{ color: "#64748b" }}>Human-in-the-loop verification for ambiguous field events</p>
        </div>
        <button onClick={load} style={{ fontSize: "0.85rem", color: "#3b82f6", background: "none", border: "1px solid #3b82f6", borderRadius: "4px", padding: "0.4rem 0.8rem", cursor: "pointer" }}>
          ↻ Refresh
        </button>
      </div>

      {loading && <p style={{ color: "#64748b" }}>Loading review queue…</p>}
      {error   && <p style={{ color: "red" }}>Error: {error}</p>}
      {!loading && !error && reviews.length === 0 && (
        <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px", padding: "1.5rem", textAlign: "center" }}>
          <div style={{ fontSize: "1.5rem" }}>✓</div>
          <h3 style={{ color: "#16a34a", margin: "0.5rem 0" }}>Queue is clear</h3>
          <p style={{ color: "#64748b" }}>All field events have been resolved.</p>
        </div>
      )}
      {!loading && !error && reviews.map(r => (
        <ReviewCard
          key={r.event_id}
          review={r}
          activities={activities}
          onDecision={handleDecision}
        />
      ))}
    </div>
  );
}