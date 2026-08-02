---
name: emaillove-migration-audit
description: Audit an existing Figma design system or template library for migration to Email Love, producing a read-only migration report with a deduplicated module inventory that classifies every module as live-text convertible, editable-image candidate, hybrid, or not emailable, classifies how much of the source's geometry is a specification worth preserving, detects the source's scale factor when one applies, censuses the source's spacing values into one system per role, censuses every distinct family/size/weight/line-height tuple in the file into one type ramp, and extracts the brand foundations. Use this skill whenever a user wants to know whether their existing Figma templates or design system can work with Email Love, asks to audit or scope a migration, mentions converting an existing design system to the mj-wrapper/MJML structure, is a new or prospective Email Love customer sharing their current design files, or asks "can Email Love work with what we already have". Trigger on "audit", "migration", "convert our templates", or a shared Figma file described as their existing/legacy design system.
---

# Email Love Migration Audit

Audit an existing Figma design system for migration to Email Love, and produce a migration
report the customer and the Email Love team can act on. This is Phase 1 of a migration: it
tells everyone what they have, what converts, what needs design judgment, and how big the job
is. It also settles a question that reframes all of those: whether the source's geometry is a
specification to preserve or only a reference to take brand and structure from. That is Step 3,
and it decides how much of the rest of the audit even applies.
Phase 2 is the conversion, and the report is its input: the emaillove-eds-converter skill
runs it, or Email Love's team runs it for the customer as part of Enterprise onboarding. Step 8
is the hand-off, and it is part of the job, not an afterthought.

**This skill is strictly read-only.** Never create, modify, rename, or delete anything in the
customer's file. Every Figma call you make must be an inspection. If the user asks you to start
converting, that is Phase 2: it happens in a separate target file through the
emaillove-eds-converter skill (Step 8 has the hand-off), and the source file stays read-only in
that phase too.

**If your environment lets you choose a model, use your most capable one here too.** The whole
conversion phase builds on this report's classifications, so a misjudged verdict or a wrong
source fidelity tier compounds into every module built from it. This is also work a customer runs
once per migration, not daily, which is exactly when the extra cost is worth paying.

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
not guarantees, so keep the Step 7 effort estimate framed as a range too.

### Report progress while you walk

The walk is where the silence is. Reading the pages and then every candidate design is one Figma
call after another with nothing appearing on screen, so a library that takes minutes reads as a
hung run. Three lines fix that, and three is the whole contract here: this skill creates nothing,
so it earns far fewer updates than the conversion does.

1. **After the census** (end of Step 2): the counts you found. Pages, candidate frames, designs
   after desktop/mobile twins are merged, text and paint styles. **The design count is the
   denominator for everything after it**, so state it here even when it is obvious. Add the
   **source fidelity tier** you read off those same counts (Step 3) and one clause of why, because
   it decides whether scale detection happens at all and the user should hear that before the
   silence of the walk rather than in the report.
2. **As you walk the designs** (Step 5, pass 1): one line per design. A count, a percentage, the
   design's name, and what it added to the inventory. Say a blocker at the design where you hit
   it rather than saving it for the report: a component library file you cannot see, a split you
   are inferring and need the designer to confirm, a type ramp that contradicts the width
   derivation.
3. **At the end** (Step 7): the shape of the report. Modules by verdict, the scale factor (or, on a
   reference-only source, that there is none and the build uses email standards), and the
   one or two flags that decide the next step.

The format for the walking line, and it is a count and a percentage rather than prose:

> Design 3 of 11 walked, 27 percent: Welcome email, 4 blocks cut, 2 of them new, 9 modules in the
> inventory so far.

**Name the design**, so the user can find it in their own file. **Design boundaries only**, never
per node and never per style: an audit that narrates every text node it reads is worse than one
that stays quiet, and it is the failure mode to avoid here. If the library turns out larger than
it looked and the walk is running well past the minutes you promised up front, say so at the next
design boundary with a revised number rather than letting the user work it out.

### Say when you STOP, too

Those three lines cover a walk that is still walking, and line 2 fires per design, so its absence
reads as the next design being read right now. **An agent that reports progress but not its own stop
is worse than one that does neither, because the user infers continuation from the last progress
line.** Silence is indistinguishable from still working.

So **never stop silently.** If you stop, for any reason, say so in the SAME message as the last of
the work, not in a later reply and not only once the user asks: what you walked, what remains by
design name, why you stopped, and the exact thing needed to resume. The reasons that qualify are a
blocker, a decision only the user can make, a limit you have hit, or reaching the end of a unit of
work. Finishing the audit is that last one, and line 3 plus the Step 8 hand-off are how it gets
announced. There is no batch here, so the only mid-walk stop is a real blocker, and Step 1 names the
usual one: a component library file you cannot see.

**If you saved state, name its path in that message.** On a library big enough to span a session,
writing the partial inventory to a small JSON file as you walk is expected behaviour rather than
extra credit, and it is not a Figma write, so the read-only rule above is untouched. State the user
cannot see does not make the walk resumable, it only makes you feel that it is.

One worked example, the format to copy:

> Stopped, not still walking. 7 of 11 designs walked, 64 percent: 14 modules in the inventory so far.
> Remaining: 4 designs, starting with Winback. Why I stopped: the component masters for the product
> card live in a separate library file I cannot open, and three of those four designs are built almost
> entirely from it, so their verdicts would be guesses rather than findings. To resume, share that
> library file, or say "audit what you can see and flag the rest", and I will pick up from the saved
> inventory at `./audit-state.json`.

## Step 0: Pick your source

Ask the customer where their existing emails live, in one question:

> Where are the emails you want to migrate?
> - (a) A Figma file (design system or template library)
> - (b) A local folder of HTML files or PNG screenshots
> - (c) Klaviyo (via the official Klaviyo MCP)
> - (d) Marketo (via the customer's Marketo REST API credentials)
> - (e) Customer.io (via the CIO MCP)
> - (f) Google Drive folder (via the Google Drive MCP)
> - (g) SharePoint folder (via a Microsoft Graph MCP)
> - (h) Brevo (via the official Brevo MCP)
> - (i) Kit (via the official Kit MCP; formerly ConvertKit)
> - (j) ActiveCampaign (via the official ActiveCampaign MCP)
> - (k) Iterable (via the official Iterable MCP; currently beta)
> - (l) Omnisend (via the official Omnisend MCP)
> - (m) HubSpot (via the official HubSpot MCP)

Their answer decides everything downstream. The rest of the audit uses the source adapter for
whichever they picked. **You cannot skip this question.** An unstated source is the default
silent-failure mode that makes a converter walk a folder as if it were a Figma page, or
inspects a Figma file as if it were a Klaviyo library.

**Recommend Figma when it is on offer.** If the customer has their design system in a Figma
file, that is by far the richest source: components, styles, and variables are structured data,
cross-source deduplication happens for free, and the audit report is fully populated with
verdicts and factor-detection. The other sources work and produce a real Email Love design
system out the other end, but they carry less metadata forward and the audit report is slimmer.
Say this once and honestly, then follow whichever source the customer actually has.

Source adapters:

- **(a) Figma:** the rest of this document as-written. No adapter needed; proceed to Step 1
  below.
- **(b) Local folder:** load the Local Folder Source section at the end of this file, then
  follow its Discover, Fetch, and audit-step adaptations in place of the Figma-specific
  behavior below.
- **(c) Klaviyo:** load the Klaviyo Source section at the end of this file.
- **(d) Marketo:** load the Marketo Source section at the end of this file.
- **(e) Customer.io:** load the Customer.io Source section at the end of this file.
- **(f) Google Drive folder:** load the Google Drive Source section at the end of this file.
- **(g) SharePoint folder:** load the SharePoint Source section at the end of this file.
- **(h) Brevo:** load the Brevo Source section at the end of this file.
- **(i) Kit:** load the Kit Source section at the end of this file.
- **(j) ActiveCampaign:** load the ActiveCampaign Source section at the end of this file.
- **(k) Iterable:** load the Iterable Source section at the end of this file.
- **(l) Omnisend:** load the Omnisend Source section at the end of this file.
- **(m) HubSpot:** load the HubSpot Source section at the end of this file.

## Step 1: Scope the input

For a Figma source, you need the file link. If several files hold the design system, audit
each. Ask only three questions if not obvious: which frames or pages are the email templates
(as opposed to web or app design); whether there is an existing production email you can use
as a reference for how their emails actually render today; and whether the component masters
live in this file or in a separate Figma library, and if separate, ask for that file too. A
missing library file is the most common blocker an audit surfaces, and knowing up front saves
the report from guessing about components it cannot see.

For any other source, follow the scoping instructions in that source's adapter section at the
end of this file.

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
4. **Asset survey, and the distinction that decides everything downstream: absent versus
   fused.** Walk the images the designs actually rely on (image fills, placed assets, logos,
   icon rows, badge rows, rating rows) and note where each one lives. Then separate two findings
   that look identical in a screenshot and have completely different remedies:
   - **Genuinely absent.** The design points at an asset that is not in the file: an image that
     failed to load, a literal placeholder, an icon set the team keeps elsewhere, a vector that
     lives only in the component library you were not given. Nobody can build the module until
     the customer supplies it, so this is a blocker and it is an ask.
   - **Present but fused.** The asset is in the file, combined with others into a single raster.
     A row of social icons carried as one screenshot rectangle is the standard case; payment
     badges, app-store buttons, and star rows do the same thing. Nothing is missing and there is
     nothing to ask anyone for: whoever converts the module renders that strip and slices it
     into the individual images the email needs. Two tells, either one being enough: one image
     node spans a region the design reads as several separate things, and its dimensions are a
     wide, short strip rather than the size of any single item in it.

   Reporting a fused asset as absent is an observed failure and it cost a whole conversion pass:
   the audit concluded that a footer's six social icons "are not in the file", the converter
   built the footer with six empty rectangles, and the icons had been in the file the whole time
   inside one strip image. **So write which of the two it is, in those words, and write it on the
   module's row rather than only in Flags** (Step 5's rule about build constraints): `build
   constraints` reads `slice the fused N-item strip, do not treat as missing` for the fused case
   and `asset absent, blocked on customer` for the absent one. Say how many items are in the
   strip, since that count is what the converter checks its slice against. The verdict does not
   change either way; what changes is whether the module is buildable today, and by whom.

5. **Fidelity signals, which Step 3 classifies from.** You are reading all of these already while
   you do 1 to 4; the only new work is writing each one down as present or absent rather than
   using it and moving on: a standard email width or not, local text styles, local paint styles,
   variable collections, components or component sets (as opposed to loose frames and groups),
   auto layout (as opposed to absolute positioning), mobile variants. Add one measurement the
   census does not otherwise need: **the left content inset of three or four designs.** Whether
   equivalent margins are identical or merely similar is the signal that separates a file somebody
   designed from a file somebody eyeballed, and it is two reads per design.

