import React, { useState } from "react";
import "../App.css";

function FieldCapture() {
  const [report, setReport] = useState("");
  const [location, setLocation] = useState("Unit 3");
  const [discipline, setDiscipline] = useState("Piping");
  const [date, setDate] = useState("03 Sep 2026");
  const [analyzed, setAnalyzed] = useState(false);

  const handleAnalyze = () => {
    if (report.trim()) {
      setAnalyzed(true);
    }
  };

  return (
    <div className="fc-page">

      {/* Header */}
      <div className="fc-header">
        <div className="fc-eyebrow">
          NORTH PROCESSING UNIT <span>LIVE</span>
        </div>

        <h1>Capture field update</h1>
        <p>
          Report what happened naturally. The system structures and links it.
        </p>
      </div>

      {/* Main grid */}
      <div className="fc-layout">

        {/* Left side */}
        <div className="fc-main">

          <div className="fc-section-label">NEW FIELD EVENT</div>

          <textarea
            className="fc-report"
            placeholder="Describe the work in your own words..."
            value={report}
            onChange={(e) => {
              setReport(e.target.value);
              setAnalyzed(false);
            }}
          />

          <div className="fc-hint">
            Use text, voice, or evidence. No schedule required.
          </div>

          <div className="fc-actions">
            <button
              className="fc-analyze-btn"
              onClick={handleAnalyze}
            >
              Analyze field update →
            </button>

            <button className="fc-voice-btn">
              ◉ Record voice
            </button>
          </div>


          {/* Optional context */}
          <div className="fc-context">
            <div className="fc-section-label">OPTIONAL CONTEXT</div>

            <div className="fc-context-grid">

              <div className="fc-input-group">
                <label>Location</label>
                <input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>

              <div className="fc-input-group">
                <label>Discipline</label>
                <input
                  value={discipline}
                  onChange={(e) => setDiscipline(e.target.value)}
                />
              </div>

              <div className="fc-input-group">
                <label>Date</label>
                <input
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>

            </div>
          </div>


          {/* Evidence */}
          <div className="fc-evidence">
            <div className="fc-section-label">ATTACH EVIDENCE</div>

            <div className="fc-upload-box">
              <div className="fc-plus">+</div>

              <div>
                <h3>Add site photo</h3>
                <p>Photo / video optional — used to corroborate the event</p>
              </div>
            </div>
          </div>

        </div>


        {/* Right side guidance */}
        <aside className="fc-guidance">

          <h2>Capture guidance</h2>

          <div className="fc-guide-item">
            <span>01</span>
            <div>
              <h3>Describe the work</h3>
              <p>Use field language</p>
            </div>
          </div>

          <div className="fc-guide-item">
            <span>02</span>
            <div>
              <h3>Add context</h3>
              <p>Location improves matching</p>
            </div>
          </div>

          <div className="fc-guide-item">
            <span>03</span>
            <div>
              <h3>Attach evidence</h3>
              <p>Photos can corroborate</p>
            </div>
          </div>

          <div className="fc-guide-item">
            <span>04</span>
            <div>
              <h3>Review the result</h3>
              <p>Low confidence never silently updates</p>
            </div>
          </div>

        </aside>

      </div>


      {/* Analysis Result */}
      {analyzed && (
        <div className="fc-result">
          <div>
            <span className="fc-result-label">ANALYSIS COMPLETE</span>
            <h2>Field update structured successfully</h2>
            <p>
              The event has been matched with the relevant project activity.
            </p>
          </div>

          <div className="fc-confidence">
            <span>Confidence</span>
            <strong>94%</strong>
          </div>
        </div>
      )}

    </div>
  );
}

export default FieldCapture;