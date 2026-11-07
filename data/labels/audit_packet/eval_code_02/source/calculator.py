"""Module 2 implementing numerical utilities."""

def compute_mean(values: list[float]) -> float:
    """Calculate arithmetic mean."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def compute_variance(values: list[float]) -> float:
    """Calculate sample variance."""
    if len(values) < 2:
        return 0.0
    avg = compute_mean(values)
    return sum((x - avg) ** 2 for x in values) / (len(values) - 1)
