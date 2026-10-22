# Technical writing portfolio · Lucía Tejeda Dorado

Technical writer and documentation lead with 8 years documenting enterprise software in very different domains: real-time banking notifications, casino management systems and contact centre platforms. I currently lead documentation at a B2B SaaS company for banks, where I founded the technical writing function from scratch.

My current documentation is client-only and protected behind SSO, so the samples here were written specifically to be public.

> **Two readers, one product.** This repository is the technical documentation. The [product content portfolio](https://github.com/ltejdor/product-content-portfolio) covers the same features for business readers, and shows how documentation drives adoption and upsell.

## One product, a complete documentation set

The samples document **Relay**, a fictional notification platform for banks, based on what I know about how banks send notifications. Documenting one product end to end shows how the pieces fit together, the way they would in a real documentation portal: each page has one job, and links to the others instead of repeating them.

| Sample | Type | Reader | What it shows |
|---|---|---|---|
| [Relay Notifications API](api-reference/README.md) | API reference | Bank developers | A REST API documented in Markdown and in an [OpenAPI 3.0 specification](api-reference/openapi.yaml), with idempotency, statuses and errors explained by what the developer should do. |
| [Receive delivery updates with webhooks](webhooks/README.md) | Developer guide | Backend developers | Signature verification, retries, duplicate events and ordering. |
| [Relay 2026.1 release notes](release-notes/relay-2026.1.md) and [migration guide](release-notes/migration-2026.1.md) | Release notes, migration guide | Developers and operations teams | A breaking change explained by who it affects and what to do, with a "do you need to act?" table and a step-by-step migration with no downtime. |
| [Mandatory, service and marketing notifications](concepts/notification-categories.md) | Concept | Product, compliance and technical teams | A regulatory topic (PSD2, DORA, GDPR and ePrivacy) explained for a mixed audience, with a decision guide. |
| [A customer didn't receive an OTP](troubleshooting/otp-not-received.md) | Troubleshooting | Support teams | A diagnosis that starts from what the customer says and leads to a cause and a fix, using the API. |
| [Relay Playground](https://ltejdor.github.io/technical-writing-portfolio/playground/) | Interactive demo | Anyone | The API and webhooks guides in action: send a notification, watch the fallback happen, and see how a receiver checks signed updates. Runs in the browser. |

## How these samples were made

**How I test documentation at work:** before I publish, I test every procedure in a demo or sandbox environment.

For public samples I don't have that environment, so I used AI (Claude) to build one. AI is already part of how I work: at my current company it helped me take our client documentation portal live in six months, and I built an interactive demo tool with Claude Code to show users how to use the product.

This is who did what in these samples:

- **What I did:** I decided what to document and for whom, based on what I know about how banks send notifications: fallbacks for one-time passwords, mandatory and marketing notifications, consent, and the slower, yearly release cycle of banking software. I chose the documentation set, defined the reader of each page and reviewed the content for accuracy in my domain.
- **What Claude did:** it built the test environment these samples needed: the [Relay Playground](https://ltejdor.github.io/technical-writing-portfolio/playground/), an interactive page where anyone can send a notification, watch the push-to-SMS fallback happen, and see how a receiver verifies real signed webhooks. It also drafted the text under my direction.
- **How we worked together:** I set the reader, the scope and the domain rules. Claude drafted, built and tested. I reviewed, corrected and decided what was published.

## Skills

- **Documentation types:** API reference, developer guides, tutorials, how-to guides, concepts, troubleshooting, release notes, migration guides, user manuals, installation and configuration guides, online help.
- **Docs as code:** Markdown, Git, GitHub, OpenAPI 3.0.
- **Tools I've used in my roles:** Paligo, Confluence, Trados.
- **Domains:** banking notifications, event-driven architecture and APIs (webhooks, queues, idempotency), EU regulation for banking communications (GDPR, ePrivacy, PSD2, DORA).
- **Documentation leadership:** information architecture, style guides, building a documentation function from scratch, leading a remote writer.
- **Languages:** Spanish and Catalan (native), English (professional), French (intermediate), German (basic, A2).

## Contact

- [LinkedIn](https://www.linkedin.com/in/ltejdor)
