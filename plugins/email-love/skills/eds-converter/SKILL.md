---
name: eds-converter
description: Convert an audited legacy Figma design system into a working Email Love design system, foundations first, then modules in batches with design review between batches. Builds under the audit's source fidelity tier, preserving the source's geometry where it is a specification and building to email standards where it is not. Use this skill whenever the user wants to convert, rebuild, or migrate their existing Figma email templates to the Email Love structure, run foundations, or convert a batch of modules, after the emaillove-migration-audit skill has produced their audit report. The audit report is required input; if it does not exist yet, run the audit first.
---

# Email Love EDS Converter

Convert an audited legacy design system into a working Email Love design system. This skill
follows a migration audit (the migration-audit skill produces it) and works in two
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

**If your environment lets you choose a model, use your most capable one for this skill.** A
migration runs once and holds a large rule set at once, the render spec alone is tens of
thousands of tokens, and a rule dropped partway through becomes a component that silently
breaks on export later, for someone who was not here to catch it. That is a different budget
than the emails a customer builds afterward against an already-verified design system, where a
faster model is usually the right call.

## Inputs

1. The migration audit report from the migration-audit skill (file or pasted).
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

- **The audit** (the migration-audit skill): minutes, scaling with library size. It
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

### Say when you STOP, too

The five checkpoints above cover a run that is still running. Nothing in them covers a run that has
stopped, and that asymmetry is worse than having neither half: **an agent that reports progress but
not its own stop is worse than one that does neither, because the user infers continuation from the
last progress line.** Checkpoint 3 fires at every module boundary, so its absence reads as module 4
being transcribed right now. Silence is indistinguishable from still working.

**Never stop silently.** If you stop, for any reason, say so in the SAME message as the last of the
work, not in a later reply and not only once the user asks. Four things, every time:

- what you completed, in the checkpoint 3 format so it reconciles with the lines before it;
- what remains, by module name from the audit's Module inventory;
- why you stopped;
- the exact thing needed to resume, phrased so the user can send it straight back.

The reasons that qualify are a blocker, a decision only the user can make, a limit you have hit, or
reaching the end of a unit of work. That last one is the common case rather than an exception:
finishing a batch IS a stop, and checkpoint 5 plus the gate in Phase 3 step 7 are how that one gets
announced.

**Do not pause mid-batch.** The batch is the unit of work and the design review happens BETWEEN
batches (Phase 3 step 7), so five modules of a five-module batch is a defined stopping point and one
module of five is not. Either complete the batch, or stop AT the blocker and name it. An overrun is
not a blocker: a batch tracking at double the estimate earns a revised number at the next module
boundary, not a stop.

A blocker specific enough to stop mid-batch is one this file already names: a concession with no
human yes in the audit's Flags, a scale factor nobody has confirmed, an asset or component library
file that is genuinely absent so the module cannot be built at all, or another decision only a
designer can make. Having built some of the batch is not on that list, and neither is the batch
feeling long.

**Writing resumable state is correct, so say WHERE it is.** A batch that can span sessions needs
state that survives one, so keep a small JSON state file beside the per-module MJML JSON you already
save in Phase 3 step 1, and update it at the same module boundaries as checkpoint 3: the batch
number, the modules completed and remaining by inventory name, the fidelity tier, and the scale
factor and content width the batch is being built at. That much is expected behaviour rather than
extra credit. **Then name its path in the stop message**, because state the user cannot see does not
make a run resumable, it only makes you feel that it is.

One worked example, the format to copy. It is one message, sent unprompted, not an answer to "are
you still working on it":

> Stopped, not still running. Batch 1 of 3, 4 of 5 modules done, 80 percent: Global header, Hero with
> CTA, Two column product row, Testimonial, all built at the REFERENCE ONLY standards (600 body, 560
> content width). Remaining in this batch: Global footer. Why I stopped: the footer's inventory row
> carries the image bleed rebuilt as a two column row concession and there is no human yes on it in
> the audit's Flags, so building it now means rebuilding it. To resume, confirm the two column
> rebuild or say "defer the footer to batch 2", and I will finish the batch from the saved state at
> `./migration-state.json`.

## Phase 2: Foundations (run once per customer)

### Precondition check: confirm the references are present

Before building anything, confirm you can read both `references/render-spec.md` and
`references/structure.md`. This skill cites them by section number 23 times; they carry every
MJML tag and attribute mapping and the exporter's ground truth. If either file is missing,
say so to the user before you start, name what you will not be able to verify (the mapping
for any tag not covered inline below, structural checklist items keyed by render-spec section,
worked examples of the Two Column Swap and the group rule, most of Phase 3 step 5's
verification), and either fetch a fresh skill bundle before continuing or agree with the
user on a reduced scope. This exact absence bit an earlier customer batch four modules in and cost
five rounds of design review to work around; a one-line check catches it before the first
module.

### The shared plugin data keys the exporter reads (inline, load-bearing)

The exporter reads shared plugin data in namespace `emaillove`. This table is the irreducible
contract; it lives inline here so a batch can proceed even if the references above did not
ship. The render spec keeps the prose, the worked examples, and the rationale.

| key | where it goes | value | what it does |
| --- | --- | --- | --- |
| `name` | every tagged node | the MJML tag string (`mj-wrapper`, `mj-section`, `mj-column`, `mj-column-inner`, `mj-text`, `mj-image`, `mj-button`, `mj-divider`, `mj-spacer`, `mj-social`, `mj-social-element`, `mj-group`, `mj-hero`, `mj-navbar`, `mj-navbar-link`, `mj-table`, `mj-raw`; frame variants add `-Frame`) | tells the exporter which MJML element this node emits. REQUIRED on every tagged node; the layer-name fallback is a fallback, not the contract. |
| `nodeType` | ONLY the root frame of a whole email | `'mainFrame'` | marks the frame as an email template. Absent on every module (an `mj-wrapper` component). Present on a module = the block uploads as a whole email and no component JSON is emitted. |
| `backgroundColor` | mainFrame root | hex | DARK MODE page background. House default `'#000000'`. These six keys only fire in dark mode; filling them with the light palette ships light-on-light. |
| `contentColor` | mainFrame root | hex | DARK MODE content/section background. House default `'#1F1F1F'`. |
| `textColor` | mainFrame root | hex | DARK MODE text color. House default `'#FFFFFF'`. |
| `linkColor` | mainFrame root | hex | DARK MODE link color. House default `'#FFFFFF'`. |
| `buttonTextColor` | mainFrame root | hex | DARK MODE button label color. House default `'#000000'`. |
| `buttonContentColor` | mainFrame root | hex | DARK MODE button background. House default `'#FFFFFF'`. |
| `lightThemeBackgroundColor` | mainFrame root | hex | the LIGHT mj-body `background-color`; defaults to `#FFFFFF` when empty. The one light value in the set. |
| `fallBackFontName` | mainFrame root | font family, e.g. `'Arial'` | fallback for text nodes whose pinned font is unavailable. |
| `emailSubject` | mainFrame root | plain string | optional. |
| `emailPreHeader` | mainFrame root | plain string | optional. |
| `fullWidth` | `mj-wrapper` | `'true'` | only when MJML has `full-width`; otherwise omit. |
| `stackColumns` | `mj-wrapper` or `mj-section` | `'true'` (default) or `'false'` | `'false'` prevents mobile stacking WITHOUT wrapping in an `mj-group`. Propagates down from the wrapper to its sections. |
| `reverseStack` | `mj-wrapper` or `mj-section` | `'true'` | reverses stacking order on mobile. |
| `href` | `mj-image` | absolute URL | link target; omit when absent, never write `#`. |
| `altText` | `mj-image` | plain string | image alt text. |

**Magic link values the exporter rewrites at export time.** Some hrefs are not links, they are
instructions to the exporter: write the magic value on the link (text, button, or image; the
link is what matters, not what surrounds it) and the plugin substitutes the right thing for
the customer's ESP at export. Never invent a placeholder for these and never hand-type an
ESP's merge tag unless the customer explicitly asks for a specific one; a design system that
hard-codes one ESP's tag stops being portable, which is the whole point of the magic value.
A customer who already knows their tag can link to it directly and the exporter preserves it.

| Put this on the link | What the exporter does |
| --- | --- |
| `unsubscribe.com` | Replaced with the selected ESP's unsubscribe merge tag. Works on text, buttons and images. Source: `help.emaillove.com/plugin/links/unsubscribe`. |
| `manage-preferences.com` | Replaced with the ESP's preference-center merge tag on Klaviyo ONLY (`{% manage_preferences_link %}`). Not on the help site; verified in plugin and backend source 2026-08-04. On every other target the literal URL ships. |

**The exporter also INJECTS the preference placeholder on its own.** Any text
containing the word "preference(s)" that carries no hyperlink gets
`https://manage-preferences.com` auto-linked at export (the plugin's
placeholder, mirroring `unsubscribe.com`). Combined with the row above, that
means a non-Klaviyo export ships a live link to a third-party domain the
customer does not control, from text the builder deliberately left unlinked.
Observed in a real export before the source was checked: the injection is
intended plugin behavior, only undocumented. The defense is to never leave
preference wording unlinked: give it an explicit link the plugin will preserve.
Default to `unsubscribe.com` (the help site itself says a "Manage preferences"
control should point there), use a real preference-center URL when the customer
supplies one, or use `manage-preferences.com` deliberately when the target is
known to be Klaviyo.

