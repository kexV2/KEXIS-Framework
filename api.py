from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_collection.github_api import get_github_profile
from data_collection.github_activity import (
    get_user_repos,
    extract_repo_features,
    get_github_activity_timestamps,
)
from data_collection.mastodon_api import (
    search_mastodon_account,
    get_mastodon_posts,
    get_mastodon_post_timestamps,
)
from feature_extraction.username_similarity import compare_usernames
from feature_extraction.topic_similarity import (
    calculate_topic_similarity,
    get_shared_keywords,
)
from feature_extraction.activity_similarity import (
    calculate_activity_similarity,
    get_top_active_hours,
)
from scoring_engine.confidence_model import calculate_confidence_score

app = FastAPI(title="KEXIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    github_username: str
    mastodon_handle: str


def safe_string(value: Any, fallback: str = "") -> str:
    """Return a safe string value."""
    if value is None:
        return fallback
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else fallback
    return str(value)


def safe_list(value: Any) -> List[Any]:
    """Ensure a value is always returned as a list."""
    if isinstance(value, list):
        return value
    return []


def clamp_score(value: float) -> float:
    """Clamp feature scores between 0.0 and 1.0."""
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def classify_score(score: float) -> str:
    """Convert numeric score into a confidence band."""
    if score >= 0.7:
        return "High likelihood"
    if score >= 0.4:
        return "Moderate likelihood"
    return "Low likelihood"


def build_github_text_source(
    github_username: str,
    bio: str,
    repo_names: List[str],
    repo_descriptions: List[str],
    languages: List[str],
) -> List[str]:
    """Build a GitHub text corpus for topic comparison."""
    source = [github_username, bio]
    source.extend(repo_names)
    source.extend(repo_descriptions)
    source.extend(languages)
    return [safe_string(item) for item in source if safe_string(item)]


def build_mastodon_text_source(
    mastodon_username: str,
    display_name: str,
    bio: str,
    posts: List[str],
) -> List[str]:
    """Build a Mastodon text corpus for topic comparison."""
    source = [mastodon_username, display_name, bio]
    source.extend(posts)
    return [safe_string(item) for item in source if safe_string(item)]


@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "ok", "message": "KEXIS API is running"}


@app.post("/analyze")
def analyze(request: AnalysisRequest) -> Dict[str, Any]:
    # -------------------------
    # Step 1: GitHub collection
    # -------------------------
    github_profile = get_github_profile(request.github_username)
    if github_profile is None:
        return {"error": "No GitHub profile found for that username."}

    github_username = safe_string(github_profile.get("login"))
    github_bio = safe_string(github_profile.get("bio"), "No bio available")
    github_public_repos = github_profile.get("public_repos", 0) or 0
    github_followers = github_profile.get("followers", 0) or 0
    github_following = github_profile.get("following", 0) or 0

    github_repos = safe_list(get_user_repos(github_username))
    github_repo_features = extract_repo_features(github_repos) if github_repos else {
        "repo_count": 0,
        "repo_names": [],
        "repo_descriptions": [],
        "languages": [],
    }

    github_repo_names = safe_list(github_repo_features.get("repo_names"))
    github_repo_descriptions = safe_list(github_repo_features.get("repo_descriptions"))
    github_languages = safe_list(github_repo_features.get("languages"))

    github_activity_timestamps = safe_list(
        get_github_activity_timestamps(github_username, limit=100)
    )

    # ---------------------------
    # Step 2: Mastodon collection
    # ---------------------------
    mastodon_profile = search_mastodon_account(request.mastodon_handle)
    if mastodon_profile is None:
        return {"error": "No Mastodon account found for that handle."}

    mastodon_id = safe_string(mastodon_profile.get("id"))
    mastodon_username = safe_string(mastodon_profile.get("username"))
    mastodon_acct = safe_string(mastodon_profile.get("acct"))
    mastodon_display_name = safe_string(
        mastodon_profile.get("display_name"),
        "No display name",
    )
    mastodon_bio = safe_string(mastodon_profile.get("bio"), "No bio available")
    mastodon_followers = mastodon_profile.get("followers", 0) or 0
    mastodon_following = mastodon_profile.get("following", 0) or 0
    mastodon_url = safe_string(mastodon_profile.get("url"))

    mastodon_posts = safe_list(get_mastodon_posts(mastodon_id, limit=10))
    mastodon_posts = [safe_string(post) for post in mastodon_posts if safe_string(post)]

    mastodon_activity_timestamps = safe_list(
        get_mastodon_post_timestamps(mastodon_id, limit=40)
    )

    # -------------------------
    # Step 3: Feature extraction
    # -------------------------
    username_similarity = clamp_score(
        compare_usernames(github_username, mastodon_username)
    )

    github_text_source = build_github_text_source(
        github_username=github_username,
        bio=github_bio,
        repo_names=github_repo_names,
        repo_descriptions=github_repo_descriptions,
        languages=github_languages,
    )

    mastodon_text_source = build_mastodon_text_source(
        mastodon_username=mastodon_username,
        display_name=mastodon_display_name,
        bio=mastodon_bio,
        posts=mastodon_posts,
    )

    topic_similarity = clamp_score(
        calculate_topic_similarity(github_text_source, mastodon_text_source)
    )

    shared_keywords = safe_list(
        get_shared_keywords(github_text_source, mastodon_text_source)
    )
    shared_keywords = [safe_string(word) for word in shared_keywords if safe_string(word)]

    activity_similarity = clamp_score(
        calculate_activity_similarity(
            github_activity_timestamps,
            mastodon_activity_timestamps,
        )
    )

    # -------------------------
    # Step 4: Final confidence
    # -------------------------
    features = {
        "username_similarity": username_similarity,
        "topic_similarity": topic_similarity,
        "activity_similarity": activity_similarity,
    }

    final_score = clamp_score(calculate_confidence_score(features))
    classification = classify_score(final_score)

    # -------------------------
    # Step 5: Evidence summaries
    # -------------------------
    github_top_active_hours = get_top_active_hours(github_activity_timestamps)
    mastodon_top_active_hours = get_top_active_hours(mastodon_activity_timestamps)

    return {
        "github": {
            "username": github_username,
            "bio": github_bio,
            "public_repos": github_public_repos,
            "followers": github_followers,
            "following": github_following,
            "languages": github_languages,
            "repo_names": github_repo_names,
            "repo_descriptions": github_repo_descriptions,
            "top_active_hours": github_top_active_hours,
            "activity_sample_size": len(github_activity_timestamps),
        },
        "mastodon": {
            "username": mastodon_username,
            "handle": mastodon_acct,
            "display_name": mastodon_display_name,
            "bio": mastodon_bio,
            "followers": mastodon_followers,
            "following": mastodon_following,
            "profile_url": mastodon_url,
            "posts": mastodon_posts,
            "top_active_hours": mastodon_top_active_hours,
            "activity_sample_size": len(mastodon_activity_timestamps),
        },
        "features": {
            "username_similarity": round(username_similarity, 2),
            "topic_similarity": round(topic_similarity, 2),
            "activity_similarity": round(activity_similarity, 2),
            "shared_keywords": shared_keywords,
        },
        "result": {
            "confidence_score": round(final_score, 2),
            "classification": classification,
        },
    }