# A customer didn't receive an OTP

Use this page when a customer tells your bank that a one-time password (OTP) never arrived, or arrived too late to use.

**Who this is for:** second-line support and technical teams at banks who have access to the Relay API or console.

> Relay is a fictional notification platform, used here as an example.

## Before you begin

Ask the customer for:

- When they tried to log in or pay, as precisely as possible.
- Whether they received **nothing**, or received the OTP **late**.
- The phone number they expected the SMS on, if it was SMS.

You need the customer's `customer_id` in Relay.

## Step 1: Find the notification

List the customer's OTPs around the time they gave you:

```bash
curl "https://api.relay.example/v1/notifications?customer_id=cus_7Q2M9X&notification_type=otp&created_from=2026-10-22T09:00:00Z&created_to=2026-10-22T10:00:00Z" \
  -H "Authorization: Bearer $RELAY_TOKEN"
```

Times are in UTC. If your customer is in Madrid, 11:00 local time in summer is 09:00 UTC.

**If the list is empty**, Relay never received a request to send the OTP. The problem is before Relay: in the login or payment system that should have requested it. Escalate to the team that owns that system, with the customer ID and the time.

**If you find one or more notifications**, open the one that matches with [`GET /notifications/{id}`](../api-reference/README.md#get-a-notification) and go to Step 2.

## Step 2: Read the attempts

Each notification lists its `attempts`, one per channel, in the order Relay tried them. Find the row below that matches what you see.

| `status` of the notification | What the attempts show | What happened | Go to |
|---|---|---|---|
| `not_delivered` | Only a push, `not_delivered` | The push failed and there was no SMS fallback. | [Cause A](#cause-a-no-fallback-for-otps) |
| `not_delivered` | A push and an SMS, both `not_delivered` | Relay tried both channels and both failed. | [Cause B](#cause-b-the-sms-failed) |
| `delivered` | The last attempt is `delivered` | Relay delivered it. The problem is timing or the device. | [Cause C](#cause-c-delivered-late) or [Cause D](#cause-d-delivered-but-the-customer-didnt-see-it) |
| `accepted` or `in_progress` | No attempts, or the last one is `sent` | Relay is still working on it. | [Cause E](#cause-e-still-in-progress) |

## Cause A: No fallback for OTPs

The push wasn't delivered and Relay had no other channel to try. The `reason` tells you why the push failed:

- `no_device`: the customer doesn't have the bank's app, or has disabled notifications.
- `delivery_timeout`: the phone was probably offline.

**To fix it for this customer:** they can request a new OTP once they're connected, or your bank can send it through another channel it supports.

**To fix it for everyone:** OTPs should always have a fallback. Ask the team that manages your Relay configuration to add one.

## Cause B: The SMS failed

Look at the `reason` of the SMS attempt:

| `reason` | Meaning | What to do |
|---|---|---|
| `invalid_number` | The number isn't valid for SMS. | Check the phone number in the customer's profile with them. |
| `carrier_rejected` | The customer's mobile carrier refused the SMS. Common when the customer has blocked messages from short codes, or is roaming on a network that blocks them. | Ask the customer whether they've blocked SMS from unknown senders, or are abroad. |
| `provider_error` | Relay's SMS provider had a technical error. | If you see this for several customers at the same time, open a ticket with Relay support. |

## Cause C: Delivered late

Compare the times:

- `created_at` of the notification: when Relay received the request.
- `updated_at` of the delivered attempt: when it was delivered.

If the OTP was delivered after it had expired, check the time limit of the fallback rule. Example: an OTP valid for 5 minutes with a 300-second push time limit expires at the same moment the SMS is sent.

**To fix it:** the time limit for OTPs should be short, typically under a minute. Ask the team that manages your Relay configuration to review it.

## Cause D: Delivered, but the customer didn't see it

`delivered` means the device or the carrier confirmed delivery. Relay doesn't know whether the customer saw it. Ask the customer to check:

- **For push:** the phone's notification center, and whether notifications from the bank's app are muted.
- **For SMS:** spam or "unknown senders" folders. Some phones filter messages from short codes automatically.
- **For both:** whether they have more than one phone, or changed phones recently.

## Cause E: Still in progress

If the notification was created a few seconds ago, wait for the fallback time limit to pass and check again.

If it has been `accepted` or `in_progress` for more than a few minutes, it's not normal. Open a ticket with Relay support and include the notification `id`.

## When you escalate to Relay support

Include:

- The notification `id`.
- The `customer_id`.
- The full response of `GET /notifications/{id}`.
- What the customer told you, with the time and time zone.

Never include the OTP code itself in the ticket.

## Related pages

- [Relay Notifications API reference](../api-reference/README.md)
- [Mandatory, service and marketing notifications](../concepts/notification-categories.md)
- [Receive delivery updates with webhooks](../webhooks/README.md): set up alerts so you find failed OTPs before customers call.
