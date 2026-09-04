import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

function ReviewCard({ review, activities, onDecision }) {
  const [correctedId, setCorrectedId] = useState(review.proposed_activity_id || "");
  const [submitting,  setSubmitting]  = useState(false);

  const submit = async (decision) => {
    if (decision === "correct" && !correctedId) {
      alert("Select a different activity to correct to.");
      return;
    }
    setSubmitting(true);
    try {
      await onDecision(review.db_id, decision, correctedId || undefined);
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
        <strong style={{ color: "#0f172a", fontSize: "1rem" }}>{review.event_id}</strong>
        <span style={{ fontSize: "0.8rem", background: "#fef3c7", color: "#92400e", padding: "0.2rem 0.6rem", borderRadius: "4px", fontWeight: 600 }}>
          Pending Review
        </span>
      </div>

      <div style={{ background: "#f8fafc", borderRadius: "6px", padding: "0.85rem 1rem", marginBottom: "1rem", fontStyle: "italic", color: "#334155", borderLeft: "3px solid #f59e0b" }}>
        "{review.report_text}"
      </div>

      <div style={{ marginBottom: "0.4rem", fontSize: "0.9rem" }}>
        <span style={{ color: "#64748b" }}>Proposed match: </span>
        <strong>{review.proposed_activity_id}</strong>
        {review.proposed_activity_name && ` — ${review.proposed_activity_name}`}
        {review.confidence != null && (
          <span style={{ color: "#d97706", marginLeft: "0.5rem" }}>
            ({Math.round(review.confidence * 100)}% confidence)
          </span>
        )}
      </div>

      <div style={{ marginBottom: "1rem", fontSize: "0.85rem", color: "#ef4444" }}>
        ⚠ {review.reason}
      </div>

      {/* Correct to a different activity */}
      <div>
        <label style={{ fontSize: "0.85rem", color: "#475569", display: "block", marginBottom: "0.35rem", fontWeight: 600 }}>
          Select activity:
        </label>
        <select
          value={correctedId}
          onChange={e => setCorrectedId(e.target.value)}
          style={{ width: "100%", padding: "0.55rem", border: "1px solid #cbd5e1", borderRadius: "5px", fontSize: "0.9rem", background: "#fff" }}
        >
          <option value="">— no change (approve proposed) —</option>
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
          style={{ flex: 1, padding: "0.65rem", background: "#16a34a", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 700 }}
        >
          ✓ Approve
        </button>
        <button
          disabled={submitting || !correctedId || correctedId === review.proposed_activity_id}
          onClick={() => submit("correct")}
          style={{
            flex: 1, padding: "0.65rem", background: "#3b82f6", color: "white",
            border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 700,
            opacity: (correctedId && correctedId !== review.proposed_activity_id) ? 1 : 0.4
          }}
        >
          ✎ Correct Match
        </button>
        <button
          disabled={submitting}
          onClick={() => submit("reject")}
          style={{ flex: 1, padding: "0.65rem", background: "white", color: "#ef4444", border: "1px solid #ef4444", borderRadius: "6px", cursor: "pointer", fontWeight: 700 }}
        >
          ✕ Reject
        </button>
      </div>
    </div>
  );
}

export default function ReviewQueue() {
  const [reviews,    setReviews]    = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const [decided,    setDecided]    = useState(null);  // { decision, activityId }
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    setDecided(null);
    Promise.all([api.getReviews(), api.getActivities()])
      .then(([r, a]) => { setReviews(r); setActivities(a); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDecision = async (dbId, decision, activityId) => {
    await api.submitReview({ db_id: dbId, decision, activity_id: activityId });
    const decidedAct = activities.find(a => a.activity_id === activityId);
    setDecided({ decision, activityId, activityName: decidedAct?.activity_name });
    load();
  };

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "2rem" }}>
        <div>
          <h1>Review Queue</h1>
          <p style={{ color: "#64748b" }}>Human-in-the-loop — ambiguous field events awaiting your decision</p>
        </div>
        <button
          onClick={load}
          style={{ fontSize: "0.85rem", color: "#3b82f6", background: "none", border: "1px solid #3b82f6", borderRadius: "4px", padding: "0.4rem 0.8rem", cursor: "pointer" }}
        >
          ↻ Refresh
        </button>
      </div>

      {/* Post-decision success banner */}
      {decided && (
        <div style={{
          background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px",
          padding: "1.25rem 1.5rem", marginBottom: "1.5rem",
          display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap"
        }}>
          <div>
            <div style={{ fontWeight: 700, color: "#16a34a", marginBottom: "0.25rem" }}>
              ✓ Decision recorded — {decided.decision === "reject" ? "Event rejected" : `Verified as ${decided.activityId}`}
            </div>
            {decided.activityName && (
              <div style={{ color: "#475569", fontSize: "0.9rem" }}>{decided.activityName}</div>
            )}
            {decided.decision !== "reject" && (
              <div style={{ fontSize: "0.85rem", color: "#16a34a", marginTop: "0.2rem" }}>
                Schedule has been updated in the database.
              </div>
            )}
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button
              onClick={() => navigate("/schedule")}
              style={{ padding: "0.55rem 1.1rem", background: "#16a34a", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600, fontSize: "0.9rem" }}
            >
              View Schedule →
            </button>
            {decided.decision !== "reject" && (
              <button
                onClick={() => navigate("/insights")}
                style={{ padding: "0.55rem 1.1rem", background: "white", color: "#475569", border: "1px solid #cbd5e1", borderRadius: "6px", cursor: "pointer", fontSize: "0.9rem" }}
              >
                View Insights
              </button>
            )}
          </div>
        </div>
      )}

      {loading && <p style={{ color: "#64748b" }}>Loading review queue…</p>}
      {error   && <p style={{ color: "red" }}>Error: {error}</p>}

      {!loading && !error && reviews.length === 0 && !decided && (
        <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px", padding: "2rem", textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>✓</div>
          <h3 style={{ color: "#16a34a", margin: "0 0 0.5rem" }}>Queue is clear</h3>
          <p style={{ color: "#64748b" }}>All field events have been resolved. Submit an ambiguous update to generate a review item.</p>
          <button
            onClick={() => navigate("/field-capture")}
            style={{ marginTop: "1rem", padding: "0.55rem 1.2rem", background: "#16a34a", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600 }}
          >
            Submit a Field Update
          </button>
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