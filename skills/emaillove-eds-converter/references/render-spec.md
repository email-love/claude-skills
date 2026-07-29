# Render spec: design-converter MJML JSON to plugin-valid Figma frames

Audience: render agents transcribing the MJML JSON returned by the
design-converter worker (SKILL.md, Phase 3 step 1) into Figma frames that the
Email Love plugin will preview and export correctly. You may ONLY use what an
external agent can write: layer names, geometry, auto-layout,
fills/strokes/radii, TEXT node properties,
`setSharedPluginData('emaillove', key, value)`, and, for reusable modules,
component creation plus component properties (sections 7 and 8).

Sources of truth, in order:
1. `references/structure.md` in this skill
2. `src/figmaPluginApi/parser/ui2Figma/UiParser.ts` in the Email Love plugin
   source (`email-love/Figma-plugin`, internal): what the plugin builds
3. `src/figmaPluginApi/utils/nodeJsonExtractor.ts` in the same repo: what the
   exporter reads back

The customer's SOURCE Figma file is STRICTLY READ ONLY. All writes go to the
target file only. Never use em dashes in any layer name, plugin data value,
or text characters.

---

## 0. Sizing: hug heights, deliberate widths (read this before you create a node)

Sizing is not cosmetic. It decides whether the email survives Outlook, whether it
survives a copy change, and how the button behaves on a phone. Email Love's own
product docs state the rule plainly: make sure the Height of each component and
its child frames is set to Hug contents, not Fixed, because fixed-height
containers can cause content clipping, especially in Outlook.

Every other section of this spec assumes these rules. Where a section gives you a
`resize()` call, it is getting a node onto the canvas, not setting a size.

### 0.1 Height is HUG on the root and on EVERY descendant frame

- `layoutSizingVertical = 'HUG'` on the root, and on every wrapper, section,
  group, column, column-inner, and leaf pair wrapper inside it. Never `'FIXED'`.
- **Why this is not a preference.** A fixed height in email does not scroll and
  does not overflow gracefully. Outlook on Windows renders through the Word
  engine and CLIPS whatever does not fit, so a fixed-height frame that looked
  correct on canvas ships as a cut off headline in the least forgiving client in
  the mix. It also breaks the first time copy runs one line longer, which is
  every other send. A hug frame absorbs that change; a fixed frame crops it.
- If you call `resize(w, h)` at all, the height argument is a throwaway. Set
  `layoutMode`, then set `layoutSizingVertical = 'HUG'` in the same breath,
  before you append children. Never leave a node sitting at a resized height.
- Order of operations: `layoutSizing*` is only accepted once the node itself has
  a `layoutMode`, and `'FILL'` only once the node is a child of an auto-layout
  parent. So: create, set `layoutMode`, append, then set sizing.
- Three node types are not frames and do not hug the same way. A TEXT node hugs
  vertically (`layoutSizingVertical = 'HUG'`, section 4.1). The `mj-image`
  RECTANGLE and the `mj-divider` LINE carry intrinsic geometry from `resize()`
  and have no hug at all. Their pair wrapper FRAMES still hug, and that is what
  keeps them from being clipped.
- `mj-spacer` is the single exception in this spec, and 0.2 says why.

### 0.2 Vertical rhythm is auto layout padding, never a height

- Space between blocks is `paddingTop` / `paddingBottom` on the owning frame.
  Not a taller frame, not `itemSpacing` (ground rule 7), not manual positioning.
- **Manual positioning does not export at all.** The exporter reads Auto Layout
  padding and nothing else, so a node nudged into place on the canvas exports
  with zero spacing and the design collapses silently. If a gap is not padding,
  it does not exist in the sent email.
- Prefer padding to spacers, per the product docs: use padding instead of spacer
  elements when possible. When the worker JSON returns an `mj-spacer` whose only
  job is a gap between two blocks, fold that height into the padding of the
  neighboring element and drop the spacer. Keep a spacer only where the design
  needs a standalone gap of its own (a colored band, a gap inside a bordered
  column).
- `mj-spacer` is the ONLY node in this spec that carries a fixed height. It is
  load bearing there: the exporter emits `height: <node.height>px` straight off
  the node, and a spacer has no children to clip. Set
  `layoutSizingVertical = 'FIXED'` on a spacer and nowhere else in the tree.

### 0.3 Width: FILL, HUG, and the narrow case for FIXED

Widths are generally FILL or HUG. FIXED is correct only where the pixel number
is load bearing.

| Sizing | Where it belongs |
| --- | --- |
| FILL | `mj-wrapper` under the root; `mj-section` under a wrapper; a single `mj-column` in its section; `mj-column-inner`; every leaf pair wrapper as a column child; the `mj-text` TEXT node inside its frame; the `mj-divider` LINE for a full-width rule |
| HUG | `mj-group` (its width comes from the fixed columns inside it); the `mj-button` frame (auto-width button); `mj-button-text`; and the transient state of any frame you have created but not yet appended and set to FILL |
| FIXED | the four cases below, and nothing else |

FIXED width is correct for:

1. **The root frame**, at the numeric `mj-body` width (usually 600). This is the
   canvas the whole email is measured against.
2. **Every column in a section that holds two or more columns**, unequal columns
   above all. The exported percentage is
   `column.width / (section.width - section horizontal padding) * 100`, so the
   pixel number IS the percentage. A 200 + 360 split only stays a 200 + 360
   split because both are pinned.
3. **Every column inside an `mj-group`.** MJML requires percentage widths there,
   and the exporter derives them from your pixels (280 + 280 in a 560 group
   exports 50/50). Do not reach for FILL to express a percentage.
4. **The `mj-image` RECTANGLE**, whose pixel width also decides whether the image
   stays fluid on mobile (section 4.2).

Anywhere else, a FIXED width is a latent bug: it stops tracking the section
content box the moment a padding value changes, and the exported percentage
drifts away from the design with no visible error.

### 0.4 Button width is a mobile behavior decision

The plugin syncs a button's mobile width from how you sized it in Figma:

- **FILL** (the button stretches to fill its column): the plugin enables
  full width on mobile (`width: 100%`) and the exporter sets `applyFullWidth`.
  The button spans the column on desktop and on mobile.
- **HUG or FIXED**: the button keeps its width on mobile.

So choose from the source design, never from what makes the canvas look tidy. An
edge to edge CTA is FILL. An inline, auto-width button is HUG, which is what
worker JSON buttons are by default (section 4.3). FIXED only when the design
system pins a button width, and it behaves like HUG on mobile. Record the choice
in your report when it is anything other than HUG.

Never set the button frame's height. It comes from the text height plus
`inner-padding`, and that padding is also how you get a tap target of at least
44px.

