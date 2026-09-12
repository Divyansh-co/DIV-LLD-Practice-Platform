import React, { useState, useEffect } from 'react';
import CanvasBackground from './components/CanvasBackground';
import Navbar from './components/Navbar';
import Watermark from './components/Watermark';
import DashboardView from './views/DashboardView';
import PracticeView from './views/PracticeView';
import EvaluationView from './views/EvaluationView';
import HistoryView from './views/HistoryView';
import { api } from './services/api';

export default function App() {
  const [view, setView] = useState('dashboard'); // 'dashboard' | 'practice' | 'evaluation' | 'history'
  const [problems, setProblems] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeProblem, setActiveProblem] = useState(null);
  const [activeSubmissionId, setActiveSubmissionId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshData = async () => {
    try {
      const [problemsData, statsData] = await Promise.all([
        api.getProblems(),
        api.getDashboardStats(),
      ]);
      setProblems(problemsData);
      setStats(statsData);
      if (problemsData.length > 0 && !activeProblem) {
        setActiveProblem(problemsData[0]);
      }
    } catch (err) {
      console.error('Failed to fetch initial data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const handleSelectProblem = (problem) => {
    setActiveProblem(problem);
    setView('practice');
  };

  const handleSubmitSuccess = (submissionId) => {
    setActiveSubmissionId(submissionId);
    setView('evaluation');
    refreshData();
  };

  const handleViewSubmission = (submissionId) => {
    setActiveSubmissionId(submissionId);
    setView('evaluation');
  };

  const handleIterate = () => {
    setView('practice');
  };

  const handleViewHistory = () => {
    setView('history');
  };

  return (
    <div className="app-container">
      {/* 60fps Interactive Cursor Canvas Background */}
      <CanvasBackground />

      {/* Global Navbar */}
      <Navbar
        currentView={view}
        setView={setView}
        activeProblem={activeProblem}
      />

      {/* Main Content Area */}
      <main className="content-wrapper">
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
            Loading LLD Studio...
          </div>
        ) : (
          <>
            {view === 'dashboard' && (
              <DashboardView
                problems={problems}
                stats={stats}
                onSelectProblem={handleSelectProblem}
                onViewSubmission={handleViewSubmission}
                setView={setView}
              />
            )}

            {view === 'practice' && activeProblem && (
              <PracticeView
                problem={activeProblem}
                onBack={() => setView('dashboard')}
                onSubmitSuccess={handleSubmitSuccess}
              />
            )}

            {view === 'evaluation' && activeSubmissionId && (
              <EvaluationView
                submissionId={activeSubmissionId}
                onIterate={handleIterate}
                onViewHistory={handleViewHistory}
                onBackToDashboard={() => setView('dashboard')}
              />
            )}

            {view === 'history' && (
              <HistoryView
                problems={problems}
                activeProblem={activeProblem}
                onSelectSubmission={handleViewSubmission}
                onStartNewAttempt={handleSelectProblem}
              />
            )}
          </>
        )}
      </main>

      {/* Persistent Author Watermark */}
      <Watermark />
    </div>
  );
}
