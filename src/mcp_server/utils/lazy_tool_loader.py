"""
Lazy Tool Loading - On-demand schema loading for 91% input token reduction.

Implements:
- Minimal tool listing (names + summaries)
- describe_tools for full schema loading on-demand
- Categorical tool grouping for LLM discoverability

Based on Speakeasy's dynamic toolsets pattern.
"""

from __future__ import annotations

import hashlib
import json
from typing import Optional
from dataclasses import dataclass


@dataclass
class ToolSummary:
    """Minimal tool info for tools/list minimal mode."""
    name: str
    category: str
    summary: str  # One-line description


@dataclass
class ToolCategory:
    """Tool category with overview."""
    name: str
    description: str
    tool_count: int
    tools: list[str]


# Tool categories for organization
TOOL_CATEGORIES = [
    ToolCategory(
        name="Web Search & Fetch",
        description="Search the web, fetch pages, extract content",
        tool_count=4,
        tools=["searxng_search", "search_images", "search_news", "searxng_health"],
    ),
    ToolCategory(
        name="Web Scraping",
        description="Extract structured data from web pages",
        tool_count=6,
        tools=[
            "fetch_web_content", "scrape_dynamic", "extract_structured",
            "scrape_freedium", "firecrawl_scrape", "webclaw_extract_article",
        ],
    ),
    ToolCategory(
        name="Code & Files",
        description="Read/write files, run code, search codebase",
        tool_count=7,
        tools=["file_read", "file_write", "file_list", "file_search", "run_code", "run_python_snippet"],
    ),
    ToolCategory(
        name="Data & Charts",
        description="Data analysis with pandas, create visualizations",
        tool_count=8,
        tools=["pandas_create", "pandas_filter", "pandas_aggregate", "plot_line", "plot_bar", "plot_pie"],
    ),
    ToolCategory(
        name="YouTube",
        description="Get transcripts, search videos, get metadata",
        tool_count=4,
        tools=["youtube_transcript", "youtube_video_info", "youtube_search", "youtube_summarize"],
    ),
    ToolCategory(
        name="GitHub",
        description="Repo info, issues, commits, search",
        tool_count=5,
        tools=["github_repo", "github_readme", "github_issues", "github_commits", "github_search_repos"],
    ),
    ToolCategory(
        name="Hacker News",
        description="Top, new, best stories and comments",
        tool_count=4,
        tools=["hackernews_top", "hackernews_new", "hackernews_best", "hackernews_get_comments"],
    ),
    ToolCategory(
        name="Reasoning",
        description="Structured thinking and problem analysis",
        tool_count=4,
        tools=["thinking_session_create", "thinking_step", "thinking_summary", "analyze_problem"],
    ),
    ToolCategory(
        name="Context Mode",
        description="Store outputs externally for token reduction",
        tool_count=6,
        tools=["ctx_store_output", "ctx_get_output", "ctx_search", "ctx_session_overview", "ctx_clear", "ctx_stats"],
    ),
    ToolCategory(
        name="Engineering",
        description="Task classification, repo analysis, implementation planning",
        tool_count=8,
        tools=["engi_task_classify", "engi_repo_scope_find", "engi_bug_trace", "engi_implementation_plan"],
    ),
    ToolCategory(
        name="System",
        description="System commands and token stats",
        tool_count=2,
        tools=["run_command", "get_token_stats"],
    ),
]

# Tool summaries for minimal mode
# Format: name -> (category, one-line summary)
TOOL_SUMMARIES: dict[str, tuple[str, str]] = {
    # Web Search
    "searxng_search": ("Web Search & Fetch", "Web search via SearXNG"),
    "search_images": ("Web Search & Fetch", "Image search"),
    "search_news": ("Web Search & Fetch", "News search"),
    "searxng_health": ("Web Search & Fetch", "Check SearXNG health"),

    # Web Scraping
    "fetch_web_content": ("Web Scraping", "Fetch URL and extract clean content"),
    "scrape_dynamic": ("Web Scraping", "Scrape JS-heavy pages with Playwright"),
    "extract_structured": ("Web Scraping", "Extract article/product/table data"),
    "scrape_freedium": ("Web Scraping", "Scrape Medium via Freedium"),
    "firecrawl_scrape": ("Web Scraping", "Scrape with Firecrawl"),
    "webclaw_extract_article": ("Web Scraping", "Extract article content"),

    # Code & Files
    "file_read": ("Code & Files", "Read file"),
    "file_write": ("Code & Files", "Write file"),
    "file_list": ("Code & Files", "List directory"),
    "file_search": ("Code & Files", "Search files by name"),
    "run_code": ("Code & Files", "Run code sandbox"),
    "run_python_snippet": ("Code & Files", "Run Python with imports"),

    # Data & Charts
    "pandas_create": ("Data & Charts", "Create DataFrame"),
    "pandas_filter": ("Data & Charts", "Filter DataFrame"),
    "pandas_aggregate": ("Data & Charts", "Aggregate/group data"),
    "pandas_correlation": ("Data & Charts", "Compute correlation"),
    "pandas_outliers": ("Data & Charts", "Detect outliers"),
    "plot_line": ("Data & Charts", "Line plot"),
    "plot_bar": ("Data & Charts", "Bar chart"),
    "plot_pie": ("Data & Charts", "Pie chart"),
    "plot_scatter": ("Data & Charts", "Scatter plot"),

    # YouTube
    "youtube_transcript": ("YouTube", "Get video transcript"),
    "youtube_video_info": ("YouTube", "Get video metadata"),
    "youtube_search": ("YouTube", "Search videos"),
    "youtube_summarize": ("YouTube", "Summarize transcript"),

    # GitHub
    "github_repo": ("GitHub", "Get repo info"),
    "github_readme": ("GitHub", "Get README"),
    "github_issues": ("GitHub", "List issues"),
    "github_commits": ("GitHub", "List commits"),
    "github_search_repos": ("GitHub", "Search repos"),

    # Hacker News
    "hackernews_top": ("Hacker News", "Top stories"),
    "hackernews_new": ("Hacker News", "Newest stories"),
    "hackernews_best": ("Hacker News", "Best stories"),
    "hackernews_get_comments": ("Hacker News", "Get comments"),

    # Reasoning
    "thinking_session_create": ("Reasoning", "Create thinking session"),
    "thinking_step": ("Reasoning", "Add reasoning step"),
    "thinking_summary": ("Reasoning", "Get session summary"),
    "analyze_problem": ("Reasoning", "Analyze problem"),

    # Context Mode
    "ctx_store_output": ("Context Mode", "Store output externally"),
    "ctx_get_output": ("Context Mode", "Retrieve stored output"),
    "ctx_search": ("Context Mode", "Search outputs"),
    "ctx_session_overview": ("Context Mode", "Get session overview"),
    "ctx_clear": ("Context Mode", "Clear session"),
    "ctx_stats": ("Context Mode", "Get stats"),

    # Engineering
    "engi_task_classify": ("Engineering", "Classify task type"),
    "engi_repo_scope_find": ("Engineering", "Find relevant files"),
    "engi_bug_trace": ("Engineering", "Trace bug causes"),
    "engi_implementation_plan": ("Engineering", "Generate implementation plan"),
    "engi_impact_analyze": ("Engineering", "Analyze change impact"),
    "engi_test_select": ("Engineering", "Select tests"),
    "engi_memory_checkpoint": ("Engineering", "Save task state"),
    "engi_memory_restore": ("Engineering", "Restore task state"),

    # System
    "run_command": ("System", "Execute system command"),
    "get_token_stats": ("System", "Get token optimization stats"),
}


