# system-design-notification-router

Asynchronous distributed notification system routing high-volume emails, SMS, and push notifications with strict delivery guarantees. Implements exponential backoff with jitter in dead-letter queues to handle third-party API throttling (Twilio, SendGrid, FCM).

## Architecture

```
Notification (channel, recipient, body)
       │
  NotificationRouter.send()
       │
  Provider.send()  ←── EmailProvider / SMSProvider / PushProvider
       │
  ┌────┴──────────────────────────────┐
  │ SUCCESS → DELIVERED               │
  │ FAIL    → exponential_backoff()   │
  │         → DeadLetterQueue.add()   │
  │           ├─ attempt < max → retry queue
  │           └─ attempt >= max → dead letters
  └───────────────────────────────────┘
```

## Exponential backoff with jitter

```
delay = min(max_seconds, base * 2^attempt) ± jitter

attempt=0: ~1s   attempt=1: ~2s   attempt=2: ~4s
attempt=3: ~8s   attempt=4: ~16s  attempt=5: capped at 60s
```

Full jitter prevents thundering herd when multiple failed notifications retry simultaneously — they spread across the delay window instead of spiking at the same instant.

## Dead-letter queue flow

1. Attempt fails → `DLQ.add(notification, error)`
2. If `attempt < max_attempts` → retryable queue
3. If `attempt >= max_attempts` → dead letters (inspect/alert)
4. `router.retry_dlq()` pops retryable queue and re-sends

## Running tests

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -v   # 24 tests
```
