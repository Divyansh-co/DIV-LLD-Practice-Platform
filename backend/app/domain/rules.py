"""Rule definitions and rubric specifications for LLD problems.

These rules are executed by the Deterministic AST Evaluator to verify
structural integrity, design pattern adherence, and SOLID principles.
"""

from typing import Callable, Dict, List, Optional
from app.domain.models import CheckCategory, CheckSeverity


class RuleDefinition:
    def __init__(
        self,
        rule_id: str,
        name: str,
        category: CheckCategory,
        max_score: float,
        severity: CheckSeverity,
        description: str,
        suggestion: str,
        validator_name: str,
        parameters: Optional[Dict] = None,
    ):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.max_score = max_score
        self.severity = severity
        self.description = description
        self.suggestion = suggestion
        self.validator_name = validator_name
        self.parameters = parameters or {}


# ---------------------------------------------------------------------------
# Parking Lot Rules
# ---------------------------------------------------------------------------
PARKING_LOT_RULES: List[RuleDefinition] = [
    RuleDefinition(
        rule_id="PL_VEHICLE_HIERARCHY",
        name="Polymorphic Vehicle Hierarchy",
        category=CheckCategory.STRUCTURAL,
        max_score=8.0,
        severity=CheckSeverity.CRITICAL,
        description="Verify abstract Vehicle base class and concrete subtypes (Car, Bike, Truck).",
        suggestion="Create an abstract class 'Vehicle' with vehicle_type and license_plate, extended by Car, Bike, Truck.",
        validator_name="check_class_hierarchy",
        parameters={"base_class": "Vehicle", "subclasses": ["Car", "Bike", "Truck", "Motorcycle"]},
    ),
    RuleDefinition(
        rule_id="PL_SPOT_MODEL",
        name="Parking Spot Domain Model & Sizing",
        category=CheckCategory.STRUCTURAL,
        max_score=8.0,
        severity=CheckSeverity.CRITICAL,
        description="Ensure dedicated ParkingSpot entity with spot type / size compatibility checks.",
        suggestion="Define a 'ParkingSpot' class with can_fit_vehicle() or is_available attributes.",
        validator_name="check_class_methods",
        parameters={"class_name": "ParkingSpot", "required_methods": ["is_available", "assign_vehicle", "vacate", "can_fit"]},
    ),
    RuleDefinition(
        rule_id="PL_PRICING_STRATEGY",
        name="Open/Closed: Decoupled Pricing Strategy",
        category=CheckCategory.PATTERNS,
        max_score=10.0,
        severity=CheckSeverity.CRITICAL,
        description="Ensure pricing calculation uses Strategy Pattern rather than hardcoded if/else in Ticket or ParkingLot.",
        suggestion="Implement a 'PricingStrategy' or 'FeeCalculator' interface/base class with compute_fee() method.",
        validator_name="check_strategy_pattern",
        parameters={"pattern_class": "PricingStrategy", "strategy_method": "calculate_fee", "alternates": ["FeeStrategy", "CostStrategy"]},
    ),
    RuleDefinition(
        rule_id="PL_GOD_CLASS_CHECK",
        name="Single Responsibility: Avoid God Class",
        category=CheckCategory.SOLID,
        max_score=6.0,
        severity=CheckSeverity.WARNING,
        description="Verify ParkingLot does not conflate ticket printing, payment processing, and spot allocation.",
        suggestion="Delegate parking spot allocation to a 'ParkingFloor' or 'AllocationStrategy' and payments to PaymentService.",
        validator_name="check_god_class",
        parameters={"class_name": "ParkingLot", "max_method_threshold": 10},
    ),
    RuleDefinition(
        rule_id="PL_THREAD_SAFETY",
        name="Concurrency Guard: Spot Allocation Lock",
        category=CheckCategory.CONCURRENCY,
        max_score=8.0,
        severity=CheckSeverity.CRITICAL,
        description="Ensure parking spot assignment uses synchronization or Lock primitives to prevent double booking.",
        suggestion="Use 'threading.Lock', 'RLock', or synchronized blocks when querying and allocating available spots.",
        validator_name="check_concurrency_lock",
        parameters={"lock_tokens": ["Lock", "RLock", "mutex", "synchronized", "acquire", "with self.lock"]},
    ),
]