Record the authored type sizes and the design widths verbatim, in the numbers the file actually
carries. Step 4 divides both when it runs, and it cannot do that from rounded or remembered
figures. Record them even when you expect the source to be reference only, because they are also
the evidence for the Step 3 classification.

## Step 3: Classify the source fidelity

Before deriving anything from the source's geometry, decide whether that geometry is a
specification at all. This comes before scale detection because it decides whether scale
detection is relevant, and it changes how every later section of the report should be read.

Two sources can look equally finished in a screenshot and mean completely different things.

- **A well organised email-native library** is drawn at real email widths, with a desktop and a
  mobile variant, real text styles, real components, variables, and margins that repeat because
  somebody chose them. Here **the geometry IS the specification**, and carrying it across is the
  job.
- **An old file drawn before the designer knew the tool** is at no particular width, with no
  styles, no components, no auto layout, and margins that vary because each one was eyeballed on
  its own. Here **the geometry is NOT a specification**, it is an artefact of how the file happened
  to get made, and preserving its proportions faithfully reproduces guesses. What is worth taking
  is the brand: palette, typefaces, logo, the copy, and the module structure, meaning which blocks
  exist and in what order.

**Classify from the census you already have** (Step 2, item 5). This step adds no new inspection
work: the signals are the counts and the presence-or-absence notes you just wrote down.

Two of the signals are load bearing and the rest are hygiene:

- **Is the source at a standard email width** (600 or 640, with a mobile variant near 320 to 390)?
- **Are equivalent margins consistent across designs** (the left content insets you measured are
  identical, not merely similar)?

The hygiene signals: local text styles, local paint styles, variable collections, components or
component sets, auto layout, mobile variants of the designs.

Two rules make the call cheap and keep it from drifting on feel: **a source at a standard email
width whose equivalent margins are consistent cannot be reference only**, and **a source at
neither cannot be authoritative**, whatever the hygiene signals say. Between those, most of the
hygiene signals present reads authoritative, almost none of them reads reference only, and a mix
reads partial.

### AUTHORITATIVE: the geometry is the spec

**Definition.** Widths, margins, type sizes, and spacing were chosen, and they are worth carrying
into the email unchanged. Preserve them. Deviating from a source number needs a reason, written
down in the report.

**Signals.** Drawn at 600 or 640 with a mobile variant; text and paint styles applied consistently
rather than ad hoc fills; components or variables in use; auto layout throughout; equivalent
margins identical design to design.

**Downstream.** Scale detection runs, and it should come out at 1.0 or within a few percent of it,
because a source at email scale has nothing to scale. Brand foundations record the source's own
ramp, spacing, and content width as measured. Module rows inherit source geometry.

### PARTIAL: some of it is deliberate and some is not

**Definition.** Preserve what is demonstrably consistent, standardise what is not, and flag each
judgement so a reader can see which numbers came from the file and which came from us.
**"Demonstrably consistent" has a test:** the same measurement appears in at least three places
and is identical, not similar. A value that appears once, or three times with three values, is not
a specification and gets standardised.

**Signals.** Mixed, and mixed is the normal shape of a real library: real text styles but no
components, auto layout on the newer designs and absolute positioning on the older ones, a
standard email width on some designs and an arbitrary canvas on others, margins consistent inside
one design and different in the next.

**Downstream.** Scale detection runs. Derive the factor from the part of the file that is
deliberate and say which part that was. Every standardisation gets its own line in Flags, since
each one is a place the built system will not match the source on purpose.

### REFERENCE ONLY: take the brand, build the geometry

**Definition.** Take the palette, the typefaces, the logo, the copy, and the module structure.
Build the geometry to email standards. Ignore every source measurement: widths, margins, type
sizes, spacing, image dimensions.

**Signals.** No standard email width; no local text or paint styles; no variables; no components;
no auto layout; no mobile variants; equivalent margins that differ design to design.

**Downstream, and this is the part that currently misbehaves:**

- **Step 4 is SKIPPED, not attempted.** Do not derive a scale factor. Not from the width, not from
  the ramp, and not "for information". There is no proportion to preserve, so a factor is a number
  with nothing on the other side of it, and there is no gap between two derivations to agonise
  over because neither derivation should exist.
- **The report says so, in as many words.** The Scale factor section reads `Not applicable, source
  is reference only` and states the email standards used instead. Write that rather than dropping
  the section, so a reader can tell a decision from an omission, and so nobody supplies the
  missing number themselves.
- **Record that the geometry is ours.** A converted module that does not match the source's margins
  is correct, and the report has to say that plainly, or somebody downstream will later "fix" the
  built system back toward the source and reintroduce exactly what this tier exists to discard.
- This is not a theoretical failure. Deriving a factor on a reference-only source and applying it
  faithfully produced a 16px body sitting inside 20px margins: both numbers correctly divided out
  of a source where nobody had chosen either.

### What email standards mean for a reference-only build

Defaults, stated rather than derived. Put these in the report as the geometry the build uses.

- **A 600 body width**, and **one content width for every module**, 560 inside that 600 with 20/20
  side padding: no module invents its own.
- **A conventional type ramp with body at 16:** 12 fine print, 14 secondary, 16 body, 20 subhead,
  24 to 30 headline. Line height around 1.4 to 1.5 on body copy, tighter on headings.
- **A spacing scale in multiples of 8:** 8, 16, 24, 32, 40, 48. Pick one section padding off that
  scale and use it library-wide rather than a different value per module.

Take only the brand from the source alongside these: palette, typefaces, logo, copy, module
structure and its order.

### This is a judgement, and it has consequences

Say so in the report rather than presenting the tier as a measurement. The two ways of getting it
wrong are not equally recoverable:

- **Calling an authoritative file reference-only throws away deliberate design decisions.** The
  margins, the ramp, and the spacing that made their emails theirs get replaced with our defaults,
  and the customer gets a system that is generically correct and not theirs. This is the worse
  error, because the reasoning behind those numbers is not recoverable from the built file.
- **Calling a reference-only file authoritative dresses guesses as decisions** and hard-codes them
  into every module.

So **when the signals are mixed, prefer PARTIAL and flag it.** Do not guess at either extreme to
make the report tidier. PARTIAL is the accurate answer to a mixed file rather than a hedge: it
preserves what the file proves and standardises what it does not, and it makes each of those
calls visible one at a time. State the signals you saw, both the ones for and the ones against, in
the report's Source fidelity section, and say that the tier is a recommendation their designer can
overrule. One question at hand-off, "is this file a specification or a reference", is the entire
cost of getting it right.

## Step 4: Detect the scale factor (authoritative and partial sources only)

**Run this step only when Step 3 classified the source AUTHORITATIVE or PARTIAL. On a REFERENCE
ONLY source this step does not run at all:** derive nothing, report no factor, and go straight to
Step 5, leaving the report's Scale factor section to record the email standards from Step 3.
Deriving a factor anyway and captioning it as background does not work, because whoever converts
applies the number that is in that section whatever sits next to it.

Not every source library is drawn at email scale. A file that was never meant to export as
email is often drawn at some multiple of it: a mockup enlarged for presentation, a web-first
canvas, a slide artboard. The factor decides every type size, line height, and spacing value in
every converted module, so getting it wrong makes the whole library uniformly wrong, and nobody
notices until a converted module sits next to a real email.

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

**On an AUTHORITATIVE source, expect 1.0, and treat anything else as a contradiction.** The file is
already at email scale, so both derivations should land at or within a few percent of 1 and this
step is a confirmation rather than a derivation. A factor materially away from 1 on a file you
called authoritative means two of your own findings disagree: re-read the width and the ramp, and
if the factor is real, the tier is wrong. Fix the tier and re-run this step from it, rather than
shipping a report that claims the geometry is the spec and then scales it.

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

Record the result in the report's **Scale factor** section (Step 7). Phase 2 reads that number
instead of deriving its own, which is the whole point of settling it here.

### The width factor and the type factor will not agree, and the report has to name which governs what

Choosing a target email width AND a type factor independently brings a second factor back into a
system whose whole rule is one factor. The two ratios agree only when the source happens to have
been drawn at an exact multiple of the target width, and a mockup drawn to present is not drawn to
email proportions, so on a real source they usually do not.

**Run the check and put it in the report.** Divide the source width by the target email width,
compare that ratio to the type factor you recommended, and state the gap. Measured on the migration
this rule comes from: a 1092 wide source against a 600 target is 1.82, the recommended type factor
was 2.2, and 1092/2.2 = 496 rather than 600, so the library was always going to carry 2.2 on its
type and 1.82 across its width. Nobody wrote that down, and the cost landed on the margins: the
source's own 115px text margin is 52px through the type factor and 63px through the width ratio,
the converted library shipped 20px, and no reader of the report could trace which derivation the
number came from, because neither of them produced it.

**When the two differ, name which factor governs which quantities, in the report, in words.** The
defensible split, and the one to state unless the designer decides otherwise, is that the type
factor governs type sizes, line heights, and the spacing scale, while the target email width
governs the body width and everything measured across it: content width, content margin, column
splits, image widths. The reason is that the email width is a hard constraint from the clients
rather than a choice, and legibility is a hard constraint on type, so neither quantity can be bent
to make the two ratios meet. Write it as a sentence with both numbers in it rather than leaving a
reader to infer it from two tables.

**Be honest that this is a genuine tension, not a defect with a fix.** No single factor both
preserves the source's type ramp and preserves its proportions across a body width email can
actually use, because the source was drawn at a width email cannot use. The failure is not having
two ratios. The failure is having two ratios and not saying so, which is how a converted library
ends up with margins nobody can trace back to a decision (converter Phase 2, render spec 0.6).

### The factor is ONE number, and the ramp table has to prove it

Recommending a factor is necessary and not sufficient. Phase 2 has to APPLY it, uniformly, to
every quantity it governs: type sizes, line heights, the spacing scale, paddings, spacer heights.
Widths are the exception the section above just named, and they come from the target email width.
The report is what makes that auditable, so it shows the arithmetic per style rather
than only the conclusion.

**Write the type ramp mapping as a four-column table, one row per style:**

| Style | Authored size | Factor | Email size |
| --- | --- | --- | --- |
| Headline | 65 | 2.2 | 30 |
| Subhead | 55 | 2.2 | 25 |
| Body | 35 | 2.2 | 16 |

The Factor column carries the SAME number on every row, and that is the reason for printing it
at all: a per-style factor cannot hide in a table that restates the factor on each line, because
a second number in that column is visible at a glance. Never write the table as authored size
straight to email size with the division left out, and never round a row toward a size that
looks like a nicer email number. Divide, round to the nearest whole pixel, write down what you
get. Same table, same discipline, for the spacing scale.

