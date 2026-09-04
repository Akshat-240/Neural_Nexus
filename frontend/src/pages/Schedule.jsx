import React, { useEffect, useState, useCallback } from "react";
import { api } from "../api/client";

const statusColor = s =>
  s === "completed"   ? { bg: "#dcfce7", text: "#166534" } :
  s === "in_progress" ? { bg: "#dbeafe", text: "#1e40af" } :
                        { bg: "#f1f5f9", text: "#64748b" };

const statusLabel = s =>
  s === "completed"   ? "Complete" :
  s === "in_progress" ? "In Progress" :
  s === "not_started" ? "Not Started" : s;

export default function Schedule() {
  const [activities, setActivities] = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    api.getActivities()
      .then(data => {
        setActivities(data);
        setError(null);
        setLastUpdated(new Date().toLocaleTimeString());
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const total     = activities.length;
  const completed = activities.filter(a => a.status === "completed").length;
  const active    = activities.filter(a => a.status === "in_progress").length;
  const deviations= activities.filter(a => a.deviation_flag).length;

  return (
    <div style={{ padding: "2rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ margin: 0 }}>Project Schedule</h1>
          <p style={{ color: "#64748b", margin: "0.25rem 0 0" }}>
            North Processing Unit · PRJ-DEMO-01 · {lastUpdated && `Updated ${lastUpdated}`}
          </p>
        </div>
        <button
          onClick={load}
          style={{ padding: "0.5rem 1rem", background: "white", border: "1px solid #cbd5e1", borderRadius: "6px", cursor: "pointer", fontSize: "0.85rem", color: "#475569" }}
        >
          ↻ Refresh
        </button>
      </div>

      {/* Summary strip */}
      {!loading && !error && (
        <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
          {[
            ["Total Activities", total, "#0f172a"],
            ["Completed",        completed, "#16a34a"],
            ["In Progress",      active, "#2563eb"],
            ["Deviations",       deviations, deviations > 0 ? "#dc2626" : "#64748b"],
          ].map(([label, val, color]) => (
            <div key={label} style={{
              padding: "0.75rem 1.25rem", background: "#fff",
              border: "1px solid #e2e8f0", borderRadius: "8px", minWidth: "120px"
            }}>
              <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.04em" }}>{label}</div>
              <div style={{ fontSize: "1.6rem", fontWeight: 700, color }}>{val}</div>
            </div>
          ))}
        </div>
      )}

      {/* States */}
      {loading && <p style={{ color: "#64748b", padding: "2rem 0" }}>Loading schedule…</p>}
      {error && (
        <div style={{ padding: "1.5rem", background: "#fee2e2", borderRadius: "8px", color: "#991b1b" }}>
          Unable to load project schedule: {error}
        </div>
      )}
      {!loading && !error && activities.length === 0 && (
        <div style={{ padding: "2rem", background: "#fef9c3", borderRadius: "8px", color: "#713f12", textAlign: "center" }}>
          <h3>No schedule activities found</h3>
          <p>Run <code>python reset_demo.py</code> to seed the database.</p>
        </div>
      )}

      {/* Table */}
      {!loading && !error && activities.length > 0 && (
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead>
              <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
                {["Activity ID", "Activity Name", "Discipline", "Location", "Planned", "Actual", "Variance", "Status"].map(h => (
                  <th key={h} style={{ padding: "0.85rem 1rem", fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.04em", color: "#64748b", fontWeight: 600 }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {activities.map((act, i) => {
                const sc = statusColor(act.status);
                const variance = act.variance_pct ?? 0;
                const isDeviation = act.deviation_flag;
                return (
                  <tr
                    key={act.activity_id}
                    style={{
                      borderBottom: "1px solid #f1f5f9",
                      background: i % 2 === 0 ? "#fff" : "#fafafa",
                      ...(isDeviation ? { background: "#fff8f8" } : {}),
                    }}
                  >
                    <td style={{ padding: "0.85rem 1rem", fontWeight: 700, fontFamily: "monospace", fontSize: "0.9rem", color: "#1e40af" }}>
                      {act.activity_id}
                    </td>
                    <td style={{ padding: "0.85rem 1rem", color: "#0f172a", maxWidth: "220px" }}>
                      {act.activity_name}
                    </td>
                    <td style={{ padding: "0.85rem 1rem", color: "#64748b", fontSize: "0.85rem" }}>{act.discipline}</td>
                    <td style={{ padding: "0.85rem 1rem", color: "#64748b", fontSize: "0.85rem" }}>{act.location}</td>
                    <td style={{ padding: "0.85rem 1rem", color: "#475569", fontWeight: 600 }}>{act.planned_progress}%</td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <div style={{ width: "60px", height: "6px", background: "#e2e8f0", borderRadius: "3px", overflow: "hidden" }}>
                          <div style={{ width: `${act.actual_progress}%`, height: "100%", background: isDeviation ? "#ef4444" : "#3b82f6", borderRadius: "3px" }} />
                        </div>
                        <span style={{ fontWeight: 600, color: isDeviation ? "#ef4444" : "#0f172a" }}>
                          {act.actual_progress}%
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: "0.85rem 1rem", fontWeight: 700, color: variance < -5 ? "#ef4444" : variance < 0 ? "#d97706" : "#16a34a" }}>
                      {variance > 0 ? "+" : ""}{variance}pp
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <span style={{ padding: "0.25rem 0.6rem", borderRadius: "4px", fontSize: "0.78rem", fontWeight: 600, background: sc.bg, color: sc.text }}>
                        {statusLabel(act.status)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}