"""
Semantic Tool Search - Natural language tool discovery.

Provides natural language interface to tool discovery:
1. semantic_search: Find tools by describing what you want to do
2. semantic_describe: Get full schema for selected tools
3. semantic_execute: Execute with discovered tools

Uses keyword matching and embeddings-ready architecture.
"""

from __future__ import annotations

from typing import Optional
from dataclasses import dataclass

from ..schemas.trimmed_tool_schemas import ALL_TRIMMED_TOOLS


# Tool intent mappings for semantic search
# Maps user intents to tools
INTENT_MAPPINGS = {
    # Web searching
    "search the web": ["searxng_search"],
    "search web": ["searxng_search"],
    "look up": ["searxng_search"],
    "find information": ["searxng_search"],
    "google something": ["searxng_search"],
    "search for": ["searxng_search"],

    # Web fetching
    "fetch a page": ["fetch_web_content"],
    "get webpage": ["fetch_web_content"],
    "read url": ["fetch_web_content"],
    "scrape website": ["fetch_web_content", "scrape_dynamic", "webclaw_extract_article"],
    "extract content": ["fetch_web_content", "webclaw_extract_article", "extract_structured"],
    "get article": ["webclaw_extract_article"],

    # File operations
    "read file": ["file_read"],
    "write file": ["file_write"],
    "save file": ["file_write"],
    "list files": ["file_list"],
    "list directory": ["file_list"],
    "search files": ["file_search"],
    "find files": ["file_search"],

    # Code execution
    "run code": ["run_code", "run_python_snippet"],
    "execute code": ["run_code", "run_python_snippet"],
    "run python": ["run_python_snippet"],
    "test code": ["test_code_snippet"],
    "sandbox": ["run_code"],

    # Data analysis
    "create dataframe": ["pandas_create"],
    "filter data": ["pandas_filter"],
    "aggregate": ["pandas_aggregate"],
    "analyze data": ["pandas_filter", "pandas_aggregate", "pandas_correlation"],
    "find outliers": ["pandas_outliers"],
    "compute correlation": ["pandas_correlation"],

    # Visualization
    "plot": ["plot_line", "plot_bar", "plot_pie", "plot_scatter"],
    "chart": ["plot_line", "plot_bar", "plot_pie", "plot_scatter"],
    "create chart": ["plot_line", "plot_bar", "plot_pie", "plot_scatter"],
    "visualize": ["plot_line", "plot_bar", "plot_pie", "plot_scatter"],
    "line chart": ["plot_line"],
    "bar chart": ["plot_bar"],
    "pie chart": ["plot_pie"],
    "scatter plot": ["plot_scatter"],

    # YouTube
    "youtube transcript": ["youtube_transcript"],
    "get video transcript": ["youtube_transcript"],
    "youtube video": ["youtube_video_info", "youtube_search"],
    "search youtube": ["youtube_search"],
    "summarize video": ["youtube_summarize"],

    # GitHub
    "github repo": ["github_repo"],
    "get repo": ["github_repo"],
    "github issues": ["github_issues"],
    "github commits": ["github_commits"],
    "search github": ["github_search_repos"],
    "get readme": ["github_readme"],

    # Hacker News
    "hacker news": ["hackernews_top", "hackernews_new", "hackernews_best"],
    "hn stories": ["hackernews_top", "hackernews_new", "hackernews_best"],

    # Thinking
    "think": ["thinking_step", "analyze_problem"],
    "reason": ["thinking_step", "analyze_problem"],
    "analyze problem": ["analyze_problem"],
    "structured thinking": ["thinking_session_create", "thinking_step"],

    # Engineering
    "classify task": ["engi_task_classify"],
    "find relevant files": ["engi_repo_scope_find"],
    "implement": ["engi_implementation_plan"],
    "implementation plan": ["engi_implementation_plan"],
    "bug trace": ["engi_bug_trace"],
    "impact analysis": ["engi_impact_analyze"],
    "find tests": ["engi_test_select"],

    # Context mode
    "store output": ["ctx_store_output"],
    "external storage": ["ctx_store_output"],
    "reduce tokens": ["ctx_store_output"],

    # System
    "run command": ["run_command"],
    "execute command": ["run_command"],
    "system command": ["run_command"],
}