**Acceptance test, run on the table before the report ships: the source's ratios must survive.**
Divide the largest email size in the table by the smallest, divide the largest authored size by
the smallest, and compare the two. More than a couple of percent apart means a row has been
rounded off the factor: find that row and fix it, do not ship the table. Run the same check
across the spacing scale. Worked, from the migration this rule comes from: authored 65/35 = 1.86
against email 30/16 = 1.88 passes, a 1 percent drift that is nothing but whole-pixel rounding.
The module that actually shipped came out with a 55 source headline at 30 and a 35 source body
at 16, so 1.57 in the source against 1.88 built, a 20 percent failure. That is the defect this
test exists to catch, and it is worth catching here because downstream it presents as a padding
problem rather than a type problem, so nobody thinks to look at the ramp.

If a row's email size looks wrong, that is evidence the FACTOR is wrong, not licence to adjust
the row. Revisit the factor, re-divide the whole ramp, re-run the test.

## Step 5: Split the designs into modules, then classify every module

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
   component.
   **Technique for unstructured sources: render the whole design at 1:1 and detect content
   bands from the pixels.** Rows of pure canvas background between text and imagery are the
   gaps between modules; the transitions from a run of solid background pixels to a run of
   mixed pixels are the module boundaries. This finds cuts where node structure gave none, on
   the artifact the reader will actually see rather than the tree structure they will not, and
   it costs one render. Record the y-coordinates you detected on each source ref (`top 128 to
   540` rather than a hand-eyeballed range), so Phase 3 can crop to the same pixels without
   re-deriving the boundary. **Then write the boundary down on the row.** Whoever converts the module has to
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

   **Then order the categories deliberately, because they become PAGES.** Phase 2 builds one page
   per category in this inventory, in the order the inventory presents them, and it builds no
   others. So a category order that came out of whatever the walk happened to find first becomes
   an incidental page list in the customer's finished library, which is the shape problem the
   prescription in Phase 2 exists to remove. Do not leave it to the walk.

   **Order the categories the way modules appear in a typical email, top to bottom:** Pre-Header,
   Header, Heroes, Single Column, Two Column, Three Column, Four Column, Images, Reviews, Lists,
   Order Tables, Buttons, Footer. That is how someone building an email scans for the next block
   they need, so it is how the file should be ordered. Skip any category the inventory does not
   use, and add none it does not. Where a category genuinely has no settled place in that
   sequence, put it where the customer's own emails put it and say in the report that you did.

   **Group the inventory rows by category, in that order, and order the rows inside a category by
   reuse, highest first.** The category order is the load-bearing part, since it is what Phase 2
   reads; the within-category order is what makes the highest-reuse modules easy to find. The
   batch plan is read off Recommended next step, which names modules explicitly, so it does not
   depend on row order.

Then assign every module exactly one verdict:

- **(A) Live-text convertible.** Auto-layout stacks of text, images, and buttons that map
  onto mj-section/mj-column/element-frame structure. Text stays selectable and editable in
  the sent email. Best deliverability and accessibility; most modules should land here. **A block
  whose only obstacle is a photograph that overlaps or bleeds past its band is an A too**, with
  the named bleed concession below: the substitute is settled, so it is not a C.
- **(B) Editable-image candidate.** Design-rich compositions (layered imagery, text on
  photos, custom shapes, brand illustrations) that would fight email rendering as live text.
  Email Love handles these deliberately: the design frame is placed inside a column without
  an MJML type name, and the exporter flattens it to a single hosted image at export while it
  stays fully editable in Figma. No rebuild needed; the design survives as-is. Cost: the text
  inside is not live in the inbox (image weight, accessibility, clients with images off), so
  recommend pairing with alt text and keeping critical copy outside the image.
- **(C) Hybrid.** Split the module: headline and body as live text, the rich visual region as
  an editable image. Reserve it for blocks where copy and picture are one composited whole with no
  boundary to cut on: type set over a photographic collage where the lettering is part of the
  artwork. **An image that merely overlaps or bleeds past its band is NOT a C**; it is an A with
  the bleed concession below. The test: if you can name the rectangle the image belongs in and the
  rectangle the text belongs in, it is an A. If you cannot, it is a C. C reads to a customer as a
  partial conversion, so spend it only where the module really is one.
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

**One concession has a settled substitute, so do not invent one: an image that overlaps or
bleeds.** Source designs routinely place a photograph so it overlaps or bleeds past the block it
belongs to: a product shot entering from the right behind body copy, an animal cropped off by the
left edge of a cream band with text beside it. In Figma that is z-order plus absolute position,
and email has neither, so it cannot be reproduced. **The standard remedy is to rebuild the block as
a two column row**: one section, the image in one column and the text in the other, in the same
left to right order the design implies, so the image stops at its column edge and nothing overlaps.
It is called the **Two Column Swap**, and the converter builds it from section 3.4.1 of the render
spec. Name it that way in the report so the two skills are talking about one thing.

Recognizing it is its own step, because nothing in the source labels it and the screenshot looks
like an ordinary photo in a band. Two tells, either one being enough:

- **The photo's bounds extend past the bounds of the block it reads as part of.** Compare the
  image node's absolute box against the band's box, never the screenshot, where the overflow is
  invisible by construction.
- **The photo is clipped by a sibling drawn over it rather than by a mask.** A rectangle of
  background color sits above it in z-order, the layer panel shows no mask and no crop, and the
  composite you see exists in no single node.

When you find one:

- **The verdict is A**, and the row carries the standard wording verbatim rather than a phrasing of
  your own: concession column `image bleed rebuilt as a two column row`, verdict column
  `A (concession: image bleed rebuilt as a two column row)`.
- **Do not propose an alternative and do not re-argue it per module.** It is settled, for reasons
  worth stating once in the report if a reader asks: the substitute keeps the text LIVE, where
  flattening the block to one editable image gives up selectable text, accessibility, and dark mode
  for the sake of an effect; and it degrades well, because two columns stack on mobile so the image
  lands above the text, a normal email pattern and better than a bleed that would have had to be
  abandoned on a 390 wide screen anyway.
- **The notes name the loss precisely: the overlap, and nothing else.** Add the mobile stacking
  note so nobody reads the stack as a second concession.
- **Build constraints carry "render the node, not the fill" for that image**, because the substitute
  needs a rendered crop of the source region and the raw fill is the whole uncropped photograph.

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
side only, and **a two-column row that reads as a visual lockup** (a logo beside a headline, an
icon beside a line of copy, columns sharing a single continuous background bar or card, header
and footer strips): the row says "`mj-group`; keep side by side on mobile". This last one is
worth calling out separately because the audit is walking the whole library and is much better
placed to notice that six header rows across six emails are all the same lockup than the
converter is, meeting each row alone with only a desktop screenshot in front of it. Two roughly
equal content columns (image beside copy, two product cards) are not lockups and get no
constraint; they stack on mobile normally. Write each constraint short and imperative: one
clause a builder can act on without reading anything else. A constraint that applies to the
whole library belongs in Brand foundations or Flags instead of being repeated on twenty rows.

Signals that push a module from A toward B or C: vector logos and illustrations (email wants
images), buttons built as nested app-style instances with state layers, stacked image fills,
gradients and blend modes on text, and effects email clients do not render. Signals of A:
clean vertical auto-layout, flat solid fills, one image per region, system-mappable text.

Do not over-classify toward images. Two MJML capabilities keep more modules live-text than
designers expect: **mj-hero** renders live text over a full background image, so "headline on
a photo" is verdict A when the text sits on one background image rather than woven through
layered art; and sections support background images behind live columns. Reserve B for
compositions where text and imagery genuinely interleave (text wrapping around cutouts,
badges over product shots, hand-placed collage). An overlapping or bleeding photo is not one of
those: it is an A with the bleed concession above.

Finally, **roll the verdicts up per design**: for each design, the ordered list of module names
it is made of and the worst verdict present in it. The Per-design roll-up is a view of the Module
inventory, not a second classification, so it introduces no verdict that is not already on a
module row. It exists so a customer can still ask "what happens to this email" and get an answer,
and Phase 2 does not work from it.

## Step 6: Extract the brand foundations

From the survey, draft what the Email Love design system will carry. **Where each number comes
from depends on the Step 3 tier**, so say on every row which it was: measured from the source, or
taken from the email standards. On an AUTHORITATIVE source the numbers are the source's. On
PARTIAL they are the source's where it is demonstrably consistent and the standards' elsewhere. On
REFERENCE ONLY only the brand comes from the file (palette, typefaces, logo) and every measurement
comes from Step 3's email standards, with no factor involved anywhere.

- **Type ramp, CENSUSED rather than sampled.** Do not derive the ramp from the text you happened
  to meet in Step 5's content modules: a sampled ramp misses the nav-link style, the caption, the
  quote, the eyebrow, and anything else that lives on a page you did not walk through in full, and
  a ramp that arrives incomplete gets filled in mid-conversion where every addition is a decision
  made without the file in front of you. Enumerate every distinct `(family, size, weight,
  line-height)` tuple in the source. On a file with text styles this is the styles page plus any
  local overrides you find; on a file without text styles this is a walk over every text node
  across every design surveyed in Step 2, tabulated. Cluster the tuples where they are within a
  point or two of each other, and treat each cluster as one ramp row. This is a cheap complete
  operation on a file you are already walking and it is strictly better than sampling. The
  arithmetic gate then does its job (an incomplete ramp cannot pass a ratio test on an unseen
  size), and the mapping table below is populated from the census rather than from what got noticed.
  Then map each of their text styles or ramp clusters to an email-safe equivalent, using their own
  fallback choices when a fallbacks page exists. Flag fonts that need web-font
  hosting or substitution. When the Step 4 scale factor is not 1, use the four-column table Step
  4 specifies (style, authored size, factor, email size), with the factor restated on every row,
  so a reader can audit the arithmetic instead of trusting it. Run Step 4's ratio acceptance test
  on the finished table. **On a reference-only source there is no factor and no such table:** state
  the standard ramp (body 16, with 12, 14, 20, and 24 to 30 around it), map their typefaces onto
  it, and label it as the email standard rather than as a measurement. The census still runs on
  reference-only sources, because the typefaces and weights the source uses are the palette the
  ramp gets mapped onto; the sizes are what get discarded on this tier.
