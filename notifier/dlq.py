from dataclasses import dataclass, field
from .message import Notification, DeliveryStatus


@dataclass
class DLQEntry:
    notification: Notification
    last_error: str
    total_attempts: int


class DeadLetterQueue:
    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts
        self._queue: list = []
        self._dead: list = []

    def add(self, notification: Notification, error: str) -> None:
        if notification.attempt >= self.max_attempts:
            notification.status = DeliveryStatus.DLQ
            self._dead.append(DLQEntry(notification, error, notification.attempt))
        else:
            self._queue.append(DLQEntry(notification, error, notification.attempt))

    def pop_retryable(self) -> list:
        retryable = [e for e in self._queue]
        self._queue.clear()
        return retryable

    @property
    def dead_count(self) -> int:
        return len(self._dead)

    @property
    def retry_count(self) -> int:
        return len(self._queue)

    @property
    def dead_letters(self) -> list:
        return list(self._dead)
