import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

const CASE_A = "24-XX spool erected today at Unit 3.";
const CASE_B = "Line 24 work completed.";
const CASE_C = "Pipe support installation is approximately 50 percent complete at Unit 3.";

// Pipeline step labels shown during analysis
const STEPS = [
  "Capturing field information",
  "Extracting activity from text",
  "Reading schedule from database",
  "Matching against schedule activities",
  "Analyzing visual evidence",
  "Fusing confidence scores",
  "Generating verification decision",
];

function PipelineProgress({ activeStep }) {
  return (
    <div style={{
      margin: "1.5rem 0", padding: "1.25rem 1.5rem",
      background: "#f8fafc", border: "1px solid #e2e8f0",
      borderRadius: "8px"
    }}>
      <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "1rem" }}>
        ANALYZING FIELD UPDATE
      </div>
      {STEPS.map((step, i) => {
        const done    = i < activeStep;
        const current = i === activeStep;
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.6rem" }}>
            <div style={{
              width: "18px", height: "18px", borderRadius: "50%", flexShrink: 0,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "0.7rem", fontWeight: 700,
              background: done ? "#16a34a" : current ? "#3b82f6" : "#e2e8f0",
              color: done || current ? "white" : "#94a3b8",
              animation: current ? "pulse 1s infinite" : "none",
            }}>
              {done ? "✓" : i + 1}
            </div>
            <span style={{
              fontSize: "0.9rem",
              color: done ? "#16a34a" : current ? "#1e40af" : "#94a3b8",
              fontWeight: current ? 600 : 400,
            }}>
              {step}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function ConfidenceBar({ value }) {
  const pct = value != null ? Math.round(value * 100) : 0;
  const color = pct >= 80 ? "#16a34a" : pct >= 60 ? "#d97706" : "#ef4444";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "6px" }}>
      <div style={{ flex: 1, height: "10px", background: "#e2e8f0", borderRadius: "5px", overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: "5px", transition: "width 0.6s ease" }} />
      </div>
      <strong style={{ color, minWidth: "3rem", fontSize: "1.1rem" }}>{pct}%</strong>
    </div>
  );
}

