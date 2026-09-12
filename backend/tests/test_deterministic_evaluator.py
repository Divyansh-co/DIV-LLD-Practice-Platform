"""Tests for Deterministic AST Evaluator and Rule Engine."""

import pytest
from app.data.seed_problems import ELEVATOR_SYSTEM, PARKING_LOT, VENDING_MACHINE
from app.domain.models import Submission
from app.evaluators.deterministic import DeterministicEvaluator


@pytest.mark.asyncio
async def test_empty_code_submission():
    evaluator = DeterministicEvaluator()
    sub = Submission(submitted_code="")
    res = await evaluator.evaluate(sub, PARKING_LOT)

    assert res["score"] == 0.0
    assert len(res["checks"]) == 1
    assert res["checks"][0].rule_id == "EMPTY_SUBMISSION"
    assert not res["checks"][0].passed


@pytest.mark.asyncio
async def test_syntax_error_submission():
    evaluator = DeterministicEvaluator()
    sub = Submission(submitted_code="def broken_func(: pass")
    res = await evaluator.evaluate(sub, PARKING_LOT)

    assert len(res["checks"]) == 1
    assert res["checks"][0].rule_id == "SYNTAX_ERROR"
    assert not res["checks"][0].passed


@pytest.mark.asyncio
async def test_parking_lot_starter_code_passes_checks():
    evaluator = DeterministicEvaluator()
    sub = Submission(submitted_code=PARKING_LOT.starter_code)
    res = await evaluator.evaluate(sub, PARKING_LOT)

    assert res["score"] > 25.0  # Starter code has Vehicle hierarchy, spot, pricing strategy, lock
    checks_by_id = {c.rule_id: c for c in res["checks"]}

    assert checks_by_id["PL_VEHICLE_HIERARCHY"].passed
    assert checks_by_id["PL_PRICING_STRATEGY"].passed
    assert checks_by_id["PL_THREAD_SAFETY"].passed
    assert checks_by_id["PL_GOD_CLASS_CHECK"].passed


@pytest.mark.asyncio
async def test_parking_lot_missing_pricing_strategy():
    evaluator = DeterministicEvaluator()
    bad_code = """
class Vehicle: pass
class Car(Vehicle): pass
class Bike(Vehicle): pass
class ParkingSpot:
    def is_available(self): return True
    def assign_vehicle(self, v): pass
    def vacate(self): pass
class ParkingLot:
    def park(self): pass
"""
    sub = Submission(submitted_code=bad_code)
    res = await evaluator.evaluate(sub, PARKING_LOT)
    checks_by_id = {c.rule_id: c for c in res["checks"]}

    assert not checks_by_id["PL_PRICING_STRATEGY"].passed
    assert not checks_by_id["PL_THREAD_SAFETY"].passed


@pytest.mark.asyncio
async def test_elevator_starter_code_passes_checks():
    evaluator = DeterministicEvaluator()
    sub = Submission(submitted_code=ELEVATOR_SYSTEM.starter_code)
    res = await evaluator.evaluate(sub, ELEVATOR_SYSTEM)

    checks_by_id = {c.rule_id: c for c in res["checks"]}
    assert checks_by_id["EL_CAR_MODEL"].passed
    assert checks_by_id["EL_STATE_PATTERN"].passed
    assert checks_by_id["EL_DISPATCH_STRATEGY"].passed
    assert checks_by_id["EL_CONCURRENCY"].passed


@pytest.mark.asyncio
async def test_vending_machine_state_pattern_checks():
    evaluator = DeterministicEvaluator()
    sub = Submission(submitted_code=VENDING_MACHINE.starter_code)
    res = await evaluator.evaluate(sub, VENDING_MACHINE)

    checks_by_id = {c.rule_id: c for c in res["checks"]}
    assert checks_by_id["VM_STATE_PATTERN"].passed
    assert checks_by_id["VM_INVENTORY_MODEL"].passed
    assert checks_by_id["VM_CONCURRENCY"].passed
