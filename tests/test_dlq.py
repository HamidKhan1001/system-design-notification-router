import pytest
from notifier import Notification, Channel, DeliveryStatus
from notifier.dlq import DeadLetterQueue


@pytest.fixture
def dlq():
    return DeadLetterQueue(max_attempts=3)


def test_add_retryable(dlq):
    n = Notification(Channel.EMAIL, "a@b.com", "hello", attempt=0)
    dlq.add(n, "timeout")
    assert dlq.retry_count == 1
    assert dlq.dead_count == 0


def test_add_exceeds_max_goes_dead(dlq):
    n = Notification(Channel.EMAIL, "a@b.com", "hello", attempt=3)
    dlq.add(n, "too many")
    assert dlq.dead_count == 1
    assert dlq.retry_count == 0


def test_pop_retryable_clears_queue(dlq):
    n = Notification(Channel.EMAIL, "a@b.com", "body", attempt=1)
    dlq.add(n, "err")
    entries = dlq.pop_retryable()
    assert len(entries) == 1
    assert dlq.retry_count == 0


def test_dead_letters_accumulate(dlq):
    for i in range(3):
        n = Notification(Channel.SMS, f"+{i}", "msg", attempt=3)
        dlq.add(n, "throttled")
    assert dlq.dead_count == 3


def test_dead_letters_property(dlq):
    n = Notification(Channel.PUSH, "token", "push", attempt=3)
    dlq.add(n, "fcm fail")
    assert len(dlq.dead_letters) == 1
    assert dlq.dead_letters[0].notification.status == DeliveryStatus.DLQ
