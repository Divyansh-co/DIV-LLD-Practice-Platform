const API_BASE = '/api/v1';

export async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorDetail = 'API request failed';
    try {
      const err = await res.json();
      errorDetail = err.detail || errorDetail;
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Problems
  getProblems: () => fetchJson('/problems'),
  getProblem: (slug) => fetchJson(`/problems/${slug}`),

  // Attempts & Workstations
  startAttempt: (problemId, userId = '[USER_SENIOR_CANDIDATE]') =>
    fetchJson('/attempts', {
      method: 'POST',
      body: JSON.stringify({ problem_id: problemId, user_id: userId }),
    }),
  getAttempt: (attemptId) => fetchJson(`/attempts/${attemptId}`),
  saveDraft: (attemptId, code, designNotes, diagramDsl) =>
    fetchJson(`/attempts/${attemptId}`, {
      method: 'PUT',
      body: JSON.stringify({
        code,
        design_notes: designNotes,
        diagram_dsl: diagramDsl,
      }),
    }),
  submitAttempt: (attemptId) =>
    fetchJson(`/attempts/${attemptId}/submit`, {
      method: 'POST',
    }),

  // Submissions & Evaluation
  getSubmission: (submissionId) => fetchJson(`/submissions/${submissionId}`),
  retrySubmission: (submissionId) =>
    fetchJson(`/submissions/${submissionId}/retry`, {
      method: 'POST',
    }),

  // Analytics & History
  getProblemHistory: (slug) => fetchJson(`/problems/${slug}/history`),
  getDashboardStats: () => fetchJson('/dashboard/stats'),
};
