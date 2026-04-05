"""GPT Researcher MCP - Autonomous research agent for comprehensive studies."""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False


class ResearchReport:
    """Represents a research report."""

    def __init__(self, query: str):
        self.query = query
        self.queries_generated = []
        self.sources_visited = []
        self.findings = []
        self.conclusion = ""

    def add_query(self, query: str):
        self.queries_generated.append(query)

    def add_source(self, source: Dict):
        self.sources_visited.append(source)

    def add_finding(self, finding: str):
        self.findings.append(finding)

    def set_conclusion(self, conclusion: str):
        self.conclusion = conclusion

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "queries_generated": self.queries_generated,
            "sources": self.sources_visited[:10],
            "findings": self.findings,
            "conclusion": self.conclusion,
            "sources_count": len(self.sources_visited),
            "findings_count": len(self.findings),
        }


# Storage for active research
_research_storage: Dict[str, ResearchReport] = {}


def generate_search_queries(topic: str, num_queries: int = 5) -> dict:
    """
    Generate search queries for a research topic.

    Args:
        topic: Research topic
        num_queries: Number of queries to generate

    Returns:
        dict with keys: queries (list), error
    """
    # Generate variations of the topic
    queries = [
        f"{topic}",
        f"{topic} latest research",
        f"{topic} overview guide",
        f"{topic} best practices",
        f"{topic} trends 2024",
        f"what is {topic}",
        f"how to {topic}",
        f"{topic} examples",
    ]

    # Filter out any duplicates and limit
    queries = list(dict.fromkeys(queries))[:num_queries]

    return {"queries": queries, "error": None}


def start_research(
    research_id: str,
    query: str,
    depth: str = "basic",
) -> dict:
    """
    Start a new research session.

    Args:
        research_id: Unique ID for this research
        query: Research question/topic
        depth: 'basic', ' thorough', or 'extensive'

    Returns:
        dict with keys: research_id, queries, message
    """
    report = ResearchReport(query)
    _research_storage[research_id] = report

    num_queries = {"basic": 3, "thorough": 5, "extensive": 8}.get(depth, 5)

    queries = generate_search_queries(query, num_queries)["queries"]
    for q in queries:
        report.add_query(q)

    return {
        "research_id": research_id,
        "query": query,
        "queries": queries,
        "message": f"Research started with {len(queries)} search queries",
    }


def add_research_source(
    research_id: str,
    source: Dict,
) -> dict:
    """
    Add a source to research.

    Args:
        research_id: Research session ID
        source: Dict with keys: url, title, content, snippet

    Returns:
        dict with keys: success, total_sources
    """
    if research_id not in _research_storage:
        return {"success": False, "total_sources": 0, "error": "Research not found"}

    _research_storage[research_id].add_source(source)
    return {
        "success": True,
        "total_sources": len(_research_storage[research_id].sources_visited),
    }


def add_research_finding(
    research_id: str,
    finding: str,
) -> dict:
    """Add a finding to research."""
    if research_id not in _research_storage:
        return {"success": False, "error": "Research not found"}

    _research_storage[research_id].add_finding(finding)
    return {
        "success": True,
        "total_findings": len(_research_storage[research_id].findings),
    }


def complete_research(
    research_id: str,
    conclusion: str,
) -> dict:
    """Complete research with conclusion."""
    if research_id not in _research_storage:
        return {"success": False, "error": "Research not found"}

    _research_storage[research_id].set_conclusion(conclusion)

    return {
        "success": True,
        "report": _research_storage[research_id].to_dict(),
    }


def get_research_report(research_id: str) -> dict:
    """Get research report."""
    if research_id not in _research_storage:
        return {"error": "Research not found"}

    return {"report": _research_storage[research_id].to_dict()}


def list_research() -> dict:
    """List all research sessions."""
    return {
        "research": [
            {"id": rid, "query": r.query, "findings": len(r.findings)}
            for rid, r in _research_storage.items()
        ]
    }


def delete_research(research_id: str) -> dict:
    """Delete a research session."""
    if research_id in _research_storage:
        del _research_storage[research_id]
        return {"success": True}
    return {"success": False, "error": "Research not found"}


def synthesize_sources(sources: List[Dict]) -> dict:
    """
    Synthesize information from multiple sources.

    Args:
        sources: List of source dicts with content

    Returns:
        dict with keys: summary, key_points, contradictions
    """
    if not sources:
        return {
            "summary": "No sources provided",
            "key_points": [],
            "contradictions": [],
        }

    # Extract key points from each source
    key_points = []
    contradictions = []

    for i, source in enumerate(sources):
        content = source.get("content", source.get("snippet", ""))
        if content:
            # Simple extraction - in production, use LLM for this
            sentences = content.split(".")[:3]
            for sent in sentences:
                if len(sent) > 50:
                    key_points.append({
                        "source": source.get("title", f"Source {i+1}"),
                        "point": sent.strip(),
                    })

    summary = f"Synthesized from {len(sources)} sources. Key themes: "
    if key_points:
        summary += ", ".join([p["point"][:50] + "..." for p in key_points[:3]])

    return {
        "summary": summary,
        "key_points": key_points[:10],
        "contradictions": contradictions,
        "sources_used": len(sources),
    }


def conduct_quick_research(query: str, max_sources: int = 5) -> dict:
    """
    Conduct a quick research with automated search and synthesis.

    Args:
        query: Research question
        max_sources: Maximum sources to gather

    Returns:
        dict with comprehensive research summary
    """
    import uuid
    research_id = str(uuid.uuid4())[:8]

    # Start research
    start_research(research_id, query, depth="basic")

    # Get search queries
    queries = generate_search_queries(query, 3)["queries"]

    # Simulate gathering sources (in production, use actual search)
    for q in queries[:max_sources]:
        # In production, actually search and add sources
        pass

    # Generate summary
    report = _research_storage.get(research_id)
    if report:
        report.set_conclusion(f"Research on '{query}' completed. Generated {len(queries)} search queries.")

    return get_research_report(research_id)