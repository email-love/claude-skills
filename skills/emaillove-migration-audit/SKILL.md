---
name: emaillove-migration-audit
description: Audit an existing Figma design system or template library for migration to Email Love, producing a read-only migration report with a deduplicated module inventory that classifies every module as live-text convertible, editable-image candidate, hybrid, or not emailable, detects the source's scale factor, and extracts the brand foundations. Use this skill whenever a user wants to know whether their existing Figma templates or design system can work with Email Love, asks to audit or scope a migration, mentions converting an existing design system to the mj-wrapper/MJML structure, is a new or prospective Email Love customer sharing their current design files, or asks "can Email Love work with what we already have". Trigger on "audit", "migration", "convert our templates", or a shared Figma file described as their existing/legacy design system.
---

# Email Love Migration Audit

Audit an existing Figma design system for migration to Email Love, and produce a migration
report the customer and the Email Love team can act on. This is Phase 1 of a migration: it
tells everyone what they have, what converts, what needs design judgment, and how big the job
is. Phase 2 is the conversion, and the report is its input: the emaillove-eds-converter skill
runs it, or Email Love's team runs it for the customer as part of Enterprise onboarding. Step 7
is the hand-off, and it is part of the job, not an afterthought.

**This skill is strictly read-only.** Never create, modify, rename, or delete anything in the
customer's file. Every Figma call you make must be an inspection. If the user asks you to start
converting, that is Phase 2: it happens in a separate target file through the
emaillove-eds-converter skill (Step 7 has the hand-off), and the source file stays read-only in
that phase too.

## How long this takes

**The audit is the quick part.** It is read-only and creates nothing, so it runs in minutes,
scaling with the size of the library rather than its complexity: a walk of the pages, the
styles, and each candidate design. Tell the user that up front.

Conversion is where the time goes, and the report should not leave anyone surprised by it. A
first batch of about five modules takes tens of minutes, and materially longer on an
unstructured source (groups, absolute positioning, a scaled-up mockup) than on an email-native
one (frames already at 600 or 640, with auto layout in place), because the agent has to work out
where each module begins and ends before it can rebuild anything. A library of a hundred or more
modules runs across multiple sessions, which is why conversion is batched with a design review
between batches. The time is dominated by round trips to Figma, one per node created or read,
not by AI: the automated conversion of a design takes seconds. These are ranges from past runs,
not guarantees, so keep the Step 6 effort estimate framed as a range too.

## Step 1: Scope the input

You need the Figma file link. If several files hold the design system, audit each. Ask only
three questions if not obvious: which frames or pages are the email templates (as opposed to
web or app design); whether there is an existing production email you can use as a reference
for how their emails actually render today; and whether the component masters live in this
file or in a separate Figma library, and if separate, ask for that file too. A missing
library file is the most common blocker an audit surfaces, and knowing up front saves the
report from guessing about components it cannot see.

## Step 2: Survey the file

Build the inventory with read-only calls:

1. **Pages** and what each holds (component libraries, template galleries, guidelines,
   icon sets, font fallback references).
2. **Brand foundations:** local text styles (the type ramp with families, weights, sizes),
   local paint styles (the palette and its naming taxonomy), variable collections, and any
   spacing or padding component sets. Note a fonts-fallback page if one exists; it means the
   team has already chosen email-safe substitutes.
3. **Design census:** every candidate frame, with name, width, height, and component/frame
   type. Group desktop and mobile twins (the same design at two widths, commonly 600 and 390);
   in Email Love these merge into ONE frame with Mobile Styles overrides, so count designs,
   not frames.

Record the authored type sizes and the design widths verbatim, in the numbers the file actually
carries. Step 3 divides both, and it cannot do that from rounded or remembered figures.

## Step 3: Detect the scale factor

Not every source library is drawn at email scale. A file that was never meant to export as
email is often drawn at some multiple of it: a mockup enlarged for presentation, a web-first
canvas, a slide artboard. The factor decides every number in every converted module (widths,
type sizes, paddings, image dimensions), so getting it wrong makes the whole library uniformly
wrong, and nobody notices until a converted module sits next to a real email.

Compute BOTH derivations, always, and put both in the report:

1. **From the canvas width:** the source design width divided by the email width they intend
   (600 or 640). A 1089px design against 600 gives 1.815. If nobody has named a target width,
   derive against 600, Email Love's default, and say in the report that you assumed it.
2. **From the type ramp:** the authored type sizes divided by the standard email sizes they map
   onto. Divide the whole ramp, not one style, and look for a cluster: a 35px body over a 16px
   email body gives 2.19, a 26px caption over 12 gives 2.17, a 53px headline over 24 gives
   2.21. Three styles landing near 2.2 is a signal; one style is a coincidence. Sanity check
   the candidate by dividing the ramp back by it: if 2.2 turns the authored sizes into 16, 12,
   and 24, the factor is real.