Batch 4 shipped a footer with `https://www.example.com/unsubscribe-placeholder`
because this convention was not surfaced in the skill; the agent escalated it as the one
item that was a legal problem, not a polish problem. The answer was one word.

**Mobile behaviors that are NOT shared plugin data keys** (a common trap: Batch 2 spent
rounds hunting for keys that do not exist because these behaviors are Figma-side, not
data-side):

- **Full-width mobile button (`applyFullWidth`, the exported `.mj-b-full` class):** set by
  `layoutSizingHorizontal = 'FILL'` on the `mj-button` node. No plugin data key. HUG =
  auto-width, FIXED = pinned, FILL = full-width mobile. Section 3.7 of render spec.
- **Fluid-on-mobile image (`fluid-on-mobile`, class `lf`):** derived from width comparison.
  When the `mj-image` rectangle's width equals its column's content width, the exporter
  keeps `fluid-on-mobile` and the image scales; when the rectangle is narrower, the
  exporter drops it and the image stays fixed. No plugin data key. So a footer logo that
  should NOT scale is built at less than its column's content width; a hero photo that
  SHOULD scale is built at exactly the content width. Section 4.2 of render spec.
- **Mobile stacking of columns:** default behavior for `mj-column` inside `mj-section`.
  Suppress with `stackColumns='false'` (above) or by wrapping the columns in an
  `mj-group`. The choice between the two is a decision, not a preference: `mj-group`
  holds a lockup shape (unequal columns, shared background, header/footer strip);
  `stackColumns='false'` fits the rare case where you want equal columns to stay side
  by side without pinning them as a group. Section 3.3 of render spec.

The load-bearing rule from all of this: **not every mobile behavior is a plugin data key.**
When the exporter surprises you, first check whether the intended behavior is Figma-side
(layout sizing, width relationship, node property) before you go hunting for a key that
does not exist.

### Mobile Styles ARE shared plugin data: two schemas, both observed

Everything below was read back off nodes AFTER the plugin's own Mobile Styles tab wrote them.
That provenance is the point: an earlier conversion invented plausible key names
(`mobileStylesFontSize`, `isFontSizeActive`), wrote them to 23 frames, verified them by reading
its own writes back, and shipped a library where none of it did anything. Worse, one invented
activation flag switched a control on at its default value and the customer's body copy rendered
at 10px. **Never write a plugin-data key you have not observed the plugin itself write.** To
observe one: have a human set the value once in the Mobile Styles tab, then dump the node's
shared keys and copy exactly what appeared.

**Schema A, container spacing.** On `mj-wrapper`, `mj-section`, `mj-column`, and leaf pair
wrappers:

| key | value |
| --- | --- |
| `mobileStylesPaddingTop/Right/Bottom/Left` | px number as a string |
| `isPaddingActive` | `'true'`, REQUIRED. Without it the padding values are stored and silently ignored |
| `stackColumns` | `'true'` / `'false'` |
| `mobileStylesHideInMobileDevice` / `mobileStylesHideInDesktopDevice` | `'true'` |

**Schema B, type.** On the `mj-text` / `mj-button-text` TEXT node itself, NOT the frame:

| key | value |
| --- | --- |
| `fontSize` | mobile px number as a string |
| `fontSize_mode` | `'override'`, the switch; without it the value is ignored |
| `lineHeight`, `lineHeight_mode` | same pattern, only when a mobile line height is genuinely needed (see the percentage rule in Phase 2 step 3; usually it is not) |
| `letterSpacing`, `letterSpacing_mode` | same pattern |

Two different conventions in one panel: containers use a `mobileStyles` prefix plus a shared
`isPaddingActive` flag; type uses bare property names plus a per-property `_mode` switch, on a
different node than the panel is opened from. Do not rationalise them into one scheme, and do
not trust this table over a fresh observation if the plugin has shipped since it was written.

**Read-back is necessary but NOT sufficient.** Your own write always reads back. The only
end-to-end verification is a render: export or preview, and measure the mobile output. Measured again on a
later build: a two-column nav carried `stackColumns` and read it back cleanly, and the
export still rendered alternating full-width rows; only the exporter render showed it.
Whether the plugin consults private state the shared key does not reflect is unconfirmed;
either way the render is the arbiter, never the key.

### Build the foundations

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

**Read the audit's Spacing system section and build to it, not to per-module source values.** The
audit's census consolidated the source's ad-hoc side insets, vertical rhythm, gutter and card
paddings, and their mobile equivalents, into one system per role, with a designer decision on
each. That system is what every module in every batch inherits. When a module conversion asks
"what side padding does this section get", the answer is the audit's row, not a number measured
off this module's own screenshot: a per-module measurement is exactly how the batch 2 defect
landed, thirty distinct side insets across twenty-eight modules and one that broke mobile.
Named exceptions (a full-bleed image band with zero side padding, a wide-quote outset) are
allowed only where the audit's Spacing system listed them as exceptions, with the reason. A
module that needs a spacing value the system does not carry is a designer question raised out of
batch, not a silent override.

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
     can follow.
     **The frame is vertical HUG with clipsContent OFF, never a fixed height.** A fixed height
     clips the content invisibly and the page functionally disappears; batch 2 shipped a
     100px-fixed frame that clipped 940px of instruction text and the page rendered as the
     bottom edge of its own title. After you finish writing the block, screenshot the whole page
     and confirm every line is visible; a screenshot that shows only the title is a fail.
     Required, one short block each: that modules are wrapper components and are used
     by INSTANCING them, never by copying or detaching; that **text is edited through the
     component properties on an instance** while **images are edited by selecting the image
     rectangle inside the instance and replacing its image fill** (never by detaching or
     reparenting anything). Figma has no image component-property type, so the phrase "swap
     images using the component properties panel" is wrong and reads to a user as a workflow
     that does not exist; say the actual workflow instead. Continuing: that color, type,
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
     **A gap in the ramp is a decision for foundations, not for batch 3.** If the specimen sheet
     shows a jump with nothing between it (a 26 next to a 17, or a 30 next to a 20), look at
     the source for content that would sit in the gap: eyebrows, card captions, small
     subheads, fine print. If any exists, add the step now and record it as a standardisation.
     Adding it later means editing every module that would have used it, and the ramp gap will
     not have gone away, it will have been resolved module by module into per-module sizes.
     Batch 4's foundations report predicted this cost verbatim ("adding it later means
     touching every module that would have used it") and deferred anyway; three modules in
     Batch 3 wanted exactly the missing 20px step. Predicting the cost and deferring is not a
     judgement, it is the rule the skill is now naming.
     **A step added this way sits outside the ratio check** and must say so, exactly like the
     spacing scale: the check proves one factor was applied uniformly across the sizes the audit
     derived, and a standardised step was never derived from that factor. Say which rows the
     check covers.
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

   **Check the font is installed before you build the ramp, and know the substitute.** Call
   `figma.listAvailableFontsAsync()` and look for the target family by name. The Figma
   environment an agent runs in typically serves Google Fonts only (about 1,900 families),
   which means **Helvetica, Helvetica Neue and Arial are all absent** even though they are
   the most common email-safe answer and every migration whose customer picks the standard
   email-safe stack (`'Helvetica Neue', Helvetica, Arial, sans-serif`) will hit this. The
   failure mode without the check is silently building the ramp in Inter or whatever Figma
   substituted, which then flows into every module.
   When the target family is Arial or Helvetica and unavailable, **build in Arimo**. It is
   the metrically compatible clone of Arial: identical advance widths, so a string that fits
   on the canvas fits in the email and section 3.3.1's slack arithmetic stays accurate
   rather than approximate. Arimo is in the Google Fonts set and the Figma environment
   loads it. The same move covers the other two common email-safe stacks: **Gelasio** is
   the metric clone of Georgia, **Tinos** of Times New Roman, both in the Google Fonts set.
   One caveat that belongs in the foundations report: metric clones are close, not
   identical, and display sizes are where the difference shows. Measured: a 64px headline
   that fits two lines in the original face measured 542px against a 540px content box in
   the clone and wrapped to a third line, a 58px height change. That is the concrete
   argument for resolving real font hosting before batch 1.
   **State the consequence in the foundations report**, because it is real: the exporter
   writes `fontName.family` into `font-family`, so an export will say Arimo until the family
   is swapped or Arial is accepted at send time. Say it once, plainly, rather than leaving
   it for someone to find in a send.
   Also expect the weight count to drop. The email-safe stack offers Regular and Bold; a
   brand font with Light, XBold, and Black collapses to two, and that collapse belongs in
   the report so a designer sees which weights they lost and can push back if any were
   load-bearing.

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

   **Line heights in every text style are PERCENT, never PIXELS.** The exporter emits a percent
   line height as a unitless ratio, which scales with the font size at every breakpoint; a pixel
   value is frozen at every breakpoint. Measured failure: 17px mobile copy rendering on its
   desktop 33px line box, double-spaced. Converting is lossless on desktop (27px body at 33px
   becomes 122.2%, which is still 33px) and makes mobile line heights automatic; no mobile
   line-height override is needed at all. Convert the ramp's pixel values at build time:
   `percent = px / fontSize * 100`.
   **The bold-range trap that comes with this:** `setRangeFontName` (used for a bold run inside
   a body paragraph) detaches that range from the text style, so a later style-level line-height
   change leaves the range frozen at the old pixel value: one paragraph tight, its sibling
   double-spaced, same node. After any per-range font work, `setRangeLineHeight(0, length, ...)`
   with the style's percent value, and verify with `getStyledTextSegments(['lineHeight'])`
   returning ONE segment.

   **Then take the MOBILE ramp from the audit's Mobile styles section verbatim.** It is a
   two-anchor compression, not the scale factor applied again; the audit has the rule and the
   measured case. Foundations records the numbers (report + Type page, `Body: 27px desktop /
   18px mobile`); Phase 3 step 3 writes them per module using Schema B (the `fontSize` +
   `fontSize_mode` keys on the TEXT node; see "Mobile Styles ARE shared plugin data" above).
   Where the audit predates this contract, derive here with the audit's two-anchor rule and say
   you did.
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
   never vectors. **Logos have an intrinsic size and are never resized to fit.** A logo's own
   aspect ratio and pixel dimensions are the source of truth; do not stretch it to fill a
   column, do not scale it up to match a hero image, do not fold it into a "grow inset images
   to fill their column" pass. This is a separate rule from the image sizing rules that apply
   to hero photography, because a stretched logo damages a brand asset the customer already
   owns rather than an editable image the plugin will regenerate.
   Export the RENDERED node every time, never the raw image fill behind it: a
   source fill with `scaleMode: 'CROP'` loses its crop the moment you take the underlying
   asset, and you get the whole photograph instead of the picture the designer composed
   (render spec 4.2.1, which also has the aspect-ratio rule).
   **The render-node-not-fill rule fires here, in Phase 2 step 6, and again in Phase 3 step 1
   where the module gets screenshotted for the worker.** They are two different actions, taken
   at two different times, on two different pipelines. A bulk canvas-crop pass done for
   efficiency in either phase reintroduces the same defect: on batch 2 the hero photograph
   was cropped out of a canvas render and the overlapping white card baked into the image,
   producing a ghost headline inside the picture that only surfaced at the visual check.
   Bulk pipelines that crop from a canvas render are the failure mode; export each image
   node individually.
   **Transparency for dark mode: key UI icons, never brand logos, and check before keying.**
   Icons rendered off their light band carry that band baked in, and on a dark-mode ground they
   read as solid light boxes; so social icons, store badges, and decorative marks should be
   keyed to transparent PNGs. Use a border-connected flood fill, never a global colour replace
   (artwork legitimately contains the band colour inside itself; a global replace punches holes
   through it). **But a brand logo is different, and this is a measured failure: a logo whose
   letterforms depend on its band (dark ink with brand-colour counters, designed for a yellow
   bar) was keyed transparent and became illegible ink-on-ink in dark mode; the customer's
   words were "you butchered it".** Before keying ANY asset, check what remains against
   `#1F1F1F`: if the surviving ink does not clear contrast on a dark ground, ship it opaque
   with its band intact, and say so in the report. Logos default to opaque; this is the
   dark-mode sibling of the never-resize-a-logo rule.
