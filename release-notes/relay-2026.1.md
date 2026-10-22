# Relay 2026.1 release notes

**Release date:** 2 March 2026
**Previous version:** 2025.1

> Relay is a fictional notification platform, used here as an example.

Relay 2026.1 makes delivery results easier to trust and easier to act on. Webhooks are now protected against replay attacks, you can see exactly when a fallback starts, and notifications that Relay deliberately didn't send are no longer counted as failures.

## Before you upgrade

This release has **one breaking change** and **two deprecations**. Read [Breaking changes](#breaking-changes) and check the table below to see whether your team needs to act.

| If your team... | Do you need to act? | What to do |
|---|---|---|
| Counts or reports on `not_delivered` notifications | **Yes, before upgrading** | Handle the new `blocked` status. See [Step 2 of the migration guide](migration-2026.1.md#step-2-handle-the-blocked-status). |
| Receives webhooks | Yes, before 2027.1 | Verify the new `Relay-Signature` header. See [Step 1 of the migration guide](migration-2026.1.md#step-1-verify-the-new-signature-header). |
| Sends the `channel` field in `POST /notifications` | Yes, before 2027.1 | Move channel choices to fallback rules. See [Step 3 of the migration guide](migration-2026.1.md#step-3-stop-sending-the-channel-field). |
| Only uses the Relay console | No | — |

## Breaking changes

### Notifications that Relay doesn't send now have their own status: `blocked`

**Before:** when Relay didn't send a notification on purpose, for example a marketing message to a customer who hasn't consented, its status was `not_delivered`, the same as a real delivery failure.

**Now:** these notifications have the status `blocked`, and Relay sends the new `notification.blocked` webhook event.

**Why:** a blocked marketing message is Relay respecting the customer's consent, not a failure. Mixing both made delivery rates look worse than they were and triggered false alerts.

**Who is affected:** any code, report or alert that reads notification statuses. A report that calculates the delivery rate as `delivered / (delivered + not_delivered)` will show a higher rate after the upgrade, because blocked notifications are no longer in the denominator.

## New features

### Signed webhooks with replay protection

Webhooks now include a `Relay-Signature` header that signs the request body **together with a timestamp**. Your receiver can reject requests signed more than 5 minutes ago, so a captured request can't be sent again later.

See [Receive delivery updates with webhooks](../webhooks/README.md#step-1-verify-the-signature).

### New webhook event: `notification.fallback_triggered`

Relay now tells you when the first channel fails and it moves to the fallback, not just the final result. Use it to measure how often your customers' push notifications fail, and why.

### List a customer's notifications

The new `GET /notifications` endpoint returns a customer's notifications, filtered by type and time. Support teams can now find an OTP a customer says never arrived without knowing its ID.

See [List notifications](../api-reference/README.md#list-notifications).

### Notification categories

Every notification type now belongs to a category: `mandatory`, `service` or `marketing`. The category decides which rules apply: for example, Relay checks consent only for marketing notifications. Relay returns the category in API responses and webhooks.

When you upgrade, Relay assigns a category to your existing types:

| Existing types | Category assigned |
|---|---|
| `otp`, `security_alert` | `mandatory` |
| Types that have a marketing consent check | `marketing` |
| Everything else | `service` |

Review these in the Relay console after upgrading. See [Mandatory, service and marketing notifications](../concepts/notification-categories.md).

## Deprecations

These still work in 2026.1 and will be **removed in 2027.1**.

| Deprecated | Replacement |
|---|---|
| `X-Relay-Signature` webhook header (signs the body only) | `Relay-Signature` header (signs the body and a timestamp). Relay sends both headers during 2026.1. |
| `channel` field in `POST /notifications` | Fallback rules in your notification configuration. Relay ignores `channel` when a fallback rule exists for the notification type. |

## Fixed issues

- When a push was delivered at the exact moment the fallback time limit ended, the customer sometimes received both the push and the SMS. Relay now waits for the delivery confirmation to be fully processed before starting the fallback.
- `delivery_timeout_seconds` values above 3600 were silently reduced to 3600. Relay now rejects them with a clear error when you save the rule.
- Notification history in the console showed times in UTC even when the console was set to another time zone.
