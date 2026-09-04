import React, { useEffect, useState } from "react";
import { api } from "../api/client";

function StatCard({ label, value, sub, warn }) {
  return (
    <div className="stat-card" style={{ borderLeft: warn ? "3px solid #ef4444" : undefined }}>
      <p>{label}</p>
      <h2>{value ?? "—"}</h2>
      {sub && <span>{sub}</span>}
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = () => {
    setLoading(true);
    api.getDashboard()
      .then(d => { setData(d); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  if (loading) return <div className="dashboard"><p style={{padding:"2rem"}}>Loading dashboard…</p></div>;
  if (error)   return <div className="dashboard"><p style={{padding:"2rem",color:"red"}}>Unable to load dashboard: {error}</p></div>;

  const progressPct = data.overall_progress_pct ?? 0;

  return (
    <div className="dashboard">
      <div className="top-header">
        <div>
          <h1>Project Control Center</h1>
          <p>Verified execution intelligence — North Processing Unit</p>
        </div>
        <div className="project-status">
          <span>PRJ-DEMO-01</span>
          <span className="live-badge">LIVE</span>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <StatCard label="Total Activities"   value={data.total_activities} />
        <StatCard label="In Progress"        value={data.in_progress} />
        <StatCard label="Pending Review"     value={data.pending_reviews} warn={data.pending_reviews > 0} />
        <StatCard label="Deviations"         value={data.deviations} warn={data.deviations > 0} />
      </div>

      {/* Overall progress bar */}
      <div className="dashboard-card" style={{ marginBottom: "1rem" }}>
        <h3>Overall Progress</h3>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginTop: "0.75rem" }}>
          <div style={{ flex: 1, height: "12px", background: "#e2e8f0", borderRadius: "6px", overflow: "hidden" }}>
            <div style={{ width: `${progressPct}%`, height: "100%", background: "#3b82f6", borderRadius: "6px", transition: "width 0.4s" }} />
          </div>
          <strong style={{ minWidth: "3rem", textAlign: "right" }}>{progressPct}%</strong>
        </div>
        <p style={{ marginTop: "0.5rem", color: "#64748b", fontSize: "0.85rem" }}>
          {data.completed} completed · {data.verified_events} verified events
        </p>
      </div>

      {/* Middle */}
      <div className="dashboard-grid">
        {/* Attention */}
        <div className="dashboard-card attention">
          <h3>Deviations</h3>
          {data.attention_items.length === 0
            ? <p style={{ color: "#64748b", marginTop: "0.5rem" }}>No deviations detected ✓</p>
            : data.attention_items.map(item => (
              <div className="attention-item" key={item.activity_id}>
                <div>
                  <b>{item.activity_id}</b>
                  <p>{item.activity_name}</p>
                </div>
                <span className="warning">{item.variance}pp</span>
              </div>
            ))
          }
        </div>

        {/* Recent verified */}
        <div className="dashboard-card">
          <h3>Recently Verified</h3>
          {data.recent_verified.length === 0
            ? <p style={{ color: "#64748b", marginTop: "0.5rem" }}>No verified events yet</p>
            : (
              <div className="activity-table">
                <div className="table-header">
                  <span>Event</span>
                  <span>Activity</span>
                  <span>Confidence</span>
                </div>
                {data.recent_verified.map(r => (
                  <div className="table-row" key={r.event_id}>
                    <span>{r.event_id}</span>
                    <span>{r.activity_id}</span>
                    <span>{r.confidence ? `${(r.confidence * 100).toFixed(0)}%` : "—"}</span>
                  </div>
                ))}
              </div>
            )
          }
        </div>
      </div>

      <div style={{ textAlign: "right", marginTop: "0.5rem" }}>
        <button onClick={load} style={{ fontSize: "0.8rem", color: "#64748b", background: "none", border: "none", cursor: "pointer" }}>
          ↻ Refresh
        </button>
      </div>
    </div>
  );
}