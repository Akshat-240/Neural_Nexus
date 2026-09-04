import React from "react";
import "../App.css";

export default function Schedule() {
  const scheduleItems = [
    {
      time: "08:00",
      title: "Line 24 spool installation",
      unit: "Unit 3",
      type: "Planned work",
      status: "Scheduled",
    },
    {
      time: "10:30",
      title: "Valve inspection",
      unit: "North Processing Unit",
      type: "Inspection",
      status: "Scheduled",
    },
    {
      time: "13:00",
      title: "Hydrostatic pressure test",
      unit: "Unit 2",
      type: "Testing",
      status: "Pending",
    },
    {
      time: "15:30",
      title: "Pipeline welding activity",
      unit: "Line 24",
      type: "Field work",
      status: "Scheduled",
    },
    {
      time: "17:00",
      title: "End of day inspection",
      unit: "North Processing Unit",
      type: "Inspection",
      status: "Upcoming",
    },
  ];

  return (
    <div className="sch-page">

      <div className="sch-top">
        <div className="sch-unit">
          North Processing Unit
          <span>LIVE</span>
        </div>

        <button className="sch-add-btn">+ Add schedule</button>
      </div>

      <div className="sch-heading">
        <h1>Schedule</h1>
        <p>Planned work and operational activities for today.</p>
      </div>

      <div className="sch-toolbar">
        <div className="sch-date">
          <span className="sch-arrow">‹</span>
          <div>
            <strong>Today</strong>
            <small>03 September 2026</small>
          </div>
          <span className="sch-arrow">›</span>
        </div>

        <div className="sch-view">
          <button className="sch-view-active">Day</button>
          <button>Week</button>
        </div>
      </div>

      <div className="sch-content">
        <div className="sch-column-label">TODAY'S OPERATIONS</div>

        <div className="sch-list">
          {scheduleItems.map((item, index) => (
            <div className="sch-row" key={index}>
              
              <div className="sch-time">{item.time}</div>

              <div className="sch-line"></div>

              <div className="sch-details">
                <div className="sch-title">{item.title}</div>
                <div className="sch-meta">
                  {item.unit} <span>•</span> {item.type}
                </div>
              </div>

              <div className={`sch-status ${item.status.toLowerCase()}`}>
                {item.status}
              </div>

            </div>
          ))}
        </div>
      </div>

      <div className="sch-side-note">
        <span>5</span>
        activities scheduled today
      </div>

    </div>
  );
}