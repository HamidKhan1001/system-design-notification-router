import pytest
from notifier import Notification, Channel, EmailProvider, SMSProvider, PushProvider, ProviderError


def test_email_sends_successfully():
    p = EmailProvider(failure_rate=0.0)
    n = Notification(Channel.EMAIL, "a@b.com", "hello")
    p.send(n)
    assert len(p.sent) == 1


def test_email_fails_with_rate_1():
    p = EmailProvider(failure_rate=1.0)
    n = Notification(Channel.EMAIL, "a@b.com", "hello")
    with pytest.raises(ProviderError):
        p.send(n)


def test_sms_sends_successfully():
    p = SMSProvider(failure_rate=0.0)
    n = Notification(Channel.SMS, "+155500000", "code")
    p.send(n)
    assert len(p.sent) == 1


def test_push_sends_successfully():
    p = PushProvider(failure_rate=0.0)
    n = Notification(Channel.PUSH, "tok", "ping")
    p.send(n)
    assert len(p.sent) == 1


def test_sms_fails_at_rate_1():
    p = SMSProvider(failure_rate=1.0)
    n = Notification(Channel.SMS, "+1", "msg")
    with pytest.raises(ProviderError):
        p.send(n)
