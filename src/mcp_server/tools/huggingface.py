"""Hugging Face MCP - Access models, datasets, and Hub information."""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False

HF_API = "https://huggingface.co/api"
HF_TOKEN = os.environ.get("HF_TOKEN", "")


def _get_headers() -> dict:
    """Get headers for Hugging Face API."""
    headers = {
        "User-Agent": "MCP-Server/1.0",
    }
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    return headers


def search_models(query: str, limit: int = 10, sort: str = "downloads") -> dict:
    """Search for models on Hugging Face Hub."""
    if not HTTpx_AVAILABLE:
        return {"models": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{HF_API}/models",
                headers=_get_headers(),
                params={"search": query, "sort": sort, "direction": -1, "limit": limit},
            )
            response.raise_for_status()

        data = response.json()
        models = []
        for item in data:
            models.append({
                "id": item.get("id"),
                "downloads": item.get("downloads", 0),
                "likes": item.get("likes", 0),
                "tags": item.get("tags", [])[:10],
                "pipeline_tag": item.get("pipeline_tag"),
                "created_at": item.get("createdAt"),
                "last_modified": item.get("lastModified"),
            })

        return {"models": models, "error": None}
    except Exception as e:
        return {"models": [], "error": str(e)}


def get_model_info(model_id: str) -> dict:
    """Get detailed information about a model."""
    if not HTTpx_AVAILABLE:
        return {"model": None, "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{HF_API}/models/{model_id}",
                headers=_get_headers(),
            )
            response.raise_for_status()

        data = response.json()
        return {
            "model": {
                "id": data.get("id"),
                "author": data.get("author"),
                "sha": data.get("sha"),
                "created_at": data.get("createdAt"),
                "last_modified": data.get("lastModified"),
                "downloads": data.get("downloads"),
                "likes": data.get("likes"),
                "tags": data.get("tags"),
                "pipeline_tag": data.get("pipelineTag"),
                "siblings": [f.get("rfilename") for f in data.get("siblings", [])],
            },
            "error": None,
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"model": None, "error": "Model not found"}
        return {"model": None, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"model": None, "error": str(e)}


def search_datasets(query: str, limit: int = 10, sort: str = "downloads") -> dict:
    """Search for datasets on Hugging Face Hub."""
    if not HTTpx_AVAILABLE:
        return {"datasets": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{HF_API}/datasets",
                headers=_get_headers(),
                params={"search": query, "sort": sort, "direction": -1, "limit": limit},
            )
            response.raise_for_status()

        data = response.json()
        datasets = []
        for item in data:
            datasets.append({
                "id": item.get("id"),
                "downloads": item.get("downloads", 0),
                "likes": item.get("likes", 0),
                "tags": item.get("tags", [])[:10],
                "created_at": item.get("createdAt"),
                "last_modified": item.get("lastModified"),
            })

        return {"datasets": datasets, "error": None}
    except Exception as e:
        return {"datasets": [], "error": str(e)}


def get_dataset_info(dataset_id: str) -> dict:
    """Get detailed information about a dataset."""
    if not HTTpx_AVAILABLE:
        return {"dataset": None, "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{HF_API}/datasets/{dataset_id}",
                headers=_get_headers(),
            )
            response.raise_for_status()

        data = response.json()
        return {
            "dataset": {
                "id": data.get("id"),
                "author": data.get("author"),
                "created_at": data.get("createdAt"),
                "last_modified": data.get("lastModified"),
                "downloads": data.get("downloads"),
                "likes": data.get("likes"),
                "tags": data.get("tags"),
                "card_data": data.get("cardData", {}),
            },
            "error": None,
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"dataset": None, "error": "Dataset not found"}
        return {"dataset": None, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"dataset": None, "error": str(e)}


def list_model_files(model_id: str, path: str = "") -> dict:
    """List files in a model repository."""
    if not HTTpx_AVAILABLE:
        return {"files": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            url = f"{HF_API}/models/{model_id}/tree/main/{path}" if path else f"{HF_API}/models/{model_id}/tree/main"
            response = client.get(url, headers=_get_headers())
            response.raise_for_status()

        data = response.json()
        files = []
        for item in data:
            files.append({
                "path": item.get("path"),
                "type": item.get("type"),
                "size": item.get("size"),
            })

        return {"files": files, "error": None}
    except Exception as e:
        return {"files": [], "error": str(e)}


def get_model_card(model_id: str) -> dict:
    """Get model README/card content."""
    if not HTTpx_AVAILABLE:
        return {"card": "", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"https://huggingface.co/{model_id}/raw/main/README.md",
                headers=_get_headers(),
            )
            response.raise_for_status()

        return {"card": response.text, "error": None}
    except httpx.HTTPStatusError:
        return {"card": "", "error": "README not found"}
    except Exception as e:
        return {"card": "", "error": str(e)}


def get_trending_models(limit: int = 10) -> dict:
    """Get trending models on Hugging Face."""
    return search_models(query="", limit=limit, sort="trending")


def get_popular_models(limit: int = 10) -> dict:
    """Get most downloaded models."""
    return search_models(query="", limit=limit, sort="downloads")


def search_spaces(query: str, limit: int = 10) -> dict:
    """Search for Spaces on Hugging Face Hub."""
    if not HTTpx_AVAILABLE:
        return {"spaces": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{HF_API}/spaces",
                headers=_get_headers(),
                params={"search": query, "limit": limit, "sort": "likes"},
            )
            response.raise_for_status()

        data = response.json()
        spaces = []
        for item in data:
            spaces.append({
                "id": item.get("id"),
                "sdk": item.get("sdk"),
                "likes": item.get("likes", 0),
                "tags": item.get("tags", [])[:5],
            })

        return {"spaces": spaces, "error": None}
    except Exception as e:
        return {"spaces": [], "error": str(e)}