function LanguageInsightsPanel({ insights }) {
  if (!insights || !insights.language) return null;
  const { language, sentiment, entities, key_phrases } = insights;
  
  const getSentimentColor = (sent) => {
    if (sent === "positive") return { bg: "#dcfce7", text: "#166534" };
    if (sent === "negative") return { bg: "#fee2e2", text: "#991b1b" };
    return { bg: "#f3f4f6", text: "#374151" };
  };
  const sc = getSentimentColor(sentiment?.overall);

  return (
    <div style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.25rem", marginBottom: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "1rem" }}>
        Azure NLP Insights
      </div>
      
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
        {/* Language Badge */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          <span style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Language</span>
          <div style={{ background: "#eff6ff", color: "#1d4ed8", padding: "0.25rem 0.6rem", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 600 }}>
            {language.name} {language.confidence ? `(${Math.round(language.confidence * 100)}%)` : ""}
          </div>
        </div>

        {/* Sentiment Badge */}
        {sentiment && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <span style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Sentiment</span>
            <div style={{ background: sc.bg, color: sc.text, padding: "0.25rem 0.6rem", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 600, textTransform: "capitalize" }}>
              {sentiment.overall}
            </div>
          </div>
        )}
      </div>

      {/* Entities & Key Phrases */}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {entities && entities.length > 0 && (
          <div>
            <span style={{ fontSize: "0.75rem", color: "#64748b", display: "block", marginBottom: "0.3rem" }}>Entities Detected</span>
            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
              {entities.map((e, idx) => (
                <span key={idx} style={{ background: "#f8fafc", border: "1px solid #cbd5e1", color: "#334155", fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: "12px" }}>
                  <strong>{e.text}</strong> ({e.category})
                </span>
              ))}
            </div>
          </div>
        )}
        
        {key_phrases && key_phrases.length > 0 && (
          <div>
            <span style={{ fontSize: "0.75rem", color: "#64748b", display: "block", marginBottom: "0.3rem" }}>Key Phrases</span>
            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
              {key_phrases.map((kp, idx) => (
                <span key={idx} style={{ background: "#f1f5f9", color: "#475569", fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: "4px" }}>
                  {kp}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ResultPanel({ result, report, dbId, onNavigate }) {
  const m  = result.match        || {};
  const ev = result.evidence     || {};
  const sc = result.schedule     || {};
  const isVerified = result.pipeline_status === "verified";
  const isReview   = result.pipeline_status === "pending_review";
  const imageUrl   = result.image_url ? api.imageUrl(result.image_url) : null;
  const navigate   = useNavigate();

  return (
    <div style={{ marginTop: "2rem", border: "2px solid " + (isVerified ? "#bbf7d0" : isReview ? "#fde68a" : "#e2e8f0"), borderRadius: "8px", overflow: "hidden" }}>

      {/* Status banner */}
      <div style={{
        padding: "0.75rem 1.5rem", fontWeight: 700, fontSize: "0.95rem",
        background: isVerified ? "#f0fdf4" : isReview ? "#fffbeb" : "#fef2f2",
        color:      isVerified ? "#16a34a"  : isReview ? "#d97706"  : "#dc2626",
        borderBottom: "1px solid #e2e8f0",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <span>{isVerified ? "✓ Verified — schedule updated" : isReview ? "⚠ Human review required" : "✗ Pipeline failed"}</span>
        <span style={{ fontSize: "0.75rem", fontWeight: 400, color: "#64748b" }}>{result.event_id}</span>
      </div>

      {/* Field update echo */}
      <div style={{ background: "#f8fafc", padding: "1rem 1.5rem", borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#94a3b8", marginBottom: "0.25rem" }}>FIELD UPDATE</div>
        <p style={{ fontStyle: "italic", color: "#1e293b", margin: 0 }}>"{report}"</p>
      </div>

      {/* Match */}
      <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#94a3b8", marginBottom: "0.5rem" }}>MATCH</div>
        {m.activity_id ? (
          <>
            <div style={{ fontWeight: 700, fontSize: "1.15rem", color: "#0f172a" }}>{m.activity_id}</div>
            <div style={{ color: "#475569", marginBottom: "0.75rem" }}>{m.activity_name}</div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>Confidence</div>
              <ConfidenceBar value={m.final_confidence} />
            </div>
          </>
        ) : (
          <p style={{ color: "#ef4444" }}>No schedule activity matched — consider a different description.</p>
        )}
      </div>

      {/* Evidence */}
      <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid #e2e8f0", display: "flex", gap: "1.5rem", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#94a3b8", marginBottom: "0.5rem" }}>EVIDENCE</div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
            <span style={{ color: "#16a34a", fontSize: "0.9rem" }}>✓ Semantic text match</span>
            {ev.available
              ? <span style={{ color: ev.supportive ? "#16a34a" : "#d97706", fontSize: "0.9rem" }}>
                  {ev.supportive ? "✓ Visual evidence: Supportive" : "⚠ Visual evidence: Weak"}
                </span>
              : <span style={{ color: "#94a3b8", fontSize: "0.9rem" }}>○ No image uploaded</span>
            }
            {ev.available && (
              <span style={{ fontSize: "0.8rem", color: "#64748b", marginLeft: "1rem" }}>
                Pipe-like structural pattern detected
              </span>
            )}
          </div>
        </div>
        {imageUrl && (
          <img
            src={imageUrl}
            alt="Uploaded site evidence"
            style={{ width: "110px", height: "76px", objectFit: "cover", borderRadius: "6px", border: "1px solid #e2e8f0", flexShrink: 0 }}
          />
        )}
      </div>

      {/* Schedule impact */}
      {sc && (sc.planned_progress_pct != null || sc.planned_progress != null) && (
        <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid #e2e8f0", background: isVerified ? "#f0fdf4" : "#fffbeb" }}>
          <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#94a3b8", marginBottom: "0.75rem" }}>SCHEDULE IMPACT</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
            {[
              ["Planned",  sc.planned_progress_pct ?? sc.planned_progress, null],
              ["Actual",   sc.actual_progress_pct  ?? sc.actual_progress,  null],
              ["Variance", sc.variance_pct, sc.variance_pct],
            ].map(([label, val, colorRef]) => (
              <div key={label}>
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>{label}</div>
                <div style={{
                  fontWeight: 700, fontSize: "1.2rem",
                  color: colorRef != null && colorRef < -5 ? "#ef4444" : colorRef != null && colorRef < 0 ? "#d97706" : "#0f172a"
                }}>
                  {val != null ? `${val}${label === "Variance" ? " pp" : "%"}` : "—"}
                </div>
              </div>
            ))}
          </div>
          {sc.variance_pct != null && sc.variance_pct < -5 && (
            <div style={{ marginTop: "0.75rem", color: "#ef4444", fontWeight: 600, fontSize: "0.9rem" }}>
              ⚠ Deviation detected — check Insights
            </div>
          )}
        </div>
      )}

      {/* Consequence navigation */}
      <div style={{ padding: "1.25rem 1.5rem", background: "#f8fafc", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        {dbId && (
          <button
            onClick={() => navigate(`/evidence?event=${dbId}`)}
            style={{ padding: "0.6rem 1.2rem", background: "#1e40af", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600, fontSize: "0.9rem" }}
          >
            View Evidence Trail →
          </button>
        )}
        {isReview && (
          <button
            onClick={() => navigate("/review-queue")}
            style={{ padding: "0.6rem 1.2rem", background: "#d97706", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600, fontSize: "0.9rem" }}
          >
            Go to Review Queue →
          </button>
        )}
        {isVerified && (
          <button
            onClick={() => navigate("/schedule")}
            style={{ padding: "0.6rem 1.2rem", background: "#16a34a", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600, fontSize: "0.9rem" }}
          >
            View Schedule →
          </button>
        )}
        {sc.variance_pct != null && sc.variance_pct < -5 && (
          <button
            onClick={() => navigate("/insights")}
            style={{ padding: "0.6rem 1.2rem", background: "#ef4444", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: 600, fontSize: "0.9rem" }}
          >
            View Deviation →
          </button>
        )}
        <button
          onClick={() => navigate("/field-events")}
          style={{ padding: "0.6rem 1.2rem", background: "white", color: "#475569", border: "1px solid #cbd5e1", borderRadius: "6px", cursor: "pointer", fontSize: "0.9rem" }}
        >
          All Events
        </button>
      </div>
    </div>
  );
}

export default function FieldCapture() {
  const [report,       setReport]       = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [pipelineStep, setPipelineStep] = useState(-1);
  const [result,       setResult]       = useState(null);
  const [resultDbId,   setResultDbId]   = useState(null);
  const [error,        setError]        = useState(null);
  const [recording,    setRecording]    = useState(false);
  const [transcript,   setTranscript]   = useState(null);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [audioUrl,     setAudioUrl]     = useState(null);
  const [languageInsights, setLanguageInsights] = useState(null);
  const [analyzingLang, setAnalyzingLang] = useState(false);
  const [targetLang, setTargetLang] = useState("hi");
  const [translatedText, setTranslatedText] = useState("");
  const [translating, setTranslating] = useState(false);
  const [translationError, setTranslationError] = useState(null);
  const [showTranslator, setShowTranslator] = useState(false);
  const mediaRecRef = useRef(null);
  const recognitionRef = useRef(null);
  const liveTranscriptRef = useRef(""); // To access latest transcript in onstop closure
  const navigate    = useNavigate();

  const runPipeline = async (text, file) => {
    setLoading(true);
    setResult(null);
    setResultDbId(null);
    setError(null);
    setPipelineStep(0);

    // Advance steps with small delays to mirror real processing stages
    const stepTimes = [200, 400, 500, 600, 500, 400, 300];
    let step = 0;
    const advance = () => {
      step++;
      if (step < STEPS.length) {
        setPipelineStep(step);
        setTimeout(advance, stepTimes[step] ?? 400);
      }
    };
    setTimeout(advance, stepTimes[0]);

    try {
      const data = await api.processUpdate("PRJ-DEMO-01", text, file);
      setPipelineStep(STEPS.length); // all done
      setResult(data);
      // Derive numeric DB id from event_id string returned by backend (field_update id persisted)
      // The orchestrator returns event_id like "EVT-ABCDEF" (not db integer).
      // We need to fetch events list to find the matching db_id — or we add db_id to the response.
      // Fetch recent events to find it.
      try {
        const events = await api.getEvents();
        const match = events.find(e => e.report_text === text);
        if (match) setResultDbId(match.db_id);
      } catch (_) {}
    } catch (e) {
      setError(e.message);
      setPipelineStep(-1);
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async (text) => {
    if (!text.trim()) return;
    setAnalyzingLang(true);
    try {
      const insights = await api.analyzeLanguage(text);
      setLanguageInsights(insights);
    } catch (e) {
      console.error("Language API failed", e);
    } finally {
      setAnalyzingLang(false);
    }
  };

  const handleTranslate = async (lang = targetLang) => {
    if (!report.trim()) return;
    setTranslating(true);
    setTranslationError(null);
    try {
      const res = await api.translateText(report, lang);
      if (res.error) throw new Error(res.error);
      setTranslatedText(res.translated_text);
    } catch (err) {
      console.error(err);
      setTranslationError("Failed to translate. Please try again.");
    } finally {
      setTranslating(false);
    }
  };

  useEffect(() => {
    if (showTranslator && report.trim()) {
      handleTranslate(targetLang);
    }
  }, [targetLang]);

  const handleAnalyze = () => {
    if (!report.trim()) return;
    fetchInsights(report);
    runPipeline(report, selectedFile);
  };

  // Voice recording via browser MediaRecorder + Web Speech API for live preview
  const startVoice = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      alert("Microphone not supported in this browser.");
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    // Setup audio recording to send to backend
    const rec = new MediaRecorder(stream);
    const chunks = [];
    liveTranscriptRef.current = ""; // Reset ref
    
    rec.ondataavailable = e => chunks.push(e.data);
    rec.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      setRecording(false);
      setTranscript("Processing and verifying audio...");
      try {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        const data = await api.transcribeVoice("PRJ-DEMO-01", audioBlob);
        
        // Use the live transcript if available (since backend dummy returns "Field voice report..."), 
        // fallback to backend data if Web Speech API failed.
        const finalTranscript = liveTranscriptRef.current.trim() || data.transcript;
        
        setTranscript(finalTranscript);
        setReport(finalTranscript);
        setLiveTranscript("");
        fetchInsights(finalTranscript);
      } catch (e) {
        setTranscript("Transcription failed: " + e.message);
      }
    };
    rec.start();
    mediaRecRef.current = rec;

    // Setup live transcription
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.onresult = (event) => {
        let text = "";
        for (let i = 0; i < event.results.length; i++) {
          text += event.results[i][0].transcript;
        }
        setLiveTranscript(text);
        liveTranscriptRef.current = text;
      };
      recognition.start();
      recognitionRef.current = recognition;
    }

    setRecording(true);
    setTranscript(null);
    setAudioUrl(null);
    setLiveTranscript("Listening...");
  };

  const stopVoice = () => {
    if (mediaRecRef.current) mediaRecRef.current.stop();
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
  };

  const setDemo = (text) => {
    setReport(text);
    setResult(null);
    setResultDbId(null);
    setError(null);
    setPipelineStep(-1);
    setTranscript(null);
  };

  return (
    <div className="fc-page">
      <div className="fc-header">
        <div className="fc-eyebrow">NORTH PROCESSING UNIT <span>LIVE</span></div>
        <h1>Capture field update</h1>
        <p>Report what happened at site. The system extracts, matches, and verifies it against the project schedule.</p>
      </div>

      <div className="fc-layout">
        <div className="fc-main">

          {/* Project */}
          <div className="fc-section-label">PROJECT</div>
          <select disabled style={{ width: "100%", padding: "0.6rem", marginBottom: "1.25rem", border: "1px solid #cbd5e1", borderRadius: "4px", background: "#f8fafc", color: "#475569" }}>
            <option>PRJ-DEMO-01 — North Processing Unit</option>
          </select>

          {/* Voice transcript echo */}
          {(transcript || (recording && liveTranscript)) && (
            <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: "6px", padding: "0.75rem 1rem", marginBottom: "1rem", fontSize: "0.9rem" }}>
              <div style={{ fontSize: "0.7rem", color: "#3b82f6", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.25rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>{recording ? "🎙 LIVE TRANSCRIPT" : "VOICE TRANSCRIPT"}</span>
                {recording && <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#ef4444", animation: "pulse 1.5s infinite" }} />}
              </div>
              <p style={{ fontStyle: "italic", color: "#1e40af", margin: 0, marginBottom: audioUrl ? "0.75rem" : 0 }}>"{recording ? liveTranscript : transcript}"</p>
              
              {audioUrl && !recording && (
                <div style={{ display: "flex", alignItems: "center", marginTop: "0.5rem", paddingTop: "0.75rem", borderTop: "1px solid #dbeafe" }}>
                  <audio src={audioUrl} controls style={{ height: "36px", width: "100%", outline: "none" }} />
                </div>
              )}
            </div>
          )}

          {/* Azure NLP Insights */}
          {!recording && analyzingLang && (
            <div style={{ fontSize: "0.85rem", color: "#64748b", marginBottom: "1rem", fontStyle: "italic" }}>
              Analyzing language insights...
            </div>
          )}
          {!recording && languageInsights && (
             <LanguageInsightsPanel insights={languageInsights} />
          )}

          {/* Translation Panel */}
          {showTranslator && (
            <div style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.25rem", marginBottom: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Translation
                </div>
                <select 
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  style={{ padding: "0.4rem 0.75rem", borderRadius: "4px", border: "1px solid #cbd5e1", fontSize: "0.85rem", color: "#334155", background: "#f8fafc", outline: "none", cursor: "pointer" }}
                >
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="hi">Hindi</option>
                  <option value="ar">Arabic</option>
                  <option value="zh-Hans">Chinese (Simplified)</option>
                </select>
              </div>

              {translating ? (
                <div style={{ fontSize: "0.85rem", color: "#64748b", fontStyle: "italic", padding: "0.5rem 0" }}>
                  Translating...
                </div>
              ) : translationError ? (
                <div style={{ fontSize: "0.85rem", color: "#ef4444", padding: "0.5rem 0", background: "#fef2f2", borderRadius: "4px", paddingLeft: "0.5rem" }}>
                  {translationError}
                </div>
              ) : (
                <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                  <p style={{ margin: 0, fontSize: "0.95rem", color: "#334155", fontStyle: "italic" }}>
                    "{translatedText}"
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Text input */}
          <div className="fc-section-label">FIELD UPDATE</div>
          <textarea
            className="fc-report"
            placeholder="Describe what happened at site in your own words…&#10;&#10;e.g. &quot;24-XX spool erected today at Unit 3&quot;"
            value={report}
            onChange={e => { setReport(e.target.value); setResult(null); setError(null); setPipelineStep(-1); }}
          />

          {/* Actions */}
          <div className="fc-actions">
            <button
              className="fc-analyze-btn"
              onClick={handleAnalyze}
              disabled={loading || !report.trim()}
            >
              {loading ? "Analyzing…" : "Analyze update →"}
            </button>
            <button
              className="fc-voice-btn"
              onClick={recording ? stopVoice : startVoice}
              style={{ background: recording ? "#ef4444" : undefined }}
            >
              {recording ? "◼ Stop recording" : "🎙 Record voice"}
            </button>
            <button
              className="fc-translate-btn"
              onClick={() => {
                if (showTranslator) {
                  setShowTranslator(false);
                } else {
                  setShowTranslator(true);
                  handleTranslate(targetLang);
                }
              }}
              disabled={loading || !report.trim()}
              style={{
                padding: "0.85rem 1.5rem", borderRadius: "8px", fontWeight: 600,
                fontSize: "0.95rem", cursor: "pointer", transition: "all 0.2s",
                background: showTranslator ? "#1e40af" : "white",
                color: showTranslator ? "white" : "#475569",
                border: "1px solid #cbd5e1"
              }}
            >
              🌐 Translate
            </button>
          </div>

          {/* Demo shortcuts */}
          <div style={{ marginTop: "1.25rem" }}>
            <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Demo scenarios:
            </div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {[
                ["A — Verified",   CASE_A],
                ["B — Review",     CASE_B],
                ["C — Deviation",  CASE_C],
              ].map(([label, text]) => (
                <button
                  key={label}
                  onClick={() => setDemo(text)}
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
                onChange={e => setSelectedFile(e.target.files[0] || null)}
                style={{ position: "absolute", opacity: 0, top: 0, left: 0, width: "100%", height: "100%", cursor: "pointer" }}
              />
              <div className="fc-plus">{selectedFile ? "✓" : "+"}</div>
              <div>
                <h3>{selectedFile ? selectedFile.name : "Add site photo"}</h3>
                <p>Processed by CV pipeline for visual corroboration</p>
              </div>
            </div>
            {selectedFile && (
              <div style={{ marginTop: "0.5rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <img
                  src={URL.createObjectURL(selectedFile)}
                  alt="Preview"
                  style={{ width: "90px", height: "60px", objectFit: "cover", borderRadius: "4px", border: "1px solid #cbd5e1" }}
                />
                <button
                  onClick={() => setSelectedFile(null)}
                  style={{ fontSize: "0.8rem", color: "#ef4444", background: "none", border: "none", cursor: "pointer" }}
                >
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Pipeline progress */}
          {loading && pipelineStep >= 0 && (
            <PipelineProgress activeStep={pipelineStep} />
          )}

          {/* Error */}
          {error && (
            <div style={{ marginTop: "1rem", padding: "0.75rem 1rem", background: "#fee2e2", borderRadius: "6px", color: "#991b1b", fontSize: "0.9rem" }}>
              Pipeline error: {error}
            </div>
          )}

          {/* Result */}
          {result && !loading && (
            <ResultPanel result={result} report={report} dbId={resultDbId} />
          )}
        </div>

        {/* Guidance sidebar */}
        <aside className="fc-guidance">
          <h2>How it works</h2>
          <div className="fc-guide-item"><span>01</span><div><h3>Describe the work</h3><p>Natural field language — no activity codes needed</p></div></div>
          <div className="fc-guide-item"><span>02</span><div><h3>AI extraction</h3><p>Extracts activity, location, and status from text</p></div></div>
          <div className="fc-guide-item"><span>03</span><div><h3>Schedule matching</h3><p>Semantic similarity against all DB activities</p></div></div>
          <div className="fc-guide-item"><span>04</span><div><h3>Visual corroboration</h3><p>CV analyzes uploaded photo for pipe-like structures</p></div></div>
          <div className="fc-guide-item"><span>05</span><div><h3>Confidence gate</h3><p>High → verified. Low → human review queue.</p></div></div>
          <div className="fc-guide-item"><span>06</span><div><h3>Schedule updated</h3><p>Verified events persist to DB — visible in Schedule & Insights</p></div></div>
        </aside>
      </div>
    </div>
  );
}