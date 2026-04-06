"""YouTube Transcript MCP - Extract transcripts from YouTube videos for research."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False

# Check if yt-dlp is available
YTDLP_AVAILABLE = False
try:
    result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        YTDLP_AVAILABLE = True
except Exception:
    pass


YOUTUBE_TRANSCRIPT_API = "https://youtubetranscript.com"
YT_WIDGET_API = "https://www.youtube.com/youtubei/v1/widgets"


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:v=|/v/|/embed/)([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript_captions(video_id: str, lang: str = "en") -> dict:
    """
    Get transcript from YouTube using multiple methods.

    Args:
        video_id: YouTube video ID
        lang: Language code (default: en)

    Returns:
        dict with keys: transcript, subtitles, error
    """
    if not HTTpx_AVAILABLE:
        return {"transcript": "", "subtitles": [], "error": "httpx not installed"}

    # Method 1: Try YouTube's transcript API via invidious
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            # Use Invidious to get captions
            for instance in ["https://yewtu.be", "https://invidious.privacyredirect.com"]:
                try:
                    response = client.get(
                        f"{instance}/api/v1/captions/{video_id}",
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("captions"):
                            transcript_parts = []
                            for cap in data["captions"]:
                                transcript_parts.append(cap.get("text", ""))
                            if transcript_parts:
                                return {"transcript": " ".join(transcript_parts), "subtitles": [], "error": None}
                except Exception:
                    continue
    except Exception as e:
        pass

    # Method 2: Try Google translate captions API
    try:
        with httpx.Client(timeout=30.0) as client:
            # Try YouTube's caption endpoint
            caption_url = f"https://youtubetranscript.com/?v={video_id}"
            response = client.get(caption_url)
            if response.status_code == 200:
                transcript = parse_transcript_response(response.text)
                if transcript and len(transcript) > 50:
                    return {"transcript": transcript, "subtitles": [], "error": None}
    except Exception:
        pass

    # Method 3: Try fetching auto-generated captions directly
    try:
        with httpx.Client(timeout=30.0) as client:
            # YouTube auto-generated captions
            response = client.get(
                f"https://subtitle.tools/?url=https://www.youtube.com/watch?v={video_id}&format=json",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("subtitles"):
                        parts = [s.get("text", "") for s in data["subtitles"]]
                        return {"transcript": " ".join(parts), "subtitles": [], "error": None}
                except Exception:
                    pass
    except Exception:
        pass

    return {"transcript": "", "subtitles": [], "error": "No transcript available - video may not have captions"}


def get_transcript_ytdlp(video_id: str, lang: str = "en") -> dict:
    """
    Get transcript using yt-dlp (most reliable method).

    Args:
        video_id: YouTube video ID
        lang: Language code (default: en)

    Returns:
        dict with keys: transcript, segments, error
    """
    if not YTDLP_AVAILABLE:
        return {"transcript": "", "segments": [], "error": "yt-dlp not installed"}

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract transcript using yt-dlp with VTT format
            output_template = os.path.join(tmpdir, "caption")
            cmd = [
                "yt-dlp",
                "--write-auto-subs",
                "--write-subs",
                "--sub-lang", f"{lang},{lang}-US,{lang}-GB,en",
                "--skip-download",
                "--output", output_template,
                f"https://www.youtube.com/watch?v={video_id}",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Find the subtitle file (vtt or srt)
            vtt_files = [f for f in os.listdir(tmpdir) if f.endswith(".vtt")]
            srt_files = [f for f in os.listdir(tmpdir) if f.endswith(".srt")]

            subtitle_file = None
            if vtt_files:
                subtitle_file = os.path.join(tmpdir, vtt_files[0])
            elif srt_files:
                subtitle_file = os.path.join(tmpdir, srt_files[0])

            if subtitle_file:
                with open(subtitle_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse VTT format
                if subtitle_file.endswith(".vtt"):
                    segments, transcript = parse_vtt(content)
                else:
                    # Parse SRT format
                    segments, transcript = parse_srt(content)

                if segments or transcript:
                    return {
                        "transcript": transcript,
                        "segments": segments,
                        "error": None,
                    }

            return {"transcript": "", "segments": [], "error": "No captions found"}

    except subprocess.TimeoutExpired:
        return {"transcript": "", "segments": [], "error": "Timeout extracting transcript"}
    except Exception as e:
        return {"transcript": "", "segments": [], "error": str(e)}


def parse_vtt(content: str) -> tuple:
    """Parse VTT subtitle content."""
    segments = []
    transcript_parts = []

    lines = content.strip().split("\n")
    i = 0
    # Skip header
    while i < len(lines) and "WEBVTT" not in lines[i]:
        i += 1
    i += 1

    while i < len(lines):
        line = lines[i].strip()

        # Check for timestamp line
        if "-->" in line:
            try:
                start, end = line.split("-->")
                start = start.strip().replace(",", ".")
                end = end.strip().replace(",", ".")

                # Parse start time
                parts = start.split(":")
                if len(parts) == 3:
                    start_sec = (
                        int(parts[0]) * 3600 +
                        int(parts[1]) * 60 +
                        float(parts[2])
                    )
                elif len(parts) == 2:
                    start_sec = int(parts[0]) * 60 + float(parts[1])
                else:
                    start_sec = 0

                # Collect text lines until empty line
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1

                text = " ".join(text_lines)
                if text:
                    segments.append({
                        "start": start_sec,
                        "text": text,
                        "timestamp": format_timestamp(start_sec),
                    })
                    transcript_parts.append(text)
            except Exception:
                pass
        i += 1

    return segments, " ".join(transcript_parts)


def parse_srt(content: str) -> tuple:
    """Parse SRT subtitle content."""
    segments = []
    transcript_parts = []

    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 2:
            try:
                # Second line is timestamp
                if "-->" in lines[1]:
                    start, end = lines[1].split("-->")
                    parts = start.strip().replace(",", ".").split(":")
                    if len(parts) == 3:
                        start_sec = (
                            int(parts[0]) * 3600 +
                            int(parts[1]) * 60 +
                            float(parts[2])
                        )
                    else:
                        start_sec = 0

                    text = " ".join(lines[2:])
                    if text:
                        segments.append({
                            "start": start_sec,
                            "text": text,
                            "timestamp": format_timestamp(start_sec),
                        })
                        transcript_parts.append(text)
            except Exception:
                pass

    return segments, " ".join(transcript_parts)


def parse_transcript_response(html: str) -> str:
    """Parse transcript from HTML response."""
    # Simple extraction - in production use proper parsing
    lines = []
    # Look for transcript segments
    pattern = r'<p class="transcript-segment[^"]*">(.*?)</p>'
    matches = re.findall(pattern, html, re.DOTALL)
    for match in matches:
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', match)
        if text.strip():
            lines.append(text.strip())

    if lines:
        return ' '.join(lines)

    # Fallback: extract from any paragraph-like content
    pattern = r'>([^<]{20,})<'
    matches = re.findall(pattern, html)
    return ' '.join(m.strip() for m in matches if len(m.strip()) > 10)


def get_video_info(video_id: str = None, url: str = None) -> dict:
    """
    Get basic video information.

    Args:
        video_id: YouTube video ID (11 chars)
        url: Video URL (alternative to video_id)

    Returns:
        dict with keys: title, channel, thumbnail, video_id, error
    """
    # Extract video_id from url if provided
    if not video_id and url:
        video_id = extract_video_id(url)

    if not video_id:
        return {"title": "", "channel": "", "thumbnail": "", "video_id": "", "error": "No video_id provided"}

    if not HTTpx_AVAILABLE:
        return {"title": "", "channel": "", "thumbnail": "", "video_id": video_id, "error": "httpx not installed"}

    try:
        # Use YouTube oEmbed API
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                "https://www.youtube.com/oembed",
                params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            )
            response.raise_for_status()

        data = response.json()
        return {
            "title": data.get("title", ""),
            "channel": data.get("author_name", ""),
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "video_id": video_id,
            "error": None,
        }
    except Exception as e:
        return {"title": "", "channel": "", "thumbnail": "", "video_id": video_id, "error": str(e)}


def search_youtube(query: str, limit: int = 10) -> dict:
    """
    Search YouTube videos (bypasses API rate limits).

    Tries methods in order:
    1. RSS feed (fast, may be blocked)
    2. Playwright (reliable, uses thread pool)
    3. Invidious (fallback)

    Args:
        query: Search query
        limit: Max results

    Returns:
        dict with keys: videos (list), error
    """
    # Method 1: Try RSS feed
    rss_result = search_youtube_rss(query, limit)
    if rss_result.get("videos"):
        return rss_result

    # Method 2: Try Playwright (thread pool to avoid asyncio conflicts)
    playwright_result = search_youtube_playwright(query, limit)
    if playwright_result.get("videos"):
        return playwright_result

    # Method 3: Fallback to Invidious
    if not HTTpx_AVAILABLE:
        return {"videos": [], "error": "All search methods failed"}

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/json",
            }

            # Try multiple Invidious instances
            invidious_instances = [
                "https://yewtu.be",
                "https://invidious.privacyredirect.com",
                "https://iv.nboeck.de",
                "https://invidious.kavin.rocks",
            ]

            for instance in invidious_instances:
                try:
                    response = client.get(
                        f"{instance}/api/v1/search",
                        params={"q": query, "type": "video", "limit": limit},
                        headers=headers,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        videos = []

                        for item in data[:limit]:
                            videos.append({
                                "videoId": item.get("videoId", ""),
                                "title": item.get("title", ""),
                                "author": item.get("author", ""),
                                "description": item.get("description", "")[:200],
                                "duration": item.get("lengthSeconds", 0),
                                "viewCount": item.get("viewCount", 0),
                                "publishedText": item.get("publishedText", ""),
                                "url": f"https://youtube.com/watch?v={item.get('videoId', '')}",
                            })

                        return {"videos": videos, "error": None}

                except Exception:
                    continue

            return {"videos": [], "error": "All search methods unavailable"}

    except Exception as e:
        return {"videos": [], "error": str(e)}


def search_youtube_playwright(query: str, limit: int = 10) -> dict:
    """
    Search YouTube videos using local Playwright (bypasses API rate limits).
    Uses thread pool to avoid asyncio conflicts.

    Args:
        query: Search query
        limit: Max results

    Returns:
        dict with keys: videos (list), error
    """
    import asyncio
    import concurrent.futures

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"videos": [], "error": "Playwright not installed"}

    def _search_sync(q: str, lim: int) -> dict:
        """Sync search inside thread."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                search_url = f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}"
                page.goto(search_url, wait_until="networkidle", timeout=45000)

                try:
                    page.wait_for_selector("ytd-video-renderer", timeout=15000)
                except Exception:
                    browser.close()
                    return {"videos": [], "error": "No search results found"}

                videos = []
                items = page.query_selector_all("ytd-video-renderer")

                for item in items[:lim]:
                    try:
                        title_el = item.query_selector("yt-formatted-string")
                        title = title_el.inner_text().strip() if title_el else ""

                        link_el = item.query_selector("a#video-title")
                        href = link_el.get_attribute("href") if link_el else ""
                        video_id = ""
                        if href:
                            import re
                            match = re.search(r"[?&]v=([^&]+)", href)
                            if match:
                                video_id = match.group(1)

                        channel_el = item.query_selector("#channel-name a")
                        channel = channel_el.inner_text().strip() if channel_el else ""

                        metadata_els = item.query_selector_all("#metadata-line span")
                        metadata = [el.inner_text() for el in metadata_els] if metadata_els else []

                        duration_el = item.query_selector("#time")
                        duration = duration_el.inner_text().strip() if duration_el else ""

                        if video_id and title:
                            videos.append({
                                "videoId": video_id,
                                "title": title,
                                "author": channel,
                                "url": f"https://youtube.com/watch?v={video_id}",
                                "description": "",
                                "duration": duration,
                                "viewCount": metadata[0] if metadata else "",
                                "publishedText": metadata[1] if len(metadata) > 1 else "",
                            })
                    except Exception:
                        continue

                browser.close()
                return {"videos": videos, "error": None if videos else "No videos extracted"}
        except Exception as e:
            return {"videos": [], "error": f"Playwright error: {str(e)}"}

    try:
        # Run in thread pool to avoid asyncio conflicts
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_search_sync, query, limit)
            result = future.result(timeout=60)
        return result
    except concurrent.futures.TimeoutError:
        return {"videos": [], "error": "Playwright search timeout"}
    except Exception as e:
        return {"videos": [], "error": f"Thread pool error: {str(e)}"}


