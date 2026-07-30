---
name: emaillove-eds-converter
description: Convert an audited legacy Figma design system into a working Email Love design system, foundations first, then modules in batches with design review between batches. Builds under the audit's source fidelity tier, preserving the source's geometry where it is a specification and building to email standards where it is not. Use this skill whenever the user wants to convert, rebuild, or migrate their existing Figma email templates to the Email Love structure, run foundations, or convert a batch of modules, after the emaillove-migration-audit skill has produced their audit report. The audit report is required input; if it does not exist yet, run the audit first.
---

# Email Love EDS Converter

Convert an audited legacy design system into a working Email Love design system. This skill
follows a migration audit (the emaillove-migration-audit skill produces it) and works in two
phases: foundations once, then modules in batches. A designer reviews between batches; never
convert the whole library in one unreviewed pass.

Prefer to have this done for you? Email Love's team runs this exact process, with design
review included, as part of Enterprise onboarding: hello@emaillove.com.

Three hard rules:

- **The customer's source file is read-only, always.** All building happens in a separate
  target file. Reads from the source are inspections, screenshots, and asset downloads only.
- **The audit report is required input.** It carries the source fidelity tier, the per-module
  classification (A/B/C/D plus any named concession), the scale factor where one applies, the
  brand foundations, and the flags. Do not re-derive what it already settled; do re-verify
  anything that looks wrong when you meet the actual nodes.
- **The SOURCE FIDELITY TIER decides where your numbers come from, so read it first.** The audit
  classifies whether the source's geometry is a specification at all, and every phase below
  branches on the answer:
  - **AUTHORITATIVE:** the geometry IS the spec. Preserve the source's widths, margins, type
    sizes, and spacing. Deviating from a source number needs a reason, written down.
  - **PARTIAL:** preserve what the audit proved consistent, standardise what it did not, and flag
    each standardisation as a place the build differs from the source on purpose.
  - **REFERENCE ONLY:** take the brand (palette, typefaces, logo), the copy, and the module
    structure. **Build the geometry to email standards, and do not scale anything.** There is no
    factor to read, no source proportion to preserve, and no ratio of the source's to check
    against. A source measurement is not evidence here: it is an artefact of how the file happened
    to get made.

  A tier is a judgement the audit recommends and the customer's designer can overrule. If they
  overrule it, build under the tier they give you and record whose call it was.

## Inputs

1. The migration audit report from the emaillove-migration-audit skill (file or pasted).
2. The source Figma file link (read-only).
3. The target file: an existing one the team designates, or create one named
   "[Customer] - Email Love Design System" via the Figma MCP.
4. Which batch to run: "foundations", or a batch of modules named by their rows in the audit's
   **Module inventory** ("batch 1: the five modules the audit's Recommended next step lists
   first", or an explicit list of row names). An explicit list from the user wins over the
   audit's proposed batch.

### What you read out of the audit, by section name

The audit's sections map onto the phases below. Use the audit's own words for these artifacts so
the two halves of the migration stay one conversation:

- **Module inventory** (required in the report): the deduplicated module list. One row is one
  module, and a batch is a group of rows. It carries each module's name (which becomes the
  component name), category, the designs it appears in, the source ref, verdict, concession,
  build constraints, and effort. The source ref is the appearance to convert from and the
  boundary to crop at, so you never re-derive a split the audit already made; a row's build
  constraints bind how that module is built (Phase 3). This is what Phase 3 iterates over, and its
  category ORDER is what Phase 2 builds the component pages in. There
  is no per-design conversion pass: the report's Per-design roll-up is context for the customer,
  not a work list.
- **Source fidelity** (required in the report): the tier, plus the signals behind it. **Read this
  before any other section**, because it tells you whether the sections below are measurements to
  carry across or evidence about a file whose proportions you are deliberately not reusing. State
  the tier in your first line to the user, so nobody discovers it halfway through a type ramp.
- **Scale factor** (required unless the source is REFERENCE ONLY): the number every geometry
  decision is divided by. Read it; never re-derive it (see Phase 2). On a REFERENCE ONLY source
  this section carries no number and states email standards instead. **That is a finished answer,
  not a gap to fill:** do not derive a factor of your own, not from the width, not from the ramp,
  and not "for information", because whoever builds applies the number that is there.
- **Brand foundations:** the type ramp on email-safe fallbacks, the proposed theme colors, the
  spacing scale, the button styles, the target email width, and the source's content margin as a
  percentage of source width with the content width it converts to. Phase 2 builds from these, and
  it SETS the library's one content width from that derived value rather than inventing one. An
  older audit may carry no margin percentage; then Phase 2 decides the content width itself and
  says so. **On a REFERENCE ONLY source, only the brand half of this section is source material:**
  the palette, the typefaces, the logo, the copy. The geometry half (ramp sizes, spacing scale,
  content width) is the email standards the audit stated, and the source's own numbers stay in the
  report as evidence for the tier rather than as a specification to build.
- **Flags:** the gates. Two always block work rather than describe it: the scale factor when
  the audit's two derivations disagreed, and each named concession. Both need a human "yes"
  before the affected modules get built. **A third joins them whenever Flags carries the source
  fidelity tier**, which the audit does whenever that call was a judgement rather than a reading
  (audit Step 8): the tier needs the same yes, because it decides whether the customer's geometry
  comes across at all. Where the tier is REFERENCE ONLY the yes is cheap rather than deliberative,
  so ask it as one confirming sentence at the start of foundations: their brand comes across and
  the geometry will be ours.

If the report has no Module inventory, it predates this contract. Do not improvise a module list
out of a per-design table: go back and run the audit skill again, which is minutes of work and
saves rebuilding a batch against the wrong boundaries.

A report with a Module inventory but **no Source fidelity section** predates the fidelity contract,
and that one you can settle in a question instead of a re-run. Ask the audit's own signals: is the
source at a standard email width with a mobile variant, are equivalent margins identical rather
than merely similar, and does it have local text styles, paint styles, variables, components, and
auto layout. Most of those present is AUTHORITATIVE, almost none is REFERENCE ONLY, a mix is
PARTIAL, and a source at neither a standard width nor consistent margins cannot be AUTHORITATIVE
whatever the rest says. Record the tier you settled on and that you settled it here rather than
reading it. **A missing Scale factor is only a gap on an AUTHORITATIVE or PARTIAL source.** On a
REFERENCE ONLY one there is nothing missing, so do not go back for the number.

## How long this takes

Read this before starting a batch, and set the user's expectations from it. These are measured
figures, not guarantees. Each was timed on a batch of FIVE modules, with several agents working
in parallel and an adversarial verification pass on every module:

- rendering a batch from converted MJML: about 38 minutes
- restructuring a batch: about 31 minutes
- promoting a batch to components: about 28 minutes
- a sizing correction pass: about 18 minutes
- adding component properties: about 14 minutes

A single agent following this skill has a different profile: less parallelism, but also fewer
passes, since it is not re-verifying another agent's work. Treat the figures as the shape of the
work rather than as a quote.

Honest ranges to give a user:

- **The audit** (the emaillove-migration-audit skill): minutes, scaling with library size. It
  creates nothing, so it is the quick part.
- **Foundations:** a single pass, comparable in length to one batch of modules.
- **A first batch of about five modules:** expect tens of minutes, and longer on an unstructured
  source.
- **A full library of a hundred or more modules:** multiple sessions. That is exactly why the
  process is batched with a design review between batches instead of run end to end.

**Where the time actually goes: round trips to Figma, not model thinking.** Every node created
or read is a call. A module with forty nodes therefore takes many times longer than one with
six, and the node count predicts the time far better than how complicated the design looks.

**Source shape moves the number more than anything else.** An email-native source (frames
already at 600 or 640, auto layout in place) converts far faster than an unstructured one
(groups, absolute positioning, a scaled-up mockup), because in the second case the agent must
first work out where each module begins and ends before it can rebuild anything. Measured on a
real unstructured file: roughly three times slower per module than an email-native one.

