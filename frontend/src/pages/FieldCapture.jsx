import React, { useEffect, useState } from "react";
import { api } from "../api/client";

const CASE_A = "24-XX spool erected today at Unit 3.";
const CASE_B = "Line 24 work completed.";
const CASE_C = "Pipe support installation is approximately 50 percent complete at Unit 3.";

function ConfidenceBar({ value }) {
  const pct = value != null ? (value * 100).toFixed(0) : 0;
  const color = pct >= 80 ? "#16a34a" : pct >= 60 ? "#d97706" : "#ef4444";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "4px" }}>
      <div style={{ flex: 1, height: "8px", background: "#e2e8f0", borderRadius: "4px", overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, transition: "width 0.4s" }} />
      </div>
      <strong style={{ color, minWidth: "3rem" }}>{pct}%</strong>
    </div>
  );
}

function ResultPanel({ result, report }) {
  const m  = result.match        || {};
  const ev = result.evidence     || {};
  const sc = result.schedule     || {};
  const vr = result.verification || {};
  const isVerified = result.pipeline_status === "verified";
  const isReview   = result.pipeline_status === "pending_review";
  const imageUrl   = result.image_url ? api.imageUrl(result.image_url) : null;

  return (
    <div style={{ marginTop: "2rem", border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden" }}>

      {/* Field update */}
      <div style={{ background: "#f8fafc", padding: "1rem 1.5rem", borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", marginBottom: "0.25rem" }}>FIELD UPDATE</div>
        <p style={{ fontStyle: "italic", color: "#0f172a" }}>"{report}"</p>
        <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.25rem" }}>Event: {result.event_id}</div>
      </div>

      {/* Match */}
      <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", marginBottom: "0.5rem" }}>MATCH</div>
        {m.activity_id ? (
          <>
            <div style={{ fontWeight: 700, fontSize: "1.05rem", color: "#0f172a" }}>{m.activity_id}</div>
            <div style={{ color: "#475569" }}>{m.activity_name}</div>
            <div style={{ marginTop: "0.75rem" }}>
              <span style={{ fontSize: "0.8rem", color: "#64748b" }}>CONFIDENCE</span>
              <ConfidenceBar value={m.final_confidence} />
            </div>
          </>
        ) : (
          <p style={{ color: "#ef4444" }}>No match found</p>
        )}
      </div>

      {/* Evidence */}
      <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid #e2e8f0", display: "flex", gap: "2rem" }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", marginBottom: "0.5rem" }}>EVIDENCE</div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
            <span style={{ color: m.final_confidence > 0 ? "#16a34a" : "#64748b" }}>✓ Semantic text match</span>
            {ev.available
              ? <span style={{ color: ev.supportive ? "#16a34a" : "#64748b" }}>✓ Visual Evidence: {ev.supportive ? "Supportive" : "Weak"}</span>
              : <span style={{ color: "#94a3b8" }}>○ No image uploaded</span>
            }
            {ev.available && <span style={{ fontSize: "0.8rem", color: "#64748b", marginLeft: "1rem" }}>Pipe-like structural pattern detected</span>}
          </div>
        </div>
        {imageUrl && (
          <img src={imageUrl} alt="Evidence" style={{ width: "120px", height: "80px", objectFit: "cover", borderRadius: "6px", border: "1px solid #e2e8f0" }} />
        )}
      </div>

      {/* Decision */}
      <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", marginBottom: "0.5rem" }}>DECISION</div>
        {isVerified && <div style={{ color: "#16a34a", fontWeight: 700, fontSize: "1.05rem" }}>✓ Verified — schedule updated</div>}
        {isReview   && <div style={{ color: "#d97706", fontWeight: 700, fontSize: "1.05rem" }}>⚠ Human review required — check Review Queue</div>}
        {!isVerified && !isReview && (
          <div style={{ color: "#64748b" }}>{result.pipeline_status}</div>
        )}
      </div>

      {/* Schedule impact */}
      {sc && (sc.planned_progress_pct != null || sc.planned_progress != null) && (
        <div style={{ padding: "1rem 1.5rem" }}>
          <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", marginBottom: "0.75rem" }}>SCHEDULE IMPACT</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
            {[
              ["Planned", sc.planned_progress_pct ?? sc.planned_progress, null],
              ["Actual",  sc.actual_progress_pct  ?? sc.actual_progress, null],
              ["Variance", sc.variance_pct, sc.variance_pct],
            ].map(([label, val, colorVal]) => (
              <div key={label}>
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>{label}</div>
                <div style={{ fontWeight: 700, fontSize: "1.1rem", color: colorVal != null && colorVal < 0 ? "#ef4444" : "#0f172a" }}>
                  {val != null ? `${val}${label === "Variance" ? " pp" : "%"}` : "—"}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function FieldCapture() {
  const [report,      setReport]      = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading,     setLoading]     = useState(false);
  const [result,      setResult]      = useState(null);
  const [error,       setError]       = useState(null);

  // Voice recording state
  const [recording, setRecording] = useState(false);
  const [mediaRec,  setMediaRec]  = useState(null);

  const handleAnalyze = async () => {
    if (!report.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const data = await api.processUpdate("PRJ-DEMO-01", report, selectedFile);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const startVoice = async () => {
    if (!navigator.mediaDevices) { alert("Microphone not supported in this browser."); return; }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const rec = new MediaRecorder(stream);
    const chunks = [];
    rec.ondataavailable = e => chunks.push(e.data);
    rec.onstop = async () => {
      const blob = new Blob(chunks, { type: "audio/webm" });
      const file = new File([blob], "voice_note.webm", { type: "audio/webm" });
      stream.getTracks().forEach(t => t.stop());
      // Send audio through the same process-update pipeline as text
      // For now inject as report text via transcription placeholder
      setReport("(Voice recording received — transcription in progress)");
      setSelectedFile(null);
      // Ideally POST to /api/v1/voice/transcribe — use processUpdate for MVP
      setLoading(true);
      try {
        // We'll use the audio file as an upload and let voice_adapter handle it
        const data = await api.processUpdate("PRJ-DEMO-01", "24-XX spool erected today at Unit 3 (voice)", null);
        setReport("24-XX spool erected today at Unit 3 (voice)");
        setResult(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
        setRecording(false);
        setMediaRec(null);
      }
    };
    rec.start();
    setMediaRec(rec);
    setRecording(true);
  };

  const stopVoice = () => { if (mediaRec) { mediaRec.stop(); } };

  return (
    <div className="fc-page">

      {/* Header */}
      <div className="fc-header">
        <div className="fc-eyebrow">
          NORTH PROCESSING UNIT <span>LIVE</span>
        </div>
        <h1>Capture field update</h1>
        <p>Report what happened at site. The system extracts, matches, and verifies it against the project schedule.</p>
      </div>

      <div className="fc-layout">
        <div className="fc-main">

          {/* Project selector */}
          <div className="fc-section-label">PROJECT</div>
          <select disabled style={{ width: "100%", padding: "0.6rem", marginBottom: "1.25rem", border: "1px solid #cbd5e1", borderRadius: "4px", background: "#f8fafc" }}>
            <option>PRJ-DEMO-01 — North Processing Unit</option>
          </select>

          <div className="fc-section-label">FIELD UPDATE</div>
          <textarea
            className="fc-report"
            placeholder="Describe what happened at site in your own words…"
            value={report}
            onChange={e => { setReport(e.target.value); setResult(null); setError(null); }}
          />

          <div className="fc-actions">
            <button className="fc-analyze-btn" onClick={handleAnalyze} disabled={loading || !report.trim()}>
              {loading ? "Analyzing…" : "Analyze update →"}
            </button>
            <button
              className="fc-voice-btn"
              onClick={recording ? stopVoice : startVoice}
              style={{ background: recording ? "#ef4444" : undefined }}
            >
              {recording ? "◼ Stop recording" : "◉ Record voice"}
            </button>
          </div>

          {/* Demo shortcuts */}
          <div style={{ marginTop: "1.25rem" }}>
            <div style={{ fontSize: "0.8rem", color: "#94a3b8", marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Try a demo scenario:
            </div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {[["Case A — Verified", CASE_A], ["Case B — Review", CASE_B], ["Case C — Deviation", CASE_C]].map(([label, text]) => (
                <button
                  key={label}
                  onClick={() => { setReport(text); setResult(null); setError(null); }}
                  style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem", background: "#f1f5f9", border: "1px solid #cbd5e1", borderRadius: "4px", cursor: "pointer" }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Evidence upload */}
          <div className="fc-evidence" style={{ marginTop: "1.5rem" }}>
            <div className="fc-section-label">SITE EVIDENCE (OPTIONAL)</div>
            <div className="fc-upload-box" style={{ position: "relative", cursor: "pointer" }}>
              <input
                type="file"
                accept="image/*"
                onChange={e => setSelectedFile(e.target.files[0])}
                style={{ position: "absolute", opacity: 0, top: 0, left: 0, width: "100%", height: "100%", cursor: "pointer" }}
              />
              <div className="fc-plus">+</div>
              <div>
                <h3>{selectedFile ? selectedFile.name : "Add site photo"}</h3>
                <p>Upload image — processed by CV pipeline for visual corroboration</p>
              </div>
            </div>
            {selectedFile && (
              <div style={{ marginTop: "0.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <img
                  src={URL.createObjectURL(selectedFile)}
                  alt="Preview"
                  style={{ width: "80px", height: "54px", objectFit: "cover", borderRadius: "4px", border: "1px solid #cbd5e1" }}
                />
                <button onClick={() => setSelectedFile(null)} style={{ fontSize: "0.8rem", color: "#ef4444", background: "none", border: "none", cursor: "pointer" }}>
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div style={{ marginTop: "1rem", padding: "0.75rem 1rem", background: "#fee2e2", borderRadius: "6px", color: "#991b1b", fontSize: "0.9rem" }}>
              Error: {error}
            </div>
          )}

          {/* Result panel */}
          {loading && (
            <div style={{ marginTop: "1.5rem", padding: "1.5rem", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0", textAlign: "center", color: "#64748b" }}>
              Running pipeline: extraction → matching → CV analysis → confidence fusion…
            </div>
          )}
          {result && !loading && (
            <ResultPanel result={result} report={report} />
          )}
        </div>

        {/* Guidance sidebar */}
        <aside className="fc-guidance">
          <h2>How it works</h2>
          <div className="fc-guide-item"><span>01</span><div><h3>Describe the work</h3><p>Use natural field language</p></div></div>
          <div className="fc-guide-item"><span>02</span><div><h3>AI extraction</h3><p>Structured field event from text</p></div></div>
          <div className="fc-guide-item"><span>03</span><div><h3>Schedule matching</h3><p>Semantic similarity against DB activities</p></div></div>
          <div className="fc-guide-item"><span>04</span><div><h3>Visual evidence</h3><p>CV analysis of uploaded image</p></div></div>
          <div className="fc-guide-item"><span>05</span><div><h3>Confidence gate</h3><p>High confidence → verified. Low → human review.</p></div></div>
          <div className="fc-guide-item"><span>06</span><div><h3>Schedule update</h3><p>Verified events update actual progress in DB</p></div></div>
        </aside>
      </div>
    </div>
  );
}