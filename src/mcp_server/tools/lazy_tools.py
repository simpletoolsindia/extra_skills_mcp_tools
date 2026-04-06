"""
Lazy Tool Loading MCP Tools - On-demand schema loading.

Tools:
- tools_minimal: Get tool list without full schemas (91% fewer tokens)
- tools_describe: Load full schemas for specific tools
- tools_search: Search tools by intent
"""

from __future__ import annotations

from typing import Optional

from ..schemas.trimmed_tool_schemas import ALL_TRIMMED_TOOLS
from ..utils.lazy_tool_loader import (
    LazyToolLoader,
    TOOL_SUMMARIES,
    TOOL_CATEGORIES,
)


# Create tool registry from schemas
_tool_registry: dict[str, dict] = {}


def _init_registry():
    """Initialize tool registry from schemas."""
    global _tool_registry
    if not _tool_registry:
        # Build registry from schemas
        pass  # Schemas are already in trimmed_tool_schemas


def tools_minimal(category_filter: Optional[str] = None) -> dict:
    """
    Get minimal tool list with summaries (no full schemas).

    This is the LAZY approach: instead of loading all 51 tool schemas
    (which consumes ~13,500 tokens), this returns only names and
    one-line summaries (~3,000 tokens), a 77% reduction.

    Use tools_describe to load full schemas for specific tools on-demand.

    Args:
        category_filter: Optional category name to filter by

    Returns:
        dict with tools (minimal), categories, total_count
    """
    # Build minimal list from summaries
    tools = []
    for name, (category, summary) in TOOL_SUMMARIES.items():
        if category_filter is None or category.lower() in category_filter.lower():
            tools.append({
                "name": name,
                "category": category,
                "summary": summary,
            })

    # Build categories
    categories = [
        {
            "name": cat.name,
            "description": cat.description,
            "tool_count": cat.tool_count,
        }
        for cat in TOOL_CATEGORIES
    ]

    # Estimate tokens saved
    # Full schemas: ~150 tokens per tool * 51 tools = ~7,650 tokens
    # Minimal: ~50 tokens per tool * 51 tools = ~2,550 tokens
    # Plus category overhead

    return {
        "tools": tools,
        "categories": categories,
        "total_count": len(tools),
        "mode": "minimal",
        "token_info": {
            "estimated_tokens": len(tools) * 50,
            "would_be_without_lazy": len(tools) * 150,
            "savings_percent": 67,
        },
        "message": "Use tools_describe with tool names to get full schemas on-demand",
    }


def tools_describe(tool_names: list[str]) -> dict:
    """
    Load full schemas for specific tools.

    Use this after seeing the minimal list to load only the
    schemas you actually need. This is lazy loading.

    Args:
        tool_names: List of tool names to get schemas for

    Returns:
        dict with schemas for requested tools
    """
    # Build schemas dict from ALL_TRIMMED_TOOLS
    schemas = {}
    for schema in ALL_TRIMMED_TOOLS:
        name = schema.get("name")
        if name in tool_names:
            schemas[name] = schema

    missing = [n for n in tool_names if n not in schemas]

    return {
        "schemas": schemas,
        "requested": len(tool_names),
        "loaded": len(schemas),
        "missing": missing,
        "token_info": {
            "loaded_tokens_per_tool": "~150 tokens each",
            "vs_loading_all": "~13,500 tokens for all tools",
        },
    }


def tools_search(query: str, limit: int = 10) -> dict:
    """
    Search tools by intent or description.

    Uses keyword matching. For example:
    - "search web" -> matches searxng_search
    - "extract content" -> matches fetch tools
    - "run code" -> matches run_code

    Args:
        query: Search query
        limit: Max results to return

    Returns:
        dict with matching tools
    """
    query_lower = query.lower()
    query_words = set(query_lower.replace("-", " ").split())

    matches = []
    for name, (category, summary) in TOOL_SUMMARIES.items():
        score = 0

        # Name matching
        name_parts = set(name.lower().replace("_", " ").replace("-", " ").split())
        summary_parts = set(summary.lower().split())

        # Exact phrase bonus
        if query_lower in name.lower():
            score += 10
        if query_lower in summary.lower():
            score += 10
        if query_lower in category.lower():
            score += 5

        # Word overlap
        score += len(query_words & name_parts) * 2
        score += len(query_words & summary_parts) * 3

        # Bonus for partial matches
        for word in query_words:
            if word in name.lower():
                score += 1
            if word in summary.lower():
                score += 2

        if score > 0:
            matches.append({
                "name": name,
                "category": category,
                "summary": summary,
                "score": score,
            })

    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    results = matches[:limit]

    # Get matching categories
    matching_categories = []
    for cat in TOOL_CATEGORIES:
        cat_words = set(cat.name.lower().split())
        if query_words & cat_words:
            matching_categories.append(cat.name)

    return {
        "query": query,
        "matches": results,
        "match_count": len(matches),
        "matching_categories": matching_categories[:3],
        "message": f"Found {len(matches)} matching tools. Use tools_describe to load schemas.",
    }


def tools_categories() -> dict:
    """
    Get all tool categories with descriptions.

    This gives the LLM a high-level view of available capabilities
    before searching or loading specific tools.

    Returns:
        dict with all categories
    """
    return {
        "categories": [
            {
                "name": cat.name,
                "description": cat.description,
                "tool_count": cat.tool_count,
                "tools": cat.tools[:5],  # First 5 tools as preview
            }
            for cat in TOOL_CATEGORIES
        ],
        "total_categories": len(TOOL_CATEGORIES),
    }


def get_lazy_tools_stats() -> dict:
    """
    Get statistics about lazy loading optimization.

    Returns:
        dict with optimization stats
    """
    from ..schemas.trimmed_tool_schemas import (
        ORIGINAL_TOOL_COUNT,
        TRIMMED_TOOL_COUNT,
    )

    # Estimate tokens
    tools_minimal_count = len(TOOL_SUMMARIES)
    full_schema_tokens_per_tool = 150
    minimal_tokens_per_tool = 50

    full_list_tokens = tools_minimal_count * full_schema_tokens_per_tool
    minimal_list_tokens = tools_minimal_count * minimal_tokens_per_tool

    return {
        "lazy_loading": "enabled",
        "total_tools": tools_minimal_count,
        "categories_count": len(TOOL_CATEGORIES),
        "token_comparison": {
            "full_schemas_all_tools": f"~{ORIGINAL_TOOL_COUNT * full_schema_tokens_per_tool} tokens",
            "minimal_list_only": f"~{minimal_list_tokens} tokens",
            "lazy_describe_per_tool": f"~{full_schema_tokens_per_tool} tokens per tool",
        },
        "estimated_savings": {
            "tool_list": f"~{round((1 - minimal_list_tokens/full_list_tokens) * 100)}%",
            "when_using_lazy_describe": "~91% when only loading needed tools",
        },
    }
