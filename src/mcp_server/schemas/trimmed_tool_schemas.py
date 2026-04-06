"""Token-optimized tool schemas for reduced context usage."""

from __future__ import annotations

# ===== WEB CONTENT OPTIMIZATION TOOLS =====

FETCH_OPTIMIZED_TOOLS = [
    {
        "name": "fetch_web_content",
        "description": "Fetch URL and extract clean content. Optimized for LLM (strips nav/ads, converts to markdown).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "max_tokens": {"type": "integer", "description": "Max tokens output (default: 4000)", "default": 4000},
            },
            "required": ["url"],
        },
    },
    {
        "name": "fetch_structured",
        "description": "Fetch and extract structured data (article metadata, product info, tables, links). Most token-efficient.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "extraction_type": {
                    "type": "string",
                    "enum": ["article", "product", "table", "links"],
                    "description": "Extraction type"
                },
                "max_tokens": {"type": "integer", "description": "Max tokens (default: 2000)", "default": 2000},
            },
            "required": ["url", "extraction_type"],
        },
    },
    {
        "name": "fetch_with_selectors",
        "description": "Fetch URL and extract using CSS selectors. Best for known page structures.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "selectors": {
                    "type": "object",
                    "description": "Dict of {field_name: css_selector}",
                    "additionalProperties": {"type": "string"},
                },
                "max_tokens": {"type": "integer", "description": "Max tokens (default: 2000)", "default": 2000},
            },
            "required": ["url", "selectors"],
        },
    },
    {
        "name": "quick_fetch",
        "description": "Ultra-fast fetch for quick lookups. Returns title + summary only. Minimal tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "max_tokens": {"type": "integer", "description": "Max tokens (default: 1500)", "default": 1500},
            },
            "required": ["url"],
        },
    },
]

# ===== TRIMMED WEB SCRAPING TOOLS =====

FETCH_TRIMMED_TOOLS = [
    {
        "name": "scrape_freedium",
        "description": "Scrape Medium via Freedium. Returns title, author, content, tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Freedium URL"},
                "max_tokens": {"type": "integer", "description": "Max tokens (default: 4000)", "default": 4000},
            },
            "required": ["url"],
        },
    },
    {
        "name": "webclaw_extract_article",
        "description": "Extract article content using common patterns.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Article URL"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "webclaw_extract_product",
        "description": "Extract e-commerce product info.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Product URL"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "webclaw_crawl",
        "description": "Crawl with CSS selectors.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to crawl"},
                "selectors": {"type": "object", "description": "Dict of {field: selector}"},
            },
            "required": ["url", "selectors"],
        },
    },
]

# ===== TRIMMED SEARCH TOOLS =====

SEARCH_TRIMMED_TOOLS = [
    {
        "name": "searxng_search",
        "description": "Web search via SearXNG. Supports categories, engines, time range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results (default: 10)", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_images",
        "description": "Image search via SearXNG.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Image search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_news",
        "description": "News search via SearXNG.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "News search query"},
                "time_range": {"type": "string", "enum": ["day", "week", "month", "year"]},
            },
            "required": ["query"],
        },
    },
    {
        "name": "searxng_health",
        "description": "Check SearXNG health.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

# ===== TRIMMED HACKERNEWS TOOLS =====

HN_TRIMMED_TOOLS = [
    {
        "name": "hackernews_top",
        "description": "Top HN stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_new",
        "description": "Newest HN stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_best",
        "description": "Best HN stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_get_comments",
        "description": "Get story comments.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "story_id": {"type": "integer", "description": "Story ID"},
                "limit": {"type": "integer", "description": "Max comments", "default": 20},
            },
            "required": ["story_id"],
        },
    },
]

# ===== TRIMMED GITHUB TOOLS =====

