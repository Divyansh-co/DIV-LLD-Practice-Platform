import React from 'react';

export default function Navbar({ currentView, setView, activeProblem }) {
  return (
    <nav className="navbar">
      <div className="nav-brand" onClick={() => setView('dashboard')}>
        <div className="brand-badge">LD</div>
        <div>
          <span className="brand-title">LLD Practice</span>
          <span className="brand-subtitle">Design Platform</span>
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
          Practice {activeProblem ? `(${activeProblem.title.split(' ')[2] || 'Active'})` : ''}
        </button>
        <button
          className={`nav-btn ${currentView === 'history' ? 'active' : ''}`}
          onClick={() => setView('history')}
        >
          History
        </button>
      </div>

      <div className="user-profile-widget">
        <div className="profile-avatar">DM</div>
        <div className="profile-info">
          <span className="profile-name">Divyansh Mishra</span>
          <span className="profile-role">5-Day Streak</span>
        </div>
      </div>
    </nav>
  );
}
