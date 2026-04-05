#!/usr/bin/env python3
"""Quick verification script — tests all three tools with minimal setup."""

import sys
import os
from pathlib import Path

# Ensure local src is on path (overrides any installed package for live testing)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
os.chdir(Path(__file__).parent.parent)

from mcp_server.security.command_validator import validate_command
from mcp_server.security.sandbox import execute_sandboxed
from mcp_server.tools.web_search import web_search
from mcp_server.tools.fetch_web_content import fetch_web_content
from mcp_server.tools.run_command import run_command


def test(command, label):
    ok = "✓" if command else "✗"
    status = "PASS" if command else "FAIL"
    print(f"  {ok} {label}: {status}")
    return command


def main():
    print("MCP Server Verification")
    print("=" * 40)

    print("\n[1] Command Validator")
    test(validate_command("ls", ["/tmp"]).valid, "ls /tmp allowed")
    test(not validate_command("curl", []).valid, "curl blocked")
    test(not validate_command("cat", ["../../etc/passwd"]).valid, "path traversal blocked")
    test(not validate_command("ls", ["/tmp; rm -rf /"]).valid, "shell chars blocked")

    print("\n[2] Sandbox — run_command tool")
    result = run_command("ls", ["/tmp"])
    test(result["error"] is None, "ls /tmp executes")
    test(result["exit_code"] == 0, "exit code 0")

    blocked = run_command("rm", ["-rf", "/"])
    test(blocked["error"] is not None, "rm -rf / blocked")

    print("\n[3] Web Search — requires SearXNG at SEARXNG_BASE_URL")
    base_url = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8888")
    print(f"  Using: {base_url}")
    if os.environ.get("SKIP_NETWORK"):
        print("  SKIP_NETWORK set — skipping live test")
    else:
        result = web_search("python programming", limit=3)
        if result["error"]:
            print(f"  ! SearXNG not reachable: {result['error']}")
            print("  (Start SearXNG first, or set SKIP_NETWORK=1)")
        else:
            print(f"  ✓ Got {len(result['results'])} results")
            for r in result["results"][:3]:
                print(f"    - {r['title']}")

    print("\n[4] Fetch Web Content — live test")
    if os.environ.get("SKIP_NETWORK"):
        print("  SKIP_NETWORK set — skipping live test")
    else:
        result = fetch_web_content("https://example.com")
        if result["error"]:
            print(f"  ! Error: {result['error']}")
        else:
            print(f"  ✓ Title: {result['title']}")
            print(f"  ✓ Content length: {len(result['text'])} chars")

    print("\n" + "=" * 40)
    print("Verification complete.")
    print("\nTo run live tests with a live SearXNG:")
    print("  SEARXNG_BASE_URL=http://localhost:8888 python tests/verify.py")
    print("\nTo skip live network tests:")
    print("  SKIP_NETWORK=1 python tests/verify.py")


if __name__ == "__main__":
    main()
