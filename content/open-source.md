---
title: Open source
description: The tools I build and use, my public GitHub activity, and selected contributions to other projects.
sections:
  - title: Dotfiles
    id: dotfiles
  - title: Viewrule
    id: viewrule
  - title: GitHub activity
    id: github-activity
  - title: Contributions
    id: open-source
---
Open source is part of my day-to-day work: maintaining my own tools, trying them in practice, and contributing improvements upstream. Early experiments and visualizations live in [Labs](/labs/).

## Dotfiles {#dotfiles}

{{< project-logo src="/logos/projects/dotfiles.png" alt="Dotfiles repository logo" >}}

**My everyday development environment · Actively maintained**

My largest ongoing personal open-source project is the environment I work in. These dotfiles bring together Neovim, tmux, zsh, terminal tools, and coding-agent configuration across macOS and Linux.

I keep improving the small things that shape a working day: finding information, moving between sessions, carrying configuration between machines, and giving agents consistent instructions. A Makefile installs the configuration and converges the tools toward the setup I use.

This is an opinionated personal environment. Read the installation steps and scripts before applying it to your own machine.

[Browse the dotfiles](https://github.com/lanej/dotfiles) · [Setup and documentation](https://github.com/lanej/dotfiles#readme)

## Viewrule {#viewrule}

{{< project-logo src="/logos/projects/viewrule.png" alt="Viewrule repository logo" >}}

**Experimental tool · Used on this website**

How do you give a coding agent useful design boundaries—and check whether its UI stays within them?

Viewrule combines written design rules with executable browser checks for layout, density, context, and accessibility. It captures both page overviews and native-scale detail so large screens do not conceal small defects. Agents receive findings tied to the rules; human feedback helps refine the constraints.

It includes a CLI and a Claude Code plugin. This website uses it to check its rendered pages. Passing those checks means the configured constraints passed; it does not establish that a design is good or automate every accessibility judgment.

[Source and installation](https://github.com/lanej/viewrule) · [Releases](https://github.com/lanej/viewrule/releases) · [Why feedback matters](/writing/close-the-loop/)

## GitHub activity {#github-activity}

{{< github-activity >}}
