"""Curated Problem Catalog for the LLD Practice Platform.

Contains detailed specifications, requirements, starter templates, and
rubrics for Parking Lot, Elevator System, and Vending Machine.
"""

from typing import Dict, List
from app.domain.models import Difficulty, Problem


PARKING_LOT = Problem(
    id="prob_parking_lot",
    slug="parking-lot",
    title="Design a Multi-Floor Parking Lot",
    difficulty=Difficulty.MEDIUM,
    domain="Resource Allocation & Concurrency",
    summary=(
        "Design a robust, multi-level parking facility capable of accommodating different vehicle "
        "types (Motorcycles, Cars, Large Trucks), dynamically allocating spots, issuing tickets, "
        "and supporting flexible pricing strategies with thread-safe operations."
    ),
    functional_requirements=[
        "Support multi-level parking with distinct spot types (Compact, Regular, Large, Handicapped).",
        "Vehicle types: Motorcycle/Bike (fits anywhere), Car (Regular/Large), Truck/Bus (Large only).",
        "Assign an optimal spot upon vehicle entry and generate an entry ticket.",
        "Vacate spot upon departure and calculate parking fee based on duration and vehicle type.",
        "Extensible pricing engine: support hourly rates, flat fees, and future peak-hour surge pricing.",
        "Display real-time availability board per floor and per vehicle category.",
    ],
    non_functional_requirements=[
        "Thread Safety: Multiple entry and exit gates operating concurrently must never double-book a spot.",
        "Extensibility (Open/Closed Principle): Adding a new vehicle type (e.g., Electric Vehicle with charging) or new pricing formula must not require modifying core spot allocation code.",
        "Low Latency: Spot lookup and allocation must execute in O(1) or O(log N) time per floor.",
    ],
    constraints=[
        "Capacity: Up to 5 floors, 200 spots per floor.",
        "A spot can only be occupied by one vehicle at a time.",
        "If no suitable spot exists, entry gate must cleanly reject vehicle with an appropriate response.",
    ],
    sample_entities=[
        "Vehicle (abstract), Car, Motorcycle, Truck",
        "ParkingSpot (abstract/concrete), CompactSpot, LargeSpot, BikeSpot",
        "ParkingFloor, ParkingLot (Singleton or Controller)",
        "ParkingTicket, Gate (EntryGate, ExitGate)",
        "PricingStrategy (Strategy Pattern: HourlyPricing, FlatPricing)",
    ],
    starter_code="""from abc import ABC, abstractmethod
from enum import Enum
import time
import threading
from typing import Dict, List, Optional


class VehicleType(Enum):
    MOTORCYCLE = 1
    CAR = 2
    TRUCK = 3


class SpotType(Enum):
    MOTORCYCLE = 1
    COMPACT = 2
    LARGE = 3


class Vehicle(ABC):
    \"\"\"Abstract Vehicle base class.\"\"\"
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type


class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)


class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.MOTORCYCLE)


class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)


class ParkingSpot:
    \"\"\"Represents an individual parking slot.\"\"\"
    def __init__(self, spot_id: str, spot_type: SpotType):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.vehicle: Optional[Vehicle] = None
        self.is_available: bool = True

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        # TODO: Implement spot compatibility check
        return False

    def assign_vehicle(self, vehicle: Vehicle) -> bool:
        # TODO: Assign vehicle if available
        return False

    def vacate(self) -> None:
        # TODO: Vacate spot
        pass


class PricingStrategy(ABC):
    \"\"\"Strategy interface for extensible parking fee calculations.\"\"\"
    @abstractmethod
    def calculate_fee(self, duration_hours: float, vehicle_type: VehicleType) -> float:
        pass


class HourlyPricingStrategy(PricingStrategy):
    def calculate_fee(self, duration_hours: float, vehicle_type: VehicleType) -> float:
        rate = {VehicleType.MOTORCYCLE: 10.0, VehicleType.CAR: 20.0, VehicleType.TRUCK: 40.0}
        return duration_hours * rate.get(vehicle_type, 20.0)


class ParkingLot:
    \"\"\"Main controller for parking lot operations.\"\"\"
    def __init__(self, lot_id: str):
        self.lot_id = lot_id
        self.spots: Dict[str, ParkingSpot] = {}
        self.pricing_strategy: PricingStrategy = HourlyPricingStrategy()
        self.lock = threading.Lock()

    def park_vehicle(self, vehicle: Vehicle):
        with self.lock:
            # TODO: Thread-safe spot allocation and ticket issuance
            pass

    def vacate_vehicle(self, ticket_id: str):
        with self.lock:
            # TODO: Release spot, calculate fee, and return receipt
            pass
""",
    default_notes_template="""# Architecture & Design Rationale

## 1. Class Responsibilities & Abstractions
- **Vehicle Hierarchy:** Polymorphic inheritance with Vehicle abstract base.
- **ParkingSpot:** Encapsulates spot state and vehicle sizing constraints.
- **PricingStrategy:** Decoupled via Strategy Pattern to satisfy Open/Closed Principle.

## 2. Concurrency & Thread Safety
- Used `threading.Lock` across spot querying and reservation to prevent race conditions.

## 3. Trade-offs Considered
- **Centralized vs Floor-level allocation:** Evaluated single lock vs per-floor locks.
""",
    starter_diagram_dsl="""classDiagram
    class Vehicle {
        <<abstract>>
        +string license_plate
        +VehicleType vehicle_type
    }
    class Car
    class Motorcycle
    class Truck
    Vehicle <|-- Car
    Vehicle <|-- Motorcycle
    Vehicle <|-- Truck

    class ParkingSpot {
        +string spot_id
        +SpotType spot_type
        +bool is_available
        +can_fit_vehicle(Vehicle)
        +assign_vehicle(Vehicle)
        +vacate()
    }

    class PricingStrategy {
        <<interface>>
        +calculate_fee(duration, vehicle_type)
    }

    class ParkingLot {
        -spots: List~ParkingSpot~
        -strategy: PricingStrategy
        +park_vehicle(Vehicle)
        +vacate_vehicle(ticket_id)
    }

    ParkingLot --> ParkingSpot
    ParkingLot --> PricingStrategy
""",
)