**The worker is not the bottleneck.** The design-converter conversion itself takes a few seconds
to about half a minute per design. Everything after it, transcribing the result into Figma, is
where the time is spent. Never leave a user thinking the AI is the slow part.

**Say this out loud before you begin.** At the start of every batch, tell the user roughly how
long you expect it to take and that progress will be quiet for long stretches, so twenty silent
minutes does not read as a hung run.

### Report progress while it runs

The estimate is the promise; these checkpoints are how you keep it. Post exactly one line at each
of these five points, and nowhere else:

1. **After the source census** (your read of the audit's Module inventory plus your first look at
   the source file): the counts found. Modules in the inventory, modules in this batch, designs
   they come from. **Add the source fidelity tier you are building under**, and on a REFERENCE ONLY
   source the one clause that follows from it, that the geometry is being built to email standards
   and their brand is what comes across. A user who hears that up front reads a module whose
   margins do not match their file as the plan rather than as a mistake.
2. **Before a batch starts:** what IS in it by module name, what is NOT and why (deferred,
   blocked on an unconfirmed concession, out of scope), and the opening estimate.
3. **After each module completes:** count, percentage, module name, revised remaining time.
4. **The moment a step is retried or a decision goes to the user:** a `recache=1` re-run, a
   trivial-response retry, an unconfirmed concession, an unsigned scale factor. Say it then, not
   in the batch report.
5. **At the end:** what was built, what was skipped, and why.

How each line is written:

- **A count and a percentage, never prose.** "Module 3 of 7 done, 43 percent" is the format.
  "Making good progress" is not a checkpoint. The denominator is the batch size you listed at
  checkpoint 2.
- **Name the module.** "Module 4 of 7: Global footer" lets the user click it in Figma. "Module 4
  of 7" does not.
- **Revise the estimate from observed pace, every time.** After module 1 you know the real
  per-module cost in this file, so recompute the remainder from it instead of repeating the
  opening guess. Revising upward is fine and expected: an unstructured source runs slower than
  the opening guess, and the honest larger number beats the tidy stale one.
- **Say what is happening now, in the user's language.** "Transcribing the footer, 43 nodes"
  tells them why it is slow. "Calling the worker" does not.
- **Module boundaries only.** Never narrate per node, per API call, or per screenshot. A
  fifty-node module gets one line when it finishes, not fifty.
- **Own an overrun the moment it is apparent.** If the run is tracking well past the estimate you
  gave, say so at that module boundary, with the new number. A user who was told twenty minutes
  and is at forty should hear it from you rather than work it out.

One worked example, the format to copy:

> Module 3 of 7 done, 43 percent: Global footer, 43 nodes transcribed. Modules are averaging 6
> minutes in this file against the 4 I estimated, so the remaining 4 are roughly 25 minutes,
> putting the batch near 45 minutes total against the 30 I opened with. Next: Module 4 of 7,
> Two column product row.

## Phase 2: Foundations (run once per customer)

**Start by reading the audit's Source fidelity tier, and say which tier you are building under
before you create a node.** It decides where every number below comes from, so it is not something
to discover in the middle of a type ramp.

**Everything you build, here and in Phase 3, is at email scale.** How you get there is the tier's
answer, not a single procedure:

- **AUTHORITATIVE or PARTIAL: build from the source, through the factor.** Take the factor from the
  audit's Scale factor section and divide the source numbers by it: type sizes, line heights, the
  spacing scale, paddings, spacer heights. **Widths are not the factor's to divide**: the body width
  and everything measured across it (content width, column splits, image widths) come from the target
  email width, which is the width-versus-type check below and render spec 0.6's two factor tension.
  Do not re-derive the factor from the file, even when the arithmetic looks
  obvious to you: the audit computed both derivations, and where they disagreed a human chose
  between them, so a fresh derivation here quietly overrules that decision. When the audit says
  the factor is still a designer decision and nobody has confirmed it, get the yes before you
  build, because the factor changes every module. State the factor you built at in the foundations
  report, so batch 1 and every batch after it inherits one number. On a PARTIAL source the factor
  came from the deliberate part of the file and the audit said which part that was: preserve what
  it proved consistent, standardise the rest onto the defaults below, and give every
  standardisation its own line in the report.
- **REFERENCE ONLY: build to email standards, and scale nothing.** There is no factor, you do not
  derive one, and there is no source measurement to divide. **The defaults, stated rather than
  derived:** a **600** body width; **one content width for the whole library**, 560 on a 600 body,
  so no module invents its own; a conventional type ramp with **body at 16** (12 fine print, 14
  secondary, 16 body, 20 subhead, 24 to 30 headline, line height around 1.4 to 1.5 on body copy and
  tighter on headings); and a **spacing scale in multiples of 8** (8, 16, 24, 32, 40, 48), with one
  section padding chosen off that scale and used library-wide. From the source take the palette, the
  typefaces, the logo, the copy, and the module structure and its order: nothing else.
  **Record in the foundations report that the geometry is ours**, in those words, because otherwise
  somebody downstream compares a module to the source, reads the difference as a defect, and
  "fixes" the library back toward the guesses this tier exists to discard.

Everything below that reads a source number, the ramp in step 3 and the spacing scale in step 5
above all, is an AUTHORITATIVE and PARTIAL instruction. On a REFERENCE ONLY source it is the
defaults above that get built, and the source's numbers stay in the audit as evidence.

**Foundations also SETS the content width, once, for the whole library, and records it.** This is
the same shape as the scale factor rule above, so treat it the same way: one number, decided here,
applied by every later batch, never re-derived per module. Content width is the width text
actually occupies inside a module (the body width minus the side margins), and it decides where a
reader's eye finds the left edge of every line in every email built from this library. On an
AUTHORITATIVE or PARTIAL source, take the audit's derived content margin and content width from its
**Brand foundations** section as the starting value, decide the number, and state it in the
foundations report and on Getting Started. **On a REFERENCE ONLY source the number is 560 on a 600
body**, straight off the defaults, with no derivation from a source margin: a margin nobody chose
carries no information, and converting a percentage of an arbitrary canvas width is how a library
ends up with 20px margins that came out of arithmetic rather than out of a decision.
With a 600 body and a 560 content width, every text-bearing section carries 20/20 padding.
Full-bleed image bands at the body width are the only exception. You may overrule a derived value,
but say so and say why, exactly as you would for a type size.

Why this needs saying: the design-converter worker in Phase 3 returns a section padding per
screenshot, it sees one module at a time, and it has no knowledge of the module's siblings, so its
side margin is a per-module guess BY CONSTRUCTION. Accepting it per module does not risk drift, it
guarantees it. Measured on one assembled email: side margins of 48, 40, and 20 across six modules,
which is three content widths in one email and a text left edge that moves as the reader scrolls,
with every individual padding value looking perfectly reasonable on its own. Render spec section
0.3.1 has the measured table and the failure signature. Foundations fixing one number is half the
remedy; Phase 3 applying that number instead of the worker's is the other half.

**And run the width-versus-type factor check, once, here, on an AUTHORITATIVE or PARTIAL source.**
Divide the source width by the target
email width and compare that ratio to the scale factor you are building at. If they differ by more
than a couple of percent, the library carries two factors whatever the audit recommended, so say so
in the foundations report and name which one governs which quantities: type factor for type sizes,
line heights, and the spacing scale, target width for the body width and everything measured
across it (content width, column splits, image widths). Measured case: a 1092 wide source built to
600 is 1.82 across the width while the confirmed type factor was 2.2, and nobody wrote that down,
so the content-width decision had no traceable derivation. This is a tension to declare, not a bug
to fix (render spec 0.6, audit Step 4).

**On a REFERENCE ONLY source this check does not run**, and the reason is worth stating rather than
leaving as an omission: the tension it exists to declare is between two ways of preserving a source
proportion, and this tier preserves none. There is one factor to disagree with nothing, which is no
factor. Record in the report that you skipped it because the geometry is built to standards. Do not
compute the ratios anyway as background: the measured failure this whole branch exists to prevent
began with two derivations on a file where neither belonged, and ended as a 16px body inside 20px
margins that nobody had chosen.

Build the scaffold every later batch depends on:

