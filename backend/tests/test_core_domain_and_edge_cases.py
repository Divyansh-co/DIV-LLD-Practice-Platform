"""Tests for Priority 5: Core Domain Behavior, State Machine, and Edge Cases.

Covers:
1. Core domain behavior (ParkingSpot vehicle fitting/rejection, PricingStrategy variations)
2. State machine transitions (PENDING -> EVALUATING -> COMPLETED / FAILED)
3. Edge cases (Idempotent duplicate handling, malformed code, failed checks returning usable results)
"""

from abc import ABC, abstractmethod
from enum import Enum
import pytest

from app.data.seed_problems import PARKING_LOT
from app.domain.models import (
    Attempt,
    CheckSeverity,
    EvaluationResult,
    Problem,
    Submission,
    SubmissionStatus,
)
from app.evaluators.composite import CompositeEvaluator
from app.evaluators.deterministic import DeterministicEvaluator
from app.evaluators.llm import LLMEvaluator
from app.services.attempt_service import AttemptService
from app.services.evaluation_service import EvaluationService


# =====================================================================
# 1. Core Domain Behavior Tests
# =====================================================================

class VehicleType(Enum):
    MOTORCYCLE = 1
    CAR = 2
    TRUCK = 3


class SpotType(Enum):
    MOTORCYCLE = 1
    COMPACT = 2
    LARGE = 3


class Vehicle(ABC):
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type


class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.MOTORCYCLE)


class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)


class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)


class ParkingSpot:
    """Core domain model representing an individual slot with vehicle fitting logic."""

    def __init__(self, spot_id: str, spot_type: SpotType):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.assigned_vehicle = None

    @property
    def is_available(self) -> bool:
        return self.assigned_vehicle is None

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        if not self.is_available:
            return False
        if self.spot_type == SpotType.LARGE:
            return True
        if self.spot_type == SpotType.COMPACT:
            return vehicle.vehicle_type in (VehicleType.MOTORCYCLE, VehicleType.CAR)
        if self.spot_type == SpotType.MOTORCYCLE:
            return vehicle.vehicle_type == VehicleType.MOTORCYCLE
        return False

    def assign_vehicle(self, vehicle: Vehicle) -> bool:
        if not self.can_fit_vehicle(vehicle):
            return False
        self.assigned_vehicle = vehicle
        return True

    def vacate(self) -> None:
        self.assigned_vehicle = None


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, duration_hours: float, vehicle_type: VehicleType) -> float:
        pass


class HourlyPricingStrategy(PricingStrategy):
    def calculate_fee(self, duration_hours: float, vehicle_type: VehicleType) -> float:
        rates = {VehicleType.MOTORCYCLE: 10.0, VehicleType.CAR: 20.0, VehicleType.TRUCK: 40.0}
        return duration_hours * rates[vehicle_type]


class FlatRatePricingStrategy(PricingStrategy):
    def __init__(self, flat_fee: float = 15.0):
        self.flat_fee = flat_fee

    def calculate_fee(self, duration_hours: float, vehicle_type: VehicleType) -> float:
        multiplier = 1.0 if vehicle_type != VehicleType.TRUCK else 2.0
        return self.flat_fee * multiplier


def test_parking_spot_fits_and_rejects_vehicles_correctly():
    moto_spot = ParkingSpot("S-1", SpotType.MOTORCYCLE)
    compact_spot = ParkingSpot("S-2", SpotType.COMPACT)
    large_spot = ParkingSpot("S-3", SpotType.LARGE)

    bike = Motorcycle("M-101")
    car = Car("C-202")
    truck = Truck("T-303")

    # Motorcycle spot accepts only motorcycle
    assert moto_spot.can_fit_vehicle(bike) is True
    assert moto_spot.can_fit_vehicle(car) is False
    assert moto_spot.can_fit_vehicle(truck) is False

    # Compact spot accepts motorcycle and car, rejects truck
    assert compact_spot.can_fit_vehicle(bike) is True
    assert compact_spot.can_fit_vehicle(car) is True
    assert compact_spot.can_fit_vehicle(truck) is False

    # Large spot accepts all vehicles
    assert large_spot.can_fit_vehicle(bike) is True
    assert large_spot.can_fit_vehicle(car) is True
    assert large_spot.can_fit_vehicle(truck) is True

    # Cannot double-occupy an already assigned spot
    assert compact_spot.assign_vehicle(car) is True
    assert compact_spot.is_available is False
    assert compact_spot.can_fit_vehicle(bike) is False  # Occupied, so cannot fit another
    assert compact_spot.assign_vehicle(bike) is False

    # Vacating frees the spot
    compact_spot.vacate()
    assert compact_spot.is_available is True
    assert compact_spot.can_fit_vehicle(bike) is True


def test_pricing_strategy_calculations_across_types():
    hourly = HourlyPricingStrategy()
    flat = FlatRatePricingStrategy(flat_fee=25.0)

    # Hourly pricing rates
    assert hourly.calculate_fee(2.0, VehicleType.MOTORCYCLE) == 20.0
    assert hourly.calculate_fee(3.0, VehicleType.CAR) == 60.0
    assert hourly.calculate_fee(1.5, VehicleType.TRUCK) == 60.0

    # Flat pricing rates
    assert flat.calculate_fee(0.5, VehicleType.MOTORCYCLE) == 25.0
    assert flat.calculate_fee(10.0, VehicleType.CAR) == 25.0
    assert flat.calculate_fee(1.0, VehicleType.TRUCK) == 50.0  # Truck 2x multiplier


