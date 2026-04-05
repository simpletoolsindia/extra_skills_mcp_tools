"""Engineering Intelligence MCP - Python port of engi-mcp tools.

Provides compact intelligence layer for repositories with:
- Scoped file discovery
- Flow summaries
- Bug tracing
- Planning tools
- Multi-session memory
"""

from __future__ import annotations

import os
import json
import hashlib
from typing import Optional, List, Dict, Any, TypeVar
from pathlib import Path
from datetime import datetime
from collections import defaultdict

T = TypeVar('T')

# Storage for task memory and repo index
_TASK_STORAGE: Dict[str, Dict] = {}
_REPO_INDEX: Dict[str, Dict] = {}


class RepoIndex:
    """Repository index for fast file discovery."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.files: List[Dict] = []
        self.symbols: Dict[str, List] = defaultdict(list)
        self.imports: Dict[str, List] = defaultdict(list)
        self.tests: List[Dict] = []
        self.docs: List[Dict] = []

    def build(self, extensions: List[str] = None):
        """Build index by scanning repository."""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java']

        self.files = []
        skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'build', 'dist'}

        for path in self.repo_path.rglob('*'):
            if any(skip in path.parts for skip in skip_dirs):
                continue
            if path.is_file() and path.suffix in extensions:
                rel_path = str(path.relative_to(self.repo_path))
                self.files.append({
                    "path": rel_path,
                    "size": path.stat().st_size,
                    "ext": path.suffix,
                })

    def search(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """Search files by keywords."""
        scores = []
        keywords_lower = [k.lower() for k in keywords]

        for f in self.files:
            score = 0
            path_lower = f["path"].lower()
            for kw in keywords_lower:
                if kw in path_lower:
                    score += 1
            if score > 0:
                scores.append((score, f))

        scores.sort(reverse=True)
        return [f for _, f in scores[:limit]]


def task_classify(task: str, keywords: List[str] = None) -> dict:
    """
    Classify engineering task type.

    Args:
        task: Task description
        keywords: Optional context keywords

    Returns:
        dict with keys: task_type, confidence, reasoning
    """
    task_lower = task.lower()

    # Classification rules
    classifications = {
        "bug": {
            "keywords": ["bug", "fix", "error", "crash", "fail", "broken", "issue", "problem", "not working"],
            "weight": 1.0
        },
        "feature": {
            "keywords": ["add", "new", "implement", "create", "feature", "enhance", "improve"],
            "weight": 1.0
        },
        "refactor": {
            "keywords": ["refactor", "restructure", "clean", "simplify", "optimize", "rewrite"],
            "weight": 1.0
        },
        "documentation": {
            "keywords": ["doc", "readme", "comment", "document", "explain", "describe"],
            "weight": 1.0
        },
        "test": {
            "keywords": ["test", "spec", "coverage", "unit", "integration"],
            "weight": 1.0
        },
        "analysis": {
            "keywords": ["analyze", "review", "understand", "explore", "investigate"],
            "weight": 1.0
        },
        "poc": {
            "keywords": ["proof", "concept", "prototype", "demo", "sketch", "experiment"],
            "weight": 1.0
        }
    }

    scores = {}
    for ctype, info in classifications.items():
        score = sum(1 for kw in info["keywords"] if kw in task_lower)
        if keywords:
            score += sum(1 for kw in keywords if kw.lower() in task_lower)
        if score > 0:
            scores[ctype] = score * info["weight"]

    if not scores:
        return {
            "task_type": "unknown",
            "confidence": 0.0,
            "reasoning": "No clear classification pattern detected"
        }

    best_type = max(scores, key=scores.get)
    confidence = scores[best_type] / (len(task.split()) + 1)

    reasoning_map = {
        "bug": f"Task contains bug-fix related keywords",
        "feature": f"Task appears to be a new feature or enhancement",
        "refactor": f"Task involves code restructuring",
        "documentation": f"Task is documentation focused",
        "test": f"Task involves testing",
        "analysis": f"Task is exploratory or analysis focused",
        "poc": f"Task is proof-of-concept or prototyping"
    }

    return {
        "task_type": best_type,
        "confidence": min(confidence * 2, 1.0),
        "reasoning": reasoning_map.get(best_type, "Task classification based on keyword analysis"),
        "alternatives": [k for k, v in sorted(scores.items(), key=lambda x: -x[1]) if k != best_type][:3]
    }


def repo_scope_find(repo_path: str, task: str, task_type: str = None, limit: int = 20) -> dict:
    """
    Find minimum relevant files for a task.

    Args:
        repo_path: Repository path
        task: Task description
        task_type: Optional pre-classified task type
        limit: Max results

    Returns:
        dict with keys: files (list), scope, reasoning
    """
    # Build index if not cached
    cache_key = f"{repo_path}_index"
    if cache_key not in _REPO_INDEX:
        index = RepoIndex(repo_path)
        index.build()
        _REPO_INDEX[cache_key] = index
    else:
        index = _REPO_INDEX[cache_key]

    # Extract keywords from task
    words = task.lower().split()
    stop_words = {"the", "a", "an", "is", "are", "to", "for", "of", "and", "in", "on", "with", "this", "that"}
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    # Search files
    results = index.search(keywords, limit=limit)

    # Determine scope
    if task_type == "bug":
        scope = "critical"
    elif task_type == "feature":
        scope = "expanded"
    else:
        scope = "standard"

    return {
        "files": [f["path"] for f in results],
        "scope": scope,
        "reasoning": f"Found {len(results)} files matching keywords: {keywords[:5]}",
        "keywords_used": keywords[:10],
        "indexed_files": len(index.files)
    }


def flow_summarize(entry_point: str, scope: List[str] = None, verbosity: str = "standard") -> dict:
    """
    Summarize execution flow (compact, not raw code).

    Args:
        entry_point: Main file or function
        scope: Files to include
        verbosity: minimal, standard, detailed

    Returns:
        dict with keys: flow, components, summary
    """
    # This is a placeholder - in production, parse actual code
    flow_summary = {
        "minimal": "Flow: Main entry -> Process -> Output",
        "standard": "Flow: Main entry imports modules, processes data, returns output",
        "detailed": "Entry point initializes, loads dependencies, processes input, generates output, handles errors"
    }

    components = []
    if scope:
        components = [f"Component: {s}" for s in scope[:5]]

    return {
        "flow": flow_summary.get(verbosity, flow_summary["standard"]),
        "components": components,
        "summary": f"Execution follows a standard pattern with {len(components)} main components",
        "entry_point": entry_point
    }


def bug_trace_compact(scope: List[str], symptom: str) -> dict:
    """
    Pinpoint likely bug causes from symptom.

    Args:
        scope: Files to investigate
        symptom: Bug description

    Returns:
        dict with keys: likely_causes, confidence, reasoning
    """
    symptom_lower = symptom.lower()

    causes = []

    # Pattern matching for common bugs
    if any(w in symptom_lower for w in ["null", "none", "undefined", "undefined"]):
        causes.append({"cause": "Null/undefined reference", "confidence": 0.8, "pattern": "Check variable initialization"})

    if any(w in symptom_lower for w in ["crash", "exit", "kill"]):
        causes.append({"cause": "Unhandled exception or exit", "confidence": 0.7, "pattern": "Add try-catch or error handler"})

    if any(w in symptom_lower for w in ["slow", "lag", "performance"]):
        causes.append({"cause": "Performance issue", "confidence": 0.6, "pattern": "Check for loops, DB queries, or memory issues"})

    if any(w in symptom_lower for w in ["wrong", "incorrect", "wrong"]):
        causes.append({"cause": "Logic error", "confidence": 0.75, "pattern": "Review business logic and conditions"})

    if any(w in symptom_lower for w in ["missing", "not found", "404"]):
        causes.append({"cause": "Missing resource or dependency", "confidence": 0.8, "pattern": "Check imports and file paths"})

    if any(w in symptom_lower for w in ["memory", "leak", "oom"]):
        causes.append({"cause": "Memory leak", "confidence": 0.7, "pattern": "Check for unclosed resources or growing data structures"})

    if not causes:
        causes.append({"cause": "Unknown - requires manual investigation", "confidence": 0.3, "pattern": "Review code and add debug logs"})

    return {
        "likely_causes": causes,
        "symptom": symptom,
        "scope_files": scope[:5],
        "recommendation": causes[0]["pattern"] if causes else "Add debugging to identify root cause"
    }


def implementation_plan(task: str, scope: List[str], task_type: str = "feature", existing_patterns: List[str] = None) -> dict:
    """
    Generate step-by-step implementation plan.

    Args:
        task: Task description
        scope: Files to modify
        task_type: bug, feature, refactor
        existing_patterns: Patterns to follow

    Returns:
        dict with keys: steps, risks, files_to_modify
    """
    steps = []

    if task_type == "bug":
        steps = [
            {"step": 1, "action": "Reproduce and isolate the bug", "target": scope[0] if scope else None},
            {"step": 2, "action": "Identify root cause", "target": None},
            {"step": 3, "action": "Implement fix", "target": scope[0] if scope else None},
            {"step": 4, "action": "Add regression tests", "target": "tests/"},
            {"step": 5, "action": "Verify fix", "target": None},
        ]
        risks = ["risk: Fix may introduce new bugs", "risk: Edge cases not covered"]
    elif task_type == "feature":
        steps = [
            {"step": 1, "action": "Design solution architecture", "target": None},
            {"step": 2, "action": "Implement core functionality", "target": scope[0] if scope else "src/"},
            {"step": 3, "action": "Add error handling", "target": None},
            {"step": 4, "action": "Write tests", "target": "tests/"},
            {"step": 5, "action": "Update documentation", "target": "docs/"},
        ]
        risks = ["risk: Complexity may grow", "risk: May need refactoring later"]
    else:
        steps = [
            {"step": 1, "action": "Analyze current implementation", "target": scope[0] if scope else None},
            {"step": 2, "action": "Plan refactoring approach", "target": None},
            {"step": 3, "action": "Execute refactoring", "target": scope},
            {"step": 4, "action": "Verify tests pass", "target": "tests/"},
        ]
        risks = ["risk: Breaking changes", "risk: May need temporary workaround"]

    return {
        "steps": steps,
        "risks": risks,
        "files_to_modify": scope,
        "task_type": task_type,
        "patterns_to_follow": existing_patterns or ["follow existing code style"]
    }


def poc_plan(goal: str, existing_code: List[str] = None, constraints: List[str] = None) -> dict:
    """
    Scaffold minimum viable proof-of-concept.

    Args:
        goal: POC goal
        existing_code: Existing code to leverage
        constraints: Known constraints

    Returns:
        dict with keys: scaffold, minimum_viable, approach
    """
    scaffold = {
        "project_structure": ["src/", "tests/", "README.md", "requirements.txt"],
        "core_files": [
            {"name": "main.py", "purpose": "Entry point"},
            {"name": "core.py", "purpose": "Core logic"},
            {"name": "test_main.py", "purpose": "Basic tests"},
        ],
        "dependencies": ["httpx", "pydantic"]
    }

    return {
        "goal": goal,
        "scaffold": scaffold,
        "minimum_viable": [
            f"1. Create {scaffold['core_files'][0]['name']} with entry point",
            "2. Implement basic logic in core module",
            "3. Add simple test",
            "4. Verify it works"
        ],
        "constraints": constraints or [],
        "leverage_existing": existing_code[:3] if existing_code else []
    }


def impact_analyze(scope: List[str], change_type: str) -> dict:
    """
    Estimate blast radius of changes.

    Args:
        scope: Files being changed
        change_type: add, modify, delete

    Returns:
        dict with keys: impact_level, affected_areas, risk_score
    """
    risk_map = {
        "delete": {"critical": ["core", "main", "app"], "high": ["service", "api"], "medium": ["test", "util"]},
        "modify": {"critical": ["core", "main"], "high": ["service"], "medium": ["test", "util"]},
        "add": {"low": ["new"], "medium": ["module"]}
    }

    impact_scores = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.1}
    impact_level = "low"
    risk_score = 0.1

    for f in scope:
        f_lower = f.lower()
        for severity, keywords in risk_map.get(change_type, {}).items():
            if any(kw in f_lower for kw in keywords):
                impact_level = max(impact_level, severity)
                risk_score = max(risk_score, impact_scores[severity])

    affected_areas = [f"Area: {s}" for s in scope[:5]]

    return {
        "impact_level": impact_level,
        "risk_score": risk_score,
        "affected_areas": affected_areas,
        "recommendation": "Review carefully" if risk_score > 0.5 else "Safe to proceed"
    }


def test_select(scope: List[str], change_type: str) -> dict:
    """
    Return minimum test set for changed files.

    Args:
        scope: Changed files
        change_type: add, modify, delete

    Returns:
        dict with keys: tests_to_run, coverage_estimate
    """
    tests = []

    for f in scope:
        # Map source files to test files
        if f.endswith('.py'):
            test_file = f.replace('src/', 'tests/').replace('.py', '_test.py')
            tests.append({"test": test_file, "covers": f})
        elif f.endswith('.js') or f.endswith('.ts'):
            test_file = f.replace('src/', '__tests__/').replace('.ts', '.test.ts')
            tests.append({"test": test_file, "covers": f})

    coverage = 80 if change_type != "delete" else 60

    return {
        "tests_to_run": tests,
        "coverage_estimate": f"{coverage}%",
        "total_tests": len(tests),
        "skip_tests": ["integration"] if change_type == "add" else []
    }


def doc_context_build(audience: str, changed_files: List[str], feature: str = None) -> dict:
    """
    Build compact context for documentation.

    Args:
        audience: junior, senior, pm, qa, api
        changed_files: Files that changed
        feature: Feature being documented

    Returns:
        dict with keys: context, key_points, omit
    """
    audience_contexts = {
        "junior": "Simple explanations, step-by-step, code examples",
        "senior": "Technical depth, architecture, patterns",
        "pm": "High-level overview, business impact, timeline",
        "qa": "Test scenarios, edge cases, expected behavior",
        "api": "Endpoints, parameters, return values, examples"
    }

    return {
        "audience": audience,
        "context": audience_contexts.get(audience, audience_contexts["senior"]),
        "key_points": [f"Point: {f}" for f in changed_files[:5]],
        "omit": ["internal implementation details"] if audience == "pm" else [],
        "feature": feature or "Changes"
    }


def doc_update_plan(changed_files: List[str], existing_docs: List[str] = None) -> dict:
    """
    Identify which docs need updating after code changes.

    Args:
        changed_files: Files that changed
        existing_docs: Existing documentation files

    Returns:
        dict with keys: docs_to_update, docs_to_create, reasoning
    """
    docs_to_update = []
    docs_to_create = []

    # Simple mapping
    for f in changed_files:
        if 'README' in f:
            docs_to_update.append("README.md")
        elif 'API' in f or 'api' in f:
            docs_to_update.append("API.md")
            docs_to_create.append("CHANGELOG.md")

    return {
        "docs_to_update": docs_to_update or ["Update main documentation"],
        "docs_to_create": docs_to_create,
        "reasoning": f"Based on {len(changed_files)} changed files"
    }


def memory_checkpoint(task_id: str, files: List[str], modules: List[str] = None,
                    symbols: List[str] = None, notes: str = None,
                    pending_docs: List[str] = None, pending_validations: List[str] = None,
                    decisions: List[Dict] = None, risks: List[str] = None,
                    task_type: str = "mixed") -> dict:
    """
    Save task state for multi-session continuity.

    Args:
        task_id: Unique task identifier
        files: Files in scope
        modules: Modules in scope
        symbols: Symbols in scope
        notes: Additional notes
        pending_docs: Pending documentation
        pending_validations: Pending validations
        decisions: Decisions made
        risks: Identified risks
        task_type: analysis, feature, bug, poc, documentation, mixed

    Returns:
        dict with confirmation
    """
    _TASK_STORAGE[task_id] = {
        "task_id": task_id,
        "files": files,
        "modules": modules or [],
        "symbols": symbols or [],
        "notes": notes or "",
        "pending_docs": pending_docs or [],
        "pending_validations": pending_validations or [],
        "decisions": decisions or [],
        "risks": risks or [],
        "task_type": task_type,
        "checkpoint_time": datetime.now().isoformat()
    }

    return {
        "checkpoint_id": task_id,
        "status": "saved",
        "files_tracked": len(files),
        "message": f"Task state saved. Restore with memory_restore."
    }


def memory_restore(task_id: str = None, id: str = None) -> dict:
    """
    Restore previously saved checkpoint.

    Args:
        task_id: Task ID to restore
        id: Alias for task_id

    Returns:
        dict with restored state or error
    """
    lookup_id = task_id or id

    if not lookup_id:
        return {"error": "Provide task_id or id parameter"}

    if lookup_id not in _TASK_STORAGE:
        available = list(_TASK_STORAGE.keys())
        return {
            "error": f"Checkpoint not found: {lookup_id}",
            "available_checkpoints": available,
            "hint": "Use memory_checkpoint to save a new checkpoint"
        }

    return {
        "task_id": lookup_id,
        "state": _TASK_STORAGE[lookup_id],
        "message": "Checkpoint restored successfully"
    }