# Mandatory, service and marketing notifications

Not every notification a bank sends has the same weight. A one-time password has to arrive in seconds. A card payment alert is useful, but the customer can turn it off. A promotion can only be sent if the customer agreed to receive it.

Relay groups notifications into three **categories** so it can apply the right rules to each one automatically. This page explains what each category means, which rules Relay applies, and how to choose the right category for a new notification type.

**Who this is for:** product owners, compliance teams and technical teams at banks who decide which notifications the bank sends and how.

> Relay is a fictional notification platform, used here as an example. This page describes general principles of EU regulation as context. It isn't legal advice: rules vary by country and change over time, so confirm every decision with your bank's compliance team.

## The three categories

| | Mandatory | Service | Marketing |
|---|---|---|---|
| **Purpose** | The customer must receive it, for security or because the law requires it. | Helps the customer manage their products. | Promotes a product or offer. |
| **Examples** | One-time passwords (OTPs), fraud and security alerts, notices the bank is legally required to send | Card payment alerts, low balance alerts, direct debit reminders | A new savings account, a mortgage offer |
| **Needs marketing consent?** | No | No | **Yes** |
| **Customer can turn it off?** | No | Usually yes, in the app | Yes, at any time |
| **Quiet hours** | Never applied | Optional | Always applied |
| **Fallback to another channel** | Strongly recommended | Recommended | Rarely needed |

## Mandatory notifications

These are the notifications a bank can't afford to lose. They fall into two groups.

**Security.** OTPs are part of how banks apply strong customer authentication, which the EU's second Payment Services Directive (PSD2) requires for most online payments and logins. If the OTP doesn't arrive, the customer can't pay or log in. Fraud alerts are just as urgent: the sooner the customer sees them, the sooner they can block a card.

**Required by law.** Some regulations require banks to inform customers about certain events. For example, under PSD2 and under the Digital Operational Resilience Act (DORA), when a major incident affects customers' financial interests, the bank must inform them without undue delay.

Because the customer has to receive these, Relay:

- Never applies quiet hours. An OTP requested at 3 a.m. is sent at 3 a.m.
- Doesn't let customers opt out.
- Should always have a fallback configured.

## Service notifications

Service notifications are part of the service the customer has contracted. They don't need marketing consent, but customers usually expect to control them: someone who pays for coffee with their card every morning may not want a notification each time.

Relay applies the customer's notification preferences, which your app can update through Relay. Quiet hours are optional: a low balance alert can wait until the morning, a large card payment probably shouldn't.

## Marketing notifications

Under EU rules on electronic communications (the ePrivacy Directive, as each country implements it) and the GDPR, sending marketing by push, SMS or email generally requires the customer's prior consent, which they can withdraw at any time.

For every marketing notification, Relay checks the customer's consent first. If the customer hasn't consented, Relay doesn't send it and sets its status to `blocked`. This isn't a failure: Relay is doing what it should. See [Statuses](../api-reference/README.md#statuses).

## Choose the category for a new notification type

When your bank creates a new notification type, ask these questions in order. The first "yes" gives you the category.

1. **Does the customer need it to authenticate, or to protect their money or data?** → Mandatory.
2. **Does a regulation require the bank to send it?** → Mandatory. Ask your compliance team which regulation, and keep the reference.
3. **Does it promote a product, an offer or a service the customer doesn't have yet, even partly?** → Marketing.
4. **Otherwise** → Service.

### Watch out for mixed messages

Question 3 comes before question 4 on purpose. A service notification that includes a promotion is a marketing notification.

> "Your card payment of €45.00 at Café Central was approved."
> → Service.

> "Your card payment of €45.00 at Café Central was approved. Get 2% cashback with our Premium card!"
> → Marketing. Relay checks consent and blocks it for customers who haven't agreed to marketing, so they don't get the payment alert either.

If you want to promote a product after a payment, send two separate notifications: a service one with the payment, and a marketing one with the offer.

## Where to set the category

You set the category on each notification type in your notification configuration, not in the API request. Relay returns it in the `category` field of API responses and webhooks.

## Related pages

- [Relay Notifications API reference](../api-reference/README.md)
- [A customer didn't receive an OTP](../troubleshooting/otp-not-received.md)
- [Relay 2026.1 release notes](../release-notes/relay-2026.1.md), where categories were introduced
