# Low-Level Design (LLD) Practice & Assessment Platform

A production-grade, end-to-end sandbox engineered for software developers to practice object-oriented Low-Level Design (OOD/LLD), submit solutions across interactive workstations, and receive explainable, dual-engine feedback (deterministic structural checks + LLM architectural trade-off reasoning).

---

## 1. The Learner Journey
$$\textbf{Choose Problem} \longrightarrow \textbf{Think \& Structure} \longrightarrow \textbf{Submit \& Queue} \longrightarrow \textbf{Explainable Feedback} \longrightarrow \textbf{Review} \longrightarrow \textbf{Try Again}$$

1. **Choose Problem:** Select from curated enterprise problems (**Multi-Floor Parking Lot**, **Elevator Dispatcher System**, or **State-Driven Vending Machine**) with complete functional/non-functional requirements, constraints, and entity models.
2. **Think & Design:** Work in an interactive studio featuring code editor (Python 3.13), architectural trade-off notes (Markdown), and Mermaid class diagram visualization with debounced draft auto-saving.
3. **Submit:** Submit solution and observe the observable asynchronous lifecycle (`PENDING \to EVALUATING \to COMPLETED | FAILED`).
4. **Get Feedback:** Receive explainable, multidimensional feedback separating objective structural invariants from subjective design trade-offs.
5. **Review:** Inspect the SOLID compliance matrix, design trade-off commentary, alternative production patterns, and a concrete before/after code refactoring diff.
6. **Iterate & Try Again:** Jump back into the studio to refine the solution and observe iterative score progression on the historical timeline.

---

## 2. Core Architecture & Domain Design

```
assesment 1 internship/
├── docs/
│   ├── RESEARCH.md               # 1-2 pages: learner problem, existing tools, gaps, product direction
│   ├── DESIGN.md                 # Architecture, domain model, class diagrams, trade-offs
│   ├── AI_USAGE.md               # 4 key AI-assisted decisions: what was suggested vs accepted/rejected
│   └── README.md                 # System overview and quickstart guide
├── backend/
│   ├── app/
│   │   ├── domain/
│   │   │   ├── models.py         # Problem, Attempt, Submission, EvaluationResult, CheckResult
│   │   │   └── rules.py          # LLD structural rules (Parking Lot, Elevator, Vending Machine)
│   │   ├── evaluators/
│   │   │   ├── base.py           # Evaluator abstract strategy interface
│   │   │   ├── deterministic.py  # Python AST static analysis rule engine
│   │   │   ├── llm.py            # LLM semantic & trade-off analyzer (Groq/Gemini + heuristic fallback)
│   │   │   └── composite.py      # Composite orchestrator with async timeout & retry
│   │   ├── repositories/
│   │   │   ├── database.py       # SQLite database initialization with WAL mode
│   │   │   └── storage.py        # Typed repositories for entities
│   │   ├── services/
│   │   │   ├── attempt_service.py    # Draft persistence and session lifecycle
│   │   │   └── evaluation_service.py # State machine, async workers, analytics
│   │   ├── api/
│   │   │   ├── routes.py         # REST API endpoints
│   │   │   └── schemas.py        # Pydantic request/response schemas
│   │   ├── data/
│   │   │   └── seed_problems.py  # Curated problem catalog and starter templates
│   │   └── main.py               # FastAPI application entrypoint
│   ├── tests/
│   │   ├── test_domain_models.py # Model validations & state transitions
│   │   ├── test_deterministic_evaluator.py # AST & rule verification
│   │   ├── test_submission_lifecycle.py   # Async states, timeouts, retries
│   │   └── test_api_endpoints.py # Integration API tests
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── index.css             # Obsidian, pearly white, jungle green tokens & global styles
        ├── App.jsx               # View router and state coordinator
        ├── components/
        │   ├── CanvasBackground.jsx # 60fps cursor-reactive background canvas
        │   ├── Navbar.jsx        # Navigation & profile widget
        │   ├── StatCard.jsx      # Summary metrics card
        │   └── SkillRadar.jsx    # LLD Skill progression tracker
        ├── views/
        │   ├── DashboardView.jsx # Summary stats, progress, recent attempts
        │   ├── PracticeView.jsx  # Split-pane practice studio (brief + editor + draft autosave)
        │   ├── EvaluationView.jsx# Detailed evaluation report & refactoring diff
        │   └── HistoryView.jsx   # Iterative progress timeline per problem
        └── services/
            └── api.js            # Frontend API client
```

