"""
MCP Server — Unified Model Context Protocol server.
Supports both STDIO (local) and TCP (remote) modes.
"""

from __future__ import annotations

import json
import sys
import os
import logging
import asyncio
from typing import Any

# Import tool schemas
from .schemas.tool_schemas import TOOL_DEFINITIONS

# Import all tools
from .tools import web_search as ws_tool
from .tools import fetch_web_content
from .tools import run_command
from .tools import playwright_scrape
from .tools import scrapling_extract
from .tools import freedium_scrape
from .tools import code_sandbox
from .tools import searxng
from .tools import hackernews
from .tools import wikipedia
from .tools import github
from .tools import file_system
from .tools import markitdown
from .tools import matplotlib_tools
from .tools import pandas_tools
from .tools import antd_charts
from .tools import huggingface
from .tools import sequential_thinking
from .tools import firecrawl
from .tools import webclaw
from .tools import browserbase
from .tools import youtube_transcript
from .tools import gpt_researcher
from .tools import engi_intelligence

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("mcp_server")


# Complete tool registry
TOOL_CALLABLES: dict[str, Any] = {
    # === SearXNG Native ===
    "searxng_search": searxng.search,
    "search_images": searxng.search_images,
    "search_news": searxng.search_news,
    "searxng_health": searxng.health_check,

    # === Web Scraping ===
    "fetch_web_content": fetch_web_content.fetch_web_content,
    "scrape_dynamic": playwright_scrape.scrape_dynamic_page,
    "extract_structured": scrapling_extract.extract_structured,
    "scrape_freedium": freedium_scrape.scrape_freedium,
    "list_freedium_articles": freedium_scrape.list_freedium_articles,
    "firecrawl_scrape": firecrawl.scrape_url,
    "firecrawl_crawl": firecrawl.crawl_url,
    "webclaw_crawl": webclaw.crawl_with_selectors,
    "webclaw_extract_article": webclaw.extract_article,
    "webclaw_extract_product": webclaw.extract_product,
    "browserbase_browse": browserbase.fallback_browse,

    # === Hacker News ===
    "hackernews_top": hackernews.get_top_stories,
    "hackernews_new": hackernews.get_new_stories,
    "hackernews_best": hackernews.get_best_stories,
    "hackernews_ask": hackernews.get_ask_hn,
    "hackernews_show": hackernews.get_show_hn,
    "hackernews_get_comments": hackernews.get_story_comments,
    "hackernews_user": hackernews.get_user,

    # === Wikipedia ===
    "wikipedia_search": wikipedia.search_wikipedia,
    "wikipedia_get_article": wikipedia.get_article,
    "wikipedia_related": wikipedia.get_related_articles,

    # === Hugging Face ===
    "huggingface_search_models": huggingface.search_models,
    "huggingface_search_datasets": huggingface.search_datasets,
    "huggingface_model_info": huggingface.get_model_info,
    "huggingface_trending": huggingface.get_trending_models,

    # === GitHub ===
    "github_repo": github.get_repo,
    "github_readme": github.get_readme,
    "github_issues": github.list_issues,
    "github_commits": github.list_commits,
    "github_search_repos": github.search_repositories,
    "github_file_content": github.get_file_content,

    # === File System ===
    "file_read": file_system.read_file,
    "file_write": file_system.write_file,
    "file_list": file_system.list_directory,
    "file_info": file_system.file_info,
    "file_search": file_system.search_files,

    # === Code Execution ===
    "run_code": code_sandbox.run_code,
    "run_python_snippet": code_sandbox.run_python_snippet,
    "test_code_snippet": code_sandbox.test_code_snippet,

    # === Pandas Data ===
    "pandas_create": pandas_tools.create_dataframe,
    "pandas_filter": pandas_tools.filter_dataframe,
    "pandas_aggregate": pandas_tools.aggregate_data,
    "pandas_correlation": pandas_tools.compute_correlation,
    "pandas_outliers": pandas_tools.detect_outliers,

    # === Matplotlib Charts ===
    "plot_line": matplotlib_tools.plot_line,
    "plot_bar": matplotlib_tools.plot_bar,
    "plot_pie": matplotlib_tools.plot_pie,
    "plot_scatter": matplotlib_tools.plot_scatter,
    "plot_histogram": matplotlib_tools.plot_histogram,

    # === Ant Design Charts ===
    "generate_chart_spec": antd_charts.generate_line_chart,

    # === Markitdown ===
    "markitdown_html_to_md": markitdown.html_to_markdown,
    "markitdown_url_to_md": markitdown.url_to_markdown,
    "markitdown_file_to_md": markitdown.extract_text_from_file,
    "markitdown_md_to_html": markitdown.markdown_to_html,

    # === Sequential Thinking ===
    "thinking_session_create": sequential_thinking.create_session,
    "thinking_step": sequential_thinking.think,
    "thinking_revoke": sequential_thinking.revise,
    "thinking_summary": sequential_thinking.get_session,
    "analyze_problem": sequential_thinking.analyze_problem,

    # === Research ===
    "research_start": gpt_researcher.start_research,
    "research_add_source": gpt_researcher.add_research_source,
    "research_complete": gpt_researcher.complete_research,
    "research_report": gpt_researcher.get_research_report,

    # === YouTube Transcript ===
    "youtube_transcript": youtube_transcript.get_transcript_from_url,
    "youtube_transcript_timed": youtube_transcript.get_transcript_with_timestamp,
    "youtube_search": youtube_transcript.search_youtube,
    "youtube_video_info": youtube_transcript.get_video_info,
    "youtube_batch_transcribe": youtube_transcript.batch_transcribe,
    "youtube_summarize": youtube_transcript.summarize_transcript,

    # === Engineering Intelligence ===
    "engi_task_classify": engi_intelligence.task_classify,
    "engi_repo_scope_find": engi_intelligence.repo_scope_find,
    "engi_flow_summarize": engi_intelligence.flow_summarize,
    "engi_bug_trace": engi_intelligence.bug_trace_compact,
    "engi_implementation_plan": engi_intelligence.implementation_plan,
    "engi_poc_plan": engi_intelligence.poc_plan,
    "engi_impact_analyze": engi_intelligence.impact_analyze,
    "engi_test_select": engi_intelligence.test_select,
    "engi_doc_context_build": engi_intelligence.doc_context_build,
    "engi_doc_update_plan": engi_intelligence.doc_update_plan,
    "engi_memory_checkpoint": engi_intelligence.memory_checkpoint,
    "engi_memory_restore": engi_intelligence.memory_restore,

    # === System ===
    "run_command": run_command.run_command,
}