### 0.5 Where padding belongs, by level

| Level | Typical values | Notes |
| --- | --- | --- |
| `mj-wrapper` | 0 to 20 | Outer breathing room around a group of rows. This is where a visible gap between content and the outer background color comes from |
| `mj-section` | 0 to 20, often 0 | Many designs keep section padding at 0 and control all spacing at column and element level. Horizontal section padding also defines the content box that column percentages are computed against (section 3.2), so reproduce the worker values exactly |
| `mj-column` | 20 to 30 horizontal, 10 to 20 vertical | The most commonly adjusted level. This is what gives text, images, and buttons room from the column edge |
| Leaf pair wrapper (`mj-text-Frame`, `mj-image-Frame`, `mj-button-Frame`, `mj-divider-Frame`) | sparingly | Fine tuning one element, for example 10px above a button but not above the text over it |
| `mj-button` `inner-padding` | from the MJML, symmetric only | This is the button's tap target, not layout spacing. Asymmetric values round-trip wrong (section 4.3) |

In a conversion the worker JSON paddings are authoritative: transcribe them
exactly. The ranges above are for gaps you have to invent, and for judging when a
converted value is obviously wrong.

Four things that keep padding honest:

- **Be consistent.** Pick a base unit (8px is a good one) and use multiples of
  it across the whole module rather than mixing 20 and 30 between rows.
- **Padding sits inside the box and eats content width.** Two 50 percent columns
  with 20px on each side lose 80px of content width in total.
- **Outlook** ignores very small values (under 5px) and handles even numbers more
  predictably.
- **Mobile padding is a separate override** (`mobileStylesPadding*`), not a
  reason to compromise the desktop value.

---

## 1. Non-negotiable ground rules

1. **Tag every node via shared plugin data.** The plugin identifies a node with
   `getMetaName(node)`: it reads the plugin data key `name` first (private, with
   fallback to the shared `emaillove` namespace since commit f60c404,
   2026-07-24), else the Figma layer name. Always write
   `node.setSharedPluginData('emaillove', 'name', '<exact tag>')`.
   The layer name is then free for a human label, and section 6 says exactly
   which label to use: the plugin's own display name for that tag, so a
   converted file reads like one the plugin built. Never rely on the layer-name
   fallback. If you did skip the shared key, the layer name itself would have to
   be either the bare tag (`mj-section`) or the parsed form
   `Label, (mjml:mj-section)`; a layer named `mj-section - Report CTA` with no
   shared key FAILS, because the whole string is read as the tag.
2. **Exact tag strings.** Matching is exact string equality against:
   `mj-wrapper`, `mj-section`, `mj-group`, `mj-column`, `mj-column-inner`,
   `mj-text-Frame`, `mj-text`, `mj-image-Frame`, `mj-image`,
   `mj-button-Frame`, `mj-button`, `mj-button-text`, `mj-divider-Frame`,
   `mj-divider`, `mj-spacer`. Case sensitive, `-Frame` suffix capitalized
   exactly as shown.
3. **Every frame in the chain must resolve to a known tag.** The exporter's
   fallback for anything unrecognized is `renderNodeAsImage`: it silently
   flattens the node AND its entire subtree into a hosted PNG. An untagged
   frame between a column and its leaves destroys every well-tagged leaf
   below it. An untagged button becomes a picture of a button with no href.
   Never insert helper/group frames that are not one of the tags above.
4. **Visibility.** `extractNodeJson` returns early on `!node.visible`. Every
   node you create must end `visible = true`.
5. **Both axes, same value.** For horizontal alignment the exporter reads
   `primaryAxisAlignItems` and maps MIN to left, MAX to right, anything else
   (including CENTER) to center. On a VERTICAL frame that mapping is wrong for
   what you see on canvas, so the plugin's own components always set
   `primaryAxisAlignItems` and `counterAxisAlignItems` to the SAME value.
   Do the same on every auto-layout frame you create. The shared value is what
   exports.
6. **Fills discipline.** The exporter treats `fills[0]` as a background signal:
   - leaf wrapper frames (`mj-text-Frame`, `mj-button-Frame`,
     `mj-divider-Frame`, `mj-spacer`) with any visible fill export
     `container-background-color`
   - `mj-image-Frame` must always have `fills = []`
   - columns/sections/wrappers with a fill export `background-color`
   So: set `fills = []` on every frame that has no background in the MJML,
   and one SOLID fill of the exact hex when the MJML sets a background.
7. **itemSpacing = 0 everywhere.** Nonzero itemSpacing makes the exporter emit
   extra `c-gap` raw divs and half-padding CSS. All vertical rhythm in the
   worker JSON is expressed as padding; keep it that way. Not a taller frame
   either: heights hug, spacing is padding, and section 0 is the whole rule.
8. **Ignore `css-class` in the worker JSON.** The exporter regenerates classes
   (UUIDs plus `mj-s`, `mj-c`, `mj-t`, `mj-b` etc.). Never copy them anywhere.
9. **Fonts.** Load every font before setting characters. Map
   `font-family: "Arial, sans-serif"` to Figma family `Arial` (first entry of
   the stack, trimmed). Weight+style map to the Figma style name:

   | font-weight | style (normal) | style (italic) |
   | --- | --- | --- |
   | 100 | Thin | Thin Italic |
   | 200 | Extra Light | Extra Light Italic |
   | 300 | Light | Light Italic |
   | 400 | Regular | Italic |
   | 500 | Medium | Medium Italic |
   | 600 | Semi Bold | Semi Bold Italic |
   | 700 | Bold | Bold Italic |
   | 800 | Extra Bold | Extra Bold Italic |
   | 900 | Black | Black Italic |

   If a family lacks the style, fall back to Regular of the same family, then
   Inter Regular, and note it in your run report.
10. **Line-height.** Worker values are unitless ratios ("1.5"). Set Figma
    `lineHeight = { unit: 'PERCENT', value: ratio * 100 }` (1.5 becomes 150%).
    Exception: a ratio of exactly 1.2 or 1 may be left as `{ unit: 'AUTO' }`;
    the exporter emits AUTO as `1.2`.
11. **Content HTML.** Worker `content` strings may contain inline HTML.
    Convert: `<br>`/`<br/>` to `\n`; `<a href="...">text</a>` to a
    `setRangeHyperlink` on that character range; `<b>`/`<strong>` to the Bold
    style on that range (`setRangeFontName`); strip any other tags. Characters
    must contain no leftover markup.

---

## 2. Root frame (one per MJML document)

Create a top-level FRAME on the target page. When the thing you are building is
a reusable design-system module rather than a one-off email, build the root as
a COMPONENT instead and read section 7 first; everything below applies
unchanged either way.

