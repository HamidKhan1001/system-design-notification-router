import pytest
from notifier import Notification, Channel, DeliveryStatus, NotificationRouter


def test_successful_email_delivery():
    router = NotificationRouter()
    n = Notification(Channel.EMAIL, "a@b.com", "hi")
    assert router.send(n) is True
    assert router.delivered_count == 1


def test_successful_sms_delivery():
    router = NotificationRouter()
    n = Notification(Channel.SMS, "+1555", "code")
    assert router.send(n) is True


def test_failed_delivery_goes_to_dlq():
    router = NotificationRouter(email_failure_rate=1.0)
    n = Notification(Channel.EMAIL, "a@b.com", "fail")
    result = router.send(n)
    assert result is False
    assert router.dlq.retry_count == 1


def test_delay_recorded_on_failure():
    router = NotificationRouter(email_failure_rate=1.0)
    n = Notification(Channel.EMAIL, "a@b.com", "fail")
    router.send(n)
    assert len(router.recorded_delays) == 1
    assert router.recorded_delays[0] >= 0.0


def test_retry_dlq_succeeds():
    router = NotificationRouter(email_failure_rate=1.0)
    n = Notification(Channel.EMAIL, "a@b.com", "retry")
    router.send(n)
    router._providers[Channel.EMAIL].failure_rate = 0.0
    succeeded = router.retry_dlq()
    assert succeeded == 1


def test_max_attempts_reaches_dead():
    router = NotificationRouter(max_attempts=2, email_failure_rate=1.0)
    n = Notification(Channel.EMAIL, "a@b.com", "dead", attempt=2)
    router.send(n)
    assert router.dlq.dead_count == 1


def test_push_notification_delivered():
    router = NotificationRouter()
    n = Notification(Channel.PUSH, "device-token-xyz", "alert")
    assert router.send(n) is True