7. **Root EMAIL TEMPLATE frame** on Campaigns at the audit's target email width (600 or 640,
   never the source canvas width when the source was not at email scale; 600 on a REFERENCE ONLY
   source unless the customer's ESP or brand asks for 640): vertical
   auto-layout, width FIXED at that email width, height Hug, the shared marker, and the theme
   colors from the audit's proposal:
   `setSharedPluginData('emaillove', 'nodeType', 'mainFrame')` plus backgroundColor,
   contentColor, textColor, linkColor, buttonTextColor, buttonContentColor,
   lightThemeBackgroundColor, and fallBackFontName (section 2.1 of the render spec has all
   nine keys and what each one is for). **The six theme keys are DARK MODE values: take them
   from the audit Palette's dark-mode proposal, or the house defaults (`#000000` page,
   `#1F1F1F` content, `#FFFFFF` text and links, `#FFFFFF` button with `#000000` label), and
   never the light palette repeated**, which only fires in dark mode and ships light-on-light
   there. `lightThemeBackgroundColor` is the one light value in the set.
   **This is the only `mainFrame` foundations produces, and it is an email, not a module.**
   It exists so batch 1 has somewhere to drop modules and see them in context. The modules
   themselves are a different shape entirely (Phase 3, and section 2 of the render spec):
   each one is an `mj-wrapper` COMPONENT with **no** `mainFrame` marker and no theme keys.
   Do not copy this frame as a starting point for a module.

   **A wrapper is FIXED at the target email width, as a component and as every instance of it.**
   When Phase 3 drops wrapper instances into this root frame, size each instance
   `layoutSizingHorizontal = 'FIXED'` at the same width the component was built at, not FILL.
   Section 0's FILL rule (prefer FILL, pin only when you must) is for frames INSIDE a wrapper,
   not for the wrapper itself. A wrapper sized FILL inherits from whatever container it is in,
   which reads correctly the moment its container is this 640-wide root and breaks the moment
   the same instance is placed elsewhere or the root width changes. The plugin's export also
   reads column widths from the pinned wrapper width, so a FILL wrapper leaves the export math
   ambiguous. Step 5 of Phase 3 has the matching verification.