ELEVATOR_SYSTEM = Problem(
    id="prob_elevator_system",
    slug="elevator-system",
    title="Design an Elevator Dispatcher & Control System",
    difficulty=Difficulty.HARD,
    domain="State Machine & Scheduling Algorithms",
    summary=(
        "Design a building elevator management system supporting multiple elevator cars, handling "
        "internal floor requests and external up/down hall calls efficiently using state pattern and "
        "pluggable dispatch heuristics (e.g. SCAN, LOOK, FCFS)."
    ),
    functional_requirements=[
        "Support multi-car elevator banks (e.g., 4 elevators serving 20 floors).",
        "Process internal requests (user inside car presses destination floor).",
        "Process external hall calls (user at floor presses UP or DOWN button).",
        "Elevator cars transition cleanly across states: IDLE, MOVING_UP, MOVING_DOWN, DOOR_OPEN.",
        "Dispatcher assigns incoming calls to the optimal elevator car to minimize wait and journey times.",
        "Safety and edge cases: Emergency stop, weight overload sensor, and maintenance mode.",
    ],
    non_functional_requirements=[
        "Extensible Dispatch Algorithm: Easy to plug new scheduling strategies (LOOK, SCAN, Energy-Saver) without rewriting elevator car logic.",
        "Thread Safety: Concurrent hall requests and elevator movement ticks must be synchronized.",
        "Starvation Prevention: Requests in the opposite direction must eventually be serviced without infinite wait.",
    ],
    constraints=[
        "Building: 1 to 30 floors, 2 to 6 elevator cars.",
        "Door opening/closing takes finite simulated time.",
        "Car moves 1 floor at a time in current direction until no further requests exist ahead.",
    ],
    sample_entities=[
        "ElevatorCar, ElevatorState (State Pattern or Enum)",
        "ElevatorController / Dispatcher",
        "DispatchStrategy (LOOKStrategy, ScanStrategy, NearestCarStrategy)",
        "Request (InternalRequest, HallCall), Direction (UP, DOWN, NONE)",
    ],
    starter_code="""from abc import ABC, abstractmethod
from enum import Enum
import threading
from typing import List, Set, Optional


class Direction(Enum):
    UP = 1
    DOWN = 2
    IDLE = 3


class ElevatorState(Enum):
    IDLE = 1
    MOVING_UP = 2
    MOVING_DOWN = 3
    DOOR_OPEN = 4


class Request:
    \"\"\"Represents a passenger hall call or internal destination request.\"\"\"
    def __init__(self, source_floor: int, destination_floor: int, direction: Direction):
        self.source_floor = source_floor
        self.destination_floor = destination_floor
        self.direction = direction


class Elevator:
    \"\"\"Represents a single elevator car.\"\"\"
    def __init__(self, car_id: int, min_floor: int = 1, max_floor: int = 20):
        self.car_id = car_id
        self.current_floor = 1
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        self.destinations: Set[int] = set()
        self.lock = threading.Lock()

    def add_destination(self, floor: int):
        with self.lock:
            self.destinations.add(floor)

    def move_step(self):
        with self.lock:
            # TODO: Advance one floor in current direction, check doors and stops
            pass


class DispatchStrategy(ABC):
    \"\"\"Strategy for allocating incoming hall requests to an elevator car.\"\"\"
    @abstractmethod
    def select_elevator(self, elevators: List[Elevator], request: Request) -> Elevator:
        pass


class NearestCarStrategy(DispatchStrategy):
    def select_elevator(self, elevators: List[Elevator], request: Request) -> Elevator:
        # Simple heuristic: nearest idle or same-direction car
        return min(elevators, key=lambda e: abs(e.current_floor - request.source_floor))


class ElevatorController:
    \"\"\"Coordinates elevator bank and schedules dispatching.\"\"\"
    def __init__(self, elevators: List[Elevator], strategy: Optional[DispatchStrategy] = None):
        self.elevators = elevators
        self.strategy = strategy or NearestCarStrategy()
        self.lock = threading.Lock()

    def handle_hall_call(self, request: Request):
        with self.lock:
            car = self.strategy.select_elevator(self.elevators, request)
            car.add_destination(request.source_floor)
""",
    default_notes_template="""# Elevator System Design Rationale

## 1. Scheduling & Algorithm Choice
- Decoupled `DispatchStrategy` via Strategy Pattern.
- Considered SCAN (Elevator Algorithm) vs LOOK algorithm for throughput optimization.

## 2. State Modeling
- Modeled Elevator states: IDLE, MOVING_UP, MOVING_DOWN, DOOR_OPEN.
""",
    starter_diagram_dsl="""classDiagram
    class Direction {
        <<enumeration>>
        UP
        DOWN
        IDLE
    }
    class Elevator {
        +int car_id
        +int current_floor
        +Direction direction
        +ElevatorState state
        +add_destination(floor)
        +move_step()
    }
    class DispatchStrategy {
        <<interface>>
        +select_elevator(elevators, request)
    }
    class ElevatorController {
        -elevators: List~Elevator~
        -strategy: DispatchStrategy
        +handle_hall_call(request)
    }
    ElevatorController --> Elevator
    ElevatorController --> DispatchStrategy
""",
)