- **Palette, CENSUSED rather than sampled.** Same shape and rationale as the type ramp and
  spacing system above: enumerate every distinct fill hex used in the file, cluster
  near-duplicates within a small delta (2-3 units per channel, so `#3C023C` and `#3C004A` do
  NOT collapse but `#009EE2` and `#009FE1` do), and report each cluster with its source hex,
  the count of fills that use it, and the module or modules it appears on. On a file with
  named paint styles this is the styles page plus any local overrides; on a file without
  styles it is a walk over every fillable node. Then propose a set of the six Email Love
  theme colors (backgroundColor, contentColor, textColor, linkColor, buttonTextColor,
  buttonContentColor) drawn from the census clusters, marked as a proposal for the designer
  to confirm, and **name every proposed theme value that does NOT match a source cluster
  exactly, with the delta**: a proposal that quietly lightens `#C4014B` to `#D03E75` is a
  brand decision made without the designer, and this is where it gets surfaced instead of
  shipping into a foundations page that reads as source-fidelity. The census also carries
  low-frequency colors the theme roles do not need (a decorative green used on one badge, a
  bright blue used on one hero); list them as "additional source colors not carried into the
  theme roles" so nothing gets silently dropped. On a REFERENCE ONLY source the census still
  runs, because the palette is what the file contributes on that tier; the theme roles map
  onto the census clusters as normal, no theme value is invented from outside the file.
- **Spacing system, CENSUSED rather than sampled.** A design system's coherence is decided by
  spacing more than by any other quantity, and unlike scale it is invisible in any one module and
  only visible when modules sit together. So enumerate every distinct spacing value in the source,
  clustered by role: **section side padding** (the inset from body edge to content), **vertical
  rhythm** (top and bottom padding on sections and between sections), **column gutter** (the gap
  between side-by-side columns), **card or inset padding** (the inset inside a bordered or filled
  block from its own edge to its content), and the **mobile equivalents** of each where a mobile
  variant exists. Read them from every module you saw in Step 5, not from padding or spacer
  components alone: a source without spacer components can still be hand-drawn with thirty distinct
  side insets, and a source with a tidy spacer library can still have modules that ignore it. State
  each value at email scale (divided by the Step 4 factor) with the count of modules that used it,
  as one row per role. Then **propose one system, per role, with a designer-decision gate**, the
  same shape as the Scale factor block: for each role, the value or short ladder the converted
  library will use, the source values it consolidates, and one sentence naming which module or
  modules disagreed the most so the designer can inspect the outliers before saying yes. Prefer
  multiples of 8 for the system values (8, 16, 24, 32, 40, 48) unless the source's clustered
  centres are strongly on a different grid, so the ladder stays legible. Flag any mobile value that
  is greater than 160px (half a 320 viewport), because that is a defect the source is carrying
  regardless of what the designer decides on the desktop system. **Recorded reason exceptions are
  allowed but named up front:** a full-bleed image band with zero side padding, a wide-quote
  treatment where the block deliberately outsets, and so on. The output of this step is the
  spacing scale the converter builds on; the ratio-acceptance shape of Scale factor applies here
  too, in that the system replaces the source's ad-hoc numbers rather than averaging them. On a
  REFERENCE ONLY source, do not census: the multiples-of-8 scale from Step 3 is the system, label
  it as the email standard rather than as a measurement, and record no source values.
- **Buttons:** their button styles as candidates for the Email Love button component page.
- **Target email width:** the width the converted system gets built at, which is 600 or 640 and
  nothing else. It is a hard constraint from the email clients rather than something the factor
  derives, so do not divide the source width by the factor to get it: on the measured case that
  arithmetic returns 496, which is not a width email can use, and the gap between it and 600 is
  exactly the width-versus-type tension Step 4 declares. Take 640 only where their ESP or brand
  asks for it, 600 otherwise. Label it as the target, and list anything in the file that
  contradicts it.
- **Content margin, extracted as a PERCENTAGE of source width, then converted, and the content
  width it implies.** The audit already hands over a target email width; this is the other half of
  the same measurement, and without it foundations has to invent the number. Measure where text
  actually starts on several designs rather than one: the left inset of the headline, the body copy,
  and the button label. Divide the inset by the source width to get a percentage, multiply that
  percentage by the TARGET email width to get the email-scale margin, and state the content width it
  implies (target width minus twice the margin). Worked, from the migration this rule comes from:
  text starting between 109 and 118px in on a 1092 wide design is about 10.5 percent, which on a
  600px target is a 63px margin and a 474px content width. Report the percentage, the converted
  margin, the implied content width, and which designs you measured.
  - **A consistent source margin is evidence worth carrying, and say so in those terms.** It means
    the customer's own system has ONE margin, so the converted library should have one too, and
    that is the finding foundations acts on. It is the same measurement the Step 3 margin-consistency
    signal already asked for, so reuse those insets rather than re-measuring.
  - **An inconsistent source margin is a FLAG.** List the values you found, say the source has no
    single margin to inherit, and say that foundations will therefore pick one rather than derive
    it. Do not average them into a number that looks derived.
  - **Convert through the target width, not through the type factor**, and note in the report where
    the two disagree (the width-versus-type check in Step 4). Same worked case: 10.5 percent of 1092
    is 115px, which is 52px through a 2.2 type factor and 63px through the 1.82 width ratio. Those
    are two different numbers for one margin, so state which factor you converted through.
  - **On a REFERENCE ONLY source, measure nothing here:** the content width is Step 3's standard
    (560 inside a 600 body, one content width for every module), labelled as the standard rather
    than as a measurement.
  This is a derived STARTING value for the converter's foundations phase, not the final decision.
  Phase 2 fixes ONE content width for the library and may overrule this with a stated reason, and a
  derived number it can accept or overrule is strictly better than a number it invents: a per-module
  content width is what produces a text left edge that moves as the reader scrolls (render spec
  0.3.1).

## Step 7: Write the migration report

Produce one markdown report, in this exact structure. **Source fidelity, Scale factor, Spacing
system, Palette and Module inventory are required sections**: they are what Phase 2 consumes,
and a report missing any one of them cannot be converted from. Source fidelity sits near the top because it changes how every
section below it should be read.

