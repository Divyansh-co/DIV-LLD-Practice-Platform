"""FastAPI application entrypoint for the LLD Practice Platform."""

from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables from local and root directories
load_dotenv()
_base_dir = os.path.dirname(os.path.abspath(__file__))
for _env_path in [
    os.path.abspath(os.path.join(_base_dir, "..", "..", "..", ".env")),
    os.path.abspath(os.path.join(_base_dir, "..", "..", ".env")),
    os.path.abspath(os.path.join(_base_dir, "..", ".env")),
]:
    if os.path.exists(_env_path):
        load_dotenv(_env_path)

from app.api.routes import router
from app.repositories.database import init_db
from app.repositories.storage import ProblemRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & seed problems
    init_db()
    repo = ProblemRepository()
    repo.seed_defaults()
    yield


app = FastAPI(
    title="LLD Practice Platform API",
    description="Low-level design practice and evaluation API.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local dev and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router (/api/v1/...)
app.include_router(router)

# Mount static frontend if bundled
current_dir = os.path.dirname(os.path.abspath(__file__))
static_candidates = [
    os.path.join(current_dir, "static"),
    os.path.abspath(os.path.join(current_dir, "..", "..", "frontend", "dist")),
    os.path.abspath(os.path.join(current_dir, "..", "..", "dist")),
]

static_dir = None
for cand in static_candidates:
    if os.path.exists(cand) and os.path.exists(os.path.join(cand, "index.html")):
        static_dir = cand
        break

if static_dir:
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.api_route("/index.html", methods=["GET", "HEAD"])
    @app.api_route("/", methods=["GET", "HEAD"])
    def serve_frontend():
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    def catch_all(full_path: str):
        if full_path.startswith("api/") or full_path in ("docs", "openapi.json"):
            raise HTTPException(status_code=404, detail="Not Found")
        target = os.path.join(static_dir, full_path)
        if os.path.exists(target) and not os.path.isdir(target):
            return FileResponse(target)
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "service": "LLD Practice Platform API",
            "version": "1.0.0",
            "docs_url": "/docs",
            "health_url": "/api/v1/health",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

