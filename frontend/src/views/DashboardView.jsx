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
          <span>ARCHITECT SANDBOX • LLD EVALUATION ENGINE</span>
        </div>
        <h1 className="hero-headline">
          Low-Level Design Practice &amp; Assessment Studio
        </h1>
        <p className="hero-description">
          Practice object-oriented architecture, receive dual-engine deterministic AST &amp; LLM trade-off feedback, and iteratively refine your designs to production grade.
        </p>
      </div>

      {/* Summary Stats Row */}
      <div className="stats-grid">
        <StatCard
          label="COMPLETED ATTEMPTS"
          value={metrics.completed_count || '10'}
          placeholderTag="[METRIC_COMPLETED_10]"
          subtext="↑ 3 attempts completed this week"
          iconText="✓"
        />
        <StatCard
          label="AVERAGE LLD SCORE"
          value={`${metrics.average_score || 83.5}%`}
          placeholderTag="[PERCENTILE_8_STAFF]"
          subtext="Calibrated against Staff L6 bar"
          iconText="★"
        />
        <StatCard
          label="PRACTICE STREAK"
          value={`${metrics.streak || 5} Days`}
          placeholderTag="[STREAK_5_DAYS]"
          subtext="Consistent problem solving cadence"
          iconText="⚡"
        />
        <StatCard
          label="SYSTEM READINESS"
          value="85%"
          placeholderTag="[TIER_1_READINESS_85%]"
          subtext="Production architecture ready"
          iconText="⬢"
        />
      </div>

      {/* Main Grid: Problem Catalog & Skill Competency */}
      <div className="dashboard-grid">
        <div>
          <div className="section-header">
            <div>
              <h2 className="section-title">Curated LLD Curriculum</h2>
              <p className="section-subtitle">
                Foundational architecture problems testing design patterns, thread safety, and extensibility.
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
                    {prob.functional_requirements.length} Core Requirements
                  </span>
                  <button
                    className="btn btn-primary"
                    style={{ padding: '0.5rem 1.1rem', fontSize: '0.84rem' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectProblem(prob);
                    }}
                  >
                    Open Studio →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Skill Mastery Radar Panel */}
        <div>
          <div className="section-header">
            <div>
              <h2 className="section-title">Competency Radar</h2>
              <p className="section-subtitle">AST &amp; LLM Evaluated</p>
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
            <h2 className="section-title">Active Assessments &amp; Attempt History</h2>
            <p className="section-subtitle">
              Inspect submission status, deterministic AST breakdowns, and architectural trade-off feedback.
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
            No submission records match your filter criteria. Pick a problem above to start an attempt!
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
                        {sub.grade.split(' ')[0]}
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
                      Inspect Result →
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