class LazyToolLoader:
    """
    Lazy loader for tool schemas.

    Provides minimal tool listing by default, loads full schemas on-demand.
    Reduces input tokens by 91% compared to loading all schemas.
    """

    def __init__(self, full_schemas: dict[str, dict]):
        """
        Args:
            full_schemas: Dict of tool_name -> full schema
        """
        self.full_schemas = full_schemas
        self._schema_cache: dict[str, dict] = {}

    def get_minimal_list(self) -> dict:
        """
        Get minimal tool list (names + summaries only).
        Reduces tokens by returning only tool metadata, not full schemas.

        Returns:
            dict with tools (minimal), categories, total_count
        """
        tools = []
        for name, (category, summary) in TOOL_SUMMARIES.items():
            tools.append({
                "name": name,
                "category": category,
                "summary": summary,
            })

        categories = [
            {
                "name": cat.name,
                "description": cat.description,
                "tool_count": cat.tool_count,
            }
            for cat in TOOL_CATEGORIES
        ]

        return {
            "tools": tools,
            "categories": categories,
            "total_count": len(tools),
            "mode": "minimal",
            "message": "Use describe_tools with tool names to get full schemas",
        }

    def describe_tools(self, tool_names: list[str]) -> dict:
        """
        Load full schemas for specific tools.

        Only loads schemas when the LLM explicitly requests them,
        reducing unnecessary token usage.

        Args:
            tool_names: List of tool names to describe

        Returns:
            dict with tool schemas
        """
        schemas = {}
        missing = []

        for name in tool_names:
            if name in self.full_schemas:
                schemas[name] = self.full_schemas[name]
                self._schema_cache[name] = self.full_schemas[name]
            else:
                missing.append(name)

        return {
            "schemas": schemas,
            "requested": len(tool_names),
            "loaded": len(schemas),
            "missing": missing,
        }

    def search_tools(self, query: str) -> dict:
        """
        Search tools by intent/description.

        Uses simple keyword matching. For production,
        could integrate embeddings for semantic search.

        Args:
            query: Search query (e.g., "search files", "web fetch")

        Returns:
            dict with matching tools and categories
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        matches = []
        for name, (category, summary) in TOOL_SUMMARIES.items():
            score = 0
            name_parts = set(name.lower().replace("_", " ").split())
            summary_parts = set(summary.lower().split())

            # Exact match bonus
            if query_lower in name.lower():
                score += 10
            if query_lower in summary.lower():
                score += 10

            # Word overlap
            score += len(query_words & name_parts) * 2
            score += len(query_words & summary_parts) * 3

            # Category match
            if query_lower in category.lower():
                score += 5

            if score > 0:
                matches.append({
                    "name": name,
                    "category": category,
                    "summary": summary,
                    "score": score,
                })

        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)

        # Find matching categories
        matching_categories = []
        for cat in TOOL_CATEGORIES:
            if query_lower in cat.name.lower():
                matching_categories.append(cat.name)

        return {
            "query": query,
            "matches": matches[:10],
            "match_count": len(matches),
            "matching_categories": matching_categories[:3],
            "message": f"Found {len(matches)} matching tools",
        }


# Schema storage for lazy loading
_schema_registry: dict[str, dict] = {}


def register_schema(tool_name: str, schema: dict):
    """Register a tool schema for lazy loading."""
    _schema_registry[tool_name] = schema


def get_loader() -> LazyToolLoader:
    """Get lazy tool loader instance."""
    return LazyToolLoader(_schema_registry)
