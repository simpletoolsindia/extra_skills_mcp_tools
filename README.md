# 🦁 MCP Unified Server — 86 Tools for Agentic AI

> **The ultimate SELF-HOSTED MCP server for local LLMs, Claude Code, and AI agents.**
> **100% self-hosted infrastructure** — Your data never leaves your server.

[![GitHub](https://img.shields.io/github/stars/simpletoolsindia/extra_skills_mcp_tools?style=social)](https://github.com/simpletoolsindia/extra_skills_mcp_tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tools: 86](https://img.shields.io/badge/Tools-86-success?style=flat)](#features)

---

## 🎯 What is This?

This is a **100% SELF-HOSTED Model Context Protocol (MCP) server** that gives your AI assistant superpowers without compromising privacy:

- 🏠 **Self-Hosted Infrastructure** - SearXNG, Firecrawl, Playwright all run on YOUR server
- 🌐 **Web Search** - Privacy-respecting SearXNG search engine
- 📖 **Content Extraction** - Read any webpage, even JavaScript-heavy ones
- 📺 **YouTube Transcripts** - Get text from videos using free Invidious API
- 📰 **News & Articles** - Hacker News, Wikipedia, Freedium (Medium bypass)
- 🐙 **GitHub** - Explore repos, issues, code (free GitHub API)
- 💻 **Code Execution** - Run Python, JavaScript, Bash safely in sandbox
- 📊 **Data Analysis** - Pandas, Matplotlib charts, statistics
- 🧠 **Engineering Intelligence** - Bug tracing, planning, impact analysis
- 💾 **File System** - Read/write files safely with permissions
- 📝 **Document Conversion** - HTML ↔ Markdown
- 🤖 **Local LLM Gateway** - LiteLLM for local model access

---

## ⚡ Quick Start (5 Minutes)

### For Non-Technical Users

#### Step 1: Install Python
1. Go to [python.org/downloads](https://python.org/downloads)
2. Click the big yellow button "Download Python 3.12"
3. Run the downloaded file
4. **IMPORTANT**: Check "Add Python to PATH" ✅
5. Click "Install Now"

#### Step 2: Download This Project
1. Go to [github.com/simpletoolsindia/extra_skills_mcp_tools](https://github.com/simpletoolsindia/extra_skills_mcp_tools)
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to your Desktop

#### Step 3: Open Terminal
**Windows:**
- Press `Windows + R`
- Type `cmd` and press Enter

**Mac:**
- Press `Command + Space`
- Type `Terminal` and press Enter

**Linux:**
- Press `Ctrl + Alt + T`

#### Step 4: Install Dependencies
Copy and paste these commands (one at a time):

```bash
# Navigate to the project
cd Desktop/extra_skills_mcp_tools-main

# Create a virtual environment (keeps things organized)
python -m venv .venv

# Activate it (turn it on)
source .venv/bin/activate   # Mac/Linux
# or for Windows: .venv\Scripts\activate

# Install everything at once
pip install -e .
```

#### Step 5: Start the Server
```bash
# Start SearXNG (web search engine) - Port 7711
docker run -d -p 7711:8080 --name searxng searxng/searxng

# Start MCP Server
SEARXNG_BASE_URL=http://localhost:7711 python -m mcp_server
```

🎉 **You're done!** Your AI assistant can now use 86 tools!

---

## 📋 Detailed Installation (For Technical Users)

### Prerequisites
- Python 3.11 or higher
- Docker (for SearXNG web search)
- pip or uv package manager

### Installation Methods

#### Method 1: Clone & Install
```bash
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./install.sh
```

#### Method 2: Manual Install
```bash
# Create environment
python -m venv .venv
source .venv/bin/activate

# Install
pip install -e .

# Install optional tools
pip install matplotlib pandas numpy playwright scrapling
playwright install chromium
```

#### Method 3: Docker (Everything in One)
```bash
cd docker
docker-compose up -d
```

---

## 🔧 Claude Code Configuration

### Find Your Config File

**Windows:** `C:\Users\YourName\.claude\settings.json`
**Mac:** `/Users/YourName/.claude/settings.json`
**Linux:** `/home/YourName/.claude/settings.json`

### Add This Configuration

Open `settings.json` and add:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/path/to/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:7711",
        "FIRECRAWL_HOST": "http://localhost:7712",
        "PYTHONPATH": "/path/to/mcp-server/src"
      }
    }
  }
}
```

**Find your Python path:**
- Windows: `where python` (usually `C:\Python312\python.exe`)
- Mac/Linux: `which python3` (usually `/usr/local/bin/python3`)

---

## 🛠️ All 86 Tools (Complete Reference)

### 🏠 Self-Hosted Infrastructure

All core services run on YOUR server — no external APIs or cloud dependencies:

| Service | Purpose | Port | Docker Image | Resources |
|---------|---------|------|-------------|-----------|
| **SearXNG** | Privacy-respecting web search | 7711 | `searxng/searxng` | Lightweight |
| **Firecrawl** | Intelligent web scraping | 7712 | `firecrawl/mcp-server` | ⚠️ **Heavy** (6 CPU + 12GB) |
| **LiteLLM** | Local LLM gateway | 7713 | `ghcr.io/berriai/litellm` | Lightweight |
| **PostgreSQL** | Database | 7714 | `postgres:15-alpine` | Lightweight |
| **Redis** | Cache | 7715 | `redis:7-alpine` | Lightweight |
| **Playwright** | JS rendering | (local) | Built-in | Lightweight |
| **Scrapling** | Fast CSS extraction | (local) | Built-in | Lightweight |

**⚠️ Firecrawl is OPTIONAL** — Requires 6 CPU + 12GB RAM. For lightweight servers (Pi5), use built-in scrapers:
- **Playwright** — JS-heavy pages
- **Scrapling** — Fast CSS extraction
- **Webclaw** — Article extraction

**Docker Compose (One command to start everything):**
```bash
cd docker
docker-compose up -d
```

---

### 🔍 Category 1: Web Search (4 tools)

| Tool | What It Does | Example |
|------|--------------|---------|
| `searxng_search` | Search the web | `"Find Python tutorials"` |
| `search_images` | Find images | `"Cute cat pictures"` |
| `search_news` | Get news articles | `"AI news this week"` |
| `searxng_health` | Check if search works | (no input needed) |

**Setup for Search:** You need SearXNG running:
```bash
docker run -d -p 8888:8080 --name searxng searxng/searxng
```

---

### 🌐 Category 2: Web Scraping (10 tools) — ALL SELF-HOSTED

| Tool | What It Does | Example |
|------|--------------|---------|
| `fetch_web_content` | Get clean text from any URL | `"https://news.ycombinator.com"` |
| `scrape_dynamic` | Pages that need JavaScript (Playwright) | `"React app that loads content"` |
| `extract_structured` | Pull out articles/products (Scrapling) | "Parse product listings" |
| `scrape_freedium` | Read Medium articles free | `"https://freedium-mirror.cfd/ARTICLE_ID"` |
| `list_freedium_articles` | Browse free Medium articles | (no input needed) |
| `firecrawl_scrape` | Smart scraping (Firecrawl - OPTIONAL) | `"https://example.com"` |
| `firecrawl_crawl` | Scrape multiple pages (Firecrawl) | `"https://blog.com/posts"` |
| `webclaw_crawl` | Custom extraction patterns | `{url, selectors: {...}}` |
| `webclaw_extract_article` | Extract article content | `"https://medium.com/article"` |
| `browserbase_browse` | Fallback to Playwright | `"https://example.com"` |

**Lightweight Scraping (Default - Works on Pi5):**
```bash
# Playwright (for JS-heavy pages)
playwright install chromium

