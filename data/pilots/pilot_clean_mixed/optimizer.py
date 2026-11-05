"""Gradient descent optimizer implementation."""


def step(weights: list[float], gradients: list[float], lr: float = 0.01) -> list[float]:
    """Perform one gradient descent update step."""
    if len(weights) != len(gradients):
        raise ValueError("Weights and gradients must have equal dimension")
    return [w - lr * g for w, g in zip(weights, gradients)]
