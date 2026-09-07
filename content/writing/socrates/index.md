+++
title = "Socrates: Before I Say ‘Go Build It’"
description = "I built a Claude skill to challenge the request, preserve the decisions, and make the handoff executable."
date = 2026-09-06T17:45:00-07:00
draft = false
toc = false
layout = "socratic"
callout = "Research should arm the question, not eliminate it."
+++

{{< socrates-opening >}}
I originally told Socrates to ask me fewer questions.

Socrates is a [Claude skill](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md) I use before planning a piece of work. An earlier version had what sounded like a good rule: read the code, inspect the configuration, look through prior decisions, and try to answer every question before interrupting me. If the agent found a plausible answer, it should record the assumption and move on.

That worked well for facts. It was a bad rule for decisions.

Which language does this repository use? Research it. Does an old restriction still serve a purpose? The repository can tell me that the restriction exists. It cannot tell me whether I still want it.

I had optimized the skill to reduce conversation at exactly the point where the conversation was useful. I did not need a faster requirements form. I wanted the agent to help me think through the work before an implementation gave one interpretation momentum.

So I changed the rule: [research should arm the question, not eliminate it](https://github.com/lanej/dotfiles/commit/39048c0f3cc72f8f6ab7a0c025bd5304be24fb2d). Bring me what you found. Explain why it might matter. Then ask the question that the evidence cannot answer for us.
{{< /socrates-opening >}}

{{< socrates-section id="why-socrates" number="01" title="Why Socrates" diagram="method" >}}
The part of the [Socratic method](https://plato.stanford.edu/entries/plato-ethics-shorter/#2) I’m borrowing is not “keep asking why.” It is the examination of a claim against the rest of what we think we know. A question exposes an assumption; another commitment puts pressure on it; the contradiction or missing premise becomes visible.

That matters because a request to an AI is not necessarily a correct specification of the problem. I may arrive with a preferred solution and a lot of confidence. The model may have an equally plausible interpretation. Neither deserves to become the plan merely because it was stated first.

The useful outcome is sometimes less certainty, not more. We discover the hole in an answer we were already prepared to act on.

That is different from endless debate. Socrates still has to converge. The current dialogue loop works one consequential topic at a time: research it, ask one informed question, judge the answer, follow up when it is vague or contradictory, and stop when the relevant issue is stable enough to proceed. There is no question quota to satisfy and no prize for making a small task ceremonial.

The useful thing is making the assumption visible before either of us builds on it, not getting the agent to agree with me.
{{< /socrates-section >}}

{{< socrates-section id="request-to-clarity" number="02" title="From request to clarity" kicker="A real bug in Socrates itself" diagram="comparison" >}}
A bug in Socrates became a useful example of what this process is for.

Socrates stores each piece of work in a timestamped directory under `.socrates/`. Originally there was one `.current` file that pointed at the active specification. That was fine while one Claude session worked in a repository. With two sessions, either conversation could replace the pointer. Both specifications could remain perfectly intact while one agent quietly resumed against the other agent’s task.

The obvious fix was: **make the pointer session-specific.**

That sentence is a direction, not yet a contract.

What counts as a session? A resumed conversation should recover which specification? If a binding exists but its target has been deleted, do we fail or fall back? If the binding is missing and several specifications exist, is choosing the newest acceptable? What tells us that another candidate is active in a different session?

Those questions changed the work. The eventual fix binds a specification to `CLAUDE_CODE_SESSION_ID`, preserves the binding across resume, treats a missing binding and a deleted target as explicit fallback cases, and refuses to guess in non-interactive critique or verification when several candidates remain. The implementation also had to use the Claude process identifier rather than the PID of a shell spawned by a tool call.

That behavior is documented in the [session-binding change](https://github.com/lanej/dotfiles/commit/e48e4f0f3b8b7e5b1fe4d0b3ff17846529902977). The important part is not the filename. It is that the conversation turned “use a different pointer” into a statement of what must remain true when the normal path fails.

A competent agent could have implemented the first sentence in a few minutes. I would have gotten a cleaner version of the same underspecified system.
{{< /socrates-section >}}

{{< socrates-section id="layered-reasoning" number="03" title="Layered reasoning" kicker="Make the argument inspectable" diagram="layers" >}}
Once the dialogue settles, Socrates does something that matters more than producing polished prose: it turns the result into a [reasoning chain](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md#phase-2--validation-and-layered-reasoning).

The layers are problem, requirements, constraints, risks, success, validation, and execution readiness. I do not care whether all seven headings are present because seven is a nice number. I care that each layer has to follow from the one below it.

For the session bug, the **problem** is not “the pointer filename is global.” The problem is that one conversation can load another conversation’s specification. That distinction changes the **requirements**: preserve each session’s binding and recover it correctly. It exposes a **risk**: a fallback can silently select the wrong task. That risk changes **success** and **validation**: normal resolution is not enough; we need to force missing, stale, and ambiguous states.

This is where false greens become easier to see. “The new pointer file exists” is evidence about the implementation. It is not evidence that a resumed session loads the intended specification. “Fallback works” is meaningless if the test never makes the fast path unavailable.

The specification also records authority boundaries. An executor can choose implementation details. It should not decide that ambiguity means “pick the newest specification” merely because that makes the code simpler. If the choice changes what task is being executed, that decision belongs back in the agreement.

That is one of the ways this is specifically about AI. The next agent may be capable and completely unfamiliar with the conversation that produced the requirement. The document has to carry the reasoning that prevents it from helpfully solving a different problem.
{{< /socrates-section >}}

{{< socrates-section id="preserve-intent" number="04" title="Document, sequence, and preserve intent" diagram="workflow" >}}
The output of Socrates is not the conversation. It is a set of artifacts another process can use: an authoritative `spec.md`, an optional independent critique, a `plan.md`, and verification evidence when the work is done.

A condensed decision record for the session bug might look like this:

> **Decision**  
> If several specifications remain possible, stop. Do not select the newest one automatically.
>
> **Reason**  
> Recency does not establish which task the user intended.
>
> **Executor may decide**  
> How to implement the lookup and pointer storage.
>
> **Executor must not change**  
> Ambiguity into a silent guess.
>
> **Evidence**  
> Remove the binding, leave multiple candidates, and confirm that verification refuses to proceed.

That is not copied from a saved Socrates session. It is the kind of information I want the handoff to preserve: the decision, why it exists, what is delegated, and what evidence would demonstrate it.

Once that agreement is stable enough, Socrates freezes and versions the specification before planning. “Frozen” is procedural, not magical file protection. If critique exposes a bad assumption or execution discovers something genuinely new, the specification can reopen. What should not happen is an executor quietly weakening the requirement until its preferred implementation qualifies.

Then sequencing becomes a different problem. Every task in the plan has to trace back through a requirement to the original problem, and the plan gets its own dependency graph. The question is no longer “what do we mean?” but “what has to happen before what?”

The session-binding change went through five rounds of independent plan critique. Those rounds caught concrete defects: missing tool permissions, using `$$` when the code needed Claude’s PID, twice dropping the step that loads `spec.md`, a grep-based acceptance check that could false-positive against its own new filenames, and a dogfood test that claimed to exercise fallback without actually forcing execution down the fallback path.

That is why I separate specification review from plan review. A specification can be right while the proposed steps fail to preserve it. A plan can be internally coherent while testing the wrong thing.

The final checks deliberately exercised direct resolution, forced fallback, claiming an unbound session, a deleted pointer target, and the picker/write behavior. The verifier was not allowed to redefine success at the end.

This is an AI workflow, but the underlying discipline is older and broader: examine the claim, make the reasoning explicit, preserve the decisions, sequence the dependencies, and test the thing you actually meant.

I use Socrates because AI makes execution cheap enough that **starting the wrong work is increasingly the expensive mistake**. Sometimes the outcome is a better plan. Sometimes the outcome is deciding not to build the thing I originally asked for.

Before I say “go build it,” that is exactly the kind of friction I want.
{{< /socrates-section >}}

{{< socrates-resources >}}
Continue with [Close the Loop](/writing/close-the-loop/), on verifying the work against reality. [Read the Socrates source](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md).
{{< /socrates-resources >}}