# Scrapling & Webclaw - already installed
```

**Optional Heavy Scraping (Requires 6 CPU + 12GB RAM):**
```bash
# Firecrawl self-hosting
docker run -d -p 7712:3002 --name firecrawl ghcr.io/mendableai/firecrawl/main
```

**Example - Get an Article:**
```python
{
  "name": "fetch_web_content",
  "arguments": {
    "url": "https://example.com/article",
    "max_length": 8000
  }
}
```

---

### 📰 Category 3: News & Research (12 tools)

#### Hacker News (7 tools)
| Tool | What It Does |
|------|--------------|
| `hackernews_top` | Get top stories |
| `hackernews_new` | Get newest stories |
| `hackernews_best` | Get best stories |
| `hackernews_ask` | Ask HN posts |
| `hackernews_show` | Show HN posts |
| `hackernews_get_comments` | Comments for a story |
| `hackernews_user` | User profile info |

**Example:**
```python
{"name": "hackernews_top", "arguments": {"limit": 10}}
```

#### Wikipedia (3 tools)
| Tool | What It Does |
|------|--------------|
| `wikipedia_search` | Search Wikipedia |
| `wikipedia_get_article` | Get article content |
| `wikipedia_related` | Related articles |

**Example:**
```python
{"name": "wikipedia_get_article", "arguments": {"title": "Python (programming language)", "extract_length": 2000}}
```

#### Hugging Face (4 tools)
| Tool | What It Does |
|------|--------------|
| `huggingface_search_models` | Find AI models |
| `huggingface_search_datasets` | Find datasets |
| `huggingface_model_info` | Model details |
| `huggingface_trending` | Trending models |

---

### 🐙 Category 4: GitHub (6 tools)

| Tool | What It Does | Example |
|------|--------------|---------|
| `github_repo` | Repository info | `{"owner": "facebook", "repo": "react"}` |
| `github_readme` | Get README | `{"owner": "openai", "repo": "chatgpt"}` |
| `github_issues` | List issues | `{"owner": "microsoft", "repo": "vscode"}` |
| `github_commits` | Recent commits | `{"owner": "tensorflow", "repo": "tensorflow"}` |
| `github_search_repos` | Search repos | `{"query": "machine learning"}` |
| `github_file_content` | Get file contents | `{"owner": "python", "repo": "cpython", "path": "README.md"}` |

**Setup (Optional):**
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

---

### 📁 Category 5: File System (5 tools)

| Tool | What It Does | Example |
|------|--------------|---------|
| `file_read` | Read a file | `{"path": "/home/user/notes.txt"}` |
| `file_write` | Write a file | `{"path": "/home/user/output.txt", "content": "Hello!"}` |
| `file_list` | List directory | `{"path": "/home/user/projects"}` |
| `file_info` | File details | `{"path": "/home/user/file.txt"}` |
| `file_search` | Search files | `{"directory": "/home/user", "pattern": "*.py"}` |

**Security:** Only safe extensions allowed (.txt, .md, .py, .js, .json, etc.)
**Protected paths:** /etc, /var, /usr, /System, /boot are blocked

---

### 💻 Category 6: Code Execution (3 tools)

| Tool | What It Does | Example |
|------|--------------|---------|
| `run_code` | Execute code safely | `{"code": "print('Hello!')", "language": "python"}` |
| `run_python_snippet` | Python with imports | `{"code": "print(math.pi)", "imports": ["math"]}` |
| `test_code_snippet` | Run & verify output | `{"code": "print(2+2)", "expected_output": "4"}` |

**Supported Languages:** Python, JavaScript (Node.js), Bash

**Security:** Blocks dangerous patterns (os.system, eval, exec, rm -rf, etc.)

**Example:**
```python
{
  "name": "run_code",
  "arguments": {
    "code": "import json\ndata = {'name': 'Alice', 'age': 30}\nprint(json.dumps(data, indent=2))",
    "language": "python",
    "timeout": 30
  }
}
```

---

### 📊 Category 7: Data Analysis (5 tools)

| Tool | What It Does |
|------|--------------|
| `pandas_create` | Create a DataFrame |
| `pandas_filter` | Filter with conditions |
| `pandas_aggregate` | Group and aggregate |
| `pandas_correlation` | Compute correlations |
| `pandas_outliers` | Detect outliers |

**Example - Filter Data:**
```python
{
  "name": "pandas_filter",
  "arguments": {
    "data": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
    "conditions": "{\"column\": \"age\", \"operator\": \">\", \"value\": 20}"
  }
}
```

---

### 📈 Category 8: Visualization (6 tools)

| Tool | What It Does |
|------|--------------|
| `plot_line` | Line charts |
| `plot_bar` | Bar charts |
| `plot_pie` | Pie charts |
| `plot_scatter` | Scatter plots |
| `plot_histogram` | Histograms |
| `generate_chart_spec` | Ant Design specs |

**Example - Bar Chart:**
```python
{
  "name": "plot_bar",
  "arguments": {
    "categories": ["Apple", "Banana", "Orange"],
    "values": [30, 45, 25],
    "title": "Fruit Sales"
  }
}
```

**Output:** Returns `base64_image` and `html` for embedding

---

### 📝 Category 9: Document Conversion (4 tools)

| Tool | What It Does |
|------|--------------|
| `markitdown_html_to_md` | HTML → Markdown |
| `markitdown_url_to_md` | URL → Markdown |
| `markitdown_file_to_md` | File → Markdown |
| `markitdown_md_to_html` | Markdown → HTML |

**Example:**
```python
{"name": "markitdown_url_to_md", "arguments": {"url": "https://example.com"}}
```

---

### 🧠 Category 10: Reasoning & Planning (5 tools)

| Tool | What It Does |
|------|--------------|
| `thinking_session_create` | Start thinking session |
| `thinking_step` | Add a thought |
| `thinking_revoke` | Revise previous thought |
| `thinking_summary` | Get session summary |
| `analyze_problem` | Structured analysis |

**Example - Problem Analysis:**
```python
{
  "name": "analyze_problem",
  "arguments": {
    "problem": "How to improve API performance?",
    "approach": "decompose"
  }
}
```

---

### 🔬 Category 11: Research (4 tools)

| Tool | What It Does |
|------|--------------|
| `research_start` | Start research session |
| `research_add_source` | Add information |
| `research_complete` | Add conclusion |
| `research_report` | Get full report |

---

### 📺 Category 12: YouTube (6 tools)

| Tool | What It Does | Example |
|------|--------------|---------|
| `youtube_transcript` | Get video transcript | `"https://youtube.com/watch?v=ABC123"` |
| `youtube_transcript_timed` | With timestamps | `"https://youtu.be/ABC123"` |
| `youtube_search` | Search videos | `{"query": "Python tutorial"}` |
| `youtube_video_info` | Video metadata | `"https://youtube.com/watch?v=ABC123"` |
| `youtube_batch_transcribe` | Multiple videos | `{"urls": ["url1", "url2"]}` |
| `youtube_summarize` | Create summary | `{"transcript": "...", "max_words": 500}` |

**Example - Get Transcript:**
```python
{
  "name": "youtube_transcript",
  "arguments": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }
}
```

---

### 🔧 Category 13: Engineering Intelligence (12 tools)

> 🎯 **97% token reduction** - Perfect for large codebases!

#### Analysis Tools (4)
| Tool | What It Does |
|------|--------------|
| `engi_task_classify` | Classify task (bug, feature, etc.) |
| `engi_repo_scope_find` | Find relevant files |
| `engi_flow_summarize` | Compact flow description |
| `engi_bug_trace` | Pinpoint bug causes |

#### Planning Tools (2)
| Tool | What It Does |
|------|--------------|
| `engi_implementation_plan` | Step-by-step plan |
| `engi_poc_plan` | Proof-of-concept scaffold |

#### Execution Tools (2)
| Tool | What It Does |
|------|--------------|
| `engi_impact_analyze` | Estimate blast radius |
| `engi_test_select` | Minimum test set |

#### Documentation Tools (2)
| Tool | What It Does |
|------|--------------|
| `engi_doc_context_build` | Build doc context |
| `engi_doc_update_plan` | Find docs to update |

#### Memory Tools (2)
| Tool | What It Does |
|------|--------------|
| `engi_memory_checkpoint` | Save task state |
| `engi_memory_restore` | Restore checkpoint |

**Example - Task Classification:**
```python
{
  "name": "engi_task_classify",
  "arguments": {
    "task": "Fix the login bug that crashes when password is empty",
    "keywords": ["authentication", "security"]
  }
}
```

**Output:**
```json
{"task_type": "bug", "confidence": 0.85, "reasoning": "Task contains bug-fix related keywords"}
```

---

### ⚙️ Category 14: System (1 tool)

| Tool | What It Does |
|------|--------------|
| `run_command` | Execute whitelisted commands |

**Allowed:** ls, cat, cp, mv, rm (with restrictions)

---

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_BASE_URL` | http://localhost:8888 | SearXNG search |
| `PLAYWRIGHT_HEADLESS` | true | Headless browser |
| `BROWSER_TIMEOUT` | 15 | Page load timeout |
| `GITHUB_TOKEN` | - | GitHub API token |
| `HF_TOKEN` | - | Hugging Face token |
| `FIRECRAWL_API_TOKEN` | - | Firecrawl API key |

