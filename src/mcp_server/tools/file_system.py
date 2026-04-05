"""File System MCP - Safe file operations for LLM agents."""

from __future__ import annotations

import os
import json
import hashlib
from typing import Optional, List, Dict, Any

# Allowed operations and paths
ALLOWED_EXTENSIONS = {
    "read": [".txt", ".md", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
             ".py", ".js", ".ts", ".html", ".css", ".csv", ".log", ".sh",
             ".h", ".cpp", ".c", ".go", ".rs", ".java", ".rb", ".php"],
    "write": [".txt", ".md", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
              ".py", ".js", ".ts", ".html", ".css", ".csv", ".log", ".sh"],
}

RESTRICTED_PATHS = ["/etc", "/var", "/usr", "/System", "/boot", "/proc", "/sys"]


def _is_safe_path(path: str, write: bool = False) -> bool:
    """Check if path is safe to access."""
    abs_path = os.path.abspath(path)

    # Check restricted paths
    for restricted in RESTRICTED_PATHS:
        if abs_path.startswith(restricted):
            return False

    # Check extensions for write operations
    if write:
        ext = os.path.splitext(path)[1].lower()
        if ext not in ALLOWED_EXTENSIONS.get("write", []):
            return False

    return True


def read_file(path: str, max_size: int = 1024 * 1024) -> dict:
    """
    Read a file safely.

    Args:
        path: File path (absolute or relative)
        max_size: Maximum file size to read (default: 1MB)

    Returns:
        dict with keys: content, error, size, lines
    """
    if not _is_safe_path(path, write=False):
        return {"content": "", "error": "Access denied: path restricted", "size": 0, "lines": 0}

    try:
        # Check file size
        file_size = os.path.getsize(path)
        if file_size > max_size:
            return {"content": "", "error": f"File too large: {file_size} bytes (max: {max_size})", "size": file_size, "lines": 0}

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return {
            "content": content,
            "error": None,
            "size": file_size,
            "lines": len(content.splitlines()),
            "path": os.path.abspath(path),
        }
    except FileNotFoundError:
        return {"content": "", "error": "File not found", "size": 0, "lines": 0}
    except PermissionError:
        return {"content": "", "error": "Permission denied", "size": 0, "lines": 0}
    except Exception as e:
        return {"content": "", "error": str(e), "size": 0, "lines": 0}


def write_file(path: str, content: str, create_dirs: bool = True) -> dict:
    """
    Write content to a file safely.

    Args:
        path: File path
        content: Content to write
        create_dirs: Create parent directories if needed

    Returns:
        dict with keys: success, path, error
    """
    if not _is_safe_path(path, write=True):
        return {"success": False, "path": path, "error": "Access denied: path or extension restricted"}

    try:
        if create_dirs:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "path": os.path.abspath(path),
            "size": len(content),
            "error": None,
        }
    except Exception as e:
        return {"success": False, "path": path, "error": str(e)}


def list_directory(path: str = ".", include_hidden: bool = False, max_items: int = 100) -> dict:
    """
    List directory contents.

    Args:
        path: Directory path
        include_hidden: Include hidden files
        max_items: Maximum items to return

    Returns:
        dict with keys: items (list), error
    """
    if not os.path.isdir(path):
        return {"items": [], "error": "Not a directory"}

    try:
        items = []
        entries = os.listdir(path)

        for name in entries[:max_items]:
            if not include_hidden and name.startswith("."):
                continue

            full_path = os.path.join(path, name)
            try:
                stat = os.stat(full_path)
                item = {
                    "name": name,
                    "type": "directory" if os.path.isdir(full_path) else "file",
                    "size": stat.st_size if os.path.isfile(full_path) else 0,
                    "modified": stat.st_mtime,
                }
                items.append(item)
            except:
                pass

        return {"items": items, "error": None}
    except Exception as e:
        return {"items": [], "error": str(e)}


def create_directory(path: str) -> dict:
    """Create a directory."""
    try:
        os.makedirs(path, exist_ok=True)
        return {"success": True, "path": os.path.abspath(path), "error": None}
    except Exception as e:
        return {"success": False, "path": path, "error": str(e)}


def file_info(path: str) -> dict:
    """Get file/directory information."""
    try:
        stat = os.stat(path)
        return {
            "path": os.path.abspath(path),
            "type": "directory" if os.path.isdir(path) else "file",
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "readable": os.access(path, os.R_OK),
            "writable": os.access(path, os.W_OK),
            "error": None,
        }
    except FileNotFoundError:
        return {"error": "File not found"}
    except Exception as e:
        return {"error": str(e)}


def search_files(directory: str, pattern: str, include_content: bool = False, max_results: int = 50) -> dict:
    """
    Search for files by name pattern.

    Args:
        directory: Directory to search
        pattern: Filename pattern (simple glob: * and ?)
        include_content: Also search file contents
        max_results: Maximum results

    Returns:
        dict with keys: matches (list), error
    """
    if not os.path.isdir(directory):
        return {"matches": [], "error": "Not a directory"}

    matches = []
    pattern_lower = pattern.lower()

    try:
        for root, dirs, files in os.walk(directory):
            # Skip hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for filename in files:
                if filename.lower().find(pattern_lower) != -1:
                    full_path = os.path.join(root, filename)
                    try:
                        matches.append({
                            "path": full_path,
                            "name": filename,
                            "size": os.path.getsize(full_path),
                            "modified": os.path.getmtime(full_path),
                        })
                        if len(matches) >= max_results:
                            return {"matches": matches, "error": None}
                    except:
                        pass

            if len(matches) >= max_results:
                break

        return {"matches": matches, "error": None}
    except Exception as e:
        return {"matches": [], "error": str(e)}


def get_file_hash(path: str, algorithm: str = "md5") -> dict:
    """Get file hash."""
    if not os.path.isfile(path):
        return {"hash": "", "error": "Not a file"}

    try:
        if algorithm == "md5":
            hasher = hashlib.md5()
        elif algorithm == "sha256":
            hasher = hashlib.sha256()
        elif algorithm == "sha1":
            hasher = hashlib.sha1()
        else:
            return {"hash": "", "error": f"Unknown algorithm: {algorithm}"}

        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)

        return {"hash": hasher.hexdigest(), "algorithm": algorithm, "error": None}
    except Exception as e:
        return {"hash": "", "error": str(e)}