def _calculate_intent_score(intent: str, tool_name: str, tool_summary: str, tool_category: str) -> float:
    """Calculate relevance score between intent and tool."""
    score = 0.0
    intent_lower = intent.lower()

    # Direct tool name match
    if tool_name.replace("_", " ").lower() in intent_lower:
        score += 10

    # Intent match via mappings
    for pattern, tools in INTENT_MAPPINGS.items():
        if tool_name in tools:
            # Pattern in intent
            if pattern in intent_lower:
                score += 8
            # Intent in pattern
            if intent_lower in pattern:
                score += 6
            # Word overlap
            intent_words = set(intent_lower.split())
            pattern_words = set(pattern.split())
            overlap = len(intent_words & pattern_words)
            score += overlap * 2

    # Summary match
    summary_words = set(tool_summary.lower().split())
    intent_words = set(intent_lower.split())
    overlap = len(intent_words & summary_words)
    score += overlap * 3

    # Category match
    if intent_lower in tool_category.lower():
        score += 3

    # Partial word matches
    for word in intent_words:
        if word in tool_name.lower() and len(word) > 2:
            score += 1
        if word in tool_summary.lower() and len(word) > 2:
            score += 2

    return score


@dataclass
class ToolMatch:
    """Represents a tool match from semantic search."""
    name: str
    category: str
    summary: str
    score: float
    match_reason: str


class SemanticToolSearch:
    """
    Natural language tool discovery.

    Allows users to describe what they want to accomplish
    and matches it to appropriate tools.
    """

    def __init__(self):
        # Load tool metadata
        from ..utils.lazy_tool_loader import TOOL_SUMMARIES

        self.tool_summaries = TOOL_SUMMARIES

    def search(self, intent: str, limit: int = 10) -> list[ToolMatch]:
        """
        Find tools that match the user's intent.

        Args:
            intent: Natural language description of what to do
                   e.g., "I want to search the web", "run some Python code"
            limit: Max number of tools to return

        Returns:
            List of ToolMatch objects ranked by relevance
        """
        intent_lower = intent.lower()
        matches = []

        for tool_name, (category, summary) in self.tool_summaries.items():
            score = _calculate_intent_score(intent_lower, tool_name, summary, category)

            if score > 0:
                # Generate match reason
                reason = self._generate_match_reason(intent_lower, tool_name, summary)

                matches.append(ToolMatch(
                    name=tool_name,
                    category=category,
                    summary=summary,
                    score=score,
                    match_reason=reason,
                ))

        # Sort by score
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches[:limit]

    def _generate_match_reason(self, intent: str, tool_name: str, summary: str) -> str:
        """Generate human-readable match reason."""
        reasons = []

        # Check direct matches
        for pattern, tools in INTENT_MAPPINGS.items():
            if tool_name in tools and pattern in intent:
                reasons.append(f'Matches "{pattern}"')

        # Check category
        category_map = {
            "web": "Web Search & Fetch",
            "fetch": "Web Scraping",
            "scrape": "Web Scraping",
            "file": "Code & Files",
            "code": "Code & Files",
            "python": "Code & Files",
            "data": "Data & Charts",
            "plot": "Data & Charts",
            "chart": "Data & Charts",
            "youtube": "YouTube",
            "github": "GitHub",
            "hacker": "Hacker News",
            "think": "Reasoning",
            "engineering": "Engineering",
            "context": "Context Mode",
        }

        for keyword, category in category_map.items():
            if keyword in intent and category in self.tool_summaries.get(tool_name, ("", ""))[0]:
                reasons.append(f"Category: {category}")

        return "; ".join(reasons[:2]) if reasons else "Semantic match"


