"""
MCP Server — STDIO-based Model Context Protocol server.

Implements the MCP protocol over STDIO using JSON-RPC 2.0.
"""

from __future__ import annotations

import json
import sys
import logging
from typing import Any
import asyncio

# Support both direct execution (python server.py) and module execution (python -m mcp_server)
if __package__ is None or __package__ == "":
    # Running as script — use absolute imports from installed package
    import mcp_server.schemas.tool_schemas as schemas_module
    import mcp_server.tools.web_search as ws_tool
    import mcp_server.tools.fetch_web_content
    import mcp_server.tools.run_command
    import mcp_server.tools.playwright_scrape
    import mcp_server.tools.scrapling_extract
    import mcp_server.tools.freedium_scrape
    import mcp_server.tools.code_sandbox

    TOOL_DEFINITIONS = schemas_module.TOOL_DEFINITIONS
    fetch_web_content = mcp_server.tools.fetch_web_content
    run_command = mcp_server.tools.run_command
    playwright_scrape = mcp_server.tools.playwright_scrape
    scrapling_extract = mcp_server.tools.scrapling_extract
    freedium_scrape = mcp_server.tools.freedium_scrape
    code_sandbox = mcp_server.tools.code_sandbox
else:
    # Running as package — use relative imports
    from .schemas.tool_schemas import TOOL_DEFINITIONS
    from .tools import web_search as ws_tool
    from .tools import fetch_web_content
    from .tools import run_command
    from .tools import playwright_scrape
    from .tools import scrapling_extract
    from .tools import freedium_scrape
    from .tools import code_sandbox

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("mcp_server")


# Tool registry: maps tool name -> callable
TOOL_CALLABLES: dict[str, Any] = {
    "web_search": ws_tool.web_search,
    "fetch_web_content": fetch_web_content.fetch_web_content,
    "run_command": run_command.run_command,
    "scrape_dynamic": playwright_scrape.scrape_dynamic_page,
    "extract_structured": scrapling_extract.extract_structured,
    "scrape_freedium": freedium_scrape.scrape_freedium,
    "list_freedium_articles": freedium_scrape.list_freedium_articles,
    "run_code": code_sandbox.run_code,
    "run_python_snippet": code_sandbox.run_python_snippet,
    "test_code_snippet": code_sandbox.test_code_snippet,
}


def send_response(response: dict) -> None:
    """Send a JSON-RPC response to stdout."""
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def send_notification(method: str, params: dict | None = None) -> None:
    """Send a JSON-RPC notification (no id)."""
    msg: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params:
        msg["params"] = params
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_initialize(params: dict) -> dict:
    """Handle MCP initialize handshake."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {
            "name": "mcp-server",
            "version": "0.1.0",
        },
    }


def handle_tools_list(params: dict) -> dict:
    """Handle tools/list — return all registered tools."""
    return {"tools": TOOL_DEFINITIONS}


def handle_tools_call(params: dict) -> dict:
    """Handle tools/call — dispatch to the appropriate tool."""
    name: str = params.get("name", "")
    arguments: dict = params.get("arguments", {})

    if name not in TOOL_CALLABLES:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": f"Unknown tool: {name}"}),
                }
            ],
            "isError": True,
        }

    try:
        tool_func = TOOL_CALLABLES[name]

        # Handle async functions (playwright)
        if asyncio.iscoroutinefunction(tool_func):
            result = asyncio.run(tool_func(**arguments))
        else:
            result = tool_func(**arguments)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False),
                }
            ],
            "isError": False,
        }

    except TypeError as e:
        # Wrong arguments passed to tool
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": f"Invalid arguments: {e}"}),
                }
            ],
            "isError": True,
        }
    except Exception as e:
        log.exception("Tool '%s' raised an exception", name)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": str(e)}),
                }
            ],
            "isError": True,
        }


def handle_request(method: str, params: dict, msg_id: int | str | None) -> None:
    """Route a JSON-RPC request and send the response."""
    if method == "initialize":
        result = handle_initialize(params)
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result,
        })
        # MCP: send initialized notification after successful initialize response
        send_notification("notifications/initialized", {})
        return

    handler = {
        "tools/list": handle_tools_list,
        "tools/call": handle_tools_call,
    }.get(method)

    if handler is None:
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        })
        return

    try:
        result = handler(params)
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result,
        })
    except Exception as e:
        log.exception("Handler for '%s' raised an exception", method)
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32603, "message": str(e)},
        })


def run() -> None:
    """Main server loop — read JSON-RPC requests from stdin."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            msg: dict = json.loads(line)
        except json.JSONDecodeError:
            continue

        if msg.get("method") in ("initialize", "tools/list", "tools/call"):
            handle_request(
                method=msg["method"],
                params=msg.get("params", {}),
                msg_id=msg.get("id"),
            )
        elif msg.get("method", "").startswith("notifications/"):
            # Silently ignore notifications
            pass


if __name__ == "__main__":
    run()
