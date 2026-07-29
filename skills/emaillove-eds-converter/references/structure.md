# Email Love structure: ground truth

Derived from the plugin source (`email-love/Figma-plugin`), not from inference. Cite this
rather than guessing. File references are to that repo.

## How the plugin identifies a node

`getMetaName(node)` returns the **`name` plugin data key** if present, else the Figma layer
name (`helpers.ts`). `getName()` then parses a tag from that string: a bare string is used
whole, or `Label, (mjml:mj-section)` yields tag `mj-section` with frame name `Label`.

Two consequences:

- `mj-section — Report CTA` with no `name` key **fails**: the whole string is read as the tag.
- Writing `setSharedPluginData('emaillove', 'name', 'mj-section')` is the robust path, because
  `getPD` reads private data first and falls back to the shared `emaillove` namespace.

The root frame is identified separately, by `nodeType === 'mainFrame'`.

## Alignment: the trap

`getPrimaryAlign(node, layout)` (`helpers.ts:1648`) reads **`primaryAxisAlignItems`** and maps
it to *horizontal* alignment:

| primaryAxisAlignItems | exported align |
| --- | --- |
| `MIN` | left |
| `MAX` | right |
| anything else (incl. `CENTER`) | center |

In Figma a **vertical** auto-layout centers horizontally via `counterAxisAlignItems`, so a
column that looks centered on canvas exports `align="left"`. The plugin's own components avoid
this by setting **both axes to the same value**. Verified on plugin-built nodes:

| node | layoutMode | primary | counter |
| --- | --- | --- | --- |
| `mj-section` | HORIZONTAL | CENTER | CENTER |
| `mj-column` (left) | VERTICAL | MIN | MIN |
| `mj-column` (centered) | VERTICAL | CENTER | CENTER |
| `mj-text-Frame` | HORIZONTAL | CENTER | CENTER |

**Rule: set `primaryAxisAlignItems` and `counterAxisAlignItems` to the same value.** That value
is what exports. Note `mj-text-Frame` is HORIZONTAL, not vertical.

Buttons read alignment from their **parent**: `extractButtonJson` calls
`getPrimaryAlign(node.parent, 'row')`, so a button's alignment comes from the column, not the
button frame.

## Node types

From `src/constants/nodeTypes/mjmlNodeTypes.ts`, which splits them explicitly:

**Containers:** `mj-body`, `mj-wrapper`, `mj-section`, `mj-group`, `mj-column`,
`mj-column-inner`

**Content block frames (outer wrappers):** `mj-text-Frame`, `mj-image-Frame`,
`mj-button-Frame`, `mj-hero-Frame`, `mj-hero-Image`, `mj-divider-Frame`

**Content blocks (inner nodes):** `mj-text`, `mj-image`, `mj-button`, `mj-button-text`,
`mj-hero`, `mj-divider`, `mj-raw`, `mj-raw-text`, `mj-spacer`

**Others:** `mj-social` / `mj-social-element`, `mj-navbar` / `mj-navbar-link` / `mj-nav-text`,
`mj-table` / `mj-table-row` / `mj-table-column` / `mj-table-text` / `mj-table-image`,
`beforeIcon-Frame` / `afterIcon-Frame`

## Every content leaf is a tagged pair

The wrapper carries layout; the inner node carries content, and **both must be tagged**:

```
mj-text-Frame   → mj-text     (the TEXT node)
mj-image-Frame  → mj-image    (a RECTANGLE with the image fill)
mj-button-Frame → mj-button   (whose own direct child is a TEXT node)
mj-divider-Frame→ mj-divider  (a line/rectangle)
```

`extractButtonJson` finds the label via `node.children?.find(c => c.type === 'TEXT')` on the
`mj-button` node, so the text must be a **direct** child of it.

Two failure modes, both silent:

1. **Untagged content is flattened, not skipped.** Anything unrecognized hits
   `renderNodeAsImage` ("render the unknown as the image", `nodeJsonExtractor.ts:849`) — the
   same path that powers editable images. A missing `mj-button` tag turns a live button into a
   PNG with no text or link.
2. **An untagged frame swallows its whole subtree.** An unrecognized frame between a column and
   its leaves flattens everything beneath it into one image, however well-tagged the leaves are.
   Every frame in the chain must resolve to a type.