# Global instance
_semantic_search: Optional[SemanticToolSearch] = None


def get_semantic_search() -> SemanticToolSearch:
    """Get or create semantic search instance."""
    global _semantic_search
    if _semantic_search is None:
        _semantic_search = SemanticToolSearch()
    return _semantic_search


def semantic_search(intent: str, limit: int = 10) -> dict:
    """
    Search tools by describing what you want to do.

    This is the NATURAL way to find tools. Instead of browsing
    a list of tool names, describe your goal.

    Examples:
    - "I want to search the web for something"
    - "run some Python code"
    - "extract content from a webpage"
    - "create a chart"

    Args:
        intent: Natural language description of your goal
        limit: Max tools to return

    Returns:
        dict with matching tools, their categories, and match reasons
    """
    search = get_semantic_search()
    matches = search.search(intent, limit)

    if not matches:
        return {
            "intent": intent,
            "matches": [],
            "suggestions": [
                "Try being more specific about what you want to do",
                "e.g., 'search the web', 'run code', 'fetch a webpage'",
            ],
        }

    return {
        "intent": intent,
        "matches": [
            {
                "name": m.name,
                "category": m.category,
                "summary": m.summary,
                "score": round(m.score, 2),
                "reason": m.match_reason,
                "next_step": f"Use semantic_describe(['{m.name}']) to get the schema",
            }
            for m in matches
        ],
        "match_count": len(matches),
        "message": "Use semantic_describe to load schemas for the tools you need",
    }


def semantic_describe(tool_names: list[str]) -> dict:
    """
    Get full schemas for tools from semantic search results.

    This is step 2 of the 3-tool pattern:
    1. semantic_search -> find matching tools
    2. semantic_describe -> load their schemas
    3. semantic_execute -> run the tool

    Args:
        tool_names: List of tool names from search results

    Returns:
        dict with full schemas
    """
    from ..utils.lazy_tool_loader import TOOL_SUMMARIES

    # Check if tools exist
    valid_tools = []
    invalid_tools = []

    for name in tool_names:
        if name in TOOL_SUMMARIES:
            valid_tools.append(name)
        else:
            invalid_tools.append(name)

    # Get schemas
    schemas = {}
    for schema in ALL_TRIMMED_TOOLS:
        if schema.get("name") in valid_tools:
            schemas[schema["name"]] = schema

    return {
        "tools": valid_tools,
        "schemas": schemas,
        "loaded": len(schemas),
        "invalid_tools": invalid_tools,
        "next_step": "Use the tools directly - they now have full schemas",
        "alt_next_step": "Use semantic_execute for a guided execution",
    }


def semantic_execute(intent: str, **kwargs) -> dict:
    """
    Guided execution: search, describe, then execute.

    This combines the 3-tool pattern:
    1. semantic_search -> find matching tools
    2. semantic_describe -> load schemas
    3. Execute -> run the matched tool

    Args:
        intent: What you want to do
        **kwargs: Arguments for the tool (if auto-execution desired)

    Returns:
        dict with search results and optional execution
    """
    search = get_semantic_search()
    matches = search.search(intent, limit=3)

    if not matches:
        return {
            "error": f"No tools found for intent: {intent}",
            "suggestions": [
                "Try rephrasing your intent",
                "e.g., 'search the web', 'fetch content', 'run code'",
            ],
        }

    # Get best match
    best_match = matches[0]

    return {
        "intent": intent,
        "best_match": {
            "name": best_match.name,
            "category": best_match.category,
            "summary": best_match.summary,
            "score": round(best_match.score, 2),
        },
        "all_matches": [
            {
                "name": m.name,
                "summary": m.summary,
                "score": round(m.score, 2),
            }
            for m in matches
        ],
        "execution_hint": f"To execute, call '{best_match.name}' directly with your arguments",
        "schema_hint": f"First call semantic_describe(['{best_match.name}']) to see full schema",
    }
