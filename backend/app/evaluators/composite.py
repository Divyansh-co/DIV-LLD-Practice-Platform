"""Composite Evaluator orchestrating deterministic and semantic evaluators.

Handles timeouts, async orchestration, weighted scoring, and fault recovery.
"""

import asyncio
import time
from typing import Optional
from app.domain.models import EvaluationResult, Problem, Submission
from app.evaluators.base import Evaluator
from app.evaluators.deterministic import DeterministicEvaluator
from app.evaluators.llm import LLMEvaluator


class CompositeEvaluator(Evaluator):
    """Orchestrates deterministic AST checks and LLM semantic trade-off analysis."""

    def __init__(
        self,
        deterministic_evaluator: Optional[DeterministicEvaluator] = None,
        llm_evaluator: Optional[LLMEvaluator] = None,
        timeout_seconds: float = 25.0,
    ):
        self.deterministic_evaluator = deterministic_evaluator or DeterministicEvaluator()
        self.llm_evaluator = llm_evaluator or LLMEvaluator()
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "CompositeLLDEvaluator"

    async def evaluate(self, submission: Submission, problem: Problem) -> EvaluationResult:
        """Executes full evaluation pipeline with fault-tolerant timeout."""
        start_time = time.perf_counter()

        # Step 1: Deterministic AST checks (fast & objective)
        det_output = await self.deterministic_evaluator.evaluate(submission, problem)
        det_score = det_output.get("score", 0.0)
        checks = det_output.get("checks", [])

        # Step 2: Semantic LLM evaluation with timeout protection
        ai_score = 0.0
        llm_feedback = None
        dimensions = []

        try:
            llm_output = await asyncio.wait_for(
                self.llm_evaluator.evaluate(submission, problem),
                timeout=self.timeout_seconds,
            )
            ai_score = llm_output.get("score", 0.0)
            llm_feedback = llm_output.get("feedback")
            dimensions = llm_output.get("dimensions", [])
        except asyncio.TimeoutError:
            raise RuntimeError(
                f"AI evaluation service timed out after {int(self.timeout_seconds)} seconds. Please retry."
            )
        except Exception as e:
            raise RuntimeError(f"AI evaluation failed: {e}")

        # Step 3: Aggregate scores (Deterministic max 40 + AI rubric max 60 = 100)
        overall_score = round(det_score + ai_score, 1)
        overall_score = max(0.0, min(100.0, overall_score))

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        result = EvaluationResult(
            submission_id=submission.id,
            overall_score=overall_score,
            deterministic_score=det_score,
            ai_score=ai_score,
            checks=checks,
            dimensions=dimensions,
            llm_feedback=llm_feedback,
            execution_time_ms=elapsed_ms,
        )
        result.grade = result.calculate_grade()
        return result

