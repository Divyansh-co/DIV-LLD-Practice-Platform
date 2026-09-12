# AI Usage Log

This document notes four specific instances where I used AI tools while working on this project, what was suggested, and what I kept or threw out.

---

## 1. Structuring the LLM Evaluation Rubric Prompt

### What the AI suggested
When I asked the AI to help design a prompt for grading LLD submissions, it generated a large JSON prompt asking the model to return 15 separate architectural sub-metrics, multi-paragraph critiques, five alternative design pattern proposals, and a complete rewritten Python codebase inside an escaped JSON string field.

### What was kept vs. rejected, and why
- **Rejected:** I threw out the request for a fully rewritten codebase and the 15 granular metrics. In initial tests with Groq, asking for that much output regularly caused the request to take 30 to 45 seconds, blowing past HTTP client timeouts. Worse, escaping a 200-line Python implementation inside a JSON string often produced malformed JSON that failed `json.loads()`.
- **Kept:** I kept the idea of a structured dimensions array, but simplified it down to 8 distinct criteria that match standard LLD interview dimensions: structural decomposition, pattern selection, extensibility, separation of concerns, SOLID compliance, interface design, failure handling, and trade-off awareness. Each criterion returns score, evidence, concern, suggestion, and confidence. This reliably generates in 3 to 5 seconds and parses cleanly every time.

---

## 2. Choosing and Configuring the Groq LLM Model

### What the AI suggested
The AI suggested using the model string `llama-3.3-70b-versatile` and importing the official `groq` Python SDK with standard client initialization.

### What was kept vs. rejected, and why
- **Rejected:** When tested against the configured Groq API key, `llama-3.3-70b-versatile` immediately threw a 404 `model_not_found` error. The AI also did not account for `.env` loading, which left the API key empty at runtime and caused the evaluator to silently fall back to hardcoded strings. I also rejected adding the official `groq` SDK package because the backend already had `httpx` installed, and making direct HTTP requests to Groq's OpenAI-compatible endpoint avoided adding another dependency.
- **Kept:** I queried the Groq models API, found `qwen/qwen3.8-27b`, and tested it with structured JSON mode (`response_format: {"type": "json_object"}`). It responded consistently and adhered to the schema. I also added a 3-attempt exponential backoff loop around the HTTP call to handle Groq's HTTP 429 rate limit responses gracefully.

---

## 3. Designing Async Submission Retries and State Handling

### What the AI suggested
When designing the async failure and retry flow, the AI suggested installing Celery and Redis as a message broker, and having the "Retry" button create a brand new submission record in the SQLite database every time the user clicked it.

### What was kept vs. rejected, and why
- **Rejected:** I rejected Celery and Redis. This is a single-node assessment app running on SQLite and FastAPI. Adding Redis, a Celery worker daemon, and a broker is unnecessary complexity when FastAPI's built-in `BackgroundTasks` works fine for evaluating submissions asynchronously. I also rejected creating new database records on retry. If a submission failed due to a 20-second API timeout and the user clicked retry three times, their attempt history would be cluttered with three failed duplicate records.
- **Kept:** I kept the status transition pattern (`PENDING` / `SUBMITTED` → `EVALUATING` → `COMPLETED` / `FAILED`), but made the retry action reuse the existing submission ID. When retrying, `prepare_retry()` resets the submission status to `SUBMITTED`, increments `retry_count`, clears the previous `error_message`, and re-enqueues the same background task. This keeps the database clean and makes retrying idempotent.

---

## 4. Class Diagram Rendering in the Practice Workspace

### What the AI suggested
The AI suggested either installing an interactive flowchart library (like React Flow) with drag-and-drop node editing, or rendering Mermaid diagrams on the backend using a headless Chrome CLI (like `mermaid-cli` via Puppeteer) and sending PNG images back to the frontend.

### What was kept vs. rejected, and why
- **Rejected:** I rejected backend headless Chrome rendering because requiring a Node/Puppeteer process or Chromium binary just to convert text to an image is slow, heavy, and fragile. I also rejected React Flow because building an interactive visual UML drag-and-drop editor shifts the platform into a diagramming tool rather than a coding assessment environment.
- **Kept:** I kept the implementation entirely client-side using the `mermaid` JavaScript library. In `PracticeView.jsx`, the diagram is rendered directly into an SVG inside a simple container component with a dark theme. I added a small toggle button (`[Diagram | Edit Syntax]`) so learners can view the diagram rendered by default or click into the text area to edit Mermaid syntax directly.
