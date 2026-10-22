# Relay Notifications API reference

Use the Relay Notifications API to send notifications to your bank's customers and check whether they were delivered.

**Who this is for:** developers at banks who integrate their systems (core banking, card processing, login) with Relay.

> Relay is a fictional notification platform, used here as an example. The full specification is in [`openapi.yaml`](openapi.yaml) (OpenAPI 3.0).

## Contents

- [How the API works](#how-the-api-works)
- [Base URLs](#base-urls)
- [Authentication](#authentication)
- [Idempotency](#idempotency)
- [Send a notification](#send-a-notification)
- [Get a notification](#get-a-notification)
- [List notifications](#list-notifications)
- [Statuses](#statuses)
- [Errors](#errors)
- [Try the API with a mock server](#try-the-api-with-a-mock-server)

## How the API works

You tell Relay **what** to notify and **to whom**. Relay decides **how**: the channel, the order of channels and when to use a fallback all come from your bank's notification configuration, not from the API request.

This keeps channel decisions out of your code. If your bank changes the fallback for OTPs from 30 to 20 seconds, nobody has to change the integration.

Sending is asynchronous:

1. You send a notification. Relay responds `202 Accepted` with an ID.
2. Relay delivers it through one or more channels.
3. You find out the result by [getting the notification](#get-a-notification) or by receiving [webhooks](../webhooks/README.md).

## Base URLs

| Environment | Base URL |
|---|---|
| Production | `https://api.relay.example/v1` |
| Sandbox | `https://sandbox.api.relay.example/v1` |

The sandbox accepts the same requests as production, but no message reaches a real customer. Use it to test your integration.

## Authentication

Every request needs an access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

Get the token with the OAuth 2.0 client credentials flow, using the client ID and secret Relay gives your bank. Tokens expire after one hour. Request a new one before it expires, not after a request fails.

## Idempotency

Every request that sends a notification needs an `Idempotency-Key` header with a unique value, such as a UUID:

```http
Idempotency-Key: 3f1c9a2e-6b7d-4e0a-9c55-0d2f8e71b4aa
```

If a request times out, you can't know whether Relay received it. Retry it **with the same key**: if Relay already accepted the notification, it returns the original response instead of sending it again. Your customer gets one OTP, not two.

| If you retry with... | Relay... |
|---|---|
| The same key and the same body | Returns the original response. Nothing is sent twice. |
| The same key and a different body | Returns `409 idempotency_key_reused`. |
| A new key | Treats it as a new notification. |

Relay keeps keys for 24 hours.

## Send a notification

```http
POST /notifications
```

Accepts a notification for delivery. The response means Relay has the notification, not that the customer has received it.

### Headers

| Header | Required | Description |
|---|---|---|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Idempotency-Key` | Yes | A unique value for this notification. See [Idempotency](#idempotency). |
| `Content-Type` | Yes | `application/json` |

### Body

| Field | Type | Required | Description |
|---|---|---|---|
| `customer_id` | string | Yes | Your bank's identifier for the customer, as registered in Relay. |
| `notification_type` | string | Yes | The type of notification as configured for your bank, such as `otp`, `security_alert` or `card_activity`. The type decides the category, channels and fallback rules. |
| `template_id` | string | Yes | The template with the message text for each channel and language. |
| `variables` | object | No | Values to insert into the template, such as a code or an amount. |
| `reference` | string | No | Your own reference, such as the ID of the transaction that triggered the notification. Up to 128 characters. Relay returns it in responses and webhooks. |

### Example request

```bash
curl -X POST https://sandbox.api.relay.example/v1/notifications \
  -H "Authorization: Bearer $RELAY_TOKEN" \
  -H "Idempotency-Key: 3f1c9a2e-6b7d-4e0a-9c55-0d2f8e71b4aa" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_7Q2M9X",
    "notification_type": "otp",
    "template_id": "otp_login_v2",
    "variables": { "code": "482913", "expires_in_minutes": 5 },
    "reference": "login-2026-10-22-0042"
  }'
```

### Example response

`202 Accepted`

```json
{
  "id": "ntf_01HZX3K8D2",
  "customer_id": "cus_7Q2M9X",
  "notification_type": "otp",
  "category": "mandatory",
  "reference": "login-2026-10-22-0042",
  "status": "accepted",
  "created_at": "2026-10-22T09:14:03Z",
  "attempts": []
}
```

Save the `id`. You need it to check the notification later.

## Get a notification

```http
GET /notifications/{notification_id}
```

Returns the notification and every delivery attempt Relay made, in order. This is where you see whether a fallback was used.

### Path parameters

| Parameter | Description |
|---|---|
| `notification_id` | The `id` Relay returned when you sent the notification. |

### Example response

The push wasn't delivered within the time limit, so Relay sent the SMS fallback, which was delivered:

`200 OK`

```json
{
  "id": "ntf_01HZX3K8D2",
  "customer_id": "cus_7Q2M9X",
  "notification_type": "otp",
  "category": "mandatory",
  "reference": "login-2026-10-22-0042",
  "status": "delivered",
  "created_at": "2026-10-22T09:14:03Z",
  "attempts": [
    {
      "channel": "push",
      "status": "not_delivered",
      "reason": "delivery_timeout",
      "sent_at": "2026-10-22T09:14:03Z",
      "updated_at": "2026-10-22T09:14:33Z"
    },
    {
      "channel": "sms",
      "status": "delivered",
      "reason": null,
      "sent_at": "2026-10-22T09:14:33Z",
      "updated_at": "2026-10-22T09:14:36Z"
    }
  ]
}
```

## List notifications

```http
GET /notifications?customer_id={customer_id}
```

Returns a customer's notifications, most recent first. Use it when you don't have the notification ID, for example when a customer calls support saying an OTP never arrived.

### Query parameters

| Parameter | Required | Description |
|---|---|---|
| `customer_id` | Yes | The customer whose notifications you want. |
| `notification_type` | No | Return only this type, such as `otp`. |
| `created_from` | No | Return only notifications created at or after this time, in UTC (ISO 8601). |
| `created_to` | No | Return only notifications created before this time, in UTC (ISO 8601). |
| `limit` | No | Maximum results, from 1 to 100. Default: 20. |

### Example request

```bash
curl "https://sandbox.api.relay.example/v1/notifications?customer_id=cus_7Q2M9X&notification_type=otp&created_from=2026-10-22T09:00:00Z" \
  -H "Authorization: Bearer $RELAY_TOKEN"
```

The response is an object with a `data` array of notifications, in the same format as [Get a notification](#get-a-notification).

## Statuses

### Notification status

The overall result of the notification.

| Status | Meaning | Final? |
|---|---|---|
| `accepted` | Relay has the notification and hasn't sent it yet. | No |
| `in_progress` | Relay is sending it, or waiting to decide whether to use the fallback. | No |
| `delivered` | One attempt was delivered. | Yes |
| `not_delivered` | Every attempt failed. | Yes |
| `blocked` | Relay didn't send it, for example because the customer hasn't consented to marketing. | Yes |

### Attempt status

The result of one attempt on one channel.

| Status | Meaning |
|---|---|
| `sent` | Handed to the channel provider. No delivery confirmation yet. |
| `delivered` | The provider confirmed delivery to the device or inbox. |
| `not_delivered` | The provider reported a failure, or the time limit ended without confirmation. |

### Reasons

When an attempt is `not_delivered`, `reason` tells you why.

| Reason | Meaning |
|---|---|
| `delivery_timeout` | No delivery confirmation arrived before the time limit. Common for push when the phone is offline. |
| `no_device` | The customer has no device registered for push. |
| `invalid_number` | The phone number doesn't exist or isn't valid for SMS. |
| `carrier_rejected` | The mobile carrier refused the SMS. |
| `provider_error` | The channel provider had a technical error. |

> **Delivered isn't read.** `delivered` means the message reached the device or inbox. Relay doesn't know whether the customer opened it.

## Errors

Errors return a JSON body with a stable `code` you can use in your error handling:

```json
{
  "code": "unknown_notification_type",
  "message": "Notification type 'otp_login' isn't configured for your bank.",
  "field": "notification_type"
}
```

Don't parse `message`. It's for people and may change.

| HTTP status | `code` | What to do |
|---|---|---|
| `400` | `missing_field`, `invalid_field` | Fix the request. Check `field`. Don't retry unchanged. |
| `401` | `invalid_token` | Get a new access token and retry. |
| `404` | `not_found` | Check the notification ID. |
| `409` | `idempotency_key_reused` | You reused a key for a different notification. Generate a new key. |
| `422` | `unknown_notification_type`, `unknown_template`, `unknown_customer` | The request is valid, but something it refers to isn't configured in Relay. Check your configuration. |
| `429` | `rate_limited` | Wait for the seconds in the `Retry-After` header, then retry with the same `Idempotency-Key`. |
| `5xx` | — | Retry with the same `Idempotency-Key`, waiting longer between each try. |

## Try the API with a mock server

You can explore the API on your own machine without a Relay account. [Prism](https://github.com/stoplightio/prism) reads `openapi.yaml` and answers requests with the examples in the specification.

You need [Node.js](https://nodejs.org/) installed.

1. From this folder, start the mock server:

   ```bash
   npx @stoplight/prism-cli mock openapi.yaml
   ```

   Prism starts on `http://127.0.0.1:4010`.

2. In another terminal, send a notification:

   ```bash
   curl -X POST http://127.0.0.1:4010/notifications \
     -H "Authorization: Bearer test" \
     -H "Idempotency-Key: 3f1c9a2e-6b7d-4e0a-9c55-0d2f8e71b4aa" \
     -H "Content-Type: application/json" \
     -d '{"customer_id": "cus_7Q2M9X", "notification_type": "otp", "template_id": "otp_login_v2"}'
   ```

   You get the `202` example response.

3. Try the same request without the `Idempotency-Key` header. Prism checks every request against the specification, so it returns an error status instead of `202`.

   The error body is one of the examples in the specification, so it won't describe your mistake. To see what was wrong, look at the terminal where Prism is running:

   ```text
   Violation: request.header Request header must have required property 'idempotency-key'
   ```
