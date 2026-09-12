"""Unit tests for domain models, idempotency hashes, and state transitions."""

import pytest
from app.domain.models import (
    Attempt,
    AttemptStatus,
    EvaluationResult,
    RubricDimensionResult,
    Submission,
    SubmissionStatus,
)


def test_attempt_draft_lifecycle():
    attempt = Attempt(problem_id="prob_parking_lot", user_id="user_123")
    assert attempt.status == AttemptStatus.IN_PROGRESS
    assert attempt.draft_version == 1

    attempt.update_draft("class Car: pass", "# notes", "classDiagram")
    assert attempt.draft_version == 2
    assert "Car" in attempt.code

    attempt.mark_submitted()
    assert attempt.status == AttemptStatus.SUBMITTED


def test_submission_state_machine_happy_path():
    sub = Submission(attempt_id="att_1", problem_id="prob_1")
    assert sub.status == SubmissionStatus.SUBMITTED
    assert len(sub.content_hash) == 64  # SHA256 hex string

    sub.start_evaluating()
    assert sub.status == SubmissionStatus.EVALUATING

    result = EvaluationResult(submission_id=sub.id, overall_score=88.5)
    sub.complete_evaluation(result)
    assert sub.status == SubmissionStatus.COMPLETED
    assert sub.evaluation.overall_score == 88.5


def test_submission_state_machine_failure_and_retry():
    sub = Submission(attempt_id="att_1", problem_id="prob_1")
    sub.start_evaluating()
    sub.fail_evaluation("LLM rate limit exceeded")

    assert sub.status == SubmissionStatus.FAILED
    assert sub.error_message == "LLM rate limit exceeded"
    assert sub.retry_count == 0

    sub.prepare_retry()
    assert sub.status == SubmissionStatus.SUBMITTED
    assert sub.retry_count == 1
    assert sub.error_message is None


def test_invalid_submission_state_transitions():
    sub = Submission(attempt_id="att_1", problem_id="prob_1")
    sub.start_evaluating()
    result = EvaluationResult(submission_id=sub.id, overall_score=90.0)
    sub.complete_evaluation(result)

    with pytest.raises(ValueError, match="Cannot evaluate submission in status"):
        sub.start_evaluating()

    with pytest.raises(ValueError, match="Only failed or submitted"):
        sub.prepare_retry()


def test_rubric_dimension_shape():
    dim = RubricDimensionResult(
        criterion="Class Responsibilities",
        score=7.0,
        max_score=7.5,
        evidence="ParkingSpot manages spot state cleanly.",
        concern="ParkingLot manages collection directly.",
        suggestion="Introduce ParkingFloor.",
        confidence=0.92,
    )
    assert dim.criterion == "Class Responsibilities"
    assert dim.score == 7.0
    assert dim.confidence == 0.92


def test_evaluation_grade_calculation():
    e_s = EvaluationResult(overall_score=95.0)
    assert "S" in e_s.calculate_grade()

    e_a = EvaluationResult(overall_score=82.0)
    assert "A" in e_a.calculate_grade()

    e_b = EvaluationResult(overall_score=68.0)
    assert "B" in e_b.calculate_grade()

    e_c = EvaluationResult(overall_score=52.0)
    assert "C" in e_c.calculate_grade()

    e_f = EvaluationResult(overall_score=35.0)
    assert "Needs Rework" in e_f.calculate_grade()