# Migration audit: [Design system name]
## Summary
[Three sentences: what they have, how much converts cleanly, the one or two biggest items
needing design judgment. Name the source fidelity tier here, since it reframes everything after
it. If the source is authoritative or partial and not at email scale, say that here too; it is the
finding that changes the most work.]
## Source fidelity
[REQUIRED, and it changes how every section below it should be read. State the tier, in these
words: AUTHORITATIVE, PARTIAL, or REFERENCE ONLY. Then the signals you classified from, each as
present or absent, so a reader can check the call rather than take it: standard email width, local
text styles, local paint styles, variables, components, auto layout, mobile variants, and margin
consistency with the left content insets you actually measured. Then what it means downstream, in
a sentence or two, which is whether source geometry gets preserved, standardised, or replaced.
- On AUTHORITATIVE: source widths, margins, type sizes, and spacing are carried across as
  measured, and any deviation from a source number is called out with its reason.
- On PARTIAL: which parts of the file you are preserving because they are demonstrably consistent,
  and which you are standardising because they are not.
- On REFERENCE ONLY: that scale detection was SKIPPED because it does not apply, that the built
  geometry is Email Love's rather than the source's, and the email standards used (a 600 body with
  one 560 content width for every module, body 16 with a conventional ramp around it, spacing in
  multiples of 8). Add the sentence that a converted module not matching the source's margins is
  correct and should not later be "fixed" back toward the source.
Close with the honest framing: this is a judgement, not a measurement, it is a recommendation their
designer can overrule, and when the signals were mixed say so here and carry the call into Flags.]
## Inventory
[Pages, style counts, component counts, design count (with desktop/mobile pairs merged),
distinct module count, fonts in play.]
## Scale factor
[REQUIRED as a section; what goes in it depends on Source fidelity.
On AUTHORITATIVE or PARTIAL: both derivations with their arithmetic, the gap between them in
percent, the recommended factor, the reasoning for choosing it, and "designer decision" in as many
words. State the target email width the factor is measured against. One factor for the library;
note any design that contradicts it. When the two derivations agree, say so and give the single
number. On an authoritative source expect 1.0 and say so.
Also state the WIDTH-VERSUS-TYPE check (Step 4): source width divided by target email width,
compared against the recommended type factor, the gap between them, and, when they differ, which
factor governs which quantities in words (type factor for type sizes, line heights, and spacing;
target width for the body width, content width, content margin, column splits, and image widths).
Say plainly that this is a tension the conversion declares rather than resolves, so nobody reads two
factors as an error to be corrected later.
On REFERENCE ONLY: the words `Not applicable, source is reference only`, then the email standards
the build uses instead, and nothing that reads as a factor. Never omit the section and never fill
it with a number derived "for information": whoever converts applies whatever number is here.]
## Spacing system
[REQUIRED as a section; what goes in it depends on Source fidelity, same shape as Scale factor.
On AUTHORITATIVE or PARTIAL: the census from Step 6, one row per role (section side padding,
vertical rhythm, gutter, card or inset padding, mobile equivalents), each row listing the distinct
source values found at email scale with the count of modules that used each, then the proposed
system value or short ladder, then the outlier module or two the designer should inspect. Close
with the words "designer decision", the same as Scale factor: the census is measurement, the
system is a recommendation.
List every mobile value greater than 160px as a defect the source is carrying regardless of the
decision, since it will not fit inside a 320 viewport.
Named exceptions (a full-bleed image band with zero side padding, a wide-quote outset, and so on)
are recorded here as system values with a note, not as ad-hoc overrides.
On REFERENCE ONLY: the words `Not applicable, source is reference only`, then the multiples-of-8
scale the build uses instead (8, 16, 24, 32, 40, 48) with the one section side padding chosen off
it. Never omit the section and never populate it with source measurements on this tier: whoever
converts builds against whatever spacing system is here, and a per-module number reintroduces the
Portsmouth defect the section exists to prevent.]
## Palette
[REQUIRED as a section; same shape as Spacing system. The census from Step 6, one row per
color cluster: source hex, count of fills that used it, module or modules it appears on.
Near-duplicates within a small delta collapsed, exact source hexes preserved. Then the
proposed set of the six Email Love theme colors (backgroundColor, contentColor, textColor,
linkColor, buttonTextColor, buttonContentColor), each named with the source cluster it maps
from and the delta if the proposal deviates from the exact source hex. **Every deviation
listed as a line: `proposed pink #D03E75 vs source #C4014B, delta 60/60/42`**, so a designer
approving the theme is approving the drift too and not reading a lightened value as source
fidelity. Additional source colors not carried into theme roles listed at the bottom (a
decorative green used on one badge, a bright blue used on one hero), so nothing is silently
dropped. Close with "designer decision" the same as Scale factor and Spacing system: the
census is measurement, the theme mapping is a recommendation. On REFERENCE ONLY: the census
runs, the theme roles map onto census clusters as normal, no theme value invented from
outside the file, and no deviation line is expected. Never omit the section: without it the
foundations report reads as source-fidelity and the drift becomes invisible.]
## Module inventory
[REQUIRED, deduplicated, and this is the section Phase 2 works from. One row per DISTINCT
module: module name | category | appears in (design names) | source ref | verdict A/B/C/D |
concession | build constraints | effort S/M/L | notes. The name is the name the converted
component will carry. **Source ref is REQUIRED on every row** and names the one appearance to
convert from, precisely enough to screenshot without re-deriving the split (Step 5): a design
name plus a node name or id, or, where there is no node to name, a position within that design
("top 0 to 480", "between the divider and the footer rule"). Every A row states either `none` or
a named concession in the concession column, with what is lost and the proposed substitute in the
notes; a bleed module carries `image bleed rebuilt as a two column row` verbatim rather than a
substitute you worded yourself. **Build constraints is REQUIRED on every row
and states either `none` or the short imperative constraints from Step 5** (for example "render
nodes, not raw fills: images clipped by z-order" or "image is inset 91 percent, not full bleed"),
so that nothing which changes how a module is built exists only in Flags. **Group the rows by
category, in the top-of-email-to-bottom order Step 5 specifies, and order the rows within a
category by reuse, highest first. The category order is load bearing:** Phase 2 creates one page
per category in exactly the order they appear here, so an incidental order in this table becomes
an incidental page list in the customer's library. The batch plan is read off Recommended next
step, which names its modules, rather than off row order.]
## Per-design roll-up
[One row per design: design name | width(s) | the module names it is made of, in order | worst
verdict present. A roll-up of the Module inventory, not a second classification: no verdict
appears here that is not already on a module row above.]
## Brand foundations
[Type ramp mapping table (style, authored size, factor, email size, one row per style with the
same factor on every row). The rows come from the Step 6 census of every distinct
`(family, size, weight, line-height)` tuple, not from what was sampled in content modules, so a
nav-link style or a quote style that never appeared in a body-copy module still gets a row.
Button styles, target email width. The spacing system and the palette live in their own
sections above, so do not restate either here beyond a one-line pointer to each. State that the ratio acceptance test passed, with the two ratios you
compared. Also REQUIRED here, because foundations otherwise invents it: the source's **content
margin as a percentage of source width**, the email-scale margin it converts to through the target
width, the **content width** that implies, the designs you measured, and whether the source margin
was CONSISTENT (evidence the customer's system has one margin, which the converted library should
keep) or INCONSISTENT (a flag, listed with the values found, and foundations picks one rather than
inheriting it). Say which factor you converted the percentage through. On a REFERENCE ONLY source
there is no factor column, no authored sizes, and no ratio
test to run: give the standard ramp, point at the Spacing system section above rather than
restating the multiples-of-8 ladder here, say the ramp is the email standard rather than a
measurement, give the standard 600 body with its one 560 content width for every module, and take
only the palette, typefaces, and logo from the file.]
## Flags
[Everything a human should look at: fonts unavailable for email, naming typos, empty pages,
inconsistent widths, accessibility risks from image-heavy modules, module boundaries you
inferred rather than read. Plus three that are decisions rather than observations: every named
concession from the Module inventory, for the designer to accept or reject; the scale-factor
recommendation when the two derivations disagreed; and the source fidelity tier whenever the call
was a judgement rather than a reading, which means any mixed-signal call and every REFERENCE ONLY
one, since that tier discards the source's own geometry. State the signals for and against, the
call you made, and the question "is this file a specification or a reference". On a PARTIAL source
also give one line per standardisation, since each is a place the built system will deliberately
not match the source.
**Write a concession line as what it actually
is.** A bleed concession is a known remedy the designer is confirming, not an open question, so
state the loss (the overlap), the substitute (rebuilt as a two column row, image beside text,
stacking image-above-text on mobile), and that this is Email Love's standard for the case, so the
answer is yes or a deliberate exception. A concession whose substitute you proposed yourself is
genuinely open, so ask it as a question and say what you would do absent an answer. Anything here
that constrains how a specific module gets built must ALSO appear in that module's build
constraints column (Step 5): Flags is
where a human decides, the row is where a builder reads, and a build constraint that lives only
here will be missed.]
## Effort estimate
[Per-verdict counts over MODULES, not designs, and an S/M/L per module (the Module inventory
already carries the per-module value; total it here). A modules are mechanical; C modules need a
design pass; D modules need product decisions; a concession costs decision time, and the bleed
concession below is the one that also costs a little build time.
**Bleed modules count as A, so expect the A count to run higher and the C count lower than a first
look at the library suggests.** That is correct rather than an under-count: say in one line that the
standard two column substitute keeps those modules live-text, so a reader who expected a large C
number knows why there is not one. The swap is a known shape rather than a design pass, so those
modules stay mechanical; it does add a restructure, so a module that would otherwise have been an S
can be an M. State the total in designer-days as a range, and say plainly that estimates firm up
after the first converted batch.]
## Recommended next step
[The batch plan, naming modules by their Module inventory row names: foundations first, then
batch 1 of about five of the highest-reuse modules, then the later batches, with a design review
between batches. Then point at Step 8's two routes.]

Numbers in the report come from your actual reads, never estimates presented as counts. Where
you sampled instead of walking everything, say so.

## Step 8: Hand off to conversion

Deliver the report as a file or artifact the user can share internally. Then close the loop,
because an audit that ends without naming what happens next leaves the customer thinking the
migration is somebody's private process. There are two routes, and the report is the input to
both:

1. **Self-serve.** The **emaillove-eds-converter** skill runs Phase 2 from this report:
   foundations once, then modules in batches with a designer review between batches. It builds
   in a NEW target file and keeps this source file read-only. What it reads out of this report,
   by section name: **Source fidelity** (which tells it whether to preserve the source's geometry,
   standardise part of it, or build to email standards and take only the brand), the **Module
   inventory** (one module per row, one batch per group of rows,
   with the source refs, verdicts, concessions, build constraints, categories, and effort, and
   its category ORDER, which becomes the order of the component pages in the converted file), the
   **Scale factor** (every number it builds is at that scale, where there is a factor at all), the
   **Brand foundations** (type
   ramp on email-safe fallbacks, proposed theme colors, spacing, buttons, target email width, and
   the content margin percentage with the content width it converts to, which is where foundations
   gets its one library-wide content width),
   and the **Flags**.
2. **Done for you.** Email Love's team runs the same process, design review included, as part
   of Enterprise onboarding: hello@emaillove.com.

Two things need a human "yes" before either route starts, three when the fidelity call was a
judgement between tiers, and all of them are in Flags: **the source fidelity tier whenever Flags
carries it**, the scale
factor, and each named concession. They change what gets built, so getting them agreed now is
cheaper than re-running a batch. **The tier is the cheapest of the three to ask about and the most
expensive to get wrong**, since calling an authoritative file reference-only discards decisions the
designer made on purpose: ask it as one question, "is this file a specification or a reference",
and note that a reference-only tier means the built geometry is Email Love's and is not meant to
match the source. **For a bleed concession that yes is a confirmation of a known
remedy, not a design question**, so ask for it as one and expect it to be quick; only a concession
whose substitute you proposed yourself needs the designer to actually deliberate. If the audit
surfaced a missing component library file, that blocks conversion outright; say so rather than
letting a batch start without it.

Offer to answer questions about any specific module's verdict, and to re-run the audit after
they clean up anything the flags surfaced.

## Source Adapters

Load only the section for the source the customer picked in Step 0. Each adapter defines its
own Discover step (what replaces Step 2's Figma survey), its own Fetch step (how to hand each
item to the design-converter worker in Phase 3), and the specific audit-step adaptations
that apply because the source is not Figma.

The adapters are ordered by simplicity and by how much of the audit report they can populate.
Local Folder is the simplest and the most bare-bones; the two cloud folders (Google Drive and SharePoint) work the same way as Local Folder but reach files via an MCP instead of the local filesystem; Klaviyo, Marketo, and Customer.io carry more
template metadata forward.

### Source: Local Folder

The customer has emails as `.html` files, `.eml` files, PNG screenshots, or a mix, sitting in
a folder they can point Claude at. **Requires Claude Code** (local file access). Not usable
from Claude.ai.

**Discover.** Ask the customer for the folder path. Then walk it once, non-recursive by
default (recursive only if they say so), and list every candidate file:

```
find <folder> -maxdepth 1 -type f \( -iname '*.html' -o -iname '*.htm' -o -iname '*.eml' -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \)
```

Group the results by inferred template intent from the filename. Common patterns:

- `welcome.html`, `welcome-v2.html`, `welcome-final.html` → three versions of the same
  welcome email; ask which is current.
- `holiday-2024-01.html` ... `holiday-2024-12.html` → a monthly newsletter series; treat as
  one template with 12 sends.
- Anything ambiguous, ask.

Report the discovery back to the customer:

> Found 14 candidate emails in your folder: 8 HTML, 3 PNG screenshots, 3 .eml exports.
> Grouped into 11 distinct templates (2 welcome, 6 promo, 3 lifecycle). Confirm before I
> convert.

**Do not walk without asking.** A `find` on the customer's Downloads folder returns all their
personal emails and receipts. Confirm the path is a folder of source-of-truth email templates,
not a general inbox export or a downloads dump.

**Fetch.** For each item the customer approves:

- **`.html`:** read the file. Render it to PNG at the target email width using headless
  Chrome:
  ```
  google-chrome --headless=new --screenshot=<out.png> --window-size=<width>,4000 --force-device-scale-factor=2 file://<absolute-path>
  ```
  Trim trailing blank space before sending to the converter. A screenshot padded with empty
  page invites the worker to invent spacers.
- **`.eml`:** extract the `text/html` part using the customer's local Python
  (`email.parser`); render as above. Fall back to the `text/plain` part only if HTML is
  absent, and tell the customer plain-text emails will not produce an interesting design
  system.
- **`.png` / `.jpg`:** use directly. Do not upscale. If it is under email width, tell the
  customer the render will be limited by the source resolution.

Send the resulting PNG to the design-converter worker exactly as in Path B of the
`emaillove-figma-builder` skill (see its B3 step, or the `emaillove-eds-converter` skill's
Phase 3 step 1), same headers, same `promptInputs` (with `emailWidth` pinned to the target).
The converter is source-agnostic once the input is a PNG.

**Audit-step adaptations.** The audit steps that change from the Figma default when the
source is a local folder:

- **Step 2 (Survey the file):** Not applicable. There is no Figma file to survey. Replaces
  with the Discover step above: the list of candidate templates plus the raw counts.
- **Step 3 (Source fidelity):** Local sources are always **REFERENCE ONLY**. The customer's
  HTML/PNG carries no styles, variables, or component structure that could serve as a
  specification for widths, spacing, or type sizes. Build to email standards, no scale factor.
- **Step 4 (Scale factor):** Not applicable, per Step 3.
- **Step 5 (Split into modules, classify):** Runs per-template rather than across-templates.
  Each template's modules are listed independently in the inventory. **No cross-template
  deduplication in v1**, so a header used in 5 templates becomes 5 near-identical modules,
  collapsed during design review. Say so in the report explicitly.
- **Step 6 (Brand foundations):** Extract from the first 3 templates' worker output. Palette
  and typography come back from the converter's OCR; the customer confirms them. Do not
  attempt to extract from a single template; the sample is too small.
- **Step 7 (Effort estimate):** Straight per-template estimate. No dedup means one component
  per module per template, so the count is higher than the Figma path would produce. Call this
  out explicitly in the estimate.

**Report shape for a local-folder source.** Slimmer than the Figma report. It carries:

- The source path and the confirmed template count.
- Per-template list: name, format (HTML / EML / PNG), module count, verdict rollup.
- Brand foundations proposal derived from the first 3 templates.
- **The one flag every local-folder audit carries:** cross-template deduplication is
  deferred to design review, so the initial component count is higher than a formal design
  system's would be.
- Effort estimate as designer-days, with the "higher than usual due to no dedup" caveat.

Not present in the local-folder report: verdict-by-verdict rollup across a shared batch,
scale-factor block, source-fidelity classification section (it is always REFERENCE ONLY,
stated once at the top).

### Source: Klaviyo

The customer's emails live in Klaviyo. Requires the official Klaviyo MCP connected to your
Claude session (works from Claude.ai, Claude Code, or any Claude surface with MCP support).
The tool names are prefixed with the MCP's namespace in your environment; the tool NAMES
below are the ones you actually call.

**Discover.**

1. Call `get_account_details` first, always. Klaviyo customers commonly have separate staging
   and production accounts on the same email address; confirming the account name and
   organization back to the customer avoids migrating the staging library by accident.

2. Call `list_email_templates` with the minimal-payload set for discovery:
   `fields_template=["id","name","editor_type","created","updated"]` and
   `sort="-updated"` (most-recently-modified first, which correlates strongly with what is
   actually in use). Klaviyo's `page_size` is capped at 10, so paginate with the cursor from
   `links.next` until it is null.

3. **When the customer has more than about 50 templates, ask them to filter rather than
   pulling everything.** Suggest sort options ("last 30 days," "top 20 by last-updated,"
   "just the campaigns starting with `Welcome`"), and let them pick a batch by name, date
   range, or ID list. Migrating 200 templates unprompted is almost always wrong: most of
   them are old drafts, one-off promo variants, or A/B splits the customer forgot about.

Report the discovery to the customer:

> Klaviyo account: Acme Inc. (org id `abc123`). Found 47 templates, 12 modified in the last
> 30 days. Top 20 by last-updated: Welcome v3, Winback H2, ... Confirm which to migrate.

**Fetch.**

For each template the customer approves:

1. Call `get_email_template` with the template ID, requesting the `html` field. (The `html`
   field is also present in the `list_email_templates` response by default, so if you kept the
   list response in memory you can pull HTML from there instead of a second call. Prefer the
   second call when the customer's selection is small.)
2. **Skip templates with no HTML.** `editor_type=SYSTEM_TEXT_ONLY` (or any type that returns
   only a `text` field) is a plain-text email; log it, tell the customer it will not produce
   a design system contribution, and move on.
3. Render the returned HTML to PNG at the target email width using headless Chrome (same
   command as the Local Folder adapter above). Save each render to a per-template file path
   the audit can reference. Trim trailing blank space.
4. Feed the resulting PNG to the design-converter worker on the same Path B route the other
   adapters use.

**Do NOT default to `render_email_template`.** It substitutes template tags for a provided
context, which sounds appealing ("no `{{first_name}}` in the render!") but it is rate-limited
to 3 requests/second burst and 60/minute steady, much stricter than the other endpoints. For
migration you want structure, not populated content, and the design-converter reads pixels
regardless of whether it sees `{{first_name}}` or `John`. Use `render_email_template` only if
the customer explicitly wants merge tags substituted before conversion, and warn them about
the rate cap on a batch of more than 10 templates.

**A note on the `model` parameter.** Every Klaviyo MCP tool requires a `model` string naming
the LLM you are running as (e.g. `"claude-opus-4-8"`). This is Klaviyo's telemetry, not
optional. Pass the most-specific model identifier you know.

**Audit-step adaptations.**

Same as Local Folder, because a Klaviyo template carries no styles/variables/component
metadata the audit could read: always REFERENCE ONLY, no scale factor, per-template modules
with no cross-template dedup in v1, foundations from the first 3 templates.

Two Klaviyo-specific report additions:

- **Include the Klaviyo template ID and the direct edit URL for every row**
  (`https://www.klaviyo.com/email-editor/{TEMPLATE_ID}/edit`), so the customer can jump back
  to the source when reviewing.
- **Note the editor type per template.** Drag-and-drop templates (`editor_type=SYSTEM_DRAGGABLE`)
  produce cleaner converter output than raw HTML templates, because their layout is more
  structured. Not a verdict, just useful context for setting expectations.

**One honest caveat, worth naming for the customer up front.** v1 pulls Klaviyo **templates**
only. Many Klaviyo customers keep their best current content inside **campaigns** and **flows**,
not standalone templates. If a customer's active work lives in campaigns, tell them the two
paths: create standalone templates from their best campaigns and re-run the audit, or wait for
v1.1 which extends to campaign and flow messages. Do not silently pull only templates and
present it as their whole library.

### Source: Marketo

The customer's emails live in Marketo. **No official Marketo MCP exists at time of writing**,
so this adapter uses direct Marketo REST API calls with the customer's OAuth 2.0 credentials.
Requires an environment where the agent can make outbound HTTP calls (Claude Code and Codex
CLI both support this via `curl` or the standard fetch capability). Not usable from Claude.ai
in its current form, because Claude.ai does not permit arbitrary outbound HTTP.

**One-time credential collection.**

Before Discover, get four things from the customer:

1. **Munchkin ID.** The account identifier that prefixes their Marketo URL. Format:
   `123-ABC-456`. They find it in Marketo Admin → Integration → Web Services → "Munchkin ID".
2. **Client ID** and **Client Secret** for a REST API service. If they do not have one yet:
   - Marketo Admin → Integration → LaunchPoint → New → New Service
   - Service type: **Custom** (Marketo confusingly also has other service types)
   - Assign a role with "Access API - Read-Only" (Access Assets is enough for this workflow)
   - Save, then click **View Details** to reveal the client ID and secret
3. **Workspace name** (optional). Enterprise Marketo installs partition assets by workspace.
   If the customer has only one workspace, skip. If multiple, ask which one to migrate.

The three required values (Munchkin ID, client ID, client secret) are as sensitive as an API
key. Confirm the customer wants to paste them into the current session, or offer to run
against shell environment variables they set locally (`MARKETO_MUNCHKIN_ID`,
`MARKETO_CLIENT_ID`, `MARKETO_CLIENT_SECRET`) so nothing literal appears in the conversation
history.

**Base URL.** Every Marketo API call uses the Munchkin ID as a subdomain:
`https://{munchkinId}.mktorest.com`. Substitute their actual Munchkin ID into every URL
below.

**Auth (do this once per session, cache the token).**

```
POST https://{munchkinId}.mktorest.com/identity/oauth/token
  ?grant_type=client_credentials
  &client_id={clientId}
  &client_secret={clientSecret}
```

The response contains `access_token` valid for `expires_in` seconds (typically 3600). Cache
and reuse it for every subsequent call this session; re-auth only on a 401 response or when
approaching expiration. Pass it on every asset call as `Authorization: Bearer {access_token}`.

**Discover.**

1. If the customer said they have more than one workspace, list workspaces first
   (`GET /rest/asset/v1/workspaces.json`) and confirm which workspace's assets to walk.

2. List email templates with the minimal parameters for discovery:

   ```
   GET https://{munchkinId}.mktorest.com/rest/asset/v1/emailTemplates.json
     ?maxReturn=200
     &offset=0
     &status=approved
   ```

   Paginate by incrementing `offset` by `maxReturn` (200) until the response's `result`
   array is empty. Do not include `status=draft` in v1: drafts are typically one-off
   experiments, not the templates the customer wants to migrate. The API does not have a
   native sort parameter for templates, so sort the accumulated list by `updatedAt`
   descending after fetching.

   Response items include `id`, `name`, `workspace`, `folder`, `status`, `createdAt`,
   `updatedAt`.

3. **When the customer has more than about 50 templates, ask them to filter rather than
   pulling everything.** Marketo template lists are often dominated by legacy A/B variants,
   one-off event emails, and templates from teams that no longer exist. Suggest filtering
   options: by folder (most Marketo orgs use folder hierarchies), by the last 90 days of
   `updatedAt`, or by a name pattern (`Welcome*`, `Winback*`).

Report the discovery to the customer:

> Marketo account: OpenAI (munchkin `123-ABC-456`), workspace: Marketing. Found 87 approved
> templates, 24 updated in the last 90 days. Top 20 by last-updated: Welcome v4, Onboarding
> Day 1, ... Confirm which to migrate.

**Fetch.**

For each template the customer approves:

1. Get the HTML content:

   ```
   GET https://{munchkinId}.mktorest.com/rest/asset/v1/emailTemplate/{id}/content.json
   ```

   The response's `result[0].content` is the raw HTML template. Marketo does not have a
   drag-and-drop equivalent to Klaviyo's `SYSTEM_DRAGGABLE`; every Marketo template is HTML.

2. **Marketo templates use Marketo's own templating syntax** for variables and editable
   modules: `${var:name}`, `${module.name}`, `<mktEditable>`, `<mktModuleContent>`. These
   will render as literal strings in the PNG. The design-converter reads pixels, so it does
   not care, and the customer's Email Love design system will use its own merge-tag syntax
   for the target ESP anyway. Do not attempt to substitute Marketo tags before conversion.

3. Render the HTML to PNG at the target email width using the same headless Chrome command
   as the other adapters. Trim trailing blank space.

4. Feed the resulting PNG to the design-converter worker on the same Path B route.

**Rate limits.**

Marketo enforces two limits: 100 API calls per 20-second window, and 10,000 API calls per
day per instance. The daily cap is generous: a 100-template migration is roughly 200 calls
(auth + list pagination + one content call per template). The 20-second cap is what to
watch. **Do not parallelize template fetches.** Serial fetch keeps you well under the
window without any bookkeeping.

If you hit the burst limit anyway, the response returns error code `606` (rate limit
exceeded). Back off for the remainder of the 20-second window and retry the same request.

**Audit-step adaptations.**

Same as Local Folder and Klaviyo, because a Marketo template carries no styles/variables/
component metadata the audit could read: always REFERENCE ONLY, no scale factor,
per-template modules with no cross-template dedup in v1, foundations from the first 3
templates.

Two Marketo-specific report additions:

- **Include the Marketo template ID and the direct edit URL for every row**
  (`https://app-{munchkinId}.marketo.com/#EMTP{id}A1`), so the customer can jump back to
  the source when reviewing.
- **Include folder path and workspace per template.** Marketo customers often organize
  templates in nested folders (`Marketing / Lifecycle / Welcome`), which is useful signal
  for grouping modules into the target design system's category pages.

**One honest v1 caveat, worth naming for the customer up front.** Marketo has three places
a customer's actual email content lives:

- **Email Templates** (what this adapter pulls). Reusable design templates.
- **Emails** (`GET /rest/asset/v1/emails.json`). Individual email assets, usually inside
  Programs. This is where most customers' actual sent content lives.
- **Content Blocks** (`GET /rest/asset/v1/contentBlocks.json`). Reusable snippets (headers,
  footers, disclaimers) used across many emails.

v1 pulls **Templates only**. Tell the customer this up front: if their best current content
lives inside individual Emails (common) or Content Blocks (very common for headers and
footers), this migration will get their design system foundations right but miss the
campaign-level content. v1.1 will extend to Emails and Content Blocks. Do not silently pull
only Templates and present it as their whole library.

### Source: Customer.io

The customer's emails live in Customer.io. Requires the Customer.io MCP connected to your
session (`cio_read_api`, `cio_schema`, `cio_prime` at minimum).

**First, read the prime doc.** `cio_prime` returns the current authoritative usage
instructions for the whole CLI, and Customer.io's API surface has non-obvious behaviors
(product-renaming, environment-scoping, non-obvious required fields). **Call it at the top
of every session that uses this adapter, before anything else.** The prime doc supersedes
anything below that has drifted.

**Product-naming trap, worth knowing before you ask the customer anything:**

- **"Automations" in the Customer.io UI == the `campaigns` API resource.** The API name did
  not change when the UI renamed them. When the customer says "our automations," they mean
  campaigns; when they say "our campaigns," they might mean campaigns (API) or newsletters,
  ask which. When you talk back to the customer, use their word, not the API's.
- **"Profiles" in the UI == `customers` API resource.** Not relevant to this adapter but
  worth knowing for context.

**Auth check.**

Confirm the MCP is authenticated before Discover: call `cio_auth_status`. If it errors,
tell the customer to run `cio auth login` and paste their `sa_live_` service-account token.
Every request is workspace-scoped via `environment_id` (a Customer.io environment == a
workspace); confirm the customer's environment ID up front.

**What Customer.io actually contains, and what v1 pulls:**

Customer.io has several places email content lives:

- **Templates** (`/v1/environments/{env}/templates`): reusable email templates. Most direct
  equivalent of Klaviyo/Marketo templates.
- **Newsletters** (`/v1/environments/{env}/newsletters`): one-off email sends. This is
  often where a customer's actual sent content lives, so worth pulling by default.
- **Campaigns / Automations** (`/v1/environments/{env}/campaigns`): triggered workflows
  containing messages. **Not pulled in v1.** Campaign message bodies live one level below
  the campaign, and there is no simple "list all campaign message HTMLs" path.
- **Transactional messages** (`/v1/environments/{env}/transactional_messages`): templates
  for API-triggered sends. **Not pulled in v1.**
- **Design Studio emails** (`/v1/environments/{env}/design_studio/emails`): the newer
  Customer.io email builder with components + emails. **Not pulled in v1.** Modern CIO
  customers may have most of their content here; if they mention Design Studio, tell them
  v1 will miss that surface.
- **Layouts** (`/v1/environments/{env}/layouts`): reusable email skeletons that wrap
  content. **Not pulled in v1.**
- **Snippets** (`/v1/environments/{env}/snippets`): reusable content blocks. **Not
  pulled in v1.**

**v1 pulls Templates and Newsletters only.** Ask the customer which (or both) at the top of
Discover, since the balance depends on how they use CIO. Some are template-heavy, some are
newsletter-heavy, most have both.

**Discover.**

1. Ask the customer which of {templates, newsletters, or both} to walk. Their answer
   decides which of the two listings below to run.

2. For each chosen resource, use `cio_schema` to fetch the current list-endpoint schema
   (`cio_schema` with `templates.list` or `newsletters.list`) rather than assuming the exact
   response shape. Customer.io evolves the API more frequently than the other ESPs in this
   adapter, so grounding on the current schema costs one small call and avoids stale-field
   bugs.

3. List with `cio_read_api`. Auto-paginate with `--page-all` for anything beyond the first
   page, and use `--jq` to keep the payload small on the discovery pass:

   ```
   cio api /v1/environments/{env}/templates \
     --page-all \
     --jq '.templates[] | {id, name, updated_at, type}'
   ```

   (Same shape for newsletters; the property name inside the JQ may differ, hence the
   schema lookup in step 2.)

4. Sort locally by `updated_at` descending after fetching. Ask the customer to filter when
   the combined list is >~50, same reasoning as Klaviyo and Marketo: legacy A/B splits,
   dead workflows, one-offs.

Report the discovery to the customer:

> Customer.io environment `123456` authenticated. Found 34 templates and 18 newsletters.
> Top 20 by last-updated: Welcome Template, Onboarding Day 1 Newsletter, ... Confirm which
> to migrate.

**Fetch.**

For each item the customer approves:

1. Fetch the individual resource via `cio_read_api` with its get-endpoint path:

   ```
   cio api /v1/environments/{env}/templates/{template_id}
   cio api /v1/environments/{env}/newsletters/{newsletter_id}
   ```

   The response's HTML body field name differs by resource type; use `cio_schema` on the
   corresponding `.get` endpoint if unclear. Common field names: `body`, `html`, `content`.

2. Render the HTML to PNG at the target email width using the same headless Chrome command
   as the other adapters. Trim trailing blank space.

3. Feed the resulting PNG to the design-converter worker on the same Path B route.

**A note on Customer.io's own agent skills.** The CLI ships two skills that overlap with
this adapter's domain: `cio skills read design-studio` and `cio skills read fly-api`. Do NOT
follow either during a migration audit. They document how to CREATE content in Customer.io;
this adapter READS content out of Customer.io for migration to Email Love. Reading either
skill mid-audit will introduce contradictions.

**Audit-step adaptations.**

Same as the other ESP adapters: always REFERENCE ONLY, no scale factor, per-item modules
with no cross-item dedup in v1, foundations from the first 3 items.

Two Customer.io-specific report additions:

- **Include the Customer.io asset ID, resource type, and direct edit URL** for every row
  (the URL pattern differs by resource; templates and newsletters live at different app
  paths).
- **Include the "created via UI as template vs newsletter" distinction per row.** A
  customer reviewing the migration report cares which of their two content pools each
  module came from.

**One honest v1 caveat, worth naming for the customer up front.** v1 pulls Templates and
Newsletters. It does NOT pull:

- **Automations (`campaigns`)** and their messages: where most triggered/lifecycle content
  lives.
- **Transactional messages**: where receipts, verification emails, password resets live.
- **Design Studio emails**: Customer.io's newer email builder. Modern customers may keep
  the majority of their content here.
- **Layouts** and **Snippets**: reusable wrappers and content blocks.

If the customer's active content mostly lives in one of the not-pulled surfaces, tell them
so up front rather than silently returning a partial library. v1.1 will extend to campaign
messages, transactional, and Design Studio.

### Source: Google Drive

The customer's emails live in a Google Drive folder (`.html`, `.eml`, `.png`, or `.jpg`
files). Requires the Google Drive MCP connected to your session. Works from any Claude or
Codex surface with MCP support (no local file access needed, unlike Local Folder).

**Which MCP.** The reference implementation is the [official Google Drive MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive)
from the modelcontextprotocol servers repo. Third-party implementations exist with varying
tool names. Introspect the connected MCP's tool list at session start so the exact tool
names below match what your MCP actually exposes.

**Discover.**

1. Ask the customer for the Drive folder URL or ID. Format:
   `https://drive.google.com/drive/folders/{folder_id}`. Extract the folder ID from the URL.
2. Confirm the MCP is authenticated for the account that has access to that folder. Google
   Drive's per-user permissions mean a folder shared with a specific person may not be
   accessible to whichever account authorized the MCP.
3. Call the MCP's list-files-in-folder tool (typically `gdrive_list_files_in_folder`, or a
   search query with the folder ID as parent). Filter to these MIME types: `text/html`,
   `message/rfc822` (EML), `image/png`, `image/jpeg`.

Report the discovery to the customer:

> Google Drive folder: "Legacy email templates" (id `1AbC...`). Found 24 files: 15 HTML, 6
> PNG screenshots, 3 EML exports. Confirm which to migrate.

Same 50-file threshold as the ESP adapters: if the folder has more than about 50 candidate
files, ask the customer to narrow (specific filenames, a date-modified range, or a
subfolder).

**Fetch.**

For each file the customer approves:

1. Call the MCP's read-file tool with the file ID. For HTML files, the response body is HTML
   directly. For EML, extract the `text/html` part (see the Local Folder adapter's EML
   handling). For PNG/JPG, the response body is base64-encoded image content: decode and
   save to a temporary file.
2. HTML files: render to PNG via headless Chrome (same command as the Local Folder adapter).
3. EML files: extract the HTML part, then render to PNG.
4. PNG/JPG files: use directly.
5. Feed the resulting PNG to the design-converter worker on the same Path B route the other
   adapters use.

**Audit-step adaptations.**

Same as Local Folder: always REFERENCE ONLY, no scale factor, per-file modules with no
cross-file dedup in v1, foundations from the first 3 items.

**Google Drive specific report addition:** include the file's Google Drive URL per row
(`https://drive.google.com/file/d/{file_id}/view`) so the customer can click through to the
source.

**One caveat worth naming.** Google Drive's OAuth scopes matter. The MCP typically requests
either `drive.readonly` (all files the user can access) or `drive.file` (only files the app
created or that the user opened with the app through a Google file picker). If the MCP was
set up with `drive.file` scope, it will not see arbitrary folders even when the customer
has access to them; the customer would need to re-authorize with `drive.readonly`, or pick
each file individually through a picker. If the MCP returns empty for a folder the customer
knows contains files, the scope is the first thing to check.

### Source: SharePoint

The customer's emails live in a SharePoint site folder (`.html`, `.eml`, `.png`, or `.jpg`
files). Requires a Microsoft Graph MCP connected to your session with permission to read
the customer's SharePoint content.

