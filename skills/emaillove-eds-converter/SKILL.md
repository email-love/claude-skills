---
name: emaillove-eds-converter
description: Convert an audited legacy Figma design system into a working Email Love design system, foundations first, then modules in batches with design review between batches. Use this skill whenever the user wants to convert, rebuild, or migrate their existing Figma email templates to the Email Love structure, run foundations, or convert a batch of modules, after the emaillove-migration-audit skill has produced their audit report. The audit report is required input; if it does not exist yet, run the audit first.
---

# Email Love EDS Converter

Convert an audited legacy design system into a working Email Love design system. This skill
follows a migration audit (the emaillove-migration-audit skill produces it) and works in two
phases: foundations once, then modules in batches. A designer reviews between batches; never
convert the whole library in one unreviewed pass.

Prefer to have this done for you? Email Love's team runs this exact process, with design
review included, as part of Enterprise onboarding: hello@emaillove.com.

Two hard rules:

- **The customer's source file is read-only, always.** All building happens in a separate
  target file. Reads from the source are inspections, screenshots, and asset downloads only.
- **The audit report is required input.** It carries the per-module classification (A/B/C/D plus
  any named concession), the scale factor, the brand foundations, and the flags. Do not re-derive
  what it already settled; do re-verify anything that looks wrong when you meet the actual nodes.

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
  constraints bind how that module is built (Phase 3). This is what Phase 3 iterates over. There
  is no per-design conversion pass: the report's Per-design roll-up is context for the customer,
  not a work list.
- **Scale factor** (required in the report): the number every geometry decision is divided by.
  Read it; never re-derive it (see Phase 2).
- **Brand foundations:** the type ramp on email-safe fallbacks, the proposed theme colors, the
  spacing scale, the button styles, and the target email width. Phase 2 builds from these.
- **Flags:** the gates. Two of them block work rather than describe it: the scale factor when
  the audit's two derivations disagreed, and each named concession. Both need a human "yes"
  before the affected modules get built.

If the report has no Module inventory or no Scale factor, it predates this contract. Do not
improvise a module list out of a per-design table: go back and run the audit skill again, which
is minutes of work and saves rebuilding a batch against the wrong boundaries.

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

## Phase 2: Foundations (run once per customer)

**Everything you build, here and in Phase 3, is at email scale.** Take the factor from the
audit's Scale factor section and divide the source numbers by it: type sizes, widths, paddings,
image dimensions. Do not re-derive the factor from the file, even when the arithmetic looks
obvious to you: the audit computed both derivations, and where they disagreed a human chose
between them, so a fresh derivation here quietly overrules that decision. When the audit says
the factor is still a designer decision and nobody has confirmed it, get the yes before you
build, because the factor changes every module. State the factor you built at in the foundations
report, so batch 1 and every batch after it inherits one number.

Build the scaffold every later batch depends on:

1. **Pages**, following Email Love library conventions: a Cover, one page per category the
   audit's Module inventory uses (Heroes, Single Column, Lists, and so on), Buttons, Type,
   Campaigns.
2. **Type mapping.** Recreate the customer's type ramp as Figma text styles in the target
   file using their email-safe fallback choices from the audit (never the unlicensed brand
   font unless the user confirms web-font hosting). Name styles as the customer named theirs.
   Use the email sizes the audit's Brand foundations table already computed at the scale
   factor, not the authored source sizes.
3. **Buttons page.** Rebuild each of their button styles as a component: correct email
   construction (a styled frame with a single text node), not their app-style nested
   instances. These become the sub-components nested inside mj-button-Frames, and they are
   the INSTANCE_SWAP targets for module-level "Button Style" properties later. Put the
   label's TEXT property on the button component itself: a label living inside a nested
   instance cannot be bound from the module that uses it (render spec, section 8.5).
4. **Spacing.** Recreate their spacer scale as components if they had one, at the email-scale
   values from the audit.
5. **Assets.** Export the logo and any recurring imagery from the source file
   (download_assets) and upload into the target file (upload_assets). Logos become images,
   never vectors. Export the RENDERED node every time, never the raw image fill behind it: a
   source fill with `scaleMode: 'CROP'` loses its crop the moment you take the underlying
   asset, and you get the whole photograph instead of the picture the designer composed
   (render spec 4.2.1, which also has the aspect-ratio rule).
6. **Root EMAIL TEMPLATE frame** on Campaigns at the audit's target email width (600 or 640,
   never the source canvas width when the source was not at email scale): vertical
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
7. **Report** what was built, the scale factor and target email width you built at, what the
   audit proposed that you changed, and what needs the designer's eye before batch 1 (theme
   colors especially: they are a proposal until a human confirms).

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
reviewer can tell your boundary from the audit's. Build every number at the audit's scale factor, dividing source pixels by it as you go
(Phase 2 has the rule; render spec section 0.6 has it at the geometry level).

Before building any module whose inventory row carries a concession, check the audit's Flags for
a human "yes" on it. If there is none, ask, and record the answer in the batch report. Building
first and asking later means rebuilding.

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
   **Size the export so the PNG comes back at the target email width**, which means exporting a
   source at scale factor 2.2 at roughly 0.45x. The worker infers its numbers from the pixels
   you send it, so a PNG already at email scale returns email-scale widths, paddings, and type
   sizes, and the render spec's rule that worker values are authoritative stays true as written.
   If you did send a source-scale PNG, its numbers are authoritative only at that scale: divide
   every one of them by the factor before it becomes geometry, and say in the batch report that
   you converted that way.
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
- Images: one image fill per `mj-image-Frame`, assets round-tripped from the source file.
- Buttons: `mj-button-Frame` wrapping an instance of the foundations button component.
- **Honor the inventory row's verdict.** Verdict A: live text throughout. **Verdict
  `A (concession: ...)`: build it as live text like any other A and apply the named substitute,
  nothing more.** Do not quietly reproduce the effect the concession gave up, in an image or
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
- Scale: the module root is at the audit's target email width, and its type sizes, paddings, and
  image dimensions are at email scale rather than source scale (render spec section 0.6). A
  module built at source scale looks correct in isolation and wrong the moment it sits next to
  another module, so check it before the batch grows.
- Naming: every layer carries the display name for its tag, and no friendly string leaked
  into the plugin data `name` key.
- Component: the module root is a direct child of its category page, not inside a component
  set or a Figma section, with no stray instances of it left loose on the page. Every property
  binding re-read and confirmed.
- Visual: screenshot the rebuild next to the source screenshot from step 1; flag
  divergences rather than silently accepting them.
- Mobile: list the mobile keys you set per node.

### 6. Batch report and gate

One report per batch: per module, keyed by its Module inventory row name, what was rebuilt, the
design you converted it from, verdict honored or changed (with reason), any concession and
whether it was accepted and by whom, mobile decisions, divergences flagged, component properties
added and the evidence for each, the category you kept or changed. Open with the scale factor and
target email width the batch was built at, so a reviewer can check one number instead of
measuring modules. End with the open questions for the design review. Do not start the next batch
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

This is version 1.12.0 of this skill. If you have web access, check once per conversation
(quietly, without narrating it) whether a newer version exists: fetch
https://api.github.com/repos/email-love/claude-skills/releases/latest and compare the tag. If a
newer version exists, mention it once at hand-off with the right update path for the user's
surface: claude.ai users re-upload the .skill file from that release, Claude Code plugin users
run the marketplace update. If you have no web access, skip this silently.
