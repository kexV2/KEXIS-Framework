from typing import Dict


def calculate_confidence_score(features: Dict[str, float]) -> float:
    """
    Calculate a weighted confidence score from extracted features.
    """
    weights = {
        "username_similarity": 0.40,
        "topic_similarity": 0.30,
        "activity_similarity": 0.30,
    }

    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0

    weighted_sum = 0.0
    for feature_name, weight in weights.items():
        value = features.get(feature_name, 0.0)
        weighted_sum += value * weight

    return weighted_sum / total_weight