GITHUB_TRIMMED_TOOLS = [
    {
        "name": "github_repo",
        "description": "Get repo info.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repo owner"},
                "repo": {"type": "string", "description": "Repo name"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_readme",
        "description": "Get repo README.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repo owner"},
                "repo": {"type": "string", "description": "Repo name"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_issues",
        "description": "List repo issues.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repo owner"},
                "repo": {"type": "string", "description": "Repo name"},
                "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_commits",
        "description": "List recent commits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repo owner"},
                "repo": {"type": "string", "description": "Repo name"},
                "limit": {"type": "integer", "description": "Max commits", "default": 20},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_search_repos",
        "description": "Search repos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["query"],
        },
    },
]

# ===== TRIMMED FILE TOOLS =====

FILE_TRIMMED_TOOLS = [
    {
        "name": "file_read",
        "description": "Read file (restricted paths).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "max_size": {"type": "integer", "description": "Max bytes (default: 1MB)", "default": 1048576},
            },
            "required": ["path"],
        },
    },
    {
        "name": "file_write",
        "description": "Write file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "file_list",
        "description": "List directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory", "default": "."},
                "max_items": {"type": "integer", "description": "Max items", "default": 100},
            },
        },
    },
    {
        "name": "file_search",
        "description": "Search files by name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to search"},
                "pattern": {"type": "string", "description": "Filename pattern"},
                "max_results": {"type": "integer", "description": "Max results", "default": 50},
            },
            "required": ["directory", "pattern"],
        },
    },
]

# ===== TRIMMED CODE TOOLS =====

CODE_TRIMMED_TOOLS = [
    {
        "name": "run_code",
        "description": "Run code sandbox (Python, JS, Bash).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to execute"},
                "language": {"type": "string", "enum": ["python", "javascript", "bash"]},
                "timeout": {"type": "integer", "description": "Timeout sec", "default": 30},
            },
            "required": ["code", "language"],
        },
    },
    {
        "name": "run_python_snippet",
        "description": "Run Python with common imports.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code"},
                "timeout": {"type": "integer", "description": "Timeout sec", "default": 30},
            },
            "required": ["code"],
        },
    },
]

# ===== TRIMMED DATA TOOLS =====

DATA_TRIMMED_TOOLS = [
    {
        "name": "pandas_create",
        "description": "Create DataFrame from data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "JSON data"},
                "name": {"type": "string", "description": "DataFrame name", "default": "df"},
            },
            "required": ["data"],
        },
    },
    {
        "name": "pandas_filter",
        "description": "Filter DataFrame.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "Rows as dicts"},
                "conditions": {"type": "string", "description": "Filter JSON"},
            },
            "required": ["data", "conditions"],
        },
    },
    {
        "name": "pandas_aggregate",
        "description": "Aggregate/group data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "Rows"},
                "group_by": {"type": "array", "items": {"type": "string"}, "description": "Columns"},
                "aggregations": {"type": "object", "description": "{column: function}"},
            },
            "required": ["data", "group_by", "aggregations"],
        },
    },
]

# ===== TRIMMED VISUALIZATION TOOLS =====

VIZ_TRIMMED_TOOLS = [
    {
        "name": "plot_line",
        "description": "Line plot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "array", "description": "X data"},
                "y": {"type": "array", "description": "Y data"},
                "title": {"type": "string", "description": "Chart title"},
            },
            "required": ["x", "y"],
        },
    },
    {
        "name": "plot_bar",
        "description": "Bar chart.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "categories": {"type": "array", "description": "Labels"},
                "values": {"type": "array", "description": "Values"},
                "title": {"type": "string", "description": "Chart title"},
            },
            "required": ["categories", "values"],
        },
    },
    {
        "name": "plot_pie",
        "description": "Pie chart.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "labels": {"type": "array", "description": "Labels"},
                "values": {"type": "array", "description": "Values"},
                "title": {"type": "string", "description": "Chart title"},
            },
            "required": ["labels", "values"],
        },
    },
    {
        "name": "plot_scatter",
        "description": "Scatter plot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "array", "description": "X data"},
                "y": {"type": "array", "description": "Y data"},
                "title": {"type": "string", "description": "Chart title"},
            },
            "required": ["x", "y"],
        },
    },
]