8. **Report** what was built, **the source fidelity tier you built under and one clause of why**,
   the target email width, and the content width you built
   at, the completion checklist result below, what the
   audit proposed that you changed, and
   what needs the designer's eye before batch 1 (theme colors especially: they are a proposal
   until a human confirms).
   **Include a WCAG contrast table for every text-on-fill pairing the theme will render.** Walk
   the proposed theme (`textColor` on `backgroundColor`, `linkColor` on `backgroundColor`,
   `buttonTextColor` on `buttonContentColor`, and each explicit text-on-brand pairing the
   design uses, for instance a headline color on a hero band), compute the WCAG contrast ratio,
   and label each row `pass` (>=4.5:1 for normal text, >=3:1 for large text at 18pt or 14pt bold
   and above) or `fail` with the ratio. Flag any pairing that fails 4.5:1 for normal text since
   most email body copy sits under that threshold, and any button pairing whose ratio sits at
   exactly the 3:1 large-text floor since it leaves no safety margin. Batch 2 shipped
   `color/text/accent = #009EE2` at 3.00:1 on white and used it on 18px bold subheads, which
   fails AA for text below 18pt bold; the table is what surfaces that before the designer
   confirms the palette. On a fail, name the darker semantic token that reaches the threshold
   (batch 3's `blue/700 = #0078B4` reaches 4.83:1) or note that the designer needs to
   supply one.
   Then the tier's own numbers:

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
- [ ] **Getting Started:** the frame is vertical HUG with clipsContent OFF and no fixed height
      (screenshot the whole page and confirm every line is visible; a page that shows only its
      title is a fail); text-editing describes component properties while image-editing describes
      selecting the image rectangle inside the instance and replacing its fill (Figma has no
      image component-property type, so any wording that says "swap images using component
      properties" is wrong); instancing rather than copying, styling from the tokens, and the
      "does not export as expected" path are all present; plus the email width, the content
      width with its side margin, and the scale factor, or, on a REFERENCE ONLY source, the
      sentence that the geometry is built to email standards and the brand came from the source.
- [ ] **Foundations:** every swatch labeled with hex AND variable name, primitives and semantics
      visibly separated, the spacing scale rendered and labeled with token names and values, the
      radius token present. No hex anywhere on the page that no variable carries.
- [ ] **Type:** one specimen row per style, each with the style name, a sample line actually set
      in that style, and a caption naming family, weight, and size, ordered largest to smallest.
      Then look at it: does the ramp step evenly? A step that reads wrong beside its neighbors is
      a factor problem, not a style problem, on a source built through a factor, and a mis-built
      standard ramp on one that was not (step 3).
- [ ] **Every text style's NAME matches its own VALUE, read back from the style, not from what
      you meant to set.** A style called `P2/Regular` whose `fontName.style` is `Light` is a fail,
      and it is a fail that survives every downstream check: the style exists, applies cleanly,
      and is named correctly, so nothing structural ever contradicts it. The Ultimate EDS
      foundations shipped five such styles and put 271 text nodes, essentially every paragraph in
      the library, at the wrong weight. Also compare the ramp's dominant body weight against the
      dominant body weight in the audit's census; if the source is overwhelmingly Regular and your
      body style is Light, the ramp is wrong no matter how evenly it steps.
- [ ] **Every text style's line height is PERCENT**: read them back; a PIXELS unit anywhere is
      a fail (it freezes the mobile line box). And **the mobile ramp is recorded** with its two
      anchors, in the report and on the Type page. Numbers only; nothing written to nodes yet.
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

**Before the first module, establish how the batch checks will run.** Check the Email Love
MCP (mcp.emaillove.com) for `emaillove_export_figma`: when it is present, step 6's export
sniff is fully agent-run with `operationType: "preview"` (no plugin click, no export quota),
and the mobile render already runs through `emaillove_preview_email`, so the whole batch
check loop needs zero human sessions. **The Email Love MCP is a SEPARATE connection from
this skill's install; installing the plugin does not connect it.** When the tools are
absent, do not conclude they do not exist and do not silently fall back: give the user the
one-time connect step (`claude mcp add --transport http emaillove
https://mcp.emaillove.com/mcp`, or add `https://mcp.emaillove.com/mcp` as a custom connector
in claude.ai Settings → Connectors; other clients are covered at
help.emaillove.com/plugin/ai/agents-in-figma), and tell them the sign-in it opens is Email
Love's normal account flow, the same sign-in the Figma plugin uses, so it is the right
screen even though it does not mention the exporter. A fresh session after connecting
exposes the tools. Also do not confuse this server with the Email Inspiration MCP
(email search and inspiration); the two are not interchangeable. Its v1 coverage is the core tag set (mj-wrapper,
mj-section, mj-group, mj-column, mj-column-inner, mj-text, mj-image, mj-button, mj-divider,
mj-spacer); it rejects mj-hero, mj-social, mj-navbar, and mj-table with a CoverageError
naming the node, and only those modules still need the plugin's human-click Export. When the
tool is NOT on the MCP, the export sniff needs the plugin's Export button, a human click on a
paid seat: say so now, in the batch-1 opening message, and say what it means: mobile
behaviour will be built and computed but never verified against exporter output until a
human runs it. Do not discover this at step 6 of batch 3. (Measured on a three-batch run:
sixteen modules delivered with zero renders and zero sniffs, every mobile decision verified
as intent only, and three clean batch reports silent on the one axis that matters most.)

**Batch 1 is a proof batch of at most four modules.** Pick them to cover as many of these risk
classes as the source contains: a full-width or deliberately cropped photo; a grouped
icon-and-text row; a multi-column module with component properties; a footer or social-icon
row. Do not release later modules until every proof module passes production desktop and mobile Preview/export. When no production render route exists in the session (no exporter tool, no
human click available), stop after the proof batch and report the deferred state; continuing
into later batches on deferred exports is the exact expansion the proof batch exists to stop.
Canvas evidence cannot waive this gate.

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
build constraints, and its effort. **A library of 8 or fewer modules may run as ONE batch**,
with one design review before upload; the batch structure exists to stop defects propagating
across batches, and a single batch has nothing to propagate into. Above that, stay at roughly
five modules per batch: batch 1 always surfaces something, and the review after it is the
highest-value gate in the whole conversion. Where a module appears in several designs, the source ref
names the one appearance to convert from, so convert it ONCE from there and note that design; the
other appearances are the same component placed again, not more work. When a row has no source
ref, pick the cleanest appearance yourself and record which one in the batch report, so a
reviewer can tell your boundary from the audit's.

**Freeze a compact batch Fact Pack before the batch's first write.** It carries only what this
batch can be wrong about, and nothing else:

```text
Batch Fact Pack - batch <n>
- Structural authority: <source node tree, or the supplied/ESP HTML, per the audit>
- Visual authority: <approved comps / source renders; defect screenshots are symptoms>
- Tier / email width / content width / scale factor: <from the audit>
- Modules: <inventory row name> -> <source ref actually converted from> (one line each)
- Unknown or pending: <anything unresolved that could change a module's geometry or
  responsive behavior>
```

Do not start writing while `Unknown or pending` holds anything that can change what you build;
resolve it or record why it cannot change this batch. Evidence that arrives mid-batch and
contradicts the Fact Pack stops the batch until the pack is re-frozen - it does not get patched
around silently. Include geometry lines only for modules where geometry is the thing being
preserved; a REFERENCE ONLY batch carries the standards instead.

**Approvals stay conversational and scoped to the batch.** The design-review gate after each
batch is one approval for one batch. When the user's request already clearly authorizes exactly
this batch ("convert batch 2 as planned"), that is the approval - do not stack a second
confirmation on top of it. Tool-execution permissions are separate and stay as they are.

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

**First decide whether the worker is the right input at all.** The worker is a structure
detector for sources where structure must be inferred from pixels. When the audit classified
the source AUTHORITATIVE or PARTIAL *and* the source carries components, auto layout, and
frames at the target email width, read the source node tree directly instead: it already
holds exact fills, sizes, paddings and nesting, and it exposes facts a render cannot show
(crop transforms, container clipping, zero-height text, fills stacked under an image).
Measured on an email-native source: direct reads gave exact values with no reconciliation
pass, and caught an image 994px wide clipped to 640 by its container that any screenshot
would have shipped 55 percent too wide. Use the worker path for unstructured sources,
flattened mockups, and every non-Figma adapter.

**When the supplied source includes HTML (any ESP adapter, or a customer-supplied file),
that HTML is the authoritative structure for BOTH breakpoints.** Before building, inventory
the desktop structure from the DOM and the mobile structure from its media queries as two
separate lists (text runs, images with their own hrefs and dimensions, per-breakpoint
composition), and build to that inventory. A screenshot never overrides the HTML, and a
canvas that disagrees with the supplied HTML is the thing to fix, not the evidence.
Measured: a footer was patched repeatedly from its screenshot while the supplied HTML held
the real desktop grid, the real mobile recomposition, and the individual logo assets the
whole time.

Say in the batch report which path you took
and why.

On the worker path: do not rebuild by eye and do not run the plugin's Convert button for migration batches. The
pipeline is: screenshot the source module (read-only), POST it to the design-converter
worker, transcribe the returned MJML JSON into the target file, then verify.

1. **Screenshot the module** from the customer's file (read-only; `get_screenshot` or an
   export). The row's source ref says what to shoot: on an email-native source that is a named
   frame or node; on an unstructured source it is the region of a design the source ref bounds,
   cropped at the boundaries the audit set rather than at ones you decide now. Keep the PNG; it
   is also your visual reference for verification.
   **On an unstructured source, render the whole design page once at 1:1, then crop locally.**
   Per-node screenshots via `get_screenshot` fail on a file with no grouping: a loose rectangle
   comes back rendered in isolation, without the text that visually sits on top of it in the
   design, which is useless when the design's meaning is layered z-order. One full-canvas render
   at native resolution costs one call and gives exact pixels for every module the audit's
   source refs bound; the agent crops locally to each module's rectangle. On an email-native
   source with proper components this is not needed and per-node screenshots are correct. The
   choice is per source, not per module.
   The module screenshot is for the worker to classify structure. It is not the source of
   image assets. **Any image asset a module will actually carry is exported from its own node,
   not cropped out of this screenshot or out of a canvas render.** A crop taken out of a
   broader render bakes overlapping siblings into the picture (a headline over a hero, a card
   over a photograph, a badge over a product shot), which then survives every downstream step
   and only surfaces at the visual check as a ghost. This is the same render-node-not-fill
   rule as Phase 2 step 6, restated here because the pipeline is different: a bulk
   canvas-crop pass for efficiency in either phase is exactly how the batch 2 hero shipped
   with a ghost headline inside the picture. When you need a per-module image asset (for
   example a hero photograph the customer wants placed rather than a gray fill), export that
   image node in isolation even when it is slower than cropping the module screenshot.
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
2. **POST to the worker** at `https://convert.emaillove.com`:
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
   - **If the worker returns `403` with body `error code: 1010`, that is a Cloudflare
     browser check, not an auth failure.** The edge is fingerprinting the User-Agent and
     rejecting non-browser clients. The Bearer and provider headers above are correct as
     documented; auth is not the problem. Retry with a normal browser `User-Agent` header
     (any recent Chrome or Firefox UA string works) and the request goes through. This is
     an infrastructure quirk the worker edge may lift later, so the first line of the
     error body is the diagnostic to check; a 403 without `error code: 1010` is still an
     auth problem and the Bearer/provider check applies.
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

- **Multi-column rows top-align by default.** Columns holding different amounts of content
  otherwise centre against each other and the row reads as a jumble. The exporter reads a
  column's `primaryAxisAlignItems` as `vertical-align` (MIN = top) and its
  `counterAxisAlignItems` as the column `text-align`, two INDEPENDENT reads, so a column can
  be top-pinned with centred text: primary MIN, counter CENTER. Set the parent section's
  `counterAxisAlignItems = 'MIN'` too, so the canvas shows what the export does. This
  deliberately relaxes the "both axes same value" rule for multi-column rows; single-column
  sections keep the matched-axes rule as-is. Override to middle only where the design
  demonstrably centres (a badge beside a headline in a lockup).
- **Build the pair, do not style the wrapper.** The wrapper carries layout; the inner node
  carries content. An image is an `mj-image-Frame` containing a rectangle whose fill is the
  image, never a frame with an image fill on itself. A divider is an `mj-divider-Frame`
  containing a line, never a frame with a solid fill. Childless wrappers export as empty
  cells. Legacy designs almost always express images and rules as fills on a frame, so this
  is the most common thing you must actively restructure rather than copy.
- **A lockup is an `mj-group`, not two loose columns.** A two-column row is a lockup when it
  needs to stay side by side on mobile, and the design does not say that in words. Recognizing it
  is its own step, because nothing in the source labels it and the desktop screenshot the worker
  read is silent on mobile behavior. Three visual tells, any one is enough:
  - **Unequal columns with one small and fixed.** A logo beside a headline. An icon beside a line
    of copy. A price chip beside a product name. A date beside a badge. The small column reads as
    an attribute of the larger one, not as its own row of content.
  - **The two columns share a single continuous background.** A colored bar, a boxed panel, a
    rounded card. Stacking would split the background in half and the visual identity collapses.
  - **The block sits in the top or bottom strip of the email as a header or footer.** Headers and
    footers are lockups by default, because they read as one strip of chrome rather than a stack
    of content blocks.
  Two roughly equal columns of *content*, image beside copy or two product cards, are not lockups
  and should stack normally on mobile. When in doubt, err toward grouping headers and footers, and
  err toward stacking content rows. Every case gets a recorded decision either way in step 3
  Part A of this phase, and step 5's mobile verification confirms the decision is present.
  **Worked exception: a row of five or more nav links does NOT survive as a group.** A grouped
  nav bar of five or more short links breaks words mid-letter at phone width, because the
  exporter has to divide the body width by the column count and the resulting per-link box is
  narrower than a single word. A single inline text line with wide spacing wraps into nonsense
  for the same reason. Ungrouped columns stack cleanly, one link per row, and that is the
  shipped shape. Record the stacking decision as "loose columns, stack expected, no keys set,
  nav bar exceeds group-safe width" in step 3 Part A, and move on. On batch 2 this cost two
  attempts before landing on the stacked build; the rule saves them.
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
- **Take the STRUCTURE from the worker and every NUMBER from measurement.** The worker is a
  very good structure detector: it finds columns, rows, stacking order, which things are
  buttons, and it will sometimes find a structural fix the source does not advertise (a
  single 538px text run split into four separately linked items is the kind of structural
  finding to trust). It is not a measuring instrument. Colors drift by several units, sizes
  land on plausible round numbers rather than the customer's ramp, and fonts flatten to
  Arial when unpinned; the worker returns all of these confidently. So transcribe its tree,
  then replace every color with one sampled from the source pixels, every type size with one
  measured (cap-height method in render spec section 5.2.1), and pin every font
  against the audit's ramp before accepting the value.
  **A size the worker returns that is not on the audit's ramp is the loudest signal it
  guessed.** The ramp is the specification; a 40 where the ramp says 36 is a per-module
  factor sneaking back in, which is the exact drift the single-factor rule exists to prevent.
  Batch 4 carried nine color and size mismatches on the worker output where the delta
  ranged from "one shade off" to "not even close" (`#CCCCCC` for measured `#FFFFFF`, four
  different wrong reds for one button color, a 40px headline where the ramp said 36 and 40
  was not on the ramp at all).
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

### 3. Decide mobile behavior

**This step always runs, whether the source has a mobile twin or not**, because the biggest
mobile decision is structural (mj-group vs loose columns), made in step 2, and it does not live
in Mobile Styles data. An earlier version of this skill made this step "merge the mobile twin"
and skipped it silently on unstructured legacy sources with no mobile frames, which is where the
Batch 2 batch shipped with header lockups that stacked on mobile. Do not repeat that. This is
the ONE mobile checkpoint every module gets, twin or no twin.

**Part A: for every multi-column section, record the stacking decision.**

Read each section in the module you just built. If it has more than one column, ask which
of THREE mobile behaviors the source calls for: it stays side by side (`mj-group`), it
stacks (loose columns), or the source uses a genuinely different mobile COMPOSITION that no
stacking of the desktop structure can produce. Apply the lockup tells from step 2 (unequal
columns with one small and fixed, columns sharing a continuous background, header or footer
strips are lockups by default). Then write the decision and the reason in the module's report
line, per section, in this format:

- `header row: mj-group (lockup: logo + headline sharing the dark bar)`
- `product cards row: loose columns (two equal content blocks, stack expected)`
- `footer top row: mj-group (lockup: logo + H6 headline in one strip)`
- `brand logo row: recomposed (mobile shows the primary mark on its own row, siblings beneath)`

**The third option builds paired sections**: a desktop-only section carrying
`mobileStylesHideInMobileDevice` and a mobile-only sibling carrying
`mobileStylesHideInDesktopDevice`, each composed for its breakpoint (the same observed
visibility keys the band-decoration pattern uses). There is no observed mobile-alignment
key and the never-write-unobserved-keys rule stands, so when mobile alignment or
arrangement differs from desktop, recomposition IS the sanctioned route. Headers and
footers get an explicit desktop-versus-mobile comparison before their decision is
recorded: they are where sources most often recompose rather than stack, and a stacked
desktop footer that should have been recomposed reads as broken, not as adapted.

A section with more than one column and no recorded decision is not done. Step 5's mobile
verification fails a module where any multi-column section lacks a decision.

**Every `mj-group` decision also gets a mobile geometry ledger.** At 320, 375, and 390px (or
the customer's named target viewports): mobile content = viewport minus the section's mobile
left and right padding; resolved column = column width / group width * mobile content;
resolved inner = resolved column minus that column's own left and right padding. Prove
`resolved inner >= natural image width` for an icon or image that must not shrink, and
`resolved inner >=` the longest unbreakable text run measured in the exported font stack, not
the canvas font. Use the inner content box. Comparing the asset to the total column while ignoring column padding is a false pass. Record the ledger in the module's report line; a
group that fails the ledger gets wider columns, less padding, or a different structure, not
a smaller icon quietly stretched or shrunk by the renderer.

**Part B: write the mobile styles. This ALWAYS runs.**

An earlier version fired only when the source had a mobile twin, which on a typical migration
means never, and the result was a library correct at 640 and unreadable at 375. The audit's
Mobile styles section is the input; writing it onto the built nodes is this step. Use ONLY the
observed schemas from "Mobile Styles ARE shared plugin data" (Schema A containers, Schema B
text nodes); an invented key fails silently and an invented activation flag actively breaks
(the measured case shipped 10px body copy).

Per module:

- **Mobile font size on every `mj-text` and `mj-button-text` TEXT node** from the audit's
  mobile ramp: `fontSize` = the mobile px, `fontSize_mode` = `'override'`. On the TEXT node,
  not the frame.
- **No mobile line heights**; the percentage line heights from Phase 2 step 3 ride the mobile
  size automatically. Only write `lineHeight` + `lineHeight_mode` for a genuine per-module
  exception, and record it.
- **Mobile padding on every wrapper/section whose horizontal inset exceeds the mobile value**:
  `mobileStylesPaddingTop/Right/Bottom/Left` plus `isPaddingActive = 'true'` on the same node.
- **Stacked-column spacing:** every section whose columns stack on mobile (loose columns, not
  `mj-group`) gets `mobileStylesPaddingBottom = '28'` + `isPaddingActive = 'true'` on each
  column EXCEPT the last. Their desktop gutter is horizontal and disappears on stack; without
  this, stacked cards and badges land flush against each other. The last column is excluded so
  the section's own bottom padding is not doubled (0.7's rule).
- **Visibility** per the audit's hide-on-mobile list; **alignment** where the mobile layout
  differs; **stacking** decisions from Part A.

Then read every key back AND treat that as necessary, not sufficient: your own write always
reads back, so the only true verification is a render (step 6's batch checks: the mobile
render and the export sniff). List everything written in the module's report line.

**Where the source HAS a mobile twin**, diff it first and let measured differences win over the
derived ramp for that module, noting which. Ignore differences that are only the narrower frame;
capture deliberate ones. Inexpressible differences (different copy, different crop) go to the
designer via the report.

**Provisional rules, forward-test-gated.** Three patterns are strong recommendations but are
NOT yet exporter-proven hard rules; treat them as preferences with the escape hatch intact
until a production desktop AND mobile Preview forward-test confirms each:

- Prefer ONE responsive content tree when supported controls (stacking, mobile keys, visibility)
  can express both breakpoints - but the documented paired-section escape hatch stays available
  where recomposition genuinely differs.
- Treat adjacent filled rows that visually form one card as one continuous perimeter (one
  resolved outer bound, radii on the outer perimeter only) - verify the seam in both production
  renders before promising it is gone.
- Reject silent desktop simplification as the price of a mobile repair - a mobile fix that
  regresses desktop fails, it does not ship quietly.

When one of these is forward-tested and holds, record the evidence in the batch report; until
then do not present them as guaranteed exporter behavior.

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

**Customer-facing copy gets TEXT properties BY DEFAULT.** Headlines, eyebrows, subheads,
body copy, and button labels are what a marketer changes every send, and the Getting Started
page tells them to change text through the property panel; a module with no TEXT properties
cannot be edited the documented way. Do not wait for evidence that the copy varies: on a
single-design source there is no such evidence for anything, and an evidence gate applied to
TEXT starves the whole library into read-only (measured on a one-design shakedown: zero text
properties module after module, each one individually justified). The only text that stays
unbound is boilerplate a marketer should NOT touch per send (legal copy, the postal address,
the unsubscribe line) and **text carrying hyperlink ranges**: binding `characters` to a
component property wipes `setRangeHyperlink` ranges at bind time, and every later edit
through the property wipes them again, so a footer or CTA band whose links silently break
the first time someone edits the copy is worse than a fixed block. Observed during a live
build; the links had to be re-applied after an accidental bind. A link-bearing node stays
unbound and is edited in place.
The evidence gate applies to the OTHER property types: a BOOLEAN needs a sibling design
where that region is genuinely absent (never add "Show X" speculatively), and an
INSTANCE_SWAP needs a real variant to swap to. Two to seven properties per module is the
working range; zero is legitimate only for a module with no customer-facing copy at all
(a full-bleed image band, a divider).
**A property whose binding is wrong is worse than no property**, so re-read
`componentPropertyReferences` back off each node to confirm the binding landed. Record the
properties you added, and why, in the module's report line.

**Every module that contains a button MUST expose the button's label as a TEXT property at
module-root level**, named `Button label` on a single-CTA module or `Card 1 button label`,
`Card 2 button label` in a grid. **Figma rejects remapping a nested instance's TEXT property
to a module-root property** (measured: `Unrecognized key(s) in object: 'Label#3:0'`), so the
construction that satisfies this rule is an INLINE button: a styled frame plus a single text
node matching the foundations button component exactly, with the label property bound on the
inline text node. The foundations component remains the style reference and the
INSTANCE_SWAP target for a Button Style property; it is not instanced inside modules. Batch 2 shipped 18 buttons across 18 modules, every one with
a working label property on the foundation and none of them surfaced at the module the
marketer instances, so a user following the Getting Started page could not change any CTA
copy from the top-level property panel. The Show button BOOLEAN is a separate decision from
Label: add it only where a sibling design in the source has that button absent, not
speculatively. Any module with a button and no top-level Button label property is a fail on
the step 5 checklist.

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

### 5. Verify per module: ONE read-back pass, then one screenshot

Verification is expensive in Figma round trips, so do not walk the tree once per check.
**Read the built module back ONCE**, into a single dump per node (transport note:
`get_metadata` fails with an opaque SSE parse error above roughly 80KB or on non-ASCII layer
names, so do the read-back with `use_figma` in batches of about a dozen nodes, one compact
ASCII-sanitised line per node; that is also what makes this single-pass discipline
practical): node type, layer name,
layout mode and sizing, both alignment axes, paddings, resolved x/width, fills and their
variable bindings, all `emaillove` shared plugin data, component property references, and
(on text nodes) `getStyledTextSegments(['lineHeight'])`. Evaluate every predicate below
against that dump locally. **List every violation by node id in the batch report; an empty
list per group is the only pass.** A "walked the tree, looked fine" pass is what shipped 18
alignment mismatches and 18 untagged button TEXT children on batch 2 without a single line
of the checklist reporting anything.

**Group 0: parity with the source. Run this FIRST, and treat it as the gate the other five are
not.** Every group below asks "is this build internally consistent?" None of them asks "is this
the module the customer gave me?" A build can pass all five perfectly and be the wrong design.

For every module in the batch, compare the BUILD against the SOURCE, paired by inventory name:

- **TEXT node count**, against the audit row's content census `T`. Then the strings themselves:
  the trimmed first 40 characters of every text node, sorted, in both. A count that matches while
  the strings differ is the failure that hides best (a footer whose four named nav links became
  three generic `ADD YOUR CTA` buttons passes any count check).
- **Image-bearing node count** against the census `I`, plus each node's rounded width x height.
  This is what catches a full-bleed background photo rebuilt as a flat fill, and a 2x3 grid
  rebuilt as 2x2.
- **Text alignment** per node, and the module's band fills.

**Any difference is a FAIL that names the module and the delta.** Exactly three resolutions are
allowed, and each is written into the batch report rather than assumed:

1. an optional region you added deliberately, which ships `visible = false` so an instance out of
   the box still matches the source exactly, and which the batch report lists by module and node
   so a reviewer can reject it;
2. a deliberate consolidation the module's inventory row calls for;
3. a source defect the rebuild fixes, named as such.

Anything else you add is invented content, and it costs the customer trust faster than a missing
feature does: three footers in the Ultimate EDS build carried a postal address the source never
had, and one replaced four named navigation links with three generic `ADD YOUR CTA` buttons. Copy
comes from the source. When a module genuinely needs a region the source lacks, that is case 1,
and it is hidden by default.

"The counts differ because the transcription is a summary" is not one of them, and neither is
"the module looked right". On the Ultimate EDS migration (180 modules) all five internal groups
reported zero violations across five separate batch verifications while **26 modules disagreed
with the source**: one two-column module had lost all 8 of its text nodes, a list had lost all 8
of its row icons, four heroes had a flat fill where the source has a full-bleed background photo,
and three footers carried an address line the source does not contain. Every one of those was
invisible to a structural predicate and obvious to a count.

**If you build modules through a serializer-and-builder pair** (compress each source module into
a compact spec, rebuild from the spec), this group is not optional and not a sampling exercise.
That pattern is what makes a large library tractable, and its failure mode is total and silent:
anything the spec does not model does not survive, and nothing inside the build can tell.
Run Group 0 on **every** module, not a sample.

**Group 1: shape and tags.**
- Root is a COMPONENT tagged `mj-wrapper`, layer name = module name, `nodeType` empty on the
  root and on every node below it (a module carrying `mainFrame` uploads as a whole email).
  No theme color keys unless a designer asked for a dark-mode block treatment.
- `name` key resolves to a real tag on every tagged node, including `mj-button-text` on
  every button's TEXT child (an untagged inner text of a foundation-button instance still
  fails). Every leaf is a complete tagged pair. No unrecognized frames except intentional
  editable-image regions. `mj-column-inner`, if used, is literally `children[0]` of its
  column. No detached instances. Layer names carry display names; no friendly string leaked
  into the `name` key.
