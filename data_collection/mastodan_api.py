import requests
from typing import Any, Dict, List, Optional


MASTODON_INSTANCE = "https://mastodon.social"


def search_mastodon_account(username: str) -> Optional[Dict[str, Any]]:
    """
    Search Mastodon for an account by username.
    """
    url = f"{MASTODON_INSTANCE}/api/v2/search"

    params = {
        "q": username,
        "type": "accounts",
        "limit": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        accounts = data.get("accounts", [])

        if not accounts:
            return None

        account = accounts[0]

        return {
            "id": account["id"],
            "username": account["username"],
            "display_name": account["display_name"],
            "bio": account["note"],
            "followers": account["followers_count"],
            "following": account["following_count"]
        }

    except Exception as exc:
        print(f"Mastodon search error: {exc}")
        return None


def get_mastodon_posts(user_id: str, limit: int = 10) -> List[str]:
    """
    Fetch recent posts from a Mastodon account.
    """
    url = f"{MASTODON_INSTANCE}/api/v1/accounts/{user_id}/statuses"

    params = {
        "limit": limit
    }

    posts: List[str] = []

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return posts

        statuses = response.json()

        for status in statuses:
            content = status.get("content")

            if content:
                posts.append(content)

        return posts

    except Exception as exc:
        print(f"Mastodon posts error: {exc}")
        return posts