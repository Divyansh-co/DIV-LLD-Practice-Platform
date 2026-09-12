"""Database initialization and schema definition using SQLite."""

import os
import sqlite3
from typing import Optional


def get_db_path() -> str:
    if os.getenv("VERCEL"):
        return os.getenv("LLD_DATABASE_URL", "/tmp/lld_platform.db")
    return os.getenv("LLD_DATABASE_URL", "lld_platform.db")


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection configured with WAL mode and dict rows."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except sqlite3.OperationalError:
        pass
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Auto-ensure tables exist
    _ensure_tables_exist(conn)
    return conn


def _ensure_tables_exist(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS problems (
        id TEXT PRIMARY KEY,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        domain TEXT NOT NULL,
        summary TEXT NOT NULL,
        data_json TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS attempts (
        id TEXT PRIMARY KEY,
        problem_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        code TEXT NOT NULL,
        design_notes TEXT NOT NULL,
        diagram_dsl TEXT NOT NULL,
        status TEXT NOT NULL,
        draft_version INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS submissions (
        id TEXT PRIMARY KEY,
        attempt_id TEXT NOT NULL,
        problem_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        submitted_code TEXT NOT NULL,
        submitted_notes TEXT NOT NULL,
        submitted_diagram_dsl TEXT NOT NULL,
        status TEXT NOT NULL,
        retry_count INTEGER NOT NULL DEFAULT 0,
        error_message TEXT,
        content_hash TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS evaluations (
        id TEXT PRIMARY KEY,
        submission_id TEXT UNIQUE NOT NULL,
        overall_score REAL NOT NULL,
        deterministic_score REAL NOT NULL,
        ai_score REAL NOT NULL,
        grade TEXT NOT NULL,
        checks_json TEXT NOT NULL,
        dimensions_json TEXT NOT NULL,
        llm_feedback_json TEXT NOT NULL,
        execution_time_ms INTEGER NOT NULL,
        created_at TEXT NOT NULL
    );

    """)
    conn.commit()

    # Migration: Ensure content_hash column exists on existing submissions tables
    try:
        cursor.execute("ALTER TABLE submissions ADD COLUMN content_hash TEXT;")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists



def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection(db_path)
    conn.close()

