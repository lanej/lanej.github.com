---
title: Selected work
description: Selected work by Josh Lane across technology strategy, shipping systems, cloud APIs, deployment automation, and open source.
---
EasyPost is the clearest through-line in my work. I joined as a senior software engineer in 2019 and became CTO in 2026. The scope changed from building shipping software to deciding which technical systems and organizational changes the company should invest in.

## Technology strategy at EasyPost {#easypost-technology-strategy}

As CTO, I own company-wide technology strategy across product, platform, data, and infrastructure. The job is no longer simply to make engineering better; it is to decide where technology can create leverage for the company and make sure the architecture and operating model reinforce that choice.

That has meant simplifying overlapping products and systems, treating data integrity and decision systems as core capabilities, and making technology investment decisions with efficiency, margin, risk, enterprise readiness, and scalable growth in view.

The current role is a continuation of work I did deeper in the stack:

- **2019–2022 — software and engineering management.** I worked on warehouse logistics, inventory management, third-party order integrations, and fulfillment software; later I led work on USPS CASS-certified address verification and the decomposition of a monolithic application toward service-oriented architecture.
- **2022–2025 — platform and financial infrastructure.** My scope expanded across infrastructure, finance, shared services, and developer tooling. I led architectural reviews and R&D, redesigned financial data pipelines to shorten revenue-recognition time, and worked on developer throughput and reliability.
- **2025–2026 — Vice President of Engineering.** I led a 130+ engineer organization across Core API, Enterprise, Platform, and international subsidiaries. The work shifted toward portfolio simplification, capital allocation, operating mechanisms, and the evolution of Core API and decision systems.
- **2026–present — Chief Technology Officer.** The scope is company-wide: technology strategy, architecture, data, infrastructure, organizational design, and the connection between technical decisions and business economics.

That progression is more useful to me than a list of titles because it changed how I think about technical leadership: architecture, organizational structure, and economics are usually different views of the same system.

Current role: [EasyPost leadership biography](https://www.easypost.com/about/). Career history and scope: [professional profile](https://www.linkedin.com/in/lanejoshlane/).

## Engine Yard’s cloud API {#engine-yard}

I architected and led development of the Engine Yard API. The work extended from the backend to the interfaces developers used to operate their applications and infrastructure.

The official Ruby client and command-line utility, `ey-core`, expose operations such as application deployment and environment management. The client supports a mocked mode for testing integrations without making live API calls.

The distinction matters: an API is not just a collection of endpoints. Its usefulness depends on whether teams can integrate it, test against it, and operate it reliably.

Software: [Engine Yard Core API client](https://github.com/engineyard/core-client-rb).

## Speaking: Sapporo RubyKaigi 2012 {#sapporo-rubykaigi-2012}

**Release Early and Release Often: Reducing deployment friction**

Sapporo, Japan · September 14, 2012 · Engine Yard

I presented Engine Yard’s approach to connecting automated testing, continuous integration, and deployment. The main cloud codebase could be released at least daily while retaining a rigorous testing and release process.

The talk is an early public example of my interest in engineering leverage: reducing the friction between completing a change and putting it into production.

[Conference program and abstract](https://sapporo.rubykaigi.org/2012/en/schedule/details/37.html) · [Event report (Japanese)](https://gihyo.jp/news/report/01/sapporo-rubykaigi2012/0001)
