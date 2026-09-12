import React from 'react';

export default function SkillRadar({ skills }) {
  const defaultSkills = {
    'Concurrency & Thread Safety': 84,
    'SOLID: Single Responsibility': 78,
    'SOLID: Open/Closed & Strategy': 88,
    'State Modeling & Encapsulation': 85,
    'Extensibility & Modularity': 80,
  };

  const data = skills || defaultSkills;

  return (
    <div className="competency-card">
      <div style={{ marginBottom: '1.45rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-pearly)', letterSpacing: '-0.01em' }}>
            Skill Breakdown
          </h3>
          <span className="badge badge-easy" style={{ fontSize: '0.68rem', padding: '0.15rem 0.55rem' }}>
            ACTIVE
          </span>
        </div>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
          Average scores across evaluated submissions.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
        {Object.entries(data).map(([skillName, score]) => (
          <div key={skillName}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.85rem',
                marginBottom: '0.4rem',
              }}
            >
              <span style={{ color: 'var(--text-pearly)', fontWeight: 500 }}>{skillName}</span>
              <span
                style={{
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--accent-jungle)',
                  fontWeight: 700,
                }}
              >
                {Math.round(score)}%
              </span>
            </div>
            <div
              style={{
                width: '100%',
                height: '7px',
                background: 'var(--bg-obsidian)',
                borderRadius: '9999px',
                overflow: 'hidden',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div
                style={{
                  width: `${score}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #4A0E2A, var(--accent-jungle), var(--accent-mint))',
                  borderRadius: '9999px',
                  boxShadow: '0 0 10px rgba(244, 63, 133, 0.45)',
                  transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: '1.75rem',
          padding: '0.85rem 1.1rem',
          background: 'var(--bg-surface-elevated)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.82rem',
          color: 'var(--text-secondary)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: 'var(--inner-highlight)',
        }}
      >
        <span>Target Benchmark</span>
        <span style={{ color: 'var(--accent-jungle)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
          &gt; 75% Target
        </span>
      </div>
    </div>
  );
}
