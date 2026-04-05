"""Command allowlist and argument validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple


class ValidationResult(NamedTuple):
    """Result of command validation."""
    valid: bool
    error: str | None = None


# Commands allowed to read from any path (including absolute).
READ_COMMANDS = frozenset(["ls", "cat"])
# Commands restricted to relative paths only (no absolute paths, no /).
WRITE_COMMANDS = frozenset(["cp", "mv", "rm"])

ALLOWED_COMMANDS = frozenset(["ls", "cat", "cp", "mv", "rm"])

# Pattern for valid path arguments: alphanumeric, dots, underscores, hyphens, slashes.
# No shell metacharacters.
SAFE_PATH_PATTERN = re.compile(r"^[\w\-./]+$")


def validate_command(command: str, args: list[str]) -> ValidationResult:
    """
    Validate a command against the allowlist.

    Security rules:
    - Command must be in the allowlist
    - Arguments must not contain shell metacharacters
    - No path traversal (..)
    - No environment variables or command substitution
    - rm/cp/mv: no absolute paths (starting with /)
    - rm: additionally block dangerous flag combos (-rf /, -rf /*, etc.)
    """
    if command not in ALLOWED_COMMANDS:
        return ValidationResult(False, f"Command '{command}' not in allowlist")

    for arg in args:
        # Block shell metacharacters per argument
        if re.search(r"[;&|`$(){}\[\]!?*<>\"\'\\]", arg):
            return ValidationResult(False, f"Disallowed characters in argument: {arg}")

        # Block environment variables
        if re.search(r"\$\w+|\$\{", arg):
            return ValidationResult(False, f"Environment variable not allowed: {arg}")

        # Block command substitution
        if "`" in arg or "$(" in arg:
            return ValidationResult(False, "Command substitution not allowed")

        # Block path traversal
        if ".." in arg:
            return ValidationResult(False, "Path traversal (..) not allowed")

        # Write commands (cp/mv/rm): no absolute paths
        if command in WRITE_COMMANDS:
            if arg.startswith("/"):
                return ValidationResult(False, f"Absolute paths not allowed for '{command}': {arg}")
            if arg == "/":
                return ValidationResult(False, "Root path '/' not allowed")

        # rm: block dangerous flag + target combos
        if command == "rm":
            if re.match(r"^-rf?$", arg):
                return ValidationResult(False, "Dangerous rm flags not allowed")
            if arg.startswith("-rf") or arg.startswith("-r"):
                return ValidationResult(False, f"Dangerous rm flags not allowed: {arg}")
            if arg in ("/", "/tmp", "/var", "/etc", "/home"):
                return ValidationResult(False, f"Refusing to rm critical path: {arg}")

        # Validate path characters only
        if not SAFE_PATH_PATTERN.match(arg):
            return ValidationResult(False, f"Invalid characters in argument: {arg}")

    return ValidationResult(True)