- **Geometry:** `resize(W, 100)` where `W` = numeric `mj-body` `width`
  (usually `600`), then `layoutMode = 'VERTICAL'` and immediately
  `layoutSizingVertical = 'HUG'`, horizontal FIXED at `W`.
  `primaryAxisAlignItems = counterAxisAlignItems = 'MIN'`. `itemSpacing = 0`,
  all paddings 0.
  The `100` is a throwaway that gets the node onto the canvas; the root's real
  height is whatever its content hugs to, and it must never be left FIXED
  (section 0.1). The width is one of the four load-bearing FIXED widths (0.3).
- **Layer name:** the module/email name (this becomes the component name and
  S3 path if the frame is later promoted, so keep it clean, e.g.
  `[Customer] / banner-bright`). Do NOT put a tag in the root layer name.
- **Shared plugin data (namespace `emaillove`), all REQUIRED:**

  | key | value |
  | --- | --- |
  | `nodeType` | `mainFrame` (this is how the plugin recognizes the template; without it nothing else matters) |
  | `backgroundColor` | dark-mode page background. Use the mj-body/first-wrapper background hex so dark mode matches the design |
  | `contentColor` | dark-mode content/section background. Use the dominant section background hex |
  | `textColor` | dark-mode text color. Use the dominant mj-text `color` |
  | `linkColor` | link color. Use the design link color, else same as textColor |
  | `buttonTextColor` | the button label `color` (e.g. `#FFFFFF`) |
  | `buttonContentColor` | the button `background-color` (e.g. `#2A3C1F`) |
  | `lightThemeBackgroundColor` | the mj-body background hex; exports as mj-body `background-color` (defaults to `#ffffff` when empty) |
  | `fallBackFontName` | `Arial` |

  Empty theme keys are NOT neutral: the exporter substitutes dark defaults
  (`#000000` background, white text), which wrecks a light email. Always set
  all of them. Setting the dark keys equal to the light design colors makes
  dark mode render identical to light, which is the correct behavior for a
  first conversion pass. Where the values come from, in priority order:
  1. If the migration has an established design-system palette (a reviewed
     foundations phase, or theme colors the customer confirmed), use it on
     EVERY module root, identically. Consistency across the system beats
     per-module color matching; modules get restyled by the design system.
  2. Only when no such palette exists yet, derive the keys from THIS module's
     own MJML colors as a stand-in, and flag them for design review.
- Optional: `emailSubject`, `emailPreHeader` (plain strings).
- Also give the root frame a visible SOLID fill of the body background so the
  canvas looks right.
- Children: the `mj-wrapper` frames in document order. After appending each
  wrapper set its `layoutSizingHorizontal = 'FILL'`.

The `mjml`, `mj-head`, `mj-body` tags themselves produce NO Figma nodes; the
exporter reconstructs them (body width comes from the root frame's width).

---

## 3. Containers

### 3.1 mj-wrapper

- Node: FRAME, direct child of the root.
- Shared `name` = `mj-wrapper`.
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG (never FIXED, section
  0.1), horizontal FILL (600 wide),
  `primaryAxisAlignItems = counterAxisAlignItems = 'MIN'`.
- Attribute mapping:

  | MJML attr | Figma property |
  | --- | --- |
  | `padding-top/right/bottom/left` | `paddingTop/Right/Bottom/Left` (parseFloat px) |
  | `background-color` | one SOLID fill; absent means `fills = []` |
  | `border-radius` | `cornerRadius` (or the four per-corner radii for a 4-value string) |
  | `full-width` | shared plugin data `fullWidth` = `'true'` (only if present) |

- Optional shared keys: `stackColumns` (`'true'` default), `reverseStack`.
  They propagate down to child sections that lack their own value.
- Children: `mj-section` frames in order; each gets
  `layoutSizingHorizontal = 'FILL'` after append.
- The exporter reads paddings, fill, radius, and strokes straight off this
  frame and emits them as wrapper attributes.

### 3.2 mj-section

- Node: FRAME, child of a wrapper (or of the root if the MJML has no wrapper).
- Shared `name` = `mj-section`.
- Auto-layout: `layoutMode = 'HORIZONTAL'`, both sizing HUG, then FILL width
  as a child of the wrapper (height stays HUG),
  `primaryAxisAlignItems = counterAxisAlignItems = 'CENTER'`
  (the plugin's own sections are CENTER/CENTER; primary exports as the
  section `text-align`, MIN = left, MAX = right, else center).
- Attribute mapping: same table as wrapper (`padding-*` to paddings,
  `background-color` to fill, `border-radius` to radius). Borders map to
  strokes (see 5.6).
- Geometry matters: exported column widths are computed as
  `columnWidth / (section.width - section.paddingLeft - section.paddingRight) * 100%`.
  With the standard worker output (section 600 wide, padding-left/right 20,
  column width 560) that is exactly 100 percent. Make the section 600 wide
  (FILL under the wrapper) and give it the exact worker paddings, and make
  each column's pixel width match the worker `width` attr.
- Children: `mj-column` frames (or a single `mj-group`) left to right.
  Every child gets `layoutSizingHorizontal` per section 3.4 below.
- Optional shared keys: `stackColumns` = `'false'` to prevent mobile
  stacking without a group; `reverseStack` = `'true'` to reverse stacking
  order on mobile.

### 3.3 mj-group

- Node: FRAME, MUST be a direct child of `mj-section`, never of a column.
- Shared `name` = `mj-group`.
- Auto-layout: `layoutMode = 'HORIZONTAL'`, both sizing HUG (the group's width
  comes from the fixed columns inside it, section 0.3),
  `primaryAxisAlignItems = counterAxisAlignItems = 'CENTER'` (primary exports
  as the group's horizontal alignment; counter exports as `vertical-align`).
- `background-color` to fill, `padding-*` to paddings, `border-radius` to
  radius, borders to strokes.
- Children: two or more `mj-column` frames with FIXED pixel widths.
- Width math: the exporter emits the group width as
  `group.width / (section.width - section horizontal padding) * 100%`, and
  each inner column as `column.width / (group.width - group horizontal padding) * 100%`.
  MJML requires percentage columns inside a group; you get that for free by
  setting exact pixel widths and letting the exporter divide. Example: group
  560 wide containing columns 280 + 280 exports 50%/50%.
- Columns inside a group keep their elements side by side on mobile.

### 3.4 mj-column

- Node: FRAME, child of `mj-section` or `mj-group`.
- Shared `name` = `mj-column`.
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG, never FIXED. A column
  is the frame most often left at a fixed height by mistake, and it is the one
  where Outlook clipping bites hardest, because every leaf in the email hangs
  off a column (section 0.1).
- Horizontal sizing, per section 0.3:
  - **Single column in its section: FILL.** It resolves to the section content
    box, which is the worker `width` when you have reproduced the section's
    width and paddings exactly, and it exports `width: 100%`. FILL keeps
    tracking that content box if a padding value is later corrected. An
    explicit FIXED at the worker width is acceptable and exports identically;
    never use HUG, which collapses the column to its content.
  - **Two or more columns in one section, or any column inside an `mj-group`:
    FIXED at the worker `width` (e.g. 280, 200).** This is load bearing. The
    exported percentage is derived from the pixel number, so unequal splits and
    group percentages only survive when every column is pinned.
- **Axis alignment rule (the trap):** set BOTH axes to the dominant
  horizontal alignment of the column's content:
  - content `align="left"` (or mixed/default): `MIN` / `MIN`
  - content `align="center"`: `CENTER` / `CENTER`
  - content `align="right"`: `MAX` / `MAX`

  Why: `counterAxisAlignItems` drives the column-level
  `text-align: <value> !important` CSS the exporter writes, and
  `primaryAxisAlignItems` exports as the column `vertical-align`
  (MIN = top, MAX = bottom, else middle). The plugin's own components accept
  this coupling (a centered column exports `vertical-align: middle`), and for
  hug-height columns the vertical value is visually irrelevant. Do NOT try to
  honor the worker's `vertical-align: top` on a centered column; horizontal
  fidelity wins.
- Attribute mapping:

  | MJML attr | Figma property |
  | --- | --- |
  | `width` | frame width in px: FILL for a lone column, FIXED at this number for multi-column and group columns (above) |
  | `padding-*` | paddings |
  | `background-color` | SOLID fill; absent means `fills = []` (any fill at all exports as background-color, even at opacity 0, so leave fills truly empty) |
  | `border-radius` | cornerRadius |
  | `border` / `border-*` | strokes (see 5.6) |

- Children: leaf PAIR wrapper frames (`mj-text-Frame`, `mj-image-Frame`,
  `mj-button-Frame`, `mj-divider-Frame`) and `mj-spacer`, top to bottom.
  After appending, set each child's `layoutSizingHorizontal = 'FILL'`.

### 3.5 mj-column-inner (rarely needed)

Use ONLY when a column needs a second, inner background/border box distinct
from its own (card inside a colored column). Most card-in-column designs are
expressible without it: put the card fill, radius, and paddings directly on
the `mj-column` and the outer color on the section. Prefer that.

If you must use it:

- Node: FRAME, the FIRST (and only) child of an `mj-column`; the leaves move
  inside it. This is load bearing: the exporter checks `column.children[0]`
  and ONLY there. In any other position the node renders fine on canvas but
  its fill, radius, borders, and paddings are silently discarded on export
  and its children flatten into the parent. If a card sits below other
  content in a column, split the section so the card gets its own dedicated
  column with the `mj-column-inner` as sole first child.
- Shared `name` = `mj-column-inner`.
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG (never FIXED, even when
  the card looks like a fixed box in the source), horizontal FILL,
  `primaryAxisAlignItems = counterAxisAlignItems = 'CENTER'`.
- Inner background color to fill, inner radius to cornerRadius, inner
  borders to strokes, inner paddings to paddings.
- The exporter detects it by checking the column's `children[0]` tag and
  emits `inner-background-color`, `inner-border-radius`, `inner-border-*`,
  merging inner paddings into per-child CSS.

---

## 4. Leaf pairs

Every content leaf is TWO tagged nodes: an outer wrapper FRAME that carries
layout (paddings, alignment, container background) and an inner node that
carries content. Style the inner node, not the wrapper. Both must be tagged.
A wrapper with a fill and no child exports as an empty cell.

Every pair wrapper hugs vertically. A leaf's height is its content plus the
wrapper's padding, and nothing else: never a height you typed (section 0.1).
`mj-spacer` in 4.5 is the one node that breaks this, deliberately.

### 4.1 mj-text: `mj-text-Frame` wrapping a TEXT node `mj-text`

Wrapper FRAME:
- Shared `name` = `mj-text-Frame`. Layer name e.g. `Text Block`.
- `layoutMode = 'HORIZONTAL'` (yes, horizontal), vertical HUG, never FIXED:
  a pinned text frame is the classic Outlook clip, because copy length is the
  thing that changes most often between sends.
  `primaryAxisAlignItems = counterAxisAlignItems = 'CENTER'`.
- `padding-*` from the mj-text attrs go HERE (the exporter reads
  `node.parent.paddingTop` etc. off this frame).
- `fills = []` unless the MJML has `container-background-color`, which
  becomes this frame's SOLID fill.
- As a column child: `layoutSizingHorizontal = 'FILL'`.

Inner TEXT node (direct child):
- Shared `name` = `mj-text`.
- `layoutSizingHorizontal = 'FILL'`, `layoutSizingVertical = 'HUG'` (so
  `node.width` equals the column content width; alignment happens inside the
  text box).
- Property mapping (all read back by `extractTextJson`):

  | MJML attr | TEXT property |
  | --- | --- |
  | `align` | `textAlignHorizontal` = LEFT / CENTER / RIGHT (this is the ONLY source of the exported `align`) |
  | `color` | one SOLID fill |
  | `font-family` | `fontName.family` (first of the stack) |
  | `font-weight` + `font-style` | `fontName.style` per the table in rule 9 |
  | `font-size` | `fontSize` (px number) |
  | `line-height` | `lineHeight` PERCENT (ratio * 100), AUTO allowed for 1.2/1 |
  | `letter-spacing` | `letterSpacing` `{ unit: 'PIXELS' }` |
  | `text-transform` | `textCase`: uppercase = UPPER, lowercase = LOWER, capitalize = TITLE, none = ORIGINAL |
  | `text-decoration` | `textDecoration`: underline = UNDERLINE, line-through = STRIKETHROUGH, none = NONE |
  | `content` | `characters` after HTML conversion (rule 11); links via `setRangeHyperlink` |

- Also set `textAlignVertical = 'CENTER'`.

### 4.2 mj-image: `mj-image-Frame` wrapping a RECTANGLE `mj-image`

Wrapper FRAME:
- Shared `name` = `mj-image-Frame`. Layer name e.g. `Image Block`.
- `layoutMode = 'HORIZONTAL'`, both sizing HUG (FILL width as column child,
  height stays HUG so it takes the rectangle's height).
- `primaryAxisAlignItems` from `align`: left = MIN, right = MAX, center or
  absent = CENTER. Set `counterAxisAlignItems` to the SAME value.
- `padding-*` from the mj-image attrs go HERE.
- `fills = []` ALWAYS.
- Never copy the rectangle's height onto this frame. The wrapper hugs; the
  rectangle carries the pixels.

Inner RECTANGLE (direct child):
- Shared `name` = `mj-image`.
- `resize(width, height)` from the MJML `width`/`height` attrs (numeric px).
  Keep `layoutSizingHorizontal = 'FIXED'` so the rectangle keeps its size.
  A RECTANGLE is not a frame: it has no hug, and its pixel size is one of the
  four load-bearing FIXED widths in section 0.3. This is the one place in a
  module where a hard height is expected, and it is safe because a rectangle
  has no children to clip.
- Fill: if the worker `src` is a real URL, create the image via
  `figma.createImageAsync(src)` and set an IMAGE fill, `scaleMode: 'FILL'`.
  If `src` is `"placeholder"` or unavailable, substitute the matching asset
  already round-tripped into the target file's foundations pages when one
  exists (logos especially); otherwise use one SOLID light gray fill
  (`#E8E8E8`). The exporter re-exports the node's own pixels to S3, so a
  gray rect exports as a gray image, which is correct placeholder behavior.
- `cornerRadius` from `border-radius` (exporter emits the max of wrapper and
  rectangle radius; setting it on the rectangle is sufficient).
- Shared plugin data ON THE RECTANGLE (not the wrapper):

  | key | from |
  | --- | --- |
  | `href` | MJML `href` (omit when absent; never write `#`) |
  | `altText` | MJML `alt` |

- Sizing note: if the rectangle width is LESS than the column content width
  the exporter drops `fluid-on-mobile` (class `lf`); if equal it keeps it
  (`nf`). So match the worker `width` exactly: a 560 image in a 560 column
  stays fluid, a 134 logo does not. This is automatic; just get the px right.

### 4.3 mj-button: `mj-button-Frame` wrapping FRAME `mj-button` whose DIRECT child is a TEXT node

Three levels. The TEXT node MUST be a direct child of the `mj-button` frame:
`extractButtonJson` locates it via `node.children.find(c => c.type === 'TEXT')`.

Level 1, wrapper FRAME:
- Shared `name` = `mj-button-Frame`. Layer name e.g. `Button Block`.
- `layoutMode = 'HORIZONTAL'`, both sizing HUG (FILL width as column child,
  height stays HUG).
- `primaryAxisAlignItems` from the mj-button `align` (left = MIN,
  right = MAX, else CENTER); `counterAxisAlignItems` = SAME value.
  The exporter reads the button's alignment from this frame, the button's
  direct parent (`getPrimaryAlign(node.parent, 'row')`). Also mirror the
  same alignment on the containing column's axes when all of the column's
  content shares it (see 3.4); the two must not fight.
- `padding-*` from the mj-button attrs go HERE.
- `fills = []` unless `container-background-color` is set.

Level 2, FRAME `mj-button`:
- Shared `name` = `mj-button`.
- `layoutMode = 'HORIZONTAL'`, `layoutSizingVertical = 'HUG'` always (the
  height is text height plus `inner-padding`, never a number you set), and
  `layoutSizingHorizontal` per section 0.4, because **width here is a mobile
  behavior decision, not a cosmetic one**:
  - `'HUG'` exports an auto-width button and the plugin keeps that width on
    mobile. Worker buttons are auto width, so HUG is the default.
  - `'FILL'` exports a full-width button, sets `applyFullWidth`, and the plugin
    automatically makes it full width on mobile (`width: 100%`). Choose it when
    the source design shows an edge to edge CTA, and say so in your report.
  - `'FIXED'` exports an explicit `width` and also keeps that width on mobile.
    Only when the design system pins a button width.
- `primaryAxisAlignItems` from `text-align` (default CENTER);
  `counterAxisAlignItems = 'CENTER'`.
- `background-color` to one SOLID fill (a missing fill exports
  `background-color: transparent`).
- `border-radius` to `cornerRadius` (e.g. 25).
- `border` shorthand (e.g. `2px solid #1A1A4B`) to strokes:
  `strokes = [SOLID color]`, `strokeWeight = weight`. `border: 0px` means no
  strokes.
- `inner-padding` `"T R B L"` to paddings: `paddingTop = T`,
  `paddingRight = R`, `paddingBottom = B`, `paddingLeft = L`
  (e.g. `15px 25px 15px 25px` gives 15/25/15/25). Symmetric values are safe;
  note the plugin's own re-import of asymmetric inner-padding swaps
  left/right, so avoid asymmetric inner padding. This padding is the button's
  tap target and the only thing that sets its height, so check the result is at
  least 44px tall rather than reaching for a fixed height.
- Shared plugin data ON THIS FRAME:

  | key | from |
  | --- | --- |
  | `href` | MJML `href` (omit when absent) |

Level 3, TEXT node (direct child of the `mj-button` frame):
- Shared `name` = `mj-button-text`. Layer name e.g. `Button Text`.
- `characters` = the button `content` (plain text, rule 11).
- Font family/style/size/line-height/text-transform/text-decoration mapped
  exactly as in 4.1, from the mj-button attrs.
- `color` attr to the TEXT fill (this exports as the button label color).
- `textAlignHorizontal = 'CENTER'`, `textAlignVertical = 'CENTER'`.
- `layoutSizingHorizontal = 'HUG'`, `layoutSizingVertical = 'HUG'`.

The exported button `height` is read from the `mj-button` frame's height
(auto: text height + vertical inner padding) and the font attributes are read
from the TEXT child. Do not add any other children (no icons in this spec's
scope; icon frames have their own `beforeIcon-Frame`/`afterIcon-Frame` tags
and are out of scope).

### 4.4 mj-divider: `mj-divider-Frame` wrapping a LINE `mj-divider`

Wrapper FRAME:
- Shared `name` = `mj-divider-Frame`. Layer name e.g. `Divider`.
- `layoutMode = 'HORIZONTAL'`, vertical HUG, FILL width as column child. Space
  above and below a rule is this frame's padding, never its height.
- `primaryAxisAlignItems` from `align` (default CENTER);
  `counterAxisAlignItems` = SAME value... the exporter reads divider `align`
  from this wrapper via `getPrimaryAlign(node.parent, 'row')`, same pattern
  as buttons and images.
- `padding-*` from the mj-divider attrs go HERE.
- `fills = []` unless `container-background-color`.

Inner LINE node (use `figma.createLine()`, not a rectangle: the exporter
reads `strokes`, `strokeWeight`, and `dashPattern`):
- Shared `name` = `mj-divider`.
- `strokes = [SOLID <border-color>]` (default `#000000`).
- `strokeWeight` = numeric `border-width` (default 1).
- `dashPattern`: `[]` for solid, `[4, 4]` for dashed, `[1, 2]` for dotted.
- `resize(W, 0)` where W = numeric `width` if given in px, else the column
  content width; then `layoutSizingHorizontal = 'FILL'` for a full-width
  divider. The exporter emits `width: <node.width>px`. A LINE is not a frame
  and has no hug; its zero height is the geometry of a line, not a sizing
  choice.

### 4.5 mj-spacer: single FRAME (no pair), and the one fixed height in the spec

**Try not to need one.** The product docs are explicit that padding beats
spacers, and section 0.2 says how: when the worker JSON hands you a spacer whose
only job is a gap between two blocks, fold its height into the padding of the
neighboring element and drop it. Build the spacer only when the design needs a
standalone gap of its own, for example a colored band or a gap inside a bordered
column.

When you do build one:

- Node: FRAME, direct child of the column.
- Shared `name` = `mj-spacer`. Layer name e.g. `Spacer`.
- `layoutMode = 'HORIZONTAL'`, `fills = []` (any visible fill exports as
  `container-background-color`).
- `resize(width, H)` with H = numeric `height` attr, then
  `layoutSizingVertical = 'FIXED'` and `layoutSizingHorizontal = 'FILL'` as a
  column child. The exporter emits `height: <node.height>px`.
- **This is the only FIXED vertical sizing anywhere in this spec**, and it is
  load bearing: the exported height is read straight off the node, and a spacer
  has no children to clip. It is not a precedent for any other node.
- `padding-*` attrs map to the frame's paddings.
- No children.

---

## 5. Cross-cutting attribute rules

### 5.1 Padding

Worker `padding-top/right/bottom/left` are always explicit px strings.
`parseFloat` them onto the OWNING frame per the tables above. Rules of thumb:
container tags (wrapper/section/column/group/column-inner) carry their own
paddings; leaf tags carry theirs on the PAIR WRAPPER frame (the exporter
reads `node.parent.padding*` for text, button, image, divider). A shorthand
`padding` attr, if ever present, expands CSS-style before mapping.

Padding is also the only mechanism for vertical rhythm, and section 0.5 has the
level-by-level table with the documented typical ranges for any gap the worker
JSON does not already specify.

### 5.2 Colors

All colors are hex strings. One SOLID fill per background; TEXT fills for
text color. `transparent` or absent means `fills = []`. The exporter converts
`fills[0].color` back to hex and ignores opacity everywhere except the
text/button/spacer container checks, so never leave a "hidden" 0-opacity
fill lying around.

### 5.3 Alignment master table

| Node | Property read by exporter | Exported as |
| --- | --- | --- |
| `mj-section` | `primaryAxisAlignItems` ('row' map) | section `text-align` |
| `mj-group` | `primaryAxisAlignItems` ('row'), `counterAxisAlignItems` ('row') | group left/right class, `vertical-align` |
| `mj-column` | `primaryAxisAlignItems` ('col' map: MIN top, MAX bottom, else middle) | column `vertical-align` |
| `mj-column` | `counterAxisAlignItems` ('col' map: MIN left, MAX right, else center) | column-level `text-align !important` CSS |
| TEXT `mj-text` | `textAlignHorizontal` | text `align` |
| `mj-image-Frame` | `primaryAxisAlignItems` ('row') | image `align` |
| `mj-button-Frame` | `primaryAxisAlignItems` ('row') | button `align` |
| `mj-button` | `primaryAxisAlignItems` ('row') | button `text-align` |
| `mj-divider-Frame` | `primaryAxisAlignItems` ('row') | divider `align` |

'row' map: MIN = left, MAX = right, anything else = center. Always set the
counter axis to the same value as the primary on every one of these frames.

### 5.4 Column width handling

- Single column: section 600 wide with `padding-left/right: 20px` and a FILL
  column (which resolves to 560) exports `width: 100%`; a column pinned FIXED
  at 560 exports the same thing. FILL is preferred because it keeps tracking
  the content box (section 0.3). Always reproduce the worker's exact px on the
  section so that content box is right.
- Multi column: widths export as percentages of the section content box.
  280 + 280 in a 560 content box gives 50% + 50%. The worker may bake gutters
  as column paddings (e.g. `padding-right: 10px` on the left column); keep
  those as paddings, do NOT convert them to itemSpacing.
- Inside `mj-group`: same math against the group's content box; MJML gets the
  required percentage widths automatically.

### 5.5 href and alt

`href` and `alt` NEVER live in layer names or geometry; they are shared
plugin data: `href` on the `mj-image` rectangle and on the `mj-button` frame;
`altText` on the `mj-image` rectangle. Omit the key entirely when the worker
value is empty or `#`.

### 5.6 Borders

Per-side `border-top/right/bottom/left` ("Wpx style #hex"): set
`strokes = [SOLID hex]` plus `strokeTopWeight` etc. per side (0 for absent
sides). Uniform `border` shorthand: `strokes` + `strokeWeight`. Dashed and
dotted map to `dashPattern` `[4,4]` / `[1,2]`. The exporter reads stroke
color from `strokes[0]` and per-side weights.

---

## 6. Layer names: friendly on the canvas, the tag in plugin data

Every node carries two names, read by two different audiences:

- `node.name`, the Figma layer name, is for the human who opens the file.
- the plugin data key `name` (shared namespace `emaillove`) is the MJML tag.

**The exporter never reads the layer name for dispatch.** It resolves the tag
through `getMetaName(node)`, which reads plugin data `name` first (private,
then the shared `emaillove` namespace) and falls back to `node.name` only when
both are empty. Every branch of the export tree walker keys off that resolved
tag. So a friendly layer name cannot break the export, as long as the plugin
data tag is there. The plugin does exactly this to its own nodes: it writes the
friendly string to the layer name and the tag to plugin data in the same
breath.

Name every node you create twice:

```js
const section = figma.createFrame()
section.name = 'Row (Contains columns that sit side by side)'   // for humans
section.setSharedPluginData('emaillove', 'name', 'mj-section')  // for the plugin
```

Use the display names in 6.1. They are the plugin's own strings, so a converted
file reads identically to one the plugin built, and a designer opening the
layers panel sees the same vocabulary the plugin's UI uses.

Three ways this goes wrong:

1. **Skipping the plugin data write and relying on the fallback.** Do not. The
   plugin has a helper (`enableVariableNaming`) that copies `node.name` into
   plugin data `name` for any node whose plugin data `name` is empty. Once that
   runs, the friendly label IS the tag, permanently, and the node matches no
   branch in the exporter. Write the tag at creation time on every node.
2. **Putting the friendly name in plugin data.** The plugin data value must be
   either the bare tag (`mj-section`) or the parsed form
   `Friendly, (mjml:mj-section)`. A friendly-only value is read whole as the
   tag, matches nothing, and the node is dropped with no error. Extra props
   ride in the same string when needed: `, (type:link)`, `, (group:Button)`.
3. **Button icon frames are the one exception, and they are a real trap.** The
   library-save and template-upload path finds a button's icon frames by a RAW
   layer-name substring check (`c.name.includes('beforeIcon-Frame')`), not
   through `getMetaName`. The HTML export path uses `getMetaName` and is fine.
   So a button whose icon frames carry only the friendly names loses its icons
   when the component is saved to the library. If you build button icons at
   all, keep the literal substring `beforeIcon-Frame` / `afterIcon-Frame` in
   the layer name. Button icons are out of scope for this spec's leaf set
   (section 4.3), so the safe move is not to build them here.

The root is the one node this spec gives no tag: it is identified by
`nodeType = mainFrame`, and its layer name is the module or email name
(section 2), which also becomes the component name when it is saved into the
plugin. Keep that name clean and do not put a tag in it.

### 6.1 Display names by tag

| tag (plugin data `name`) | Figma layer name (`node.name`) |
| --- | --- |
| `mj-body` | Email Canvas |
| `mj-wrapper` | Wrapper (Groups rows and sets the background for this section ) |
| `mj-section` | Row (Contains columns that sit side by side) |
| `mj-column` | Column (Your images, text, buttons, and other content go in here) |
| `mj-column-inner` | Inner Column |
| `mj-group` | Group (Groups columns together for responsive stacking) |
| `mj-text-Frame` | Text Block |
| `mj-text` | Text |
| `mj-image-Frame` | Image Block |
| `mj-image` | Image |
| `mj-button-Frame` | Button Block |
| `mj-button` | Button |
| `mj-button-text` | Button Text |
| `mj-hero-Frame` | Hero Block |
| `mj-hero` | Hero |
| `mj-hero-Image` | Hero Image |
| `mj-divider-Frame` | Divider |
| `mj-divider` | Divider Line |
| `mj-raw` | Code Block |
| `mj-raw-text` | Code Text |
| `mj-spacer` | Spacer |
| `mj-social` | Social Bar |
| `mj-social-element` | Social Icon |
| `mj-navbar` | Nav Bar |
| `mj-navbar-link` | Nav Link |
| `mj-nav-text` | Nav Text |
| `mj-table` | Table |
| `mj-table-row` | Table Row |
| `mj-table-column` | Table Cell |
| `mj-table-text` | Table Text |
| `mj-table-image` | Table Image |
| `beforeIcon-Frame` | Before Icon (but see failure 3 above) |
| `afterIcon-Frame` | After Icon (but see failure 3 above) |

Reproduce these strings verbatim, including the stray space before the closing
paren in the wrapper string; that is what the plugin writes, and matching it
keeps diffs and comparison tooling clean. Any tag not listed uses the tag
itself as the layer name.

You may append a short human qualifier when a module holds several of the same
block and the distinction helps a reviewer ("Text Block / eyebrow"). Avoid the
comma form there, since `Label, (mjml:mj-text)` is the parsed tag syntax and a
comma reads as the start of one. Never prepend anything that looks like a tag,
and never let the qualifier replace the display name.

---

## 7. Components: when a node is a COMPONENT instead of a FRAME

**Make it a COMPONENT when it is meant to be reused**: a converted design-system
module, a section you built to fill a gap and intend to save into the library,
a foundations button or badge that other modules instance. Keep it a FRAME when
it is a one-off campaign email that nobody will instance.

This is safe. Confirmed against the plugin source:

- **Export accepts a COMPONENT everywhere it accepts a FRAME.** The export
  gate whitelists `FRAME`, `INSTANCE`, `COMPONENT` at the root and at every
  container level, and the root branch is `nodeType === 'mainFrame'` plus that
  whitelist. The HTML export path has no node-type check on the root at all.
- **Add New Template accepts a COMPONENT.** The whole-email branch tests plugin
  data only (`nodeType === 'mainFrame'`), never `node.type`. The save-a-module
  branch clones your selection into a temporary frame it creates itself, which
  is the plugin's own established move.
- **The plugin already does this.** Every `mj-wrapper` the plugin renders is
  created as a COMPONENT, not a FRAME. Purple components inside a plugin-built
  email are normal. Do not "fix" them into frames.
- **Instances work.** `INSTANCE` is in the same whitelist and an instance
  surfaces the main component's plugin data, so a customer who places an
  instance of a componentized module still exports correctly.

The calls, either at creation or by promoting a finished frame:

```js
// build it as a component from the start...
const moduleRoot = figma.createComponent()      // instead of figma.createFrame()
// ...or promote the frame you already finished:
const moduleRoot = figma.createComponentFromNode(frame)

moduleRoot.name = 'Hero, text led'              // becomes the saved component name
moduleRoot.setSharedPluginData('emaillove', 'nodeType', 'mainFrame')
```

Everything else in this spec applies unchanged: a ComponentNode supports the
same auto-layout, sizing, padding, fill, resize, and plugin data calls the frame
sections use.

Four rules keep a COMPONENT root working:

1. **Keep it a direct child of the page.** The plugin's template discovery
   enumerates DIRECT page children and filters on plugin data. A root that gets
   pulled into a COMPONENT_SET (someone adds variants to it) is no longer a page
   child and vanishes from the plugin's template picker. Never combine template
   roots into a variant set. A Figma SECTION swallows a root the same way, and
   that hazard applies to FRAME roots too.
2. **Do not leave instances of a template root on the page.** Instances inherit
   the main component's plugin data, which is the mechanism the plugin relies on
   elsewhere, so an instance of a template root also reads as a template. If you
   need to show a module in use, place it inside an email root, not loose on the
   library page.
3. **Properties go on the component that owns the node** (section 8). Because
   every `mj-wrapper` is itself a COMPONENT, a root component cannot bind a
   property to anything inside its wrapper components: Figma rejects
   `componentPropertyReferences` on an instance sublayer. Bind at the level that
   directly owns the node.
4. **Do not write `isStandalone`.** The shipped plugin build ignores that key
   entirely (it is behind a compile-time flag that is off), so a "standalone"
   section or hero sitting directly under the root gets no wrapper-level
   controls in the properties sidebar and is not eligible for the Upload button.
   Keep `mj-wrapper` as the top-level block boundary and put properties on the
   wrapper-level component.

---

## 8. Component properties

Properties turn a rebuilt module into something a marketer can use without
opening it. They are an agent-side layer on top of the plugin's plugin data
model: the plugin neither writes nor reads them, and they change nothing about
the export except through `visible` (see 8.2).

Three hard constraints before any code:

- `addComponentProperty` exists **only** on ComponentNode and ComponentSetNode.
  A FrameNode does not have the method. Convert first (section 7).
- The property id that comes back is **suffixed** (`Body#12:3`). Always bind and
  set with the returned id, never with the bare name.
- Figma refuses `componentPropertyReferences` on an **instance sublayer**. The
  property must be added to the component that directly contains the node you
  are binding.

There are exactly four property types: BOOLEAN, TEXT, INSTANCE_SWAP, VARIANT.
**There is no image property type**, so an `mj-image` fill cannot be exposed as
a property; image swapping stays a plugin-side fill edit.

### 8.1 TEXT, bound to `characters`, for copy that changes per send

Bind the inner TEXT node, never the wrapper: the `mj-text` node inside a
`mj-text-Frame`, or `mj-button-text`, `mj-nav-text`, `mj-table-text`.

```js
const headline = moduleRoot.addComponentProperty('Headline', 'TEXT', textNode.characters)
textNode.componentPropertyReferences = { characters: headline }
// later, on an instance:
instance.setProperties({ [headline]: 'New headline' })
```

`characters` is only valid on a TextNode. This is safe for export because the
exporter reads the live `characters` off the node at extract time.

### 8.2 BOOLEAN, bound to `visible`, for optional regions

Bind the block-level wrapper frame, never the inner leaf: the
`mj-button-Frame` for an optional CTA, the `mj-image-Frame` for an optional
image, the eyebrow's `mj-text-Frame`.

```js
const showBtn = moduleRoot.addComponentProperty('Show Button', 'BOOLEAN', true)
ctaFrame.componentPropertyReferences = { visible: showBtn }
```

This composes exactly with the exporter, which returns early on any node where
`visible` is false. Flipping the boolean off on an instance genuinely removes
the block from the exported MJML and HTML rather than shipping a hidden
element.

### 8.3 INSTANCE_SWAP, bound to `mainComponent`, for style variants

Bind an INSTANCE node inside the module, in practice the button instance
pointing at a foundations button.

```js
const style = moduleRoot.addComponentProperty(
  'Button Style',
  'INSTANCE_SWAP',
  primaryButton.key,          // the default the instance starts on
  {
    preferredValues: [
      { type: 'LOCAL_COMPONENT', key: primaryButton.key },
      { type: 'LOCAL_COMPONENT', key: inverseButton.key },
      { type: 'LOCAL_COMPONENT', key: textLink.key },
    ],
  },
)
buttonInstance.componentPropertyReferences = { mainComponent: style }
```

For a published library component the default value is the component `key`. A
local component's node id also resolves in practice.

### 8.4 VARIANT

Only meaningful on a ComponentSetNode, and added to the set rather than to a
member. Skip it for email modules unless you deliberately want a variant set,
and remember rule 1 in section 7: a template root inside a component set
disappears from the plugin's picker.

### 8.5 Which properties to add

**A property whose binding is wrong is worse than no property.** It looks
editable in the panel, does nothing or edits the wrong node, and the person who
trusted it ships the mistake. Bind fewer things, and verify every binding by
reading `componentPropertyReferences` back off the node after you set it.

Derive properties from evidence, not from imagination:

- A BOOLEAN needs a sibling design in the source library where that region is
  genuinely absent.
- A TEXT needs evidence that the copy actually changes between sends (different
  values across variants, a template variable in the source, a date or offer).
- Boilerplate stays unbound: mailing address, legal lines, standing disclosures.
- Two to five properties per module is the working range. Zero is a legitimate
  answer for a module with no text node and no optional region, for example a
  fixed logo header. Four good properties beat twenty; a cluttered panel gets
  ignored.

Name properties in plain language ("Show Button", "Headline", "Body", "Button
Style") and reuse the same names across modules so the panel reads consistently
system-wide.

**The known failure:** a button label that lives on a sublayer inside a nested
button instance cannot be bound from the module. The fix is to add the TEXT
property to the foundations button component itself and let it surface through
the instance. Same rule as always: put the property on the component that owns
the node.

---

## 9. Post-build checklist (run per module before handing off)

1. Root has shared `nodeType = mainFrame` plus ALL theme color keys and
   `lightThemeBackgroundColor`.
2. Every FRAME/RECT/LINE/TEXT you created has shared `name` set to exactly
   one known tag; zero untagged frames anywhere in the tree. No node is
   relying on the layer-name fallback.
3. Every node's layer name is the display name for its tag (section 6.1), and
   no friendly string was written into the plugin data `name` key.
4. Every leaf is a complete pair; every `mj-button` has a direct TEXT child;
   no empty wrapper frames.
5. `primaryAxisAlignItems === counterAxisAlignItems` on every auto-layout
   frame.
6. All nodes `visible = true` (except a region you deliberately left off via a
   BOOLEAN default); `itemSpacing = 0` everywhere; no stray fills.
7. **Every frame in the tree has `layoutSizingVertical === 'HUG'`.** Walk the
   whole tree and check, root included. The only FIXED height allowed is on an
   `mj-spacer`; the only hard heights are on the `mj-image` rectangle and the
   `mj-divider` line, neither of which is a frame. Anything else pinned is an
   Outlook clip waiting to happen (section 0.1).
8. **Every FIXED width is one of the four load-bearing cases** (root, columns
   in a multi-column section, columns in a group, the image rectangle). Lone
   columns are FILL, groups and buttons are HUG (section 0.3).
9. **Every button's width sizing was a decision.** HUG unless the design calls
   for a full-width CTA, in which case FILL, which is also what makes it full
   width on mobile (section 0.4). Buttons are at least 44px tall, from
   `inner-padding` rather than a set height.
10. All vertical spacing is padding: no gaps produced by a taller frame, by
    `itemSpacing`, or by a manually positioned node (which exports as nothing).
11. Root width equals the mj-body width; column px widths equal the worker
    attrs; section paddings equal the worker attrs.
12. If the module is reusable: the root is a COMPONENT, a direct child of the
    page, not inside a COMPONENT_SET or a Figma SECTION, with no stray instances
    of it left on the page.
13. Every component property you added was re-read back off the node to confirm
    the binding landed, and each one has a reason you can state in the report.
14. No em dashes in any layer name, plugin data value, or text characters.
15. Compare a fresh screenshot of the frame against the source screenshot you
    converted from, for spacing, alignment, and color parity. Small color and
    font-metric differences are acceptable; missing content, zero-height
    sections, clipped text, and alignment flips are not.
