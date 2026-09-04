function Dashboard() {
  const stats = [
    { label: "Active activities", value: "42", detail: "+6 today" },
    { label: "Verified today", value: "18", detail: "+3 today" },
    { label: "Needs review", value: "5", detail: "2 high priority" },
    { label: "Schedule deviation", value: "3", detail: "Requires attention" },
  ]

  return (
    <div className="dashboard">
      <div className="top-header">
        <div>
          <h1>Project Control Center</h1>
          <p>Verified execution intelligence for North Processing Unit</p>
        </div>

        <div className="project-status">
          <span>North Processing Unit</span>
          <span className="live-badge">LIVE</span>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {stats.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <p>{stat.label}</p>
            <h2>{stat.value}</h2>
            <span>{stat.detail}</span>
          </div>
        ))}
      </div>

      {/* Middle section */}
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Execution pipeline</h3>
          <p className="subtext">Today · 24 field events processed</p>

          <div className="pipeline">
            <div><span>CAPTURE</span><b>24</b></div>
            <div><span>EXTRACT</span><b>24</b></div>
            <div><span>MATCH</span><b>21</b></div>
            <div><span>EVIDENCE</span><b>18</b></div>
            <div><span>VERIFY</span><b>18</b></div>
            <div><span>UPDATE</span><b>16</b></div>
          </div>
        </div>

        <div className="dashboard-card attention">
          <h3>Attention required</h3>

          <div className="attention-item">
            <div>
              <b>PIP-1022</b>
              <p>Pipe support installation</p>
            </div>
            <span className="warning">30%</span>
          </div>

          <div className="attention-item">
            <div>
              <b>EVT-0007</b>
              <p>Line 24 work completed</p>
            </div>
            <span>81%</span>
          </div>

          <div className="attention-item">
            <div>
              <b>PIP-1026</b>
              <p>Hydro testing - Unit 3</p>
            </div>
            <span className="review">Review</span>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="dashboard-card recent">
        <h3>Recent verified activity</h3>

        <div className="activity-table">
          <div className="table-header">
            <span>ID</span>
            <span>Activity</span>
            <span>Status</span>
            <span>Confidence</span>
          </div>

          <div className="table-row">
            <span>PIP-1024</span>
            <span>Erect Line 24-XX</span>
            <span className="status completed">Completed</span>
            <span>94%</span>
          </div>

          <div className="table-row">
            <span>PIP-1025</span>
            <span>Spool fabrication</span>
            <span className="status progress">In progress</span>
            <span>89%</span>
          </div>

          <div className="table-row">
            <span>PIP-1021</span>
            <span>Foundation preparation</span>
            <span className="status verified">Verified</span>
            <span>91%</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard