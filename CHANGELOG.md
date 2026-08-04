# Changelog

User-visible changes to the Email Love Claude skills, newest first, by skill. Versions are
independent per skill. Every release attaches all three `.skill` bundles.

## Repo: plugin restructure (2026-08-03)

The three skills now ship as ONE Claude Code plugin, `email-love`, at
`plugins/email-love/`. One install carries all three, namespaced
`/email-love:migration-audit`, `/email-love:eds-converter`,
`/email-love:figma-builder`:

```
claude plugin marketplace add email-love/claude-skills
claude plugin install email-love@email-love
```

- Skill directories moved to `plugins/email-love/skills/{eds-converter,
  migration-audit,figma-builder}`; frontmatter `name:` fields renamed to the
  short names (the frontmatter name determines the invocation name, so the
  doubled `/emaillove-eds-converter:emaillove-eds-converter` namespace is gone).
- Skill descriptions untouched: they drive automatic invocation and were tuned
  for trigger accuracy.
- **Three legacy shim entries stay in marketplace.json under the old names**,
  pointing at the moved directories as deprecated single-skill plugins. Old
  marketplace installs keep resolving and updating, and every shipped copy's
  "Staying current" check keeps working (each SKILL.md now names its legacy
  entry explicitly). Shim versions stay synced with each SKILL.md's own version
  line, in the same commit, every release.
- Per-skill `.claude-plugin/plugin.json` files removed: skill directories stay
  plain (SKILL.md + references) so they read as skills inside the bundle AND as
  single-skill shim plugins without conflict. The bundle carries the one
  plugin.json.
- `.skill` release bundles keep their legacy `emaillove-*` names (release asset
  URLs, docs links, and uploaded claude.ai copies know those names); a plugin
  ships its whole directory, so the missing-references failure class is
  structurally gone for plugin installs.
- validate_repo.py reworked for the new layout (bundle + shim validation, shim
  version sync, stale-URL detection); build.sh and CI updated; .gitignore paths
  updated so workspace directories stay excluded.
- Plugin version starts at 1.0.0 (new distribution shape). Per-skill versions
  continue in each SKILL.md and its shim entry.

## emaillove-figma-builder

### 2.9.2
- A "Which model to run this with" note: strongest model for Path B (and for the
  migration-audit/eds-converter skills), a faster model for routine Path A campaign builds once a
  design system is already synced and verified.

### 2.9.1
- The downloadable bundle now carries the stop-and-resume rules that shipped after 2.9.0.
- The update check reads `marketplace.json` rather than the repo-wide latest release, so a
  builder no longer compares itself against another skill's release.

### 2.9.0 and earlier (same day)
- Announce when you stop: report completed work, what remains, why, and how to resume, in the
  same message. Do not stop between the sections of one email.
- Two build paths made explicit: instance a published design system, or generate structure
  through AI Import and transcribe it. Never hand-author structure.
- Path B derives the source scale before converting, and states the content width once.
- Progress reporting with counts, a named section, and an estimate revised from observed pace.
- Runtime expectations stated up front, so a normal multi-section build does not read as a hang.

## emaillove-eds-converter

### 1.37.0
- **Customer-facing copy gets TEXT properties BY DEFAULT** (batch 7, first finding from the
  plugin shakedown migration). The old rule gated TEXT properties on evidence the copy
  changes between sends, which worked on multi-design sources and starved single-design
  sources to zero: on a one-design shakedown, no text node anywhere had "changes between
  sends" evidence, so a rule-following agent added no text properties at all, module after
  module, and the library shipped read-only from the property panel. That contradicts the
  Getting Started page, which tells marketers text is edited through component properties.
- New default: headlines, eyebrows, subheads, body copy, and button labels get TEXT
  properties without needing evidence; only boilerplate a marketer should not touch per
  send stays unbound (legal, postal address, unsubscribe line). The evidence gate now
  applies only to BOOLEANs (sibling design with the region absent) and INSTANCE_SWAPs
  (a real variant to swap to). Working range widens to two to seven properties; zero is
  legitimate only for a module with no customer-facing copy at all.
- Step 5 Group 4 predicate updated to enforce it: every customer-facing text node reachable
  through a module-root TEXT property, violations by node id, boilerplate excepted.
- Images unchanged and correct as-is: Figma has no image component-property type; imagery
  is edited by replacing the rectangle's fill (the batch 3 Getting Started correction).
- Bumps to 1.37.0 (minor: default inversion for TEXT properties).

### 1.36.0
- **Phase 3 verification consolidated: one read-back pass per module, batch checks hoisted.**
  Step 5 had grown to seventeen prose checks across six defect-fix batches, each written as
  its own walk of the tree. Same coverage, restructured: read the built module back ONCE
  (one dump per node: type, layout, axes, paddings, resolved geometry, fills and bindings,
  plugin data, property references, line-height segments), then evaluate five predicate
  groups locally (shape and tags, sizing, geometry against foundations, fills and bindings,
  mobile data), listing violations by node id. One screenshot for the desktop visual check.
  Every measured case and rationale preserved in compressed form; no check dropped.
- **Step 6 is now "Batch checks": the mobile render joins the export sniff.** Both share the
  provisional-upload precondition, so they run as one flow once per batch. The mobile render
  (`emaillove_preview_email`) was written per-module in step 5 but always operated at batch
  level; it now lives where it runs.
- **Small-library single-batch allowance.** A library of 8 or fewer modules may run as ONE
  batch with one design review before upload; the batch structure exists to stop defects
  propagating across batches, and a single batch has nothing to propagate into. Above that,
  roughly five modules per batch stands: batch 1 always surfaces something.
- Motivation: Figma round trips are the conversion's stated bottleneck, and a seventeen-item
  list of separate walk instructions either costs N walks or gets skimmed. One walk, local
  evaluation, same teeth.
- Bumps to 1.36.0 (minor: verification restructure, no coverage change).

### 1.35.0
- **Mobile styles are now a first-class output, with VERIFIED plugin-data schemas** (batch 6,
  from a live migration on 2026-08-03). New "Mobile Styles ARE shared plugin data" section in
  Phase 2 replaces the batch 2 claim that mobile padding was node properties, which live
  observation disproved. Two schemas, both read back off nodes AFTER the plugin's own Mobile
  Styles tab wrote them: Schema A containers (`mobileStylesPadding*` + `isPaddingActive`,
  values inert without the flag) and Schema B type (`fontSize`/`lineHeight`/`letterSpacing` +
  `<prop>_mode='override'` on the TEXT node, not the frame). New hard rule: **never write a
  plugin-data key you have not observed the plugin itself write**; an invented activation flag
  switched a control on at its default and shipped 10px body copy.
- **Phase 3 step 3 Part B rewritten: "write the mobile styles" and it ALWAYS runs.** The old
  Part B fired only when the source had a mobile twin, which on a typical migration means
  never, and the result was a library correct at 640 and unreadable at 375. Per module: mobile
  font size on every TEXT node from the audit's ramp, no mobile line heights (percentages ride
  the size), mobile padding with its flag, 28px mobile bottom padding on every non-last
  stacking column (the desktop gutter is horizontal and vanishes on stack), visibility and
  alignment per the audit. Read-back is necessary but not sufficient; only a render verifies.
- **Line heights in every text style are PERCENT, never PIXELS.** A percent scales with the
  font size at every breakpoint; a pixel value freezes (measured: 17px mobile copy on its
  desktop 33px line box, double-spaced). Plus the `setRangeFontName` detachment trap: a bold
  range detaches from its style and freezes its old line height; re-apply with
  `setRangeLineHeight` and verify one segment.
- **Dark mode: the six theme keys are DARK MODE values, never the light palette repeated.**
  The old guidance ("set dark keys equal to light colors, renders identical") was verified
  wrong against the exporter's dark CSS: those keys only fire in dark mode, so a light value
  ships light-on-light. House defaults are the exporter's own dark CSS (#000000 page, #1F1F1F
  content, #FFFFFF text/links, #FFFFFF button with #000000 label). Inline key table,
  Phase 2 step 7, send-readiness pass, and render-spec 2.1 all corrected.
- **Asset transparency for dark mode: key UI icons, never brand logos, check before keying.**
  Border-connected flood fill, never a global colour replace. Measured failure: a logo whose
  letterforms depend on its band was keyed transparent and became illegible ink-on-ink; logos
  default to opaque (the dark-mode sibling of never-resize-a-logo).
- **Multi-column rows top-align by default.** `primaryAxisAlignItems` (vertical-align) and
  `counterAxisAlignItems` (text-align) are independent exporter reads, so primary MIN +
  counter per content is valid. Relaxes the matched-axes rule for multi-column rows only;
  the batch 3 enforcement-teeth checklist marks these as intentional.
- Phase 2 checklist gains the percent-line-height + mobile-ramp-recorded item; Phase 3 step 5
  Mobile item rewritten around the observed schemas plus a range-hygiene check
  (`getStyledTextSegments(['lineHeight'])` returns ONE segment).
- structure.md writable-keys table mobile rows corrected to the observed schemas.
- Bumps to 1.35.0 (minor: verified schema replaces wrong guidance, Part B behavior change,
  dark-mode correction).

### 1.34.0
- **New multi-column gutter guardrail: zero column padding on a multi-column section is a
  FAIL** unless the source design has a measured zero gutter and the batch report says so
  (defect surfaced by Codex during a v4.1.0 shakedown; three-column module built with zero
  padding passed the content-width equation trivially because 0-gutter columns sum to
  content-width by construction). Phase 3 step 5 gets a new checklist bullet; render-spec
  gets a new subsection 3.4.0 "Multi-column gutters" that generalises 3.4.1's
  "spacing on one side of each boundary only" rule to every multi-column row.
- **Failure signature named:** headlines from adjacent columns visually concatenate into
  one sentence; a card image touches the next card's edge; a button sits a pixel from a
  neighbour. Treat any of those as a gutter failure, not a typography problem. The
  arithmetic gate cannot see this.
- **Worked example for three equal cards** in a 560 content box with 16px source gutter:
  `card content = (560 - 32) / 3 = 176px`, expressed as 186.67px column boxes with 8px
  horizontal padding on each side, so adjacent card content is separated by 16px.
- Do not infer card width by dividing content width by column count unless the measured
  source gutter is zero. That inference is how the failure lands.
- Section 3.4.0 numbering used (not a new top-level section) so 3.4.1's Two Column Swap
  keeps its number.
- Bumps to 1.34.0 (minor: new required checklist rule + new render-spec subsection).

### 1.33.2
- **Cloudflare 403 `error code: 1010` workaround documented** (batch 4 defect, closes
  queue). Phase 3 step 1 POST-to-worker instructions now say: if the worker returns 403
  with body `error code: 1010`, it is a Cloudflare browser check, not an auth failure.
  Retry with a normal browser User-Agent header; the Bearer/provider headers are correct
  as documented.
- Rationale: Batch 4 hit this and every POST returned 403 with body
  `error code: 1010`. Auth was irrelevant (empty Bearer, no Bearer, and a real token all
  failed identically); setting a browser User-Agent fixed it instantly. The 403 sat next
  to Bearer/license-key instructions, so the natural conclusion was an auth problem.
- Bumps to 1.33.2 (patch: infrastructure workaround note).

### 1.33.1
- **`mj-navbar` mapping documented** (batch 4 defect). Render-spec section 6.1 note now
  says: when the worker returns `mj-navbar`, do not invent a mapping. Rebuild as one
  `mj-text` node whose characters carry every label, with `setRangeHyperlink` per label,
  separated by a normal space plus non-breaking spaces so the visible gap survives HTML
  whitespace collapsing while the line can still break between labels but never inside
  one. Type styling from the audit's Nav Link ramp entry.
- Two reasons this shape wins over the alternatives on any nav past three items: it
  reflows (a group of pinned columns cannot, per section 3.3.2), and it satisfies audit
  constraints of the form "split the single text run into N separately linked items"
  without a per-item column.
- Rationale: Batch 4 met `mj-navbar` twice and improvised twice, ending at the
  reflowing-text shape both times. Task #42's four-item nav shipped this way after the
  group build failed twice.
- Bumps to 1.33.1 (patch: documentation of a mapping the skill previously punted on).

### 1.33.0
- **Check the font is installed before building the ramp; know the substitute** (batch 4 defect). Phase 2 step 3 (Type mapping) now says: call
  `figma.listAvailableFontsAsync()` and look for the target family by name before building.
  The Figma environment an agent runs in typically serves Google Fonts only (about 1,900
  families); Helvetica, Helvetica Neue, and Arial are all absent even though they are the
  most common email-safe answer.
- **When the target is Arial or Helvetica and unavailable, build in Arimo**, the
  metrically compatible Arial clone. Identical advance widths, so a string that fits on
  the canvas fits in the email and section 3.3.1's slack arithmetic stays accurate.
- State the consequence in the foundations report: the exporter writes `fontName.family`
  into `font-family`, so an export will say Arimo until the family is swapped or Arial is
  accepted at send time.
- Expect the weight count to drop (Regular and Bold only from email-safe stack); collapse
  belongs in the foundations report so a designer sees which weights they lost.
- Rationale: every agent-run migration whose customer picks the standard email-safe stack
  hits this, and the silent failure mode is building the ramp in Inter.
- Bumps to 1.33.0 (minor: new Phase 2 step 3 rule + external tool call added).

