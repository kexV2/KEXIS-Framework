from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# EXISTING IMPORTS
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

# NEW YOUTUBE IMPORTS
from data_collection.youtube_api import (
    get_youtube_channel,
    get_youtube_videos,
    extract_youtube_features,
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


# UPDATED REQUEST MODEL
class AnalysisRequest(BaseModel):
    github_username: str
    mastodon_handle: str
    youtube_channel: str


# -------------------------
# UTILITY FUNCTIONS
# -------------------------
def safe_string(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else fallback
    return str(value)


def safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def clamp_score(value: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def classify_score(score: float) -> str:
    if score >= 0.7:
        return "High likelihood"
    if score >= 0.4:
        return "Moderate likelihood"
    return "Low likelihood"


# -------------------------
# TEXT SOURCES
# -------------------------
def build_github_text_source(
    github_username: str,
    bio: str,
    repo_names: List[str],
    repo_descriptions: List[str],
    languages: List[str],
) -> List[str]:
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
    source = [mastodon_username, display_name, bio]
    source.extend(posts)
    return [safe_string(item) for item in source if safe_string(item)]


# NEW YOUTUBE TEXT BUILDER
def build_youtube_text_source(
    channel_title: str,
    channel_description: str,
    video_titles: List[str],
    video_descriptions: List[str],
) -> List[str]:
    source = [channel_title, channel_description]
    source.extend(video_titles)
    source.extend(video_descriptions)
    return [safe_string(item) for item in source if safe_string(item)]


# -------------------------
# ROOT
# -------------------------
@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "ok", "message": "KEXIS API is running"}


# -------------------------
# MAIN ANALYSIS
# -------------------------
@app.post("/analyze")
def analyze(request: AnalysisRequest) -> Dict[str, Any]:

    # -------------------------
    # GitHub
    # -------------------------
    github_profile = get_github_profile(request.github_username)
    if github_profile is None:
        return {"error": "No GitHub profile found."}

    github_username = safe_string(github_profile.get("login"))
    github_bio = safe_string(github_profile.get("bio"), "No bio available")

    github_repos = safe_list(get_user_repos(github_username))
    github_repo_features = extract_repo_features(github_repos)

    github_repo_names = safe_list(github_repo_features.get("repo_names"))
    github_repo_descriptions = safe_list(github_repo_features.get("repo_descriptions"))
    github_languages = safe_list(github_repo_features.get("languages"))

    github_activity_timestamps = safe_list(
        get_github_activity_timestamps(github_username)
    )

    # -------------------------
    # Mastodon
    # -------------------------
    mastodon_profile = search_mastodon_account(request.mastodon_handle)
    if mastodon_profile is None:
        return {"error": "No Mastodon account found."}

    mastodon_id = safe_string(mastodon_profile.get("id"))
    mastodon_username = safe_string(mastodon_profile.get("username"))
    mastodon_display_name = safe_string(
        mastodon_profile.get("display_name"), "No display name"
    )
    mastodon_bio = safe_string(mastodon_profile.get("bio"), "No bio available")

    mastodon_posts = safe_list(get_mastodon_posts(mastodon_id))
    mastodon_activity_timestamps = safe_list(
        get_mastodon_post_timestamps(mastodon_id)
    )

    # -------------------------
    # YouTube
    # -------------------------
    youtube_profile = get_youtube_channel(request.youtube_channel)
    if youtube_profile is None:
        return {"error": "No YouTube channel found."}

    youtube_channel_id = safe_string(youtube_profile.get("channel_id"))
    youtube_channel_title = safe_string(youtube_profile.get("title"))
    youtube_channel_description = safe_string(
        youtube_profile.get("description"),
        "No channel description available",
    )

    youtube_videos = get_youtube_videos(youtube_channel_id)
    youtube_features = extract_youtube_features(youtube_videos)

    youtube_titles = safe_list(youtube_features.get("titles"))
    youtube_descriptions = safe_list(youtube_features.get("descriptions"))
    youtube_timestamps = safe_list(youtube_features.get("timestamps"))

    # -------------------------
    # TEXT SOURCES
    # -------------------------
    github_text_source = build_github_text_source(
        github_username,
        github_bio,
        github_repo_names,
        github_repo_descriptions,
        github_languages,
    )

    mastodon_text_source = build_mastodon_text_source(
        mastodon_username,
        mastodon_display_name,
        mastodon_bio,
        mastodon_posts,
    )

    youtube_text_source = build_youtube_text_source(
        youtube_channel_title,
        youtube_channel_description,
        youtube_titles,
        youtube_descriptions,
    )

    # COMBINE SOCIAL SOURCES
    combined_social_text = mastodon_text_source + youtube_text_source

    # -------------------------
    # FEATURES
    # -------------------------
    username_similarity = clamp_score(
        compare_usernames(github_username, mastodon_username)
    )

    topic_similarity = clamp_score(
        calculate_topic_similarity(github_text_source, combined_social_text)
    )

    shared_keywords = safe_list(
        get_shared_keywords(github_text_source, combined_social_text)
    )

    combined_activity = mastodon_activity_timestamps + youtube_timestamps

    activity_similarity = clamp_score(
        calculate_activity_similarity(
            github_activity_timestamps,
            combined_activity,
        )
    )

    # -------------------------
    # FINAL SCORE
    # -------------------------
    features = {
        "username_similarity": username_similarity,
        "topic_similarity": topic_similarity,
        "activity_similarity": activity_similarity,
    }

    final_score = clamp_score(calculate_confidence_score(features))
    classification = classify_score(final_score)

    # -------------------------
    # RESPONSE
    # -------------------------
    return {
        "github": {
            "username": github_username,
            "languages": github_languages,
        },
        "mastodon": {
            "username": mastodon_username,
            "posts": mastodon_posts,
        },
        "youtube": {
            "channel": youtube_channel_title,
            "videos": youtube_titles,
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