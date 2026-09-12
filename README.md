LLD Practice & Assessment Platform

A small platform for practicing Low-Level Design problems (Parking Lot, Elevator, Vending Machine, etc.), submitting a solution, and getting feedback that's actually useful — not just a score.

Built as a 2-day take-home assignment focused on domain design over infrastructure.

The problem this solves

LLD practice is easy to start and hard to self-evaluate. You can design a Parking Lot system and still have no idea if your class boundaries, responsibilities, or extensibility choices are actually good — especially since more than one design can be "correct." This platform gives learners a repeatable loop (attempt → submit → get feedback → try again) and keeps a history so they can see whether they're actually improving.

How it works
Pick a problem — a small curated set (Multi-Floor Parking Lot, Elevator Dispatcher, Vending Machine), each with clear requirements and constraints.
Work on a solution — write it up in the practice studio (code + design notes).
Submit — the submission is saved immediately and moves through a simple status pipeline: PENDING → EVALUATING → COMPLETED / FAILED. It's saved before evaluation starts so nothing is lost if evaluation fails.
Get feedback — feedback is split into two kinds:
Deterministic checks — structural things that don't need judgment (required classes present, interface usage, basic rule checks).
LLM-based feedback — reasoning about design trade-offs, SOLID adherence, coupling/cohesion, and suggestions for improvement, generated against a fixed rubric so it stays consistent instead of just asking "is this good?"
Review & retry — past attempts are kept per problem so you can see what changed and whether your score actually moved.
Tech stack
Backend: Python
Frontend: JavaScript (React)
Docs: design notes / diagrams under /docs

LLD Practice & Assessment Platform

A small platform for practicing Low-Level Design problems (Parking Lot, Elevator, Vending Machine, etc.), submitting a solution, and getting feedback that's actually useful — not just a score.

Built as a 2-day take-home assignment focused on domain design over infrastructure.

The problem this solves

LLD practice is easy to start and hard to self-evaluate. You can design a Parking Lot system and still have no idea if your class boundaries, responsibilities, or extensibility choices are actually good — especially since more than one design can be "correct." This platform gives learners a repeatable loop (attempt → submit → get feedback → try again) and keeps a history so they can see whether they're actually improving.

How it works
Pick a problem — a small curated set (Multi-Floor Parking Lot, Elevator Dispatcher, Vending Machine), each with clear requirements and constraints.
Work on a solution — write it up in the practice studio (code + design notes).
Submit — the submission is saved immediately and moves through a simple status pipeline: PENDING → EVALUATING → COMPLETED / FAILED. It's saved before evaluation starts so nothing is lost if evaluation fails.
Get feedback — feedback is split into two kinds:
Deterministic checks — structural things that don't need judgment (required classes present, interface usage, basic rule checks).
LLM-based feedback — reasoning about design trade-offs, SOLID adherence, coupling/cohesion, and suggestions for improvement, generated against a fixed rubric so it stays consistent instead of just asking "is this good?"
Review & retry — past attempts are kept per problem so you can see what changed and whether your score actually moved.
Tech stack
Backend: Python
Frontend: JavaScript (React)
Docs: design notes / diagrams under /docs