VENDING_MACHINE = Problem(
    id="prob_vending_machine",
    slug="vending-machine",
    title="Design a State-Driven Vending Machine",
    difficulty=Difficulty.EASY,
    domain="Gang-of-Four State Pattern",
    summary=(
        "Design a multi-product vending machine handling coin/bill inputs, product selection, "
        "dispensing, change calculation, and cancellation using the classic Gang of Four State Pattern."
    ),
    functional_requirements=[
        "Support item selection by slot/code with varying prices and stock quantities.",
        "Accept money (coins/notes: $1, $5, quarters, dimes) and maintain user current balance.",
        "Transition through states: IdleState -> HasMoneyState -> DispensingState -> SoldOutState.",
        "Refund full balance if user cancels before dispensing.",
        "Dispense item, deduct inventory, and compute correct change upon successful purchase.",
        "Maintain internal cash float and handle out-of-change or out-of-stock scenarios gracefully.",
    ],
    non_functional_requirements=[
        "Gang of Four State Pattern: Every state must encapsulate its allowed transitions and actions.",
        "No God Conditional: Avoid monolithic switch/case or nested if/elif statements inside VendingMachine.",
        "Atomic Transaction: Item dispensing and money acceptance must be atomic to prevent inventory loss.",
    ],
    constraints=[
        "Up to 20 slots, max 10 items per slot.",
        "Coins/bills are validated upon insertion.",
        "Cannot dispense item if inserted amount is less than item price.",
    ],
    sample_entities=[
        "VendingMachine (Context)",
        "State (abstract interface), IdleState, HasMoneyState, DispenseState, SoldOutState",
        "Item, Inventory",
        "Coin / Bill, PaymentProcessor",
    ],
    starter_code="""from abc import ABC, abstractmethod
import threading
from typing import Dict, Optional


class Item:
    def __init__(self, code: str, name: str, price: float):
        self.code = code
        self.name = name
        self.price = price


class Inventory:
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.stock: Dict[str, int] = {}

    def add_item(self, item: Item, quantity: int):
        self.items[item.code] = item
        self.stock[item.code] = quantity

    def is_available(self, code: str) -> bool:
        return self.stock.get(code, 0) > 0

    def deduct_stock(self, code: str) -> None:
        if self.is_available(code):
            self.stock[code] -= 1

    def get_item(self, code: str) -> Optional[Item]:
        return self.items.get(code)


class State(ABC):
    \"\"\"Gang of Four State interface for Vending Machine.\"\"\"
    @abstractmethod
    def insert_money(self, machine: 'VendingMachine', amount: float) -> None:
        pass

    @abstractmethod
    def select_item(self, machine: 'VendingMachine', code: str) -> None:
        pass

    @abstractmethod
    def dispense(self, machine: 'VendingMachine') -> None:
        pass

    @abstractmethod
    def cancel(self, machine: 'VendingMachine') -> float:
        pass


class IdleState(State):
    def insert_money(self, machine: 'VendingMachine', amount: float) -> None:
        machine.current_balance += amount
        machine.set_state(machine.has_money_state)

    def select_item(self, machine: 'VendingMachine', code: str) -> None:
        print("Please insert money first.")

    def dispense(self, machine: 'VendingMachine') -> None:
        print("No item selected.")

    def cancel(self, machine: 'VendingMachine') -> float:
        return 0.0


class HasMoneyState(State):
    def insert_money(self, machine: 'VendingMachine', amount: float) -> None:
        machine.current_balance += amount

    def select_item(self, machine: 'VendingMachine', code: str) -> None:
        item = machine.inventory.get_item(code)
        if not item or not machine.inventory.is_available(code):
            print("Item out of stock.")
            return
        if machine.current_balance < item.price:
            print(f"Insufficient balance. Need ${item.price - machine.current_balance:.2f} more.")
            return
        machine.selected_code = code
        machine.set_state(machine.dispense_state)
        machine.dispense()

    def dispense(self, machine: 'VendingMachine') -> None:
        pass

    def cancel(self, machine: 'VendingMachine') -> float:
        refund = machine.current_balance
        machine.current_balance = 0.0
        machine.set_state(machine.idle_state)
        return refund


class DispenseState(State):
    def insert_money(self, machine: 'VendingMachine', amount: float) -> None:
        print("Dispensing in progress, cannot accept money.")

    def select_item(self, machine: 'VendingMachine', code: str) -> None:
        print("Already dispensing.")

    def dispense(self, machine: 'VendingMachine') -> None:
        item = machine.inventory.get_item(machine.selected_code)
        if item:
            machine.inventory.deduct_stock(item.code)
            change = machine.current_balance - item.price
            machine.current_balance = 0.0
            machine.selected_code = None
            print(f"Dispensed {item.name}. Change returned: ${change:.2f}")
        machine.set_state(machine.idle_state)

    def cancel(self, machine: 'VendingMachine') -> float:
        print("Cannot cancel while dispensing.")
        return 0.0


class VendingMachine:
    \"\"\"Context class coordinating states and inventory.\"\"\"
    def __init__(self):
        self.inventory = Inventory()
        self.current_balance: float = 0.0
        self.selected_code: Optional[str] = None
        self.lock = threading.Lock()

        # State instances
        self.idle_state = IdleState()
        self.has_money_state = HasMoneyState()
        self.dispense_state = DispenseState()

        self.current_state: State = self.idle_state

    def set_state(self, state: State):
        self.current_state = state

    def insert_money(self, amount: float):
        with self.lock:
            self.current_state.insert_money(self, amount)

    def select_item(self, code: str):
        with self.lock:
            self.current_state.select_item(self, code)

    def dispense(self):
        with self.lock:
            self.current_state.dispense(self)

    def cancel(self) -> float:
        with self.lock:
            return self.current_state.cancel(self)
""",
    default_notes_template="""# Vending Machine Design Rationale

## 1. State Pattern Application
- Applied GoF State Pattern (`State` interface, `IdleState`, `HasMoneyState`, `DispenseState`).
- Decoupled state transition rules from the `VendingMachine` context.

## 2. Concurrency & Atomicity
- Encapsulated money deduction and inventory decrement under `threading.Lock`.
""",
    starter_diagram_dsl="""classDiagram
    class State {
        <<interface>>
        +insert_money(machine, amount)
        +select_item(machine, code)
        +dispense(machine)
        +cancel(machine)
    }
    class IdleState
    class HasMoneyState
    class DispenseState
    State <|-- IdleState
    State <|-- HasMoneyState
    State <|-- DispenseState

    class VendingMachine {
        -current_state: State
        -inventory: Inventory
        +insert_money(amount)
        +select_item(code)
        +dispense()
        +cancel()
    }
    VendingMachine --> State
""",
)


SEED_PROBLEMS: List[Problem] = [
    PARKING_LOT,
    ELEVATOR_SYSTEM,
    VENDING_MACHINE,
]

PROBLEMS_BY_SLUG: Dict[str, Problem] = {p.slug: p for p in SEED_PROBLEMS}
PROBLEMS_BY_ID: Dict[str, Problem] = {p.id: p for p in SEED_PROBLEMS}
