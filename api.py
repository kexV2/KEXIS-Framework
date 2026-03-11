from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_collection.github_api import get_github_profile
from data_collection.github_activity import get_user_repos, extract_repo_features
from data_collection.mastodon_api import search_mastodon_account, get_mastodon_posts
from feature_extraction.username_similarity import compare_usernames
from feature_extraction.topic_similarity import (
    calculate_topic_similarity,
    get_shared_keywords,
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


def classify_score(score: float) -> str:
    if score >= 0.7:
        return "High likelihood"
    if score >= 0.4:
        return "Moderate likelihood"
    return "Low likelihood"


def build_github_text_source(
    github_username: str,
    bio: str,
    repo_names: list[str],
    repo_descriptions: list[str],
    languages: list[str],
) -> list[str]:
    source = [github_username, bio]
    source.extend(repo_names)
    source.extend(repo_descriptions)
    source.extend(languages)
    return source


def build_mastodon_text_source(
    mastodon_username: str,
    display_name: str,
    bio: str,
    posts: list[str],
) -> list[str]:
    source = [mastodon_username, display_name, bio]
    source.extend(posts)
    return source


@app.get("/")
def root():
    return {"status": "ok", "message": "KEXIS API is running"}


@app.post("/analyze")
def analyze(request: AnalysisRequest):
    github_profile = get_github_profile(request.github_username)
    if github_profile is None:
        return {"error": "No GitHub profile found for that username."}

    github_username = github_profile.get("login", "")
    github_bio = github_profile.get("bio") or "No bio available"
    github_public_repos = github_profile.get("public_repos", 0)
    github_followers = github_profile.get("followers", 0)
    github_following = github_profile.get("following", 0)

    github_repos = get_user_repos(github_username)
    github_repo_features = extract_repo_features(github_repos)

    github_repo_names = github_repo_features["repo_names"]
    github_repo_descriptions = github_repo_features["repo_descriptions"]
    github_languages = github_repo_features["languages"]

    mastodon_profile = search_mastodon_account(request.mastodon_handle)
    if mastodon_profile is None:
        return {"error": "No Mastodon account found for that handle."}

    mastodon_id = mastodon_profile["id"]
    mastodon_username = mastodon_profile["username"]
    mastodon_acct = mastodon_profile["acct"]
    mastodon_display_name = mastodon_profile["display_name"] or "No display name"
    mastodon_bio = mastodon_profile["bio"] or "No bio available"
    mastodon_followers = mastodon_profile["followers"]
    mastodon_following = mastodon_profile["following"]
    mastodon_url = mastodon_profile["url"]

    mastodon_posts = get_mastodon_posts(mastodon_id, limit=10)

    username_similarity = compare_usernames(github_username, mastodon_username)

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

    topic_similarity = calculate_topic_similarity(github_text_source, mastodon_text_source)
    shared_keywords = get_shared_keywords(github_text_source, mastodon_text_source)

    features = {
        "username_similarity": username_similarity,
        "topic_similarity": topic_similarity,
    }

    final_score = calculate_confidence_score(features)
    classification = classify_score(final_score)

    return {
        "github": {
            "username": github_username,
            "bio": github_bio,
            "public_repos": github_public_repos,
            "followers": github_followers,
            "following": github_following,
            "languages": github_languages,
            "repo_names": github_repo_names,
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
        },
        "features": {
            "username_similarity": round(username_similarity, 2),
            "topic_similarity": round(topic_similarity, 2),
            "shared_keywords": shared_keywords,
        },
        "result": {
            "confidence_score": round(final_score, 2),
            "classification": classification,
        },
    }