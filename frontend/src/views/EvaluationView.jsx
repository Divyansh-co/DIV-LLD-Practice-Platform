import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function EvaluationView({
  submissionId,
  onIterate,
  onViewHistory,
  onBackToDashboard,
}) {
  const [submission, setSubmission] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('rubric'); // 'rubric' | 'checks' | 'llm' | 'refactor'
  const [isRetrying, setIsRetrying] = useState(false);

  // Poll for evaluation completion
  useEffect(() => {
    let intervalId;
    let isMounted = true;

    async function fetchStatus() {
      try {
        const data = await api.getSubmission(submissionId);
        if (!isMounted) return;

        setSubmission(data);
        if (data.evaluation) {
          setEvaluation(data.evaluation);
          setLoading(false);
          clearInterval(intervalId);
        } else if (data.status === 'FAILED') {
          setError(data.error_message || 'Evaluation pipeline failed');
          setLoading(false);
          clearInterval(intervalId);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    }

    fetchStatus();
    intervalId = setInterval(fetchStatus, 800);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [submissionId]);

  const handleRetry = async () => {
    setIsRetrying(true);
    try {
      await api.retrySubmission(submissionId);
      setLoading(true);
      setError(null);
    } catch (err) {
      alert(`Retry failed: ${err.message}`);
    } finally {
      setIsRetrying(false);
    }
  };

  if (loading && (!submission || submission.status !== 'COMPLETED')) {
    return (
      <div style={{ maxWidth: '800px', margin: '4rem auto', textAlign: 'center' }}>
        <div
          style={{
            background: 'var(--bg-surface-translucent)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '3.5rem 2.5rem',
            boxShadow: 'var(--inner-highlight)',
          }}
        >
          <div
            style={{
              width: '52px',
              height: '52px',
              borderRadius: '50%',
              border: '3.5px solid var(--border-subtle)',
              borderTopColor: 'var(--accent-jungle)',
              animation: 'spin 0.9s linear infinite',
              margin: '0 auto 1.5rem',
            }}
          />
          <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.5rem' }}>
            Evaluating Low-Level Design Solution
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '2rem' }}>
            Running deterministic AST static analysis &amp; 8-dimension structured AI rubric synthesis...
          </p>

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              maxWidth: '560px',
              margin: '0 auto',
              fontSize: '0.84rem',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            <span>[1] Persisted Snapshot ✓</span>
            <span style={{ color: 'var(--accent-jungle)' }}>[2] AST Structural Checks •</span>
            <span>[3] 8-Dimension Rubric</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '720px', margin: '4rem auto' }}>
        <div
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--status-failed)',
            borderRadius: 'var(--radius-md)',
            padding: '2.5rem',
            textAlign: 'center',
          }}
        >
          <h2 style={{ color: 'var(--status-failed)', marginBottom: '0.75rem', fontWeight: 800 }}>
            Evaluation Pipeline Exception
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.75rem', fontSize: '0.92rem' }}>
            {error}
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
            <button className="btn btn-primary" onClick={handleRetry} disabled={isRetrying}>
              {isRetrying ? 'Retrying...' : 'Retry Evaluation ↺'}
            </button>
            <button className="btn btn-outline" onClick={onBackToDashboard}>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!evaluation) return null;

  const passedChecksCount = evaluation.checks.filter((c) => c.passed).length;
  const totalChecksCount = evaluation.checks.length;
  const dimensions = evaluation.dimensions || [];

  return (
    <div>
      {/* Top Header & Actions */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.75rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <button
            className="btn btn-outline"
            onClick={onBackToDashboard}
            style={{ fontSize: '0.84rem', marginBottom: '0.6rem' }}
          >
            ← Back to Dashboard
          </button>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Evaluation &amp; Architecture Assessment
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Submission ID: <span style={{ fontFamily: 'var(--font-mono)' }}>{submissionId}</span> • Executed in {evaluation.execution_time_ms}ms
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.85rem' }}>
          <button className="btn btn-secondary" onClick={onViewHistory}>
            Progression Timeline 📈
          </button>
          <button className="btn btn-primary" onClick={onIterate}>
            Refine in Studio (Next Iteration) →
          </button>
        </div>
      </div>

      {/* Hero Score Gauge */}
      <div className="score-gauge-box">
        <div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.06em', marginBottom: '0.35rem', textTransform: 'uppercase' }}>
            OVERALL ARCHITECTURAL SCORE
          </div>
          <div className="score-main">
            <span className="score-number">{evaluation.overall_score}</span>
            <span className="score-max">/ 100</span>
          </div>
          <div style={{ marginTop: '0.65rem', fontSize: '0.9rem', color: 'var(--text-pearly)' }}>
            Deterministic AST Checks: <strong style={{ color: 'var(--accent-jungle)' }}>{evaluation.deterministic_score}/40</strong> • AI Rubric Dimensions: <strong style={{ color: 'var(--accent-mint)' }}>{evaluation.ai_score || evaluation.llm_score}/60</strong>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div className="grade-pill">{evaluation.grade}</div>
          <div
            style={{
              marginTop: '0.85rem',
              fontSize: '0.84rem',
              color: 'var(--text-secondary)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {passedChecksCount} of {totalChecksCount} Structural Invariants Verified
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div
        style={{
          display: 'flex',
          gap: '0.75rem',
          borderBottom: '1px solid var(--border-subtle)',
          marginBottom: '1.75rem',
          paddingBottom: '0.5rem',
          flexWrap: 'wrap',
        }}
      >
        <button
          className={`panel-tab ${activeTab === 'rubric' ? 'active' : ''}`}
          onClick={() => setActiveTab('rubric')}
          style={{ fontSize: '0.92rem', padding: '0.5rem 1.15rem' }}
        >
          8-Dimension Rubric Matrix ({dimensions.length})
        </button>
        <button
          className={`panel-tab ${activeTab === 'checks' ? 'active' : ''}`}
          onClick={() => setActiveTab('checks')}
          style={{ fontSize: '0.92rem', padding: '0.5rem 1.15rem' }}
        >
          Deterministic AST Checks ({passedChecksCount}/{totalChecksCount})
        </button>
        <button
          className={`panel-tab ${activeTab === 'llm' ? 'active' : ''}`}
          onClick={() => setActiveTab('llm')}
          style={{ fontSize: '0.92rem', padding: '0.5rem 1.15rem' }}
        >
          Trade-off &amp; Edge Cases
        </button>
        <button
          className={`panel-tab ${activeTab === 'refactor' ? 'active' : ''}`}
          onClick={() => setActiveTab('refactor')}
          style={{ fontSize: '0.92rem', padding: '0.5rem 1.15rem' }}
        >
          Recommended Code Refactor
        </button>
      </div>

      {/* Tab 1: 8-Dimension Structured Rubric Matrix */}
      {activeTab === 'rubric' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div
            style={{
              background: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '1rem 1.25rem',
              fontSize: '0.86rem',
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <span>
              Each criterion is evaluated via structured shape: <code>criterion → score → evidence → concern → suggestion → confidence</code>
            </span>
            <span style={{ color: 'var(--accent-jungle)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
              Weighted 60% of Total Score
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
            {dimensions.map((dim, idx) => (
              <div
                key={idx}
                className="card"
                style={{
                  borderLeft: `4px solid ${dim.score >= 6.5 ? 'var(--accent-jungle)' : 'var(--status-pending)'}`,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.65rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <h3 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-pearly)' }}>
                    {dim.criterion}
                  </h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span
                      style={{
                        fontSize: '0.74rem',
                        fontFamily: 'var(--font-mono)',
                        color: 'var(--text-muted)',
                        background: 'var(--bg-obsidian)',
                        padding: '0.15rem 0.45rem',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      {Math.round(dim.confidence * 100)}% conf
                    </span>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 700,
                        color: 'var(--accent-jungle)',
                        fontSize: '0.95rem',
                      }}
                    >
                      {dim.score} / {dim.max_score}
                    </span>
                  </div>
                </div>

                <div>
                  <strong style={{ fontSize: '0.78rem', color: 'var(--accent-mint)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Candidate Evidence
                  </strong>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                    {dim.evidence}
                  </p>
                </div>

                <div>
                  <strong style={{ fontSize: '0.78rem', color: 'var(--status-pending)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Architectural Concern
                  </strong>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                    {dim.concern}
                  </p>
                </div>

                <div
                  style={{
                    background: 'rgba(0, 0, 0, 0.35)',
                    padding: '0.65rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <strong style={{ fontSize: '0.78rem', color: 'var(--accent-jungle)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Actionable Suggestion
                  </strong>
                  <p style={{ fontSize: '0.84rem', color: 'var(--text-pearly)', marginTop: '0.2rem' }}>
                    {dim.suggestion}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Deterministic AST Checks */}
      {activeTab === 'checks' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {evaluation.checks.map((check) => (
            <div
              key={check.rule_id}
              className={`check-item ${check.passed ? 'passed' : 'failed'}`}
            >
              <div className="check-item-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 700,
                      color: check.passed ? 'var(--status-completed)' : 'var(--status-failed)',
                    }}
                  >
                    {check.passed ? '✓ PASSED' : '✕ FAILED'}
                  </span>
                  <span className="check-title">{check.rule_name}</span>
                  <span className="badge badge-domain" style={{ fontSize: '0.7rem' }}>
                    {check.category}
                  </span>
                </div>
                <div
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.9rem',
                    color: check.passed ? 'var(--accent-jungle)' : 'var(--text-muted)',
                    fontWeight: 700,
                  }}
                >
                  +{check.score} / {check.max_score} pts
                </div>
              </div>

              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {check.message}
              </p>

              {check.code_reference && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  {check.code_reference}
                </div>
              )}

              {check.suggestion && (
                <div className="check-suggestion">
                  <strong>Recommendation:</strong> {check.suggestion}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: LLM Trade-off Analysis */}
      {activeTab === 'llm' && evaluation.llm_feedback && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Executive Summary */}
          <div className="card">
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--accent-jungle)' }}>
              Executive Architectural Assessment
            </h3>
            <p style={{ color: 'var(--text-pearly)', fontSize: '0.94rem', lineHeight: 1.65 }}>
              {evaluation.llm_feedback.summary}
            </p>
          </div>

          {/* Trade-offs & Extensibility */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.65rem', color: 'var(--text-pearly)' }}>
                Design Trade-offs &amp; Bottlenecks
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', whiteSpace: 'pre-line', lineHeight: 1.6 }}>
                {evaluation.llm_feedback.trade_off_analysis}
              </p>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.65rem', color: 'var(--text-pearly)' }}>
                Extensibility &amp; Edge Cases
              </h3>
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ fontSize: '0.86rem', color: 'var(--accent-mint)' }}>Extensibility:</strong>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
                  {evaluation.llm_feedback.extensibility_critique}
                </p>
              </div>
              <div>
                <strong style={{ fontSize: '0.86rem', color: 'var(--accent-mint)' }}>Edge Cases:</strong>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
                  {evaluation.llm_feedback.edge_cases_analysis}
                </p>
              </div>
            </div>
          </div>

          {/* Alternative Approaches */}
          {evaluation.llm_feedback.alternative_approaches?.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-pearly)' }}>
                Alternative Production Topologies
              </h3>
              <ul style={{ paddingLeft: '1.35rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                {evaluation.llm_feedback.alternative_approaches.map((alt, idx) => (
                  <li key={idx} style={{ marginBottom: '0.45rem' }}>{alt}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Recommended Refactor Diff */}
      {activeTab === 'refactor' && evaluation.llm_feedback && (
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-pearly)' }}>
            Concrete Refactoring Transformation
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Compare your submission against this target refactored snippet demonstrating fine-grained locking and clean interface decoupling:
          </p>
          <div className="code-diff-block">
            {evaluation.llm_feedback.suggested_refactor_diff}
          </div>
        </div>
      )}
    </div>
  );
}