**Which MCP.** Microsoft's [official Graph MCP](https://github.com/microsoftgraph/msgraph-mcp)
is the canonical option, but the SharePoint MCP ecosystem is thinner than Google's.
Third-party implementations exist with varying tool names. Introspect the connected MCP's
tool list at session start.

**Enterprise IT often blocks third-party OAuth into SharePoint.** Confirm the customer's IT
allows the Graph MCP's app registration before assuming setup will work. If not, they need
admin consent, which can take a week or two in a large org. This is not a v1 blocker for
the skill itself, but it is a real friction the customer needs to know about up front.

**Discover.**

1. Ask the customer for the SharePoint folder path. Format varies but typically:
   `https://{tenant}.sharepoint.com/sites/{site}/Shared%20Documents/{folder}`.
2. Confirm the MCP is authenticated with permission to read that site's content. Some
   enterprise SharePoint setups scope OAuth per-site, not tenant-wide, so a token that
   works for one site may not work for another.
3. Call the MCP's list-files tool for that folder. Filter to the same file types as the
   Local Folder and Drive adapters: HTML, EML, PNG, JPG.

Report the discovery the same way (folder path, file count, format breakdown).

Same 50-file threshold. If the folder is a general document library rather than a
templates folder, ask the customer to narrow to the templates subfolder before pulling.

