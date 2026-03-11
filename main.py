from data_collection.github_api import get_github_profile
from feature_extraction.username_similarity import compare_usernames
from scoring_engine.confidence_model import calculate_confidence_score


def classify_score(score: float) -> str:
    """Convert a numeric score into a human-readable label."""
    if score >= 0.7:
        return "High likelihood"
    if score >= 0.4:
        return "Moderate likelihood"
    return "Low likelihood"


def main() -> None:
    print("=== KEXIS Framework Prototype ===")
    input_username = input("Enter a username to investigate: ").strip()

    if not input_username:
        print("Error: username cannot be empty.")
        return

    print("\n[1] Collecting GitHub data...")
    github_profile = get_github_profile(input_username)

    if github_profile is None:
        print("No GitHub profile found for that username.")
        return

    github_username = github_profile.get("login", "")
    bio = github_profile.get("bio") or "No bio available"
    public_repos = github_profile.get("public_repos", 0)
    followers = github_profile.get("followers", 0)
    following = github_profile.get("following", 0)

    print("[2] Extracting features...")
    username_similarity = compare_usernames(input_username, github_username)

    features = {
        "username_similarity": username_similarity
    }

    print("[3] Calculating confidence score...")
    final_score = calculate_confidence_score(features)
    classification = classify_score(final_score)

    print("\n=== Attribution Analysis Report ===")
    print(f"Input Username: {input_username}")
    print(f"GitHub Username: {github_username}")
    print(f"Bio: {bio}")
    print(f"Public Repositories: {public_repos}")
    print(f"Followers: {followers}")
    print(f"Following: {following}")

    print("\n=== Feature Results ===")
    print(f"Username Similarity: {username_similarity:.2f}")

    print("\n=== Final Result ===")
    print(f"Confidence Score: {final_score:.2f}")
    print(f"Classification: {classification}")


if __name__ == "__main__":
    main()