- Both alignment axes match on every auto-layout frame, with ONE deliberate exception:
  multi-column top-align (primary MIN + counter per content, the step 2 default; independent
  exporter reads, render spec 3.4). Report each mismatch as `<node id>: primary=X,
  counter=Y`, marking top-align cases intentional. Batch 2 shipped 18 mismatches through
  instances into 37.

**Group 2: sizing.**
- Every frame vertical HUG; the only fixed height is an `mj-spacer`. Every FIXED width is a
  load-bearing case; every pinned width carrying text has 3.3.1 slack; each button's width
  sizing matches its intended mobile behavior (section 0). The wrapper itself is FIXED at
  the target email width, on the component AND on every placed instance (a FILL wrapper
  leaves the export math ambiguous; Phase 2 step 7).

**Group 3: geometry against foundations.** These compare numbers against foundations and the
audit, never against how the module looks:
- **Type: the WEIGHT as well as the size.** Every text node's family and style, checked against
  the audit's Brand foundations census, not merely against the ramp. A ramp can be internally
  flawless and uniformly wrong. The Ultimate EDS build shipped five text styles NAMED
  `P1/Regular`, `P2/Regular`, `P2/Italic`, `P3` and `P4` that were every one of them built in
  Inter **Light**, putting 271 text nodes, essentially every paragraph in the library, at 300
  weight against a source whose dominant body weight is Regular. Every structural check passed:
  the style existed, was applied, and was named correctly. The whole library read thin and washed
  out and no predicate said a word. **Assert that each style's name matches its own value**, and
  that the ramp's dominant body weight equals the dominant body weight in the source census.
