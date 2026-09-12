"""FastAPI application entrypoint for the LLD Practice Platform."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    description="Low-Level Design practice, submission, and automated assessment platform.",
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

app.include_router(router)


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
