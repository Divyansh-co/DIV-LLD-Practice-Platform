# LLD Practice & Assessment Platform

A tool for practicing Low-Level Design problems (Parking Lot, Elevator, Vending Machine), submitting code and notes, and getting structured feedback on design trade-offs.

## The Problem This Solves

Low-level design practice is easy to start and hard to self-evaluate. You can write code for a parking lot or elevator system and still not know if your class boundaries, responsibilities, or extensibility choices make sense.

This tool runs a practice loop (`attempt → submit → review feedback → retry`) and tracks past attempts so you can see how your design changes across iterations.

## How It Works

1. **Pick a problem** — Choose from three problems (Multi-Floor Parking Lot, Elevator Dispatcher, Vending Machine).
2. **Work on a solution** — Write Python classes, design notes, and optional Mermaid class diagrams in the editor.
3. **Submit** — Your solution is saved immediately and moves through `PENDING → EVALUATING → COMPLETED / FAILED`.
4. **Get feedback** — Feedback is split into two parts:
   - **Structural checks:** AST checks verifying class hierarchies, abstract methods, and basic patterns.
   - **Design rubric:** Qualitative feedback across 8 criteria (scores, code evidence, concerns, and suggestions).
5. **Review & retry** — Review your results and click "Try Again" to iterate on your previous draft.

## Tech Stack & Docs

- **Backend:** Python (FastAPI, SQLite)
- **Frontend:** React (Vite)
- **Design & Research Notes:** See [RESEARCH_NOTE.md](file:///c:/Users/divya/Downloads/ai-pdf-chatbot-langchain-main%20%281%29/assesment%201%20internship/RESEARCH_NOTE.md), [DESIGN_NOTE.md](file:///c:/Users/divya/Downloads/ai-pdf-chatbot-langchain-main%20%281%29/assesment%201%20internship/DESIGN_NOTE.md), and [AI_USAGE.md](file:///c:/Users/divya/Downloads/ai-pdf-chatbot-langchain-main%20%281%29/assesment%201%20internship/AI_USAGE.md) in the project root.

- Design decisions worth calling out
Why a monolith: the assignment scope doesn't need microservices or distributed infra — a single backend service keeps the domain model easy to reason about, which is where the actual grading weight is.
Why split evaluation into deterministic + LLM: treating every check as an LLM call would make feedback inconsistent and slow. Structural checks are cheap and reliable on their own; the LLM is reserved for the parts that genuinely need judgment (trade-offs, abstraction quality).
Why an explicit submission state machine: evaluation (especially the LLM part) can be slow or fail. Persisting the submission before evaluation starts, and giving it a clear status, means a failed evaluation doesn't lose the learner's work and the UI always has something honest to show.
Known limitations.
Only a handful of problems are seeded — not meant to be a full curriculum yet.
No retry/backoff strategy beyond basic failure handling; a production version would need one.
Evaluation rubric is fixed per problem type — no support yet for a human-reviewer evaluator, though the Evaluator interface is written so one could be added without touching the practice flow.