def search_youtube_rss(query: str, limit: int = 10) -> dict:
    """
    Search YouTube via RSS feed (no API required, bypasses rate limits).

    Args:
        query: Search query
        limit: Max results

    Returns:
        dict with keys: videos (list), error
    """
    if not HTTpx_AVAILABLE:
        return {"videos": [], "error": "httpx not available"}

    try:
        import httpx
        import xml.etree.ElementTree as ET

        # YouTube search via RSS
        search_url = f"https://www.youtube.com/feeds/videos.xml?search_query={query}&max_results={limit}"

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(search_url, headers={"User-Agent": "Mozilla/5.0"})

            if response.status_code != 200:
                return {"videos": [], "error": f"RSS failed: {response.status_code}"}

            # Parse RSS/Atom feed
            root = ET.fromstring(response.text)

            # Handle Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

            videos = []
            for entry in root.findall('.//atom:entry', ns) or root.findall('.//entry'):
                try:
                    video_id = ""
                    # Try to get video ID from various locations
                    for link in entry.findall('.//atom:link', ns) or entry.findall('.//link'):
                        href = link.get('href', '')
                        if '/watch?v=' in href:
                            match = re.search(r'v=([^&]+)', href)
                            if match:
                                video_id = match.group(1)
                                break

                    title = ""
                    for t in entry.findall('.//atom:title', ns) or entry.findall('.//title'):
                        if t.text:
                            title = t.text.strip()
                            break

                    author = ""
                    for author_el in entry.findall('.//atom:name', ns) or entry.findall('.//author/name') or entry.findall('.//author'):
                        if author_el.text:
                            author = author_el.text.strip()
                            break

                    published = ""
                    for pub in entry.findall('.//atom:published', ns) or entry.findall('.//published'):
                        if pub.text:
                            published = pub.text
                            break

                    if video_id:
                        videos.append({
                            "videoId": video_id,
                            "title": title,
                            "author": author,
                            "url": f"https://youtube.com/watch?v={video_id}",
                            "description": "",
                            "duration": "",
                            "viewCount": "",
                            "publishedText": published[:10] if published else "",
                        })

                    if len(videos) >= limit:
                        break

                except Exception:
                    continue

            if videos:
                return {"videos": videos, "error": None}
            return {"videos": [], "error": "No videos found in RSS feed"}

    except Exception as e:
        return {"videos": [], "error": f"RSS search error: {str(e)}"}


