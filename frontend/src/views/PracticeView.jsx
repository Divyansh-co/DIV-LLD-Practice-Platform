import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';

export default function PracticeView({
  problem,
  onBack,
  onSubmitSuccess,
}) {
  const [leftTab, setLeftTab] = useState('requirements'); // 'requirements' | 'rubric'
  const [rightTab, setRightTab] = useState('code'); // 'code' | 'notes' | 'diagram'
  const [code, setCode] = useState(problem.starter_code || '');
  const [notes, setNotes] = useState(problem.default_notes_template || '');
  const [diagramDsl, setDiagramDsl] = useState(problem.starter_diagram_dsl || '');
  const [attemptId, setAttemptId] = useState(null);
  const [saveStatus, setSaveStatus] = useState('idle'); // 'idle' | 'saving' | 'saved'
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sanityResults, setSanityResults] = useState(null);
  const autoSaveTimerRef = useRef(null);

  // Initialize or resume attempt
  useEffect(() => {
    async function initAttempt() {
      try {
        const attempt = await api.startAttempt(problem.id);
        setAttemptId(attempt.id);
        if (attempt.code) setCode(attempt.code);
        if (attempt.design_notes) setNotes(attempt.design_notes);
        if (attempt.diagram_dsl) setDiagramDsl(attempt.diagram_dsl);
      } catch (err) {
        console.error('Failed to initialize attempt:', err);
      }
    }
    initAttempt();
  }, [problem.id]);

  // Debounced Auto-Save
  useEffect(() => {
    if (!attemptId) return;

    setSaveStatus('saving');
    if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);

    autoSaveTimerRef.current = setTimeout(async () => {
      try {
        await api.saveDraft(attemptId, code, notes, diagramDsl);
        setSaveStatus('saved');
      } catch (err) {
        console.error('Auto-save error:', err);
        setSaveStatus('error');
      }
    }, 2000);

    return () => clearTimeout(autoSaveTimerRef.current);
  }, [code, notes, diagramDsl, attemptId]);

  const handleManualSave = async () => {
    if (!attemptId) return;
    setSaveStatus('saving');
    try {
      await api.saveDraft(attemptId, code, notes, diagramDsl);
      setSaveStatus('saved');
    } catch (err) {
      setSaveStatus('error');
    }
  };

  const handleSubmit = async () => {
    if (!attemptId) return;
    setIsSubmitting(true);
    try {
      // Save draft first
      await api.saveDraft(attemptId, code, notes, diagramDsl);
      // Submit
      const submission = await api.submitAttempt(attemptId);
      onSubmitSuccess(submission.id);
    } catch (err) {
      alert(`Submission failed: ${err.message}`);
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      {/* Studio Top Control Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.25rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="btn btn-outline" onClick={onBack} style={{ fontSize: '0.82rem' }}>
            ← Back to Problems
          </button>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 700 }}>{problem.title}</h1>
              <span className={`badge badge-${problem.difficulty.toLowerCase()}`}>
                {problem.difficulty}
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Domain: {problem.domain}
            </div>
          </div>
        </div>

        {/* Action Controls & Auto-save status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <span
            style={{
              fontSize: '0.78rem',
              color: saveStatus === 'saved' ? 'var(--accent-jungle)' : 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            {saveStatus === 'saving' && 'Saving draft...'}
            {saveStatus === 'saved' && '✓ Draft saved'}
            {saveStatus === 'error' && '⚠ Save failed'}
          </span>

          <button
            className="btn btn-secondary"
            onClick={handleManualSave}
            style={{ fontSize: '0.82rem' }}
          >
            Save Draft
          </button>

          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={isSubmitting}
            style={{ fontSize: '0.88rem' }}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Solution →'}
          </button>
        </div>
      </div>

      {/* Main Studio Split Layout */}
      <div className="studio-layout">
        {/* Left Panel: Problem Specification */}
        <div className="studio-panel">
          <div className="panel-header">
            <span className="panel-title">Problem Description</span>
            <div className="panel-tabs">
              <button
                className={`panel-tab ${leftTab === 'requirements' ? 'active' : ''}`}
                onClick={() => setLeftTab('requirements')}
              >
                Requirements
              </button>
              <button
                className={`panel-tab ${leftTab === 'rubric' ? 'active' : ''}`}
                onClick={() => setLeftTab('rubric')}
              >
                Rubric
              </button>
            </div>
          </div>

          <div className="panel-body">
            {leftTab === 'requirements' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div>
                  <h4 style={{ fontSize: '0.88rem', color: 'var(--accent-jungle)', marginBottom: '0.35rem' }}>
                    Summary
                  </h4>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                    {problem.summary}
                  </p>
                </div>

                <div>
                  <h4 style={{ fontSize: '0.88rem', color: 'var(--text-pearly)', marginBottom: '0.5rem' }}>
                    Functional Requirements
                  </h4>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {problem.functional_requirements.map((req, idx) => (
                      <li key={idx} style={{ marginBottom: '0.4rem' }}>{req}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 style={{ fontSize: '0.88rem', color: 'var(--text-pearly)', marginBottom: '0.5rem' }}>
                    Non-Functional Requirements
                  </h4>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {problem.non_functional_requirements.map((nfr, idx) => (
                      <li key={idx} style={{ marginBottom: '0.4rem' }}>{nfr}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 style={{ fontSize: '0.88rem', color: 'var(--text-pearly)', marginBottom: '0.5rem' }}>
                    Suggested Classes
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {problem.sample_entities.map((ent, idx) => (
                      <span
                        key={idx}
                        style={{
                          fontSize: '0.78rem',
                          background: 'var(--bg-obsidian)',
                          border: '1px solid var(--border-subtle)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-pearly)',
                          fontFamily: 'var(--font-mono)',
                        }}
                      >
                        {ent}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <h4 style={{ fontSize: '0.9rem', color: 'var(--text-pearly)' }}>
                  Scoring Rubric
                </h4>
                <div
                  style={{
                    background: 'var(--bg-obsidian)',
                    padding: '1rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.84rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
                    <span>Class Structure &amp; Methods</span>
                    <strong style={{ color: 'var(--accent-jungle)' }}>40%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
                    <span>Trade-offs &amp; Extensibility</span>
                    <strong style={{ color: 'var(--accent-jungle)' }}>35%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
                    <span>SOLID Principles</span>
                    <strong style={{ color: 'var(--accent-jungle)' }}>15%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Concurrency &amp; Edge Cases</span>
                    <strong style={{ color: 'var(--accent-jungle)' }}>10%</strong>
                  </div>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Code is checked for class relationships, inheritance, and concurrency guards without requiring exact method names.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Workstation (Code, Notes, Diagram) */}
        <div className="studio-panel">
          <div className="panel-header">
            <div className="panel-tabs">
              <button
                className={`panel-tab ${rightTab === 'code' ? 'active' : ''}`}
                onClick={() => setRightTab('code')}
              >
                Python Code
              </button>
              <button
                className={`panel-tab ${rightTab === 'notes' ? 'active' : ''}`}
                onClick={() => setRightTab('notes')}
              >
                Design Notes
              </button>
              <button
                className={`panel-tab ${rightTab === 'diagram' ? 'active' : ''}`}
                onClick={() => setRightTab('diagram')}
              >
                Class Diagram
              </button>
            </div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {rightTab === 'code' ? 'Python 3.13' : rightTab === 'notes' ? 'Markdown' : 'Mermaid'}
            </span>
          </div>

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {rightTab === 'code' && (
              <textarea
                className="code-editor-area"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Write your Python classes and methods here..."
                spellCheck="false"
              />
            )}

            {rightTab === 'notes' && (
              <textarea
                className="notes-editor-area"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Explain your design choices, trade-offs considered, and how you handled concurrency..."
              />
            )}

            {rightTab === 'diagram' && (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <textarea
                  className="code-editor-area"
                  style={{ height: '320px' }}
                  value={diagramDsl}
                  onChange={(e) => setDiagramDsl(e.target.value)}
                  placeholder="Optional: write Mermaid classDiagram syntax..."
                  spellCheck="false"
                />
                <div
                  style={{
                    padding: '1rem',
                    background: 'var(--bg-obsidian)',
                    borderTop: '1px solid var(--border-subtle)',
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                  }}
                >
                  Tip: Diagrams are saved with your submission to document class relationships.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
