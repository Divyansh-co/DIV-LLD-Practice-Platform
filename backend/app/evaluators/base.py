"""Base interface for Low-Level Design evaluators (Strategy Pattern)."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from app.domain.models import Problem, Submission


class Evaluator(ABC):
    """Abstract Strategy interface for evaluating learner submissions."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the evaluator strategy."""
        pass

    @abstractmethod
    async def evaluate(self, submission: Submission, problem: Problem) -> Dict[str, Any]:
        """Execute evaluation logic and return structured result payload.
        
        Args:
            submission: The learner submission containing code, notes, and diagram.
            problem: The problem specification with requirements and rules.
            
        Returns:
            Dict containing scores, checks, and feedback chunks.
        """
        pass
