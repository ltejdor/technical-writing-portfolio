# Migrate to Relay 2026.1

This guide walks you through the changes your integration needs for Relay 2026.1, in the order you should make them.

**Who this is for:** developers and operations teams at banks who maintain an integration with Relay.

> Relay is a fictional notification platform, used here as an example. For the full list of changes, see the [release notes](relay-2026.1.md).

## Timeline

| Date | What happens |
|---|---|
| 2 March 2026 | Relay 2026.1 is released. `blocked` status starts being used. Relay sends both webhook signature headers. |
| Before your bank upgrades | Complete [Step 2](#step-2-handle-the-blocked-status). |
| Before 2027.1 | Complete [Step 1](#step-1-verify-the-new-signature-header) and [Step 3](#step-3-stop-sending-the-channel-field). |
| 2027.1 | `X-Relay-Signature` and the `channel` field are removed. |

## Before you begin

You need:

- Access to the Relay **sandbox**, already on 2026.1. Do every step there first.
- Your webhook signing secret. It hasn't changed: the new header uses the same secret.

## Step 1: Verify the new signature header

During 2026.1, Relay sends both headers on every webhook:

```text
X-Relay-Signature: 9c1b0e...            ← deprecated, removed in 2027.1
Relay-Signature: t=1792660476,v1=5257a8...  ← new
```

Switch your receiver to `Relay-Signature` without a moment where it rejects valid events:

1. Add verification of `Relay-Signature`, as described in [Verify the signature](../webhooks/README.md#step-1-verify-the-signature). Keep the old verification in place.
2. Accept a request if **either** header is valid. Log which one was used.
3. Deploy, and send test events from the sandbox.
4. Check your logs. When every request has been verified with `Relay-Signature` for a few days, remove the code that checks `X-Relay-Signature`.

> **Important:** compute the signature over the **raw request body** and the `t` value, joined by a dot. The old header signed the body only, so reusing your old function as it is won't work.

## Step 2: Handle the `blocked` status

Do this step **before** your bank upgrades production. After the upgrade, notifications that Relay doesn't send on purpose have the status `blocked` instead of `not_delivered`.

1. Search your code, reports and alerts for `not_delivered`.
2. For each one, decide how a blocked notification should be treated:

   | Where `not_delivered` appears | Typical change |
   |---|---|
   | Delivery rate reports | Leave `blocked` out of the calculation, or report it separately. |
   | Alerts for failed notifications | Don't alert on `blocked`: nothing is broken. |
   | Code that resends failed notifications | Never resend a `blocked` notification. It was blocked because the customer didn't consent. |
   | Code that checks for "final" statuses | Add `blocked` to the list of final statuses. |

3. If you receive webhooks, add a handler for `notification.blocked`, even if it only logs the event. Without one, your receiver may answer with an error, and Relay will keep retrying.
4. In the sandbox, send a marketing notification to a test customer without marketing consent. Check that its status is `blocked` and that your reports and alerts behave as you expect.

## Step 3: Stop sending the `channel` field

If your requests include `channel` to force a channel, move that decision into your notification configuration:

1. List the notification types for which you send `channel`, and the value you send.
2. For each one, create or update a fallback rule with the same channel as `primary_channel`.
3. Remove `channel` from your requests.
4. In the sandbox, send each notification type and check the `attempts` in [`GET /notifications/{id}`](../api-reference/README.md#get-a-notification) use the channel you expect.

## Check that the migration is complete

- [ ] Your receiver verifies `Relay-Signature` and no longer depends on `X-Relay-Signature`.
- [ ] Reports, alerts and resend logic handle `blocked`.
- [ ] Your receiver answers `2xx` to `notification.blocked` and `notification.fallback_triggered`.
- [ ] No request includes the `channel` field.
- [ ] You've reviewed the categories Relay assigned to your notification types.
