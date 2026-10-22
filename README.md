# Technical writing portfolio · Lucía Tejeda Dorado

Technical writer and documentation lead with 8 years documenting enterprise software in very different domains: real-time banking notifications, casino management systems and contact centre platforms. I currently lead documentation at a B2B SaaS company for banks, where I founded the technical writing function from scratch.

My current documentation is client-only and protected behind SSO, so the samples here were written specifically to be public.

> **Two readers, one product.** This repository is the technical documentation. The [product content portfolio](https://github.com/ltejdor/product-content-portfolio) covers the same features for business readers, and shows how documentation drives adoption and upsell.

## One product, a complete documentation set

Most samples document **Relay**, a fictional notification platform for banks, based on what I know about how banks send notifications. Documenting one product end to end shows how the pieces fit together, the way they would in a real documentation portal: each page has one job, and links to the others instead of repeating them.

| Sample | Type | Reader | What it shows |
|---|---|---|---|
| [Relay Notifications API](api-reference/README.md) | API reference | Bank developers | A REST API documented in Markdown and in an [OpenAPI 3.0 specification](api-reference/openapi.yaml), with idempotency, statuses and errors explained by what the developer should do. Includes a mock server you can run. |
| [Receive delivery updates with webhooks](webhooks/README.md) | Developer guide | Backend developers | Signature verification, retries, duplicate events and ordering, with a [working receiver](webhooks/example/) you can test on your own machine in five minutes. |
| [Relay 2026.1 release notes](release-notes/relay-2026.1.md) and [migration guide](release-notes/migration-2026.1.md) | Release notes, migration guide | Developers and operations teams | A breaking change explained by who it affects and what to do, with a "do you need to act?" table and a step-by-step migration with no downtime. |
| [Mandatory, service and marketing notifications](concepts/notification-categories.md) | Concept | Product, compliance and technical teams | A regulatory topic (PSD2, DORA, GDPR and ePrivacy) explained for a mixed audience, with a decision guide. |
| [A customer didn't receive an OTP](troubleshooting/otp-not-received.md) | Troubleshooting | Support teams | A diagnosis that starts from what the customer says and leads to a cause and a fix, using the API. |

### More samples

From my [technical writing samples](https://github.com/ltejdor/technical-writing-samples) repository:

| Sample | Type | What it shows |
|---|---|---|
| [Build your first Grafana dashboard](https://github.com/ltejdor/technical-writing-samples/tree/main/first-grafana-dashboard) | Tutorial | A beginner tutorial for a product I had never used: I set up the environment from scratch to test and write it. |
| [Set up a fallback from push to SMS](https://github.com/ltejdor/technical-writing-samples/tree/main/push-sms-fallback) | How-to | The first Relay guide: a configuration task for bank technical teams. |

## How these samples were made

<!-- TODO Lucía: write this in your own words once you've run the examples. Suggested points:
     - What you ran yourself (Prism mock server, webhook receiver) and anything you changed after testing.
     - Where you used AI and what you decided.
     - Which parts come from your own domain knowledge (categories, OTP troubleshooting, release cadence in banking). -->

I write in Markdown, keep documentation in Git, and test what I document before I publish it. I use AI as a working partner, and I verify everything myself. More detail in [How I work](https://github.com/ltejdor/technical-writing-samples/blob/main/how-i-work.md).

## Skills

- **Documentation types:** API reference, developer guides, tutorials, how-to guides, concepts, troubleshooting, release notes, migration guides, user manuals, installation and configuration guides, online help.
- **Docs as code:** Markdown, Git, GitHub, OpenAPI 3.0.
- **Tools I've used in my roles:** Paligo, Confluence, Trados.
- **Domains:** banking notifications, event-driven architecture and APIs (webhooks, queues, idempotency), EU regulation for banking communications (GDPR, ePrivacy, PSD2, DORA).
- **Documentation leadership:** information architecture, style guides, building a documentation function from scratch, leading a remote writer.
- **Languages:** Spanish and Catalan (native), English (professional), French (intermediate), German (basic, A2).

## Contact

- [LinkedIn](https://www.linkedin.com/in/ltejdor)
