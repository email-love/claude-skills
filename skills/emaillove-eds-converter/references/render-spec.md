# Render spec: design-converter MJML JSON to plugin-valid Figma frames

Audience: render agents transcribing the MJML JSON returned by the
design-converter worker (SKILL.md, Phase 3 step 1) into Figma frames that the
Email Love plugin will preview and export correctly. You may ONLY use what an
external agent can write: layer names, geometry, auto-layout,
fills/strokes/radii, TEXT node properties, and
`setSharedPluginData('emaillove', key, value)`.

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

## 1. Non-negotiable ground rules

1. **Tag every node via shared plugin data.** The plugin identifies a node with
   `getMetaName(node)`: it reads the plugin data key `name` first (private, with
   fallback to the shared `emaillove` namespace since commit f60c404,
   2026-07-24), else the Figma layer name. Always write
   `node.setSharedPluginData('emaillove', 'name', '<exact tag>')`.
   The layer name is then free for a human label ("Hero Text", "CTA Button").
   If you skip the shared key, the layer name itself must be either the bare
   tag (`mj-section`) or the parsed form `Label, (mjml:mj-section)`. A layer
   named `mj-section - Report CTA` with no shared key FAILS: the whole string
   is read as the tag.
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
   worker JSON is expressed as padding; keep it that way.
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

Create a top-level FRAME on the target page:

- **Geometry:** `resize(W, 100)` where `W` = numeric `mj-body` `width`
  (usually `600`), then `layoutMode = 'VERTICAL'`,
  `layoutSizingVertical = 'HUG'`, horizontal FIXED at `W`.
  `primaryAxisAlignItems = counterAxisAlignItems = 'MIN'`. `itemSpacing = 0`,
  all paddings 0.
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
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG, horizontal FILL
  (600 wide), `primaryAxisAlignItems = counterAxisAlignItems = 'MIN'`.
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
- Auto-layout: `layoutMode = 'HORIZONTAL'`, both sizing HUG (then FILL width
  as a child), `primaryAxisAlignItems = counterAxisAlignItems = 'CENTER'`
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
- Auto-layout: `layoutMode = 'HORIZONTAL'`, both sizing HUG,
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
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG.
  Horizontal sizing: FIXED at the worker `width` (e.g. 560, 280). Only use
  HUG when the section has a single column and you have verified the hug
  width equals the worker width. When multiple columns share a section, all
  must be FIXED so the exported percentages are stable.
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
  | `width` | frame width in px (FIXED) |
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
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG, horizontal FILL,
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

### 4.1 mj-text: `mj-text-Frame` wrapping a TEXT node `mj-text`

Wrapper FRAME:
- Shared `name` = `mj-text-Frame`. Layer name e.g. `Text Block`.
- `layoutMode = 'HORIZONTAL'` (yes, horizontal), vertical HUG,
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
- `layoutMode = 'HORIZONTAL'`, both sizing HUG (FILL width as column child).
- `primaryAxisAlignItems` from `align`: left = MIN, right = MAX, center or
  absent = CENTER. Set `counterAxisAlignItems` to the SAME value.
- `padding-*` from the mj-image attrs go HERE.
- `fills = []` ALWAYS.

Inner RECTANGLE (direct child):
- Shared `name` = `mj-image`.
- `resize(width, height)` from the MJML `width`/`height` attrs (numeric px).
  Keep `layoutSizingHorizontal = 'FIXED'` so the rectangle keeps its size.
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
- `layoutMode = 'HORIZONTAL'`, both sizing HUG (FILL width as column child).
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
- `layoutMode = 'HORIZONTAL'`, `layoutSizingHorizontal = 'HUG'`,
  `layoutSizingVertical = 'HUG'` (HUG exports an auto-width button; FIXED
  exports an explicit `width`; FILL exports a full-width button and sets
  `applyFullWidth`). The worker buttons are auto width: use HUG.
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
  left/right, so avoid asymmetric inner padding.
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
- `layoutMode = 'HORIZONTAL'`, vertical HUG, FILL width as column child.
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
  divider. The exporter emits `width: <node.width>px`.

### 4.5 mj-spacer: single FRAME (no pair)

- Node: FRAME, direct child of the column.
- Shared `name` = `mj-spacer`. Layer name e.g. `Spacer`.
- `layoutMode = 'HORIZONTAL'`, `fills = []` (any visible fill exports as
  `container-background-color`).
- `resize(width, H)` with H = numeric `height` attr, then
  `layoutSizingVertical = 'FIXED'` and `layoutSizingHorizontal = 'FILL'` as a
  column child. The exporter emits `height: <node.height>px`.
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

- Single column: section 600 wide with `padding-left/right: 20px` and column
  FIXED 560 exports `width: 100%`. Column FIXED 600 in an unpadded section
  also exports 100%. Always reproduce the worker's exact px.
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

## 6. Post-build checklist (run per module before handing off)

1. Root has shared `nodeType = mainFrame` plus ALL theme color keys and
   `lightThemeBackgroundColor`.
2. Every FRAME/RECT/LINE/TEXT you created has shared `name` set to exactly
   one known tag; zero untagged frames anywhere in the tree.
3. Every leaf is a complete pair; every `mj-button` has a direct TEXT child;
   no empty wrapper frames.
4. `primaryAxisAlignItems === counterAxisAlignItems` on every auto-layout
   frame.
5. All nodes `visible = true`; `itemSpacing = 0` everywhere; no stray fills.
6. Root width equals the mj-body width; column px widths equal the worker
   attrs; section paddings equal the worker attrs.
7. No em dashes in any layer name, plugin data value, or text characters.
8. Compare a fresh screenshot of the frame against the source screenshot you
   converted from, for spacing, alignment, and color parity. Small color and
   font-metric differences are acceptable; missing content, zero-height
   sections, and alignment flips are not.
