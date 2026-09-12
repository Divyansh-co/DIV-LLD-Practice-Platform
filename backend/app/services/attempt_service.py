"""Attempt management service for saving drafts and managing learner sessions."""

from typing import List, Optional
from app.domain.models import Attempt, AttemptStatus, Problem
from app.repositories.storage import AttemptRepository, ProblemRepository


class AttemptService:
    def __init__(
        self,
        attempt_repo: Optional[AttemptRepository] = None,
        problem_repo: Optional[ProblemRepository] = None,
    ):
        self.attempt_repo = attempt_repo or AttemptRepository()
        self.problem_repo = problem_repo or ProblemRepository()

    def get_or_create_attempt(self, problem_id: str, user_id: str = "[USER_SENIOR_CANDIDATE]") -> Attempt:
        """Resumes active attempt or creates a new one seeded with starter template."""
        existing = self.attempt_repo.get_latest_by_problem_and_user(problem_id, user_id)
        if existing and existing.status == AttemptStatus.IN_PROGRESS:
            return existing

        problem = self.problem_repo.get_by_id(problem_id)
        if not problem:
            problem = self.problem_repo.get_by_slug(problem_id)
        if not problem:
            raise ValueError(f"Problem {problem_id} not found")

        new_attempt = Attempt(
            problem_id=problem.id,
            user_id=user_id,
            code=problem.starter_code,
            design_notes=problem.default_notes_template,
            diagram_dsl=problem.starter_diagram_dsl,
            status=AttemptStatus.IN_PROGRESS,
        )
        return self.attempt_repo.save(new_attempt)

    def save_draft(
        self,
        attempt_id: str,
        code: str,
        notes: str,
        diagram_dsl: str,
    ) -> Attempt:
        """Persists auto-saved draft state."""
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise ValueError(f"Attempt {attempt_id} not found")

        attempt.update_draft(code, notes, diagram_dsl)
        return self.attempt_repo.save(attempt)

    def get_attempt(self, attempt_id: str) -> Optional[Attempt]:
        return self.attempt_repo.get_by_id(attempt_id)

    def list_all_attempts(self, user_id: Optional[str] = None) -> List[Attempt]:
        return self.attempt_repo.list_all(user_id)
