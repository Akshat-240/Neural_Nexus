import React, { useEffect, useState } from "react";
import "../App.css";

function Schedule() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/activities")
      .then((res) => res.json())
      .then((data) => {
        setActivities(data);
        setLoading(false);
      })
      .catch((e) => {
        console.error(e);
        setLoading(false);
      });
  }, []);

  return (
    <div className="fc-page" style={{ padding: "3rem" }}>
      <div className="fc-header" style={{ marginBottom: "2rem" }}>
        <h1>Project Schedule</h1>
        <p>Canonical schedule synced with live field updates.</p>
      </div>

      {loading ? (
        <p>Loading schedule...</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #cbd5e1" }}>
              <th style={{ padding: "1rem 0.5rem" }}>Activity ID</th>
              <th style={{ padding: "1rem 0.5rem" }}>Activity Name</th>
              <th style={{ padding: "1rem 0.5rem" }}>Discipline</th>
              <th style={{ padding: "1rem 0.5rem" }}>Location</th>
              <th style={{ padding: "1rem 0.5rem" }}>Planned</th>
              <th style={{ padding: "1rem 0.5rem" }}>Actual</th>
              <th style={{ padding: "1rem 0.5rem" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {activities.map((act) => (
              <tr key={act.activity_id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "1rem 0.5rem", fontWeight: "600" }}>{act.activity_id}</td>
                <td style={{ padding: "1rem 0.5rem" }}>{act.activity_name}</td>
                <td style={{ padding: "1rem 0.5rem" }}>{act.discipline}</td>
                <td style={{ padding: "1rem 0.5rem" }}>{act.location}</td>
                <td style={{ padding: "1rem 0.5rem" }}>{act.planned_progress}%</td>
                <td style={{ padding: "1rem 0.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <div style={{ flex: 1, height: "6px", background: "#e2e8f0", borderRadius: "3px" }}>
                      <div style={{ width: `${act.actual_progress || 0}%`, height: "100%", background: "#3b82f6", borderRadius: "3px" }}></div>
                    </div>
                    <span>{act.actual_progress || 0}%</span>
                  </div>
                </td>
                <td style={{ padding: "1rem 0.5rem" }}>
                  <span style={{ padding: "0.25rem 0.5rem", borderRadius: "4px", fontSize: "0.85rem", background: act.status === "completed" ? "#dcfce7" : "#f1f5f9", color: act.status === "completed" ? "#166534" : "#475569" }}>
                    {act.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Schedule;