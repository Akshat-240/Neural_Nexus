import React from "react";
import "../App.css";

function Insights() {
  const watchlist = [
    { id: "PIP-1022", deviation: "-30%", level: "High", type: "high" },
    { id: "PIP-1025", deviation: "-15%", level: "Medium", type: "medium" },
    { id: "PIP-1026", deviation: "-10%", level: "Medium", type: "medium" },
  ];

  const trend = [
    { date: "Aug 28", value: 62 },
    { date: "Aug 29", value: 68 },
    { date: "Aug 30", value: 71 },
    { date: "Aug 31", value: 69 },
    { date: "Sep 1", value: 74 },
    { date: "Sep 2", value: 76 },
    { date: "Sep 3", value: 78 },
  ];

  return (
    <div className="insights-page">

      <div className="insights-header">
        <div>
          <div className="unit-row">
            <span>North Processing Unit</span>
            <span className="live-badge">LIVE</span>
          </div>

          <h1>Execution insights</h1>
          <p>From execution data to actionable project intelligence</p>
        </div>

        <div className="planner-label">Planner</div>
      </div>

      <div className="insights-overview">

        <section className="progress-card">
          <h2>Progress health</h2>
          <p className="section-subtitle">Overall verified progress</p>

          <div className="progress-number">78%</div>

          <div className="progress-track">
            <div className="progress-fill"></div>
          </div>

          <p className="progress-caption">78 / 100 activities on track</p>
        </section>

        <section className="watchlist-card">
          <h2>Deviation watchlist</h2>

          <div className="watchlist-table">
            {watchlist.map((item) => (
              <div className="watchlist-row" key={item.id}>
                <span className="watch-id">{item.id}</span>
                <span className={`deviation ${item.type}`}>
                  {item.deviation}
                </span>
                <span className={`level ${item.type}`}>
                  {item.level}
                </span>
              </div>
            ))}
          </div>
        </section>

      </div>

      <section className="trend-section">
        <h2>Verified execution trend</h2>
        <p className="section-subtitle">
          Last 7 days · verified actual progress
        </p>

        <div className="chart-container">
          {trend.map((item) => (
            <div className="chart-column" key={item.date}>
              <span className="chart-date">{item.date}</span>

              <div className="bar-area">
                <div
                  className="chart-bar"
                  style={{ height: `${item.value * 2.4}px` }}
                ></div>
              </div>

              <span className="chart-value">{item.value}%</span>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
}

export default Insights;