class MCPServer:
    """MCP Server with STDIO and TCP support."""

    def __init__(self):
        self.writer = None

    def send_response(self, response: dict, writer=None) -> None:
        """Send a JSON-RPC response."""
        msg = json.dumps(response) + "\n"
        if writer:
            writer.write(msg.encode())
            writer.drain()
        else:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def send_notification(self, method: str, params: dict | None = None, writer=None) -> None:
        """Send a JSON-RPC notification (no id)."""
        msg: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params:
            msg["params"] = params
        msg_str = json.dumps(msg) + "\n"
        if writer:
            writer.write(msg_str.encode())
            writer.drain()
        else:
            sys.stdout.write(msg_str)
            sys.stdout.flush()

    def handle_initialize(self, params: dict) -> dict:
        """Handle MCP initialize handshake."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "mcp-server-unified",
                "version": "2.0.0",
            },
        }

    def handle_tools_list(self, params: dict) -> dict:
        """Handle tools/list."""
        return {"tools": TOOL_DEFINITIONS}

    def handle_tools_call(self, params: dict) -> dict:
        """Handle tools/call."""
        name: str = params.get("name", "")
        arguments: dict = params.get("arguments", {})

        if name not in TOOL_CALLABLES:
            return {
                "content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {name}"})}],
                "isError": True,
            }

        try:
            tool_func = TOOL_CALLABLES[name]

            if asyncio.iscoroutinefunction(tool_func):
                result = asyncio.run(tool_func(**arguments))
            else:
                result = tool_func(**arguments)

            return {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "isError": False,
            }

        except TypeError as e:
            return {
                "content": [{"type": "text", "text": json.dumps({"error": f"Invalid arguments: {e}"})}],
                "isError": True,
            }
        except Exception as e:
            log.exception("Tool '%s' raised an exception", name)
            return {
                "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                "isError": True,
            }

    def handle_request(self, method: str, params: dict, msg_id: int | str | None, writer=None) -> None:
        """Route a JSON-RPC request."""
        if method == "initialize":
            result = self.handle_initialize(params)
            self.send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result,
            }, writer)
            self.send_notification("notifications/initialized", {}, writer)
            return

        handler = {
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tools_call,
        }.get(method)

        if handler is None:
            self.send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }, writer)
            return

        try:
            result = handler(params)
            self.send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result,
            }, writer)
        except Exception as e:
            log.exception("Handler for '%s' raised an exception", method)
            self.send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32603, "message": str(e)},
            }, writer)

    async def handle_tcp_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle a TCP client connection."""
        addr = writer.get_extra_info('peername')
        log.warning(f"Client connected from {addr}")

        try:
            while True:
                line = await reader.readline()
                if not line:
                    break

                line = line.decode().strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if msg.get("method") in ("initialize", "tools/list", "tools/call"):
                    self.handle_request(
                        method=msg["method"],
                        params=msg.get("params", {}),
                        msg_id=msg.get("id"),
                        writer=writer,
                    )
                elif msg.get("method", "").startswith("notifications/"):
                    pass

        except Exception as e:
            log.exception(f"Client error: {addr}")
        finally:
            writer.close()
            await writer.wait_closed()
            log.warning(f"Client disconnected: {addr}")

    async def run_tcp(self, host: str = "0.0.0.0", port: int = 7710) -> None:
        """Run server in TCP mode for remote access."""
        server = await asyncio.start_server(
            self.handle_tcp_client,
            host,
            port
        )

        addr = server.sockets[0].getsockname()
        log.warning(f"MCP TCP Server running on {addr}")
        log.warning(f"Connect: nc {addr[0]} {addr[1]}")
        log.warning(f"Or use: python -m mcp_server --tcp {addr[1]}")

        async with server:
            await server.serve_forever()

    def run_stdio(self) -> None:
        """Run server in STDIO mode (default for Claude Code)."""
        log.warning(f"MCP Unified Server starting with {len(TOOL_CALLABLES)} tools")

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            if msg.get("method") in ("initialize", "tools/list", "tools/call"):
                self.handle_request(
                    method=msg["method"],
                    params=msg.get("params", {}),
                    msg_id=msg.get("id"),
                )
            elif msg.get("method", "").startswith("notifications/"):
                pass


def run() -> None:
    """Main entry point."""
    mcp = MCPServer()
    port = int(os.environ.get("MCP_SERVER_PORT", "0"))  # 0 = STDIO mode

    if port > 0:
        # TCP mode for remote access
        asyncio.run(mcp.run_tcp(port=port))
    else:
        # STDIO mode (default)
        mcp.run_stdio()


if __name__ == "__main__":
    run()
