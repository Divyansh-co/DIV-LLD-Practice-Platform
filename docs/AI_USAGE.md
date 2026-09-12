# AI Usage & Architectural Decision Record

This document records 4 key architectural decisions made during the design and implementation of the Low-Level Design (LLD) Practice Platform where AI proposals were evaluated, refined, or rejected in favor of sound software engineering and product principles.

---

## Decision 1: Evaluation Architecture — AST Static Analysis vs Sandboxed Code Execution vs Pure LLM

### What the AI Proposed:
Initially, the AI suggested two extremes:
1. **Option A (Pure Dynamic Execution):** Running learner code in a Docker/subprocess sandbox with predefined unit tests (similar to LeetCode).
2. **Option B (Pure LLM Grading):** Sending the entire learner solution to an LLM with a prompt like *"Grade this Low-Level Design from 1 to 100 on SOLID principles"*.

### What Was Accepted / Rejected and Why:
- **Rejected Option A (Pure Unit Tests):** In algorithmic challenges (e.g. two-sum), inputs and outputs are rigid. In LLD, there are multiple valid class hierarchies and naming choices. One learner might name their spot reservation method `park_vehicle()`, while another names it `assign_spot()`. A unit test harness that relies on rigid reflection fails valid architectural designs and frustrates the learner.
- **Rejected Option B (Pure LLM Grading):** Pure LLM grading is non-deterministic, prone to sycophancy (giving high praise to broken code), suffers from hallucination, and fails to provide reliable, objective baselines.
- **Accepted Decision (Hybrid AST Rule Engine + LLM Semantic Evaluator):**
  - We implemented a **Deterministic AST Analyzer** (`app/evaluators/deterministic.py`) that parses the Python Abstract Syntax Tree to objectively verify class relationships, inheritance hierarchies, abstract base classes, interface definitions, method counts (detecting God Classes), and concurrency primitives (`Lock`, `synchronized`).
  - We paired this with an **LLM Semantic Evaluator** (`app/evaluators/llm.py`) tasked *only* with subjective trade-offs, extensibility critique, and architectural nuances.
  - **Outcome:** 100% reproducible structural guardrails combined with deep contextual architectural feedback.

---

## Decision 2: Asynchronous Job Processing — RabbitMQ/Celery vs Lightweight In-Process State Machine

### What the AI Proposed:
The AI suggested setting up a Celery worker pool with a RabbitMQ or Redis message broker to manage asynchronous submission evaluation tasks.

### What Was Accepted / Rejected and Why:
- **Rejected:** Setting up Redis, RabbitMQ, and Celery workers violates the assignment's explicit constraint: *"Prioritize clean low-level design (LLD) over infrastructure complexity... A simple monolith is completely acceptable — do not build Kubernetes, microservices, multi-region deployment, sharding, or CDN-level infrastructure."*
- **Accepted Decision:**
  - Designed an in-process, observable state machine on the `Submission` domain model (`PENDING \to EVALUATING \to COMPLETED | FAILED`) managed by FastAPI's native background task executor and an async `EvaluationService`.
  - Built an explicit timeout handler (8-second threshold) and a retry endpoint (`POST /api/v1/submissions/{id}/retry`) that safely transitions state and increments `retry_count`.
  - Documented high-level scalability considerations (how this transitions to a distributed queue under heavy enterprise load) in the design note.
  - **Outcome:** Clean domain design, zero external devops dependencies, instant local setup, and fully testable async state transitions.

---

## Decision 3: Frontend Design Aesthetics — Generic Tailwind/Chakra UI vs Bespoke CSS Token System

### What the AI Proposed:
The AI initially recommended importing TailwindCSS with default modern SaaS components (purple/indigo gradients, standard rounded card grids, generic font stacks).

### What Was Accepted / Rejected and Why:
- **Rejected:** The design specification explicitly required:
  - *"Palette: deep obsidian black, crisp pearly white, subtle jungle dark green accents (define 4–6 named hex tokens; no bright primaries, no neon, no default warm-cream/terracotta or SaaS-card clichés)."*
  - *"Immaculate visual hierarchy — should read as designed by a human studio, not a template."*
  - Generic Tailwind templates create sterile, interchangeable web apps that fail the "human studio" requirement.
- **Accepted Decision:**
  - Built a bespoke CSS design system (`frontend/src/index.css`) with strict semantic tokens:
    - `--bg-obsidian: #090a0f`
    - `--bg-surface: #12151d`
    - `--bg-elevated: #1a1e29`
    - `--border-subtle: #242938`
    - `--border-focus: #10b981`
    - `--text-pearly: #f4f5f7`
    - `--text-muted: #8b949e`
    - `--accent-jungle: #10b981`
    - `--accent-jungle-glow: rgba(16, 185, 129, 0.15)`
  - Engineered a high-performance interactive canvas background that renders an obsidian starlight mesh with subtle cursor proximity lighting, running at 60fps on `requestAnimationFrame` with zero CPU overhead and strict `prefers-reduced-motion` compliance.
  - **Outcome:** A distinct, immersive, studio-crafted developer experience.

---

## Decision 4: Iterative Learning Feedback — Single Score vs Multidimensional Rubric & Refactoring Diff

### What the AI Proposed:
The AI suggested returning a single aggregate percentage score (e.g., "76/100") with a bulleted list of tips.

### What Was Accepted / Rejected and Why:
- **Rejected:** In Low-Level Design interviews, candidates need actionable guidance, not a single opaque number. Knowing you scored "70%" doesn't explain *why* your design was brittle.
- **Accepted Decision:**
  - Designed a multidimensional evaluation model comprising:
    1. **Structural Checks:** Category, Rule ID, Severity, Pass/Fail status, and file/class line references.
    2. **SOLID Matrix:** Quantitative ratings across Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.
    3. **Trade-off Commentary:** Contrasting chosen patterns against alternatives (e.g. State Pattern vs switch-cases).
    4. **Concrete Refactoring Snippets:** Exact before-and-after code transformations illustrating how to decouple classes.
    5. **Historical Attempt Tracking:** Allows learners to see their score evolve across attempts (`Attempt 1: 52` $\to$ `Attempt 2: 84`).
  - **Outcome:** Direct pedagogical value that turns mistakes into immediate learning breakthroughs.
