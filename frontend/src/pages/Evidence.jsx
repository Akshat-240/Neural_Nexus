import React from "react";
import "../App.css";
export default function Evidence() {
  const trail = [
    ["18:31", "Field event captured", "EVT-0091", "TEXT"],
    ["18:34", "LS/LO match proposed", "MAT-0001", "AI"],
    ["18:37", "Site photo corroborated", "EVD-0003", "CV"],
    ["18:40", "Confidence fused", "0.94", "AI"],
    ["18:45", "Planner verification recorded", "VER-0005", "HUMAN"],
    ["18:48", "Schedule actual updated", "AUD-0001", "SYSTEM"],
  ];

  return (
    <main className="evidence-page">
      {/* Top context */}
      <div className="page-context">
        <span>North Processing Unit</span>
        <span className="live-dot">LIVE</span>
      </div>

      {/* Header */}
      <div className="evidence-header">
        <div>
          <h1>PIP-1024 · Erect Line 24-XX</h1>
          <p>Verified activity record and evidence trail</p>
        </div>

        <span className="verified-badge">Verified</span>
      </div>

      {/* Summary */}
      <section className="evidence-summary">
        <div className="summary-title">
          <span>PIP-1024</span>
          <h2>Erect Line 24-XX</h2>
          <p>LS · Piping · Unit 3</p>
        </div>

        <div className="summary-stat">
          <span>Planned</span>
          <strong>100%</strong>
        </div>

        <div className="summary-stat">
          <span>Actual</span>
          <strong>100%</strong>
        </div>

        <div className="summary-stat">
          <span>Variance</span>
          <strong>0%</strong>
        </div>

        <div className="summary-stat">
          <span>Confidence</span>
          <strong>94%</strong>
        </div>
      </section>

      {/* Main evidence content */}
      <section className="evidence-content">
        {/* Left */}
        <div className="trail-section">
  <h3>Evidence trail</h3>

  <div className="trail-list">
    {trail.map(([time, event, id, type]) => (
      <div className="trail-row" key={time}>
        <div className="trail-time">{time}</div>
        <div className="trail-event">{event}</div>
        <div className="trail-id">{id}</div>
        <div className={`trail-type ${type.toLowerCase()}`}>
          {type}
        </div>
      </div>
    ))}
  </div>
</div>

        {/* Right */}
        <aside className="visual-evidence">
          <h3>Visual evidence</h3>

          <div className="photo-placeholder">
            <span>SITE PHOTO</span>
          </div>

          <div className="support-label">Supportive evidence</div>

          <div className="detection-info">
            <strong>Detected: pipe spool</strong>
            <span>Visual score: 0.90</span>
          </div>
        </aside>
      </section>
    </main>
  );
}