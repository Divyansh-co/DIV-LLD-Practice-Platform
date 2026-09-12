# Design Note: LLD Practice & Evaluation Platform

## MVP Scope

### Problems Included
The platform includes three curated problems:
1. **Multi-Floor Parking Lot (Medium):** Tests class hierarchies, spot allocation, and concurrency across floors and vehicle types.
2. **Elevator Dispatcher & Control System (Hard):** Tests state machine design, request scheduling heuristics, and separation between car physics and dispatcher logic.
3. **State-Driven Vending Machine (Easy):** Tests finite state transitions, transaction handling, and inventory deduction.

### Submission Format
Learners submit three items together:
- **Python Source Code:** The core class definitions, interfaces, and methods.
- **Design Notes:** Written explanations of design decisions, chosen patterns, assumptions, and concurrency trade-offs.
- **Class Diagram (Mermaid DSL):** An optional diagram rendered visually in the UI to illustrate class relationships.

### Why This Format Is Sufficient
Low-level design interviews do not evaluate whether code runs inside a specific packaging setup. They evaluate how a developer organizes abstractions, defines interfaces, and thinks through requirements. Source code demonstrates structure, and design notes explain the intent behind trade-offs that cannot be deduced from syntax alone.

---

## User Flow

1. **Select a Problem:** The user picks a problem from the dashboard, reviewing functional requirements, constraints, and suggested entities.
2. **Work in the Workspace:** The user writes Python code, draft design notes, and Mermaid class diagram text in a multi-tab editor. Draft changes save automatically to the backend SQLite database in the background.
3. **Submit Solution:** The user clicks "Submit Solution". The backend captures an immutable snapshot in `SUBMITTED` status and launches an asynchronous background task.
4. **Intermediate Evaluation Screen:** The frontend transitions to the evaluation view and polls the submission status, showing an active "Evaluating" progress screen.
5. **Review Results:** When the evaluation completes (`COMPLETED`), the user views:
   - Overall score (0 to 100) and grade (Grade S, A, B, C, or Needs Rework).
   - Deterministic checks tab (40 points max) showing passed and failed AST rules with exact line references.
   - Design rubric tab (60 points max) showing 8 evaluation dimensions with per-criterion scores, evidence, concerns, suggestions, and confidence percentages.
   - Architectural critique tab with trade-off notes and a suggested refactor diff.
6. **Failure & Retry:** If evaluation times out or the external model call fails, the submission marks itself as `FAILED`. The user sees an honest error message explaining what failed and can click "Retry Evaluation" to re-process the exact same submission without creating duplicate records.
7. **Iterate:** The user clicks "Edit Solution" to load their previous code, adjust their design based on feedback, and submit a new attempt.

---

## Key Classes and Responsibilities

The codebase splits responsibilities across domain models, evaluators, repositories, and services:

### Domain Models (`backend/app/domain/models.py`)
- `Problem`: Stores problem specifications (title, difficulty, requirements, constraints, starter code, default notes, and starter diagram DSL).
- `Attempt`: Represents a learner's active, editable draft session. Tracks code, design notes, diagram text, and a draft version counter.
- `Submission`: An immutable snapshot of an attempt at submission time. Enforces a strict status state machine (`PENDING` / `SUBMITTED` → `EVALUATING` → `COMPLETED` / `FAILED`). Generates a SHA-256 `content_hash` over the problem ID, code, and notes to prevent duplicate processing.
- `CheckResult`: Encapsulates an individual deterministic AST rule outcome (passed, score, severity, error message, and suggestion).
- `RubricDimensionResult`: Represents a single evaluated rubric criterion (criterion name, score, evidence, concern, suggestion, and confidence).
- `LLMFeedbackReport`: Aggregates the 8 rubric dimensions along with summary text, trade-off analysis, extensibility critique, and suggested refactor diff.
- `EvaluationResult`: Aggregates the overall score, deterministic check score, rubric score, letter grade, and duration in milliseconds.

### Evaluators (`backend/app/evaluators/`)
- `Evaluator` (`base.py`): Abstract base class defining the strategy interface: `name` and `async evaluate(submission, problem) -> Dict[str, Any]`.
- `DeterministicEvaluator` (`deterministic.py`): Parses submitted code into an abstract syntax tree (`ast`) and executes static checks (entity class presence, abstract base classes, type hints, enum usage, and class sizing). Runs entirely locally without network calls.
- `LLMEvaluator` (`llm.py`): Evaluates code and design notes against the 8 rubric dimensions using a remote LLM call (Groq `qwen/qwen3.8-27b`) and parses the structured JSON response.
- `CompositeEvaluator` (`composite.py`): Coordinates `DeterministicEvaluator` and `LLMEvaluator`. Enforces a 25-second timeout, propagates real errors when the service is down, and calculates the combined score (40 points deterministic + 60 points rubric).

### Services and Storage (`backend/app/services/` and `repositories/`)
- `AttemptService` (`services/attempt_service.py`): Manages draft creation, auto-saving, and retrieval of past attempts.
- `EvaluationService` (`services/evaluation_service.py`): Coordinates submission creation, checks content hashes for idempotency, triggers background processing, and manages retries.
- `ProblemRepository`, `AttemptRepository`, `SubmissionRepository` (`repositories/storage.py`): Read and write domain entities to SQLite tables.