# ---------------------------------------------------------------------------
# Elevator System Rules
# ---------------------------------------------------------------------------
ELEVATOR_RULES: List[RuleDefinition] = [
    RuleDefinition(
        rule_id="EL_CAR_MODEL",
        name="Elevator Car & State Modeling",
        category=CheckCategory.STRUCTURAL,
        max_score=8.0,
        severity=CheckSeverity.CRITICAL,
        description="Verify Elevator / ElevatorCar entity encapsulates current floor, direction, and state.",
        suggestion="Define ElevatorCar with current_floor, state (IDLE, MOVING_UP, MOVING_DOWN), and door status.",
        validator_name="check_class_exists",
        parameters={"class_names": ["Elevator", "ElevatorCar", "Car"]},
    ),
    RuleDefinition(
        rule_id="EL_STATE_PATTERN",
        name="Elevator State Management",
        category=CheckCategory.PATTERNS,
        max_score=10.0,
        severity=CheckSeverity.CRITICAL,
        description="Check for explicit state modeling (State Pattern or distinct enum/handlers) rather than nested conditionals.",
        suggestion="Represent ElevatorState with dedicated states (Idle, Moving, DoorOpen) or State interface.",
        validator_name="check_state_representation",
        parameters={"state_tokens": ["ElevatorState", "Direction", "IdleState", "MovingState"]},
    ),
    RuleDefinition(
        rule_id="EL_DISPATCH_STRATEGY",
        name="Open/Closed: Dispatcher Scheduling Strategy",
        category=CheckCategory.PATTERNS,
        max_score=10.0,
        severity=CheckSeverity.CRITICAL,
        description="Ensure elevator request scheduling algorithm (e.g. SCAN, LOOK, Nearest-Car) is decoupled from the controller.",
        suggestion="Implement a 'DispatchStrategy' interface allowing algorithms like ScanStrategy or LookStrategy to be swapped.",
        validator_name="check_strategy_pattern",
        parameters={"pattern_class": "DispatchStrategy", "strategy_method": "select_elevator", "alternates": ["ElevatorSchedulingStrategy", "DispatcherStrategy"]},
    ),
    RuleDefinition(
        rule_id="EL_REQUEST_QUEUE",
        name="Request / Floor Button Model",
        category=CheckCategory.STRUCTURAL,
        max_score=6.0,
        severity=CheckSeverity.WARNING,
        description="Verify clear separation between internal car requests and external hall call requests.",
        suggestion="Define a 'Request' or 'HallCall' class containing source_floor, destination_floor, and direction.",
        validator_name="check_class_exists",
        parameters={"class_names": ["Request", "ElevatorRequest", "FloorButton", "HallCall"]},
    ),
    RuleDefinition(
        rule_id="EL_CONCURRENCY",
        name="Thread-Safe Request Processing",
        category=CheckCategory.CONCURRENCY,
        max_score=6.0,
        severity=CheckSeverity.WARNING,
        description="Ensure request ingestion and elevator dispatch loops use thread-safe queues or lock guards.",
        suggestion="Protect internal floor destination queues using mutex locks or threading.Queue.",
        validator_name="check_concurrency_lock",
        parameters={"lock_tokens": ["Lock", "Queue", "PriorityQueue", "acquire", "with self.lock"]},
    ),
]


# ---------------------------------------------------------------------------
# Vending Machine Rules
# ---------------------------------------------------------------------------
VENDING_MACHINE_RULES: List[RuleDefinition] = [
    RuleDefinition(
        rule_id="VM_STATE_PATTERN",
        name="Gang of Four State Pattern Implementation",
        category=CheckCategory.PATTERNS,
        max_score=12.0,
        severity=CheckSeverity.CRITICAL,
        description="Enforce State interface with concrete states (IdleState, HasMoneyState, DispensingState, SoldOutState).",
        suggestion="Implement 'VendingMachineState' with methods: insert_coin, select_item, dispense, refund.",
        validator_name="check_class_hierarchy",
        parameters={"base_class": "State", "subclasses": ["IdleState", "HasMoneyState", "DispenseState", "SoldOutState"]},
    ),
    RuleDefinition(
        rule_id="VM_INVENTORY_MODEL",
        name="Inventory & Product Encapsulation",
        category=CheckCategory.STRUCTURAL,
        max_score=8.0,
        severity=CheckSeverity.CRITICAL,
        description="Verify Item/Product and Inventory encapsulation with stock quantity tracking.",
        suggestion="Define 'Item' (name, price, code) and 'Inventory' class to manage item counts and availability.",
        validator_name="check_class_methods",
        parameters={"class_name": "Inventory", "required_methods": ["get_item", "deduct_stock", "is_available", "restock"]},
    ),
    RuleDefinition(
        rule_id="VM_PAYMENT_CHANGE",
        name="Payment & Change Calculation",
        category=CheckCategory.STRUCTURAL,
        max_score=8.0,
        severity=CheckSeverity.CRITICAL,
        description="Check for coin/cash handling, balance tracking, and accurate change return calculation.",
        suggestion="Encapsulate coin handling in a Coin/PaymentManager class with calculate_change() and refund().",
        validator_name="check_class_exists",
        parameters={"class_names": ["PaymentProcessor", "CoinManager", "Coin", "MoneyHandler"]},
    ),
    RuleDefinition(
        rule_id="VM_SOLID_SRP",
        name="Single Responsibility: State vs Vending Context",
        category=CheckCategory.SOLID,
        max_score=6.0,
        severity=CheckSeverity.WARNING,
        description="VendingMachine context should delegate transitions to current State rather than modifying them directly.",
        suggestion="Call state.dispense() or state.insert_money() rather than having VendingMachine inspect internal enums.",
        validator_name="check_method_delegation",
        parameters={"context_class": "VendingMachine", "target_class": "State"},
    ),
    RuleDefinition(
        rule_id="VM_CONCURRENCY",
        name="Atomic Dispense & Stock Deduction",
        category=CheckCategory.CONCURRENCY,
        max_score=6.0,
        severity=CheckSeverity.WARNING,
        description="Ensure stock decrement and change refund are atomic to avoid race conditions under simultaneous purchase.",
        suggestion="Use a Lock around the dispensing routine to guarantee single-consumer checkout.",
        validator_name="check_concurrency_lock",
        parameters={"lock_tokens": ["Lock", "acquire", "with self.lock", "threading"]},
    ),
]


PROBLEM_RULES_REGISTRY: Dict[str, List[RuleDefinition]] = {
    "parking-lot": PARKING_LOT_RULES,
    "elevator-system": ELEVATOR_RULES,
    "vending-machine": VENDING_MACHINE_RULES,
}