1. **Pages: a FIXED frame plus a dynamic middle.** The page structure is PRESCRIBED, not derived
   from what the audit happened to find. Two customers' libraries have to be navigable by the
   same person without relearning the file, so the scaffolding pages are always present, always
   spelled exactly as written here, and always in this order. Only the component category pages
   vary.

   ```
   Cover
   Getting Started
   --- Foundations
   Foundations
   Type
   Buttons
   --- Components
   <one page per category from the audit's Module inventory, in the inventory's own order>
   --- Templates
   Campaigns
   ```

   **The scaffolding pages are not optional and not reorderable.** Do not drop the Cover because
   the file is small, do not merge Foundations into Type, do not sort the category pages
   alphabetically or by how many modules they hold, and do not move Campaigns up because it is
   the page you were working on. An agent deciding the shape per run is the defect this
   prescription removes: the page list stops being a matter of judgment.

   **The three `---` pages are dividers, not content.** Figma has no page folders, so a page
   named `--- Foundations` acts as a visual separator in the page list. Leave them empty. Name
   them with three hyphens, one space, then the word, exactly as written. **A divider sits BEFORE
   the group it introduces**, which is the order that reads correctly in the page list:
   `--- Foundations` then the foundations pages, `--- Components` then the category pages,
   `--- Templates` then Campaigns.

   **The middle is the only dynamic part.** One page per category the audit's Module inventory
   uses (Heroes, Single Column, Lists, and so on), in the order the inventory presents them, and
   no page for a category the inventory does not use. Do not invent a category here: the audit
   already chose them from the sections the customer's plugin has, and it ordered them
   deliberately.

   **One category collides with a scaffolding page, and there is exactly one right answer:
   Buttons.** `Buttons` is both a foundations page in the canonical order above and one of the
   categories the audit can use, so an inventory that carries button modules would otherwise
   produce two pages with the same name. It does not: the middle SKIPS the Buttons category, and
   any Buttons-category module goes on the existing Buttons page, below the button styles. The
   page list stays exactly the canonical list. No other category collides.

   Create the pages in one pass in this order so the list comes out right without reordering.
   **A file you just created still has Figma's default page: RENAME it to `Cover` rather than
   creating a Cover beside it**, or the finished list carries a stray `Page 1` and fails the
   checklist below. If the target file already had pages before you arrived, move them into
   position rather than appending, and delete nothing you did not create.

   **Each scaffolding page has a CONTRACT.** Layout and polish are yours; the listed content is
   not. Two runs of this skill on two customers must produce the same page doing the same job.

   - **Cover.** The first thing anyone opening the file sees, and it answers "what is this and
     what width is it" without anyone having to ask. Required: the customer's brand name set
     large; "Email Love Design System" beneath it; and a single metadata line carrying three
     facts, the design system's own version (`v1.0` on a first build, never this skill's version
     number), the email width the system is built at, and the month and year
     (for example `v1.0 · 600px · July 2026`). **The width is required because it is the single
     most useful fact about an email design system:** it decides whether a module dropped in from
     anywhere else fits. Put the content on a full-bleed frame whose fill is bound to
     `color/bg/brand`, so the cover is on brand color and moves when the brand color moves. No
     module lives on this page.
   - **Getting Started.** How to use the library, in prose a designer or marketer new to the file
     can follow. Required, one short block each: that modules are wrapper components and are used
     by INSTANCING them, never by copying or detaching; that text and images are edited through
     the component properties on an instance rather than by editing inside it; that color, type,
     and spacing come from the tokens on Foundations and Type rather than from hand-typed values;
     and where to look when something does not export as expected (confirm the block is still an
     instance and not detached, confirm the copy was changed through its property rather than in
     place, then hello@emaillove.com). Name the email width, the content width, and the scale
     factor here too, so the page stands alone. **On a REFERENCE ONLY source there is no factor to
     name, so say instead, in one sentence, that the geometry is built to email standards and the
     brand is what came from the source file.** That sentence is what stops somebody opening this
     file in six months, comparing a module to the old one, and correcting the library back toward
     it. **The content width is required here** because it
     is the number every later module is measured against and the one a module dropped in from
     elsewhere will get wrong: state it as the number plus the side margin it implies (for example
     `560px content width, 20px side margins on a 600px body`), and say that full-bleed image bands
     at the full body width are the only exception.
   - **Foundations.** The token sheet. Required: a swatch per color, each labeled with BOTH its
     hex and its variable name, with primitives and semantic aliases in two clearly separated
     groups so a reader can see which name to reach for; the spacing scale rendered as visible
     bars or frames, each labeled with its token name and its pixel value; and the radius token
     with its value. A hex on this page that no variable carries is a defect: the point of the
     page is that everything on it is bindable.
   - **Type.** A SPECIMEN sheet, not a list of style names. Per style in the ramp, three things:
     the style name, a line of sample text actually set in that style, and a caption stating
     family, weight, and size (for example `Inter, Bold, 30px`). Order the rows largest to
     smallest so the ramp reads as a ramp. **This page is how a human catches a broken ramp by
     eye.** A specimen sheet makes a style that has drifted off the single scale factor visible
     as a step the wrong size next to its neighbors, which is the same defect the ratio check in
     step 3 catches arithmetically, and which presents downstream as a padding bug rather than a
     type bug (the single-factor rule: step 3 here, render spec section 0.6). Run both checks
     every time: the arithmetic catches what the eye misses on a long ramp, and the eye catches
     what a passing ratio hides in the middle of one. On a REFERENCE ONLY source there is no ratio
     check to pair it with, so the page carries the whole load: look at the specimen sheet and
     confirm the standard ramp reads as a ramp.
   - **Buttons.** One component per button style the audit listed, built as step 4 specifies, each
     visibly labeled with its name, each with its fill bound to the semantic token that style
     actually uses. Where the inventory has a Buttons category, its modules land here too, below
     the styles and visibly separated from them. Nothing else on the page: no loose instances, no
     scratch work.
   - **Campaigns.** The one root EMAIL TEMPLATE frame, built as step 7 specifies. It is the only
     `mainFrame` in the file and it is an email, not a module. Empty until batch 1 drops modules
     into it.
2. **Variables: two tiers, and component fills BIND to them.** Build real Figma variables, not a
   page of hex values a reader has to retype. One collection named `Email Love Tokens`, one mode,
   two tiers inside it:

   - **Primitives, named by value:** `black/1000`, `navy/900`, `blue/500`, `cream/100`. The
     family plus a numeric weight, taken from the audit's palette. A primitive's name says what
     the color IS and never where it is used, so nothing about it goes stale when a usage
     changes. COLOR variable values take `{ r, g, b, a }` with alpha, on a 0 to 1 scale, while
     the paint you bind them to takes `{ r, g, b }` without it: the two are easy to cross and the
     error is silent.
   - **Semantic aliases, named by role, each pointing at a primitive:** `color/bg/page`,
     `color/bg/content`, `color/bg/brand`, `color/bg/subtle`, `color/text/primary`,
     `color/text/inverse`, `color/text/accent`. A semantic carries no color of its own; its
     value is an alias:
     `semantic.setValueForMode(modeId, { type: 'VARIABLE_ALIAS', id: primitive.id })`.
   - **A numeric spacing scale** as FLOAT variables under `spacing/`: `spacing/xs`, `spacing/sm`,
     `spacing/md`, `spacing/lg`, `spacing/xl`, `spacing/2xl`. The NAMES are prescribed; the
     default values are 4, 8, 16, 24, 32, 48. Where the audit carried the customer's own spacing
     scale, its values win and keep these names. **Do not round the audit's values onto the
     default ladder** to make them look tidier: that is step 5's rule, and rounding a customer's
     14 up to 16 is a second scale factor wearing a friendly number. **That rule is about a source
     whose spacing was chosen, so it binds on an AUTHORITATIVE or PARTIAL source only.** On a
     REFERENCE ONLY source the values are the multiples of 8 from the top of this phase (8, 16, 24,
     32, 40, 48) and no source spacing is carried across at all.
   - **A radius token for the pill,** `radius/pill`, FLOAT, at the radius the customer's button
     styles actually use.
   - **Set `scopes` explicitly on every variable.** The default `ALL_SCOPES` puts every token in
     every picker, which makes the collection useless at the moment it becomes large. Background
     colors get `['FRAME_FILL', 'SHAPE_FILL']`, text colors `['TEXT_FILL']`, spacing `['GAP']`
     plus whichever padding scopes you actually use, radius `['CORNER_RADIUS']`.
   - **Component fills bind to the SEMANTIC variables, never to a primitive and never to raw
     hex.** `setBoundVariableForPaint` returns a NEW paint, so capture it:
     `node.fills = [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', semanticVar)]`.
     Spacing binds with `node.setBoundVariable('paddingTop', spacingVar)` and its siblings;
     radius binds per corner (`topLeftRadius` and the other three), never through `cornerRadius`.
     `fontSize` and `lineHeight` are NOT bindable, so type sizes stay literal on the text node and
     the ramp is governed by the text styles from step 3 instead.
   - **What this buys: changing a brand color becomes one edit.** Repoint `color/bg/brand`'s
     alias at a different primitive and every module using it moves together. Leave forty
     components carrying hex and it is forty edits, plus a reviewer counting them to be sure.
   - **Variables are a Figma-side convenience and must not change what exports.** The plugin's
     exporter reads RESOLVED fills: it takes `node.fills[0].color` and hexes it, and it never
     reads `boundVariables` at all. A bound paint still carries the resolved RGB in `color`, so
     binding is invisible to the export, and that is exactly the property that makes this safe to
     do. Two consequences follow. Set each primitive to the hex the audit gave, so resolved
     equals intended. And the email template root's theme keys are shared plugin data STRINGS,
     not fills (step 7), so they cannot be bound at all: they carry literal hex, and repointing a
     semantic token means updating the matching theme key by hand.
