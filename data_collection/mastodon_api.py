import re
import requests
from typing import Any, Dict, List, Optional


MASTODON_INSTANCE = "https://mastodon.social"


def strip_html(text: str) -> str:
    """Remove simple HTML tags from Mastodon bios/posts."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


def normalise_handle(handle: str) -> str:
    """
    Convert input like:
    - xgh
    - @xgh
    - xgh@mastodon.social
    - @xgh@mastodon.social
    into a clean handle string.
    """
    return handle.strip().lstrip("@")


def search_mastodon_account(handle: str) -> Optional[Dict[str, Any]]:
    """
    Search Mastodon for an account and prefer an exact acct/username match.

    Best results come from using a full handle such as:
    xgh@mastodon.social
    """
    clean_handle = normalise_handle(handle)

    url = f"{MASTODON_INSTANCE}/api/v2/search"
    params = {
        "q": clean_handle,
        "type": "accounts",
        "limit": 10,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"Mastodon search returned status {response.status_code}")
            return None

        data = response.json()
        accounts = data.get("accounts", [])

        if not accounts:
            return None

        requested_username = clean_handle.split("@")[0].lower()
        requested_acct = clean_handle.lower()

        # 1. Exact acct match first
        for account in accounts:
            acct = (account.get("acct") or "").lower()
            username = (account.get("username") or "").lower()

            if acct == requested_acct or username == requested_acct:
                return format_account(account)

        # 2. Exact username match if full acct not found
        for account in accounts:
            username = (account.get("username") or "").lower()
            if username == requested_username:
                return format_account(account)

        # 3. Fall back to first result if nothing exact matched
        return format_account(accounts[0])

    except Exception as exc:
        print(f"Mastodon search error: {exc}")
        return None


def format_account(account: Dict[str, Any]) -> Dict[str, Any]:
    """Convert raw API account object into a cleaner structure."""
    return {
        "id": account.get("id"),
        "username": account.get("username", ""),
        "acct": account.get("acct", ""),
        "display_name": account.get("display_name", ""),
        "bio": strip_html(account.get("note", "")),
        "followers": account.get("followers_count", 0),
        "following": account.get("following_count", 0),
        "url": account.get("url", ""),
    }


def get_mastodon_posts(user_id: str, limit: int = 10) -> List[str]:
    """
    Fetch recent public posts from a Mastodon account.
    """
    url = f"{MASTODON_INSTANCE}/api/v1/accounts/{user_id}/statuses"
    params = {"limit": limit}

    posts: List[str] = []

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"Mastodon posts returned status {response.status_code}")
            return posts

        statuses = response.json()

        for status in statuses:
            content = strip_html(status.get("content", ""))
            if content:
                posts.append(content)

        return posts

    except Exception as exc:
        print(f"Mastodon posts error: {exc}")
        return posts
    
def get_mastodon_post_timestamps(user_id: str, limit: int = 40) -> List[str]:
    url = f"{MASTODON_INSTANCE}/api/v1/accounts/{user_id}/statuses"
    params = {"limit": limit}
    timestamps: List[str] = []

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Mastodon timestamps returned status {response.status_code}")
            return timestamps

        statuses = response.json()

        for status in statuses:
            created_at = status.get("created_at")
            if created_at:
                timestamps.append(created_at)

        return timestamps

    except Exception as exc:
        print(f"Mastodon timestamp fetch error: {exc}")
        return timestamps