"""GitHub MCP - Interact with GitHub repositories, issues, PRs, and more."""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _get_headers() -> dict:
    """Get headers for GitHub API."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MCP-Server/1.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def get_repo(owner: str, repo: str) -> dict:
    """Get repository information."""
    if not HTTpx_AVAILABLE:
        return {"repo": None, "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}",
                headers=_get_headers(),
            )
            response.raise_for_status()

        data = response.json()
        return {
            "repo": {
                "name": data.get("name"),
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "owner": data.get("owner", {}).get("login"),
                "language": data.get("language"),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "license": data.get("license", {}).get("name"),
                "url": data.get("html_url"),
                "default_branch": data.get("default_branch"),
                "created": data.get("created_at"),
                "updated": data.get("updated_at"),
                "topics": data.get("topics", [])[:10],
            },
            "error": None,
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"repo": None, "error": "Repository not found"}
        return {"repo": None, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"repo": None, "error": str(e)}


def get_readme(owner: str, repo: str) -> dict:
    """Get repository README."""
    if not HTTpx_AVAILABLE:
        return {"readme": "", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/readme",
                headers=_get_headers(),
            )
            response.raise_for_status()

        import base64
        content = response.json().get("content", "")
        # GitHub returns base64 encoded content
        decoded = base64.b64decode(content).decode("utf-8")

        return {"readme": decoded, "error": None}
    except Exception as e:
        return {"readme": "", "error": str(e)}


def list_issues(owner: str, repo: str, state: str = "open", limit: int = 20) -> dict:
    """List repository issues."""
    if not HTTpx_AVAILABLE:
        return {"issues": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/issues",
                headers=_get_headers(),
                params={"state": state, "per_page": limit},
            )
            response.raise_for_status()

        data = response.json()
        issues = []
        for item in data:
            # Skip pull requests (they're also issues in GitHub API)
            if "pull_request" in item:
                continue
            issues.append({
                "number": item.get("number"),
                "title": item.get("title"),
                "body": item.get("body", ""),
                "state": item.get("state"),
                "author": item.get("user", {}).get("login"),
                "labels": [l.get("name") for l in item.get("labels", [])],
                "created": item.get("created_at"),
                "updated": item.get("updated_at"),
                "comments": item.get("comments", 0),
                "url": item.get("html_url"),
            })

        return {"issues": issues, "error": None}
    except Exception as e:
        return {"issues": [], "error": str(e)}


def get_issue(owner: str, repo: str, issue_number: int) -> dict:
    """Get a specific issue."""
    if not HTTpx_AVAILABLE:
        return {"issue": None, "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}",
                headers=_get_headers(),
            )
            response.raise_for_status()

        data = response.json()
        return {
            "issue": {
                "number": data.get("number"),
                "title": data.get("title"),
                "body": data.get("body", ""),
                "state": data.get("state"),
                "author": data.get("user", {}).get("login"),
                "labels": [l.get("name") for l in data.get("labels", [])],
                "created": data.get("created_at"),
                "updated": data.get("updated_at"),
                "comments": data.get("comments", 0),
                "url": data.get("html_url"),
            },
            "error": None,
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"issue": None, "error": "Issue not found"}
        return {"issue": None, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"issue": None, "error": str(e)}


def search_repositories(query: str, limit: int = 10, sort: str = "stars") -> dict:
    """Search GitHub repositories."""
    if not HTTpx_AVAILABLE:
        return {"repos": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/search/repositories",
                headers=_get_headers(),
                params={"q": query, "sort": sort, "per_page": limit},
            )
            response.raise_for_status()

        data = response.json()
        repos = []
        for item in data.get("items", []):
            repos.append({
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "description": item.get("description"),
                "owner": item.get("owner", {}).get("login"),
                "language": item.get("language"),
                "stars": item.get("stargazers_count", 0),
                "url": item.get("html_url"),
            })

        return {"repos": repos, "error": None}
    except Exception as e:
        return {"repos": [], "error": str(e)}


def get_contributors(owner: str, repo: str, limit: int = 20) -> dict:
    """Get repository contributors."""
    if not HTTpx_AVAILABLE:
        return {"contributors": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/contributors",
                headers=_get_headers(),
                params={"per_page": limit},
            )
            response.raise_for_status()

        data = response.json()
        contributors = []
        for item in data:
            contributors.append({
                "login": item.get("login"),
                "contributions": item.get("contributions", 0),
                "avatar": item.get("avatar_url"),
                "url": item.get("html_url"),
            })

        return {"contributors": contributors, "error": None}
    except Exception as e:
        return {"contributors": [], "error": str(e)}


def list_commits(owner: str, repo: str, limit: int = 20) -> dict:
    """List repository commits."""
    if not HTTpx_AVAILABLE:
        return {"commits": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/commits",
                headers=_get_headers(),
                params={"per_page": limit},
            )
            response.raise_for_status()

        data = response.json()
        commits = []
        for item in data:
            commits.append({
                "sha": item.get("sha", "")[:7],
                "message": item.get("commit", {}).get("message", "").split("\n")[0],
                "author": item.get("commit", {}).get("author", {}).get("name"),
                "date": item.get("commit", {}).get("author", {}).get("date"),
                "url": item.get("html_url"),
            })

        return {"commits": commits, "error": None}
    except Exception as e:
        return {"commits": [], "error": str(e)}


def get_file_content(owner: str, repo: str, path: str, ref: str = "main") -> dict:
    """Get file content from repository."""
    if not HTTpx_AVAILABLE:
        return {"content": "", "error": "httpx not installed"}

    try:
        import base64
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
                headers=_get_headers(),
                params={"ref": ref},
            )
            response.raise_for_status()

        data = response.json()
        if data.get("encoding") == "base64":
            content = base64.b64decode(data.get("content", "")).decode("utf-8")
            return {
                "content": content,
                "path": data.get("path"),
                "size": data.get("size", 0),
                "sha": data.get("sha"),
                "error": None,
            }
        return {"content": data.get("content", ""), "error": None}

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"content": "", "error": "File not found"}
        return {"content": "", "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"content": "", "error": str(e)}


def list_branches(owner: str, repo: str) -> dict:
    """List repository branches."""
    if not HTTpx_AVAILABLE:
        return {"branches": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/branches",
                headers=_get_headers(),
            )
            response.raise_for_status()

        data = response.json()
        branches = []
        for item in data:
            branches.append({
                "name": item.get("name"),
                "protected": item.get("protected", False),
                "commit": item.get("commit", {}).get("sha", "")[:7],
            })

        return {"branches": branches, "error": None}
    except Exception as e:
        return {"branches": [], "error": str(e)}