**Style the inner node, not the wrapper.** A wrapper with an image fill and no children exports
as an empty cell. An image is `mj-image-Frame` *containing* a rectangle; a divider is
`mj-divider-Frame` *containing* a line.

## mj-group

For elements that must stay side by side on mobile (columns otherwise stack). Contains
`mj-column`s, and **must be a child of `mj-section`**, never of a column. MJML requires columns
inside a group to be sized in **percentages, not pixels**; the plugin computes this from the
Figma widths (`nodeJsonExtractor.ts:1426`).

To stop a whole section stacking without a group, set `stackColumns` = `'false'` on the section.
Wrapper-level `stackColumns`/`reverseStack` propagate down to child sections that lack their own.

## mj-raw

A frame named `mj-raw` containing **exactly one TEXT child** (conventionally `mj-raw-text`)
whose characters are emitted verbatim. `extractRawJson` reads `node.children[0]` unguarded, so
an empty `mj-raw` frame **breaks the export**. Raw content is **skipped in the plugin preview
but included in the export**, so a raw section looking absent in Preview is usually fine.

## Writable plugin data keys

All read through `getPD`, so agents can set them in the shared `emaillove` namespace. A value
already set in **private** data always wins; agent values apply only where nothing was set.

| Key | On | Purpose |
| --- | --- | --- |
| `nodeType` = `mainFrame` | root frame | marks an email template |
| `name` | any node | the MJML tag |
| `backgroundColor`, `contentColor`, `textColor`, `linkColor`, `buttonTextColor`, `buttonContentColor` | root | theme colors. On a **child** node the same five (minus background) are per-node **dark mode** overrides |
| `href` | element frame | link (buttons, images, heroes) |
| `altText` | image frame | alt text |
| `emailSubject`, `emailPreHeader` | root | subject and preheader |
| `mobileStylesPaddingTop/Right/Bottom/Left` (+ `Inner*`) | element frame | mobile padding |
| `mobileStylesHideInMobileDevice` / `HideInDesktopDevice` = `'true'` | element frame | per-device visibility |
| `mobileStylesTextAlign`, `mobileStylesAlign` | element frame | mobile alignment |
| `stackColumns`, `reverseStack` | section/wrapper | mobile stacking |
| `breakpoint` | root | when mobile styles switch on (defaults to frame width) |
There is **no** plugin data key that saves a component into a plugin section. Do not write
`saveName` or `saveCategory`; the plugin reads neither. See "Promoting a frame to a component".

Empty theme colors on the root are **not neutral**: the exporter substitutes dark-theme
defaults, so a light email exports with dark globals.

## Promoting a frame to a component

Saving into a design system is **not** plugin data driven. It is an S3 upload, keyed by design
system and category, driven entirely through the plugin UI:

1. Select the top-level frame. It must carry `nodeType = 'mainFrame'` or the sandbox rejects it
   with "Please select valid email template" (`code.ts:2699`).
2. A design system must already be selected, or you get "Please select a design system first!"
3. In the Custom Templates panel, click **Add New Template**, pick a category, confirm.

The S3 key is `ai-users/{licenseKey}/{figmaId}/customs/{brand}/{category}/{name}_{uuid}/...`
(`awsS3Service.ts:657`), where `name` is **the raw Figma frame name**.

Two consequences worth knowing:

- **Rename the frame before saving.** The frame name becomes both the component name and the S3
  path, so saving straight after an AI Import produces a component literally named
  `EmailLove_clone`. There is no rename field in the dialog.
- **A promoted component carries no on-node record of where it went.** The source of truth is the
  S3 key. Nothing can be read back off the node.

## Frames created by AI Import

`createFrameInFigma` (`codeUtils.ts:6`) presets every new frame to a **dark palette**:
background `#000000`, content `#1f1f1f`, text and link `#ffffff`. These are defaults, not derived
from the imported design, so a light-brand import needs its Appearance corrected before export or
it exports with dark globals.

Position is hardcoded to `viewport.center.x - 640`, `viewport.center.y - 100` with **no per-frame
offset**, so a multi-frame batch import stacks every result at the same coordinates.