- Module root at the audit's target email width; every type size, padding, and image
  dimension at email scale (0.6). On REFERENCE ONLY the check is that NO source measurement
  reached the module: ramp sizes, scale paddings, library content width, and a mismatch with
  the source's proportions is not a finding.
- Content width: the text-bearing column's resolved x/width equals the library content width
  from foundations, not the worker's number; multi-column rows sum columns plus gutters to it
  (0.3.1: the wrong number here reads as a text edge that moves while scrolling).
- Spacing system: every side padding, vertical padding, and gutter resolves to a value in the
  audit's Spacing system section, or to an audit-named exception. A value that resolves to
  nothing is a designer question, not a silent override (batch 2: thirty distinct side insets
  across twenty-eight modules). No mobile padding greater than 160px on a 320 viewport.
- Multi-column gutter present: a section with more than one column and zero horizontal column
  padding is a FAIL unless the source has a measured zero gutter AND the batch report says
  so. The content-width sum passes trivially at zero gutter, so this predicate exists
  separately (render spec 3.4.0 has the worked example; failure signature: adjacent
  headlines concatenate into one sentence).
- Group mobile shrink: per `mj-group` column, `resolved = columnWidth / groupWidth * (375 -
  mobile side padding)` must fit the longest unbreakable word times 1.05 (text) or the image's
  natural width (fixed-aspect image). A failing column needs one of 3.3.2's three
  restructures, not slack. Invisible on canvas and in desktop renders by construction
  (`CHA / NGI / NG`).

**Group 4: fills and bindings.**
- Every non-placeholder solid fill resolves to a variable binding from the audit's Palette;
  list unbound fills by node id with raw hex and intended role. **Test the binding, not the
  property.** Figma returns `boundVariables` as an empty object `{}` on an unbound paint, so
  `!fills[0].boundVariables` is `false` on every node alive and the check cannot fail. The
  working predicate is `!fills[0].boundVariables?.color`. The broken form reported "zero
  violations" on **242 solid-black fills across 41 modules**, five verifications running, on the
  Ultimate EDS migration; the customer found it in a screenshot. The fills were black because a
  binding helper had been passed already-prefixed token names, resolved them to `undefined`, and
  Figma returned the scratch placeholder paint unchanged. **A predicate that cannot fail is worse
  than no predicate, because it manufactures confidence.** Whenever you write a check, name the
  value that would make it fail and confirm that value is reachable.
