from collections import Counter
from datetime import datetime
from typing import Dict, List


def parse_timestamp(ts: str) -> datetime | None:
    """
    Parse ISO-like timestamps from GitHub and Mastodon.
    Handles trailing 'Z' for UTC where present.
    """
    if not ts:
        return None

    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_hour_distribution(timestamps: List[str]) -> Dict[int, float]:
    """
    Convert timestamps into a normalized 24-hour activity distribution.
    """
    hours = []

    for ts in timestamps:
        dt = parse_timestamp(ts)
        if dt is not None:
            hours.append(dt.hour)

    if not hours:
        return {}

    counts = Counter(hours)
    total = sum(counts.values())

    return {hour: count / total for hour, count in counts.items()}


def build_weekday_distribution(timestamps: List[str]) -> Dict[int, float]:
    """
    Convert timestamps into a normalized weekday distribution.
    Monday=0, Sunday=6.
    """
    weekdays = []

    for ts in timestamps:
        dt = parse_timestamp(ts)
        if dt is not None:
            weekdays.append(dt.weekday())

    if not weekdays:
        return {}

    counts = Counter(weekdays)
    total = sum(counts.values())

    return {day: count / total for day, count in counts.items()}


def histogram_overlap(dist_a: Dict[int, float], dist_b: Dict[int, float], size: int) -> float:
    """
    Compare two normalized distributions using overlap:
    sum(min(a_i, b_i)).
    Returns a value between 0 and 1.
    """
    if not dist_a or not dist_b:
        return 0.0

    overlap = 0.0
    for i in range(size):
        overlap += min(dist_a.get(i, 0.0), dist_b.get(i, 0.0))

    return overlap


def calculate_activity_similarity(
    github_timestamps: List[str],
    mastodon_timestamps: List[str],
) -> float:
    """
    Behavioural similarity based on time-of-day and weekday posting patterns.
    """
    github_hours = build_hour_distribution(github_timestamps)
    mastodon_hours = build_hour_distribution(mastodon_timestamps)

    github_weekdays = build_weekday_distribution(github_timestamps)
    mastodon_weekdays = build_weekday_distribution(mastodon_timestamps)

    hour_overlap = histogram_overlap(github_hours, mastodon_hours, 24)
    weekday_overlap = histogram_overlap(github_weekdays, mastodon_weekdays, 7)

    return (0.7 * hour_overlap) + (0.3 * weekday_overlap)


def get_top_active_hours(timestamps: List[str], top_n: int = 3) -> List[int]:
    """
    Return the most active hours for reporting.
    """
    hours = []

    for ts in timestamps:
        dt = parse_timestamp(ts)
        if dt is not None:
            hours.append(dt.hour)

    if not hours:
        return []

    counts = Counter(hours)
    return [hour for hour, _ in counts.most_common(top_n)]