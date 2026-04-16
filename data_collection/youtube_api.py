import re
import requests
from typing import Any, Dict, List, Optional

YOUTUBE_API_KEY = "AIzaSyB0bo1FPPCAM3Uyil-kr61V4ZRlsGzodts"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def normalise_youtube_input(value: str) -> str:
    return (value or "").strip()


def extract_channel_id_from_url(value: str) -> Optional[str]:
    """
    Supports:
    https://www.youtube.com/channel/UCxxxx
    """
    match = re.search(r"(?:youtube\.com/channel/)([A-Za-z0-9_-]+)", value)
    if match:
        return match.group(1)
    return None


def extract_handle_from_input(value: str) -> Optional[str]:
    """
    Supports:
    @name
    https://www.youtube.com/@name
    """
    value = normalise_youtube_input(value)

    # Direct handle input
    if value.startswith("@"):
        return value[1:]

    # URL with @handle
    match = re.search(r"(?:youtube\.com/@)([A-Za-z0-9._-]+)", value)
    if match:
        return match.group(1)

    return None


def get_channel_by_id(channel_id: str) -> Optional[Dict[str, Any]]:
    url = f"{YOUTUBE_API_BASE}/channels"
    params = {
        "key": YOUTUBE_API_KEY,
        "id": channel_id,
        "part": "snippet",
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"YouTube channel lookup by ID returned status {response.status_code}")
            print(response.text)
            return None

        items = response.json().get("items", [])
        if not items:
            return None

        snippet = items[0].get("snippet", {})

        return {
            "channel_id": channel_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
        }

    except Exception as exc:
        print(f"YouTube channel lookup by ID error: {exc}")
        return None


def search_channel_by_query(query: str) -> Optional[Dict[str, Any]]:
    url = f"{YOUTUBE_API_BASE}/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "q": query,
        "part": "snippet",
        "type": "channel",
        "maxResults": 10,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"YouTube channel search returned status {response.status_code}")
            print(response.text)
            return None

        items = response.json().get("items", [])
        if not items:
            print("No YouTube channel results found.")
            return None

        clean_query = query.lower().strip()
        selected = None

        # Prefer closer title match instead of blindly taking first result
        for item in items:
            snippet = item.get("snippet", {})
            title = (snippet.get("title") or "").lower().strip()
            if clean_query == title or clean_query in title:
                selected = item
                break

        if selected is None:
            selected = items[0]

        snippet = selected.get("snippet", {})
        channel_id = snippet.get("channelId")

        if not channel_id:
            return None

        # Fetch full channel details
        return get_channel_by_id(channel_id)

    except Exception as exc:
        print(f"YouTube channel search error: {exc}")
        return None


def get_youtube_channel(channel_input: str) -> Optional[Dict[str, Any]]:
    """
    Accepts:
    - channel search text: NetworkChuck
    - @handle: @NetworkChuck
    - handle URL: https://www.youtube.com/@NetworkChuck
    - channel ID URL: https://www.youtube.com/channel/UC...
    """
    clean_input = normalise_youtube_input(channel_input)
    if not clean_input:
        return None

    # 1. Direct channel ID URL
    channel_id = extract_channel_id_from_url(clean_input)
    if channel_id:
        return get_channel_by_id(channel_id)

    # 2. Handle or handle URL
    handle = extract_handle_from_input(clean_input)
    if handle:
        # Search by handle text
        result = search_channel_by_query(handle)
        if result:
            return result

    # 3. Fallback to generic search text
    return search_channel_by_query(clean_input)


def get_youtube_videos(channel_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch recent public videos from a YouTube channel.
    """
    if not channel_id:
        return []

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
            print(response.text)
            return []

        return response.json().get("items", [])

    except Exception as exc:
        print(f"YouTube video fetch error: {exc}")
        return []


def extract_youtube_features(videos: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Extract titles, descriptions, and timestamps from video results.
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