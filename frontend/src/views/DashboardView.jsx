import React, { useState } from 'react';
import StatCard from '../components/StatCard';
import SkillRadar from '../components/SkillRadar';

export default function DashboardView({
  problems,
  stats,
  onSelectProblem,
  onViewSubmission,
  setView,
}) {
  const [filterProblem, setFilterProblem] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const metrics = stats?.metrics || {
    total_attempts: 12,
    completed_count: 10,
    average_score: 83.5,
    streak: 5,
    readiness_rate: 85.0,
  };

  const activity = stats?.recent_activity || [];

  const filteredActivity = activity.filter((item) => {
    if (filterProblem !== 'ALL' && item.problem_id !== filterProblem) return false;
    if (filterStatus !== 'ALL' && item.status !== filterStatus) return false;
    if (
      searchQuery &&
      !item.problem_title.toLowerCase().includes(searchQuery.toLowerCase())
    )
      return false;
    return true;
  });

  return (
    <div>
      {/* Hero Header Section */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div className="hero-badge">
          <span>✦</span>
          <span>PRACTICE &amp; FEEDBACK</span>
        </div>
        <h1 className="hero-headline">
          Low-Level Design Practice
        </h1>
        <p className="hero-description">
          Practice object-oriented design problems, check your class structure, and get feedback on design trade-offs.
        </p>
      </div>

      {/* Summary Stats Row */}
      <div className="stats-grid">
        <StatCard
          label="Completed Attempts"
          value={metrics.completed_count || '10'}
          subtext="Total submitted solutions"
          iconText="✓"
        />
        <StatCard
          label="Average Score"
          value={`${metrics.average_score || '83.5'}%`}
          subtext="Across all rubric criteria"
          iconText="★"
        />
        <StatCard
          label="Current Streak"
          value={`${metrics.streak || '5'} days`}
          subtext="Daily active practice"
          iconText="⚡"
        />
        <StatCard
          label="Readiness Score"
          value={`${metrics.readiness_rate || '85'}%`}
          subtext="Based on completed attempts"
          iconText="⬢"
        />
      </div>

      {/* Main Grid: Problem Catalog & Skill Competency */}
      <div className="dashboard-grid">
        <div>
          <div className="section-header">
            <div>
              <h2 className="section-title">Problems</h2>
              <p className="section-subtitle">
                Choose a problem to start practicing.
              </p>
            </div>
          </div>

          <div className="problems-grid">
            {problems.map((prob) => (
              <div
                key={prob.id}
                className="problem-card"
                onClick={() => onSelectProblem(prob)}
              >
                <div>
                  <div className="problem-meta">
                    <span className={`badge badge-${prob.difficulty.toLowerCase()}`}>
                      {prob.difficulty}
                    </span>
                    <span className="badge badge-domain">{prob.domain}</span>
                  </div>
                  <h3 className="problem-title">{prob.title}</h3>
                  <p className="problem-desc">{prob.summary}</p>
                </div>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    paddingTop: '1.15rem',
                    borderTop: '1px solid var(--border-subtle)',
                  }}
                >
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {prob.functional_requirements.length} Requirements
                  </span>
                  <button
                    className="btn btn-primary"
                    style={{ padding: '0.5rem 1.1rem', fontSize: '0.84rem' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectProblem(prob);
                    }}
                  >
                    Start Problem →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Skill Breakdown Panel */}
        <div>
          <div className="section-header">
            <div>
              <h2 className="section-title">Skills Breakdown</h2>
              <p className="section-subtitle">Across evaluated submissions</p>
            </div>
          </div>
          <SkillRadar skills={stats?.skill_radar} />
        </div>
      </div>

      {/* Submissions & Assessment Activity Table */}
      <div className="card">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            marginBottom: '1.45rem',
          }}
        >
          <div>
            <h2 className="section-title">Recent Submissions</h2>
            <p className="section-subtitle">
              View submission status, score breakdowns, and feedback.
            </p>
          </div>

          {/* Filter Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
            <input
              type="text"
              placeholder="Search problem..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: 'var(--bg-obsidian)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-pearly)',
                padding: '0.5rem 0.95rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.84rem',
                outline: 'none',
              }}
            />

            <select
              value={filterProblem}
              onChange={(e) => setFilterProblem(e.target.value)}
              style={{
                background: 'var(--bg-obsidian)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-pearly)',
                padding: '0.5rem 0.95rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.84rem',
                outline: 'none',
              }}
            >
              <option value="ALL">All Problems</option>
              {problems.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{
                background: 'var(--bg-obsidian)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-pearly)',
                padding: '0.5rem 0.95rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.84rem',
                outline: 'none',
              }}
            >
              <option value="ALL">All Statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="EVALUATING">Evaluating</option>
              <option value="PENDING">Pending</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>
        </div>

        {filteredActivity.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '3.5rem 1rem',
              color: 'var(--text-muted)',
              fontSize: '0.92rem',
            }}
          >
            No submissions match the selected filters. Choose a problem above to get started.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Problem Title</th>
                <th>Submission ID</th>
                <th>Status</th>
                <th>Score</th>
                <th>Grade</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredActivity.map((sub) => (
                <tr key={sub.submission_id}>
                  <td style={{ fontWeight: 600 }}>{sub.problem_title}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {sub.submission_id.substring(0, 8)}...
                  </td>
                  <td>
                    <span className={`status-pill status-${sub.status.toLowerCase()}`}>
                      {sub.status === 'EVALUATING' && <span className="pulse-dot" />}
                      {sub.status}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--accent-jungle)' }}>
                    {sub.score !== null && sub.score !== undefined ? `${sub.score}%` : '—'}
                  </td>
                  <td>
                    {sub.grade ? (
                      <span
                        style={{
                          fontSize: '0.78rem',
                          padding: '0.22rem 0.6rem',
                          borderRadius: 'var(--radius-sm)',
                          background: 'var(--bg-surface-hover)',
                          color: 'var(--text-pearly)',
                          fontFamily: 'var(--font-mono)',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        {sub.grade.replace('Grade ', '')}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {sub.created_at ? new Date(sub.created_at).toLocaleTimeString() : 'Recent'}
                  </td>
                  <td>
                    <button
                      className="btn btn-outline"
                      style={{ padding: '0.38rem 0.85rem', fontSize: '0.8rem' }}
                      onClick={() => onViewSubmission(sub.submission_id)}
                    >
                      View Feedback →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
