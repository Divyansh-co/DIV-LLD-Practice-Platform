import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function HistoryView({
  problems,
  activeProblem,
  onSelectSubmission,
  onStartNewAttempt,
}) {
  const [selectedProblemId, setSelectedProblemId] = useState(
    activeProblem?.id || problems[0]?.id || 'prob_parking_lot'
  );
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const currentProblem = problems.find(
    (p) => p.id === selectedProblemId || p.slug === selectedProblemId
  );

  useEffect(() => {
    async function loadHistory() {
      if (!selectedProblemId) return;
      setLoading(true);
      try {
        const records = await api.getProblemHistory(selectedProblemId);
        setHistory(records);
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [selectedProblemId]);

  return (
    <div>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '2rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '0.35rem' }}>
            Attempt History
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
            See past attempts and track your progress on each problem.
          </p>
        </div>

        {/* Problem Filter Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {problems.map((p) => (
            <button
              key={p.id}
              className={`btn ${selectedProblemId === p.id || selectedProblemId === p.slug ? 'btn-primary' : 'btn-outline'}`}
              style={{ fontSize: '0.82rem' }}
              onClick={() => setSelectedProblemId(p.id)}
            >
              {p.title.split(' ')[2] || p.title}
            </button>
          ))}
        </div>
      </div>

      {/* Selected Problem Overview Banner */}
      {currentProblem && (
        <div
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem 1.5rem',
            marginBottom: '2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.25rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 600 }}>{currentProblem.title}</h2>
              <span className={`badge badge-${currentProblem.difficulty.toLowerCase()}`}>
                {currentProblem.difficulty}
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              {currentProblem.summary}
            </p>
          </div>

          <button
            className="btn btn-primary"
            style={{ fontSize: '0.85rem' }}
            onClick={() => onStartNewAttempt(currentProblem)}
          >
            Try Again →
          </button>
        </div>
      )}

      {/* Timeline List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading attempt history...
        </div>
      ) : history.length === 0 ? (
        <div
          className="card"
          style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-muted)' }}
        >
          No submissions recorded for this problem yet. Start an attempt to submit your first solution.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {history.map((item, index) => {
            const attemptNumber = history.length - index;
            const prevItem = index < history.length - 1 ? history[index + 1] : null;
            const scoreDelta =
              item.score !== null && prevItem && prevItem.score !== null
                ? Math.round((item.score - prevItem.score) * 10) / 10
                : null;

            return (
              <div
                key={item.submission_id}
                className="card"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '1rem',
                  borderLeft: '4px solid var(--accent-jungle)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem' }}>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 700,
                        fontSize: '1rem',
                        color: 'var(--text-pearly)',
                      }}
                    >
                      Attempt #{attemptNumber}
                    </span>
                    <span className={`status-pill status-${item.status.toLowerCase()}`}>
                      {item.status}
                    </span>
                    {item.grade && (
                      <span
                        style={{
                          fontSize: '0.75rem',
                          background: 'var(--bg-surface-elevated)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--accent-jungle)',
                          fontFamily: 'var(--font-mono)',
                        }}
                      >
                        {item.grade}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Submitted {new Date(item.created_at).toLocaleString()} • {item.passed_checks_count}/{item.total_checks_count} Checks Passed
                  </div>
                </div>

                {/* Score & Progression Delta */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
                      {item.score !== null ? `${item.score}%` : '—'}
                    </div>
                    {scoreDelta !== null && (
                      <div
                        style={{
                          fontSize: '0.78rem',
                          fontFamily: 'var(--font-mono)',
                          color: scoreDelta >= 0 ? 'var(--status-completed)' : 'var(--status-failed)',
                        }}
                      >
                        {scoreDelta >= 0 ? `+${scoreDelta}%` : `${scoreDelta}%`}
                      </div>
                    )}
                  </div>

                  <button
                    className="btn btn-outline"
                    onClick={() => onSelectSubmission(item.submission_id)}
                    style={{ fontSize: '0.82rem' }}
                  >
                    View Feedback →
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