---

## 🐳 Docker Deployment (Pi5/Dokploy)

### Deploy on Your Server

```bash
# 1. Clone
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# 2. SSL Certificates (Let's Encrypt)
sudo certbot certonly --standalone -d search.sridharhomelab.in

# 3. Copy certificates
sudo cp /etc/letsencrypt/live/search.sridharhomelab.in/fullchain.pem docker/nginx/certs/cert.pem
sudo cp /etc/letsencrypt/live/search.sridharhomelab.in/privkey.pem docker/nginx/certs/key.pem

# 4. Deploy
cd docker
docker-compose up -d
```

### Access URLs
- **Search:** https://search.sridharhomelab.in
- **API Gateway:** https://api.sridharhomelab.in

---

## 🔧 Troubleshooting

### "SearXNG not found" Error
```bash
# Start SearXNG
docker run -d -p 8888:8080 --name searxng searxng/searxng

# Check if running
curl http://localhost:8888/search?q=test&format=json
```

### "Module not found" Error
```bash
# Reinstall dependencies
pip install -e .
```

### "Permission denied" Error
```bash
# On Mac/Linux, make scripts executable
chmod +x install.sh
```

### Playwright Errors
```bash
# Install browser
playwright install chromium

# Or use pip
pip install playwright
python -m playwright install chromium
```

