import pytest
from notifier import exponential_backoff_with_jitter, retry_delays


def test_attempt_0_returns_base():
    d = exponential_backoff_with_jitter(0, base_seconds=1.0, jitter_factor=0)
    assert d == pytest.approx(1.0)


def test_delay_increases_with_attempt():
    delays = [exponential_backoff_with_jitter(i, jitter_factor=0) for i in range(5)]
    for i in range(len(delays) - 1):
        assert delays[i + 1] >= delays[i]


def test_max_seconds_cap():
    d = exponential_backoff_with_jitter(100, base_seconds=1.0, max_seconds=60.0, jitter_factor=0)
    assert d == pytest.approx(60.0)


def test_jitter_within_bounds():
    for _ in range(100):
        d = exponential_backoff_with_jitter(3, base_seconds=1.0, max_seconds=60.0, jitter_factor=0.25)
        expected = min(60.0, 1.0 * (2 ** 3))
        assert d >= 0.0
        assert d <= expected * 1.26


def test_negative_attempt_raises():
    with pytest.raises(ValueError):
        exponential_backoff_with_jitter(-1)


def test_retry_delays_length():
    delays = retry_delays(5)
    assert len(delays) == 5


def test_retry_delays_non_negative():
    delays = retry_delays(10)
    assert all(d >= 0 for d in delays)