### 1.32.2
- **Open every exported PNG before uploading it** (batch 4 defect). Render-spec 4.2.1
  now has an explicit step between download and upload: open the PNG and look at it. Three
  failure modes named, each of which presents as a layout bug rather than an asset bug:
  baked-in white (a node whose own background is white exports opaque and reads as a white
  box on a colored band; key white to transparency for line art, flood-fill surround to
  band color for photographic cutouts), neighbour's content (check the crop's far edge
  against where the adjacent column starts, not against the source node's declared width;
  a node can be wider than its visible content), and fused row not missing (already 4.2.2).
- Batch 4: four asset defects, all presented as layout bugs. The T-shirt one baked in
  28px of the neighbouring column's text; the layout got chased twice and the component
  rebuilt once before anyone opened the PNG.
- Bumps to 1.32.2 (patch: enhancement to existing 4.2.1 rule).

### 1.32.1
- **Cap-height measurement method** for settling type-size disagreements (batch 4
  defect). New render-spec section 5.2.1: when the worker returns a size and the ramp says
  a different one, or when two plausible sizes disagree by 4 pixels, crop tightly to one
  line, threshold to isolate glyphs, measure pixel ink height, compare against a known
  reference in the same casing via `size = knownSize * (measuredCapHeight / knownCapHeight)`.
  Compare all-caps against all-caps and mixed-case against mixed-case (ascenders and
  descenders change the ratio). Round onto the audit's ramp, never to the nearest round
  number. Batch 4 references: 28px all-caps measured 20px ink, 36px mixed-case measured
  33px.
- Task #45's worker-vs-measurement rule now references this section as the actual method.
- Inserted as 5.2.1 rather than a new top-level section so existing 5.3-5.6 references
  keep their numbers.
- Bumps to 1.32.1 (patch: method documentation for an existing discipline).

