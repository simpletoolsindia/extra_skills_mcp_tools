"""Integration tests for mcp_server tools."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent / "src"


# ---------------------------------------------------------------------------
# Command validator tests
# ---------------------------------------------------------------------------

def test_allowed_commands():
    from mcp_server.security.command_validator import validate_command

    # Read-only commands can use absolute paths
    assert validate_command("ls", ["/tmp"]).valid
    assert validate_command("ls", ["/"]).valid
    assert validate_command("cat", ["/etc/passwd"]).valid
    # Write commands require relative paths
    assert validate_command("cp", ["a.txt", "b.txt"]).valid
    assert validate_command("mv", ["a.txt", "b.txt"]).valid
    assert validate_command("rm", ["file.txt"]).valid


def test_blocked_commands():
    from mcp_server.security.command_validator import validate_command

    # Not in allowlist
    assert not validate_command("curl", []).valid
    assert not validate_command("wget", []).valid
    assert not validate_command("bash", []).valid
    assert not validate_command("python3", []).valid


def test_blocked_write_absolute_paths():
    from mcp_server.security.command_validator import validate_command

    # rm/cp/mv cannot use absolute paths
    assert not validate_command("rm", ["/etc/passwd"]).valid
    assert not validate_command("cp", ["/tmp/file", "dest"]).valid
    assert not validate_command("mv", ["/tmp/file", "dest"]).valid


def test_blocked_dangerous_rm():
    from mcp_server.security.command_validator import validate_command

    assert not validate_command("rm", ["-rf"]).valid
    assert not validate_command("rm", ["-r"]).valid
    assert not validate_command("rm", ["/"]).valid
    assert not validate_command("rm", ["/tmp"]).valid
    assert not validate_command("rm", ["/etc"]).valid


def test_blocked_path_traversal():
    from mcp_server.security.command_validator import validate_command

    assert not validate_command("cat", ["../../etc/passwd"]).valid
    assert not validate_command("ls", ["../root"]).valid
    assert not validate_command("cp", ["../secret", "dest"]).valid


def test_blocked_shell_metacharacters():
    from mcp_server.security.command_validator import validate_command

    assert not validate_command("ls", ["/tmp; cat /etc/passwd"]).valid
    assert not validate_command("cat", ["file | grep root"]).valid
    assert not validate_command("ls", ["`whoami`"]).valid
    assert not validate_command("ls", ["$(whoami)"]).valid


def test_blocked_env_vars():
    from mcp_server.security.command_validator import validate_command

    assert not validate_command("cat", ["$HOME/file"]).valid
    assert not validate_command("ls", ["${HOME}/.ssh"]).valid


# ---------------------------------------------------------------------------
# Sandbox tests
# ---------------------------------------------------------------------------

def test_sandbox_ls_absolute():
    from mcp_server.security.sandbox import execute_sandboxed

    result = execute_sandboxed("ls", ["/tmp"])
    assert result["error"] is None
    assert result["exit_code"] == 0


def test_sandbox_ls_relative():
    from mcp_server.security.sandbox import execute_sandboxed

    result = execute_sandboxed("ls", ["."])
    assert result["error"] is None
    assert result["exit_code"] == 0


def test_sandbox_invalid_command():
    from mcp_server.security.sandbox import execute_sandboxed

    result = execute_sandboxed("curl", [])
    assert result["error"] is not None


def test_sandbox_dangerous_rm_blocked():
    from mcp_server.security.sandbox import execute_sandboxed

    result = execute_sandboxed("rm", ["-rf"])
    assert result["error"] is not None


# ---------------------------------------------------------------------------
# Web search tool tests (mocked — no real SearXNG required)
# ---------------------------------------------------------------------------

def test_web_search_returns_structure(monkeypatch):
    import mcp_server.tools.web_search as ws
    import httpx

    @dataclass
    class FakeResponse:
        status_code: int = 200
        text: str = ""

        def json(self):
            return {"results": [
                {"title": "Test", "url": "https://example.com", "content": "Snippet", "engine": "google"}
            ]}

        def raise_for_status(self):
            pass

    class FakeClient:
        def get(self, *a, **k): return FakeResponse()
        def __enter__(self): return self
        def __exit__(self, *a): pass

    monkeypatch.setattr(ws.httpx, "Client", lambda **k: FakeClient())

    result = ws.web_search("test query", limit=5)
    assert "results" in result
    assert result["error"] is None
    assert len(result["results"]) == 1
    assert result["results"][0]["title"] == "Test"


def test_web_search_connection_error(monkeypatch):
    import mcp_server.tools.web_search as ws
    import httpx

    monkeypatch.setattr(ws.httpx, "Client", lambda **k: (_ for _ in ()).throw(httpx.ConnectError("no")))

    result = ws.web_search("test")
    assert result["error"] is not None
    assert "Cannot connect to SearXNG" in result["error"]


# ---------------------------------------------------------------------------
# Content fetch tests (mocked — no real HTTP required)
# ---------------------------------------------------------------------------

def test_fetch_web_content_returns_structure(monkeypatch):
    import mcp_server.utils.html_processor as hp

    html = "<html><head><title>Test</title></head><body><p>Hello world</p></body></html>"

    @dataclass
    class FakeResponse:
        status_code: int = 200
        text: str = html
        url: str = "https://example.com"

        def raise_for_status(self):
            pass

    class FakeClient:
        def get(self, *a, **k): return FakeResponse()
        def __enter__(self): return self
        def __exit__(self, *a): pass

    monkeypatch.setattr(hp.httpx, "Client", lambda **k: FakeClient())

    result = hp.fetch_and_extract("https://example.com")
    assert "title" in result
    assert "text" in result
    assert "error" in result
    assert result["error"] is None
    assert result["title"] == "Test"


# ---------------------------------------------------------------------------
# MCP server JSON-RPC integration tests
# ---------------------------------------------------------------------------

def _server_roundtrip(requests: list[dict], timeout: float = 5.0) -> list[dict]:
    """
    Start the MCP server, send requests, return parsed responses.
    Uses threads for non-blocking stdin/stdout since the server loops forever.
    Uses unbuffered Python to avoid stdout buffering issues.
    """
    server_script = SRC / "mcp_server" / "server.py"
    proc = subprocess.Popen(
        [sys.executable, "-u", str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,  # unbuffered
        env={**os.environ, "PYTHONPATH": str(SRC)},
    )

    responses: list[dict] = []
    write_done = threading.Event()
    read_done = threading.Event()

    def write_requests():
        for req in requests:
            proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()
        write_done.set()

    def read_responses():
        # Collect responses until write is done and we have enough lines
        # (each request may produce 1 response + 0-N notifications)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line:
                responses.append(json.loads(line))
            # Stop when writes are done AND we've collected enough response lines
            if write_done.is_set() and len(responses) >= len(requests) * 2:
                break
        read_done.set()

    w_thread = threading.Thread(target=write_requests)
    r_thread = threading.Thread(target=read_responses)

    w_thread.start()
    r_thread.start()

    w_thread.join(timeout=timeout)
    r_thread.join(timeout=timeout)

    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    return responses


def test_server_handles_initialize():
    responses = _server_roundtrip([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    ])
    # Response to initialize (has result) + notifications/initialized (has method)
    assert len(responses) == 2
    resp = next(r for r in responses if "result" in r)
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    notif = next(r for r in responses if "method" in r)
    assert notif["method"] == "notifications/initialized"


def test_server_handles_tools_list():
    responses = _server_roundtrip([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ])
    # Response 2 (id=2) should be tools/list
    list_resp = next((r for r in responses if r.get("id") == 2), None)
    assert list_resp is not None
    tools = list_resp["result"]["tools"]
    names = [t["name"] for t in tools]
    assert "web_search" in names
    assert "fetch_web_content" in names
    assert "run_command" in names


def test_server_handles_unknown_tool():
    responses = _server_roundtrip([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}}
        },
    ])
    call_resp = next((r for r in responses if r.get("id") == 2), None)
    assert call_resp is not None
    content = call_resp["result"]["content"]
    text = content[0]["text"]
    parsed = json.loads(text)
    assert "Unknown tool" in parsed["error"]


def test_server_handles_valid_run_command():
    responses = _server_roundtrip([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "run_command", "arguments": {"command": "ls", "args": ["."]}}
        },
    ])
    call_resp = next((r for r in responses if r.get("id") == 2), None)
    assert call_resp is not None
    parsed = json.loads(call_resp["result"]["content"][0]["text"])
    assert parsed["exit_code"] == 0