If the two derivations agree within a few percent, say so, give the one number, and move on:
there is nothing to decide. When they disagree, and on an unstructured source they usually do,
the report carries the disagreement rather than hiding it:

- **State both derivations with their arithmetic and name the gap in percent.** An observed
  migration came out at 1.815 from the width and 2.2 from the type, a 21 percent gap, and 21
  percent is the difference between a converted module a designer accepts and one nobody can
  use.
- **Recommend one, with the reasoning.** Prefer the type ramp when the authored sizes divide
  cleanly into standard email sizes and the width ratio does not. In that observed migration
  the type sizes divided to exactly the standard sizes while the width ratio landed on an
  arbitrary 1.815, so the ramp was the trustworthy signal. The reason generalizes: a designer
  picks type sizes deliberately off a ramp, while a canvas width absorbs bleed, margins, and
  whatever artboard someone happened to start on, so the width carries noise the ramp does not.
- **Mark it a designer decision, in those words.** It is a recommendation until their designer
  confirms it, and because it changes every module it is the highest-leverage line in the
  report.

Two more things while you are in here: check that every design shares one factor (a single
design drawn at a different scale is a flag, not a second factor), and state the email width as
the TARGET width rather than the source canvas width. Conversion divides by the factor; it
never carries source pixels across.

Record the result in the report's **Scale factor** section (Step 6). Phase 2 reads that number
instead of deriving its own, which is the whole point of settling it here.

## Step 4: Split the designs into modules, then classify every module

Email Love design systems are built from modules, not from whole designs. A module is one
reusable block that gets dropped into many emails: a hero, a copy block, a 2-up product row, a
footer. Phase 2 converts modules, one component per module, and batches them, so the audit's job
is to hand it a deduplicated **Module inventory**, which is the name both skills use for this
artifact. A per-design verdict cannot do that job. On an observed migration, six finished emails
turned out to be the same nine modules in a different order each time: the six-row per-design
table said almost nothing, and the nine-row Module inventory said everything.

Three passes:

1. **Split each design into blocks.** Walk the tree (node types, auto-layout, text nodes, image
   fills, vectors, nested instances) and cut at the natural block boundaries: a full-width
   background change, a divider, a jump in vertical padding, a repeated row, a run of copy
   followed by an image. On an email-native source the components and auto-layout frames tell
   you where the cuts are. On an unstructured source (loose groups, absolute positioning, no
   components, no styles) you are inferring them, so say so in the report and ask the designer
   to confirm the split: the Module inventory is what gets built, so a wrong boundary is a wrong
   component. **Then write the boundary down on the row.** Whoever converts the module has to
   screenshot exactly the region you cut, and a boundary you found but did not record is a
   boundary they have to infer again, differently. So record a source ref per module: the design
   to convert from, plus the node name or node id you cut at, and on a source with no node to
   name (a loose group, an absolutely positioned run) the position within that design, for
   instance "top 0 to 480" or "between the divider and the footer rule". One appearance is
   enough; it is the one that gets built.
2. **Deduplicate across designs.** The same block appearing in six designs is ONE module with
   six appearances, never six rows. Near-duplicates are one module plus a note when the
   difference is content, and two modules when the difference is structural (a different column
   count, an added region).
3. **Name each module the way it should appear in their library**, because the name carries
   straight through conversion into the component name ("Hero, text led", "Footer, legal +
   social"). Give each one a category from the sections their plugin already has (Pre-Header,
   Header, Heroes, Single Column, Two Column, Three Column, Four Column, Buttons, Reviews,
   Images, Lists, Order Tables, Footer) rather than one you invent.

Then assign every module exactly one verdict:

- **(A) Live-text convertible.** Auto-layout stacks of text, images, and buttons that map
  onto mj-section/mj-column/element-frame structure. Text stays selectable and editable in
  the sent email. Best deliverability and accessibility; most modules should land here.
- **(B) Editable-image candidate.** Design-rich compositions (layered imagery, text on
  photos, custom shapes, brand illustrations) that would fight email rendering as live text.
  Email Love handles these deliberately: the design frame is placed inside a column without
  an MJML type name, and the exporter flattens it to a single hosted image at export while it
  stays fully editable in Figma. No rebuild needed; the design survives as-is. Cost: the text
  inside is not live in the inbox (image weight, accessibility, clients with images off), so
  recommend pairing with alt text and keeping critical copy outside the image.
- **(C) Hybrid.** Split the module: headline and body as live text, the rich visual region as
  an editable image. Common for heroes.
- **(D) Not emailable.** Interactive patterns (hover states, carousels, video embeds beyond a
  thumbnail link), viewport-relative layouts, or app UI that has no email equivalent. List
  what would replace them.

