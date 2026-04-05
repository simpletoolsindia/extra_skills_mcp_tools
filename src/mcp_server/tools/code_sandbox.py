"""Code sandbox for running LLM-generated code in isolated environments."""

from __future__ import annotations

import os
import subprocess
import tempfile
import hashlib
import json
from typing import Optional


SANDBOX_TIMEOUT = int(os.environ.get("SANDBOX_TIMEOUT", "30"))
ALLOWED_LANGUAGES = {
    "python": ["py", "python", "py3"],
    "javascript": ["js", "javascript", "node"],
    "bash": ["sh", "bash", "shell"],
}


def _validate_code(code: str, language: str) -> Optional[str]:
    """Validate code for safety. Returns error message or None if valid."""
    if not code or len(code) > 100000:  # 100KB limit
        return "Code too long or empty"

    if language.lower() not in ALLOWED_LANGUAGES:
        return f"Language '{language}' not supported. Allowed: {list(ALLOWED_LANGUAGES.keys())}"

    # Basic security checks
    dangerous_patterns = [
        "import os; os.system",
        "subprocess.call",
        "__import__",
        "eval(",
        "exec(",
        "os.remove",
        "shutil.rmtree",
        "chmod 777",
        "curl http",  # Allow https
        "wget http",  # Allow https
    ]

    for pattern in dangerous_patterns:
        if pattern in code and "https" not in code.split(pattern)[0].split("\n")[-1]:
            return f"Forbidden pattern detected: {pattern}"

    return None


def run_code(
    code: str,
    language: str = "python",
    timeout: int = SANDBOX_TIMEOUT,
    args: Optional[list] = None,
) -> dict:
    """
    Run code in a sandboxed environment.

    Args:
        code: The code to execute
        language: Programming language (python, javascript, bash)
        timeout: Maximum execution time in seconds
        args: Command-line arguments to pass to the script

    Returns:
        dict with keys: output, error, execution_time, exit_code
    """
    validation_error = _validate_code(code, language)
    if validation_error:
        return {
            "output": "",
            "error": validation_error,
            "execution_time": 0,
            "exit_code": 1,
        }

    # Create temporary file with unique name
    suffix_map = {
        "python": ".py",
        "javascript": ".js",
        "bash": ".sh",
    }
    suffix = suffix_map.get(language.lower(), ".txt")

    # Create temp dir with hash to avoid conflicts
    code_hash = hashlib.md5(code.encode()).hexdigest()[:8]
    temp_dir = tempfile.mkdtemp(prefix=f"sandbox_{code_hash}_")

    try:
        filename = f"script{suffix}"
        filepath = os.path.join(temp_dir, filename)

        with open(filepath, "w") as f:
            f.write(code)

        # Build command
        if language.lower() == "python":
            cmd = ["python3", filepath]
        elif language.lower() == "javascript":
            cmd = ["node", filepath]
        elif language.lower() == "bash":
            cmd = ["bash", filepath]

        if args:
            cmd.extend(args)

        # Run with timeout
        import time
        start_time = time.time()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=min(timeout, SANDBOX_TIMEOUT),
            cwd=temp_dir,
        )

        execution_time = time.time() - start_time

        return {
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else "",
            "execution_time": round(execution_time, 2),
            "exit_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": f"Execution timed out after {timeout} seconds",
            "execution_time": timeout,
            "exit_code": -1,
        }
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "execution_time": 0,
            "exit_code": -1,
        }
    finally:
        # Cleanup temp directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


def run_python_snippet(
    code: str,
    imports: Optional[list] = None,
    timeout: int = 30,
) -> dict:
    """
    Run a Python snippet with optional common imports pre-loaded.

    Args:
        code: Python code to run
        imports: List of module names to import (json, math, re, etc.)
        timeout: Max execution time

    Returns:
        dict with keys: output, error, execution_time, exit_code
    """
    # Prepend imports if provided
    setup_code = ""
    if imports:
        import_set = set(imports)
        common_imports = {
            "json": "import json",
            "math": "import math",
            "re": "import re",
            "datetime": "from datetime import datetime",
            "collections": "from collections import Counter, defaultdict",
            "itertools": "from itertools import product, permutations",
            "functools": "from functools import lru_cache",
        }
        for mod in import_set:
            if mod in common_imports:
                setup_code += common_imports[mod] + "\n"
            else:
                setup_code += f"import {mod}\n"

    full_code = setup_code + "\n" + code
    return run_code(full_code, language="python", timeout=timeout)


def test_code_snippet(
    code: str,
    language: str = "python",
    expected_output: Optional[str] = None,
) -> dict:
    """
    Run code and optionally verify expected output.

    Args:
        code: Code to run
        language: Programming language
        expected_output: If provided, check if output matches

    Returns:
        dict with keys: passed, output, error, details
    """
    result = run_code(code, language)

    passed = result["exit_code"] == 0
    if expected_output is not None:
        passed = passed and result["output"].strip() == expected_output.strip()

    return {
        "passed": passed,
        "output": result["output"],
        "error": result["error"],
        "exit_code": result["exit_code"],
        "matches_expected": result["output"].strip() == expected_output.strip() if expected_output else None,
    }