3. **Type mapping.** Recreate the type ramp as Figma text styles in the target file using the
   customer's email-safe fallback choices from the audit (never the unlicensed brand font unless
   the user confirms web-font hosting). Name styles as the customer named theirs. **The typefaces
   come from the source on every tier. Where the SIZES come from is the tier's answer.**

   **REFERENCE ONLY: build the conventional ramp, and do not divide anything.** 12 fine print, 14
   secondary, 16 body, 20 subhead, 24 to 30 headline, line height 1.4 to 1.5 on body copy and
   tighter on headings. These are the defaults from the top of this phase, stated rather than
   derived, and the source's authored sizes play no part in them: a ramp that was eyeballed style by
   style is not a ramp, so there is nothing in it to scale down. Keep the customer's style names
   where they map onto that ramp so the file still reads as their library, and where their ramp had
   more steps than this one, collapse rather than invent: two headline sizes 2px apart in a source
   nobody built to a scale are one headline. **The ratio check below does not apply on this tier**,
   because it exists to prove a single factor was applied uniformly and there is no factor here.
   What replaces it is a read-back: confirm the built ramp is the ramp above, body at 16, each step
   present once.

   **AUTHORITATIVE or PARTIAL: build the ramp from the audit's table VERBATIM.** Take the Email size
   column of the audit's Brand
   foundations table exactly as written: every value in it is already the authored size divided
   by the one confirmed factor. Do not re-derive it, do not re-round it, and above all do not
   map a style toward a size that looks like a number email usually uses. A 65 the table says
   is 30 is 30; a 55 the table says is 25 is 25, even though 30 and 24 are the sizes you have
   seen in a hundred other emails. Mapping style by style toward pleasant numbers is exactly
   how a per-style factor gets back in after the audit removed it, and it is the defect this
   instruction exists to prevent. Render spec section 0.6 carries the measured case: a module
   that came out with 1.83 on its headline and 2.19 on its body, from a ramp built one round
   number at a time, and it read as a padding bug. On a PARTIAL source, a size the audit could not
   prove was deliberate gets standardised onto the conventional ramp above instead, and that
   substitution is one line in the report.

   **Then run the ratio check, before anything gets built on top of these styles**, on those two
   tiers. Divide the
   largest size in the ramp you just built by the smallest, divide the largest authored source
   size by the smallest, and compare the two. More than a couple of percent apart means a style
   has drifted off the factor: find it, fix it, check again. If a size still looks wrong once
   the ramp passes, that is evidence against the FACTOR, so take it back to the audit and the
   designer and move the whole ramp together. Never adjust the one style and leave the rest of
   the ramp where it was.
4. **Buttons page.** Rebuild each of their button styles as a component: correct email
   construction (a styled frame with a single text node), not their app-style nested
   instances. These become the sub-components nested inside mj-button-Frames, and they are
   the INSTANCE_SWAP targets for module-level "Button Style" properties later. Put the
   label's TEXT property on the button component itself: a label living inside a nested
   instance cannot be bound from the module that uses it (render spec, section 8.5).
5. **Spacing.** On an AUTHORITATIVE or PARTIAL source, recreate their spacer scale as components if
   they had one, at the email-scale
   values from the audit, taken verbatim like the type ramp: the same one factor, whole-pixel
   rounding only, never rounded onto a friendlier multiple of 8 because it reads better. Run the
   ratio check across the ends of the scale the same way. **On a REFERENCE ONLY source the scale is
   multiples of 8**, 8, 16, 24, 32, 40, 48, and here rounding onto a multiple of 8 is not a second
   factor sneaking in, it IS the specification: pick one section padding off that scale and use it
   library-wide rather than a different value per module. There is no ratio check, because there is
   no scale in the source to preserve the shape of.
6. **Assets.** Export the logo and any recurring imagery from the source file
   (download_assets) and upload into the target file (upload_assets). Logos become images,
   never vectors. Export the RENDERED node every time, never the raw image fill behind it: a
   source fill with `scaleMode: 'CROP'` loses its crop the moment you take the underlying
   asset, and you get the whole photograph instead of the picture the designer composed
   (render spec 4.2.1, which also has the aspect-ratio rule).
7. **Root EMAIL TEMPLATE frame** on Campaigns at the audit's target email width (600 or 640,
   never the source canvas width when the source was not at email scale; 600 on a REFERENCE ONLY
   source unless the customer's ESP or brand asks for 640): vertical
   auto-layout, width FIXED at that email width, height Hug, the shared marker, and the theme
   colors from the audit's proposal:
   `setSharedPluginData('emaillove', 'nodeType', 'mainFrame')` plus backgroundColor,
   contentColor, textColor, linkColor, buttonTextColor, buttonContentColor,
   lightThemeBackgroundColor, and fallBackFontName (section 2.1 of the render spec has all
   nine keys and what each one is for). Empty theme keys are not neutral: the exporter
   substitutes dark defaults.
   **This is the only `mainFrame` foundations produces, and it is an email, not a module.**
   It exists so batch 1 has somewhere to drop modules and see them in context. The modules
   themselves are a different shape entirely (Phase 3, and section 2 of the render spec):
   each one is an `mj-wrapper` COMPONENT with **no** `mainFrame` marker and no theme keys.
   Do not copy this frame as a starting point for a module.
8. **Report** what was built, **the source fidelity tier you built under and one clause of why**,
   the target email width, and the content width you built
   at, the completion checklist result below, what the
   audit proposed that you changed, and
   what needs the designer's eye before batch 1 (theme colors especially: they are a proposal
   until a human confirms). Then the tier's own numbers:

   - **AUTHORITATIVE or PARTIAL:** the scale factor, the width-versus-type factor check with both
     ratios and which factor governs which quantities, and the ratio check result with the two
     ratios you compared. If you changed a type size or a spacer away from the audit's table,
     that is not a foundations detail, it is a change to the factor: say so explicitly and say
     who agreed to it. On PARTIAL, list every value you standardised, one line each.
   - **REFERENCE ONLY:** that there is no scale factor and why not, the email standards you built
     to (600 body, 560 content width, the ramp with body at 16, the spacing scale in multiples of
     8), and what came from the source, which is the palette, the typefaces, the logo, the copy,
     and the module structure. **Then the sentence that has to survive this document: the geometry
     is ours, by decision, and a module whose margins do not match the source file is correct.**
     Without it the next person to open both files reads the difference as a bug.

