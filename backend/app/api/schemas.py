"""Pydantic schemas for API request and response serialization."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StartAttemptRequest(BaseModel):
    problem_id: str
    user_id: str = "user_senior_candidate"


class SaveDraftRequest(BaseModel):
    code: str
    design_notes: str = ""
    diagram_dsl: str = ""


class SubmitAttemptRequest(BaseModel):
    pass


class CheckResultSchema(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    passed: bool
    score: float
    max_score: float
    severity: str
    message: str
    suggestion: str
    code_reference: Optional[str] = None


class RubricDimensionSchema(BaseModel):
    criterion: str
    score: float
    max_score: float
    evidence: str
    concern: str
    suggestion: str
    confidence: float


class LLMFeedbackSchema(BaseModel):
    summary: str
    dimensions: List[RubricDimensionSchema] = []
    trade_off_analysis: str
    extensibility_critique: str
    edge_cases_analysis: str
    alternative_approaches: List[str]
    suggested_refactor_diff: str


class EvaluationResultSchema(BaseModel):
    id: str
    submission_id: str
    overall_score: float
    deterministic_score: float
    ai_score: float
    grade: str
    checks: List[CheckResultSchema]
    dimensions: List[RubricDimensionSchema] = []
    llm_feedback: Optional[LLMFeedbackSchema] = None
    execution_time_ms: int
    created_at: str



class SubmissionResponseSchema(BaseModel):
    id: str
    attempt_id: str
    problem_id: str
    user_id: str
    submitted_code: str
    submitted_notes: str
    submitted_diagram_dsl: str
    status: str
    retry_count: int
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    evaluation: Optional[EvaluationResultSchema] = None


class AttemptResponseSchema(BaseModel):
    id: str
    problem_id: str
    user_id: str
    code: str
    design_notes: str
    diagram_dsl: str
    status: str
    draft_version: int
    created_at: str
    updated_at: str


class ProblemDetailSchema(BaseModel):
    id: str
    slug: str
    title: str
    difficulty: str
    domain: str
    summary: str
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    constraints: List[str]
    sample_entities: List[str]
    starter_code: str
    default_notes_template: str
    starter_diagram_dsl: str
    rubric_weights: Dict[str, float]
