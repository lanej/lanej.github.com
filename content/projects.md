---
title: Projects
description: Tools I build and experiments I use to explore software, design, and uncertainty.
sections:
  - title: Viewrule
    id: viewrule
  - title: Labs
    id: labs
---
I build tools to make ideas concrete, then use them to find out where the ideas hold up. Some become tools I use; others remain experiments. These are my own projects. [Contributions to other open-source projects](/open-source/) have a separate page.

## Viewrule {#viewrule}

**Experimental tool · Used on this website**

How do you give a coding agent useful design boundaries—and check whether its UI stays within them?

Viewrule combines written design rules with executable browser checks for layout, density, context, and accessibility. It captures both page overviews and native-scale detail so large screens do not conceal small defects. Agents receive findings tied to the rules; human feedback helps refine the constraints.

It includes a CLI and a Claude Code plugin. This website uses it to check its rendered pages. Passing those checks means the configured constraints passed; it does not establish that a design is good or automate every accessibility judgment.

[Source and installation](https://github.com/lanej/viewrule) · [Releases](https://github.com/lanej/viewrule/releases) · [Why feedback matters](/writing/close-the-loop/)

## Labs {#labs}

Small experiments for exploring a question through working software. Their state and limits are part of the description.

### Delivery-time uncertainty

**Interactive prototype · Synthetic delivery data**

How can a map show both a delivery estimate and how uncertain that estimate is—and make changes understandable as deliveries happen?

An interactive 3D replay over Oakland street geometry. Scrub through a day, orbit the map, and watch nearby estimates narrow as observations arrive across three independent delivery areas.

The deliveries and predictions are simulated. The final resolved surface is supplied by the demo, not inferred with certainty from a handful of observations. This is a visualization experiment, not a production forecasting service.

[Open the experiment](https://lanej.io/delivery-time-estimate-viz/) · [Source and model assumptions](https://github.com/lanej/delivery-time-estimate-viz)

### Design constraints in context

**Interactive demonstration · Illustrative shipment data**

What do design rules mean when a whole interface combines navigation, charts, filters, a queue, and detail drawers?

The Viewrule mock application puts those elements together. Its Design lab introduces deliberate violations so you can compare their effects with the intended layout.

The demo illustrates the rules; opening it does not run the Viewrule CLI against your browser. It is a teaching example, not a shipping operations product.

[Open the demonstration](https://lanej.github.io/viewrule/) · [How the mock application works](https://github.com/lanej/viewrule/blob/main/docs/mock-application.md)