**The concession field on A: required on every A row, and deliberately not a fifth verdict
letter.** A module can convert perfectly as live text except for one effect email cannot
reproduce at all: a full-bleed treatment that has to stop at the content box, a blur, a blend
mode, a shape email has no way to draw. That is not B (nothing needs to become an image), not C
(there is no rich region to split off), and not D (it emails fine). Two modules on the observed
file were exactly this, and with nowhere to put it the finding got smuggled into a C with a
paragraph of explanation, which is how a decision a designer needed to make ends up buried.

So record it on the verdict instead: write the verdict as **`A (concession: <the named
concession>)`** and spell the concession out in the row's notes, both what is lost and the
nearest email-safe substitute you propose. Every A row states either `none` or a named
concession, so a blank is a missing answer rather than an implied no. Every named concession
also gets its own line in Flags, for the designer to accept or reject before the module is
built. **Why a field and not a letter:** the ladder answers how a module gets built, and these
get built exactly like any other A, same technique and same effort. What differs is a decision a
human has to accept. A fifth letter would fork the ladder, and every per-verdict count and
effort row with it, on something orthogonal to construction. B and C rows may carry a
concession too when one applies; on those the field is optional, because their verdict already
carries an explanation.

**A flag that constrains HOW a module gets built belongs on that module's row.** Flags is a prose
section a human reads once. The Module inventory is what the converter works from, row by row,
and a converting agent that never opens Flags is the normal case rather than a careless one. So
any finding that changes the technique for a specific module has to be written where that module
gets built from: name it in the row's `build constraints` column and spell it out in the row's
notes, and only then also in Flags when a human has to decide about it. Observed failure: an
audit correctly flagged "images are clipped by z-order, not masks, so export rendered nodes
rather than raw fills" in Flags alone. The conversion exported raw fills, every cropped image
came across as the whole uncropped photograph, and the customer reported it as a spacing bug. The
audit was right and the hand-off still failed, which is a defect in where the finding was
written, not in the finding.