**Fetch.**

Same as Google Drive: MCP tool returns file content, decode or extract HTML as needed,
render to PNG via headless Chrome, feed to the design-converter worker.

**Audit-step adaptations.**

Same as Local Folder.

**SharePoint specific report addition:** include the SharePoint file URL per row. These
URLs often include tenant-specific tokens and can look unwieldy; preserve them verbatim
rather than trying to shorten them, since the customer's team will recognize them.

### Source: Brevo

The customer's emails live in Brevo (formerly Sendinblue). Requires the [official Brevo
MCP](https://developers.brevo.com/docs/mcp-protocol) connected to your session. Auth is API
key (Bearer token).

**Security note that matters up front.** A Brevo API key grants FULL account access:
sending, contact writes, template edits, everything. It is not a scoped read-only key like
some ESPs offer. Treat the key as a high-privilege secret and offer the customer an
environment-variable path (`BREVO_API_KEY`) so the literal key does not appear in the
conversation history.

**Discover.**

1. Introspect the connected MCP's tool list at session start; tool names below are the
   likely shape but the Brevo MCP has ~27 modules and evolves. Confirm what your
   installation actually exposes.
2. Call the templates-list tool. Filter to email templates (Brevo also handles SMS and
   WhatsApp; ignore both for migration).
3. Sort locally by last-modified. Report the count back to the customer.

Same >50-template filter threshold as the other ESP adapters.

**Fetch.**

For each approved template, call the get-template tool. The response contains the raw HTML
under a field the Brevo API commonly names `htmlContent` (verify against your MCP's tool
schema). Render HTML to PNG via headless Chrome at the target email width. Feed to the
design-converter worker.

Brevo templates use Brevo's own personalization syntax (`{{ contact.FIRSTNAME }}`). Leave
it in the render; the design-converter reads pixels, and the customer's Email Love design
system will use its target ESP's merge tag syntax anyway.

**Audit-step adaptations.**

Same as the other ESP adapters: always REFERENCE ONLY, no scale factor, per-template
modules with no cross-template dedup in v1, foundations from the first 3 items.

**One honest caveat.** v1 pulls Brevo email templates only. Brevo customers often keep
active content inside campaigns and automations too; if the customer's production content
mostly lives in one of those, tell them so up front.

### Source: Kit

The customer's emails live in Kit (formerly ConvertKit). Requires the [official Kit
MCP](https://developers.kit.com/mcp/kit-mcp) connected to your session. Auth is OAuth.

**A framing note that matters.** Kit's content model differs from a formal-template ESP.
Kit primarily has:

- **Broadcasts**: one-off email sends.
- **Sequences**: automated multi-email sequences (each step is an email).
- **Templates**: reusable design templates that broadcasts and sequences can start from.

For migration purposes, all three carry HTML content worth pulling. Ask the customer which
of the three (or which combination) to migrate at the top of Discover.

**Discover.**

1. Introspect the connected MCP's tool list (Kit's MCP has 65+ tools; the exact
   template/broadcast/sequence tool names vary).