---

## 📊 Tool Count by Category

| # | Category | Tools |
|---|----------|-------|
| 1 | Web Search | 4 |
| 2 | Web Scraping | 10 |
| 3 | News & Research | 12 |
| 4 | GitHub | 6 |
| 5 | File System | 5 |
| 6 | Code Execution | 3 |
| 7 | Data Analysis | 5 |
| 8 | Visualization | 6 |
| 9 | Document Conversion | 4 |
| 10 | Reasoning | 5 |
| 11 | Research | 4 |
| 12 | YouTube | 6 |
| 13 | Engineering Intel | 12 |
| 14 | System | 1 |
| | **TOTAL** | **86** |

---

## 🎓 Example Usage

### Example 1: Research Task
```
User: Research the latest developments in AI agents

AI uses:
1. searxng_search("AI agents latest developments 2024")
2. wikipedia_search("AI agents")
3. hackernews_top(limit=10)
4. huggingface_trending(limit=10)
```

### Example 2: Bug Investigation
```
User: There's a bug in the login flow

AI uses:
1. engi_task_classify("Fix login crash when password is empty", ["login", "auth"])
2. engi_repo_scope_find("/path/to/project", "login bug", task_type="bug")
3. engi_bug_trace(["src/auth.py", "src/login.py"], "crashes when password empty")
4. engi_implementation_plan("Fix password validation", scope=["src/auth.py"])
5. engi_test_select(["src/auth.py"], "modify")
```