# ===== TRIMMED YOUTUBE TOOLS =====

YOUTUBE_TRIMMED_TOOLS = [
    {
        "name": "youtube_transcript",
        "description": "Get transcript from video.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Video URL or ID"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "youtube_video_info",
        "description": "Get video metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Video URL"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "youtube_search",
        "description": "Search videos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "youtube_summarize",
        "description": "Summarize transcript.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "transcript": {"type": "string", "description": "Transcript text"},
                "max_words": {"type": "integer", "description": "Max words", "default": 500},
            },
            "required": ["transcript"],
        },
    },
]

# ===== TRIMMED THINKING TOOLS =====

THINKING_TRIMMED_TOOLS = [
    {
        "name": "thinking_session_create",
        "description": "Create thinking session.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "thinking_step",
        "description": "Add reasoning step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID"},
                "thought": {"type": "string", "description": "Your thought"},
                "confidence": {"type": "number", "description": "Confidence 0-1", "default": 1.0},
            },
            "required": ["session_id", "thought"],
        },
    },
    {
        "name": "thinking_summary",
        "description": "Get session summary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID"},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "analyze_problem",
        "description": "Analyze problem with structured thinking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "description": "Problem description"},
                "approach": {
                    "type": "string",
                    "enum": ["decompose", "hypothesize", "compare", "evaluate"],
                    "description": "Analysis approach"
                },
            },
            "required": ["problem"],
        },
    },
]

# ===== TRIMMED ENGINEERING TOOLS =====

ENGI_TRIMMED_TOOLS = [
    {
        "name": "engi_task_classify",
        "description": "Classify task type (bug, feature, etc).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "engi_repo_scope_find",
        "description": "Find relevant files for task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "Repo path"},
                "task": {"type": "string", "description": "Task description"},
                "task_type": {"type": "string", "enum": ["analysis", "feature", "bug", "poc", "documentation", "mixed"]},
            },
            "required": ["repo_path", "task"],
        },
    },
    {
        "name": "engi_bug_trace",
        "description": "Pinpoint bug causes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Files"},
                "symptom": {"type": "string", "description": "Bug description"},
            },
            "required": ["scope", "symptom"],
        },
    },
    {
        "name": "engi_implementation_plan",
        "description": "Generate implementation plan.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description"},
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Files to modify"},
                "task_type": {"type": "string", "enum": ["bug", "feature", "refactor"]},
            },
            "required": ["task", "scope"],
        },
    },
    {
        "name": "engi_impact_analyze",
        "description": "Estimate change blast radius.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Files"},
                "change_type": {"type": "string", "enum": ["add", "modify", "delete"]},
            },
            "required": ["scope", "change_type"],
        },
    },
    {
        "name": "engi_test_select",
        "description": "Select minimum test set.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Changed files"},
                "change_type": {"type": "string", "enum": ["add", "modify", "delete"]},
            },
            "required": ["scope", "change_type"],
        },
    },
    {
        "name": "engi_memory_checkpoint",
        "description": "Save task state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Files in scope"},
                "task_type": {"type": "string", "enum": ["analysis", "feature", "bug", "poc", "documentation", "mixed"]},
            },
            "required": ["task_id", "files"],
        },
    },
    {
        "name": "engi_memory_restore",
        "description": "Restore saved checkpoint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
            },
            "required": ["task_id"],
        },
    },
]

# ===== SYSTEM TOOLS (minimal) =====

SYSTEM_TRIMMED_TOOLS = [
    {
        "name": "run_command",
        "description": "Execute whitelisted command (ls, cat, cp, mv, rm).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command name"},
                "args": {"type": "array", "items": {"type": "string"}, "description": "Args"},
            },
            "required": ["command"],
        },
    },
]

# ===== CONTEXT MODE TOOLS (98% output reduction) =====

