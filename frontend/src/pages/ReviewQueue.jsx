import React, { useState } from "react";
import "../App.css";

export default function ReviewQueue() {
  const [selectedEvent, setSelectedEvent] = useState(null);

  const events = [
    {
      id: "EVT-1007",
      event: "Line 24 work completed",
      match: "P-101 / PIP-102 / PIP-103",
      confidence: "81%",
      statement: '"Line 24 work completed."',
      source: "Daily report · 03 Sep 2026 · Unit 3",
      candidates: [
        ["PIP-1024", "Erect Line 24-XX", "0.81"],
        ["PIP-1025", "Welding inspection · Line 24-XX", "0.79"],
        ["PIP-1026", "Hydro testing · Line 24-XX", "0.77"],
        ["PIP-1027", "Valve installation · Line 24-XX", "0.74"],
      ],
    },
    {
      id: "EVT-1005",
      event: "Valve work near Unit 3",
      match: "P-102 / PIP-103",
      confidence: "78%",
      statement: '"Valve work completed near Unit 3."',
      source: "Field report · 03 Sep 2026 · Unit 3",
      candidates: [
        ["PIP-103", "Valve installation", "0.78"],
        ["PIP-102", "Welding inspection", "0.71"],
      ],
    },
    {
      id: "EVT-1015",
      event: "Hydro test completed",
      match: "P-102",
      confidence: "72%",
      statement: '"Hydro test completed."',
      source: "Daily report · 03 Sep 2026",
      candidates: [
        ["PIP-1026", "Hydro testing · Line 24-XX", "0.72"],
      ],
    },
    {
      id: "EVT-1011",
      event: "Spool installed",
      match: "PIP-103 / PIP-104",
      confidence: "76%",
      statement: '"Spool installed on Line 24."',
      source: "Field report · Unit 3",
      candidates: [
        ["PIP-103", "Spool installation", "0.76"],
        ["PIP-104", "Valve installation", "0.69"],
      ],
    },
    {
      id: "EVT-1009",
      event: "Inspection finished on Line 24",
      match: "PIP-101",
      confidence: "83%",
      statement: '"Inspection finished on Line 24."',
      source: "Inspection report · 03 Sep 2026",
      candidates: [
        ["PIP-101", "Line inspection · 24-XX", "0.83"],
      ],
    },
  ];

  if (selectedEvent) {
    return (
      <div className="review-detail-page">
        <div className="rq-top">
          <div className="rq-unit">
            North Processing Unit <span>LIVE</span>
          </div>

          <button
            className="back-btn"
            onClick={() => setSelectedEvent(null)}
          >
            ← Back to queue
          </button>
        </div>

        <div className="review-detail-header">
          <div>
            <h1>Review {selectedEvent.id}</h1>
            <p>Planner decision is required before any schedule update</p>
          </div>
          <div className="review-required">Review required</div>
        </div>

        <div className="review-detail-grid">

          {/* LEFT */}
          <div className="field-statement">
            <h3>Field statement</h3>

            <div className="statement-box">
              {selectedEvent.statement}
            </div>

            <p className="statement-note">
              The statement does not specify exactly which activity was
              performed. Review candidate matches before approval.
            </p>

            <div className="detail-meta">
              <div>
                <span>SOURCE</span>
                <p>{selectedEvent.source}</p>
              </div>

              <div>
                <span>EVIDENCE</span>
                <div className="no-photo">
                  NO ATTACHED PHOTO
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT */}
          <div className="candidate-section">
            <h3>Candidate activities</h3>

            <div className="candidate-list">
              {selectedEvent.candidates.map((candidate, index) => (
                <div
                  className={`candidate-row ${
                    index === 0 ? "candidate-selected" : ""
                  }`}
                  key={index}
                >
                  <div>
                    <span className="candidate-id">{candidate[0]}</span>
                    <p>{candidate[1]}</p>
                  </div>

                  <strong>{candidate[2]}</strong>
                </div>
              ))}
            </div>

            <div className="planner-decision">
              <span>PLANNER DECISION</span>
              <p>Select the activity that actually occurred</p>

              <div className="decision-buttons">
                <button className="approve-btn">
                  Approve {selectedEvent.candidates[0][0]}
                </button>

                <button className="correct-btn">
                  Correct match
                </button>

                <button className="reject-btn">
                  Reject event
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rq-page">
      <div className="rq-top">
        <div className="rq-unit">
          North Processing Unit <span>LIVE</span>
        </div>

        <div className="rq-awaiting">
          5 awaiting review
        </div>
      </div>

      <div className="rq-heading">
        <h1>Human review queue</h1>
        <p>Only uncertain, ambiguous or conflicting events appear here.</p>
      </div>

      <div className="rq-tabs">
        <button className="rq-active">All 5</button>
        <button>High risk</button>
        <button>Ambiguous</button>
        <button>Evidence conflict</button>
      </div>

      <div className="rq-content">
        <h3>Events requiring planner decision</h3>

        {events.map((item) => (
          <div className="rq-row" key={item.id}>
            <div className="rq-id">{item.id}</div>
            <div className="rq-event">{item.event}</div>
            <div className="rq-match">{item.match}</div>
            <div className="rq-confidence">{item.confidence}</div>

            <button
              className="rq-review"
              onClick={() => setSelectedEvent(item)}
            >
              Review
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}