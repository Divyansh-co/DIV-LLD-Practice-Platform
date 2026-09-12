# Design Note: Low-Level Design (LLD) Platform Architecture

## 1. System Goals & MVP Scope
The primary goal of this platform is to provide an end-to-end sandbox where learners can practice, submit, and receive rigorous, explainable feedback on their Low-Level Designs.

### In-Scope (MVP)
- **Curated Problem Catalog (3 Problems):**
  1. *Multi-Floor Parking Lot* (Vehicle polymorphic hierarchy, spot sizing, Strategy Pattern fee calculation, mutex synchronization).
  2. *Elevator Dispatcher System* (Directional state machine, LOOK/SCAN pluggable scheduling heuristics, starvation avoidance).
  3. *State-Driven Vending Machine* (Gang-of-Four State Pattern with `IdleState`, `HasMoneyState`, `DispenseState`, inventory deduction, atomic transactions).
- **One Deliberately Chosen Submission Format:** Combined Code (Python class declarations with method contracts and attributes) + Concise Design Rationale (Markdown).
- **Observable Submission State Machine:** `SUBMITTED \to EVALUATING \to COMPLETED | FAILED`. Persisted *before* evaluation begins with idempotency protection.
- **Dual-Engine Evaluation Architecture:** Deterministic AST checks (40%) + Structured 8-Dimension AI Rubric (60%).
- **Interactive Assessment Dashboard UI:** Obsidian base (`#0B0F0D`), layered cards (`#141A17`), bright jungle green (`#2FD97F`), soft mint (`#8FEFC3`), warm pearly white (`#F5F7F4`), and a 60fps cursor-reactive background canvas.
- **Iterative Attempt Progression:** Historical timeline showing score deltas across versions.

---

## 2. Core Domain Design & Class Responsibilities

The platform is designed around strict domain boundaries. Every class earns its place:

### 2.1 Domain Class Inventory

