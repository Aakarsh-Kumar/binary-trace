"""Clean mathematical operations for statistical verification."""


def calculate_mean(values: list[float]) -> float:
    """Compute arithmetic mean of a sequence of floats.

    Args:
        values: List of numeric values.

    Returns:
        Mean of the values.

    Raises:
        ValueError: If values list is empty.
    """
    if not values:
        raise ValueError("Cannot compute mean of empty sequence")
    return sum(values) / len(values)


def calculate_variance(values: list[float]) -> float:
    """Compute sample variance of a sequence of floats."""
    if len(values) < 2:
        raise ValueError("Variance requires at least two data points")
    mean = calculate_mean(values)
    return sum((x - mean) ** 2 for x in values) / (len(values) - 1)
