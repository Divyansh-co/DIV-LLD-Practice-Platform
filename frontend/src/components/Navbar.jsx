import React from 'react';

export default function Navbar({ currentView, setView, activeProblem }) {
  return (
    <nav className="navbar">
      <div className="nav-brand" onClick={() => setView('dashboard')}>
        <div className="brand-badge">LD</div>
        <div>
          <span className="brand-title">LLD Studio</span>
          <span className="brand-subtitle">Architect Sandbox</span>
        </div>
      </div>

      <div className="nav-links">
        <button
          className={`nav-btn ${currentView === 'dashboard' ? 'active' : ''}`}
          onClick={() => setView('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`nav-btn ${currentView === 'practice' ? 'active' : ''}`}
          onClick={() => setView('practice')}
        >
          Practice Studio {activeProblem ? `(${activeProblem.title.split(' ')[2] || 'Active'})` : ''}
        </button>
        <button
          className={`nav-btn ${currentView === 'history' ? 'active' : ''}`}
          onClick={() => setView('history')}
        >
          Attempt History
        </button>
      </div>

      <div className="user-profile-widget">
        <div className="profile-avatar">DM</div>
        <div className="profile-info">
          <span className="profile-name">Divyansh Mishra</span>
          <span className="profile-role">Lead Architect • 5d Streak</span>
        </div>
      </div>
    </nav>
  );
}