---

## Evaluation Approach: Deterministic vs. LLM Split

Evaluation is split 40/60 across two approaches:

1. **Deterministic AST Checks (40 points):**
   Structural rules can and should be evaluated deterministically. If a problem requires an abstract `Vehicle` base class with concrete subclasses, an AST visitor can verify that in milliseconds without hallucinations or API costs. The deterministic evaluator checks class definitions, method signatures, inheritance trees, and flags monolithic classes.

2. **Semantic Rubric Evaluation (60 points):**
   Qualitative design questions cannot be evaluated with static AST rules. Deciding whether a pricing strategy properly decouples billing from spot occupancy requires understanding design intent. This is where an LLM evaluates the code and design notes against 8 defined criteria:
   - Structural Decomposition
   - Pattern Selection
   - Extensibility
   - Separation of Concerns
   - SOLID Compliance
   - Interface Design
   - Failure Handling
   - Trade-off Awareness

### Reality of the LLM Evaluator & Trade-offs
When testing the evaluation logic in Part 1, I saw that the rubric feedback was actually returning static templated text. The reasons were simple: `.env` was not loaded into the running app, the model name (`llama-3.3-70b-versatile`) returned a 404 on Groq, and an `except Exception` block caught the error and quietly swapped in a deterministic heuristic generator (`_generate_heuristic_rubric`).

I fixed this by loading the `.env` file and switching to `qwen/qwen3.8-27b` on Groq with strict JSON output parsing.

I kept `_generate_heuristic_rubric` behind an environment toggle (`ALLOW_HEURISTIC_FALLBACK=1`). Free-tier API keys hit rate limits (HTTP 429) quickly during test runs. Having a deterministic stand-in generator lets unit tests run offline and reliably without breaking on external rate limits. In standard runs, failures are raised directly to the user rather than masked.

---

## Trade-offs and Limitations

1. **Python Only:** The deterministic checks and starter templates currently support only Python. Evaluating Java, C++, or Go would require language-specific AST parsers or LSP integration.
2. **Static AST vs. Dynamic Execution:** The platform inspects code structure using Python's `ast` module; it does not execute the code inside a sandbox or run dynamic test suites against simulated traffic.
3. **Mermaid Diagram Is Evaluated Visually, Not Semantically:** The Mermaid class diagram is rendered to SVG for the learner's convenience, but the current evaluators score only the Python code and design notes.
4. **Third-Party API Dependency:** The semantic rubric relies on Groq. If the external provider experiences downtime or rate limits, submissions can fail and require a retry.

---

## Architectural Extensibility Questions

### 1. What happens to the domain model if a new submission format (e.g. a class diagram as the primary submission, not just code) is added later?

The domain model is already partially prepared for this because `Submission` currently stores `submitted_diagram_dsl` alongside `submitted_code` and `submitted_notes`. 

However, making the diagram the *primary* submission format would require two concrete changes:
- **Hash calculation:** Currently, `Submission.compute_hash()` hashes `problem_id`, `submitted_code`, and `submitted_notes`. It would need to include `submitted_diagram_dsl` (or hash all non-empty submission artifacts) so that changes to only the diagram create a fresh submission hash.
- **Payload generalization:** If future problems allow diagrams without any code at all, `Submission` should replace individual fields (`submitted_code`, `submitted_notes`, `submitted_diagram_dsl`) with an artifacts dictionary or list: `artifacts: Dict[str, str]` (e.g. `{"code": "...", "diagram_dsl": "...", "notes": "..."}`).
- **Evaluator signature:** The `Evaluator.evaluate(submission, problem)` interface already takes the complete `Submission` instance. A new evaluator specializing in diagrams (for example, a `MermaidDiagramEvaluator`) can read `submission.submitted_diagram_dsl` without altering the base interface or changing how routes and background workers call it.

### 2. What happens if a second evaluator (rule-based or human review) is added later — can it be added without rewriting the practice flow?

Yes, it can be added without modifying the practice flow or frontend contracts.

The evaluation engine uses the Strategy Pattern through the `Evaluator` base class:
- Any new evaluator simply subclasses `Evaluator` and implements `evaluate(submission, problem)`.
- `CompositeEvaluator` already acts as an orchestrator. To add a new rule-based engine (such as a linter, cyclomatic complexity checker, or concurrency analyzer), you instantiate the new evaluator inside `CompositeEvaluator`, await its result alongside the deterministic and LLM evaluators, and adjust the score weighting.
- The practice flow (`submit_attempt` endpoint, async background worker, status polling, and `EvaluationResult` data structure) remains identical. The frontend continues to poll `/api/v1/submissions/{id}` and renders the returned `EvaluationResult`.
- If a human review evaluator were added, the only necessary adjustment would be extending the submission status lifecycle (for example, introducing an `AWAITING_REVIEW` state between `EVALUATING` and `COMPLETED`) so the frontend poller displays a waiting message until the review is submitted.