def get_transcript_from_url(url: str, lang: str = "en") -> dict:
    """
    Get transcript from YouTube URL.

    Args:
        url: YouTube video URL
        lang: Language code

    Returns:
        dict with keys: video_id, title, channel, transcript, segments, error
    """
    video_id = extract_video_id(url)
    if not video_id:
        return {
            "video_id": "",
            "title": "",
            "channel": "",
            "transcript": "",
            "segments": [],
            "error": "Invalid YouTube URL",
        }

    # Get video info
    info = get_video_info(video_id)

    # Try yt-dlp first (most reliable)
    if YTDLP_AVAILABLE:
        transcript_result = get_transcript_ytdlp(video_id, lang)
        if transcript_result.get("transcript"):
            return {
                "video_id": video_id,
                "title": info.get("title", ""),
                "channel": info.get("channel", ""),
                "thumbnail": info.get("thumbnail", ""),
                "transcript": transcript_result.get("transcript", ""),
                "segments": transcript_result.get("segments", []),
                "error": None,
            }

    # Fallback to httpx methods
    transcript_result = get_transcript_captions(video_id, lang)

    return {
        "video_id": video_id,
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "thumbnail": info.get("thumbnail", ""),
        "transcript": transcript_result.get("transcript", ""),
        "segments": [],
        "error": transcript_result.get("error") or info.get("error"),
    }


