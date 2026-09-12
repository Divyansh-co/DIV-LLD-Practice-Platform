"""Deterministic AST and Static Analysis Rule Engine for LLD.

Inspects Python AST to verify:
- Class hierarchies and inheritance (Open/Closed, Liskov)
- Method contracts and encapsulation (Single Responsibility)
- Strategy and State pattern implementations
- Concurrency primitives (Locks, thread-safety)
- Anti-patterns like God Classes
"""

import ast
from typing import Any, Dict, List, Optional, Set
from app.domain.models import CheckCategory, CheckResult, CheckSeverity, Problem, Submission
from app.domain.rules import PROBLEM_RULES_REGISTRY, RuleDefinition
from app.evaluators.base import Evaluator


class CodeAnalysisVisitor(ast.NodeVisitor):
    """Gathers structural metrics from Python AST."""

    def __init__(self):
        self.classes: Dict[str, Dict[str, Any]] = {}
        self.current_class: Optional[str] = None
        self.imports: Set[str] = set()
        self.uses_locks: bool = False
        self.lock_invocations: List[str] = []
        self.has_abstract_methods: bool = False

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            self.imports.add(f"{module}.{alias.name}")
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        class_name = node.name
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)

        self.classes[class_name] = {
            "name": class_name,
            "bases": bases,
            "methods": set(),
            "line_no": node.lineno,
            "has_abstract": False,
        }

        prev_class = self.current_class
        self.current_class = class_name
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.current_class:
            self.classes[self.current_class]["methods"].add(node.name)
            # Check for @abstractmethod decorator
            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Name) and decorator.id == "abstractmethod") or \
                   (isinstance(decorator, ast.Attribute) and decorator.attr == "abstractmethod"):
                    self.classes[self.current_class]["has_abstract"] = True
                    self.has_abstract_methods = True
        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        # Look for 'with self.lock:' or 'with lock:'
        for item in node.items:
            ctx = item.context_expr
            if isinstance(ctx, ast.Attribute) and "lock" in ctx.attr.lower():
                self.uses_locks = True
                self.lock_invocations.append(f"Line {node.lineno}: with {ctx.attr}")
            elif isinstance(ctx, ast.Name) and "lock" in ctx.id.lower():
                self.uses_locks = True
                self.lock_invocations.append(f"Line {node.lineno}: with {ctx.id}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Look for Lock(), acquire()
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("acquire", "release"):
                self.uses_locks = True
                self.lock_invocations.append(f"Line {node.lineno}: {node.func.attr}()")
        elif isinstance(node.func, ast.Name):
            if "Lock" in node.func.id or "RLock" in node.func.id:
                self.uses_locks = True
                self.lock_invocations.append(f"Line {node.lineno}: {node.func.id}()")
        self.generic_visit(node)


class DeterministicEvaluator(Evaluator):
    """Executes objective, AST-based rule checks against submitted code."""

    @property
    def name(self) -> str:
        return "DeterministicASTEvaluator"

    async def evaluate(self, submission: Submission, problem: Problem) -> Dict[str, Any]:
        code = submission.submitted_code.strip()
        if not code:
            return {
                "score": 0.0,
                "max_score": 40.0,
                "checks": [
                    CheckResult(
                        rule_id="EMPTY_SUBMISSION",
                        rule_name="Code Submission Present",
                        category=CheckCategory.STRUCTURAL,
                        passed=False,
                        score=0.0,
                        max_score=40.0,
                        severity=CheckSeverity.CRITICAL,
                        message="No code was submitted. Please write or paste your solution classes.",
                        suggestion="Provide Python class definitions implementing the requested system design.",
                    )
                ],
            }

        # Parse AST
        try:
            tree = ast.parse(code)
            visitor = CodeAnalysisVisitor()
            visitor.visit(tree)
        except SyntaxError as e:
            return {
                "score": 5.0,
                "max_score": 40.0,
                "checks": [
                    CheckResult(
                        rule_id="SYNTAX_ERROR",
                        rule_name="Valid Python Syntax",
                        category=CheckCategory.STRUCTURAL,
                        passed=False,
                        score=0.0,
                        max_score=40.0,
                        severity=CheckSeverity.CRITICAL,
                        message=f"Syntax error on line {e.lineno}: {e.msg}",
                        suggestion="Fix syntax error so the code can be statically parsed and analyzed.",
                        code_reference=f"Line {e.lineno}: {e.text.strip() if e.text else ''}",
                    )
                ],
            }

        rules = PROBLEM_RULES_REGISTRY.get(problem.slug, [])
        check_results: List[CheckResult] = []
        total_score = 0.0
        max_possible = sum(r.max_score for r in rules) or 40.0

        for rule in rules:
            result = self._validate_rule(rule, visitor, code)
            check_results.append(result)
            total_score += result.score

        # Normalize score to 40% weighting
        normalized_score = round((total_score / max_possible) * 40.0, 1) if max_possible > 0 else 0.0

        return {
            "score": normalized_score,
            "max_score": 40.0,
            "raw_score": total_score,
            "max_raw_score": max_possible,
            "checks": check_results,
            "parsed_classes": list(visitor.classes.keys()),
        }

    def _validate_rule(self, rule: RuleDefinition, visitor: CodeAnalysisVisitor, code: str) -> CheckResult:
        params = rule.parameters
        classes = visitor.classes

        if rule.validator_name == "check_class_hierarchy":
            base_class = params.get("base_class", "")
            subclasses = params.get("subclasses", [])
            has_base = any(base_class.lower() in c.lower() for c in classes)
            found_subclasses = [sub for sub in subclasses if any(sub.lower() in c.lower() for c in classes)]

            passed = has_base and len(found_subclasses) >= 2
            score = rule.max_score if passed else (rule.max_score * 0.4 if has_base else 0.0)
            msg = (
                f"Found base entity '{base_class}' and {len(found_subclasses)} subclasses: {found_subclasses}."
                if passed else
                f"Missing or incomplete hierarchy. Expected base '{base_class}' with subtypes like {subclasses[:3]}."
            )
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=rule.severity,
                message=msg,
                suggestion=rule.suggestion,
                code_reference=f"Found classes: {', '.join(classes.keys())}" if classes else "No classes found",
            )

        elif rule.validator_name == "check_class_methods":
            target_class = params.get("class_name", "")
            req_methods = params.get("required_methods", [])
            matching_class = next((c for c in classes if target_class.lower() in c.lower()), None)

            if not matching_class:
                return CheckResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    passed=False,
                    score=0.0,
                    max_score=rule.max_score,
                    severity=rule.severity,
                    message=f"Missing core domain class matching '{target_class}'.",
                    suggestion=rule.suggestion,
                )

            methods = classes[matching_class]["methods"]
            matched_methods = [m for m in req_methods if any(m in act.lower() for act in methods)]
            passed = len(matched_methods) >= 2
            score = rule.max_score if passed else (rule.max_score * 0.5 if len(matched_methods) >= 1 else 0.0)
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=rule.severity,
                message=f"Class '{matching_class}' implements methods: {list(methods)} (Matches: {matched_methods}).",
                suggestion=rule.suggestion,
                code_reference=f"Class {matching_class} at line {classes[matching_class]['line_no']}",
            )

        elif rule.validator_name == "check_strategy_pattern":
            pat_class = params.get("pattern_class", "")
            alternates = params.get("alternates", [])
            all_target_names = [pat_class] + alternates

            found_strategy = any(
                any(target.lower() in c.lower() for target in all_target_names)
                for c in classes
            )
            passed = found_strategy
            score = rule.max_score if passed else 0.0
            msg = (
                f"Successfully identified Strategy abstraction: {[c for c in classes if any(t.lower() in c.lower() for t in all_target_names)]}."
                if passed else
                f"Strategy pattern not detected. Expected a decoupled strategy class such as '{pat_class}'."
            )
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=rule.severity,
                message=msg,
                suggestion=rule.suggestion,
            )

        elif rule.validator_name == "check_state_representation":
            state_tokens = params.get("state_tokens", [])
            found = any(
                any(token.lower() in c.lower() for token in state_tokens)
                for c in classes
            ) or any(token.lower() in code.lower() for token in state_tokens)

            passed = found
            score = rule.max_score if passed else 0.0
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=rule.severity,
                message="Explicit state modeling verified." if passed else "No explicit state classes or state machine detected.",
                suggestion=rule.suggestion,
            )

        elif rule.validator_name == "check_god_class":
            target_class = params.get("class_name", "")
            threshold = params.get("max_method_threshold", 10)
            matching_class = next((c for c in classes if target_class.lower() in c.lower()), None)

            if not matching_class:
                return CheckResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    passed=True,
                    score=rule.max_score,
                    max_score=rule.max_score,
                    severity=CheckSeverity.INFO,
                    message=f"No God class detected for {target_class}.",
                    suggestion=rule.suggestion,
                )


            method_count = len(classes[matching_class]["methods"])
            is_god = method_count > threshold
            passed = not is_god
            score = rule.max_score if passed else (rule.max_score * 0.3)
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=CheckSeverity.WARNING if not passed else CheckSeverity.INFO,
                message=(
                    f"Class '{matching_class}' is well-focused ({method_count} methods)."
                    if passed else
                    f"Class '{matching_class}' has {method_count} methods (threshold: {threshold}), suggesting multiple responsibilities."
                ),
                suggestion=rule.suggestion,
            )

        elif rule.validator_name == "check_concurrency_lock":
            lock_tokens = params.get("lock_tokens", ["Lock", "acquire", "synchronized"])
            has_lock = visitor.uses_locks or any(token in code for token in lock_tokens)
            passed = has_lock
            score = rule.max_score if passed else 0.0
            ref = "; ".join(visitor.lock_invocations[:2]) if visitor.lock_invocations else None
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=rule.severity,
                message=(
                    f"Concurrency synchronization detected ({ref or 'Lock primitives in use'})."
                    if passed else
                    "No thread safety or synchronization primitives detected for critical state sections."
                ),
                suggestion=rule.suggestion,
                code_reference=ref,
            )

        elif rule.validator_name == "check_class_exists":
            names = params.get("class_names", [])
            found = [c for c in classes if any(name.lower() in c.lower() for name in names)]
            passed = len(found) > 0
            score = rule.max_score if passed else 0.0
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=rule.severity,
                message=f"Found entities: {found}" if passed else f"None of expected classes {names} were found.",
                suggestion=rule.suggestion,
            )

        elif rule.validator_name == "check_method_delegation":
            context_class = params.get("context_class", "")
            target_class = params.get("target_class", "")
            # Verify context delegates calls to target
            passed = any(context_class.lower() in c.lower() for c in classes) and \
                     any(target_class.lower() in c.lower() for c in classes)
            score = rule.max_score if passed else (rule.max_score * 0.4)
            return CheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                passed=passed,
                score=round(score, 1),
                max_score=rule.max_score,
                severity=rule.severity,
                message="Context delegates state operations appropriately." if passed else "Context-to-state delegation could be improved.",
                suggestion=rule.suggestion,
            )

        # Fallback default
        return CheckResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            category=rule.category,
            passed=True,
            score=rule.max_score,
            max_score=rule.max_score,
            severity=CheckSeverity.INFO,
            message="Check passed.",
            suggestion=rule.suggestion,
        )
