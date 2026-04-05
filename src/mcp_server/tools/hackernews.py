"""Hacker News MCP integration - Fetch HN articles, comments, and user data."""

from __future__ import annotations

import os
import json
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
CACHE_TTL = int(os.environ.get("HN_CACHE_TTL", "300"))  # 5 minutes


def _fetch_json(endpoint: str) -> Optional[dict]:
    """Fetch JSON from HN API."""
    if not HTTpx_AVAILABLE:
        return None
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{HN_API_BASE}/{endpoint}")
            response.raise_for_status()
            return response.json()
    except Exception:
        return None


def get_top_stories(limit: int = 10) -> dict:
    """Get top Hacker News stories."""
    story_ids = _fetch_json("topstories.json")
    if not story_ids:
        return {"stories": [], "error": "Failed to fetch stories"}

    stories = []
    for story_id in story_ids[:limit]:
        story = _fetch_json(f"item/{story_id}.json")
        if story:
            stories.append({
                "id": story.get("id"),
                "title": story.get("title", ""),
                "url": story.get("url", ""),
                "score": story.get("score", 0),
                "by": story.get("by", ""),
                "time": story.get("time", 0),
                "descendants": story.get("descendants", 0),
                "type": story.get("type", ""),
            })

    return {"stories": stories, "error": None}


def get_new_stories(limit: int = 10) -> dict:
    """Get newest Hacker News stories."""
    story_ids = _fetch_json("newstories.json")
    if not story_ids:
        return {"stories": [], "error": "Failed to fetch stories"}

    stories = []
    for story_id in story_ids[:limit]:
        story = _fetch_json(f"item/{story_id}.json")
        if story:
            stories.append({
                "id": story.get("id"),
                "title": story.get("title", ""),
                "url": story.get("url", ""),
                "score": story.get("score", 0),
                "by": story.get("by", ""),
                "time": story.get("time", 0),
                "descendants": story.get("descendants", 0),
                "type": story.get("type", ""),
            })

    return {"stories": stories, "error": None}


def get_best_stories(limit: int = 10) -> dict:
    """Get best Hacker News stories."""
    story_ids = _fetch_json("beststories.json")
    if not story_ids:
        return {"stories": [], "error": "Failed to fetch stories"}

    stories = []
    for story_id in story_ids[:limit]:
        story = _fetch_json(f"item/{story_id}.json")
        if story:
            stories.append({
                "id": story.get("id"),
                "title": story.get("title", ""),
                "url": story.get("url", ""),
                "score": story.get("score", 0),
                "by": story.get("by", ""),
                "time": story.get("time", 0),
                "descendants": story.get("descendants", 0),
                "type": story.get("type", ""),
            })

    return {"stories": stories, "error": None}


def get_ask_hn(limit: int = 10) -> dict:
    """Get Ask HN stories."""
    story_ids = _fetch_json("askstories.json")
    if not story_ids:
        return {"stories": [], "error": "Failed to fetch stories"}

    stories = []
    for story_id in story_ids[:limit]:
        story = _fetch_json(f"item/{story_id}.json")
        if story:
            stories.append({
                "id": story.get("id"),
                "title": story.get("title", ""),
                "text": story.get("text", ""),
                "url": story.get("url", ""),
                "score": story.get("score", 0),
                "by": story.get("by", ""),
                "time": story.get("time", 0),
                "descendants": story.get("descendants", 0),
            })

    return {"stories": stories, "error": None}


def get_show_hn(limit: int = 10) -> dict:
    """Get Show HN stories."""
    story_ids = _fetch_json("showstories.json")
    if not story_ids:
        return {"stories": [], "error": "Failed to fetch stories"}

    stories = []
    for story_id in story_ids[:limit]:
        story = _fetch_json(f"item/{story_id}.json")
        if story:
            stories.append({
                "id": story.get("id"),
                "title": story.get("title", ""),
                "url": story.get("url", ""),
                "score": story.get("score", 0),
                "by": story.get("by", ""),
                "time": story.get("time", 0),
                "descendants": story.get("descendants", 0),
            })

    return {"stories": stories, "error": None}


def get_story_comments(story_id: int, limit: int = 20) -> dict:
    """Get comments for a story."""
    story = _fetch_json(f"item/{story_id}.json")
    if not story:
        return {"comments": [], "error": "Story not found"}

    comments = []
    kids = story.get("kids", [])[:limit]

    for comment_id in kids:
        comment = _fetch_json(f"item/{comment_id}.json")
        if comment:
            comments.append({
                "id": comment.get("id"),
                "text": comment.get("text", ""),
                "by": comment.get("by", ""),
                "time": comment.get("time", 0),
                "kids": comment.get("kids", [])[:5],  # Nested comments
                "deleted": comment.get("deleted", False),
                "dead": comment.get("dead", False),
            })

    return {
        "story": {
            "id": story.get("id"),
            "title": story.get("title", ""),
            "url": story.get("url", ""),
        },
        "comments": comments,
        "error": None,
    }


def get_user(username: str) -> dict:
    """Get Hacker News user info."""
    user = _fetch_json(f"user/{username}.json")
    if not user:
        return {"user": None, "error": "User not found"}

    return {
        "user": {
            "id": user.get("id", ""),
            "created": user.get("created", 0),
            "karma": user.get("karma", 0),
            "about": user.get("about", ""),
            "submitted": user.get("submitted", [])[:20],  # Limit submissions
        },
        "error": None,
    }


def search_hn(query: str, limit: int = 10) -> dict:
    """Search HN stories (basic title matching via top stories)."""
    top = get_top_stories(limit=50)
    if top.get("error"):
        return {"stories": [], "error": top["error"]}

    query_lower = query.lower()
    matches = [
        s for s in top.get("stories", [])
        if query_lower in s.get("title", "").lower()
    ]

    return {"stories": matches[:limit], "error": None}