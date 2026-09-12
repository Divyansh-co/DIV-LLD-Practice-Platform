"""REST API Routes for LLD Practice Platform."""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from app.api.schemas import (
    AttemptResponseSchema,
    ProblemDetailSchema,
    SaveDraftRequest,
    StartAttemptRequest,
    SubmissionResponseSchema,
)
from app.domain.models import SubmissionStatus
from app.repositories.storage import ProblemRepository
from app.services.attempt_service import AttemptService
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/v1")

problem_repo = ProblemRepository()
attempt_service = AttemptService(problem_repo=problem_repo)
evaluation_service = EvaluationService(problem_repo=problem_repo)


@router.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "LLD Practice Platform API"}


@router.get("/problems", response_model=List[ProblemDetailSchema])
def list_problems() -> List[Dict[str, Any]]:
    problems = problem_repo.get_all()
    return [
        {
            "id": p.id,
            "slug": p.slug,
            "title": p.title,
            "difficulty": p.difficulty.value,
            "domain": p.domain,
            "summary": p.summary,
            "functional_requirements": p.functional_requirements,
            "non_functional_requirements": p.non_functional_requirements,
            "constraints": p.constraints,
            "sample_entities": p.sample_entities,
            "starter_code": p.starter_code,
            "default_notes_template": p.default_notes_template,
            "starter_diagram_dsl": p.starter_diagram_dsl,
            "rubric_weights": p.rubric_weights,
        }
        for p in problems
    ]


@router.get("/problems/{problem_id_or_slug}", response_model=ProblemDetailSchema)
def get_problem(problem_id_or_slug: str) -> Dict[str, Any]:
    p = problem_repo.get_by_id(problem_id_or_slug) or problem_repo.get_by_slug(problem_id_or_slug)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return {
        "id": p.id,
        "slug": p.slug,
        "title": p.title,
        "difficulty": p.difficulty.value,
        "domain": p.domain,
        "summary": p.summary,
        "functional_requirements": p.functional_requirements,
        "non_functional_requirements": p.non_functional_requirements,
        "constraints": p.constraints,
        "sample_entities": p.sample_entities,
        "starter_code": p.starter_code,
        "default_notes_template": p.default_notes_template,
        "starter_diagram_dsl": p.starter_diagram_dsl,
        "rubric_weights": p.rubric_weights,
    }


