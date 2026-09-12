"""Typed repository implementations for storing and retrieving LLD entities."""

import json
from datetime import datetime, timezone
import sqlite3
from typing import Any, Dict, List, Optional
from app.data.seed_problems import SEED_PROBLEMS
from app.domain.models import (
    Attempt,
    AttemptStatus,
    CheckCategory,
    CheckResult,
    CheckSeverity,
    Difficulty,
    EvaluationResult,
    LLMFeedbackReport,
    Problem,
    Submission,
    SubmissionStatus,
)
from app.repositories.database import get_db_connection


class ProblemRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def seed_defaults(self) -> None:
        """Seeds initial curated problems if not already present."""
        conn = get_db_connection(self.db_path)
        for prob in SEED_PROBLEMS:
            data = {
                "functional_requirements": prob.functional_requirements,
                "non_functional_requirements": prob.non_functional_requirements,
                "constraints": prob.constraints,
                "sample_entities": prob.sample_entities,
                "starter_code": prob.starter_code,
                "default_notes_template": prob.default_notes_template,
                "starter_diagram_dsl": prob.starter_diagram_dsl,
                "rubric_weights": prob.rubric_weights,
            }
            conn.execute(
                """
                INSERT OR REPLACE INTO problems (id, slug, title, difficulty, domain, summary, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (prob.id, prob.slug, prob.title, prob.difficulty.value, prob.domain, prob.summary, json.dumps(data)),
            )
        conn.commit()
        conn.close()

    def get_all(self) -> List[Problem]:
        conn = get_db_connection(self.db_path)
        rows = conn.execute("SELECT * FROM problems ORDER BY title").fetchall()
        problems = [self._row_to_problem(r) for r in rows]
        conn.close()
        return problems

    def get_by_id(self, problem_id: str) -> Optional[Problem]:
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM problems WHERE id = ?", (problem_id,)).fetchone()
        conn.close()
        return self._row_to_problem(row) if row else None

    def get_by_slug(self, slug: str) -> Optional[Problem]:
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM problems WHERE slug = ?", (slug,)).fetchone()
        conn.close()
        return self._row_to_problem(row) if row else None

    def _row_to_problem(self, row: sqlite3.Row) -> Problem:
        data = json.loads(row["data_json"])
        return Problem(
            id=row["id"],
            slug=row["slug"],
            title=row["title"],
            difficulty=Difficulty(row["difficulty"]),
            domain=row["domain"],
            summary=row["summary"],
            functional_requirements=data["functional_requirements"],
            non_functional_requirements=data["non_functional_requirements"],
            constraints=data["constraints"],
            sample_entities=data["sample_entities"],
            starter_code=data["starter_code"],
            default_notes_template=data["default_notes_template"],
            starter_diagram_dsl=data["starter_diagram_dsl"],
            rubric_weights=data.get("rubric_weights", {}),
        )


class AttemptRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def save(self, attempt: Attempt) -> Attempt:
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO attempts (id, problem_id, user_id, code, design_notes, diagram_dsl, status, draft_version, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt.id,
                attempt.problem_id,
                attempt.user_id,
                attempt.code,
                attempt.design_notes,
                attempt.diagram_dsl,
                attempt.status.value,
                attempt.draft_version,
                attempt.created_at.isoformat(),
                attempt.updated_at.isoformat(),
            ),
        )
        conn.commit()
        conn.close()
        return attempt

    def get_by_id(self, attempt_id: str) -> Optional[Attempt]:
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,)).fetchone()
        conn.close()
        return self._row_to_attempt(row) if row else None

    def get_latest_by_problem_and_user(self, problem_id: str, user_id: str) -> Optional[Attempt]:
        conn = get_db_connection(self.db_path)
        row = conn.execute(
            "SELECT * FROM attempts WHERE problem_id = ? AND user_id = ? ORDER BY updated_at DESC LIMIT 1",
            (problem_id, user_id),
        ).fetchone()
        conn.close()
        return self._row_to_attempt(row) if row else None

    def list_all(self, user_id: Optional[str] = None) -> List[Attempt]:
        conn = get_db_connection(self.db_path)
        if user_id:
            rows = conn.execute("SELECT * FROM attempts WHERE user_id = ? ORDER BY updated_at DESC", (user_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM attempts ORDER BY updated_at DESC").fetchall()
        attempts = [self._row_to_attempt(r) for r in rows]
        conn.close()
        return attempts

    def _row_to_attempt(self, row: sqlite3.Row) -> Attempt:
        return Attempt(
            id=row["id"],
            problem_id=row["problem_id"],
            user_id=row["user_id"],
            code=row["code"],
            design_notes=row["design_notes"],
            diagram_dsl=row["diagram_dsl"],
            status=AttemptStatus(row["status"]),
            draft_version=row["draft_version"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class SubmissionRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def save(self, sub: Submission) -> Submission:
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO submissions (id, attempt_id, problem_id, user_id, submitted_code, submitted_notes, submitted_diagram_dsl, status, retry_count, error_message, content_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sub.id,
                sub.attempt_id,
                sub.problem_id,
                sub.user_id,
                sub.submitted_code,
                sub.submitted_notes,
                sub.submitted_diagram_dsl,
                sub.status.value,
                sub.retry_count,
                sub.error_message,
                sub.content_hash,
                sub.created_at.isoformat(),
                sub.updated_at.isoformat(),
            ),
        )
        conn.commit()
        conn.close()
        return sub

    def get_by_id(self, submission_id: str) -> Optional[Submission]:
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
        conn.close()
        return self._row_to_submission(row) if row else None

    def get_by_content_hash(self, content_hash: str) -> Optional[Submission]:
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM submissions WHERE content_hash = ? ORDER BY created_at DESC LIMIT 1", (content_hash,)).fetchone()
        conn.close()
        return self._row_to_submission(row) if row else None

    def list_by_attempt(self, attempt_id: str) -> List[Submission]:
        conn = get_db_connection(self.db_path)
        rows = conn.execute("SELECT * FROM submissions WHERE attempt_id = ? ORDER BY created_at DESC", (attempt_id,)).fetchall()
        subs = [self._row_to_submission(r) for r in rows]
        conn.close()
        return subs

    def list_by_problem(self, problem_id: str, user_id: Optional[str] = None) -> List[Submission]:
        conn = get_db_connection(self.db_path)
        if user_id:
            rows = conn.execute(
                "SELECT * FROM submissions WHERE problem_id = ? AND user_id = ? ORDER BY created_at DESC",
                (problem_id, user_id),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM submissions WHERE problem_id = ? ORDER BY created_at DESC",
                (problem_id,),
            ).fetchall()
        subs = [self._row_to_submission(r) for r in rows]
        conn.close()
        return subs

    def list_recent(self, limit: int = 15) -> List[Submission]:
        conn = get_db_connection(self.db_path)
        rows = conn.execute("SELECT * FROM submissions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        subs = [self._row_to_submission(r) for r in rows]
        conn.close()
        return subs

    def _row_to_submission(self, row: sqlite3.Row) -> Submission:
        return Submission(
            id=row["id"],
            attempt_id=row["attempt_id"],
            problem_id=row["problem_id"],
            user_id=row["user_id"],
            submitted_code=row["submitted_code"],
            submitted_notes=row["submitted_notes"],
            submitted_diagram_dsl=row["submitted_diagram_dsl"],
            status=SubmissionStatus(row["status"]),
            retry_count=row["retry_count"],
            error_message=row["error_message"],
            content_hash=row["content_hash"] if "content_hash" in row.keys() and row["content_hash"] else "",
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class EvaluationRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def save(self, eval_res: EvaluationResult) -> EvaluationResult:
        conn = get_db_connection(self.db_path)

        checks_data = [
            {
                "rule_id": c.rule_id,
                "rule_name": c.rule_name,
                "category": c.category.value,
                "passed": c.passed,
                "score": c.score,
                "max_score": c.max_score,
                "severity": c.severity.value,
                "message": c.message,
                "suggestion": c.suggestion,
                "code_reference": c.code_reference,
            }
            for c in eval_res.checks
        ]

        dims_data = [
            {
                "criterion": d.criterion,
                "score": d.score,
                "max_score": d.max_score,
                "evidence": d.evidence,
                "concern": d.concern,
                "suggestion": d.suggestion,
                "confidence": d.confidence,
            }
            for d in eval_res.dimensions
        ]

        llm_data = None
        if eval_res.llm_feedback:
            llm_data = {
                "summary": eval_res.llm_feedback.summary,
                "trade_off_analysis": eval_res.llm_feedback.trade_off_analysis,
                "extensibility_critique": eval_res.llm_feedback.extensibility_critique,
                "edge_cases_analysis": eval_res.llm_feedback.edge_cases_analysis,
                "alternative_approaches": eval_res.llm_feedback.alternative_approaches,
                "suggested_refactor_diff": eval_res.llm_feedback.suggested_refactor_diff,
            }

        conn.execute(
            """
            INSERT OR REPLACE INTO evaluations (id, submission_id, overall_score, deterministic_score, ai_score, grade, checks_json, dimensions_json, llm_feedback_json, execution_time_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eval_res.id,
                eval_res.submission_id,
                eval_res.overall_score,
                eval_res.deterministic_score,
                eval_res.ai_score,
                eval_res.grade,
                json.dumps(checks_data),
                json.dumps(dims_data),
                json.dumps(llm_data or {}),
                eval_res.execution_time_ms,
                eval_res.created_at.isoformat(),
            ),
        )
        conn.commit()
        conn.close()
        return eval_res

    def get_by_submission_id(self, submission_id: str) -> Optional[EvaluationResult]:
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM evaluations WHERE submission_id = ?", (submission_id,)).fetchone()
        conn.close()
        return self._row_to_evaluation(row) if row else None

    def _row_to_evaluation(self, row: sqlite3.Row) -> EvaluationResult:
        from app.domain.models import RubricDimensionResult

        checks_raw = json.loads(row["checks_json"])
        checks = [
            CheckResult(
                rule_id=c["rule_id"],
                rule_name=c["rule_name"],
                category=CheckCategory(c["category"]),
                passed=c["passed"],
                score=c["score"],
                max_score=c["max_score"],
                severity=CheckSeverity(c["severity"]),
                message=c["message"],
                suggestion=c["suggestion"],
                code_reference=c.get("code_reference"),
            )
            for c in checks_raw
        ]

        dims_raw = json.loads(row["dimensions_json"]) if "dimensions_json" in row.keys() and row["dimensions_json"] else []
        dimensions = [
            RubricDimensionResult(
                criterion=d["criterion"],
                score=d["score"],
                max_score=d["max_score"],
                evidence=d["evidence"],
                concern=d["concern"],
                suggestion=d["suggestion"],
                confidence=d.get("confidence", 0.9),
            )
            for d in dims_raw
        ]

        llm_raw = json.loads(row["llm_feedback_json"])
        llm_feedback = None
        if llm_raw and "summary" in llm_raw:
            llm_feedback = LLMFeedbackReport(
                summary=llm_raw["summary"],
                dimensions=dimensions,
                trade_off_analysis=llm_raw.get("trade_off_analysis", ""),
                extensibility_critique=llm_raw.get("extensibility_critique", ""),
                edge_cases_analysis=llm_raw.get("edge_cases_analysis", ""),
                alternative_approaches=llm_raw.get("alternative_approaches", []),
                suggested_refactor_diff=llm_raw.get("suggested_refactor_diff", ""),
            )

        ai_score = row["ai_score"] if "ai_score" in row.keys() else row["llm_score"]

        return EvaluationResult(
            id=row["id"],
            submission_id=row["submission_id"],
            overall_score=row["overall_score"],
            deterministic_score=row["deterministic_score"],
            ai_score=ai_score,
            grade=row["grade"],
            checks=checks,
            dimensions=dimensions,
            llm_feedback=llm_feedback,
            execution_time_ms=row["execution_time_ms"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

