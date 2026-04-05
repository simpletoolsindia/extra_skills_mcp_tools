"""YouTube Transcript MCP - Extract transcripts from YouTube videos for research."""

from __future__ import annotations

import os
import re
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False


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
    Get transcript from YouTube using caption extraction.

    Args:
        video_id: YouTube video ID
        lang: Language code (default: en)

    Returns:
        dict with keys: transcript, subtitles, error
    """
    if not HTTpx_AVAILABLE:
        return {"transcript": "", "subtitles": [], "error": "httpx not installed"}

    try:
        # Method 1: Use YouTube's caption API
        caption_url = f"https://youtubetranscript.com/?v={video_id}"

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(caption_url)

            if response.status_code == 200:
                # Parse transcript from response
                transcript = parse_transcript_response(response.text)
                if transcript:
                    return {"transcript": transcript, "subtitles": [], "error": None}

        return {"transcript": "", "subtitles": [], "error": "No transcript available"}

    except Exception as e:
        return {"transcript": "", "subtitles": [], "error": str(e)}


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


def get_video_info(video_id: str) -> dict:
    """
    Get basic video information.

    Args:
        video_id: YouTube video ID

    Returns:
        dict with keys: title, channel, description, error
    """
    if not HTTpx_AVAILABLE:
        return {"title": "", "channel": "", "description": "", "error": "httpx not installed"}

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
            "error": None,
        }
    except Exception as e:
        return {"title": "", "channel": "", "description": "", "error": str(e)}


def search_youtube(query: str, limit: int = 10) -> dict:
    """
    Search YouTube videos.

    Args:
        query: Search query
        limit: Max results

    Returns:
        dict with keys: videos (list), error
    """
    if not HTTpx_AVAILABLE:
        return {"videos": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            # Use YouTube search (requires proper headers for some endpoints)
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/json",
            }

            # Use Invidious instance for search (no API key required)
            invidious_instances = [
                "https://yewtu.be",
                "https://invidious.privacyredirect.com",
                "https://iv.nboeck.de",
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

            return {"videos": [], "error": "All search instances unavailable"}

    except Exception as e:
        return {"videos": [], "error": str(e)}


def get_transcript_from_url(url: str, lang: str = "en") -> dict:
    """
    Get transcript from YouTube URL.

    Args:
        url: YouTube video URL
        lang: Language code

    Returns:
        dict with keys: video_id, title, channel, transcript, error
    """
    video_id = extract_video_id(url)
    if not video_id:
        return {
            "video_id": "",
            "title": "",
            "channel": "",
            "transcript": "",
            "error": "Invalid YouTube URL",
        }

    # Get video info
    info = get_video_info(video_id)

    # Get transcript
    transcript_result = get_transcript_captions(video_id, lang)

    return {
        "video_id": video_id,
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "thumbnail": info.get("thumbnail", ""),
        "transcript": transcript_result.get("transcript", ""),
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

    if not HTTpx_AVAILABLE:
        return {"segments": [], "full_text": "", "error": "httpx not installed"}

    try:
        # Use Invidious API for timed transcripts
        with httpx.Client(timeout=30.0) as client:
            # Try to get captions with timestamps
            response = client.get(
                f"https://yewtu.be/api/v1/videos/{video_id}",
                params={"format": "json"},
            )

            if response.status_code == 200:
                data = response.json()

                # Check for captions/subtitles
                captions = data.get("captions", [])

                if captions:
                    # Process timed captions
                    segments = []
                    full_text_parts = []

                    for caption in captions:
                        start = caption.get("start", 0)
                        duration = caption.get("dur", 0)
                        text = caption.get("text", "")

                        segments.append({
                            "start": start,
                            "duration": duration,
                            "end": start + duration,
                            "text": text,
                            "timestamp": format_timestamp(start),
                        })
                        full_text_parts.append(text)

                    return {
                        "video_id": video_id,
                        "segments": segments,
                        "full_text": " ".join(full_text_parts),
                        "error": None,
                    }

                return {
                    "video_id": video_id,
                    "segments": [],
                    "full_text": "",
                    "error": "No captions available for this video",
                }

        return {"segments": [], "full_text": "", "error": "Failed to fetch video data"}

    except Exception as e:
        return {"segments": [], "full_text": "", "error": str(e)}


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