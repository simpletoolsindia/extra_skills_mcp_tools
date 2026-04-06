"""
Context Mode MCP Tools - Store tool outputs externally for 98% token reduction.

Usage:
- ctx_store_output: Store a tool's output externally
- ctx_get_output: Retrieve stored output by reference
- ctx_search: Search stored outputs
- ctx_session_summary: Get session overview
- ctx_clear: Clear session outputs
"""

from __future__ import annotations

import json
from typing import Optional, Any

from ..utils.context_store import (
    get_context_store,
    ToolOutputRef,
    ContextStore,
)


def store_output(
    tool_name: str,
    arguments: dict,
    output: Any,
    session_id: str = "default",
    call_id: Optional[str] = None,
    max_preview: int = 500,
) -> dict:
    """
    Store tool output externally, return lightweight reference.

    Use this to store results that would consume too many tokens.
    The LLM receives a small reference instead of full output.

    Args:
        tool_name: Name of the tool
        arguments: Tool arguments
        output: Tool output to store
        session_id: Session identifier (default: "default")
        call_id: Optional custom call ID
        max_preview: Max chars in preview (default: 500)

    Returns:
        dict with reference and stats:
        {
            "success": true,
            "ref": "@ctx:session_id:call_id",
            "call_id": "abc123",
            "size_bytes": 1024,
            "preview": "first 500 chars...",
            "truncated": false
        }
    """
    store = get_context_store()

    ref = store.store(
        tool_name=tool_name,
        arguments=arguments,
        output=output,
        call_id=call_id,
        session_id=session_id,
        max_preview=max_preview,
    )

    return {
        "success": True,
        "ref": f"@ctx:{ref.cache_key}",
        "call_id": ref.call_id,
        "tool_name": ref.tool_name,
        "size_bytes": ref.size_bytes,
        "preview": ref.preview,
        "truncated": ref.truncated,
        "message": "Use ctx_get_output with call_id to retrieve full output",
    }


def get_stored_output(call_id: str) -> dict:
    """
    Retrieve full output from external storage.

    Args:
        call_id: The call ID returned from store_output

    Returns:
        dict with tool_name, arguments, output, truncated status
    """
    store = get_context_store()
    result = store.retrieve(call_id)

    if result:
        return {
            "found": True,
            "tool_name": result["tool_name"],
            "arguments": result["arguments"],
            "output": result["output"],
            "truncated": result["truncated"],
            "created_at": result["created_at"],
        }
    else:
        return {
            "found": False,
            "error": f"No output found for call_id: {call_id}",
        }


def search_outputs(
    query: str,
    session_id: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    Search stored outputs using full-text search.

    Args:
        query: Search query
        session_id: Optional session filter
        limit: Max results (default: 10)

    Returns:
        dict with matching results
    """
    store = get_context_store()
    results = store.search(query, session_id, limit)

    return {
        "query": query,
        "session_id": session_id,
        "count": len(results),
        "results": results,
    }


def get_session_overview(
    session_id: str = "default",
    limit: int = 20,
) -> dict:
    """
    Get overview of all outputs in a session.

    Args:
        session_id: Session identifier (default: "default")
        limit: Max outputs to return

    Returns:
        dict with session summary and recent outputs
    """
    store = get_context_store()
    outputs = store.get_session_outputs(session_id, limit)
    stats = store.get_stats()

    # Get session-specific stats
    session_outputs = [o for o in outputs]
    session_bytes = sum(
        len(json.dumps(o["output"], ensure_ascii=False).encode())
        for o in session_outputs
    )

    return {
        "session_id": session_id,
        "total_outputs": len(session_outputs),
        "total_bytes": session_bytes,
        "recent_outputs": [
            {
                "call_id": o["call_id"],
                "tool_name": o["tool_name"],
                "preview": json.dumps(o["output"], ensure_ascii=False)[:200],
                "truncated": o["truncated"],
            }
            for o in session_outputs[:10]
        ],
        "global_stats": stats,
    }


def clear_session(session_id: str) -> dict:
    """
    Clear all stored outputs for a session.

    Args:
        session_id: Session to clear

    Returns:
        dict with count of cleared outputs
    """
    store = get_context_store()
    count = store.clear_session(session_id)

    return {
        "session_id": session_id,
        "cleared_count": count,
        "message": f"Cleared {count} outputs from session {session_id}",
    }


def get_context_stats() -> dict:
    """
    Get Context Mode storage statistics.

    Returns:
        dict with storage stats and configuration
    """
    store = get_context_store()
    stats = store.get_stats()

    return {
        "context_mode": "enabled",
        "total_outputs_stored": stats["total_outputs"],
        "total_bytes": stats["total_bytes"],
        "truncated_count": stats["truncated_count"],
        "unique_tools": stats["unique_tools"],
        "unique_sessions": stats["unique_sessions"],
        "token_savings": f"~{stats['total_bytes'] // 1000}KB saved in context",
    }
