"""Pytest fixtures and configuration."""

import os
import sys
import tempfile
import pytest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.repositories.database import init_db
from app.repositories.storage import ProblemRepository


@pytest.fixture(autouse=True)
def test_db():
    """Sets up a temporary SQLite database for each test run."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_path = tf.name

    os.environ["LLD_DATABASE_URL"] = temp_path
    os.environ["ALLOW_HEURISTIC_FALLBACK"] = "1"
    init_db(temp_path)
    repo = ProblemRepository(temp_path)
    repo.seed_defaults()

    yield temp_path

    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except OSError:
            pass
