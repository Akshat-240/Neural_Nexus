import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

export default function FieldEvents() {
  const [events, setEvents]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    api.getEvents()
      .then(d => { setEvents(d); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const total    = events.length;
  const verified = events.filter(e => e.pipeline_status === "verified").length;
  const review   = events.filter(e => e.review_required).length;
  const deviated = events.filter(e => e.pipeline_status === "deviation").length;

  const statusColor = (s) => {
    if (s === "verified") return "#16a34a";
    if (s === "pending_review") return "#d97706";
    if (s === "deviation") return "#ef4444";
    return "#64748b";
  };

  return (
    <div className="field-events">
      <div className="page-header">
        <div>
          <h1>Field Events</h1>
          <p>All field updates processed through the AI pipeline</p>
        </div>
        <button className="primary-btn" onClick={() => navigate("/field-capture")}>
          + New Event
        </button>
      </div>

      {/* Summary */}
      <div className="events-summary">
        {[
          { label: "Total Events", value: total },
          { label: "Verified", value: verified },
          { label: "Pending Review", value: review },
          { label: "Deviations", value: deviated },
        ].map(c => (
          <div className="summary-card" key={c.label}>
            <span>{c.label}</span>
            <h2>{c.value}</h2>
          </div>
        ))}
      </div>

      <div className="events-card">
        <div className="card-header">
          <h3>Event History</h3>
          <button onClick={load} style={{ fontSize: "0.85rem", color: "#3b82f6", background: "none", border: "none", cursor: "pointer" }}>↻ Refresh</button>
        </div>

        {loading && <p style={{ padding: "1rem", color: "#64748b" }}>Loading events…</p>}
        {error   && <p style={{ padding: "1rem", color: "red" }}>Error: {error}</p>}
        {!loading && !error && events.length === 0 && (
          <p style={{ padding: "1rem", color: "#64748b" }}>
            No field events yet. Submit a field update to create one.
          </p>
        )}

        {!loading && !error && events.length > 0 && (
          <div className="events-table">
            <div className="table-head">
              <span>Event ID</span>
              <span>Field Report</span>
              <span>Activity</span>
              <span>Confidence</span>
              <span>Status</span>
            </div>
            {events.map(ev => (
              <div
                className="table-row"
                key={ev.event_id}
                style={{ cursor: "pointer" }}
                onClick={() => navigate(`/evidence?event=${ev.db_id}`)}
              >
                <span className="event-id">{ev.event_id}</span>
                <span style={{ maxWidth: "260px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {ev.report_text}
                </span>
                <span>{ev.activity_id || "—"}</span>
                <span className="confidence">
                  {ev.confidence != null ? `${(ev.confidence * 100).toFixed(0)}%` : "—"}
                </span>
                <span style={{ color: statusColor(ev.pipeline_status), fontWeight: 600, textTransform: "capitalize" }}>
                  {ev.pipeline_status?.replace("_", " ") || "—"}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}