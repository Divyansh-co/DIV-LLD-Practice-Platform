"""Vercel Serverless Function entrypoint for FastAPI backend."""

import os
import sys

# Ensure backend root is on Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.repositories.database import init_db
from app.repositories.storage import ProblemRepository

# Ensure tables and seed problems are initialized in serverless environment
try:
    init_db()
    repo = ProblemRepository()
    repo.seed_defaults()
except Exception as e:
    print(f"[Vercel Init] Database init error: {e}")