### Example 3: Video Research
```
User: Get me the transcript of this YouTube video

AI uses:
1. youtube_transcript("https://youtube.com/watch?v=XYZ123")
2. youtube_summarize(transcript, max_words=500)
```

### Example 4: Code Analysis
```
User: Analyze this Python project

AI uses:
1. file_list("/path/to/project")
2. engi_flow_summarize("main.py", verbosity="standard")
3. engi_impact_analyze(["src/core.py"], "modify")
```

---

## 📞 Support

- **GitHub Issues:** [github.com/simpletoolsindia/extra_skills_mcp_tools/issues](https://github.com/simpletoolsindia/extra_skills_mcp_tools/issues)
- **Documentation:** [github.com/simpletoolsindia/extra_skills_mcp_tools#readme](https://github.com/simpletoolsindia/extra_skills_mcp_tools#readme)
- **NPM Package:** [@simpletoolsindiaorg/engi-mcp](https://www.npmjs.com/package/@simpletoolsindiaorg/engi-mcp)

---

## 📄 License

MIT License - Use it freely for personal and commercial projects.

---

## 🙏 Credits

Built with ❤️ for the AI agent community.

Tools inspired by:
- [SearXNG](https://searxng.org/) - Privacy-respecting search
- [Playwright](https://playwright.dev/) - Browser automation
- [Pandas](https://pandas.pydata.org/) - Data analysis
- [Matplotlib](https://matplotlib.org/) - Visualization
- [@simpletoolsindiaorg/engi-mcp](https://www.npmjs.com/package/@simpletoolsindiaorg/engi-mcp) - Engineering intelligence

---

<div align="center">

**If this helped you, give it a ⭐ on GitHub!**

</div>