### Phase 2 completion checklist

**Run every line of this before reporting foundations done**, and put the result in the report.
Each line is a read-back off the file, not a recollection of having built it: an agent that
remembers creating the Cover and an agent that read its metadata line back are not in the same
position. Report the checklist as passed only when it passed in full; a partial pass is an open
item, named.

Pages, in canonical order:

- [ ] The page list reads exactly Cover, Getting Started, `--- Foundations`, Foundations, Type,
      Buttons, `--- Components`, the category pages, `--- Templates`, Campaigns. Read the names
      off `figma.root.children` and compare them in sequence, including the three hyphens and the
      single space in each divider name. Nothing else is in the list: no second `Buttons`, and no
      `Page 1` left over from creating the file.
- [ ] The category pages are exactly the categories the audit's Module inventory uses, in the
      inventory's order, with none added, none missing, and none renamed, except Buttons, which
      has its page in the Foundations group instead.
- [ ] The three divider pages are empty.
- [ ] **Cover:** brand name set large, "Email Love Design System" beneath it, and one metadata
      line stating version, email width, and month and year. The width printed there matches the
      width the root frame was actually built at. Its frame fill is bound to `color/bg/brand`.
- [ ] **Getting Started:** instancing rather than copying, editing through component properties,
      styling from the tokens, and the "does not export as expected" path are all four present,
      plus the email width, the content width with its side margin, and the scale factor, or, on a
      REFERENCE ONLY source, the sentence that the geometry is built to email standards and the
      brand came from the source.
- [ ] **Foundations:** every swatch labeled with hex AND variable name, primitives and semantics
      visibly separated, the spacing scale rendered and labeled with token names and values, the
      radius token present. No hex anywhere on the page that no variable carries.
- [ ] **Type:** one specimen row per style, each with the style name, a sample line actually set
      in that style, and a caption naming family, weight, and size, ordered largest to smallest.
      Then look at it: does the ramp step evenly? A step that reads wrong beside its neighbors is
      a factor problem, not a style problem, on a source built through a factor, and a mis-built
      standard ramp on one that was not (step 3).
- [ ] **Buttons:** one component per audit button style, each labeled, each a styled frame with a
      single text node, the label's TEXT property on the component itself, no loose instances left
      on the page.
- [ ] **Campaigns:** exactly one root frame, `nodeType = 'mainFrame'`, at the target email width,
      with all eight theme keys set (the nine of step 7 less the `nodeType` marker itself) and not
      one of them empty.

Variables and bindings:

- [ ] The collection exists with both tiers: primitives named by value, semantics named by role.
- [ ] Every semantic's value reads back as a `VARIABLE_ALIAS` pointing at a primitive, not as a
      color of its own. Read the value and check its `type`, do not infer it from the swatch.
- [ ] The spacing scale exists as FLOAT variables under `spacing/`, and `radius/pill` exists.
- [ ] `scopes` is set explicitly on every variable, and nothing is left on `ALL_SCOPES`.
- [ ] Every fill on every foundations component resolves through a semantic variable: walk the
      button components and the Cover frame and confirm each fill carries a bound variable rather
      than a hand-typed color.
- [ ] Binding changed nothing about export: read `fills[0].color` back off a bound node and
      confirm it hexes to the value the audit gave for that token.
- [ ] The root frame's theme keys carry literal hex matching the semantics they mirror, because
      plugin data cannot be bound.

Scale, checked last because it invalidates everything above it. **The first line decides which of
the next two you run:**

- [ ] The source fidelity tier is stated in the report, with the signals behind it, and it is the
      tier the audit gave or the one a named person overruled it with.
- [ ] **AUTHORITATIVE or PARTIAL only:** the ratio check passed, with both ratios recorded (step 3),
      and every number on every page is at email scale, meaning the root frame is 600 or 640, the
      type sizes are the audit's Email size column verbatim, and the spacing values are the audit's.
      On PARTIAL, every standardised value is listed in the report.
- [ ] **REFERENCE ONLY only:** no scale factor appears anywhere in the report, the pages, or the
      built values. The root frame is 600, the ramp reads 12/14/16/20/24 to 30 with body at 16, the
      spacing scale is multiples of 8, the content width is 560, and the report says in words that
      the geometry is ours. A factor that has crept back in as a caption or an aside is a failure of
      this line, because the next reader applies whatever number is on the page.
- [ ] **The library's ONE content width is decided and recorded**: in the report and on Getting
      Started, as a number plus the side margin it implies. Every text-bearing module in every
      later batch is measured against this, so an unrecorded content width means batch 1 inherits
      the worker's per-module guess and the drift in render spec 0.3.1 starts on the first module.
- [ ] The width-versus-type factor check is in the report: source width divided by target email
      width, compared to the scale factor, with which factor governs which quantities stated in
      words when the two differ (render spec 0.6). **On a REFERENCE ONLY source this line is
      satisfied by recording that the check was skipped and why**, not by running it.

## Phase 3: Module conversion (run per batch)

**Phase 3 builds MODULES, not emails.** A module is one reusable block that gets dropped into
many emails, so its shape is a **`mj-wrapper` COMPONENT**: the wrapper IS the component, it
carries shared `name = 'mj-wrapper'`, its layer name is the module name, and it carries **no
`nodeType = 'mainFrame'` marker anywhere in its tree**. The marker is not a harmless extra: the
upload does not stop you, it archives the block as a whole email and emits no component JSON.
An email template is the other shape (a `mainFrame` root with wrapper components stacked
inside), and foundations built one of those in Phase 2 for context. Do not build a module as a
small email.

Section 2 of `references/render-spec.md` has both shapes side by side and the plugin evidence.
Read it before the first module of a batch.

**One module per row of the audit's Module inventory.** The batch is a group of those rows, and
each row already tells you the module's name (use it verbatim as the component name), its
category, the designs it appears in, its source ref, its verdict, its concession if any, its
build constraints, and its effort. Where a module appears in several designs, the source ref
names the one appearance to convert from, so convert it ONCE from there and note that design; the
other appearances are the same component placed again, not more work. When a row has no source
ref, pick the cleanest appearance yourself and record which one in the batch report, so a
reviewer can tell your boundary from the audit's.

**Where this phase's numbers come from is the fidelity tier's answer, and foundations already
settled it.** On an AUTHORITATIVE or PARTIAL source, build every type size, line height, and spacing
value at the audit's scale factor, dividing source pixels by it as you go, while every width comes
from the target email width and foundations' content width instead (Phase 2 has the rule; render spec
section 0.6 has it at the geometry level). **On a REFERENCE ONLY source you scale NOTHING.** Build at the standards foundations
recorded: the 600 body, the 560 content width, the ramp and the spacing scale that are already text
styles and variables in the target file. Do not measure the source region and divide it by anything,
do not reach for a factor because a module looks small beside the source, and do not reintroduce one
per module. The source screenshot in step 1 is there to tell you which blocks exist, in what order,
with what copy and what imagery: it is a content and structure reference, not a ruler. A module
whose margins do not match the source is correct on this tier, and the batch report says so.

**Build every module at foundations' CONTENT WIDTH; do not take the worker's.** This is the same
discipline as the scale factor, one number decided once and applied everywhere, and it is the one
padding in the worker JSON that is not authoritative. The worker sees one screenshot at a time with
no knowledge of the module's siblings, so its side margin is a per-module guess by construction: a
run that accepted it produced side margins of 48, 40, and 20 across six modules of one email, three
content widths, and a text left edge that moved as the reader scrolled, with every individual
padding value looking reasonable on its own. So transcribe the worker's paddings, then set the
horizontal section padding to whatever foundations' content width requires (a 560 content width on
a 600 body means 20/20), and re-derive any multi-column split so the columns plus gutters still sum
to that content width. Full-bleed image bands stay at the body width and are the only exception.
Render spec 0.3.1 is the rule and carries the measured case; list in the batch report every module
whose worker padding you overrode to reach the library number.

