function FieldEvents() {
  const events = [
    {
      id: "EVT-1007",
      activity: "Pipeline inspection completed",
      location: "North Processing Unit",
      time: "Today, 10:42 AM",
      status: "Verified",
      confidence: "94%",
    },
    {
      id: "EVT-1008",
      activity: "Hydraulic pressure test",
      location: "Unit 3",
      time: "Today, 09:15 AM",
      status: "Under Review",
      confidence: "78%",
    },
    {
      id: "EVT-1009",
      activity: "Valve replacement",
      location: "Field Zone B",
      time: "Yesterday, 04:30 PM",
      status: "Verified",
      confidence: "97%",
    },
  ];

  return (
    <div className="field-events">
      <div className="page-header">
        <div>
          <h1>Field Events</h1>
          <p>Monitor and verify real-time field activities</p>
        </div>

        <button className="primary-btn">+ New Event</button>
      </div>

      <div className="events-summary">
        <div className="summary-card">
          <span>Total Events</span>
          <h2>24</h2>
        </div>

        <div className="summary-card">
          <span>Verified</span>
          <h2>18</h2>
        </div>

        <div className="summary-card">
          <span>Under Review</span>
          <h2>4</h2>
        </div>

        <div className="summary-card">
          <span>Flagged</span>
          <h2>2</h2>
        </div>
      </div>

      <div className="events-card">
        <div className="card-header">
          <h3>Recent Field Events</h3>
          <input
            type="text"
            placeholder="Search events..."
            className="search-input"
          />
        </div>

        <div className="events-table">
          <div className="table-head">
            <span>Event ID</span>
            <span>Activity</span>
            <span>Location</span>
            <span>Time</span>
            <span>Status</span>
            <span>Confidence</span>
          </div>

          {events.map((event) => (
            <div className="table-row" key={event.id}>
              <span className="event-id">{event.id}</span>
              <span>{event.activity}</span>
              <span>{event.location}</span>
              <span>{event.time}</span>

              <span
                className={`event-status ${
                  event.status === "Verified"
                    ? "verified"
                    : "review"
                }`}
              >
                {event.status}
              </span>

              <span className="confidence">{event.confidence}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default FieldEvents;