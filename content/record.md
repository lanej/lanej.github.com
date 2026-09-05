---
title: Selected work
description: Selected work, open-source contributions, and speaking by Josh Lane in financial infrastructure, cloud APIs, and deployment automation.
---
My work has moved from building infrastructure to leading the organizations that build and operate it. These examples cover both.

## Financial infrastructure at EasyPost {#financial-infrastructure}

**The work.** As a platform engineering leader, I was responsible for financial infrastructure, shared services, and developer tooling. That work included redesigning and automating financial data pipelines to reduce revenue recognition time.

**What changed.** A shorter revenue recognition cycle connected an engineering improvement to a business outcome. It is one example of why I treat financial operations and data quality as part of platform engineering, not as separate concerns.

Today, as CTO, I lead EasyPost’s technology organization and strategy across platform, product, and experience.

Career account: [professional profile](https://www.linkedin.com/in/lanejoshlane/). Current role: [EasyPost leadership biography](https://www.easypost.com/about/).

## OpenAPI code generation in ogen {#ogen}

**Open-source contributions · 2025**

I contributed to [ogen](https://github.com/ogen-go/ogen), which generates Go clients and servers from OpenAPI descriptions. The work expanded the API specifications the generator could handle, including more flexible parameter types and JSON media types.

Merged examples include [support for sum types in parameters](https://github.com/ogen-go/ogen/pull/1581) and [recognition of media types with a `+json` suffix](https://github.com/ogen-go/ogen/pull/1598). Other submissions covered schema discrimination, validation, and compatibility with real-world API specifications.

[Contribution history](https://github.com/ogen-go/ogen/pulls?q=is%3Apr+author%3Alanej+is%3Amerged)

## Engine Yard’s cloud API {#engine-yard}

**The work.** I architected and led development of the Engine Yard API. The work extended from the backend to the interfaces developers used to operate their applications and infrastructure.

**The public artifact.** The official Ruby client and command-line utility, `ey-core`, expose operations such as application deployment and environment management. The client supports a mocked mode for testing integrations without making live API calls.

The distinction matters: an API is not just a collection of endpoints. Its usefulness depends on whether teams can integrate it, test against it, and operate it reliably.

Career account: [professional profile](https://www.linkedin.com/in/lanejoshlane/). Software: [Engine Yard Core API client](https://github.com/engineyard/core-client-rb).

## Speaking: Sapporo RubyKaigi 2012 {#sapporo-rubykaigi-2012}

**Release Early and Release Often: Reducing deployment friction**

Sapporo, Japan · September 14, 2012 · Engine Yard

I presented Engine Yard’s approach to connecting automated testing, continuous integration, and deployment. The main cloud codebase could be released at least daily while retaining a rigorous testing and release process.

The talk is an early public example of my interest in engineering leverage: reducing the friction between completing a change and putting it into production.

[Conference program and abstract](https://sapporo.rubykaigi.org/2012/en/schedule/details/37.html) · [Event report (Japanese)](https://gihyo.jp/news/report/01/sapporo-rubykaigi2012/0001)

## Earlier Ruby open-source work {#ruby-open-source}

**Sinatra · 2011.** I contributed a [change to default parameter escaping](https://github.com/sinatra/sinatra/pull/361) and its [regression test](https://github.com/sinatra/sinatra/pull/362). Both were merged upstream.

**critic · 2017.** In my `critic` library, I worked on [ActiveRecord 5 compatibility and CI fixes](https://github.com/lanej/critic/pull/4).