Before building any module whose inventory row carries a concession, check the audit's Flags for
a human "yes" on it. If there is none, ask, and record the answer in the batch report. Building
first and asking later means rebuilding. For `image bleed rebuilt as a two column row` that yes is
a confirmation of Email Love's standard remedy rather than an open design question, so ask it as
one, briefly; it still needs answering, and silence is not a yes.

**A row's build constraints are instructions, not context.** Read them before the first node of
that module and state in the batch report how each one was satisfied. They exist because a
correct audit finding was once left in Flags alone and the conversion built straight past it. An
older audit may have no build-constraints column, so on those read Flags in full before the batch
starts, and treat anything phrased as "export rendered nodes, not raw fills", "re-crop", or
"clipped by z-order" as binding (render spec 4.2.1).

For each module in the batch, in order:

### 1. Convert the source design to MJML JSON via the design-converter worker

Do not rebuild by eye and do not run the plugin's Convert button for migration batches. The
pipeline is: screenshot the source module (read-only), POST it to the design-converter
worker, transcribe the returned MJML JSON into the target file, then verify.

1. **Screenshot the module** from the customer's file (read-only; `get_screenshot` or an
   export). The row's source ref says what to shoot: on an email-native source that is a named
   frame or node; on an unstructured source it is the region of a design the source ref bounds,
   cropped at the boundaries the audit set rather than at ones you decide now. Keep the PNG; it
   is also your visual reference for verification.
   **Size the export so the PNG comes back at the target email width.** Where a factor exists that
   means exporting a source at scale factor 2.2 at roughly 0.45x; where none does, divide the source
   region's own width by the target width and export at that, which is a framing decision about one
   PNG rather than a scale factor entering the build. Do that because it is the input the worker was
   tuned for, NOT because the numbers come back at the scale you sent. The worker is
   scale-agnostic: it classifies at a canonical email scale and returns a 600 wide `mj-body`
   with round email values whatever the input resolution (render spec section 0.6, measured on
   a 768px PNG sent for a 600px target). So do not plan on dividing its output by the factor,
   which is usually a no-op and invites a second factor into the build. Sanity check ONE number
   instead, the root `mj-body` width against the width you are building to, and only if that
   disagrees is the payload at another scale and every number in it in need of dividing. The
   factor's real job in this phase is reading the SOURCE and sizing images taken out of it.
2. **POST to the worker** at `https://design-converter.andy-30d.workers.dev`:
   - Headers: `Content-Type: application/json`, `Authorization: Bearer` with an EMPTY
     token, and `X-Auth-Provider: gumroad`. The worker treats empty Bearer + gumroad as
     an anonymous Free user, which is allowed; no license key is needed for this path.
   - Body: `{ "screenshot": "<raw base64 PNG, no data: prefix>", "screenshotMime":
     "image/png" }`. `layerTree` and `promptInputs` are optional plugin-sandbox extras;
     screenshot alone works and is the normal agent path.
   - Query params, all optional:
     - `nocache=1` skips the cache read (results are cached by screenshot hash), for QA.
     - `recache=1` skips the cache read AND forces a write, overwriting a poisoned cached
       result. Use this when a previous conversion of the same screenshot was bad.
     - `decomposeRasterized=1` asks the worker to OCR flat image-only regions into live
       `mj-text`/`mj-button` elements instead of one `mj-image`. Use for source frames
       that are a single baked screenshot with no live text.
   - The response body is the MJML JSON. Response header `X-Cache` says HIT or MISS;
     `X-Trivial-Response: true` means the result degenerated to a single image and you
     should re-run with `recache=1` (and usually `decomposeRasterized=1`).
3. **Save the MJML JSON to disk per module** so the transcription and later re-verification
   work from a stable input.

Fallback only: users without Figma MCP write access can select frames in the Figma plugin's
AI Import screen and click Convert there; it calls this same worker. The agent path above is
preferred for migration batches because every node it writes is inspectable and repairable.

### 2. Transcribe the MJML JSON into the target file

Follow `references/render-spec.md` exactly: it maps every MJML tag and attribute to the
Figma node, auto-layout, fill, and shared plugin data the plugin's exporter reads back.
**Start at its section 2 and build the MODULE shape**, not the email-template shape.

The worker returns a whole MJML document, so its JSON has an `mjml` / `mj-body` envelope and
one or more wrappers inside. You do not transcribe that envelope. Take the module's wrapper and
make it the component:

```js
const moduleRoot = figma.createComponent()                          // the mj-wrapper itself
moduleRoot.name = 'Hero, text led'                                  // the module name
moduleRoot.setSharedPluginData('emaillove', 'name', 'mj-wrapper')
// and nothing else: no nodeType, no theme colors
```

- **No `mainFrame`, no theme keys, no wrapper-inside-a-wrapper.** If the worker JSON returns
  several wrappers for one source module, that is usually one module per wrapper: convert them
  as separate modules, or, when they genuinely are one block, merge their sections under a
  single wrapper component. Never nest one wrapper inside another to keep them together.
- **The layer name is load bearing here**, unlike everywhere else in the file. It becomes the
  saved component name and its storage path, and there is no rename field in the plugin's save
  dialog, so use the module's Module inventory row name verbatim: the audit chose it to be the
  name in the customer's library, so renaming it here silently forks the two documents.
- **Every node gets two names.** The MJML tag goes in the `name` shared plugin data key;
  the Figma layer name gets the plugin's own friendly display name for that tag ("Row
  (Contains columns that sit side by side)", "Text Block", "Button Text"), so the layers
  panel reads like a plugin-built file rather than a wall of `mj-` strings. The exporter
  never reads the layer name for dispatch, so this is free. The module root is the one
  exception: it is tagged `mj-wrapper` like any wrapper, but its layer name is the module
  name rather than the wrapper display string. Section 6 of the render spec has the full tag
  to display-name table, the precedence rules, and the three ways this goes wrong. Never rely
  on the layer-name fallback.
- **Content leaves are tagged PAIRS, wrapper plus inner node.** `mj-text-Frame` contains a
  text node tagged `mj-text`; `mj-image-Frame` contains the image rectangle tagged
  `mj-image`; `mj-button-Frame` contains a node tagged `mj-button` whose own direct child is
  a TEXT node. Tagging only the wrapper is the single most damaging mistake in a conversion:
  untagged inner content is not skipped, it is flattened into a hosted PNG by the exporter's
  unknown-node path, so buttons silently lose their text and links and image sections can
  export empty. After building each module, verify every leaf pair before moving on.
- **Heights hug, widths are a decision, spacing is padding.** Section 0 of the render spec is
  the whole rule and it is not cosmetic: every frame from the root down hugs vertically, a
  fixed height clips content in Outlook, vertical rhythm comes from auto layout padding (manual
  positioning exports as nothing), a FIXED width is only for load-bearing cases like unequal
  columns and `mj-group` percentage math, and a button sized FILL is what makes it full width on
  mobile. `mj-spacer` is the single node allowed a fixed height. Read section 0 before you
  transcribe, not after.
- **Horizontal section padding comes from foundations' content width, not from the worker.**
  Every other padding in the worker JSON is authoritative and gets transcribed exactly; this one is
  not, because it is the only padding whose correctness depends on modules the worker never saw.
  Set the section's left and right padding so the column resolves to the library content width, and
  leave the outer column's horizontal padding at 0 unless the design needs an inner gutter, because
  the worker often puts the side margin at column level instead and the two add up. Then
  where the row has two or more columns, re-derive the split so the columns plus their gutters still
  sum to it: hold the image column and the gutter, and give the difference to the column that has
  slack, normally the text column. Widening a 520 row to 560 is
  `20 margin + 136 image + 24 gutter + 400 text + 20 margin`, not a new margin invented for this
  module. Full-bleed image bands keep the full body width, and they are the only exception
  (render spec 0.3.1).

**Start from the visual pattern, not the layer name.** Most conversion mistakes come from
rebuilding what a design *looks like* instead of reaching for the primitive that produces it.
This mapping covers almost everything you will meet:

