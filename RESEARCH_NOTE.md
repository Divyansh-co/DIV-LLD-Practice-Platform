# Research Note: Low-Level Design Practice & Self-Evaluation

## The Learner Problem

Practicing low-level design (LLD) is easy to start, but hard to self-evaluate.

When preparing for coding interviews or trying to write cleaner object-oriented code, developers usually pick a classic prompt like "Design a Parking Lot" or "Design an Elevator System." Writing 200 lines of Python or Java for these problems is straightforward. The code will parse, run, and maybe even simulate a couple of cars parking or an elevator moving between floors.

The problem starts the moment the code runs:
- Is the class breakdown actually sensible, or is there a single "God class" doing everything?
- Are responsibilities split properly, or did the developer put spot allocation logic directly inside the entry gate?
- Does the design respect the Open/Closed Principle, or will adding a new vehicle type require modifying three separate `if/elif` blocks?
- Did the developer choose appropriate design patterns (like Strategy for pricing or State for elevator movement), or did they force a pattern where a simple function would do?

In Data Structures and Algorithms (DSA), you get immediate binary feedback: your code either passes the test cases within time limits or it fails. In Low-Level Design, there is no single "correct" answer, and unit tests only verify whether your code works for one specific implementation. Without a senior engineer or an experienced interviewer looking over your shoulder, you have no reliable way to know if your design is sound.

---

## Existing Tools and Approaches

When looking at how developers currently practice LLD, three main options exist:

### 1. LeetCode / HackerRank style platforms
- **How they work:** You implement specific method signatures against hidden unit tests.
- **Why they fall short for LLD:** They treat design problems like standard algorithmic problems. To make automated testing work, they force you into a rigid starter template where all class names and method signatures are pre-determined. You end up implementing the internals of a predefined design rather than deciding how to structure classes, interfaces, and relationships yourself. They test functionality, not design quality.

### 2. Interview prep guides, GitHub repos, and YouTube videos
- **How they work:** Repositories and video channels (like Gaurav Sen or general LLD GitHub repositories) provide reference solutions to classic problems.
- **Why they fall short for LLD:** This is passive consumption, not active practice. You read someone else's "ideal" solution and try to memorize class hierarchies. But if you sit down and write your own version with a slightly different set of classes, these resources give you no feedback on whether your variation has merits or hidden flaws. Memorizing someone else's UML diagram does not teach you how to make design decisions under trade-offs.

### 3. General-purpose AI chatbots (ChatGPT, Claude)
- **How they work:** You paste your code into a chat prompt and ask for design feedback.
- **Why they fall short for LLD:** General chatbots are unanchored and inconsistent. One run might praise everything you wrote; another run might nitpick PEP 8 formatting while ignoring that your parking lot controller is not thread-safe. They do not grade against a consistent rubric, they do not verify static code invariants systematically, and they do not keep track of your attempts over time so you can see if you improved between draft 1 and draft 2.

---

## Product Direction and Scope

To keep the project focused on practice and feedback, I made three choices:

### 1. A small, curated problem set
Instead of an endless list of prompts, there are three classic problems:
- **Multi-Floor Parking Lot (Medium):** Focuses on resource allocation, class hierarchies, and concurrency.
- **Elevator Dispatcher & Control System (Hard):** Focuses on state machines, request scheduling, and pluggable algorithms.
- **Vending Machine (Easy):** Focuses on the State design pattern and transaction handling.

These three cover the design patterns and structural trade-offs most frequently asked in LLD interviews.

### 2. One primary submission format: Code + Design Notes
The submission format is standard Python code paired with written design notes, plus an optional Mermaid class diagram. 

I skipped building a visual drag-and-drop UML canvas. In interviews and everyday engineering work, you explain your design in code and written trade-offs, not by moving boxes on a canvas. Writing class definitions and notes matches what interviewers actually ask for.

### 3. A two-part evaluation approach
Evaluation is split into two distinct layers:
- **Deterministic checks (40 points):** Fast, local Python AST checks that verify objective structural requirements (presence of required entity classes, use of abstract methods, proper enum usage, and basic checks against oversized classes).
- **Design rubric (60 points):** Qualitative feedback evaluated across 8 consistent dimensions (structural decomposition, pattern selection, extensibility, separation of concerns, SOLID compliance, interface design, failure handling, and trade-off awareness). Each dimension returns a score, code evidence, identified concerns, and concrete suggestions.

This gives the learner clear, objective structural feedback right away, plus actionable qualitative feedback on their design trade-offs.
