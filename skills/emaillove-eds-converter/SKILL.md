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
- **The audit report is required input.** It carries the classification (A/B/C/D), the brand
  foundations, and the flags. Do not re-derive what it already settled; do re-verify anything
  that looks wrong when you meet the actual nodes.

## Inputs

1. The migration audit report (file or pasted).
2. The source Figma file link (read-only).
3. The target file: an existing one the team designates, or create one named
   "[Customer] — Email Love Design System" via the Figma MCP.
4. Which batch to run: "foundations", or a named batch of modules ("batch 1: the 5 modules
   listed in the audit's recommended next step", or an explicit list).

## Phase 2: Foundations (run once per customer)

Build the scaffold every later batch depends on:

1. **Pages**, following Email Love library conventions: a Cover, one page per section
   category the audit found (Heroes, Copy Blocks, Lists, and so on), Buttons, Type,
   Campaigns.
2. **Type mapping.** Recreate the customer's type ramp as Figma text styles in the target
   file using their email-safe fallback choices from the audit (never the unlicensed brand
   font unless the user confirms web-font hosting). Name styles as the customer named theirs.
3. **Buttons page.** Rebuild each of their button styles as a component: correct email
   construction (a styled frame with a single text node), not their app-style nested
   instances. These become the sub-components nested inside mj-button-Frames.
4. **Spacing.** Recreate their spacer scale as components if they had one.
5. **Assets.** Export the logo and any recurring imagery from the source file
   (download_assets) and upload into the target file (upload_assets). Logos become images,
   never vectors.
6. **Root template frame** on Campaigns at the customer's email width: vertical auto-layout,
   the shared marker, and the six theme colors from the audit's proposal:
   `setSharedPluginData('emaillove', 'nodeType', 'mainFrame')` plus backgroundColor,
   contentColor, textColor, linkColor, buttonTextColor, buttonContentColor.
7. **Report** what was built, what the audit proposed that you changed, and what needs the
   designer's eye before batch 1 (theme colors especially: they are a proposal until a human
   confirms).

## Phase 3: Module conversion (run per batch)

For each module in the batch, in order:

### 1. Rebuild the desktop frame as Email Love structure

Work from the source design's structure and a screenshot. In the target file, build the
module as a component with correct export structure:

- Structural frames named exactly (`mj-section`, `mj-column`) or carrying the tag in the
  `name` shared plugin data key with a human layer name.
- **Content leaves are tagged PAIRS, wrapper plus inner node.** `mj-text-Frame` contains a
  text node tagged `mj-text`; `mj-image-Frame` contains the image rectangle tagged
  `mj-image`; `mj-button-Frame` contains a node tagged `mj-button` whose own direct child is
  a TEXT node. Tagging only the wrapper is the single most damaging mistake in a conversion:
  untagged inner content is not skipped, it is flattened into a hosted PNG by the exporter's
  unknown-node path, so buttons silently lose their text and links and image sections can
  export empty. After building each module, verify every leaf pair before moving on.
- **Build the pair, do not style the wrapper.** The wrapper carries layout; the inner node
  carries content. An image is an `mj-image-Frame` containing a rectangle whose fill is the
  image, never a frame with an image fill on itself. A divider is an `mj-divider-Frame`
  containing a line, never a frame with a solid fill. Childless wrappers export as empty
  cells. Legacy designs almost always express images and rules as fills on a frame, so this
  is the most common thing you must actively restructure rather than copy.
- **A badge, pill, or icon sitting beside text is an `mj-group`, not a loose frame inside
  `mj-text-Frame`.** A loose frame there flattens to an image and detaches from the text.
  Rebuild it as a group inside the section: `mj-group` containing one `mj-column` for the badge
  (its pill styling becomes the column's background colour and corner radius, with live text
  inside) and another `mj-column` for the adjoining text. Size those columns in **percentages,
  not pixels**, and remember the group must be a child of the section, not of a column, so a
  design that nests such a row inside a column needs the row lifted to section level. Only fall
  back to treating the region as an editable image when the composition is genuinely
  inseparable.
- Map every text node to the type styles from foundations.
- Images: one image fill per `mj-image-Frame`, assets round-tripped from the source file.
- Buttons: `mj-button-Frame` wrapping an instance of the foundations button component.
- Verdict B regions (from the audit): place the design content as a frame with NO
  recognized tag name inside a column; the exporter flattens it to a hosted image at export
  while it stays editable. Verdict C modules: live-text structure for the copy, one
  editable-image frame for the rich region.
- Text over a single background photo is mj-hero territory, live text, not an image.

### 2. Merge the mobile twin

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

### 3. Componentize, add properties, and pre-tag

Make the finished module a COMPONENT on its category page.

**Add component properties for the parts a marketer will change.** Derive them from evidence
in the source library rather than adding them everywhere: if a region appears in some variants
of this module and not others, that is a BOOLEAN bound to `visible`; the headline, body, and
button label are TEXT properties bound to `characters`; a genuine style choice (button
variant, icon) is an INSTANCE_SWAP. Because the plugin exports what is visible, a boolean that
hides a region removes it from the sent email. Four good properties beat twenty; a cluttered
panel gets ignored. Record the properties you added, and why, in the module's report line.

```js
const showBtn = comp.addComponentProperty('Show Button', 'BOOLEAN', true)
ctaFrame.componentPropertyReferences = { visible: showBtn }
const headlineProp = comp.addComponentProperty('Headline', 'TEXT', textNode.characters)
textNode.componentPropertyReferences = { characters: headlineProp }
```

Then tag it for saving into the plugin. **Use the customer's real category names**, which are
whatever sections already exist in their plugin, not names you invent. If the Email Love MCP is
connected, `list_components` returns their categories; otherwise infer from their library page
names or ask. Classify by what the component structurally is: **Hero** for a top-of-email
feature block, **Single Column** for one full-width stack, **Multi-Column** for side-by-side
columns, **Receipt** for line-item layouts, **Image** for image-only blocks. When nothing fits,
choose the closest existing section and note it, rather than inventing one.

```js
node.setSharedPluginData('emaillove', 'saveCategory', 'Hero')
node.setSharedPluginData('emaillove', 'saveName', 'Hero — text led, portrait')
```

Record the category you chose per module in the batch report, so a human can correct any
misfits in one pass rather than hunting for them later.

### 4. Verify per module

- Structural checklist: naming or metadata resolves on every structural frame; content in
  element frames; no detached instances; no unrecognized frames except intentional
  editable-image regions.
- Visual: screenshot the rebuild next to a screenshot of the source design; flag divergences
  rather than silently accepting them.
- Mobile: list the mobile keys you set per node.

### 5. Batch report and gate

One report per batch: per module, what was rebuilt, verdict honored or changed (with reason),
mobile decisions, divergences flagged, save tags applied. End with the open questions for the
design review. Do not start the next batch until the user says the review happened.

## Hand-off after the final batch

The design system is on the canvas but not yet in the plugin. Walk the user through saving
each pre-tagged component (or the bulk import, once the plugin ships it), then: sync check in
the plugin, build one real sample email from the new components as proof, export it, and send
a seed test. Building is free; exports count against plan limits.