| What the design shows | What to build | Why |
| --- | --- | --- |
| A pill, badge, tag, or chip | `mj-button` | It renders a padded, rounded, background-filled box with centred text and an Outlook VML fallback. A column with a border radius does not survive Outlook. A pill needs no link to be a button. |
| A call-to-action button | `mj-button` | Same primitive; add the `href`. |
| Two things side by side that must not stack on mobile | `mj-group` of `mj-column`s | Columns stack on small screens unless grouped. |
| Headline and copy over a full-bleed image | `mj-hero` | Keeps the text live rather than baking it into a picture. |
| A horizontal rule | `mj-divider` | Never a thin rectangle. |
| Vertical breathing room | `mj-spacer` | Never an empty frame. |
| A row of links | `mj-navbar` with `mj-navbar-link` | |
| Tabular data | `mj-table` with `mj-table-row` | |
| ESP tokens, Handlebars, dynamic cards | `mj-raw` | Passed through verbatim. |
| A photo that overlaps or bleeds past the block it belongs to | a two column row: one `mj-section`, two `mj-column`s, image in one and text in the other (render spec 3.4.1) | Email has no z-order and no absolute positioning, so the overlap cannot be reproduced. The Two Column Swap is the standard substitute, not a judgment call. |
| A composition that genuinely cannot be rebuilt | an untagged frame in a column | Deliberately flattened to a hosted image, still editable in Figma. |

- **Build the pair, do not style the wrapper.** The wrapper carries layout; the inner node
  carries content. An image is an `mj-image-Frame` containing a rectangle whose fill is the
  image, never a frame with an image fill on itself. A divider is an `mj-divider-Frame`
  containing a line, never a frame with a solid fill. Childless wrappers export as empty
  cells. Legacy designs almost always express images and rules as fills on a frame, so this
  is the most common thing you must actively restructure rather than copy.
- **A badge, pill, or icon sitting beside text is an `mj-group`, not a loose frame inside
  `mj-text-Frame`.** A loose frame there flattens to an image and detaches from the text.
  Rebuild it as a group inside the section: `mj-group` containing one `mj-column` that holds
  the badge as an `mj-button` (the table row above: a pill is a button, never a radiused
  column) and another `mj-column` for the adjoining text. Give those columns exact **fixed
  pixel widths** and let the exporter derive the percentages (render spec section 3.3), pin
  those widths with slack rather than at the width Figma hugged to (render spec section 3.3.1:
  a pinned column cannot grow, and the email renders a different font binary than the canvas),
  and remember the group must be a child of the section, not of a column, so a design that nests
  such a row inside a column needs the row lifted to section level. Only fall back to treating
  the region as an editable image when the composition is genuinely inseparable.
- **The worker never emits `mj-group`,** so every side-by-side row that must not stack is
  yours to rebuild. Its whole vocabulary is `mj-wrapper`, `mj-section`, `mj-column`,
  `mj-text`, `mj-image`, `mj-button`, `mj-divider`, `mj-spacer`, and `mj-social` with
  `mj-social-element` children. When it returns a tag the render spec does not map, in
  practice a social icon row, do not invent a node and do not silently drop it: rebuild the
  row from mapped primitives (for social icons, an `mj-group` of one-column `mj-image` pairs,
  each with its own `href`). List every row you rebuilt this way in the module's report line.
- **Every `src` comes back as `"placeholder"`.** Place the real assets you round-tripped in
  foundations; use flat gray fills at the correct dimensions everywhere else and list them.
- **Unpinned colors, radii, and fonts drift** between runs, and unpinned fonts flatten to
  Arial. Correct them against the foundations rather than accepting what came back.
- Map every text node to the type styles from foundations.
- Images: one image fill on each `mj-image` RECTANGLE, from a render of the source node (render
  spec 4.2.1). Its `mj-image-Frame` keeps `fills = []` always; a fill on the frame exports as an
  empty cell.
- Buttons: `mj-button-Frame` wrapping an instance of the foundations button component.
- **Honor the inventory row's verdict.** Verdict A: live text throughout. **Verdict
  `A (concession: ...)`: build it as live text like any other A and apply the named substitute,
  nothing more.** The commonest one has a name and a fixed construction, in the next bullet. Do
  not quietly reproduce the effect the concession gave up, in an image or
  otherwise: that is the concession being un-made without the designer in the room, and it turns
  a module the audit priced as mechanical into a flattened picture. Verdict B regions: place the
  design content as a frame with NO recognized tag name inside a column; the exporter flattens it
  to a hosted image at export while it stays editable. Verdict C modules: live-text structure for
  the copy, one editable-image frame for the rich region. **Verdict D: do not build it.** D means
  the pattern has no email equivalent, so it needs the product decision the audit asked for
  (what replaces it) before anything is worth building; drop it from the batch, say so in the
  batch report, and raise the replacement question at the design review. A D that arrives inside
  a batch is usually a batching mistake rather than a module to attempt. Changing a verdict when
  the nodes contradict the audit is allowed and sometimes right; record it and its reason in the
  batch report.
