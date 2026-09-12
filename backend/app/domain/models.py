"""Core Domain Models for the Low-Level Design (LLD) Platform.

Responsibilities:
- Problem: Encapsulates requirements, constraints, sample entities, and rubric criteria.
- Attempt: Owns learner interactive draft state (code + rationale).
- Submission: Immutable snapshot with explicit state machine (SUBMITTED -> EVALUATING -> COMPLETED / FAILED).
- RubricDimensionResult: Structured evaluation shape (criterion -> score -> evidence -> concern -> suggestion -> confidence).
- EvaluationResult: Aggregated result separating deterministic AST checks from structured AI rubric dimensions.
- Evaluator: Strategy interface separating deterministic rule checks from AI semantic reasoning.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Any, Dict, List, Optional
import uuid


class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class AttemptStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    ABANDONED = "ABANDONED"


class SubmissionStatus(str, Enum):
    PENDING = "PENDING"          # Queued before evaluation begins
    SUBMITTED = "SUBMITTED"      # Persisted before evaluation begins
    EVALUATING = "EVALUATING"    # Actively processed by evaluator
    COMPLETED = "COMPLETED"      # Evaluation finished successfully
    FAILED = "FAILED"            # Evaluation failed with recoverable error


class CheckCategory(str, Enum):
    STRUCTURAL = "STRUCTURAL"
    SOLID = "SOLID"
    PATTERNS = "PATTERNS"
    CONCURRENCY = "CONCURRENCY"
    CONTRACT = "CONTRACT"


class CheckSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class CheckResult:
    """Individual deterministic AST check result."""
    rule_id: str
    rule_name: str
    category: CheckCategory
    passed: bool
    score: float
    max_score: float
    severity: CheckSeverity
    message: str
    suggestion: str
    code_reference: Optional[str] = None


@dataclass
class RubricDimensionResult:
    """Structured output shape for each rubric dimension.
    
    criterion -> score -> evidence -> concern -> suggestion -> confidence
    """
    criterion: str
    score: float
    max_score: float
    evidence: str
    concern: str
    suggestion: str
    confidence: float  # 0.0 to 1.0


@dataclass
class LLMFeedbackReport:
    """Rich architectural critique and structured rubric dimensions."""
    summary: str
    dimensions: List[RubricDimensionResult]
    trade_off_analysis: str
    extensibility_critique: str
    edge_cases_analysis: str
    alternative_approaches: List[str]
    suggested_refactor_diff: str


@dataclass
class EvaluationResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    submission_id: str = ""
    overall_score: float = 0.0
    deterministic_score: float = 0.0
    ai_score: float = 0.0
    grade: str = "PENDING"
    checks: List[CheckResult] = field(default_factory=list)
    dimensions: List[RubricDimensionResult] = field(default_factory=list)
    llm_feedback: Optional[LLMFeedbackReport] = None
    execution_time_ms: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def llm_score(self) -> float:
        return self.ai_score

    def calculate_grade(self) -> str:

        if self.overall_score >= 90:
            return "Grade S"
        elif self.overall_score >= 80:
            return "Grade A"
        elif self.overall_score >= 65:
            return "Grade B"
        elif self.overall_score >= 50:
            return "Grade C"
        return "Needs Rework"


@dataclass
class Problem:
    id: str
    slug: str
    title: str
    difficulty: Difficulty
    domain: str
    summary: str
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    constraints: List[str]
    sample_entities: List[str]
    starter_code: str
    default_notes_template: str
    starter_diagram_dsl: str
    rubric_weights: Dict[str, float] = field(default_factory=lambda: {
        "deterministic": 0.40,
        "ai_rubric": 0.60,
    })


@dataclass
class Attempt:
    """Represents a learner's draft workspace session.
    
    Responsibility: Owns active editable state (code + design notes + diagram DSL)
    and draft versioning. Persisted as the learner works.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_id: str = ""
    user_id: str = "user_senior_candidate"
    code: str = ""
    design_notes: str = ""
    diagram_dsl: str = ""
    status: AttemptStatus = AttemptStatus.IN_PROGRESS
    draft_version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_draft(self, code: str, notes: str, diagram_dsl: str) -> None:
        self.code = code
        self.design_notes = notes
        self.diagram_dsl = diagram_dsl
        self.draft_version += 1
        self.updated_at = datetime.now(timezone.utc)

    def mark_submitted(self) -> None:
        self.status = AttemptStatus.SUBMITTED
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Submission:
    """Represents an immutable snapshot submitted for evaluation.
    
    State Machine:
    SUBMITTED -> EVALUATING -> COMPLETED / FAILED
    
    Guarantees:
    - Persisted BEFORE evaluation starts (so nothing is lost if evaluator crashes)
    - Idempotency guard via content_hash preventing duplicate processing
    - Explicit retry policy with retry_count increment
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempt_id: str = ""
    problem_id: str = ""
    user_id: str = "user_senior_candidate"
    submitted_code: str = ""
    submitted_notes: str = ""
    submitted_diagram_dsl: str = ""
    status: SubmissionStatus = SubmissionStatus.SUBMITTED
    retry_count: int = 0
    error_message: Optional[str] = None
    content_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluation: Optional[EvaluationResult] = None

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self.compute_hash()

    def compute_hash(self) -> str:
        payload = f"{self.problem_id}:{self.submitted_code}:{self.submitted_notes}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def start_evaluating(self) -> None:
        """Transitions PENDING, SUBMITTED or FAILED to EVALUATING."""
        if self.status not in (SubmissionStatus.PENDING, SubmissionStatus.SUBMITTED, SubmissionStatus.FAILED):
            raise ValueError(f"Cannot evaluate submission in status {self.status}")
        self.status = SubmissionStatus.EVALUATING
        self.error_message = None
        self.updated_at = datetime.now(timezone.utc)

    def complete_evaluation(self, result: EvaluationResult) -> None:
        """Transitions EVALUATING to COMPLETED."""
        if self.status != SubmissionStatus.EVALUATING:
            raise ValueError(f"Cannot complete submission from status {self.status}")
        self.status = SubmissionStatus.COMPLETED
        self.evaluation = result
        self.updated_at = datetime.now(timezone.utc)

    def fail_evaluation(self, error: str) -> None:
        """Transitions EVALUATING to FAILED."""
        self.status = SubmissionStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.now(timezone.utc)

    def prepare_retry(self) -> None:
        """Idempotent retry preparation: resets status to PENDING / SUBMITTED."""
        if self.status not in (SubmissionStatus.FAILED, SubmissionStatus.SUBMITTED, SubmissionStatus.PENDING):
            raise ValueError(f"Only failed or submitted submissions can be retried, current: {self.status}")
        self.status = SubmissionStatus.SUBMITTED
        self.retry_count += 1
        self.error_message = None
        self.updated_at = datetime.now(timezone.utc)
