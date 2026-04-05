"""Secure system command execution tool."""

from __future__ import annotations

from ..security.sandbox import execute_sandboxed


def run_command(command: str, args: list[str] | None = None) -> dict:
    """
    Execute a whitelisted system command in a sandboxed environment.

    Args:
        command: The command to run (from allowlist: ls, cat, cp, mv, rm)
        args: Arguments for the command

    Returns:
        dict with keys: stdout, stderr, exit_code, error
    """
    if args is None:
        args = []

    return execute_sandboxed(command, args)
