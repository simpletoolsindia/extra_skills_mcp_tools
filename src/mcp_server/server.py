"""
MCP Server — Unified STDIO-based Model Context Protocol server.
35+ tools for local LLM agentic workflows.
"""

from __future__ import annotations

import json
import sys
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

    # === System ===
    "run_command": run_command.run_command,
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
            "name": "mcp-server-unified",
            "version": "2.0.0",
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
            "content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {name}"})}],
            "isError": True,
        }

    try:
        tool_func = TOOL_CALLABLES[name]

        # Handle async functions
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


def handle_request(method: str, params: dict, msg_id: int | str | None) -> None:
    """Route a JSON-RPC request and send the response."""
    if method == "initialize":
        result = handle_initialize(params)
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result,
        })
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
    log.warning(f"MCP Unified Server starting with {len(TOOL_CALLABLES)} tools")

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
            pass


if __name__ == "__main__":
    run()