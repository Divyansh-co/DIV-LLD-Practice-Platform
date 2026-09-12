"""Tests for submission lifecycle, async processing, idempotency, and retries."""

import asyncio
import pytest
from app.data.seed_problems import PARKING_LOT
from app.domain.models import SubmissionStatus
from app.services.attempt_service import AttemptService
from app.services.evaluation_service import EvaluationService


@pytest.mark.asyncio
async def test_full_submission_and_evaluation_flow():
    attempt_svc = AttemptService()
    eval_svc = EvaluationService()

    # 1. Start attempt
    attempt = attempt_svc.get_or_create_attempt(PARKING_LOT.id)
    assert attempt.status.value == "IN_PROGRESS"

    # 2. Update draft
    attempt_svc.save_draft(
        attempt.id,
        code=PARKING_LOT.starter_code,
        notes="Applied Strategy Pattern for fees and mutex locking for thread-safety.",
        diagram_dsl=PARKING_LOT.starter_diagram_dsl,
    )

    # 3. Submit
    submission = await eval_svc.submit_attempt(attempt.id)
    assert submission.status in (SubmissionStatus.SUBMITTED, SubmissionStatus.EVALUATING)

    # 4. Wait for background task to complete processing
    await asyncio.sleep(0.8)

    # 5. Verify completion
    detail = eval_svc.get_submission_detail(submission.id)
    assert detail is not None
    completed_sub = detail["submission"]
    evaluation = detail["evaluation"]

    assert completed_sub.status == SubmissionStatus.COMPLETED
    assert evaluation is not None
    assert evaluation.overall_score >= 70.0
    assert len(evaluation.checks) > 0

    # Verify the 8 structured rubric dimensions
    assert len(evaluation.dimensions) == 8
    criteria_names = [d.criterion for d in evaluation.dimensions]
    assert "Requirement Understanding" in criteria_names
    assert "Class Responsibilities" in criteria_names
    assert "Coupling & Cohesion" in criteria_names
    assert "Encapsulation & Interfaces" in criteria_names
    assert "Appropriate Use of Abstraction & Patterns" in criteria_names
    assert "Extensibility When Requirements Change" in criteria_names
    assert "Edge Cases & Testability" in criteria_names
    assert "Quality of Explanation" in criteria_names

    # Check structure of each dimension
    dim = evaluation.dimensions[0]
    assert dim.score > 0
    assert len(dim.evidence) > 0
    assert len(dim.suggestion) > 0
    assert 0.0 <= dim.confidence <= 1.0


@pytest.mark.asyncio
async def test_idempotency_duplicate_submission_guard():
    attempt_svc = AttemptService()
    eval_svc = EvaluationService()

    attempt = attempt_svc.get_or_create_attempt(PARKING_LOT.id)
    attempt_svc.save_draft(
        attempt.id,
        code="class Vehicle: pass",
        notes="Simple test draft",
        diagram_dsl="",
    )

    # First submission
    sub1 = eval_svc.create_submission(attempt.id)
    assert sub1.status == SubmissionStatus.SUBMITTED

    # Process first submission to completion
    await eval_svc.process_submission(sub1.id)
    sub1_done = eval_svc.submission_repo.get_by_id(sub1.id)
    assert sub1_done.status == SubmissionStatus.COMPLETED

    # Second submission with identical content: should return existing submission idempotently
    sub2 = eval_svc.create_submission(attempt.id)
    assert sub2.id == sub1.id
    assert sub2.status == SubmissionStatus.COMPLETED



@pytest.mark.asyncio
async def test_submission_retry_flow():
    eval_svc = EvaluationService()

    sub = eval_svc.create_submission(
        AttemptService().get_or_create_attempt(PARKING_LOT.id).id
    )

    # Force failure state to test retry policy
    sub.start_evaluating()
    sub.fail_evaluation("Simulated network timeout")
    eval_svc.submission_repo.save(sub)

    # Retry
    retried_sub = await eval_svc.retry_submission(sub.id)
    assert retried_sub.status == SubmissionStatus.SUBMITTED
    assert retried_sub.retry_count == 1

    # Wait for re-evaluation
    await asyncio.sleep(0.8)
    final_sub = eval_svc.submission_repo.get_by_id(sub.id)
    assert final_sub.status == SubmissionStatus.COMPLETED


@pytest.mark.asyncio
async def test_problem_history_tracking():
    attempt_svc = AttemptService()
    eval_svc = EvaluationService()

    attempt = attempt_svc.get_or_create_attempt(PARKING_LOT.id)
    sub1 = await eval_svc.submit_attempt(attempt.id)
    await asyncio.sleep(0.8)

    history = eval_svc.get_problem_history(PARKING_LOT.id)
    assert len(history) >= 1
    assert history[0]["submission_id"] == sub1.id
    assert history[0]["score"] is not None


def test_dashboard_stats():
    eval_svc = EvaluationService()
    stats = eval_svc.get_dashboard_stats()

    assert "candidate_profile" in stats
    assert "metrics" in stats
    assert "skill_radar" in stats
    assert stats["candidate_profile"]["name"] == "[USER_SENIOR_CANDIDATE]"
