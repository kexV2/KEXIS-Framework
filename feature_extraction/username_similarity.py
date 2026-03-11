from difflib import SequenceMatcher


def normalise_username(username: str) -> str:
    """
    Lowercase and remove common separators to improve comparison.
    Example:
    kex-gh -> kexgh
    """
    return username.lower().replace("-", "").replace("_", "").strip()


def compare_usernames(username_a: str, username_b: str) -> float:
    """
    Compare two usernames and return a similarity score between 0 and 1.
    """
    clean_a = normalise_username(username_a)
    clean_b = normalise_username(username_b)

    return SequenceMatcher(None, clean_a, clean_b).ratio()