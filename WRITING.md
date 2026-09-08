# Writing

This site is a record of working ideas, not a content feed. The writing should feel authored by one person without feeling produced from one template.

The standard is simple: make the reasoning legible, ground abstractions in something real, and leave enough texture that the piece could not have been written by anyone with the same bibliography.

`STYLE.md` is the companion visual standard. This file governs reasoning, voice, evidence, structure, and cadence; `STYLE.md` governs the shared presentation system.

## Start with something observed

Prefer an observation, decision, failure, artifact, or concrete example over a generic thesis.

Good openings usually begin from something that happened:

- a system behaved differently than expected;
- a team was asked to solve the wrong thing;
- a tool exposed a repeated failure mode;
- a design constraint forced a tradeoff;
- an existing idea became useful in a new context.

Avoid openings that could introduce hundreds of unrelated engineering essays after changing a few nouns.

## Concrete before abstract

Introduce the thing before naming the principle.

A useful default progression is:

`observation → example → mechanism → principle → implication`

This is not a required article structure. It is a test for whether the abstraction has been earned.

When a paragraph makes a broad claim, ask what the reader can point to that made the claim necessary. If there is no answer, add evidence, narrow the claim, or remove it.

## Explain mechanisms, not qualities

Avoid adjectives doing work that should be done by explanation.

Do not call something powerful, elegant, robust, transformative, strategic, or obvious when the mechanism can be described instead.

Prefer:

> The verifier runs against the deployed site, so a successful build cannot hide a broken mobile render.

Over:

> This creates a much more robust verification system.

The reader should be able to infer the quality from what the system does.

## Earn generalizations

Separate four kinds of statements:

1. **Observation** — what happened or what the system does.
2. **Inference** — what seems to follow from it.
3. **Judgment** — what I prefer or would do.
4. **Evidence** — what an external source establishes.

Do not make a judgment sound empirical or use a citation to imply that a source proves an application it only inspired.

Use first person when the claim actually comes from experience or preference. Phrases such as “I think,” “I want,” and “I use” are useful when they mark a real boundary between evidence and judgment.

## Write from particular experience

A piece should contain something that is difficult to substitute.

Concrete implementation details, real failure modes, a decision that changed, a tool that exists, or an uncomfortable tradeoff are more valuable than another polished statement of a familiar principle.

Before publishing, ask:

> Could this paragraph plausibly appear on 500 other engineering blogs after changing three nouns?

If yes, rewrite it or delete it.

## Preserve uncertainty

Do not manufacture certainty to make the argument cleaner.

It is acceptable to say:

- I do not know yet;
- this is a hypothesis;
- the example is hypothetical;
- this check narrows the risk but does not prove correctness;
- this worked in one context and may not generalize.

A qualification is useful when it changes how the claim should be interpreted. Do not add defensive caveats mechanically to every paragraph.

## Let the structure follow the material

There is one standard visual template: the shared Socrates-derived essay format in `STYLE.md`. Use ordinary Markdown H2 headings for its numbered chapters and the shared callout and diagram components. The argument determines what those chapters contain.

Legitimate shapes include:

- a short argument;
- an observation developed through examples;
- a technical deep dive;
- a postmortem or lesson;
- a design-philosophy piece;
- an amendment or response to an existing idea;
- a worked example that arrives at a broader conclusion.

Do not force every piece into an introduction, three supporting sections, a synthesis section, and a restated conclusion.

Keep the chapter presentation consistent. Vary the substance, chapter count, examples, and reasoning as the material requires.

## Avoid synthetic cadence

LLM-assisted prose has recognizable habits. Edit against them deliberately.

Watch for:

- repeated `Not X. Y.` constructions;
- three-item lists used for rhetorical neatness rather than meaning;
- a bold maxim every few paragraphs;
- paragraphs that each end with a miniature conclusion;
- repeated “This is not…” caveats;
- rhetorical questions immediately answered by the author;
- excessive em dashes;
- symmetrical sentence structures repeated across sections;
- endings that restate the entire essay in progressively grander language.

