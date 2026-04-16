import requests
from typing import Any, Dict, List, Optional

YOUTUBE_API_KEY = "AIzaSyB0bo1FPPCAM3Uyil-kr61V4ZRlsGzodts"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def get_youtube_channel(channel_query: str) -> Optional[Dict[str, Any]]:
    """
    Search for a YouTube channel by username/channel name.
    Returns basic channel info if found.
    """
    url = f"{YOUTUBE_API_BASE}/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "q": channel_query,
        "part": "snippet",
        "type": "channel",
        "maxResults": 5,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"YouTube channel search returned status {response.status_code}")
            return None

        items = response.json().get("items", [])
        if not items:
            return None

        first = items[0]
        snippet = first.get("snippet", {})
        channel_id = snippet.get("channelId")

        return {
            "channel_id": channel_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
        }

    except Exception as exc:
        print(f"YouTube channel search error: {exc}")
        return None


def get_youtube_videos(channel_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch recent public videos from a channel.
    """
    url = f"{YOUTUBE_API_BASE}/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "type": "video",
        "maxResults": limit,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"YouTube videos returned status {response.status_code}")
            return []

        return response.json().get("items", [])

    except Exception as exc:
        print(f"YouTube video fetch error: {exc}")
        return []


def extract_youtube_features(videos: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Extract simple text and timestamp features from YouTube videos.
    """
    titles: List[str] = []
    descriptions: List[str] = []
    timestamps: List[str] = []

    for video in videos:
        snippet = video.get("snippet", {})

        title = snippet.get("title")
        description = snippet.get("description")
        published_at = snippet.get("publishedAt")

        if title:
            titles.append(title)
        if description:
            descriptions.append(description)
        if published_at:
            timestamps.append(published_at)

    return {
        "titles": titles,
        "descriptions": descriptions,
        "timestamps": timestamps,
    }