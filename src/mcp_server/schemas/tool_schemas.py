"""Tool schemas matching the MCP spec - Unified MCP Server with 35+ tools."""

TOOL_DEFINITIONS = [
    # ===== WEB SEARCH & SCRAPING =====
    {
        "name": "searxng_search",
        "description": "Search the web via native SearXNG with advanced options (categories, engines, time range, language).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results (default: 10, max: 50)", "default": 10},
                "categories": {"type": "array", "items": {"type": "string"}, "description": "Filter by categories (news, web, images, videos, science)"},
                "engines": {"type": "array", "items": {"type": "string"}, "description": "Specific search engines to use"},
                "time_range": {"type": "string", "enum": ["day", "week", "month", "year"], "description": "Time filter"},
                "language": {"type": "string", "description": "Language code (default: en)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_images",
        "description": "Search for images via SearXNG.",
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
        "description": "Search for news via SearXNG.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "News search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
                "time_range": {"type": "string", "enum": ["day", "week", "month", "year"], "description": "Time filter"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "searxng_health",
        "description": "Check if SearXNG is running and healthy.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "fetch_web_content",
        "description": "Fetch a webpage and extract clean, LLM-friendly content using readability-lxml.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "max_length": {"type": "integer", "description": "Max characters (default: 8000)", "default": 8000},
            },
            "required": ["url"],
        },
    },
    {
        "name": "scrape_dynamic",
        "description": "Scrape JavaScript-heavy pages using Playwright headless browser. For SPAs, infinite scroll, etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to scrape"},
                "selector": {"type": "string", "description": "CSS selector for specific content"},
                "wait_for": {"type": "string", "description": "CSS selector to wait for"},
                "max_length": {"type": "integer", "description": "Max characters (default: 15000)", "default": 15000},
            },
            "required": ["url"],
        },
    },
    {
        "name": "extract_structured",
        "description": "Extract structured data (articles, products, tables) using scrapling's fast CSS extraction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "html_content": {"type": "string", "description": "Raw HTML to parse"},
                "extraction_type": {"type": "string", "enum": ["article", "ecommerce", "table", "links"]},
                "selector": {"type": "string", "description": "CSS selector to target"},
                "custom_selector": {"type": "string", "description": "Custom selector for links"},
            },
            "required": ["html_content", "extraction_type"],
        },
    },
    {
        "name": "scrape_freedium",
        "description": "Scrape Medium articles via Freedium (bypasses paywall). Extracts title, author, content, tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Freedium URL or article path"},
                "max_length": {"type": "integer", "description": "Max characters (default: 20000)", "default": 20000},
            },
            "required": ["url"],
        },
    },
    {
        "name": "list_freedium_articles",
        "description": "List articles on Freedium homepage or category pages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Freedium URL", "default": "https://freedium-mirror.cfd/"},
                "limit": {"type": "integer", "description": "Max articles (default: 20)", "default": 20},
            },
        },
    },
    {
        "name": "firecrawl_scrape",
        "description": "Scrape URL with Firecrawl (requires FIRECRAWL_API_TOKEN). Falls back to local scraping.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to scrape"},
                "only_main_content": {"type": "boolean", "description": "Only main content", "default": True},
                "include_html": {"type": "boolean", "description": "Include raw HTML", "default": False},
            },
            "required": ["url"],
        },
    },
    {
        "name": "firecrawl_crawl",
        "description": "Crawl URL with multiple pages using Firecrawl.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Starting URL"},
                "limit": {"type": "integer", "description": "Max pages (default: 10)", "default": 10},
                "allow_external": {"type": "boolean", "description": "Allow external domains", "default": False},
            },
            "required": ["url"],
        },
    },
    {
        "name": "webclaw_crawl",
        "description": "Crawl URL with custom CSS selectors using Webclaw.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to crawl"},
                "selectors": {"type": "object", "description": "Dict of {field_name: css_selector}"},
                "follow_links": {"type": "boolean", "description": "Follow links", "default": False},
            },
            "required": ["url", "selectors"],
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
        "name": "browserbase_browse",
        "description": "Cloud browser automation with Browserbase (requires BROWSERBASE_API_KEY). Falls back to Playwright.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to browse"},
                "action": {"type": "string", "enum": ["get_content", "screenshot", "click", "fill"], "description": "Action"},
                "selector": {"type": "string", "description": "CSS selector for action"},
            },
            "required": ["url"],
        },
    },
    # ===== SEARCH ENGINES =====
    {
        "name": "hackernews_top",
        "description": "Get top Hacker News stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories (default: 10)", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_new",
        "description": "Get newest Hacker News stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_best",
        "description": "Get best Hacker News stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_ask",
        "description": "Get Ask HN stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_show",
        "description": "Get Show HN stories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max stories", "default": 10},
            },
        },
    },
    {
        "name": "hackernews_get_comments",
        "description": "Get comments for a Hacker News story.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "story_id": {"type": "integer", "description": "Story ID"},
                "limit": {"type": "integer", "description": "Max comments", "default": 20},
            },
            "required": ["story_id"],
        },
    },
    {
        "name": "hackernews_user",
        "description": "Get Hacker News user info.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Username"},
            },
            "required": ["username"],
        },
    },
    {
        "name": "huggingface_search_models",
        "description": "Search Hugging Face models.",
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
        "name": "huggingface_search_datasets",
        "description": "Search Hugging Face datasets.",
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
        "name": "huggingface_model_info",
        "description": "Get detailed model info from Hugging Face.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_id": {"type": "string", "description": "Model ID (e.g., 'meta-llama/Llama-2-7b')"},
            },
            "required": ["model_id"],
        },
    },
    {
        "name": "huggingface_trending",
        "description": "Get trending models on Hugging Face.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
        },
    },
    # ===== GITHUB =====
    {
        "name": "github_repo",
        "description": "Get GitHub repository information.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_readme",
        "description": "Get repository README.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_issues",
        "description": "List repository issues.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
                "state": {"type": "string", "enum": ["open", "closed", "all"], "description": "Issue state", "default": "open"},
                "limit": {"type": "integer", "description": "Max issues", "default": 20},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_commits",
        "description": "List repository commits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
                "limit": {"type": "integer", "description": "Max commits", "default": 20},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_search_repos",
        "description": "Search GitHub repositories.",
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
        "name": "github_file_content",
        "description": "Get file content from repository.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
                "path": {"type": "string", "description": "File path"},
                "ref": {"type": "string", "description": "Branch/tag/SHA", "default": "main"},
            },
            "required": ["owner", "repo", "path"],
        },
    },
    # ===== FILE SYSTEM =====
    {
        "name": "file_read",
        "description": "Read a file safely (restricted paths and extensions).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "max_size": {"type": "integer", "description": "Max size in bytes (default: 1MB)", "default": 1048576},
            },
            "required": ["path"],
        },
    },
    {
        "name": "file_write",
        "description": "Write content to a file safely.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "file_list",
        "description": "List directory contents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path", "default": "."},
                "include_hidden": {"type": "boolean", "description": "Include hidden files", "default": False},
                "max_items": {"type": "integer", "description": "Max items", "default": 100},
            },
        },
    },
    {
        "name": "file_info",
        "description": "Get file/directory information.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "file_search",
        "description": "Search for files by name pattern.",
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
    # ===== CODE EXECUTION =====
    {
        "name": "run_code",
        "description": "Run LLM-generated code in sandboxed environment (Python, JavaScript, Bash).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to execute"},
                "language": {"type": "string", "enum": ["python", "javascript", "bash"], "description": "Language"},
                "timeout": {"type": "integer", "description": "Timeout seconds (default: 30)", "default": 30},
                "args": {"type": "array", "items": {"type": "string"}, "description": "Command-line args"},
            },
            "required": ["code", "language"],
        },
    },
    {
        "name": "run_python_snippet",
        "description": "Run Python code with pre-loaded common imports (json, math, re, datetime, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code"},
                "imports": {"type": "array", "items": {"type": "string"}, "description": "Modules to import"},
                "timeout": {"type": "integer", "description": "Timeout (default: 30)", "default": 30},
            },
            "required": ["code"],
        },
    },
    {
        "name": "test_code_snippet",
        "description": "Run code and verify expected output.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to run"},
                "language": {"type": "string", "description": "Language", "default": "python"},
                "expected_output": {"type": "string", "description": "Expected stdout"},
            },
            "required": ["code"],
        },
    },
    # ===== DATA & ANALYSIS =====
    {
        "name": "pandas_create",
        "description": "Create a pandas DataFrame from data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "JSON string or list of dicts"},
                "name": {"type": "string", "description": "DataFrame name", "default": "df"},
            },
            "required": ["data"],
        },
    },
    {
        "name": "pandas_filter",
        "description": "Filter DataFrame with conditions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "List of dicts (DataFrame rows)"},
                "conditions": {"type": "string", "description": "JSON filter conditions"},
            },
            "required": ["data", "conditions"],
        },
    },
    {
        "name": "pandas_aggregate",
        "description": "Aggregate DataFrame data (group by, sum, mean, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "List of dicts"},
                "group_by": {"type": "array", "items": {"type": "string"}, "description": "Columns to group by"},
                "aggregations": {"type": "object", "description": "Dict of {column: function}"},
            },
            "required": ["data", "group_by", "aggregations"],
        },
    },
    {
        "name": "pandas_correlation",
        "description": "Compute correlation matrix for numeric columns.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "List of dicts"},
                "columns": {"type": "array", "items": {"type": "string"}, "description": "Columns to include"},
            },
            "required": ["data"],
        },
    },
    {
        "name": "pandas_outliers",
        "description": "Detect outliers in numeric column (IQR or Z-score).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "List of dicts"},
                "column": {"type": "string", "description": "Column to analyze"},
                "method": {"type": "string", "enum": ["iqr", "zscore"], "description": "Detection method"},
                "threshold": {"type": "number", "description": "Threshold (default: 1.5)", "default": 1.5},
            },
            "required": ["data", "column"],
        },
    },
    # ===== VISUALIZATION =====
    {
        "name": "plot_line",
        "description": "Create a line plot with matplotlib.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "array", "description": "X-axis data"},
                "y": {"type": "array", "description": "Y-axis data"},
                "title": {"type": "string", "description": "Chart title"},
                "xlabel": {"type": "string", "description": "X-axis label"},
                "ylabel": {"type": "string", "description": "Y-axis label"},
            },
            "required": ["x", "y"],
        },
    },
    {
        "name": "plot_bar",
        "description": "Create a bar chart.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "categories": {"type": "array", "items": {"type": "string"}, "description": "Categories"},
                "values": {"type": "array", "description": "Values"},
                "title": {"type": "string", "description": "Chart title"},
                "horizontal": {"type": "boolean", "description": "Horizontal bars", "default": False},
            },
            "required": ["categories", "values"],
        },
    },
    {
        "name": "plot_pie",
        "description": "Create a pie chart.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels"},
                "values": {"type": "array", "description": "Values"},
                "title": {"type": "string", "description": "Chart title"},
            },
            "required": ["labels", "values"],
        },
    },
    {
        "name": "plot_scatter",
        "description": "Create a scatter plot.",
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
        "name": "plot_histogram",
        "description": "Create a histogram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "Data points"},
                "bins": {"type": "integer", "description": "Number of bins", "default": 30},
                "title": {"type": "string", "description": "Chart title"},
            },
            "required": ["data"],
        },
    },
    {
        "name": "generate_chart_spec",
        "description": "Generate Ant Design Charts spec (line, bar, pie, scatter, heatmap, gauge).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "enum": ["line", "bar", "pie", "scatter", "heatmap", "gauge"]},
                "data": {"type": "array", "description": "Chart data"},
                "x_field": {"type": "string", "description": "X-axis field"},
                "y_field": {"type": "string", "description": "Y-axis field"},
                "title": {"type": "string", "description": "Chart title"},
            },
            "required": ["chart_type", "data"],
        },
    },
    # ===== DOCUMENT CONVERSION =====
    {
        "name": "markitdown_html_to_md",
        "description": "Convert HTML to Markdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "html": {"type": "string", "description": "HTML content"},
            },
            "required": ["html"],
        },
    },
    {
        "name": "markitdown_url_to_md",
        "description": "Fetch URL and convert to Markdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "max_length": {"type": "integer", "description": "Max markdown length", "default": 50000},
            },
            "required": ["url"],
        },
    },
    {
        "name": "markitdown_file_to_md",
        "description": "Extract text from file (txt, md, json, html, csv).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "File path"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "markitdown_md_to_html",
        "description": "Convert Markdown to HTML.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "markdown": {"type": "string", "description": "Markdown content"},
            },
            "required": ["markdown"],
        },
    },
    # ===== REASONING =====
    {
        "name": "thinking_session_create",
        "description": "Create a new sequential thinking session.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "thinking_step",
        "description": "Add a thinking step to session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID"},
                "thought": {"type": "string", "description": "Your thought/reasoning"},
                "action": {"type": "string", "description": "Optional action taken"},
                "observation": {"type": "string", "description": "Optional observation"},
                "confidence": {"type": "number", "description": "Confidence 0-1", "default": 1.0},
            },
            "required": ["session_id", "thought"],
        },
    },
    {
        "name": "thinking_revoke",
        "description": "Revise a previous thinking step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID"},
                "step": {"type": "integer", "description": "Step number to revise (0-indexed)"},
                "new_thought": {"type": "string", "description": "New thought"},
                "reason": {"type": "string", "description": "Reason for revision"},
            },
            "required": ["session_id", "step", "new_thought", "reason"],
        },
    },
    {
        "name": "thinking_summary",
        "description": "Get thinking session summary.",
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
        "description": "Analyze a problem using structured thinking (decompose, hypothesize, compare, evaluate).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "description": "Problem description"},
                "approach": {"type": "string", "enum": ["decompose", "hypothesize", "compare", "evaluate"], "description": "Analysis approach"},
            },
            "required": ["problem"],
        },
    },
    # ===== RESEARCH =====
    {
        "name": "research_start",
        "description": "Start a new research session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "research_id": {"type": "string", "description": "Unique research ID"},
                "query": {"type": "string", "description": "Research question"},
                "depth": {"type": "string", "enum": ["basic", "thorough", "extensive"], "description": "Research depth"},
            },
            "required": ["research_id", "query"],
        },
    },
    {
        "name": "research_add_source",
        "description": "Add a source to research.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "research_id": {"type": "string", "description": "Research ID"},
                "source": {"type": "object", "description": "Source dict {url, title, content, snippet}"},
            },
            "required": ["research_id", "source"],
        },
    },
    {
        "name": "research_complete",
        "description": "Complete research with conclusion.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "research_id": {"type": "string", "description": "Research ID"},
                "conclusion": {"type": "string", "description": "Research conclusion"},
            },
            "required": ["research_id", "conclusion"],
        },
    },
    {
        "name": "research_report",
        "description": "Get research report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "research_id": {"type": "string", "description": "Research ID"},
            },
            "required": ["research_id"],
        },
    },
    # ===== SYSTEM =====
    {
        "name": "run_command",
        "description": "Execute a whitelisted system command (ls, cat, cp, mv, rm). Security restricted.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command (ls, cat, cp, mv, rm)"},
                "args": {"type": "array", "items": {"type": "string"}, "description": "Command arguments"},
            },
            "required": ["command"],
        },
    },
    # ===== YOUTUBE TRANSCRIPT =====
    {
        "name": "youtube_transcript",
        "description": "Extract transcript from YouTube video. Works with YouTube URLs or video IDs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "YouTube video URL or video ID"},
                "lang": {"type": "string", "description": "Language code (default: en)"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "youtube_transcript_timed",
        "description": "Get YouTube transcript with timestamps for better context and navigation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "YouTube video URL"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "youtube_search",
        "description": "Search YouTube videos using Invidious (no API key required).",
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
        "name": "youtube_video_info",
        "description": "Get YouTube video metadata (title, channel, thumbnail).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "YouTube video URL"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "youtube_batch_transcribe",
        "description": "Get transcripts for multiple YouTube videos at once.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "List of YouTube URLs"},
            },
            "required": ["urls"],
        },
    },
    {
        "name": "youtube_summarize",
        "description": "Create a summary and key points from YouTube transcript.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "transcript": {"type": "string", "description": "Transcript text"},
                "max_words": {"type": "integer", "description": "Max words in summary", "default": 500},
            },
            "required": ["transcript"],
        },
    },
    # ===== ENGINEERING INTELLIGENCE (engi-mcp) =====
    {
        "name": "engi_task_classify",
        "description": "Classify engineering task type (bug, feature, refactor, etc.) with confidence score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description"},
                "keywords": {"type": "array", "items": {"type": "string"}, "description": "Context keywords"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "engi_repo_scope_find",
        "description": "Find minimum relevant files for a task using repository index.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "Repository path"},
                "task": {"type": "string", "description": "Task description"},
                "task_type": {"type": "string", "enum": ["analysis", "feature", "bug", "poc", "documentation", "mixed"]},
                "limit": {"type": "integer", "description": "Max results", "default": 20},
            },
            "required": ["repo_path", "task"],
        },
    },
    {
        "name": "engi_flow_summarize",
        "description": "Get compact execution flow description (not raw code).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entry_point": {"type": "string", "description": "Main file or function"},
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Files to include"},
                "verbosity": {"type": "string", "enum": ["minimal", "standard", "detailed"], "description": "Detail level"},
            },
            "required": ["entry_point"],
        },
    },
    {
        "name": "engi_bug_trace",
        "description": "Pinpoint likely bug causes from symptom description.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Files to investigate"},
                "symptom": {"type": "string", "description": "Bug description"},
            },
            "required": ["scope", "symptom"],
        },
    },
    {
        "name": "engi_implementation_plan",
        "description": "Generate step-by-step implementation plan with edit targets and risk notes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description"},
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Files to modify"},
                "task_type": {"type": "string", "enum": ["bug", "feature", "refactor"], "description": "Task type"},
                "existing_patterns": {"type": "array", "items": {"type": "string"}, "description": "Patterns to follow"},
            },
            "required": ["task", "scope"],
        },
    },
    {
        "name": "engi_poc_plan",
        "description": "Scaffold minimum viable proof-of-concept.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "POC goal"},
                "existing_code": {"type": "array", "items": {"type": "string"}, "description": "Code to leverage"},
                "constraints": {"type": "array", "items": {"type": "string"}, "description": "Known constraints"},
            },
            "required": ["goal"],
        },
    },
    {
        "name": "engi_impact_analyze",
        "description": "Estimate blast radius before making edits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "array", "items": {"type": "string"}, "description": "Files being changed"},
                "change_type": {"type": "string", "enum": ["add", "modify", "delete"]},
            },
            "required": ["scope", "change_type"],
        },
    },
    {
        "name": "engi_test_select",
        "description": "Return minimum test set for changed files.",
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
        "name": "engi_doc_context_build",
        "description": "Build compact context for documentation (targeted at audience).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audience": {"type": "string", "enum": ["junior", "senior", "pm", "qa", "api"]},
                "changed_files": {"type": "array", "items": {"type": "string"}, "description": "Changed files"},
                "feature": {"type": "string", "description": "Feature being documented"},
            },
            "required": ["audience", "changed_files"],
        },
    },
    {
        "name": "engi_doc_update_plan",
        "description": "Identify which docs need updating after code changes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "changed_files": {"type": "array", "items": {"type": "string"}, "description": "Changed files"},
                "existing_docs": {"type": "array", "items": {"type": "string"}, "description": "Existing docs"},
            },
            "required": ["changed_files"],
        },
    },
    {
        "name": "engi_memory_checkpoint",
        "description": "Save task state for multi-session continuity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Unique task ID"},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Files in scope"},
                "modules": {"type": "array", "items": {"type": "string"}, "description": "Modules in scope"},
                "symbols": {"type": "array", "items": {"type": "string"}, "description": "Symbols in scope"},
                "notes": {"type": "string", "description": "Additional notes"},
                "pending_docs": {"type": "array", "items": {"type": "string"}, "description": "Pending docs"},
                "pending_validations": {"type": "array", "items": {"type": "string"}, "description": "Pending validations"},
                "decisions": {"type": "array", "items": {"type": "object"}, "description": "Decisions made"},
                "risks": {"type": "array", "items": {"type": "string"}, "description": "Identified risks"},
                "task_type": {"type": "string", "enum": ["analysis", "feature", "bug", "poc", "documentation", "mixed"]},
            },
            "required": ["task_id", "files"],
        },
    },
    {
        "name": "engi_memory_restore",
        "description": "Restore previously saved checkpoint by taskId.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID to restore"},
            },
            "required": ["task_id"],
        },
    },
]