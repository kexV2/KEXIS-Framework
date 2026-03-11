import re
from typing import List, Set


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "with", "this",
    "my", "your", "our", "their", "user", "project", "repo", "repository"
}


def tokenize_text(text: str) -> List[str]:
    """
    Lowercase and split text into simple word tokens.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return cleaned.split()


def extract_keywords_from_texts(texts: List[str]) -> Set[str]:
    """
    Extract simple keywords from a list of text strings.
    """
    keywords: Set[str] = set()

    for text in texts:
        for token in tokenize_text(text):
            if len(token) >= 3 and token not in STOPWORDS:
                keywords.add(token)

    return keywords


def calculate_topic_similarity(source_a: List[str], source_b: List[str]) -> float:
    """
    Calculate Jaccard similarity between two text sources based on extracted keywords.
    """
    keywords_a = extract_keywords_from_texts(source_a)
    keywords_b = extract_keywords_from_texts(source_b)

    if not keywords_a and not keywords_b:
        return 0.0

    intersection = keywords_a.intersection(keywords_b)
    union = keywords_a.union(keywords_b)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def get_shared_keywords(source_a: List[str], source_b: List[str]) -> List[str]:
    """
    Return sorted shared keywords for reporting.
    """
    keywords_a = extract_keywords_from_texts(source_a)
    keywords_b = extract_keywords_from_texts(source_b)

    return sorted(keywords_a.intersection(keywords_b))