CONTEXT_MODE_TOOLS = [
    {
        "name": "ctx_store_output",
        "description": "Store tool output externally. LLM gets reference instead of full output.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_name": {"type": "string", "description": "Tool name"},
                "arguments": {"type": "object", "description": "Tool arguments"},
                "output": {"type": "object", "description": "Output to store"},
                "session_id": {"type": "string", "description": "Session ID", "default": "default"},
            },
            "required": ["tool_name", "arguments", "output"],
        },
    },
    {
        "name": "ctx_get_output",
        "description": "Retrieve stored output by call_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "call_id": {"type": "string", "description": "Call ID from store_output"},
            },
            "required": ["call_id"],
        },
    },
    {
        "name": "ctx_search",
        "description": "Search stored outputs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "session_id": {"type": "string", "description": "Session filter"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "ctx_session_overview",
        "description": "Get session overview with recent outputs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID", "default": "default"},
                "limit": {"type": "integer", "description": "Max outputs", "default": 20},
            },
        },
    },
    {
        "name": "ctx_clear",
        "description": "Clear session outputs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session to clear"},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "ctx_stats",
        "description": "Get Context Mode stats.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

# ===== LAZY TOOL LOADING TOOLS (91% input reduction) =====

LAZY_LOADING_TOOLS = [
    {
        "name": "tools_minimal",
        "description": "Get tool list with summaries only (no full schemas). 67% fewer tokens than loading all schemas.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category_filter": {"type": "string", "description": "Filter by category name"},
            },
        },
    },
    {
        "name": "tools_describe",
        "description": "Load full schemas for specific tools on-demand. Use after seeing minimal list.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tool names to get schemas for",
                },
            },
            "required": ["tool_names"],
        },
    },
    {
        "name": "tools_search",
        "description": "Search tools by intent (e.g., 'search web', 'run code').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "tools_categories",
        "description": "Get all tool categories with descriptions.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

# ===== SEMANTIC TOOL SEARCH TOOLS (3-tool pattern) =====

SEMANTIC_SEARCH_TOOLS = [
    {
        "name": "semantic_search",
        "description": "Find tools by describing what you want to do. E.g., 'search the web', 'run code', 'fetch webpage'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "description": "What you want to do"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["intent"],
        },
    },
    {
        "name": "semantic_describe",
        "description": "Load full schemas for tools from search results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tool names to describe",
                },
            },
            "required": ["tool_names"],
        },
    },
    {
        "name": "semantic_execute",
        "description": "Guided execution: search, describe, execute in one step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "description": "What you want to do"},
            },
            "required": ["intent"],
        },
    },
]

# ===== ALL TRIMMED TOOLS =====

ALL_TRIMMED_TOOLS = (
    FETCH_OPTIMIZED_TOOLS +
    FETCH_TRIMMED_TOOLS +
    SEARCH_TRIMMED_TOOLS +
    HN_TRIMMED_TOOLS +
    GITHUB_TRIMMED_TOOLS +
    FILE_TRIMMED_TOOLS +
    CODE_TRIMMED_TOOLS +
    DATA_TRIMMED_TOOLS +
    VIZ_TRIMMED_TOOLS +
    YOUTUBE_TRIMMED_TOOLS +
    THINKING_TRIMMED_TOOLS +
    ENGI_TRIMMED_TOOLS +
    SYSTEM_TRIMMED_TOOLS +
    CONTEXT_MODE_TOOLS +
    LAZY_LOADING_TOOLS +
    SEMANTIC_SEARCH_TOOLS
)

# Token counts for comparison
ORIGINAL_TOOL_COUNT = 90
TRIMMED_TOOL_COUNT = len(ALL_TRIMMED_TOOLS)
TOKEN_REDUCTION_PER_TOOL = "~40-60%"  # From description trimming alone
CONTEXT_MODE_REDUCTION = "~98%"  # For tool outputs when using ctx_store_output
LAZY_LOADING_REDUCTION = "~91%"  # For input schemas with lazy loading