| Class | Responsibility Owned | Behaviour Belonging Here | Dependencies | What is Likely to Change | Why Abstraction is Needed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Problem`** | Problem specifications, requirements, constraints, sample entities, and rubric criteria. | Returns starter code templates and rubric weights. | None (pure domain aggregate). | Problem requirements or new problem additions. | Encapsulates problem boundary so evaluation and attempts don't hardcode rules. |
| **`Attempt`** | Learner's interactive draft workspace session. | `update_draft(code, notes, diagram)`, `mark_submitted()`, draft versioning. | Depends on `Problem.id`. | Format of draft scratchpad. | Separates mutable work-in-progress drafts from immutable completed submissions. |
| **`Submission`** | Immutable snapshot submitted for evaluation. | State machine transitions (`start_evaluating()`, `complete_evaluation()`, `fail_evaluation()`, `prepare_retry()`), `compute_hash()`. | Depends on `Attempt.id`, `Problem.id`. | Execution lifecycle states, retry policies. | Guarantees idempotency and persistence *before* evaluation starts. |
| **`RubricDimensionResult`** | Structured evaluation shape for one rubric criterion. | Stores `criterion`, `score`, `max_score`, `evidence`, `concern`, `suggestion`, `confidence`. | None (value object). | Rubric criteria definitions. | Prevents unconstrained LLM output; enforces structured evidence-based feedback. |
| **`EvaluationResult`** | Aggregated evaluation score, grade, and feedback breakdown. | `calculate_grade()`, aggregates deterministic checks and rubric dimensions. | Contains `List[CheckResult]`, `List[RubricDimensionResult]`. | Scoring weights, grading scale. | Unifies multi-engine evaluation into a single observable record. |
| **`Evaluator` (Interface)** | Strategy interface for evaluating submissions. | `evaluate(submission, problem) -> EvaluationResult`. | `Submission`, `Problem`. | Addition of new evaluation strategies. | Decouples deterministic checks from AI evaluation and enables future evaluators (Change Test B). |

---

## 3. Deliberate Submission Format Justification

### Why Combined Code + Design Rationale is the Chosen MVP Format
The platform requires candidates to submit **Python class declarations with method contracts + a brief Design Rationale scratchpad**.

**Justification (The Smallest Format with Sufficient Evidence):**
1. **Why not Pure Text?** Natural language text descriptions cannot unambiguously demonstrate method signatures, encapsulation boundaries, inheritance contracts, or mutex locking. A candidate can write *"I made it thread safe,"* but only code shows whether they used `with self.lock` properly.
2. **Why not Pure UML / Diagram?** UML diagrams show static relationships but fail to capture dynamic behavioral trade-offs, edge-case exception handling, state mutation loops, or financial precision.
3. **Why not Pure Code?** Code alone does not explain *why* a candidate chose Strategy Pattern over Factory, or how they weighed SCAN vs LOOK heuristics.
4. **Conclusion:** Combined Python class declarations (syntax, contracts, concurrency) + Design Rationale (trade-off intent) is the exact industry standard used in Senior/Staff LLD interviews at Google, Meta, and Uber. It provides 100% of the evidence required for both AST structural analysis and semantic rubric evaluation.

---

## 4. Deterministic vs. AI-Assisted Evaluation

| Dimension / Aspect | Deterministic Logic (AST Rule Engine) | AI-Assisted Evaluation (LLM Engine) | Architectural Rationale |
| :--- | :--- | :--- | :--- |
| **Required Structure & Classes** | **Yes:** Checks presence of `Vehicle`, `ParkingSpot`, `Elevator`, `State`. | No | Objective invariant; AST inspection is instant ($\le 20\text{ ms}$) and 100% reliable. |
| **Interface / Strategy Implementation** | **Yes:** Verifies polymorphic base classes and subclasses inherit properly. | No | Inheritance hierarchy is structurally provable from the AST without LLM hallucination. |
| **God Class / Cohesion Threshold** | **Yes:** Counts method definitions and flags classes exceeding threshold (> 10 methods). | No | Objective complexity metric. |
| **Concurrency & Synchronization** | **Yes:** Verifies mutex primitives (`Lock`, `synchronized`, `acquire`). | No | Lock presence is verifiable via AST visitor. |
| **Design Trade-off Reasoning** | No | **Yes:** Compares candidate's choice (e.g. LOOK vs SCAN) against scale implications. | Trade-offs depend on context and cannot be computed via AST syntax. |
| **SOLID Nuance & Extensibility** | No | **Yes:** Probes whether adding a new feature requires modifying existing classes. | Extensibility requires semantic counter-factual reasoning. |
| **Actionable Refactoring Diffs** | No | **Yes:** Generates tailored before/after code refactor snippets. | High cognitive generation task suited for LLMs. |

### The 8 Concrete Rubric Dimensions
Every AI evaluation is anchored to these 8 criteria with the structured shape:
`criterion → score → evidence → concern → suggestion → confidence`
1. **Requirement Understanding** (functional and non-functional scope)
2. **Class Responsibilities** (Single Responsibility Principle, cohesion)
3. **Coupling & Cohesion** (loose coupling, dependency inversion)
4. **Encapsulation and Interfaces** (hiding internals, programming to interfaces)
5. **Appropriate Use of Abstraction / Patterns** (patterns earning their place)
6. **Extensibility When Requirements Change** (Open/Closed Principle)
7. **Edge Cases and Testability** (race conditions, starvation, null safety)
8. **Quality of Explanation** (trade-off justification in design notes)

---

## 5. Architectural Change Tests

### Change Test A: Supporting Class Diagrams Later
> *Question:* Today the learner submits code + notes. Later the platform supports an interactive visual class diagram. How much of the domain model has to change?
- **Domain Impact: Zero core changes.**
- `Submission` already encapsulates `submitted_diagram_dsl: str`. In the domain model, a diagram is simply another representation serialized as Mermaid/JSON DSL.
- `Attempt` already persists `diagram_dsl`.
- To support visual diagrams, we only need to add a `DiagramASTEvaluator` implementing the `Evaluator` interface that parses Mermaid/UML nodes and edges, plugged into `CompositeEvaluator`. The practice workflow, repository layer, and submission state machine remain completely untouched.

### Change Test B: Adding Human Review or New Rule Evaluators Later
> *Question:* Today feedback comes from one composite evaluator. Later a rule-based linter or human reviewer is added. Can it be added without rewriting the practice flow?
- **Domain Impact: Zero practice flow rewrite.**
- The `Evaluator` interface defines:
  ```python
  class Evaluator(ABC):
      async def evaluate(self, submission: Submission, problem: Problem) -> Dict[str, Any]:
          pass
  ```
- Adding a **Human Reviewer**: Implement `HumanReviewEvaluator(Evaluator)` which queues the submission in a review dashboard and completes when a mentor submits the rubric.
- Adding a **Linter Evaluator**: Implement `PylintEvaluator(Evaluator)` which runs static security/complexity linters.
- `CompositeEvaluator` aggregates outputs from any list of `Evaluator` instances. The learner practice flow (`submit_attempt \to poll submission status`) requires zero changes.

---

## 6. Asynchronous Resilience & Idempotency

### 6.1 State Machine Lifecycle
```
[Learner Clicks Submit]
         │
         ▼
 1. Persist Submission (Status: SUBMITTED, ContentHash: SHA256)
         │
         ▼
 2. Dispatch Async Worker (BackgroundTasks)
         │
         ▼
 3. Transition to Status: EVALUATING
         │
         ├─── (Evaluator Success) ──────► Transition to Status: COMPLETED
         │
         └─── (Evaluator Exception) ────► Transition to Status: FAILED (with error_message)
```

### 6.2 Idempotency & Duplicate Submission Handling
- When `submit_attempt()` is called, the service computes:
  `content_hash = SHA256(problem_id + code + notes)`.
- If an active submission with the identical `content_hash` is currently `EVALUATING` or `COMPLETED`, the system returns the existing record immediately without spawning duplicate background evaluation tasks.
- If a submission fails, the learner clicks `Retry Evaluation`. The retry endpoint safely calls `prepare_retry()`, transitioning `FAILED \to SUBMITTED`, incrementing `retry_count`, and dispatching the worker cleanly.

---

## 7. Simple Monolithic Architecture
As specified in the core guidance, the architecture is strictly kept simple as an in-process monolith. All state transitions (`PENDING \to EVALUATING \to COMPLETED | FAILED`) are managed reliably in-process with SQLite and async background workers without unnecessary microservices, distributed queues, or infrastructure overhead.