### 1.32.0
- **STRUCTURE from worker, NUMBERS from measurement** (batch 4 defect). Phase 3 step 2
  "unpinned drifts" bullet rewritten to say plainly what the old wording undersold: the
  worker is a very good structure detector (find columns, rows, stacking order, which
  things are buttons, and sometimes structural fixes the source does not advertise) but
  it is not a measuring instrument (colors drift by several units, sizes land on plausible
  round numbers rather than the customer's ramp, unpinned fonts flatten to Arial).
  Transcribe its tree, then replace every color with one sampled from source pixels, every
  type size with one measured, and pin every font.
- **A size the worker returns that is not on the audit's ramp is the loudest signal it
  guessed.** The ramp is the specification; a 40 where the ramp says 36 is a per-module
  factor sneaking back in.
- **A gap in the ramp is a decision for foundations, not for batch 3** (batch 4 defect).
  Phase 2 step 3 Type specimen instruction now says: if the specimen shows a jump with
  nothing between it, look at the source for content that would sit in the gap (eyebrows,
  captions, small subheads); if any exists, add the step now and record it as a
  standardisation. Batch 4 foundations report predicted this exact cost and deferred
  anyway; three modules in batch 3 wanted exactly the missing 20px step.
- Bumps to 1.32.0 (minor: rewritten bullet in Phase 3 step 2 + new rule in Phase 2 step 3).

### 1.31.1
- **`unsubscribe.com` magic link convention documented inline** (batch 4 defect). Phase
  2 inline plugin data key section now carries a "Magic link values the exporter rewrites"
  table listing `unsubscribe.com` as the href the exporter substitutes with the selected
  ESP's unsubscribe merge tag at export time. Works on text, buttons, and images. Never
  invent a placeholder unsubscribe URL and never hand-type an ESP merge tag unless the
  customer asks for a specific one; a design system that hard-codes one ESP's tag stops
  being portable, which is the whole point of the magic value.
- Send-readiness pass at hand-off (task #35) updated to name `unsubscribe.com` as the
  default unsubscribe target so an agent building a footer reaches for the portable value.
- Rationale: Batch 4 could not determine the ESP, invented
  `https://www.example.com/unsubscribe-placeholder`, wrote it into the footer, and
  escalated as "the one item that is a legal problem, not a polish problem". The answer
  was one word. Source: `help.emaillove.com/plugin/links/unsubscribe`.
- Bumps to 1.31.1 (patch: documentation of an existing plugin convention).

### 1.31.0
- **Mobile visual: render it, do not reason about it** (batch 4 defect). Phase 3 step 5
  Visual bullet rewritten. Figma's canvas has no mobile breakpoint, so `get_screenshot` at
  390px just renders desktop-shaped pixels at 390px, not the plugin's mobile treatment.
  The old "second screenshot pair at mobile width" instruction silently degraded to a
  recorded intention, not a check. Replaced with a headless render via
  `emaillove_preview_email` after the batch is uploaded provisionally to the plugin
  library; the response carries desktop and mobile renders from the exporter.
- Fail conditions named explicitly: word broken mid-string (task #42's 3.3.2 group-shrink
  defect), image aspect ratio differs from desktop, stacked column carrying desktop gutter
  as indent, section that stacked where step 3 Part A recorded group (or vice versa).
- Order stated for migrations: build the batch, upload provisionally, render, diff, only
  then open the next batch. A construction mistake found at batch 1 is one fix; at batch
  5 it is five.
- Rationale: three of the four batch 4 corrections were mobile-only, every one caught
  by the customer manually exporting screenshots from the plugin and sending a zip. The
  customer should not be the mobile test harness when there is an MCP tool for it.
- Bumps to 1.31.0 (minor: workflow change to Phase 3 step 5 verification).

### 1.30.0
- **New render spec section 3.3.2: group columns shrink on mobile, and 3.3.1 does not
  protect them** (batch 4 defect). Section 3.3.1 protects a pinned column against font
  drift at the pinned width; it does nothing about the other risk which only exists for
  group columns: a group never stacks so its columns shrink proportionally at every
  smaller viewport. Formula: `resolved = columnWidth / groupWidth * (mobileViewport - side padding)`.
  Per column: text carrier needs `resolved >= widthOf(longest unbreakable word) * 1.05`;
  fixed-aspect image carrier needs `resolved >= image natural width`. Three remedies when
  a column fails (collapse to one reflowing mj-text with setRangeHyperlink ranges, drop
  the group so columns stack, or hide with mobileStylesHideInMobileDevice); widening is
  usually not available because widths must sum to the content box.
- **Phase 3 step 5 checklist gets a new "group columns resolve wide enough on mobile"
  bullet** referencing 3.3.2. Empty violation list is the only pass.
- Rationale in the skill: Batch 4 shipped a four-item nav pinned at 137/86/133/89 in
  a 560 group that rendered `CHA/NGI/NG`, `G/E/A/R`, `CLO/THIN/G`, `GI/F/T/S` at 375px;
  the 86px GEAR column resolved to 51px which cannot hold "GEAR" at 17px. Invisible on
  the Figma canvas and in the desktop preview by construction. Also caught a second
  module before ship (announcement bar text column resolving to 190px vs 191px hug).
- Bumps to 1.30.0 (minor: new required checklist rule + new render-spec section).

### 1.29.0
- **Getting Started page: HUG height, screenshot verification, accurate image workflow**
  (Batch 3 defect, closes queue). Phase 2 Getting Started page section now says: the
  frame is vertical HUG with clipsContent OFF, never a fixed height (a fixed height clips
  the content invisibly and the page functionally disappears; batch 2 shipped a
  100px-fixed frame that clipped 940px of instruction text and the page rendered as the
  bottom edge of its own title). After writing the block, screenshot the whole page and
  confirm every line is visible; a screenshot that shows only the title is a fail.
- **Image workflow described accurately, not the way it was described on batch 2.**
  Text is edited through component properties (correct); images are edited by selecting the
  image rectangle inside the instance and replacing its image fill (correct), never by
  detaching or reparenting. Figma has no image component-property type, so the wording
  "swap images using the component properties panel" is wrong and reads to a user as a
  workflow that does not exist. Say the actual workflow instead.
- Phase 2 completion checklist Getting Started bullet updated with both requirements
  (HUG-not-fixed, image workflow accuracy) so the check surfaces both defects before the
  next step runs.
- Bumps to 1.29.0 (minor: closes Batch 3 queue, Codex findings 1 and 5).

### 1.28.0
- **Button label MUST be exposed at module-root level** (Batch 3 defect). Phase 3 step 4
  (properties): every module that contains a button re-exposes the foundation button's Label
  as a TEXT property on the module root, named `Button label` (single-CTA) or
  `Card N button label` (grid). The foundation button's Label property is not surfaced on
  instances placed inside a module unless the module root re-exposes it.
- Phase 3 step 5 checklist adds: any module with a button and no top-level Button label
  property is a fail. List by node id each button whose label is not surfaced at module level.
- Rationale: Batch 2 shipped 18 buttons across 18 modules, each with a working label
  property on the foundation and none surfaced at the module the marketer instances, so a
  user following the Getting Started page could not change any CTA copy from the top-level
  property panel.
- Show button BOOLEAN is a separate decision from Label: add only where a sibling design in
  the source has that button absent, not speculatively.
- Bumps to 1.28.0 (minor: new required property rule, closes Codex finding 6).

### 1.27.0
- **New WCAG contrast table in the Phase 2 foundations report** (Batch 3 defect).
  For every text-on-fill pairing the theme will render (textColor on backgroundColor,
  linkColor on backgroundColor, buttonTextColor on buttonContentColor, plus explicit
  text-on-brand pairings), compute the WCAG contrast ratio, label each `pass` or `fail`
  with the ratio, and flag pairings that fail 4.5:1 for normal text or sit at the 3:1
  large-text floor.
- Rationale in the skill: Batch 2 shipped `color/text/accent = #009EE2` at 3.00:1 on
  white and used it on 18px bold subheads (which requires 4.5:1 under WCAG AA). The
  darker `blue/700 = #0078B4` reaches 4.83:1 on white; the contrast table is what
  surfaces the choice before the designer confirms the palette.
- Bumps to 1.27.0 (minor: new required report row, closes Codex finding 9).

### 1.26.0
- **New Phase 3 step 5 verification line: semantic-token bind count** (Batch 3
  defect). Every non-placeholder solid fill in a module must resolve to a variable binding
  from the audit's Palette, not to a raw hex. Walk every fillable node, list unbound solid
  fills by node id with the raw hex and the role they should have (brand background,
  headline text, button background, divider, footer fill). Empty list is the only pass.
  Placeholder gray fills for editable image regions are the only allowed exception, each
  named as an intentional placeholder.
- Rationale in the skill: Batch 2 shipped 43 unbound fills (31 real, 12 placeholder)
  and every downstream color change had to touch each of the 31 by hand, exactly the state
  a design system is meant to remove. When an unbound fill has no theme role, that is a
  question for the designer about extending the palette, not a silent leave-it-raw.
- Bumps to 1.26.0 (minor: new required verification line, closes Codex finding 8).

### 1.25.1
- **Enforcement teeth on Phase 3 step 5 structural rules** (Batch 3 defect). Rules
  that shipped violated on batch 2 (18 alignment axis mismatches, 18 untagged button
  TEXT children) get list-every-violation-by-node-id treatment. Empty list is the only
  pass. A "walked the tree, looked fine" pass is what shipped those defects with no
  checklist line reporting them.
- The `name` plugin data key check now explicitly includes the TEXT child of every
  `mj-button` (must carry `mj-button-text`), calling out that a foundation-button instance
  whose inner text is untagged is still untagged and still fails.
- The alignment axis check now names the exporter contract (mismatched axes render one
  way in Figma and another way in HTML) and asks for each mismatch to be reported as
  `<node id>: primary=X, counter=Y`.
- Bumps to 1.25.1 (patch: enforcement tightening on existing rules, no new behavior).

### 1.25.0
- **New "Send-readiness pass on every campaign" step at Hand-off** (Batch 3 defect).
  Before the hand-off conversation, walk every mainFrame campaign root and confirm each is
  safe to send. Batch 2 or 3's Codex review found the delivered file had zero shared hrefs,
  zero shared altText, blank subject and preheader on all three campaigns, one root with
  blank lightThemeBackgroundColor, placeholder legal, and the literal word "Address" in the
  footer.
- Send-readiness pass covers, per campaign root: all nine theme keys populated with real
  values (empty is not neutral); non-blank subject and preheader; fallBackFontName is a
  single family name not a CSS stack; the root has a non-generic name (rename QA roots with
  "QA only, do not send" prefix). Per mj-image: href is a real URL or explicitly empty for
  decorative, altText is meaningful copy or empty for decorative. In the footer: no
  placeholder legal, no "Lorem ipsum", no literal "Address" string, unsubscribe link
  present as merge tag or real URL not "#".
- List every violation by node id under a "Send-readiness violations" heading in the batch
  report. Empty list is the only pass. Do not open hand-off until clean.
- Bumps to 1.25.0 (minor: new required step at Hand-off, converter behavior change).

### 1.24.0
- **Inline plugin-data key table at the top of Phase 2** (Batch 2 defect, last of the
  queue). The skill cites `references/render-spec.md` and `references/structure.md` by
  section number 23 times. Batch 2 received a converter bundle where those files were
  absent (a v1.19.1 packaging bug, since fixed) and spent five rounds of design review
  hunting for load-bearing plugin data keys the SKILL.md would not surface. This adds:
  - A precondition check at the top of Phase 2 that confirms both reference files are
    readable. On absent files, name what cannot be verified before starting and either
    fetch a fresh bundle or agree on a reduced scope. A one-line check catches this
    before the first module instead of four modules in.
  - The complete `emaillove` shared plugin data key table inline (name, nodeType, nine
    theme keys on the mainFrame root, optional email meta, `fullWidth`, `stackColumns`,
    `reverseStack`, `href`, `altText`), with what goes where and what it does.
  - A named "NOT shared plugin data keys" section covering four mobile behaviors
    Batch 2 spent rounds hunting for that turned out to be Figma-side, not data-side:
    full-width mobile button (`layoutSizingHorizontal='FILL'` on `mj-button`),
    fluid-on-mobile image (width-relationship to column content width), mobile padding
    overrides (node properties, not shared keys), mobile column stacking (`stackColumns`
    or `mj-group`).
- The render spec keeps the prose, the worked examples, and the rationale. The inline
  table is the irreducible contract that makes the skill functional even when a bundle
  ships without references (which should never happen again, but the belt-and-braces is
  worth the forty lines).
- Bumps to 1.24.0 (minor: material additions to Phase 2 preamble, closes Batch 2
  queue).

### 1.23.0
- **Render-once-crop-locally documented for unstructured sources** (Batch 2 technique).
  Phase 3 step 1 (screenshot the module) now says: on an unstructured source, render the whole
  design page once at 1:1 and crop locally per module. Per-node `get_screenshot` calls fail on
  a file with no grouping because a loose rectangle comes back rendered in isolation without
  the text that visually sits on top of it, useless when the design's meaning is layered
  z-order. One full-canvas render costs one call and gives exact pixels for every module the
  audit's source refs bound. On an email-native source with proper components, per-node
  screenshots remain correct; the choice is per source, not per module.
- **Band detection for padding correction** (Batch 2 technique). Phase 3 step 5 visual
  check now includes: on a module that comes out 20-40px too tall (the common first-pass
  overshoot because Figma text renders taller than the hand-placed box reports), detect
  content bands in the source PNG and the rebuild PNG, diff them, and derive exact padding
  corrections from the difference. Turns a subjective back-and-forth loop into a deterministic
  two-pass one. On batch 2 this got 24 of 28 modules onto their source height.
- **Nav bar worked example added to the mj-group visual tells** (Batch 2 exception).
  A row of five or more nav links does NOT survive as a group: the exporter divides body
  width by column count and per-link boxes come out narrower than a single word, breaking
  words mid-letter at phone width. Ungrouped columns stack cleanly, one link per row, and
  that is the shipped shape. Recorded as "loose columns, stack expected, no keys set, nav
  bar exceeds group-safe width" in step 3 Part A. On batch 2 this cost two attempts
  before landing on the stacked build.
- Bumps to 1.23.0 (minor: two new techniques documented, one worked example).

### 1.22.0
- **New Phase 3 step 6: export sniff test (once per batch)** (Batch 2 defect). Every
  check in step 5 is Figma-side, and the plugin's exporter is what decides whether a group
  overflows, whether a button goes full width, whether an image scales. A batch that passes
  every Figma check can still ship with mobile defects that only exist in the exported HTML.
  Once per batch, after step 5 has passed for individual modules, drop a wrapper instance
  into a temporary email frame on Campaigns, click Export, read the HTML, and confirm four
  things: body width matches foundations, an `@media only screen and (max-width` block
  exists, mobile classes are present for anything that should stack or go full-width
  (`mj-column-per-100`, `mj-b-full`), and per-section column widths add up to the intended
  content box.
- Rationale in the skill: on batch 2 this ate five rounds of design review, each spent
  reverse-engineering exporter behavior by pixel-measuring preview PNGs, when one export
  read would have surfaced the group overflow, the button width and the fluid-image
  behavior together in the first batch. The sniff is a second-pass check on a different
  artifact, not a replacement for step 5.
- **Step numbering shifts:** old step 6 "Batch report and gate" is now step 7. The
  "finishing a batch IS a stop" reference at the top of the skill updated to point at
  step 7.
- Bumps to 1.22.0 (minor: new required step in Phase 3).

### 1.21.0
- **The render-node-not-fill rule now fires in TWO phases, not one** (Batch 2 defect).
  It always existed in Phase 2 step 6 (assets round-trip). Phase 3 step 1 (screenshot the
  module) now carries it too, because the mistake happens where the pipeline is: on
  Batch 2 the hero photograph was cropped out of a canvas render and the overlapping
  white card baked into the image, producing a ghost headline inside the picture that only
  surfaced at the visual check. A bulk canvas-crop pass for efficiency in either phase is
  the failure mode; export each image node individually, even when it is slower.
- **Logos are never resized to fit** (Batch 2 defect). Phase 2 step 6 now says the
  intrinsic size is the source of truth: do not stretch a logo to fill a column, scale it
  up to match a hero image, or fold it into a "grow inset images to fill their column" pass.
  Separate rule from image sizing, because a stretched logo damages a brand asset the
  customer already owns.
- Bumps to 1.21.0 (minor: converter behavior change in two phases, no report structure
  change).

### 1.20.0
- **Phase 2 now reads the audit's Spacing system section and builds every module against it,
  not against per-module source values** (Batch 2 headline defect). The audit's census
  consolidated the source's ad-hoc side insets, vertical rhythm, gutters, card paddings and
  their mobile equivalents into one system per role with a designer decision on each; that
  system is what every module in every batch inherits. Named exceptions (full-bleed image
  bands, wide-quote outsets) are allowed only where the audit listed them.
- **Phase 3 step 5 verification now asserts spacing resolution.** Walk the built module and
  list each side padding, vertical padding and gutter with the role and system value it
  satisfies; a padding that resolves to nothing is a fail, and the remedy is a designer
  question about the system rather than a silent per-module override. Also confirms no mobile
  padding is greater than 160px on a 320 viewport (a defect regardless of what the system
  carries).
- Rationale in the skill: Batch 2 shipped with 30-plus distinct side inset values across
  28 modules and one that broke on mobile (220/221 on a 320 viewport), and every batch
  report passed. The per-module measurement was exactly how it happened.
- Bumps to 1.20.0 (minor: new mandatory verification line, converter behavior change).

### 1.19.3
- **Mobile stacking now has a mandatory checkpoint** (Batch 1 defect). Phase 3
  step 3 renamed from "Merge the mobile twin" to "Decide mobile behavior" and split into
  Part A (always runs: record a stacking decision per multi-column section) and Part B
  (conditional: merge the mobile twin if one exists). The old skill silently skipped step 3
  when there was no mobile twin, which is the common case on unstructured legacy sources,
  and shipped header lockups that stacked on mobile as a result.
- **The mj-group rule has concrete visual tells now** (batch 2 defect same class). New
  bullet in the "visual pattern" section names three tells for a lockup: unequal columns
  with one small and fixed, columns sharing a continuous background, or the block being a
  header or footer strip. Patterned on the bleed concession's "recognizing this is its own
  step" treatment.
- **Step 5 verification catches stacking defects.** Mobile check reworded from "list the
  mobile keys you set" (empty list read as a pass) to require an explicit stacking decision
  per multi-column section plus the keys that produce it. Visual check now takes a second
  screenshot at mobile width so group-vs-loose-columns mistakes surface visually.
- **Wrapper instance sizing documented** (batch 2 defect 2). Phase 2 step 7 and Phase 3
  step 5 both state: a wrapper is FIXED at the target email width, as a component and as
  every instance of it. Section 0's FILL rule applies inside a wrapper, not to the wrapper
  itself. Previously silent, so the inside-a-module default got misapplied one level up.

### 1.19.2
- A model-choice note: use your most capable model for this skill, since a migration runs once
  and a dropped rule becomes a component that silently breaks on export later.

### 1.19.1
- Bundle and update-check fixes as above.

### 1.19.0 and earlier (same day)
- A prescribed, non-optional library structure: cover, getting started, foundations with real
  Figma variables, a type specimen sheet, buttons, one page per category, campaigns.
- One content width for the whole library, applied to every module, because the conversion
  worker guesses padding per screenshot with no knowledge of sibling modules.
- One scale factor applied to every number, with a ratio acceptance test that catches per-style
  drift. On a reference-only source there is no factor: build to email standards.
- The two-column swap: the standard rebuild for a photo that overlaps or bleeds past its block,
  which email cannot express. Such a block stays live text with a named concession, not an image.
- Images come across as rendered nodes, never raw fills, so crops and transparency survive.
- Heights hug, spacing is auto-layout padding, and a gap belongs to one block, never both.
- Pinned text columns carry slack for font substitution at send time.
- A single consolidation pass resolved 19 contradictions that accumulated across the day, and
  corrected a wrong ground-truth claim about where the exporter reads button alignment.

## emaillove-migration-audit

### 1.19.0
- **Mobile type ramp is now a required, DERIVED audit output, and it is a compression, not a
  scaling** (batch 6, from a live migration on 2026-08-03). Email clients do not scale type:
  a declared size renders identically on a 375pt phone and a 640px desktop while the line box
  nearly halves (measured: 27px copy went from 42 chars/line to 21, and the customer read it
  as "the mobile rendering is not that good"). Single-factor derivation was tried, measured,
  and rejected by the customer: one factor preserves the desktop headline:body ratio, which
  is exactly what reads wrong on a phone. New Step 6 bullet derives with TWO anchors (body
  desktop -> 16-18 mobile, largest workhorse headline -> 26-30 mobile), linear interpolation,
  whole-pixel rounding, floor at 14. Deliberately NO ratio acceptance test against the
  desktop ramp: matching the desktop ratio is the failure mode. Worked case: anchors 27->18
  and 50->28 move headline:body from 1.85 to 1.56.
- **New required "Mobile styles" report section** between Palette and Module inventory: the
  two anchors, the mobile ramp table (floored rows marked), the statement that line heights
  carry no mobile override because desktop styles use percentages, mobile spacing overrides
  (side padding drop, 28px stacking bottom padding on non-last columns, over-160px sections,
  group arithmetic), hide-on-mobile items, closing with designer decision. Where the source
  has mobile variants, census instead of deriving.
- **Palette section gains a dark-mode proposal**: the six theme keys are DARK MODE values,
  so the Palette now proposes a dark value per role, starting from the exporter's house
  defaults, with WCAG contrast ratios shown per pairing.
- Step 8 hand-off list now names Mobile styles and the Palette's dark-mode proposal among
  what Phase 2 consumes.
- Bumps to 1.19.0 (minor: new required report section, new derivation).

### 1.18.1
- **Frontmatter description trimmed under claude.ai's 1024-char upload limit.** The census
  fixes each appended a clause to the description and Batch 3 pushed it to 1106 chars, at
  which point the claude.ai skill upload rejected the bundle with "field 'description' in
  SKILL.md must be at most 1024 characters". Consolidated the three census clauses into one
  ("censuses spacing, palette, and type ramp into one system each"); now 1004 chars. All
  trigger keywords preserved.
- `validate_repo.py` now checks every skill's frontmatter description against the 1024
  limit, so CI catches the next overflow before an upload does.
- Bumps to 1.18.1 (patch: frontmatter-only change, no behavior change).

### 1.18.0
- **Palette census now clusters by ROLE as well as by VALUE** (batch 4 defect enhancement
  to task #34). Sample text-node fills as well as background fills; the same hex used as a
  band and as text on white are TWO theme tokens, not one, because the theme layer needs
  to move them independently. A palette built from `fills` alone finds bands and buttons
  and misses type, which is how a nav link `#888888` and a body color `#222222` used only
  on text disappear from a theme roles list. Batch 4 shipped both cases and the
  converter added both mid-batch.
- **Type ramp floor recommendation.** Where the smallest cluster is below 12px, the audit
  now recommends a floor at 12 (or a customer-confirmed floor). The conversion will have
  to standardise below-12 upward anyway (Android and Outlook garbling, readability), and
  it is better decided at audit than at batch 4. Batch 4: value-prop captions at ~11px
  standardised up to 12 mid-build; the audit would surface the decision now.
- Bumps to 1.18.0 (minor: two audit-behavior enhancements, no report structure change).

### 1.17.0
- **Palette is now CENSUSED, not sampled** (Batch 3 defect). Step 6 palette bullet
  rewritten to enumerate every distinct fill hex in the file, cluster near-duplicates within
  a small delta (2-3 units per channel), report each cluster with source hex, count of fills
  using it, and modules it appears on. Same shape as the type ramp and spacing censuses.
- **New required "Palette" report section** between Spacing system and Module inventory.
  Same shape as Scale factor and Spacing system: the census, the proposed theme colors, and
  **every deviation between a proposed theme value and its source cluster listed with the
  delta** so a designer approving the theme approves the drift too and does not read a
  lightened value as source fidelity. Additional source colors not carried into theme roles
  listed at the bottom so nothing is silently dropped.
- Rationale in the skill: Batch 2 or 3's Codex review found four accent primitives lightened
  from source (Pink #C4014B -> #D03E75, Magenta, Teal, Orange) with no documentation of the
  drift, and two source colors absent from the theme entirely (a decorative green, a bright
  blue). The palette section prevents undocumented drift and silent drops.
- Brand foundations report section trimmed: palette no longer restated there, one-line
  pointer instead. Same pattern as spacing.
- Bumps to 1.17.0 (minor: new required report section, audit behavior change).

### 1.16.0
- **Band-detection technique for module boundaries on unstructured sources** (Batch 2
  technique). Step 5 pass 1 (split each design into blocks) now says: on an unstructured
  source, render the whole design at 1:1 and detect content bands from the pixels. Rows of
  pure canvas background between text and imagery are the gaps between modules; transitions
  from a run of solid background pixels to a run of mixed pixels are the module boundaries.
  Finds cuts where node structure gave none, on the artifact the reader will actually see
  rather than the tree structure they will not, costs one render. Record the y-coordinates
  on the source ref (`top 128 to 540` rather than a hand-eyeballed range) so Phase 3 can
  crop to the same pixels without re-deriving.
- Bumps to 1.16.0 (minor: audit technique added, no report structure change).

### 1.15.0
- **Type ramp is now CENSUSED, not sampled** (Batch 2 defect). Step 6 replaces the old
  "each of their text styles mapped" opener with a full census: enumerate every distinct
  `(family, size, weight, line-height)` tuple in the file. On a file with text styles the
  census is the styles page plus any local overrides; on a file without text styles it is a
  walk over every text node across every design surveyed in Step 2. Cluster tuples within a
  point or two of each other, and treat each cluster as one ramp row. The mapping table then
  gets populated from the census, not from what was sampled in content modules.
- Rationale in the skill: Batch 2 ran the sampling version and missed the nav-link style
  (15px bold) and the quote style (24/38), both of which had to be added mid-conversion.
  The scale-factor ratio test still passed, because the missing sizes fell inside the
  existing range: the arithmetic gate catches a distorted ramp but not an incomplete one.
- The census still runs on REFERENCE ONLY sources, because the typefaces and weights the
  source uses are the palette the standard ramp gets mapped onto; the sizes are what get
  discarded on that tier.
- Bumps to 1.15.0 (minor: audit behavior change, no report structure change).

### 1.14.0
- **Spacing is now CENSUSED, not sampled** (Batch 2 headline defect). Step 6 replaces
  the old "spacing scale from any padding/spacer components" bullet with a full census: read
  every distinct spacing value from every module in Step 5, cluster by role (section side
  padding, vertical rhythm, gutter, card or inset padding, mobile equivalents), state each
  value at email scale with the count of modules that used it, then propose one system per
  role with a designer-decision gate, the same shape as the Scale factor section. Any mobile
  value greater than 160px is flagged as a defect the source is carrying regardless of the
  decision.
- **Report Step 7 gets a new "Spacing system" required section**, between Scale factor and
  Module inventory. Same shape and treatment: the census, the proposed system per role, the
  outlier modules for the designer to inspect, and the words "designer decision". Brand
  foundations no longer duplicates the spacing scale; it points at the Spacing system
  section instead.
- Rationale in the skill: a design system's coherence is decided by spacing more than by any
  other quantity, and unlike scale it is invisible in any one module and only visible when
  modules sit together. Batch 2 ran the old skill and passed every batch report with 30
  distinct side insets across 28 modules, one broken on mobile.
- Bumps to 1.14.0 (minor: new required report section, audit behavior change).

### 1.13.0

- **Six more ESP source adapters added: Brevo, Kit, ActiveCampaign, Iterable, Omnisend,
  HubSpot.** These are the marketing-focused ESPs verified via web search (August 2026)
  to have official MCPs. Each follows the same pattern as Klaviyo/CIO: introspect the
  connected MCP's tool list at session start, list-templates (or list-campaigns / list-
  broadcasts / list-automations, depending on the ESP's content model), get-template
  returns HTML, render to PNG, feed to design-converter.
- **Adapters direct the agent to introspect** the connected MCP's tools at session start
  rather than hardcoding tool names, since MCPs at these ESPs are evolving and each
  MCP's exact tool surface may drift over time. Links to each official docs page are
  included so the agent can verify.
- Per-ESP quirks called out up front:
  - **Brevo**: API key grants FULL account access (not scoped). Treat as high-privilege
    secret; adapter offers env-var path.
  - **Kit**: content model is broadcasts + sequences + templates (three pools, ask
    which). Kit is looser than a formal template ESP.
  - **ActiveCampaign**: drag-and-drop templates convert more cleanly than raw HTML,
    same as Klaviyo's SYSTEM_DRAGGABLE distinction.
  - **Iterable**: MCP is currently beta and self-hosted via npm (not a hosted MCP).
    Read-only by default. Adapter directs the agent to log any beta surprises for
    Iterable feedback.
  - **Omnisend**: ecommerce-focused, so many templates carry product blocks that pull
    live product data at send time. PNG will render placeholder data; report says
    product-block wiring must be rebuilt in target ESP.
  - **HubSpot**: CRM + marketing platform (no email-only surface). Marketing emails
    embed personalization tokens (fine), smart content blocks (only default variant
    renders in PNG), and CTA-library links (won't survive migration verbatim).
- Step 0 grows to 13 source options (a-m). Choices are appended rather than reordered,
  so existing letter references stay stable.
- Bumps to 1.13.0 (minor: six new capability adapters).

**Verification honesty:** unlike Klaviyo and CIO (verified against loaded MCPs in the
session that wrote them) and Marketo (verified against public REST docs), these six
adapters are written against each MCP's public docs page without loaded tool signatures
to verify tool names. The adapters direct the agent to introspect at runtime for this
reason. When a specific customer uses one of these ESPs, verify the adapter against
their actual MCP install and file corrections here.

### 1.12.0

- **ESP migration v1.5: cloud-source adapters.** Two new source options added to Step 0
  ((f) Google Drive folder and (g) SharePoint folder) via the same "walk a location, pull
  HTML/EML/PNG, feed downstream" pattern that Local Folder established. Both use the
  respective MCP for auth and file access.
- **Google Drive Source adapter** added. Uses the Google Drive MCP; customer supplies a
  folder URL or ID. Filters files to HTML, EML, PNG, JPG. Names the OAuth-scope gotcha:
  `drive.file` scope only sees files opened through a Google file picker, so an MCP set
  up with that scope will return empty on an arbitrary folder even when the user has
  access.
- **SharePoint Source adapter** added. Uses a Microsoft Graph MCP; customer supplies a
  SharePoint folder path. Same file filtering as Drive. Names the enterprise-IT
  friction: many organizations block third-party OAuth into SharePoint, requiring admin
  consent that can take a week or two.
- Both adapters share the audit-step adaptations already established for cloud sources:
  always REFERENCE ONLY, no scale factor, per-file modules with no cross-file dedup in
  v1, foundations from the first 3 items.
- Bumps to 1.12.0 (minor: new capability set, not just an addition to an existing one).

### 1.11.3

- **ESP migration v1, commit 4 (final adapter of the v1 series). Customer.io Source adapter
  added,** replacing the "Coming in v1 (next commit)" stub. Uses the Customer.io MCP
  (`cio_read_api` + `cio_schema` + `cio_prime`).
- Adapter directs the agent to call `cio_prime` first every session for latest authoritative
  usage instructions, then `cio_auth_status` to confirm the environment.
- Names the Customer.io product-naming trap up front: "Automations" in the UI == the
  `campaigns` API resource. Adapter tells the agent to speak the customer's language while
  using the API resource names in tool calls.
- v1 pulls **Templates and Newsletters only** (the two most direct "here's an email" places).
  Discover asks the customer which of the two, or both. Uses `cio_schema` to fetch current
  list-endpoint shapes before calling `cio_read_api`, so a schema drift doesn't silently
  produce wrong fields.
- Fetch: `cio_read_api` on the get-endpoint returns the resource with HTML body. Adapter
  notes the field name varies (`body`, `html`, `content`) and directs the agent to check
  the get-endpoint schema for the current field name.
- Explicit v1 non-goals named for the customer up front: does NOT pull Automations
  (campaigns) or their messages, Transactional messages, Design Studio emails, Layouts, or
  Snippets. If the customer's active content mostly lives in one of these surfaces, adapter
  says so before running so the customer doesn't get a silently-partial result. v1.1 will
  extend to campaign messages, transactional, and Design Studio.
- Two Customer.io-specific report additions per row: asset ID + resource type + direct edit
  URL, and the "templates vs newsletters" pool distinction.
- Warning against reading Customer.io's own agent skills (`design-studio`, `fly-api`)
  during a migration audit: they document CREATING content, not READING it out for
  migration, and mixing them in mid-audit introduces contradictions.
- Step 0's Customer.io load-reference stub updated (was "Coming in v1", now points to the
  real section at the end of the file).

### 1.11.2

- **ESP migration v1, commit 3 of the series. Marketo Source adapter added, prioritized
  ahead of Customer.io** for an enterprise onboarding on Marketo. No official Marketo MCP
  exists, so the adapter uses direct Marketo REST API calls with the customer's OAuth 2.0
  client-credentials.
- One-time credential collection: Munchkin ID, client ID, client secret, optional workspace
  name. The three secrets are treated as sensitive; adapter offers an environment-variable
  path so they never appear in the conversation.
- Auth: single OAuth token request at session start, cached and reused for `expires_in`
  seconds (typically 3600), re-auth only on 401.
- Discover: list `emailTemplates.json` with `status=approved` and `maxReturn=200`,
  paginated by offset until empty. Sort locally by `updatedAt` since the API has no native
  sort. Same 50-template threshold as Klaviyo: ask for a filter rather than pull the
  whole list, because Marketo template lists are dominated by legacy variants.
- Fetch: `emailTemplate/{id}/content.json` returns HTML directly. Render to PNG via
  headless Chrome at the target email width, feed to the design-converter worker on the
  same Path B route the other adapters use.
- Rate limits called out explicitly: 100 calls / 20 seconds, 10,000 / day. Adapter
  directs the agent to serial fetch (not parallel) to stay under the burst window without
  any bookkeeping, and to back off on error code 606.
- Marketo-specific report additions: template ID, direct edit URL, folder path, and
  workspace per row.
- Named the honest v1 caveat: pulls Marketo Templates only, not Emails (individual sends
  inside Programs, where most Marketo customers keep their active content) or Content
  Blocks (reusable header/footer snippets). v1.1 will extend to both.
- Step 0 updated to include Marketo as choice (d), Customer.io renumbered to (e).
- Customer.io adapter still to come as commit 4.

### 1.11.1

- **ESP migration v1, commit 2 of the series.** Klaviyo Source adapter added, replacing the
  "Coming in v1 (next commit)" stub. Uses the official Klaviyo MCP.
- Discover: `get_account_details` first to confirm staging vs production, then
  `list_email_templates` with minimal-payload discovery sort by `-updated`, paginated at
  Klaviyo's 10-per-page cap. Explicit safeguard: when the account has more than about 50
  templates, ask the customer to filter (by date range, name, or IDs) rather than pulling
  everything, since the majority of a Klaviyo template list is old drafts and one-off A/B
  splits.
- Fetch: `get_email_template` returns HTML directly. Skip templates whose `editor_type` is
  text-only. Render HTML to PNG via headless Chrome at the target email width, same command
  as the Local Folder adapter. Feed PNG to the design-converter worker.
- Explicitly do NOT default to `render_email_template`: it is rate-limited to 3/s burst and
  60/m steady (much stricter than the other endpoints), and for migration we care about
  structure, not substituted content. Only use it when a customer explicitly wants merge
  tags evaluated.
- Klaviyo-specific report additions: include the template ID and the direct edit URL for
  every row, and note the editor type (`SYSTEM_DRAGGABLE` templates convert more cleanly
  than raw HTML templates).
- Named the honest caveat about templates-only v1 scope: Klaviyo customers often keep their
  best current content inside campaigns and flows, not standalone templates. The adapter
  tells the customer this up front rather than silently pulling only templates.
- Customer.io adapter comes in commit 3.

### 1.11.0

- **ESP migration v1, commit 1 of the series.** The audit no longer assumes the source is a
  Figma file. New Step 0 ("Pick your source") at the top of the audit asks the customer where
  their emails live: a Figma file (current behavior), a local folder of HTML/EML/PNG, Klaviyo,
  or Customer.io.
- **Local Folder source adapter** added at the end of the skill. Discover walks the folder
  once, groups by inferred template intent, and confirms with the customer before proceeding.
  Fetch renders HTML/EML to PNG at the target email width via headless Chrome (or uses PNG
  directly), then hands each to the design-converter worker on the existing Path B route. The
  audit-step adaptations are named explicitly: no file to survey (Step 2 replaced), always
  REFERENCE ONLY (Step 3), no scale factor (Step 4), per-template modules with no cross-
  template dedup in v1 (Step 5), foundations from first 3 templates (Step 6), effort estimate
  higher than Figma path due to no dedup (Step 7).
- Report shape for local-folder sources is deliberately slimmer than the Figma report: no
  verdict-by-verdict rollup, no scale-factor block, no source-fidelity classification section.
- Klaviyo and Customer.io adapters come in commits 2 and 3.

### 1.10.3
- **Lockup rows are now a recognized build constraint** (Batch 1 defect,
  audit-side half). The build-constraints vocabulary now includes "a two-column row that
  reads as a visual lockup" (logo + headline, icon + copy, shared background, header or
  footer strips), which the row records as "`mj-group`; keep side by side on mobile".
  Reason: the audit walks the whole library at once and is much better placed to notice
  that six header rows across six emails are all the same lockup than the converter is,
  meeting each one alone with only a desktop screenshot.

### 1.10.2
- A model-choice note: use your most capable model here too, since the whole conversion phase
  builds on this report's classifications.

### 1.10.1
- Bundle and update-check fixes as above.

### 1.10.0 and earlier (same day)
- Source fidelity classification: whether a file's geometry is a specification to preserve
  (authoritative), partly (partial), or only a reference to take brand and structure from. A
  messy library does not block a migration; it changes what gets carried across.
- A deduplicated module inventory as the unit of work, with a per-design roll-up, rather than a
  per-template list. A repetitive library reduces to far fewer distinct modules than designs.
- Verdicts recorded per module, with a named concession where a block converts cleanly apart
  from one effect email cannot reproduce.
- Scale detection with a ratio check, skipped entirely on a reference-only source.
- Announce when you stop, and name the state file, the same as the other skills.
