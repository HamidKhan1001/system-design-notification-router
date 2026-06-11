import random
from .message import Notification, Channel


class ProviderError(Exception):
    pass


class EmailProvider:
    def __init__(self, failure_rate: float = 0.0):
        self.failure_rate = failure_rate
        self.sent: list = []

    def send(self, notification: Notification) -> None:
        if random.random() < self.failure_rate:
            raise ProviderError("SendGrid rate limit exceeded")
        self.sent.append(notification)


class SMSProvider:
    def __init__(self, failure_rate: float = 0.0):
        self.failure_rate = failure_rate
        self.sent: list = []

    def send(self, notification: Notification) -> None:
        if random.random() < self.failure_rate:
            raise ProviderError("Twilio API throttled")
        self.sent.append(notification)


class PushProvider:
    def __init__(self, failure_rate: float = 0.0):
        self.failure_rate = failure_rate
        self.sent: list = []

    def send(self, notification: Notification) -> None:
        if random.random() < self.failure_rate:
            raise ProviderError("FCM push delivery failed")
        self.sent.append(notification)


_PROVIDERS = {
    Channel.EMAIL: EmailProvider,
    Channel.SMS: SMSProvider,
    Channel.PUSH: PushProvider,
}
