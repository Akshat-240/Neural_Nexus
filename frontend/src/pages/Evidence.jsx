import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";

export default function Evidence() {
  const [params]  = useSearchParams();
  const dbId      = params.get("event");
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  useEffect(() => {
    if (!dbId) return;
    setLoading(true);
    api.getEvent(dbId)
      .then(d => { setDetail(d); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [dbId]);

  if (!dbId) {
    return (
      <main className="evidence-page">
        <div className="page-context">
          <span>North Processing Unit</span>
          <span className="live-dot">LIVE</span>
        </div>
        <div className="evidence-header">
          <h1>Evidence</h1>
          <p>Click a field event in <strong>Field Events</strong> to view its evidence trail.</p>
        </div>
      </main>
    );
  }

  if (loading) return <main className="evidence-page"><p style={{ padding: "2rem" }}>Loading evidence…</p></main>;
  if (error)   return <main className="evidence-page"><p style={{ padding: "2rem", color: "red" }}>Error: {error}</p></main>;
  if (!detail) return null;

  const m  = detail.match       || {};
  const ev = detail.evidence    || {};
  const vr = detail.verification || {};
  const sc = detail.schedule    || {};

  const confidencePct = m.final_confidence != null ? `${(m.final_confidence * 100).toFixed(0)}%` : "—";
  const imageUrl = ev.image_url ? api.imageUrl(ev.image_url) : null;

  const trail = [
    ["Field event captured", detail.event_id, "TEXT"],
    m.activity_id ? ["Activity matched", m.activity_id, "AI"] : null,
    ev.available  ? ["Visual evidence processed", `EVD · ${ev.visual_signal}`, "CV"] : null,
    m.final_confidence != null ? ["Confidence fused", confidencePct, "AI"] : null,
    vr.decision   ? [vr.decision === "verified" ? "Verification recorded" : `Decision: ${vr.decision}`, `VER-${detail.db_id}`, "SYSTEM"] : null,
    sc.actual_progress != null ? ["Schedule updated", `${sc.actual_progress}% actual`, "SYSTEM"] : null,
  ].filter(Boolean);

  return (
    <main className="evidence-page">
      <div className="page-context">
        <span>North Processing Unit</span>
        <span className="live-dot">LIVE</span>
      </div>

      <div className="evidence-header">
        <div>
          <h1>{m.activity_id || detail.event_id} · {m.activity_name || "Unknown Activity"}</h1>
          <p>Verified activity record and evidence trail</p>
        </div>
        {vr.decision === "verified" && <span className="verified-badge">Verified</span>}
        {vr.decision === "rejected"  && <span style={{ background: "#fee2e2", color: "#991b1b", padding: "0.25rem 0.75rem", borderRadius: "4px", fontWeight: 600 }}>Rejected</span>}
        {(!vr.decision || vr.decision === "review" || vr.decision === "pending_review") && (
          <span style={{ background: "#fef3c7", color: "#92400e", padding: "0.25rem 0.75rem", borderRadius: "4px", fontWeight: 600 }}>Pending Review</span>
        )}
      </div>

      {/* Summary row */}
      <section className="evidence-summary">
        <div className="summary-title">
          <span>{m.activity_id || "—"}</span>
          <h2>{m.activity_name || "—"}</h2>
          <p>{detail.source} · {detail.event_id}</p>
        </div>
        <div className="summary-stat"><span>Planned</span><strong>{sc.planned_progress != null ? `${sc.planned_progress}%` : "—"}</strong></div>
        <div className="summary-stat"><span>Actual</span><strong>{sc.actual_progress != null ? `${sc.actual_progress}%` : "—"}</strong></div>
        <div className="summary-stat">
          <span>Variance</span>
          <strong style={{ color: sc.variance_pct < 0 ? "#ef4444" : "#16a34a" }}>
            {sc.variance_pct != null ? `${sc.variance_pct}pp` : "—"}
          </strong>
        </div>
        <div className="summary-stat"><span>Confidence</span><strong>{confidencePct}</strong></div>
      </section>

      {/* Field report */}
      <section style={{ background: "#f8fafc", borderRadius: "8px", padding: "1rem", margin: "1rem 0", borderLeft: "4px solid #3b82f6" }}>
        <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "0.25rem" }}>FIELD REPORT</div>
        <p style={{ fontStyle: "italic" }}>"{detail.report_text}"</p>
      </section>

      <section className="evidence-content">
        {/* Trail */}
        <div className="trail-section">
          <h3>Evidence trail</h3>
          <div className="trail-list">
            {trail.map(([event, id, type], i) => (
              <div className="trail-row" key={i}>
                <div className="trail-event">{event}</div>
                <div className="trail-id">{id}</div>
                <div className={`trail-type ${type.toLowerCase()}`}>{type}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Visual */}
        <aside className="visual-evidence">
          <h3>Visual Evidence</h3>
          {imageUrl ? (
            <img
              src={imageUrl}
              alt="Uploaded site evidence"
              style={{ width: "100%", borderRadius: "6px", objectFit: "cover", maxHeight: "220px" }}
            />
          ) : (
            <div className="photo-placeholder">
              <span>{ev.available ? "Image unavailable" : "No image uploaded"}</span>
            </div>
          )}
          {ev.available && (
            <>
              <div className="support-label">
                {ev.visual_signal === "supportive" ? "✓ Supportive evidence" : "Weak / inconclusive"}
              </div>
              <div className="detection-info">
                <strong>Visual signal: {ev.visual_signal}</strong>
                <span>Score: {ev.confidence != null ? (ev.confidence * 100).toFixed(0) + "%" : "—"}</span>
                <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Pipe-like structural pattern detected</span>
              </div>
            </>
          )}
        </aside>
      </section>
    </main>
  );
}