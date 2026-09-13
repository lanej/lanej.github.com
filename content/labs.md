---
title: Labs
layout: labs
featured:
  - title: Delivery-time uncertainty
    anchor: delivery-time
    status: Interactive prototype
    description: Replay simulated deliveries over real Oakland streets and explore how a map can show both an estimate and its uncertainty.
  - title: Design constraints in context
    anchor: design-constraints
    status: Interactive demonstration
    description: Explore a shipment dashboard with illustrative data and deliberate design violations. Compare their effects with the intended layout.
description: Small experiments in delivery uncertainty, visualization, and interface design, with working examples and explicit limits.
---
Working experiments: a way to explore an idea, see what it does, and refine it. Tools I maintain and use live on [Open source](/open-source/).

## Delivery-time uncertainty {#delivery-time}

**Interactive prototype · Synthetic deliveries over real Oakland streets**

{{< lab-demo >}}

How can a map show both a delivery estimate and its uncertainty? Replay a day across three independent delivery areas. Height and color encode time; surface thickness shows the prediction interval. Nearby estimates narrow as observations arrive.

The deliveries and predictions are simulated. The final resolved surface is supplied by the demo; a handful of observations does not establish certainty everywhere.

[Open the experiment](https://lanej.io/delivery-time-estimate-viz/) · [Source and model assumptions](https://github.com/lanej/delivery-time-estimate-viz)

## Design constraints in context {#design-constraints}

**Interactive demonstration · Illustrative shipment data**

The Viewrule mock application combines navigation, charts, filters, a shipment queue, and detail drawers. Its Design lab introduces deliberate violations so you can compare their effects with the intended layout.

This is a teaching example. Opening it does not run the Viewrule CLI against your browser.

[Open the demonstration](https://lanej.github.io/viewrule/) · [Viewrule on Open source](/open-source/#viewrule)
