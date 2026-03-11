import requests
from typing import Optional, Dict, Any


GITHUB_API_URL = "https://api.github.com/users"


def get_github_profile(username: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a public GitHub profile by username.
    Returns a dictionary if found, otherwise None.
    """
    url = f"{GITHUB_API_URL}/{username}"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            return None

        print(f"GitHub API returned status code {response.status_code}.")
        return None

    except requests.RequestException as exc:
        print(f"Error contacting GitHub API: {exc}")
        return None