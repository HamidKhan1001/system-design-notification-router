import uuid
from dataclasses import dataclass, field
from enum import Enum


class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class DeliveryStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DLQ = "dlq"


@dataclass
class Notification:
    channel: Channel
    recipient: str
    body: str
    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempt: int = 0
    status: DeliveryStatus = DeliveryStatus.PENDING

    def next_attempt(self) -> "Notification":
        return Notification(
            channel=self.channel,
            recipient=self.recipient,
            body=self.body,
            notification_id=self.notification_id,
            attempt=self.attempt + 1,
            status=DeliveryStatus.PENDING,
        )