2. Call whichever list tool matches the customer's chosen pool: list-broadcasts,
   list-sequences, or list-templates.
3. Sort locally by last-modified. Report the count.

Same >50 threshold and filter prompt.

**Fetch.**

For each approved item, call the corresponding get-item tool. The response includes the
HTML body (field name varies by item type: check your MCP's tool schema). Render to PNG,
feed to the design-converter.

**Audit-step adaptations.** Same as other ESP adapters.

**Kit specific report addition.** Include the pool type per row (broadcast / sequence
step / template), so the customer can trace each migrated module back to where it came
from in Kit.

### Source: ActiveCampaign

The customer's emails live in ActiveCampaign. Requires the [official ActiveCampaign
MCP](https://developers.activecampaign.com/page/mcp) connected to your session. Auth is
OAuth. The MCP has 46 write-capable tools; we only use the read-side for migration.

**Discover.**

1. Introspect the connected MCP's tool list at session start.
2. ActiveCampaign has campaigns (one-off sends) and automations (workflows containing
   emails). Templates are reusable designs. Ask the customer which pool to walk. For
   migration, campaigns and templates are the most common source of design system
   material; automation emails are usually variations of the same designs.
3. Call the list tool for the chosen pool. Sort locally by last-modified. Report count.

Same >50 threshold and filter prompt.

**Fetch.**

For each approved item, call the get-item tool. HTML body is under a `content` or `html`
field depending on item type. Render to PNG, feed to the design-converter.

**Audit-step adaptations.** Same as other ESP adapters.

**One caveat.** ActiveCampaign templates can be either drag-and-drop or raw HTML.
Drag-and-drop templates convert more cleanly than raw HTML (their layout is more
structured), same trade-off as Klaviyo's `SYSTEM_DRAGGABLE` vs raw HTML templates. Include
the template type per row in the report if the MCP surfaces it.

### Source: Iterable

The customer's emails live in Iterable. Requires the [official Iterable
MCP](https://support.iterable.com/hc/en-us/articles/42936800222612-Overview-of-Iterable-s-MCP-Server)
connected to your session. **Currently beta.** Read-only by default (which is exactly what
migration needs).

**One deployment note.** Iterable's MCP is a **self-hosted local deployment** installed
via npm, not a hosted MCP the customer authenticates into. If the customer has not set it
up, point them at the docs first. Setup takes a few minutes and requires their Iterable
API key with template-read permissions.

**Discover.**

1. Introspect the connected MCP's tool list at session start (Iterable's MCP has 108 tools
   at beta launch; the exact template-list name varies).
2. Iterable has both templates (reusable designs) and campaigns (individual sends,
   including within journeys). For migration, templates are the direct hit; campaigns are
   where a customer's actual production content often lives.
3. Ask which pool to walk. Call the list tool. Sort by last-modified. Report count.

Same >50 threshold and filter prompt.

**Fetch.**

For each approved item, call the get-item tool. HTML body under a `html` field (verify
against schema). Render to PNG, feed to the design-converter.

**Audit-step adaptations.** Same as other ESP adapters.

**Iterable specific report addition.** Since the MCP is beta, log any unexpected error or
schema surprise in the report per row so the customer can flag it back to Iterable if
needed. This helps their beta feedback loop and helps this adapter improve.

### Source: Omnisend

The customer's emails live in Omnisend (an ecommerce-focused ESP with email, SMS, and
push). Requires the [official Omnisend MCP](https://mcp.omnisend.com/) connected to your
session. Auth is OAuth.

**Discover.**

1. Introspect the connected MCP's tool list at session start.
2. Omnisend content lives primarily in campaigns (one-off sends) and automations
   (triggered workflows). Templates are reusable designs used by campaigns. Ask the
   customer which pool to walk.
3. Call the list tool. Sort by last-modified. Report count.

Same >50 threshold and filter prompt.

**Fetch.**

For each approved item, call the get-item tool. HTML body under `html` or `content`
(verify against schema). Render to PNG, feed to the design-converter.

**Audit-step adaptations.** Same as other ESP adapters.

**One Omnisend-specific caveat.** Omnisend is ecommerce-focused, so many templates carry
product blocks that pull live product data at send time. Those blocks will render in the
PNG with placeholder or last-cached product data. The converted design system module
inherits the layout but not the live product logic; the customer would rebuild the
product-block wiring in their target ESP. Say this in the report so the customer knows to
expect it.

### Source: HubSpot

The customer's emails live in HubSpot's marketing hub. Requires the [official HubSpot
MCP](https://developers.hubspot.com/mcp) connected to your session. HubSpot's MCP is a
**CRM and marketing platform server**; it reads campaigns and manages contacts. There is
no separate email-only surface, so this adapter uses the marketing-emails endpoints.

**Discover.**

1. Introspect the connected MCP's tool list at session start.
2. HubSpot marketing content lives in **marketing emails** (drafts, published, and
   automated) and **email templates**. Ask the customer which pool to walk; most
   customers want marketing emails since that is where the sent design lives.
3. Call the list tool. Filter to `published` status by default (drafts are usually
   experiments). Sort by last-modified. Report count.

Same >50 threshold and filter prompt.

**Fetch.**

For each approved item, call the get-item tool. HTML body under a HubSpot-specific field
(verify against the MCP tool schema; HubSpot APIs typically expose `emailBody` or a
rendered-body field).

Render to PNG, feed to the design-converter.

**Audit-step adaptations.** Same as other ESP adapters.

**One HubSpot-specific caveat.** HubSpot marketing emails often embed HubSpot's
personalization tokens (`{{ contact.firstname }}`), smart content blocks (rules-based
conditional content), and CTAs that render from a separate HubSpot CTA library at send
time. Personalization tokens are fine (same as Marketo, Brevo). Smart content and dynamic
CTAs will render only the default variant in the PNG. Say this in the report so the
customer knows their conditional content and CTA-library links won't survive the
migration verbatim; they'd rebuild that logic in the target ESP.

## Staying current

This is version 1.17.0 of this skill. If you have web access, check once per conversation
(quietly, without narrating it) whether a newer version exists: fetch
https://raw.githubusercontent.com/email-love/claude-skills/main/.claude-plugin/marketplace.json
and compare this skill's own version to its entry there. That file lists each skill's current
version, so the check stays correct no matter which skill released most recently; the old
repository-wide latest-release check reported whichever skill shipped last, which could be a
different skill entirely. If a newer version exists, mention it once at hand-off with the right
update path for the user's surface: claude.ai users re-upload the .skill file from the newest
release, which attaches all three bundles, and Claude Code plugin users run the marketplace
update. If you have no web access, skip this silently.
