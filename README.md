# LLD Practice & Assessment Platform

A platform for practicing Low-Level Design problems (Parking Lot, Elevator, Vending Machine), submitting your solution, and getting feedback on your design trade-offs.

## The Problem This Solves

Low-level design practice is easy to start and hard to self-evaluate. You can design a parking lot system and still have no idea if your class boundaries, responsibilities, or extensibility choices are sound. 

This platform gives developers a repeatable loop (`attempt → submit → review feedback → retry`) and tracks attempt history so you can see your improvement over time.

## How It Works

1. **Pick a problem** — Choose from curated problems (Multi-Floor Parking Lot, Elevator Dispatcher, Vending Machine), each with functional requirements and constraints.
2. **Work on a solution** — Write your Python class definitions and design notes in the workspace.
3. **Submit** — Your solution is saved immediately and moves through a status sequence (`PENDING → EVALUATING → COMPLETED / FAILED`).
4. **Get feedback** — Feedback is split into two parts:
   - **Structural checks:** Static checks for class hierarchies, method signatures, and basic design patterns.
   - **Design rubric:** Qualitative feedback on design trade-offs, SOLID adherence, and suggested improvements evaluated against structured criteria.
5. **Review & retry** — Past attempts are recorded so you can compare scores and refine your design.

## Tech Stack

- **Backend:** Python (FastAPI, SQLite)
- **Frontend:** React (Vite)
- **Docs:** Design notes and architectural records in `/docs`