Findings that are build constraints rather than observations, and therefore belong on the row:
images that carry a crop transform or are clipped by overlapping siblings (the row says "render
the node, not the fill"), an image that is inset rather than full bleed and the percentage it is
inset by, copy that has to stay outside an image for accessibility, a font this module in
particular leans on, a pinned width this module cannot keep, spacing that has to come from one
side only. Write each one short and imperative: one clause a builder can act on without reading
anything else. A constraint that applies to the whole library belongs in Brand foundations or
Flags instead of being repeated on twenty rows.

Signals that push a module from A toward B or C: vector logos and illustrations (email wants
images), buttons built as nested app-style instances with state layers, stacked image fills,
gradients and blend modes on text, and effects email clients do not render. Signals of A:
clean vertical auto-layout, flat solid fills, one image per region, system-mappable text.

Do not over-classify toward images. Two MJML capabilities keep more modules live-text than
designers expect: **mj-hero** renders live text over a full background image, so "headline on
a photo" is verdict A when the text sits on one background image rather than woven through
layered art; and sections support background images behind live columns. Reserve B for
compositions where text and imagery genuinely interleave (text wrapping around cutouts,
badges over product shots, hand-placed collage).

Finally, **roll the verdicts up per design**: for each design, the ordered list of module names
it is made of and the worst verdict present in it. The Per-design roll-up is a view of the Module
inventory, not a second classification, so it introduces no verdict that is not already on a
module row. It exists so a customer can still ask "what happens to this email" and get an answer,
and Phase 2 does not work from it.

## Step 5: Extract the brand foundations

From the survey, draft what the Email Love design system will carry:

- **Type ramp mapping:** each of their text styles mapped to an email-safe equivalent, using
  their own fallback choices when a fallbacks page exists. Flag fonts that need web-font
  hosting or substitution. When the Step 3 scale factor is not 1, show the arithmetic in three
  columns (authored size, factor, resulting email size) so a reader can audit it instead of
  trusting it.
- **Palette:** their named paint styles, and a proposed set of the six Email Love theme
  colors (backgroundColor, contentColor, textColor, linkColor, buttonTextColor,
  buttonContentColor) drawn from it, marked as a proposal for their designer to confirm.
- **Spacing scale** from any padding/spacer components, stated at email scale (divided by the
  Step 3 factor) rather than at source scale.
- **Buttons:** their button styles as candidates for the Email Love button component page.
- **Target email width:** the width the converted system gets built at (600 or 640), which is
  the source design width divided by the Step 3 factor when the source is not at email scale.
  Label it as the target, and list anything in the file that contradicts it.

## Step 6: Write the migration report

Produce one markdown report, in this exact structure. **Scale factor and Module inventory are
required sections**: they are what Phase 2 consumes, and a report missing either one cannot be
converted from.

# Migration audit: [Design system name]
## Summary
[Three sentences: what they have, how much converts cleanly, the one or two biggest items
needing design judgment. If the source is not at email scale, say so here; it is the finding
that changes the most work.]
## Inventory
[Pages, style counts, component counts, design count (with desktop/mobile pairs merged),
distinct module count, fonts in play.]
## Scale factor
[REQUIRED. Both derivations with their arithmetic, the gap between them in percent, the
recommended factor, the reasoning for choosing it, and "designer decision" in as many words.
State the target email width the factor is measured against. One factor for the library; note
any design that contradicts it. When the two derivations agree, say so and give the single
number.]
## Module inventory
[REQUIRED, deduplicated, and this is the section Phase 2 works from. One row per DISTINCT
module: module name | category | appears in (design names) | source ref | verdict A/B/C/D |
concession | build constraints | effort S/M/L | notes. The name is the name the converted
component will carry. **Source ref is REQUIRED on every row** and names the one appearance to
convert from, precisely enough to screenshot without re-deriving the split (Step 4): a design
name plus a node name or id, or, where there is no node to name, a position within that design
("top 0 to 480", "between the divider and the footer rule"). Every A row states either `none` or
a named concession in the concession column, with what is lost and the proposed substitute in the
notes. **Build constraints is REQUIRED on every row
and states either `none` or the short imperative constraints from Step 4** (for example "render
nodes, not raw fills: images clipped by z-order" or "image is inset 91 percent, not full bleed"),
so that nothing which changes how a module is built exists only in Flags. Order the rows so a
batch plan can be read straight off them: highest reuse first.]
## Per-design roll-up
[One row per design: design name | width(s) | the module names it is made of, in order | worst
verdict present. A roll-up of the Module inventory, not a second classification: no verdict
appears here that is not already on a module row above.]
## Brand foundations
[Type ramp mapping table (authored size, factor, email size), proposed theme colors, spacing
scale at email scale, button styles, target email width.]
## Flags
[Everything a human should look at: fonts unavailable for email, naming typos, empty pages,
inconsistent widths, accessibility risks from image-heavy modules, module boundaries you
inferred rather than read. Plus two that are decisions rather than observations: every named
concession from the Module inventory, for the designer to accept or reject, and the scale-factor
recommendation when the two derivations disagreed. Anything here that constrains how a specific
module gets built must ALSO appear in that module's build constraints column (Step 4): Flags is
where a human decides, the row is where a builder reads, and a build constraint that lives only
here will be missed.]
## Effort estimate
[Per-verdict counts over MODULES, not designs, and an S/M/L per module (the Module inventory
already carries the per-module value; total it here). A modules are mechanical; C modules need a
design pass; D modules need product decisions; a concession costs decision time, not build time.
State the total in designer-days as a range, and say plainly that estimates firm up after the
first converted batch.]
## Recommended next step
[The batch plan, naming modules by their Module inventory row names: foundations first, then
batch 1 of about five of the highest-reuse modules, then the later batches, with a design review
between batches. Then point at Step 7's two routes.]

Numbers in the report come from your actual reads, never estimates presented as counts. Where
you sampled instead of walking everything, say so.

## Step 7: Hand off to conversion

Deliver the report as a file or artifact the user can share internally. Then close the loop,
because an audit that ends without naming what happens next leaves the customer thinking the
migration is somebody's private process. There are two routes, and the report is the input to
both:

1. **Self-serve.** The **emaillove-eds-converter** skill runs Phase 2 from this report:
   foundations once, then modules in batches with a designer review between batches. It builds
   in a NEW target file and keeps this source file read-only. What it reads out of this report,
   by section name: the **Module inventory** (one module per row, one batch per group of rows,
   with the source refs, verdicts, concessions, build constraints, categories, and effort), the
   **Scale factor** (every number it builds is at that scale), the **Brand foundations** (type
   ramp on email-safe fallbacks, proposed theme colors, spacing, buttons, target email width),
   and the **Flags**.
2. **Done for you.** Email Love's team runs the same process, design review included, as part
   of Enterprise onboarding: hello@emaillove.com.

Two things need a human "yes" before either route starts, and both are in Flags: the scale
factor, and each named concession. They change what gets built, so getting them agreed now is
cheaper than re-running a batch. If the audit surfaced a missing component library file, that
blocks conversion outright; say so rather than letting a batch start without it.

Offer to answer questions about any specific module's verdict, and to re-run the audit after
they clean up anything the flags surfaced.

## Staying current

This is version 1.3.0 of this skill. If you have web access, check once per conversation
(quietly, without narrating it) whether a newer version exists: fetch
https://api.github.com/repos/email-love/claude-skills/releases/latest and compare the tag. If a
newer version exists, mention it once at hand-off with the right update path for the user's
surface: claude.ai users re-upload the .skill file from that release, Claude Code plugin users
run the marketplace update. If you have no web access, skip this silently.