@router.post("/attempts", response_model=AttemptResponseSchema)
def start_attempt(req: StartAttemptRequest) -> Dict[str, Any]:
    try:
        attempt = attempt_service.get_or_create_attempt(req.problem_id, req.user_id)
        return {
            "id": attempt.id,
            "problem_id": attempt.problem_id,
            "user_id": attempt.user_id,
            "code": attempt.code,
            "design_notes": attempt.design_notes,
            "diagram_dsl": attempt.diagram_dsl,
            "status": attempt.status.value,
            "draft_version": attempt.draft_version,
            "created_at": attempt.created_at.isoformat(),
            "updated_at": attempt.updated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/attempts/{attempt_id}", response_model=AttemptResponseSchema)
def get_attempt(attempt_id: str) -> Dict[str, Any]:
    attempt = attempt_service.get_attempt(attempt_id)
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return {
        "id": attempt.id,
        "problem_id": attempt.problem_id,
        "user_id": attempt.user_id,
        "code": attempt.code,
        "design_notes": attempt.design_notes,
        "diagram_dsl": attempt.diagram_dsl,
        "status": attempt.status.value,
        "draft_version": attempt.draft_version,
        "created_at": attempt.created_at.isoformat(),
        "updated_at": attempt.updated_at.isoformat(),
    }


@router.put("/attempts/{attempt_id}", response_model=AttemptResponseSchema)
def save_draft(attempt_id: str, req: SaveDraftRequest) -> Dict[str, Any]:
    try:
        attempt = attempt_service.save_draft(attempt_id, req.code, req.design_notes, req.diagram_dsl)
        return {
            "id": attempt.id,
            "problem_id": attempt.problem_id,
            "user_id": attempt.user_id,
            "code": attempt.code,
            "design_notes": attempt.design_notes,
            "diagram_dsl": attempt.diagram_dsl,
            "status": attempt.status.value,
            "draft_version": attempt.draft_version,
            "created_at": attempt.created_at.isoformat(),
            "updated_at": attempt.updated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


from fastapi import APIRouter, BackgroundTasks, HTTPException, status


@router.post("/attempts/{attempt_id}/submit", response_model=SubmissionResponseSchema)
def submit_attempt(attempt_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    try:
        sub = evaluation_service.create_submission(attempt_id)
        if sub.status in (SubmissionStatus.SUBMITTED, SubmissionStatus.PENDING):
            background_tasks.add_task(evaluation_service.process_submission, sub.id)
        return {
            "id": sub.id,
            "attempt_id": sub.attempt_id,
            "problem_id": sub.problem_id,
            "user_id": sub.user_id,
            "submitted_code": sub.submitted_code,
            "submitted_notes": sub.submitted_notes,
            "submitted_diagram_dsl": sub.submitted_diagram_dsl,
            "status": sub.status.value,
            "retry_count": sub.retry_count,
            "error_message": sub.error_message,
            "created_at": sub.created_at.isoformat(),
            "updated_at": sub.updated_at.isoformat(),
            "evaluation": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/submissions/{submission_id}", response_model=SubmissionResponseSchema)
def get_submission(submission_id: str) -> Dict[str, Any]:
    detail = evaluation_service.get_submission_detail(submission_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    sub = detail["submission"]
    ev = detail["evaluation"]

    ev_data = None
    if ev:
        dims_data = [
            {
                "criterion": d.criterion,
                "score": d.score,
                "max_score": d.max_score,
                "evidence": d.evidence,
                "concern": d.concern,
                "suggestion": d.suggestion,
                "confidence": d.confidence,
            }
            for d in ev.dimensions
        ]

        ev_data = {
            "id": ev.id,
            "submission_id": ev.submission_id,
            "overall_score": ev.overall_score,
            "deterministic_score": ev.deterministic_score,
            "ai_score": ev.ai_score,
            "grade": ev.grade,
            "checks": [
                {
                    "rule_id": c.rule_id,
                    "rule_name": c.rule_name,
                    "category": c.category.value,
                    "passed": c.passed,
                    "score": c.score,
                    "max_score": c.max_score,
                    "severity": c.severity.value,
                    "message": c.message,
                    "suggestion": c.suggestion,
                    "code_reference": c.code_reference,
                }
                for c in ev.checks
            ],
            "dimensions": dims_data,
            "llm_feedback": {
                "summary": ev.llm_feedback.summary,
                "dimensions": dims_data,
                "trade_off_analysis": ev.llm_feedback.trade_off_analysis,
                "extensibility_critique": ev.llm_feedback.extensibility_critique,
                "edge_cases_analysis": ev.llm_feedback.edge_cases_analysis,
                "alternative_approaches": ev.llm_feedback.alternative_approaches,
                "suggested_refactor_diff": ev.llm_feedback.suggested_refactor_diff,
            } if ev.llm_feedback else None,
            "execution_time_ms": ev.execution_time_ms,
            "created_at": ev.created_at.isoformat(),
        }


    return {
        "id": sub.id,
        "attempt_id": sub.attempt_id,
        "problem_id": sub.problem_id,
        "user_id": sub.user_id,
        "submitted_code": sub.submitted_code,
        "submitted_notes": sub.submitted_notes,
        "submitted_diagram_dsl": sub.submitted_diagram_dsl,
        "status": sub.status.value,
        "retry_count": sub.retry_count,
        "error_message": sub.error_message,
        "created_at": sub.created_at.isoformat(),
        "updated_at": sub.updated_at.isoformat(),
        "evaluation": ev_data,
    }


@router.post("/submissions/{submission_id}/retry", response_model=SubmissionResponseSchema)
def retry_submission(submission_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    try:
        sub = evaluation_service.prepare_submission_retry(submission_id)
        background_tasks.add_task(evaluation_service.process_submission, sub.id)
        return {
            "id": sub.id,
            "attempt_id": sub.attempt_id,
            "problem_id": sub.problem_id,
            "user_id": sub.user_id,
            "submitted_code": sub.submitted_code,
            "submitted_notes": sub.submitted_notes,
            "submitted_diagram_dsl": sub.submitted_diagram_dsl,
            "status": sub.status.value,
            "retry_count": sub.retry_count,
            "error_message": sub.error_message,
            "created_at": sub.created_at.isoformat(),
            "updated_at": sub.updated_at.isoformat(),
            "evaluation": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



@router.get("/problems/{problem_id_or_slug}/history")
def get_history(problem_id_or_slug: str) -> List[Dict[str, Any]]:
    return evaluation_service.get_problem_history(problem_id_or_slug)


@router.get("/dashboard/stats")
def get_stats() -> Dict[str, Any]:
    return evaluation_service.get_dashboard_stats()
