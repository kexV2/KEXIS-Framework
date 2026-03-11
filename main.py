from data_collection.github_api import get_github_profile
from data_collection.github_activity import get_user_repos, extract_repo_features
from feature_extraction.username_similarity import compare_usernames
from feature_extraction.topic_similarity import (
    calculate_topic_similarity,
    get_shared_keywords,
)
from scoring_engine.confidence_model import calculate_confidence_score


def classify_score(score: float) -> str:
    """Convert numeric score into a human-readable label."""
    if score >= 0.7:
        return "High likelihood"
    if score >= 0.4:
        return "Moderate likelihood"
    return "Low likelihood"


def build_profile_text_sources(
    input_username: str,
    github_username: str,
    bio: str,
    repo_names: list[str],
    repo_descriptions: list[str],
    languages: list[str],
) -> tuple[list[str], list[str]]:
    """
    Build two simple text collections for comparison.

    Source A represents the investigated identity input.
    Source B represents the discovered GitHub profile evidence.
    """
    source_a = [input_username]

    source_b = [github_username, bio]
    source_b.extend(repo_names)
    source_b.extend(repo_descriptions)
    source_b.extend(languages)

    return source_a, source_b


def main() -> None:
    print("=== KEXIS Framework Prototype ===")
    input_username = input("Enter a username to investigate: ").strip()

    if not input_username:
        print("Error: username cannot be empty.")
        return

    print("\n[1] Collecting GitHub profile data...")
    github_profile = get_github_profile(input_username)

    if github_profile is None:
        print("No GitHub profile found for that username.")
        return

    github_username = github_profile.get("login", "")
    bio = github_profile.get("bio") or "No bio available"
    public_repos = github_profile.get("public_repos", 0)
    followers = github_profile.get("followers", 0)
    following = github_profile.get("following", 0)

    print("[2] Collecting GitHub repository data...")
    repos = get_user_repos(github_username)
    repo_features = extract_repo_features(repos)

    repo_names = repo_features["repo_names"]
    repo_descriptions = repo_features["repo_descriptions"]
    languages = repo_features["languages"]

    print("[3] Extracting features...")
    username_similarity = compare_usernames(input_username, github_username)

    source_a, source_b = build_profile_text_sources(
        input_username=input_username,
        github_username=github_username,
        bio=bio,
        repo_names=repo_names,
        repo_descriptions=repo_descriptions,
        languages=languages,
    )

    topic_similarity = calculate_topic_similarity(source_a, source_b)
    shared_keywords = get_shared_keywords(source_a, source_b)

    features = {
        "username_similarity": username_similarity,
        "topic_similarity": topic_similarity,
    }

    print("[4] Calculating confidence score...")
    final_score = calculate_confidence_score(features)
    classification = classify_score(final_score)

    print("\n=== Attribution Analysis Report ===")
    print(f"Input Username: {input_username}")
    print(f"GitHub Username: {github_username}")
    print(f"Bio: {bio}")
    print(f"Public Repositories (profile): {public_repos}")
    print(f"Followers: {followers}")
    print(f"Following: {following}")

    print("\n=== GitHub Repository Features ===")
    print(f"Repository Count (API): {repo_features['repo_count']}")
    print(f"Languages Used: {', '.join(languages) if languages else 'None detected'}")
    print(f"Repository Names: {', '.join(repo_names) if repo_names else 'None detected'}")

    print("\n=== Feature Results ===")
    print(f"Username Similarity: {username_similarity:.2f}")
    print(f"Topic Similarity: {topic_similarity:.2f}")
    print(f"Shared Keywords: {', '.join(shared_keywords) if shared_keywords else 'None detected'}")

    print("\n=== Final Result ===")
    print(f"Confidence Score: {final_score:.2f}")
    print(f"Classification: {classification}")


if __name__ == "__main__":
    main()