- **`A (concession: image bleed rebuilt as a two column row)` has one construction: the Two Column
  Swap, render spec 3.4.1.** Read that section before the first node of the module; it is the
  authority and this is the summary. The source design put a photograph so it overlaps or bleeds
  past its band, email has neither z-order nor absolute positioning, and the audit has already
  settled the substitute. **Build one `mj-section` with two `mj-column` children, the image column
  and the text column in the same source order the design implies**, and:
  - Both columns **FIXED**, with their widths summing to the section content box (a 600 wide
    section carrying 20/20 padding takes columns summing to 560), and the exporter derives the
    percentages from those pinned numbers.
  - **Derive the widths in this order:** pin the text column first with the slack from render spec
    3.3.1, give the image column the remainder, size the image last. Worked example from the spec:
    text hugs at 260 and pins to 292, so the image column is 268.
  - The image is a **rendered crop of the source region (4.2.1), never the raw fill**, and it is
    cropped to its column rather than padded to fit (4.2.1's never-pad rule). The `mj-image`
    rectangle takes the image column's content width and the crop's natural aspect for its height:
    a 780 x 660 render at 268 wide is 227 tall.
  - Heights **HUG** throughout, both alignment axes equal on the section and on each column, and
    the gutter is one column's horizontal padding only, never both.
  - **Not an `mj-group`.** A group keeps columns side by side on mobile, which is the opposite of
    what this pattern wants: the stack is the point, and it puts the image above the text.
  - **Mobile order follows source order.** Where the design reads text then image on desktop but
    should read image then text on mobile, set `reverseStack` = `'true'` on the section rather than
    reordering the columns.

  Two things not to do. **Do not attempt the overlap**, in any form, including a background image
  behind a column or a negative padding trick: the concession is that the overlap is gone. And **do
  not fall back to an editable image** for the block or for the text beside it, which is the failure
  this substitute exists to replace and would quietly turn an A into a partial conversion. The
  worker will not hand you this structure either, because the overlap is invisible in the screenshot
  it read, so the swap is always a rebuild you make: record it in the module's report line.
- Text over a single background photo is mj-hero territory, live text, not an image.

### 3. Merge the mobile twin

Diff the source's mobile frame against its desktop sibling and express every intentional
difference as Mobile Styles data on the rebuilt nodes, via shared plugin data:

- Padding: `mobileStylesPaddingTop/Right/Bottom/Left` (inner variants exist as
  `mobileStylesInnerPadding*`).
- Visibility: `mobileStylesHideInMobileDevice` / `mobileStylesHideInDesktopDevice` ("true").
  Desktop-only and mobile-only twins of a region become two nodes, one hidden each way.
- Alignment: `mobileStylesTextAlign` / `mobileStylesAlign`.
- Column stacking on the wrapper when the mobile layout stacks: `stackColumns`.

Ignore differences that are just the 390px frame being narrower; capture only deliberate
changes (padding scale, hidden elements, alignment shifts, reordered stacks). When a
difference cannot be expressed in these keys (different copy, different image crop), note it
in the module's report line for the designer.

### 4. Confirm the component shape, add properties, and pick its category

The module was built as a COMPONENT in step 2, because the `mj-wrapper` IS the component. Do
not create a second component around it, and do not promote a `mainFrame` frame into one.
Confirm before going further, by reading the values back off the root:

- `node.type === 'COMPONENT'`
- `getSharedPluginData('emaillove', 'name') === 'mj-wrapper'`
- `getSharedPluginData('emaillove', 'nodeType') === ''` (empty, on the root and everywhere
  below it)
- the root is a direct child of its category page, and its layer name is the module name

The plugin creates every wrapper as a COMPONENT itself (`UiParser.ts:1519-1522`), so this is
its own shape, not a convention we invented, and component properties are impossible without
it. Section 7 of the render spec has the calls and the four rules that keep a component root
working (keep it a direct page child, never combine roots into a variant set, bind properties
at the level that owns the node, do not write `isStandalone`); section 2.3 has the evidence
for why the `mainFrame` marker must be absent.

**Add component properties for the parts a marketer will change**, per section 8 of the
render spec: TEXT bound to `characters` on the inner text node, BOOLEAN bound to `visible`
on the block wrapper, INSTANCE_SWAP bound to `mainComponent` on a nested instance. There is
no image property type.

Derive them from evidence in the source library rather than adding them everywhere: a
BOOLEAN needs a sibling design where that region is genuinely absent; a TEXT needs evidence
the copy changes between sends; boilerplate stays unbound. Two to five per module is the
working range, and zero is a legitimate answer for a fixed block like a logo header.
**A property whose binding is wrong is worse than no property**, so re-read
`componentPropertyReferences` back off each node to confirm the binding landed. Record the
properties you added, and why, in the module's report line.

Then confirm its category for the upload. **The Module inventory row already proposes one**, so
start there and change it only when the rebuilt structure contradicts it, saying so in the batch
report. **Use the customer's real category names**, which are whatever sections already exist in
their plugin, not names you invent. If the Email Love MCP is connected, `list_components` returns
their categories; otherwise read them off the plugin's Assets sidebar, which ships 13 predefined
sections: Pre-Header, Header, Heroes, Single Column,
Two Column, Three Column, Four Column, Buttons, Reviews, Images, Lists, Order Tables, Footer.
Classify by what the component structurally is: **Heroes** for a top-of-email feature block,
**Single Column** for one full-width stack, **Two Column** or **Three Column** for side-by-side
columns, **Order Tables** for line-item layouts, **Images** for image-only blocks. When nothing
fits, choose the closest existing section and note it, rather than inventing one.

**Do not write `saveCategory` or `saveName` plugin data.** The plugin reads neither key. A
module goes into a design system through the Assets sidebar Upload button, and the **Figma
component name** becomes the component name, so the layer name you set in step 2 is the only
thing that carries. Record the category you chose per module in the batch report, so a human
can correct any misfits in one pass rather than hunting for them later.

### 5. Verify per module

Verify against `references/structure.md` (the plugin's ground truth) and the post-build
checklist at the end of `references/render-spec.md`:

- **Shape, first and hardest:** the root is a COMPONENT tagged `mj-wrapper`, its layer name is
  the module name, and `nodeType` is empty on the root **and on every node below it**. Read it
  back; do not assume. A module carrying `mainFrame` uploads as a whole email, and a module
  with a wrapper nested inside another wrapper is an email in disguise. No theme color keys
  unless a designer asked for a dark-mode treatment on that block.
- Structural checklist: the `name` plugin data key resolves to a real tag on every node
  (nothing relying on the layer-name fallback); every leaf is a complete tagged pair; both
  alignment axes match on every auto-layout frame; no detached instances; no unrecognized
  frames except intentional editable-image regions; `mj-column-inner`, if used, is literally
  `children[0]` of its column.
- Sizing: walk the tree and confirm every frame is vertical HUG, the only fixed height is an
  `mj-spacer`, every FIXED width is one of the load-bearing cases, every pinned width that
  carries text has slack (render spec section 3.3.1), and each button's width sizing was
  chosen for its mobile behavior (render spec section 0).
- Concession honored, where the row carried one: on a module built with the Two Column Swap, both
  columns are FIXED and their widths sum to the section content box, the text column's pin has
  slack, the `mj-image` rectangle is at the image column's
  content width with the crop's natural aspect for its height, there is no `mj-group` around the
  pair, and nothing in the block was flattened to an image (render spec 3.4.1). Confirm too that
  the overlap was not reproduced by some other means.
- Scale: the module root is at the audit's target email width, and its type sizes, paddings, and
  image dimensions are at email scale rather than source scale (render spec section 0.6). A
  module built at source scale looks correct in isolation and wrong the moment it sits next to
  another module, so check it before the batch grows. **On a REFERENCE ONLY source, the check is
  that no source measurement reached the module at all:** every type size is one of the ramp's,
  every padding is off the spacing scale, and the text column resolves to the library content width.
  Do not check the module against the source's proportions, because matching them is not the goal
  and a mismatch is not a finding.
- **Content width: read the resolved x and width of the text-bearing column off the built module
  and confirm it equals the library content width from foundations**, not the worker's number. On a
  multi-column row confirm the columns plus gutters sum to it. This is a cross-module check by
  nature, so it cannot be judged from the module in front of you: compare the number against
  foundations, never against how the module looks. A module with the wrong content width passes
  every other line in this list, which is why it reaches a reviewer as a text edge that moves while
  scrolling (render spec 0.3.1).
- Naming: every layer carries the display name for its tag, and no friendly string leaked
  into the plugin data `name` key.
- Component: the module root is a direct child of its category page, not inside a component
  set or a Figma section, with no stray instances of it left loose on the page. Every property
  binding re-read and confirmed.
- Visual: screenshot the rebuild next to the source screenshot from step 1; flag
  divergences rather than silently accepting them. **On a REFERENCE ONLY source, read that
  comparison for content and structure only:** the same blocks, in the same order, with the same
  copy and the same imagery. Margins, type sizes, and spacing are expected to differ, and listing
  them as divergences buries the ones that matter under noise a reviewer will then try to fix.
- Mobile: list the mobile keys you set per node.

### 6. Batch report and gate

One report per batch: per module, keyed by its Module inventory row name, what was rebuilt, the
design you converted it from, verdict honored or changed (with reason), any concession and
whether it was accepted and by whom (and for a bleed concession, the two column widths you landed
on, so a reviewer can check the sum), mobile decisions, divergences flagged, component properties
added and the evidence for each, the category you kept or changed. **Open with the source fidelity
tier, the target email width, and the content width the batch was built at, plus the scale factor
where one applies**, so a reviewer can check three or four numbers instead of measuring modules. On a
REFERENCE ONLY source, open instead with the tier and the standards, and repeat the one sentence that
the geometry is ours: a batch report is the document a reviewer reads with the source file open
beside it, so it is exactly where the difference gets mistaken for a defect. Name every module whose worker side margin you overrode
to reach the content width (plus the re-derived column sum where the module was multi-column). End with the open questions for the design review. Do not start the next batch
until the user says the review happened.

## Hand-off after the final batch

The design system is on the canvas but not yet in the plugin. Walk the user through the
upload: pick the design system in the plugin, open the Assets section the batch belongs to,
select the wrapper components on the canvas, click **Upload**, confirm. A multi-selection of
wrappers uploads as one batch, so an approved batch goes in with one click rather than one
component at a time. **The Upload button only renders for a user on a paid plan**
(`AssetsComponent.tsx` gates that whole header on the subscribed state), so if the person
doing the upload is on Free they will not see the button at all and the hand-off needs a seat
on a paid plan first. Then: sync check in the plugin, build one real sample email from the
new components as proof, export it, and send a test to a real inbox. Building is free;
exports count against plan limits.

## Staying current

This is version 1.19.0 of this skill. If you have web access, check once per conversation
(quietly, without narrating it) whether a newer version exists: fetch
https://api.github.com/repos/email-love/claude-skills/releases/latest and compare the tag. If a
newer version exists, mention it once at hand-off with the right update path for the user's
surface: claude.ai users re-upload the .skill file from that release, Claude Code plugin users
run the marketplace update. If you have no web access, skip this silently.
