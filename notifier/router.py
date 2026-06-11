from .message import Notification, Channel, DeliveryStatus
from .provider import EmailProvider, SMSProvider, PushProvider, ProviderError
from .backoff import exponential_backoff_with_jitter
from .dlq import DeadLetterQueue


class NotificationRouter:
    def __init__(self, max_attempts: int = 5, email_failure_rate: float = 0.0,
                 sms_failure_rate: float = 0.0, push_failure_rate: float = 0.0):
        self.max_attempts = max_attempts
        self._providers = {
            Channel.EMAIL: EmailProvider(email_failure_rate),
            Channel.SMS: SMSProvider(sms_failure_rate),
            Channel.PUSH: PushProvider(push_failure_rate),
        }
        self.dlq = DeadLetterQueue(max_attempts)
        self._delivered: list = []
        self._delays: list = []

    def send(self, notification: Notification) -> bool:
        provider = self._providers[notification.channel]
        try:
            provider.send(notification)
            notification.status = DeliveryStatus.DELIVERED
            self._delivered.append(notification)
            return True
        except ProviderError as e:
            delay = exponential_backoff_with_jitter(notification.attempt)
            self._delays.append(delay)
            self.dlq.add(notification, str(e))
            return False

    def retry_dlq(self) -> int:
        entries = self.dlq.pop_retryable()
        success = 0
        for entry in entries:
            retried = entry.notification.next_attempt()
            if self.send(retried):
                success += 1
        return success

    @property
    def delivered_count(self) -> int:
        return len(self._delivered)

    @property
    def recorded_delays(self) -> list:
        return list(self._delays)