### Key Domain Entities
- **`Problem`**: Holds problem specifications, constraints, sample entities, starter code, and rubric weights.
- **`Attempt`**: Manages interactive drafts, auto-saving code, design notes, and diagram DSL with version tracking.
- **`Submission`**: Immutable submission snapshot with explicit lifecycle states (`PENDING \to EVALUATING \to COMPLETED | FAILED`), error details, and retry counters.
- **`EvaluationResult`**: Multidimensional evaluation output aggregating deterministic AST checks, LLM qualitative feedback, category scores, and letter grade (`S`, `A`, `B`, `C`, `Needs Rework`).
- **`Evaluator`**: Strategy Pattern interface decoupling `DeterministicEvaluator` and `LLMEvaluator`, unified under `CompositeEvaluator`.

---

## 3. Dual Evaluation Engine

```mermaid
graph TD
    A[Learner Submission] --> B[Composite Evaluator]
    B --> C[Deterministic AST Rule Engine]
    B --> D[Semantic LLM Evaluator]
    
    subgraph Deterministic Engine (40% Weight)
        C --> C1[AST Node Visitor]
        C1 --> C2[Class Hierarchy & ABC Verification]
        C1 --> C3[Strategy & State Pattern Detection]
        C1 --> C4[God Class & Coupling Detection]
        C1 --> C5[Lock / Mutex Concurrency Guards]
    end
    
    subgraph Semantic Engine (60% Weight)
        D --> D1[Groq / Gemini LLM API]
        D1 -.->|Timeout / Offline| D2[Heuristic Architectural Reasoner]
        D --> D3[SOLID Principles Matrix]
        D --> D4[Design Trade-off Critique]
        D --> D5[Extensibility & Edge Cases Analysis]
        D --> D6[Concrete Refactoring Code Diff]
    end

    C --> E[Aggregator & Rubric Calculator]
    D --> E
    E --> F[EvaluationResult & Letter Grade]
```

---

## 4. Frontend Design System & Aesthetics
- **Bespoke Color Tokens:**
  - Obsidian Black (`--bg-obsidian: #090a0f`)
  - Charcoal Surface (`--bg-surface: #12151d`)
  - Elevated Surface (`--bg-surface-elevated: #181c26`)
  - Pearly White (`--text-pearly: #f4f5f7`)
  - Jungle Green Accents (`--accent-jungle: #10b981`, `--accent-jungle-dark: #0b3d2e`)
  - Semantic Status: Pending (`#f59e0b`), Evaluating (`#38bdf8`), Completed (`#10b981`), Failed (`#ef4444`)
- **Interactive Background Animation:** A high-performance geometric particle constellation rendering at 60fps via `requestAnimationFrame` that gently responds to cursor proximity with low CPU overhead and strict `prefers-reduced-motion` compliance.

---

## 5. Design Questions Answered

### Q1: What does a learner actually need to provide for an attempt to be meaningful?
A meaningful LLD attempt requires:
1. **Core Domain Class Hierarchy & Interfaces:** Abstract base classes/interfaces showing polymorphic boundaries (e.g. `Vehicle` base with `Car`, `Bike`, `Truck`).
2. **Behavioral Methods & Contracts:** Concrete methods showing how objects interact for critical use cases (e.g., `park_vehicle()`, `select_item()`, `dispense()`).
3. **Decoupled Strategy / State Abstractions:** Encapsulation of variable behavior (e.g. `PricingStrategy`, `DispatchStrategy`, or `State` classes) rather than hardcoded `if/else` ladders.
4. **Concurrency Synchronization:** Explicit locking (`threading.Lock`, mutex) around shared mutable state.
5. **Architectural Trade-off Rationale:** A brief explanation of why specific patterns were chosen.

