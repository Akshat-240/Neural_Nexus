import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import FieldCapture from './pages/FieldCapture'
import FieldEvents from './pages/FieldEvents'
import ReviewQueue from './pages/ReviewQueue'
import Schedule from './pages/Schedule'
import Evidence from './pages/Evidence'
import Insights from './pages/Insights'

import './App.css'

function App() {
  return (
    <div className="app-layout">
      
      <aside className="sidebar">
        <div className="logo">
          <h2>NEURAL<br />NEXUS</h2>
          <span>EXECUTION INTELLIGENCE</span>
        </div>

        <nav>
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/field-capture">Field Capture</NavLink>
          <NavLink to="/field-events">Field Events</NavLink>
          <NavLink to="/review-queue">Review Queue</NavLink>
          <NavLink to="/schedule">Schedule</NavLink>
          <NavLink to="/evidence">Evidence</NavLink>
          <NavLink to="/insights">Insights</NavLink>
        </nav>
      </aside>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/field-capture" element={<FieldCapture />} />
          <Route path="/field-events" element={<FieldEvents />} />
          <Route path="/review-queue" element={<ReviewQueue />} />
          <Route path="/schedule" element={<Schedule />} />
          <Route path="/evidence" element={<Evidence />} />
          <Route path="/insights" element={<Insights />} />
        </Routes>
      </main>

    </div>
  )
}

export default App