- **Text-on-background contrast** for every text node against its nearest filled ancestor. One
  ratio catches black-on-black, white-on-white and inherited low contrast in a single pass; the
  242 black fills above and a white-on-white column both fell out of it immediately once it
  existed. Report anything under 3.0 with both hex values. **Never silently change a brand colour
  to fix one**: flag it with the measured ratio and the options, and let the designer decide. A
  button red quietly darkened for AA reads to the customer as a defect, not a courtesy. Placeholder grays for
  editable-image regions are the only exception, each named as intentional (batch 2: 43
  unbound fills, every downstream color change touched 31 nodes by hand).
- Component properties re-read and confirmed via `componentPropertyReferences`. **Every
  customer-facing text node (headline, eyebrow, subhead, body, button label) is reachable
  through a module-root TEXT property**; list by node id any that is not, with boilerplate
  (legal, address, unsubscribe) and link-bearing text (binding wipes hyperlink ranges) as
  the only allowed exceptions. A module whose only
  text-bearing nodes are boilerplate legitimately has none. If the module contains any
  button, the label property is named `Button label` / `Card N button label`; a label living
  only on the foundation component fails.
- **No `mj-group` carries a fill of its own.** The exporter's dark CSS erases section and
  column fills to transparent but never touches a group's own fill, so a filled group ships
  forced-white text on its original fill the moment a client flips to dark (render-spec 3.3). Band fills live on the group's columns; list any filled
  group by node id as a FAIL.
- Module root is a direct child of its category page, not inside a component set or Figma
  section, no stray instances loose on the page.
- Concession honored where the row carries one: Two Column Swap built per 3.4.1 (FIXED
  columns summing to the content box, slack on the text pin, image at column content width
  and natural aspect, no group, nothing flattened, overlap not reproduced by other means).

**Group 5: mobile data.**
- Every multi-column section has its step 3 Part A stacking decision recorded.
- Part B keys present AND from the observed schemas only: `fontSize` + `fontSize_mode` on
  every TEXT node, `isPaddingActive` beside every mobile padding, 28px bottom on every
  non-last stacking column. A mobile padding without its flag, or a font size on the frame
  instead of the TEXT node, is a FAIL that reads back perfectly, which is why step 6's batch
  render exists.
- Range hygiene: every text node returns ONE segment from
  `getStyledTextSegments(['lineHeight'])`; a second segment is a detached frozen line height.

**Group 6: asset identity.** An image fill, on a correctly tagged node, at exactly the right
dimensions, passes every group above and can still be the wrong picture.
- **Same dimensions never means same asset.** Libraries ship a light-band and a dark-band
  colourway of one logo at identical pixel sizes. For every image node, compare the asset's own
  luminance against its nearest filled ancestor and FAIL a light mark on a light band or a dark
  mark on a dark band. The Ultimate EDS migration shipped this **three separate times**: a white
  wordmark across six light-band headers, then again on a footer logo after the first had been
  written up as a lesson. Writing the lesson down did not catch the repeat; a predicate would
  have.
- **Match the icon SET, not just the icon size.** A source can carry the same five social
  platforms twice, as bare glyphs at 20px and as circled outlines at 42px. Reusing the circled
  set at 20px renders as faint rings and reads as unfinished. Check which set the source uses
  AT THAT NODE rather than placing a plausible icon of the right size.
- **Sprite sheets.** A source that shows two app-store badges through two cropped rects yields
  ONE raw image on download. Compare the raw asset's aspect ratio against the node's before
  placing it; a large mismatch means it is a sheet, and it should be split at its transparent
  gutter rather than stuffed whole into one node.
- **`upload_assets` may ignore `nodeId`** and drop the image as a loose frame on a page. Always
  read `placedOnNodeId` in the POST response; when it is not your node, take the returned
  `imageHash`, set the fill yourself, and delete the stray frame.
- **Never hand-transcribe image bytes between files.** Use `download_assets` then
  `upload_assets`; a hand-copied base64 logo shipped as a 651-byte broken PNG rendering black.

**Then one screenshot per module: the desktop visual check.** Screenshot the rebuild next to the
source screenshot from step 1; flag divergences rather than silently accepting them. **This is
per module and it does not become optional as batches speed up.** The single largest quality
failure on the Ultimate EDS migration was that screenshots stopped after batch 2 in favour of
read-back checks alone, and read-back verifies what you wrote, not what a person sees: both the
242 black fills and a white-on-white column were invisible to structure and instant in a picture.
Batch 9 is when this matters, not batch 1. On REFERENCE
ONLY, read the comparison for content and structure only (margins, type sizes, and spacing
are expected to differ; listing them buries real divergences). **On a module 20-40px taller
than the source, do not eyeball a nudge:** detect the content bands (runs of non-canvas
pixels) in both PNGs, diff, and derive exact padding corrections; the deterministic two-pass
loop got 24 of 28 batch 2 modules onto their source height.

The mobile render check runs once per batch, not per module: step 6.

### 6. Batch checks: export sniff + mobile render (once per batch)

Everything in step 5 is a Figma-side check. The plugin's exporter is what decides whether a
group overflows, whether a button goes full width, whether an image scales, and no other step
in this phase looks at its output. A batch that passes every Figma check can still ship with
mobile defects that only exist in the exported HTML: on batch 2 this ate five rounds of
design review, each spent reverse-engineering exporter behavior by pixel-measuring preview
PNGs, when one export read would have surfaced the group overflow, the button width and the
fluid-image behavior together in the first batch. And three of four batch 4 corrections were
mobile-only, every one caught by the customer manually exporting screenshots; the customer
should not be the mobile test harness when there is a headless render for it.

Both checks below share one precondition: **upload the batch's wrappers to the plugin library
provisionally** (a QA upload of just this batch is fine; the full send-readiness pass happens
at hand-off). The order matters on a migration: build the batch, upload provisionally, run
these checks, only then open the next batch. A construction mistake found at batch 1 is one
fix; found at batch 5 it is five.

**Check A: the mobile render. Render it, do not reason about it.** Figma's canvas has no
mobile breakpoint, so `get_screenshot` at 390px just renders desktop-shaped pixels at 390px,
not the plugin's mobile treatment; that check silently degrades to a recorded stacking
intention. Instead, compose a test email from the batch's uploaded modules and call
`emaillove_preview_email` on the compose token; the response carries desktop and mobile
renders from the exporter. Diff the mobile view against the source's mobile design (or the
source screenshot where none exists). **Fail the batch on any of these**, each invisible on
the Figma canvas and in a desktop pair:

- a word broken mid-string (the section 3.3.2 group-shrink defect)
- an image whose aspect ratio differs from the desktop view (same class)
- a stacked column still carrying its desktop gutter as an indent
- a section that stacked where step 3 Part A recorded a group decision, or grouped where it
  recorded stack

Then walk every multi-column section on the mobile render and confirm its actual behavior
matches the step 3 Part A decision.

**Check B: the export sniff.**

- **Pick one representative module.** A multi-column one is best, because mobile behavior
  lives in the columns; if the batch has both a header lockup and a card row, pick the card
  row. On a batch with only single-column modules, pick the one carrying the button, since
  the full-width mobile button is the other common exporter surprise.
- **Export it to HTML, headless first.** Call `emaillove_export_figma` with the target
  file's key and the module wrapper's node id, `operationType: "preview"`: it compiles
  through the production /getHtml pipeline without charging export quota, and its output is
  golden-diffed against real plugin exports on every worker deploy, so the HTML you read IS
  the exporter's HTML. It takes a bare mj-wrapper directly (no temporary email frame), and
  returns the HTML plus a token `emaillove_preview_email` accepts for a per-module mobile
  render. On a CoverageError (mj-hero, mj-social, mj-navbar, mj-table), or when the tool is
  not on the MCP, fall back to the plugin click: drop an instance of the module wrapper into
  a temporary email frame on Campaigns (foundations built one in Phase 2 step 7), select the
  frame, and click Export in the plugin, asking the user to drive the click if you cannot.
  Save the HTML alongside the batch report either way.
- **Read the HTML and confirm four things**, none of them expensive:
  - **Body width** matches the target email width from foundations. A 600 build that exports
    at 640 (or vice versa) is a Figma-side wrapper-width mistake that step 5's wrapper check
    should have caught, and the sniff test is where it does when it did not.
  - **`@media only screen and (max-width` block is present.** Its absence means the mobile
    treatment is empty; every mobile stacking or fluid-image behavior lives inside it, so a
    module without it renders desktop-only on phones regardless of what the Figma decision
    said.
  - **Mobile classes exist for anything that should stack or go full width.** A column that
    step 3 Part A decided should stack has a `mj-column-per-100` or the equivalent width rule
    inside the media query. A button set to full-width mobile has the `mj-b-full` class or
    the exporter's current equivalent. An empty media query on a module that step 3 recorded
    a stacking decision for is a fail.
  - **Column widths add up.** For each `mj-section`, the column `width` attributes plus any
    gutters should sum to the intended content box, and no single column should exceed the
    body width. A `mj-group` that overflows is visible here as a per-column width sum that
    exceeds the section content width, and that is the failure mode batch 2's footer had
    for five rounds before it was caught.
