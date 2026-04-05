"""Sandboxed command execution with process isolation."""

from __future__ import annotations

import subprocess
import threading
from typing import Any

from .command_validator import validate_command


TIMEOUT_SECONDS = 10


def execute_sandboxed(command: str, args: list[str]) -> dict[str, Any]:
    """
    Execute a validated command in a sandboxed subprocess.

    Returns:
        dict with keys: stdout, stderr, exit_code, error
    """
    # Validate first
    result = validate_command(command, args)
    if not result.valid:
        return {
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "error": result.error,
        }

    full_cmd = [command] + args

    try:
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            # No shell=True — command is already split
            # Process group isolation
            start_new_session=True,
        )

        def wait_with_timeout():
            proc.wait()

        thread = threading.Thread(target=wait_with_timeout)
        thread.start()
        thread.join(timeout=TIMEOUT_SECONDS)

        if proc.poll() is None:
            # Still running — kill it
            proc.kill()
            proc.wait()
            return {
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": f"Command timed out after {TIMEOUT_SECONDS}s",
            }

        stdout, stderr = proc.communicate()
        return {
            "stdout": stdout[:10_000],  # Cap output
            "stderr": stderr[:2_000],
            "exit_code": proc.returncode,
            "error": None,
        }

    except PermissionError:
        return {
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "error": "Permission denied",
        }
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "error": f"Command '{command}' not found",
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "error": str(e),
        }
