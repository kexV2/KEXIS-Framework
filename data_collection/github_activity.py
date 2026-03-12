import requests
from typing import Any, Dict, List

GITHUB_API_BASE = "https://api.github.com"


def get_user_repos(username: str) -> List[Dict[str, Any]]:
    """Fetch public repositories for a GitHub user."""
    url = f"{GITHUB_API_BASE}/users/{username}/repos"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()

        print(f"GitHub repos API returned status code {response.status_code}.")
        return []

    except requests.RequestException as exc:
        print(f"Error fetching GitHub repositories: {exc}")
        return []


def extract_repo_features(repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract simple repository-based features from GitHub repositories."""
    repo_names: List[str] = []
    repo_descriptions: List[str] = []
    languages: List[str] = []

    for repo in repos:
        name = repo.get("name")
        description = repo.get("description")
        language = repo.get("language")

        if name:
            repo_names.append(name)
        if description:
            repo_descriptions.append(description)
        if language:
            languages.append(language)

    return {
        "repo_count": len(repos),
        "repo_names": repo_names,
        "repo_descriptions": repo_descriptions,
        "languages": languages,
    }


def get_github_activity_timestamps(username: str, limit: int = 100) -> List[str]:
    """
    Fetch recent public GitHub event timestamps for behavioural analysis.
    Uses the public events endpoint as a practical v1 activity source.
    """
    url = f"{GITHUB_API_BASE}/users/{username}/events/public"
    timestamps: List[str] = []

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10,
        )

        if response.status_code != 200:
            print(f"GitHub events API returned status code {response.status_code}.")
            return timestamps

        events = response.json()

        for event in events[:limit]:
            created_at = event.get("created_at")
            if created_at:
                timestamps.append(created_at)

        return timestamps

    except requests.RequestException as exc:
        print(f"Error fetching GitHub activity events: {exc}")
        return timestamps