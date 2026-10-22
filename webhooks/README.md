# Receive delivery updates with webhooks

This guide shows you how to build an endpoint that receives Relay's delivery updates, and how to make it secure and reliable.

**Who this is for:** backend developers at banks who integrate their systems with Relay.

> Relay is a fictional notification platform, used here as an example. The [`example`](example/) folder has a working receiver you can run on your own machine.

## Contents

- [Why use webhooks](#why-use-webhooks)
- [How Relay sends webhooks](#how-relay-sends-webhooks)
- [Event types](#event-types)
- [Build your receiver](#build-your-receiver)
- [Try it on your machine](#try-it-on-your-machine)
- [Go-live checklist](#go-live-checklist)

## Why use webhooks

Sending a notification is asynchronous: Relay accepts it first and delivers it afterwards. To know what happened, you have two options:

| Option | How it works | Use it when |
|---|---|---|
| Polling | You ask Relay for the status with [`GET /notifications/{id}`](../api-reference/README.md#get-a-notification). | You check a single notification, for example while helping a customer. |
| Webhooks | Relay calls your endpoint every time a notification changes status. | You need to know about every notification, as it happens. |

For a bank that sends thousands of notifications an hour, polling means thousands of requests that mostly return "no change yet". Webhooks tell you only when there's something new.

## How Relay sends webhooks

When a notification changes status, Relay sends an HTTP `POST` request to the URL you configured, with a JSON body:

```json
{
  "id": "evt_8f2a61c04b9e",
  "type": "notification.delivered",
  "created_at": "2026-10-22T09:14:36Z",
  "data": {
    "id": "ntf_01HZX3K8D2",
    "customer_id": "cus_7Q2M9X",
    "notification_type": "otp",
    "category": "mandatory",
    "reference": "login-2026-10-22-0042",
    "status": "delivered",
    "attempt": { "channel": "sms", "status": "delivered", "reason": null }
  }
}
```

`id` identifies the **event**. `data.id` identifies the **notification**. One notification can produce several events.

Four rules decide how you build your receiver:

1. **Every request is signed.** The `Relay-Signature` header proves that Relay sent it and that nobody changed the body on the way.
2. **Relay retries until you answer.** If your endpoint doesn't answer `2xx` within 10 seconds, Relay tries again after 1 minute, 5 minutes, 30 minutes, 2 hours, 6 hours and 12 hours. After the last try, the event appears as failed in the Relay console, where you can resend it.
3. **You may receive the same event more than once.** For example, if your endpoint processed an event but the answer was lost on the network, Relay sends it again.
4. **Events can arrive out of order.** A `notification.delivered` may arrive before the `notification.fallback_triggered` that came before it. Use `created_at` to order them, not the order of arrival.

## Event types

| Event | Relay sends it when |
|---|---|
| `notification.fallback_triggered` | An attempt failed and Relay is trying the next channel. `data.attempt` is the attempt that failed. |
| `notification.delivered` | An attempt was delivered. The notification is finished. |
| `notification.not_delivered` | Every attempt failed. The notification is finished. |
| `notification.blocked` | Relay didn't send the notification, for example because the customer hasn't consented to marketing. |

For mandatory notifications, such as OTPs, act on `notification.not_delivered`: the customer didn't get a message they needed. See [A customer didn't receive an OTP](../troubleshooting/otp-not-received.md).

## Build your receiver

Your receiver does three things, in this order. The code below is from [`example/receiver.py`](example/receiver.py).

### Step 1: Verify the signature

The `Relay-Signature` header has two parts:

```text
Relay-Signature: t=1792660476,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
```

| Part | Meaning |
|---|---|
| `t` | When Relay signed the request, in Unix time. |
| `v1` | An HMAC-SHA256 of `t`, a dot and the raw request body, calculated with your signing secret. |

To verify it:

1. Read the **raw body** as bytes. If you parse the JSON and convert it back to text, spaces or key order can change and the signature won't match.
2. Reject the request if `t` is more than 5 minutes away from your current time. This stops someone from capturing a real request and sending it again later (a *replay attack*).
3. Calculate the HMAC yourself and compare it with `v1` using a constant-time comparison.
4. If the signature isn't valid, answer `400` and don't process the event.

```python
def verify_signature(header, body, secret, now=None):
    parts = dict(item.split("=", 1) for item in header.split(",") if "=" in item)
    timestamp, signature = parts.get("t"), parts.get("v1")
    ...
    if abs(now - int(timestamp)) > TOLERANCE_SECONDS:
        return False

    signed_payload = timestamp.encode() + b"." + body
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

Keep the signing secret in a secrets manager or an environment variable, never in your code.

> **Upgrading from Relay 2025.1?** The `X-Relay-Signature` header, which didn't include a timestamp, is deprecated. See the [migration guide](../release-notes/migration-2026.1.md).

### Step 2: Ignore events you've already processed

Because Relay can send the same event more than once, store the `id` of every event you process. Before processing an event, check whether its `id` is already stored:

- If it is, answer `200` and do nothing else. The `200` tells Relay to stop retrying.
- If it isn't, process the event and store its `id`.

This makes your receiver **idempotent**: processing an event twice has the same result as processing it once. Without it, a retried `notification.not_delivered` could open two support tickets for the same customer.

Store event IDs in a database, not in memory, so they survive a restart. Keep them for at least as long as Relay retries: 24 hours is enough.

### Step 3: Answer quickly

Answer `2xx` as soon as the event is verified and stored. If your processing is slow (calling another system, writing to several tables), put the event in a queue and process it afterwards.

If your receiver takes more than 10 seconds, Relay considers the attempt failed and sends the event again, even if your processing eventually finished.

| Your answer | What Relay does |
|---|---|
| `2xx` within 10 seconds | Marks the event as delivered. |
| `4xx` or `5xx` | Retries later. |
| No answer within 10 seconds | Retries later. |

## Try it on your machine

The [`example`](example/) folder has a receiver and a script that sends signed test events, the way Relay would. You only need Python 3. No other packages.

1. In a terminal, start the receiver:

   ```bash
   cd example
   python3 receiver.py
   ```

   ```text
   Listening on http://localhost:8000/webhooks/relay  (Ctrl+C to stop)
   ```

2. In a second terminal, from the same folder, send a valid event:

   ```bash
   python3 send_test_event.py
   ```

   The receiver accepts it:

   ```text
   Accepted evt_dfad92cf2264
     -> notification.delivered: notification ntf_01HZX3K8D2 for cus_7Q2M9X is now 'delivered'
   ```

3. Send the same event twice, as Relay would after a lost answer:

   ```bash
   python3 send_test_event.py --duplicate
   ```

   The receiver processes it once and ignores the copy, but answers `200` both times:

   ```text
   Accepted evt_141345ce2d9a
     -> notification.delivered: ...
   Duplicate evt_141345ce2d9a: ignored
   ```

4. Send an event whose body was changed after signing:

   ```bash
   python3 send_test_event.py --tampered
   ```

   The receiver rejects it with `400`:

   ```text
   Rejected: invalid or expired signature
   ```

5. Send an event signed 10 minutes ago, as in a replay attack:

   ```bash
   python3 send_test_event.py --expired
   ```

   The receiver rejects it too.

## Go-live checklist

Before you point production traffic at your receiver:

- [ ] The endpoint uses HTTPS.
- [ ] The signing secret is in a secrets manager, not in the code or the repository.
- [ ] Requests with an invalid or old signature are rejected.
- [ ] Processed event IDs are stored in a database.
- [ ] The endpoint answers in under 10 seconds, even under load.
- [ ] Your system orders events by `created_at`, not by arrival.
- [ ] Someone is alerted when `notification.not_delivered` arrives for a mandatory notification.
- [ ] You've tested with the Relay sandbox.
