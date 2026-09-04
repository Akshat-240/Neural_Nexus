import React, { useEffect, useState } from "react";
import { api } from "../api/client";

function BarChart({ planned, actual }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", marginTop: "0.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <span style={{ width: "60px", fontSize: "0.8rem", color: "#64748b" }}>Planned</span>
        <div style={{ flex: 1, height: "8px", background: "#e2e8f0", borderRadius: "4px" }}>
          <div style={{ width: `${planned}%`, height: "100%", background: "#94a3b8", borderRadius: "4px" }} />
        </div>
        <span style={{ width: "36px", fontSize: "0.8rem", textAlign: "right" }}>{planned}%</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <span style={{ width: "60px", fontSize: "0.8rem", color: "#64748b" }}>Actual</span>
        <div style={{ flex: 1, height: "8px", background: "#e2e8f0", borderRadius: "4px" }}>
          <div style={{ width: `${actual}%`, height: "100%", background: "#ef4444", borderRadius: "4px" }} />
        </div>
        <span style={{ width: "36px", fontSize: "0.8rem", textAlign: "right" }}>{actual}%</span>
      </div>
    </div>
  );
}

export default function Insights() {
  const [insights, setInsights] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  const load = () => {
    setLoading(true);
    Promise.all([api.getInsights(), api.getDashboard()])
      .then(([ins, dash]) => { setInsights(ins); setDashboard(dash); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="insights-page">
      <div className="insights-header">
        <div>
          <div className="unit-row">
            <span>North Processing Unit</span>
            <span className="live-badge">LIVE</span>
          </div>
          <h1>Execution Insights</h1>
          <p>Deviations calculated from verified field events vs. planned schedule</p>
        </div>
        <button onClick={load} style={{ fontSize: "0.85rem", color: "#64748b", background: "none", border: "1px solid #cbd5e1", borderRadius: "4px", padding: "0.4rem 0.8rem", cursor: "pointer" }}>
          ↻ Refresh
        </button>
      </div>

      {loading && <p style={{ padding: "1rem", color: "#64748b" }}>Loading insights…</p>}
      {error   && <p style={{ padding: "1rem", color: "red" }}>Error: {error}</p>}

      {!loading && !error && dashboard && (
        <div className="insights-overview">
          <section className="progress-card">
            <h2>Progress Health</h2>
            <p className="section-subtitle">Overall verified progress</p>
            <div className="progress-number">{dashboard.overall_progress_pct}%</div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${dashboard.overall_progress_pct}%` }} />
            </div>
            <p className="progress-caption">
              {dashboard.completed} completed · {dashboard.in_progress} in progress
            </p>
          </section>

          <section className="watchlist-card">
            <h2>Deviation Watchlist</h2>
            {insights.length === 0
              ? <p style={{ color: "#64748b", marginTop: "0.5rem" }}>No deviations detected ✓</p>
              : (
                <div className="watchlist-table">
                  {insights.map(item => (
                    <div className="watchlist-row" key={item.activity_id}>
                      <span className="watch-id">{item.activity_id}</span>
                      <span className={`deviation ${item.severity}`}>
                        {item.variance_pct}pp
                      </span>
                      <span className={`level ${item.severity}`}>
                        {item.severity.charAt(0).toUpperCase() + item.severity.slice(1)}
                      </span>
                    </div>
                  ))}
                </div>
              )
            }
          </section>
        </div>
      )}

      {/* Deviation cards */}
      {!loading && !error && insights.length > 0 && (
        <section style={{ marginTop: "2rem" }}>
          <h2 style={{ marginBottom: "1rem" }}>Deviation Details</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem" }}>
            {insights.map(item => (
              <div key={item.activity_id} style={{ background: "#fff", border: "1px solid #fca5a5", borderRadius: "8px", padding: "1.25rem", borderLeft: "4px solid #ef4444" }}>
                <div style={{ fontWeight: 700, color: "#0f172a", marginBottom: "0.25rem" }}>{item.activity_id}</div>
                <div style={{ color: "#475569", marginBottom: "0.25rem" }}>{item.activity_name}</div>
                <div style={{ fontSize: "0.85rem", color: "#64748b", marginBottom: "0.75rem" }}>{item.location}</div>
                <BarChart planned={item.planned_progress} actual={item.actual_progress} />
                <div style={{ marginTop: "0.75rem", fontSize: "0.9rem", color: "#ef4444", fontWeight: 600 }}>
                  ⚠ Variance: {item.variance_pct}pp — Behind Schedule
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {!loading && !error && insights.length === 0 && (
        <div style={{ marginTop: "2rem", background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px", padding: "1.5rem", textAlign: "center" }}>
          <div style={{ fontSize: "1.5rem" }}>✓</div>
          <h3 style={{ color: "#16a34a" }}>No deviations detected</h3>
          <p style={{ color: "#64748b" }}>All activities are on or ahead of schedule.</p>
        </div>
      )}
    </div>
  );
}