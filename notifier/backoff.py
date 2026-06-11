import random


def exponential_backoff_with_jitter(
    attempt: int,
    base_seconds: float = 1.0,
    max_seconds: float = 60.0,
    jitter_factor: float = 0.25,
) -> float:
    """
    Full-jitter exponential backoff.
    delay = random(0, min(max, base * 2^attempt)) * (1 ± jitter_factor)
    """
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
    exp_delay = min(max_seconds, base_seconds * (2 ** attempt))
    jitter = exp_delay * jitter_factor * (2 * random.random() - 1)
    return max(0.0, exp_delay + jitter)


def retry_delays(max_attempts: int, **kwargs) -> list:
    return [exponential_backoff_with_jitter(i, **kwargs) for i in range(max_attempts)]
