# Research Note: Low-Level Design (LLD) Practice & Assessment Platform

## 1. Deep Dive into the Learner Problem

### 1.1 How a Learner Currently Practices an LLD Problem
In modern software engineering (particularly for Mid, Senior, and Staff roles at tier-1 tech firms), Low-Level Design (LLD) / Object-Oriented Design (OOD) is a critical interview gate. The interview tests whether an engineer can take ambiguous business requirements and model them into extensible, loosely coupled, and maintainable classes.

Today, a learner typically practices like this:
1. **Passive Reading / Watching:** Reads a blog post (e.g. *"How to design a Parking Lot in Java"*), watches a 45-minute YouTube video, or reads a Grokking chapter on Educative.
2. **Unguided Coding:** Opens a blank scratchpad, IDE file, or whiteboard and writes 5–10 classes.
3. **The Feedback Void:** Upon finishing, the learner stares at their code. There are no compiler test cases to run because there is no fixed input/output specification. The learner asks:
   - *Is my spot allocation properly decoupled from the lot controller?*
   - *Did I create a God class?*
   - *Did I violate the Open/Closed Principle by hardcoding pricing?*
   - *What happens when two cars arrive concurrently at different gates?*
4. **Abandonment or Superficial Comparison:** The learner compares their code to the author's reference solution. If the reference solution used a different pattern (e.g. Factory vs Strategy), the learner cannot tell if their own approach was an equally valid design choice or an anti-pattern. They move to the next problem without learning from their design flaws.

### 1.2 How Learners Currently Judge Whether a Solution is Good
Without automated tooling, learners rely on flawed heuristics:
- *"Does it compile and look like the reference article?"* (Creates brittle memorization).
- *"Did I include lots of design patterns?"* (Encourages gratuitous over-engineering).
- *"ChatGPT says it looks great."* (LLM sycophancy: generic conversational LLMs praise broken designs unless anchored to rigid structural rubrics).

### 1.3 What Happens When Two Valid Designs Look Very Different
Unlike LeetCode (where algorithmic time/space complexity and binary I/O test cases govern correctness), Low-Level Design has **no single unique topology**:
- In an **Elevator System**, one engineer may design a centralized `ElevatorController` with a LOOK algorithm, while another creates decentralized autonomous elevator cars communicating via an event bus. Both are valid depending on building scale.
- In a **Parking Lot**, one engineer may manage spots through a centralized multi-floor controller with mutex locks, while another partitions spots into floor-level allocation queues.
- **The Core Insight:** A platform that marks a design "wrong" simply because it doesn't match a hardcoded reference solution is useless. Good assessment must evaluate **design invariants and trade-offs**:
  - Did the candidate satisfy functional requirements?
  - Are responsibilities cohesive (Single Responsibility)?
  - Are extensions decoupled from modifications (Open/Closed)?
  - Are concurrency guards in place to prevent race conditions?

### 1.4 What Feedback Actually Helps Learners Improve
Feedback is actionable only when it provides:
1. **Objective structural verification:** Immediate verification that core abstractions, base classes, and thread locks exist.
2. **Evidence-based trade-off critique:** Quoting the learner's own classes and explaining *why* an alternative pattern provides better extensibility (e.g. *"You used nested if/else for states; adding a new state requires modifying 4 methods. Applying GoF State Pattern encapsulates these transitions."*).
3. **Concrete before/after refactoring diffs:** Showing the exact code transformation needed.

### 1.5 What Evidence Must the Platform Retain from an Attempt
To support iterative mastery, the platform must persist:
- **The exact submitted code & design rationale:** To inspect historical snapshots.
- **Content Hash:** To guard against duplicate evaluation runs (idempotency).
- **Execution State & Timestamps:** Tracking submission progression.
- **Granular Rubric Scores:** Showing score deltas (+15% improvement across iterations).

---

## 2. Research on Existing Practice Tools & Approaches

| Tool / Platform | Practice Workflow | Submission Format | Feedback Mechanism | Spotting Recurring Weaknesses | Critical Gaps Identified |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LeetCode / HackerRank** | Pick problem $\to$ code function $\to$ submit $\to$ automated unit test suite. | Code only (single function/class). | Binary Pass/Fail, runtime percentile, memory usage. | Tracks overall acceptance rate per tag (Binary Search, DP). | **Completely algorithmic.** Incapable of evaluating class hierarchies, design patterns, encapsulation, or architectural trade-offs. |
| **Educative (Grokking LLD)** | Read chapter $\to$ review UML $\to$ inspect sample Java code. | No submission (passive reading). | None. Static reference solution only. | None. No learner state or progress tracked. | **Zero interactive practice.** No automated critique; learners passively consume author solutions without active retention. |
| **Pramp / Interviewing.io** | Schedule 60-minute peer/mentor mock session $\to$ live coding on shared pad. | Plain text & live code in collaborative editor. | Peer/interviewer verbal critique and rubric score. | Qualitative text feedback in interview history. | **High friction and cost.** Requires scheduling human sessions ($150–$250/hr); peer feedback is noisy and highly uncalibrated. |
| **GitHub LLD Repositories** (e.g., `donnemartin/system-design-primer`, `tsun/functional-design`) | Browse markdown files $\to$ copy code snippets. | None (static repository). | None. | None. | Static code dumps with no assessment or automated feedback. |
| **Standalone LLM Chatbots** (ChatGPT, Claude) | Paste problem prompt $\to$ paste candidate code $\to$ ask *"Is this good?"* | Raw unstructured text/code paste. | Unconstrained conversational prose. | None (ephemeral chat context). | **Hallucinatory & uncalibrated.** Sycophantic praise; fails to check objective structural invariants; no persistent attempt history. |

---

## 3. Key Identified Gaps & Product Principles

### Gap 1: Conflation of Deterministic Rules and Subjective Reasoning
Existing tools either force brittle unit tests (which fail valid alternate designs) or rely entirely on unconstrained LLM chat (which hallucinates and varies unpredictably).
- **Product Direction:** Build a **Dual-Engine Evaluation Architecture**:
  - Deterministic AST static analysis for structural invariants (classes, inheritance, method contracts, God-class thresholds, concurrency locks).
  - Anchored AI rubric evaluation (8 explicit dimensions with structured output) for trade-offs and extensibility.

### Gap 2: Disposable, One-Time Submissions
Existing tools treat submissions as one-off checks. Learners cannot track their iterative improvement.
- **Product Direction:** An **Iterative Attempt Timeline** showing versioned progression: Attempt #1 $\to$ Review explainable feedback $\to$ Attempt #2 $\to$ Verify score delta (+15% improvement).

### Gap 3: Vague Feedback
Telling a candidate "Grade: 70%" provides zero guidance on what to refactor.
- **Product Direction:** Ground all feedback in candidate evidence, structured as `criterion → score → evidence → concern → suggestion → confidence`, paired with concrete before/after code diffs.