None of these forms is prohibited. Repetition is the problem.

Vary sentence length. Allow an ordinary paragraph to remain ordinary. Some sections should be short. Some ideas do not need a slogan.

## Use emphasis sparingly

Bold text should identify something the reader may reasonably return to, not manufacture significance.

Blockquotes should be used for actual quotations or for a small number of central propositions. If every section contains a boxed idea, none of them carries much weight.

Headings should help navigation, not narrate every transition in the argument.

## Cite intellectual lineage without performing scholarship

When an argument materially draws from an existing idea, make the lineage visible.

Use citations to:

- support factual or historical claims;
- identify the origin of an idea being extended;
- distinguish an author's original claim from my application of it;
- let an interested reader follow the argument deeper.

Do not attach citations merely to make a familiar judgment appear researched.

Prefer unobtrusive inline links or restrained references. Footnotes should not dominate the page visually. Cite the phrase or claim that depends on the source rather than turning an entire paragraph into a citation target.

When extending an existing work, say what is borrowed and what is mine.

## Visuals must carry information

A diagram should explain a relationship that prose handles poorly.

Use visuals for:

- loops;
- sequences;
- dependencies;
- contrasts;
- state transitions;
- layered models;
- structural relationships.

Do not add diagrams merely to break up a wall of text. Accent bars, typography, and whitespace can provide hierarchy without pretending to add information.

Every visual should survive this question:

> What does the reader understand faster or more accurately because this exists?

If the answer is “the page looks better,” use layout rather than a diagram.

## Keep conclusions proportionate

An article can stop when the argument has landed.

Do not automatically add a final section that restates the thesis, recaps every section, and broadens the claim to engineering, organizations, society, and life.

Read the final two paragraphs together. If the last paragraph only says the previous paragraph again with more gravity, delete it.

A useful conclusion may instead:

- state the practical rule that survived the argument;
- identify an unresolved question;
- return to the opening example;
- describe what changed in my own practice;
- stop immediately after the strongest sentence.

## Keep related essays genuinely related

Cross-links should represent intellectual dependencies, not a forced series.

If one essay extends another, state the relationship precisely. Do not repeatedly summarize the earlier piece for readers who can follow the link.

Shared concepts should retain the same meaning across essays. If a later piece changes the definition, make the revision explicit rather than quietly drifting the terminology.

## Editorial pass

Before publishing, review every piece against the same questions:

1. Delete a generic opening if the argument can begin with the actual observation.
2. Find unsupported abstractions and ground, narrow, or remove them.
3. Replace generic examples with actual ones when disclosure and clarity allow it.
4. Mark the boundary between observation, inference, judgment, and sourced evidence.
5. Identify borrowed ideas and link them where they materially influence the argument.
6. Remove unnecessary explanation for the expected reader.
7. Search for repeated rhetorical constructions and break the pattern.
8. Remove emphasis that exists only to make prose feel important.
9. Verify that every diagram adds information.
10. Read the ending skeptically and delete redundant resolution.
11. Ask what in the article could only plausibly have come from this experience, system, or line of reasoning.
12. Read it aloud once. Rewrite language that sounds composed rather than spoken.

## Corpus-level review

Individual essays can be strong while the collection becomes synthetic through repetition.

Periodically review several pieces together for:

- identical openings;
- repeated section counts or ordering;
- the same example shape;
- recurring bold aphorisms;
- identical caveat placement;
- repeated citation density;
- the same conclusion pattern;
- concepts that have drifted in meaning;
- articles that are different versions of the same argument.

Uniformity belongs in standards of reasoning, attribution, and quality. Variation belongs in reasoning, cadence, examples, and how an argument discovers its conclusion. Presentation follows the common essay format.

## The target voice

Technical, curious, opinionated, economical.

The prose should be comfortable making a strong claim when the reasoning supports it and comfortable exposing uncertainty when it does not. It should not try to sound literary, academic, visionary, or executive.

The goal is not polished authority.

The goal is to make the thinking inspectable.