- **Record the four confirmations in the batch report** with the module name you sniffed. On
  a fail, do not open the review: fix the defect on the Figma side (that is where the export
  is generated from), re-export, re-read. A batch that ships with a known exporter defect
  costs a design-review round per module the same defect touches; the sniff is what stops
  that from happening.
- **The batch checks are not a replacement for step 5**; they are a second pass on a
  different artifact (the exporter's output rather than the Figma tree). A batch that passes
  both is much less likely to surface a mobile defect at design review. A batch that passes
  step 5 alone is batch 2.

**When a check cannot run in-session (no `emaillove_export_figma` on the MCP and no human to
click, or a CoverageError module with no human available), do not mark it skipped and move
on.** Accumulate
a **Deferred verification list** across every batch, one line per module naming the specific
thing that needs confirming (this group must not stack, this button must go full width, this
image must stay fluid), and hand it over as a single checklist at step 7. One human session
against a concrete list is recoverable; a hand-off that merely says "checks not run" is not.
The two defects a human-run batch check caught on a real library (a bordered group whose
columns summed past 100 percent, and a nav label wrapping from font drift) were both
invisible to every arithmetic check in step 5, which is why the deferral must stay loud,
and why every report writes a deferred exporter check as a STATE (`exporter: deferred`),
never folded into a pass.

**Repair discipline, when any check or render fails.** Measure the failure first (which
node, which breakpoint, which mechanism) before changing structure; a fix applied to an
unmeasured symptom is a guess. A change the rendered output has disproven is not tried
again somewhere else. After two local patches on the same module, stop patching and
reconstruct the module from its source inventory: patch accumulation is how a module
drifts from the source and the spec at once, and a full reconstruction from a good
inventory is usually cheaper than the third patch. Repairs preserve what already works:
re-read `componentPropertyReferences` after any structural repair and compare the property
count against the pre-repair count, because a rebuild that silently drops bindings passes
every geometry check. Keep the batch's resumable record current throughout (node ids,
outstanding checks, last verified state per module), so an interrupted session resumes
instead of re-verifying or, worse, re-trusting.

### 7. Batch report and gate

One report per batch: per module, keyed by its Module inventory row name, what was rebuilt, the
design you converted it from, verdict honored or changed (with reason), any concession and
whether it was accepted and by whom (and for a bleed concession, the two column widths you landed
on, so a reviewer can check the sum), mobile decisions, divergences flagged, component properties
added and the evidence for each, the category you kept or changed. **Open with the Group 0 parity table: for every module in the batch, the source `T/I` content
census from its inventory row beside the built counts, and a blank column where they agree.** A
batch with any unexplained row does not pass the gate, whatever the other five groups say. This
goes first because it is the only line a reviewer can check against their own file without
opening yours, and because a report that opens with "zero violations" from internal checks alone
is how a library reaches 180 modules with 26 of them silently wrong. **Every module row then
carries its verification as a component-by-breakpoint acceptance matrix**: one keyed row per
module x breakpoint (desktop, mobile) x check (canvas, structure, exporter), each `pass`,
`fail`, `deferred`, or `missing` - `deferred` means the check was consciously postponed and
names what postpones it; `missing` means the batch never covered it, and a matrix with a
`missing` row does not pass the gate. Duplicate rows for the same module+breakpoint+check are a
report defect. A module is complete only when every required row is `pass`; `exporter:
deferred` is a state, never a pass, and "fixed" for a change no render has seen is the
completion-inflation failure this matrix exists to stop. A component or breakpoint absent from
the supplied renders is NOT tested - write `deferred` or `missing`, never infer a pass. Then **the source fidelity
tier, the target email width, and the content width the batch was built at, plus the scale factor
where one applies**, so a reviewer can check three or four numbers instead of measuring modules. On a
REFERENCE ONLY source, open instead with the tier and the standards, and repeat the one sentence that
the geometry is ours: a batch report is the document a reviewer reads with the source file open
beside it, so it is exactly where the difference gets mistaken for a defect. Name every module whose worker side margin you overrode
to reach the content width (plus the re-derived column sum where the module was multi-column). End with the open questions for the design review. Do not start the next batch
until the user says the review happened.

When the `figma-quality-gates` skill is installed, run it as an independent acceptance pass
over the batch before the design review: its machine-readable audit snapshot and validator
catch deferred-export completion claims, non-IMAGE fills, unsafe group geometry, and
incomplete BOOLEAN properties mechanically, and its verdict is evidence for the review, not
a replacement for it.

## Hand-off after the final batch

### Send-readiness pass on every campaign

**Before hand-off, walk every campaign root on the Campaigns page and confirm each is safe
to send.** A migration that ships modules the plugin can render but campaigns that will fail
in a real inbox is not done. The batch 2 Codex review found this exact gap on a delivered
file: three campaign roots, zero shared `href` values, zero shared `altText`, blank subject
and preheader on all three, one campaign root with a blank `lightThemeBackgroundColor`,
placeholder legal copy and the literal word `Address` in the footer. Fix every violation
before the hand-off conversation, and list each by node id in the batch report.

For every `mainFrame` campaign root, confirm:

- **All nine theme keys are populated with real values**, not empty strings (`backgroundColor`,
  `contentColor`, `textColor`, `linkColor`, `buttonTextColor`, `buttonContentColor`,
  `lightThemeBackgroundColor`, `fallBackFontName`, and the `nodeType = 'mainFrame'` marker
  itself). The six theme keys hold DARK MODE values (the audit Palette's dark proposal or
  the house dark defaults), never the light palette repeated; `lightThemeBackgroundColor`
  holds the light body background. See the Phase 2 inline key table for what each value
  should look like.
- **`emailSubject` and `emailPreHeader` are non-blank** and are real copy, not the module
  name or a `TODO`. A campaign whose subject reads `Campaign, Full library proof` or blank
  reaches an inbox with that string in the preview pane.
- **`fallBackFontName` is a single font family name**, not a CSS stack. `Arial` is correct;
  `Arial, Helvetica, sans-serif` is not (the plugin's export treats the whole string as one
  font name and picks a fallback that never matches). Standardise on one value across every
  campaign root in the file.
- **The campaign root has a specific, non-generic name.** A root literally named
  `EmailLove` or `Campaign - Full library proof` reads as a valid reusable template when it
  is really a scratch composition; rename QA roots with a `QA only, do not send` prefix, or
  move them off the Campaigns page.

For every `mj-image` node inside every campaign, confirm:

- **`href` is a real URL or explicitly empty for a decorative image**, not the string
  `#` and not absent-because-nobody-set-it. Record which images are deliberately unlinked so
  a reviewer can tell "no link" from "forgot the link".
- **`altText` is meaningful copy or empty for a decorative image**, again not
  absent-because-nobody-set-it. The default of "empty because Figma did not surface a value
  to set" is not accessible.

For the footer:

- **No placeholder legal text**, no `Lorem ipsum`, no literal string `Address`. Every
  campaign the customer sends has a real postal address, a real company name, and a real
  unsubscribe mechanism (usually a merge tag their ESP resolves). A migration that leaves
  `Address` as the footer contents ships an email that CAN-SPAM violates.
- **The unsubscribe link is present** and points at either the magic value `unsubscribe.com`
  (the exporter substitutes the ESP's merge tag at export time, and this is the default the
  design system should carry so it stays ESP-portable), or a merge tag the customer explicitly
  asked for (`{{unsubscribe_url}}`
  or the ESP's equivalent) or a real URL, not `#`.
- **No unlinked preference wording.** Text containing "preference(s)" with no
  hyperlink gets the `manage-preferences.com` placeholder injected at export,
  and only Klaviyo swaps it for a merge tag; every other target ships a live
  third-party link. Link it explicitly (the magic-value table in Phase 3 step 2
  has the decision).

List every violation by node id in the batch report under a "Send-readiness violations"
heading. Empty list is the only pass. On a fail, either fix the violation (populate the theme
key, add the alt text, rewrite the footer, rename the root) or record it as a deliberate
"this campaign is a QA scratch, will not send" decision and rename the root accordingly.
Do not open the hand-off conversation with the customer until this pass is clean.

### Hand-off itself

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

This is version 1.46.0 of this skill. If you have web access, check once per conversation
(quietly, without narrating it) whether a newer version exists: fetch
https://raw.githubusercontent.com/email-love/claude-skills/main/.claude-plugin/marketplace.json
and compare this skill's own version to the entry named `emaillove-eds-converter` (the legacy name this skill is versioned under, kept in that file deliberately). That file lists each skill's current
version, so the check stays correct no matter which skill released most recently; the old
repository-wide latest-release check reported whichever skill shipped last, which could be a
different skill entirely. If a newer version exists, mention it once at hand-off with the right
update path for the user's surface: claude.ai users re-upload the .skill file from the newest
release, which attaches all four bundles, and Claude Code plugin users run the marketplace
update. If you have no web access, skip this silently.