# =====================================================================
# 2. Submission State Machine Tests
# =====================================================================

def test_submission_state_machine_orderly_transitions():
    sub = Submission(attempt_id="att_test", problem_id="prob_test")
    sub.status = SubmissionStatus.PENDING

    # PENDING -> EVALUATING
    sub.start_evaluating()
    assert sub.status == SubmissionStatus.EVALUATING
    assert sub.error_message is None

    # EVALUATING -> COMPLETED
    result = EvaluationResult(submission_id=sub.id, overall_score=85.0)
    sub.complete_evaluation(result)
    assert sub.status == SubmissionStatus.COMPLETED
    assert sub.evaluation is not None
    assert sub.evaluation.overall_score == 85.0

    # Illegal transition: cannot evaluate once COMPLETED
    with pytest.raises(ValueError):
        sub.start_evaluating()


def test_submission_failed_state_records_error_plainly():
    sub = Submission(attempt_id="att_test", problem_id="prob_test")
    sub.start_evaluating()

    error_text = "AI evaluation service timed out after 25 seconds."
    sub.fail_evaluation(error_text)

    # Must land explicitly in FAILED status with error message recorded
    assert sub.status == SubmissionStatus.FAILED
    assert sub.error_message == error_text
    assert sub.evaluation is None


# =====================================================================
# 3. Explicit Edge Cases
# =====================================================================

@pytest.mark.asyncio
async def test_duplicate_submission_not_double_processed():
    """Submitting identical content returns the existing submission without creating duplicates."""
    eval_svc = EvaluationService(
        composite_evaluator=CompositeEvaluator(llm_evaluator=LLMEvaluator(allow_fallback=True))
    )
    attempt_svc = AttemptService()
    attempt = attempt_svc.get_or_create_attempt(PARKING_LOT.id)

    attempt_svc.save_draft(
        attempt.id,
        code="class Vehicle: pass\nclass Spot: pass",
        notes="Testing duplicate guard",
        diagram_dsl="",
    )

    # First submission
    sub1 = eval_svc.create_submission(attempt.id)
    await eval_svc.process_submission(sub1.id)

    sub1_completed = eval_svc.submission_repo.get_by_id(sub1.id)
    assert sub1_completed.status == SubmissionStatus.COMPLETED

    # Second submission with exact same code and notes
    sub2 = eval_svc.create_submission(attempt.id)

    # Must return identical submission record, not a new row
    assert sub2.id == sub1.id
    assert sub2.content_hash == sub1.content_hash
    assert sub2.status == SubmissionStatus.COMPLETED


@pytest.mark.asyncio
async def test_empty_and_malformed_submission_handled_gracefully():
    """Empty or unparseable code returns a clean check failure, not an unhandled crash."""
    evaluator = DeterministicEvaluator()

    # Empty code
    empty_sub = Submission(submitted_code="   \n\t  ")
    empty_res = await evaluator.evaluate(empty_sub, PARKING_LOT)
    assert empty_res["score"] == 0.0
    assert len(empty_res["checks"]) == 1
    assert empty_res["checks"][0].rule_id == "EMPTY_SUBMISSION"
    assert not empty_res["checks"][0].passed
    assert empty_res["checks"][0].severity == CheckSeverity.CRITICAL

    # Syntax error code
    malformed_sub = Submission(submitted_code="class IncompleteClass:\n    def broken(: pass")
    malformed_res = await evaluator.evaluate(malformed_sub, PARKING_LOT)
    assert len(malformed_res["checks"]) == 1
    assert malformed_res["checks"][0].rule_id == "SYNTAX_ERROR"
    assert not malformed_res["checks"][0].passed
    assert "Syntax error" in malformed_res["checks"][0].message


@pytest.mark.asyncio
async def test_submission_failing_structural_checks_returns_usable_result():
    """Code that fails all structural checks still generates a complete, usable EvaluationResult."""
    # Code compiles cleanly, but misses all parking lot requirements
    failing_code = "x = 42\nname = 'just a variable'"
    sub = Submission(
        problem_id=PARKING_LOT.id,
        submitted_code=failing_code,
        submitted_notes="Did not implement any classes.",
    )

    composite = CompositeEvaluator(
        llm_evaluator=LLMEvaluator(allow_fallback=True)
    )
    result = await composite.evaluate(sub, PARKING_LOT)

    # Result should be well-formed, not None or broken
    assert isinstance(result, EvaluationResult)
    assert result.deterministic_score <= 10.0  # Only god class anti-pattern passes
    assert result.overall_score >= 0.0
    assert result.calculate_grade() in ("Needs Rework", "Grade C")
    assert len(result.checks) > 0
    assert any(not c.passed for c in result.checks)
    assert len(result.dimensions) == 8

    # Ensure all failed checks have helpful suggestions rather than empty strings
    failed_checks = [c for c in result.checks if not c.passed]
    assert len(failed_checks) > 0
    for fc in failed_checks:
        assert len(fc.suggestion) > 0
        assert len(fc.message) > 0