### Q2: What makes feedback useful when more than one valid LLD solution can exist?
LLD problems have multiple valid topologies (e.g., an Elevator system can use SCAN, LOOK, or Nearest-Car heuristics; a Parking Lot can use centralized controllers or per-floor allocators). Useful feedback:
- Never demands a single rigid class name or rigid function signature.
- Separates structural invariants (e.g., *Did you avoid God classes? Is pricing decoupled?*) from subjective trade-offs.
- Explains the trade-off costs of the chosen architecture (e.g., *"Nearest-car minimizes single rider wait time but causes elevator starvation under peak morning traffic"*).
- Provides concrete, side-by-side before/after code refactoring snippets.

### Q3: Which parts of evaluation should be deterministic vs. LLM-assisted, and why?
- **Deterministic (AST Rule Engine):** Class existence, inheritance, interface implementation, method contracts, method count (God Class detection), and lock primitives. These checks are 100% objective, instant ($\le 20\text{ ms}$), and reproducible.
- **LLM-Assisted (Semantic Engine):** Reasoning about scalability trade-offs, state transitions completeness, assessing whether chosen patterns match stated extensibility goals, and crafting realistic refactoring diffs.

### Q4: How does the design accommodate a new evaluation approach or submission format?
- **Evaluator Strategy Pattern (`Evaluator`):** Any new evaluation technique (e.g. Linter, Cyclomatic Complexity Analyzer, Security Scanner) simply implements `Evaluator.evaluate()` and is added to `CompositeEvaluator`.
- **Submission Formats:** `Submission` encapsulates `submitted_code`, `submitted_notes`, and `submitted_diagram_dsl`. Adding support for Java, TypeScript, or JSON schemas requires only adding language-specific AST visitor strategies without changing the domain model.

### Q5: What happens if evaluation takes time or fails?
- **Asynchronous Lifecycle:** Submissions immediately receive a `PENDING` state and a background worker evaluates them without blocking HTTP requests.
- **Timeouts & Fallbacks:** The LLM call is protected by an 8-second timeout. If third-party APIs fail or rate limit, the system gracefully falls back to an intelligent heuristic reasoning engine so the learner receives rich feedback with zero crashes.
- **Retries:** Failed submissions expose a retry endpoint (`POST /api/v1/submissions/{id}/retry`) resetting state to `PENDING` and incrementing `retry_count`.

---

## 6. How to Run the Project

### Prerequisites
- Python 3.11+ (Python 3.13 tested)
- Node.js 18+ & npm

### 1. Run the Backend API
```powershell
cd "backend"
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server (runs on http://127.0.0.1:8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger API Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/v1/health`

### 2. Run the Frontend Dashboard
```powershell
cd "frontend"
# Install dependencies
npm install

# Start Vite dev server (runs on http://127.0.0.1:5173)
npm run dev
```
Open `http://127.0.0.1:5173` in your browser.

### 3. Run the Automated Test Suite
```powershell
cd "backend"
python -m pytest tests -v
```
**Results:** 22 / 22 tests pass (100% pass rate).

---

## 7. Monolith Architecture Note
This platform intentionally follows a clean, single-service monolithic architecture (FastAPI backend + Vite React frontend) with zero microservice, distributed queue, or container orchestration overhead, focusing strictly on object-oriented low-level design, class responsibilities, interfaces, and explainable evaluation.

---

## 8. Known Limitations
- **Language Coverage:** Deterministic AST static analyzer targets Python 3 class structures and contracts.
- **Diagram DSL:** Stores and evaluates Mermaid DSL for class relationships alongside code and trade-off notes.