def get_transcript_with_timestamp(url: str) -> dict:
    """
    Get transcript with timestamps for better context.

    Args:
        url: YouTube video URL

    Returns:
        dict with keys: segments (list), full_text, error
    """
    video_id = extract_video_id(url)
    if not video_id:
        return {"segments": [], "full_text": "", "error": "Invalid URL"}

    # Try yt-dlp first (most reliable)
    if YTDLP_AVAILABLE:
        result = get_transcript_ytdlp(video_id, "en")
        if result.get("segments"):
            return {
                "video_id": video_id,
                "segments": result.get("segments", []),
                "full_text": result.get("transcript", ""),
                "error": None,
            }

    # Fallback to httpx methods if yt-dlp not available or failed
    if not HTTpx_AVAILABLE:
        return {"segments": [], "full_text": "", "error": "httpx not installed and yt-dlp not available"}

    # Try multiple Invidious instances
    instances = [
        "https://yewtu.be",
        "https://invidious.privacyredirect.com",
        "https://iv.nboeck.de",
        "https://invidious.kavin.rocks",
    ]

    for instance in instances:
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                # Get video data with captions
                response = client.get(
                    f"{instance}/api/v1/videos/{video_id}",
                    params={"format": "json"},
                    headers={"User-Agent": "Mozilla/5.0"},
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check for captions/subtitles
                    captions = data.get("captions", [])
                    subtitles = data.get("subtitles", [])

                    all_captions = captions + subtitles

                    if all_captions:
                        segments = []
                        full_text_parts = []

                        for caption in all_captions:
                            start = float(caption.get("start", 0))
                            duration = float(caption.get("dur", caption.get("duration", 3)))
                            text = caption.get("text", "")

                            if text.strip():
                                segments.append({
                                    "start": start,
                                    "duration": duration,
                                    "end": start + duration,
                                    "text": text.strip(),
                                    "timestamp": format_timestamp(start),
                                })
                                full_text_parts.append(text.strip())

                        if segments:
                            return {
                                "video_id": video_id,
                                "segments": segments,
                                "full_text": " ".join(full_text_parts),
                                "error": None,
                            }

        except Exception:
            continue

    # Fallback: Try YouTube's direct caption API
    try:
        with httpx.Client(timeout=30.0) as client:
            # Try to get auto-generated captions
            for lang_code in ["en", "en-US", "en-GB"]:
                response = client.get(
                    f"https://video.google.com/timedtext?type=list&v={video_id}",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                if response.status_code == 200 and response.text:
                    # Parse available caption tracks
                    import xml.etree.ElementTree as ET
                    try:
                        root = ET.fromstring(response.text)
                        for track in root.findall(".//track"):
                            track_lang = track.get("lang_code", "")
                            if track_lang.startswith("en"):
                                name = track.get("name", "")
                                # Get timed text
                                timed_response = client.get(
                                    f"https://video.google.com/timedtext?v={video_id}&lang={track_lang}&name={name}"
                                )
                                if timed_response.status_code == 200:
                                    text_content = parse_ttml_transcript(timed_response.text)
                                    if text_content:
                                        return {
                                            "video_id": video_id,
                                            "segments": [],
                                            "full_text": text_content,
                                            "error": None,
                                        }
                    except Exception:
                        pass
    except Exception:
        pass

    return {
        "video_id": video_id,
        "segments": [],
        "full_text": "",
        "error": "No captions available - video may not have auto-generated captions enabled"
    }


def parse_ttml_transcript(xml_content: str) -> str:
    """Parse TTML/XML transcript to plain text."""
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)
        text_parts = []
        for p in root.iter():
            if p.text:
                text_parts.append(p.text.strip())
            for child in p:
                if child.tail:
                    text_parts.append(child.tail.strip())
        return " ".join(t for t in text_parts if t)
    except Exception:
        return ""


def format_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def summarize_transcript(transcript: str, max_words: int = 500) -> dict:
    """
    Create a summary of transcript (placeholder for LLM integration).

    Args:
        transcript: Full transcript text
        max_words: Max words in summary

    Returns:
        dict with keys: summary, key_points, error
    """
    if not transcript:
        return {"summary": "", "key_points": [], "error": "No transcript provided"}

    # Simple extraction - in production, use LLM for summarization
    sentences = transcript.split(".")
    key_points = []

    # Extract sentences with important keywords
    important_keywords = ["important", "key", "main", "significant", "result", "conclusion", "found", "discovered"]

    for sent in sentences:
        sent = sent.strip()
        if len(sent) > 50:
            # Check for key phrases
            if any(kw in sent.lower() for kw in important_keywords):
                key_points.append(sent)
            elif len(key_points) < 5:
                key_points.append(sent)

    summary = f"Transcript summary ({len(transcript.split())} words total):\n\n"
    summary += " ".join(key_points[:10]) if key_points else transcript[:max_words]

    return {
        "summary": summary,
        "key_points": key_points[:10],
        "word_count": len(transcript.split()),
        "error": None,
    }


def batch_transcribe(urls: List[str]) -> dict:
    """
    Get transcripts for multiple videos.

    Args:
        urls: List of YouTube URLs

    Returns:
        dict with keys: results (list), error
    """
    results = []
    for url in urls:
        result = get_transcript_from_url(url)
        results.append({
            "url": url,
            "video_id": result.get("video_id"),
            "title": result.get("title"),
            "transcript_length": len(result.get("transcript", "")),
            "success": bool(result.get("transcript")),
            "error": result.get("error"),
        })

    return {
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "error": None,
    }