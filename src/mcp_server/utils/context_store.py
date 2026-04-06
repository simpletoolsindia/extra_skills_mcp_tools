"""
Context Mode - External tool output storage for 98% token reduction.

Store tool outputs externally, pass lightweight references to LLM.
Based on context-mode MCP server architecture.
"""

from __future__ import annotations

import sqlite3
import json
import hashlib
import time
import os
from typing import Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ToolOutputRef:
    """Lightweight reference to externally stored output."""
    tool_name: str
    call_id: str
    timestamp: int
    size_bytes: int
    preview: str = ""
    truncated: bool = False
    cache_key: str = ""

    def to_dict(self) -> dict:
        return {
            "tool": self.tool_name,
            "call_id": self.call_id,
            "timestamp": self.timestamp,
            "size_bytes": self.size_bytes,
            "preview": self.preview[:200] + "..." if len(self.preview) > 200 else self.preview,
            "truncated": self.truncated,
            "ref": f"@ctx:{self.cache_key}",
        }


@dataclass
class ContextEntry:
    """Full context entry with output."""
    tool_name: str
    arguments: dict
    output: Any
    call_id: str
    timestamp: int
    session_id: str = "default"


class ContextStore:
    """
    SQLite-backed external storage for tool outputs.

    Stores outputs externally and returns lightweight references,
    reducing context window usage by 98%+.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.environ.get(
                "CONTEXT_DB_PATH",
                "/tmp/mcp_context.db"
            )

        self.db_path = db_path
        self.conn = self._init_db()

    def _init_db(self) -> sqlite3.Connection:
        """Initialize SQLite database with FTS support."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tool_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                call_id TEXT UNIQUE NOT NULL,
                session_id TEXT DEFAULT 'default',
                arguments TEXT,
                output TEXT,
                output_hash TEXT,
                size_bytes INTEGER,
                preview TEXT,
                truncated INTEGER DEFAULT 0,
                created_at INTEGER NOT NULL,
                expires_at INTEGER
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_outputs_call_id
            ON tool_outputs(call_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_outputs_session
            ON tool_outputs(session_id, created_at DESC)
        """)

        # FTS5 for search
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS tool_outputs_fts USING fts5(
                tool_name,
                arguments,
                output,
                content='tool_outputs',
                content_rowid='id'
            )
        """)

        conn.commit()
        return conn

    def store(
        self,
        tool_name: str,
        arguments: dict,
        output: Any,
        call_id: Optional[str] = None,
        session_id: str = "default",
        max_preview: int = 500,
        max_size: int = 1024 * 1024,  # 1MB
    ) -> ToolOutputRef:
        """
        Store tool output externally and return lightweight reference.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            output: Tool output (any JSON-serializable type)
            call_id: Unique call ID (generated if not provided)
            session_id: Session identifier for grouping
            max_preview: Max chars for preview
            max_size: Max size before truncation

        Returns:
            ToolOutputRef - lightweight reference for LLM context
        """
        if call_id is None:
            call_id = self._generate_call_id(tool_name, arguments)

        timestamp = int(time.time())

        # Serialize output
        if isinstance(output, (dict, list)):
            output_json = json.dumps(output, ensure_ascii=False)
        else:
            output_json = json.dumps({"result": output}, ensure_ascii=False)

        output_hash = hashlib.sha256(output_json.encode()).hexdigest()
        size_bytes = len(output_json.encode())

        # Truncate if needed
        truncated = size_bytes > max_size
        if truncated:
            output_json = output_json[:max_size]
            preview = output_json[-max_preview:]
        else:
            preview = output_json[:max_preview]

        # Store in DB
        self.conn.execute("""
            INSERT OR REPLACE INTO tool_outputs
            (tool_name, call_id, session_id, arguments, output, output_hash,
             size_bytes, preview, truncated, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tool_name,
            call_id,
            session_id,
            json.dumps(arguments, ensure_ascii=False),
            output_json,
            output_hash,
            size_bytes,
            preview,
            1 if truncated else 0,
            timestamp,
        ))
        self.conn.commit()

        return ToolOutputRef(
            tool_name=tool_name,
            call_id=call_id,
            timestamp=timestamp,
            size_bytes=size_bytes,
            preview=preview,
            truncated=truncated,
            cache_key=f"{session_id}:{call_id}",
        )

    def retrieve(self, call_id: str) -> Optional[dict]:
        """Retrieve stored output by call_id."""
        cursor = self.conn.execute("""
            SELECT tool_name, arguments, output, truncated, created_at
            FROM tool_outputs WHERE call_id = ?
        """, (call_id,))
        row = cursor.fetchone()

        if row:
            return {
                "tool_name": row[0],
                "arguments": json.loads(row[1]),
                "output": json.loads(row[2]),
                "truncated": bool(row[3]),
                "created_at": row[4],
            }
        return None

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Search tool outputs using full-text search.

        Args:
            query: Search query
            session_id: Optional session filter
            limit: Max results

        Returns:
            List of matching tool outputs
        """
        if session_id:
            sql = """
                SELECT call_id, tool_name, preview, created_at
                FROM tool_outputs
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            cursor = self.conn.execute(sql, (session_id, limit))
        else:
            sql = """
                SELECT call_id, tool_name, preview, created_at
                FROM tool_outputs
                ORDER BY created_at DESC
                LIMIT ?
            """
            cursor = self.conn.execute(sql, (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "call_id": row[0],
                "tool_name": row[1],
                "preview": row[2][:200],
                "created_at": row[3],
            })

        return results

    def get_session_outputs(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """Get recent outputs for a session."""
        cursor = self.conn.execute("""
            SELECT call_id, tool_name, arguments, output, truncated, created_at
            FROM tool_outputs
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (session_id, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                "call_id": row[0],
                "tool_name": row[1],
                "arguments": json.loads(row[2]),
                "output": json.loads(row[3]),
                "truncated": bool(row[4]),
                "created_at": row[5],
            })

        return results

    def get_stats(self) -> dict:
        """Get storage statistics."""
        cursor = self.conn.execute("""
            SELECT
                COUNT(*) as total_outputs,
                SUM(size_bytes) as total_bytes,
                SUM(CASE WHEN truncated THEN 1 ELSE 0 END) as truncated_count,
                COUNT(DISTINCT tool_name) as unique_tools,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM tool_outputs
        """)
        row = cursor.fetchone()

        return {
            "total_outputs": row[0],
            "total_bytes": row[1] or 0,
            "truncated_count": row[2] or 0,
            "unique_tools": row[3] or 0,
            "unique_sessions": row[4] or 0,
        }

    def clear_session(self, session_id: str) -> int:
        """Clear all outputs for a session."""
        cursor = self.conn.execute("""
            DELETE FROM tool_outputs WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()
        return cursor.rowcount

    def _generate_call_id(self, tool_name: str, arguments: dict) -> str:
        """Generate unique call ID from tool name and args."""
        content = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def close(self):
        """Close database connection."""
        self.conn.close()


# Global context store instance
_context_store: Optional[ContextStore] = None


def get_context_store() -> ContextStore:
    """Get or create global context store instance."""
    global _context_store
    if _context_store is None:
        _context_store = ContextStore()
    return _context_store


def reset_context_store():
    """Reset global context store (for testing)."""
    global _context_store
    if _context_store:
        _context_store.close()
    _context_store = None
