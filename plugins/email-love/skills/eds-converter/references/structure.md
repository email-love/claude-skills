# Email Love structure: ground truth

Derived from the plugin source (`email-love/Figma-plugin`), not from inference. Cite this
rather than guessing. File references are to that repo.

## How the plugin identifies a node

`getMetaName(node)` returns the **`name` plugin data key** if present, else the Figma layer
name (`helpers.ts`). `getName()` then parses a tag from that string: a bare string is used
whole, or `Label, (mjml:mj-section)` yields tag `mj-section` with frame name `Label`.

Two consequences:

- A layer named `mj-section Report CTA` with no `name` key **fails**: the whole string is read
  as the tag. Use the parenthesized form `Report CTA, (mjml:mj-section)` or the shared key.
- Writing `setSharedPluginData('emaillove', 'name', 'mj-section')` is the robust path, because
  `getPD` reads private data first and falls back to the shared `emaillove` namespace.

An **email template** root is identified separately, by `nodeType === 'mainFrame'`, and carries no
tag. A **design-system module** root carries no `nodeType` at all and is identified by its tag,
`mj-wrapper`, like any other wrapper. See "Promoting a frame" below: the two shapes are mutually
exclusive, and they upload through two different screens.

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
`getPrimaryAlign(node.parent, 'row')`, and an `mj-button`'s parent is its `mj-button-Frame` pair
wrapper, so the exported `align` comes off that wrapper rather than off the `mj-button` node
itself. Mirror the same value on the containing column when all of the column's content shares it
(`render-spec.md` section 4.3); the two must not fight.

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

Nothing in this list expresses z-order, overlap, or absolute position, and no plugin data key adds
them. A source photo that bleeds past its block or sits behind copy has no tag to be given: it is
rebuilt as a two column row, which is the Two Column Swap in `render-spec.md` section 3.4.1. Do
not improvise a container for it; an unrecognized frame is flattened to an image (below).

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
   `renderNodeAsImage` ("render the unknown as the image", `nodeJsonExtractor.ts:849`), the
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
`mj-column`s, and **must be a child of `mj-section`**, never of a column.

**In Figma, give those inner columns FIXED pixel widths.** The exported MJML needs percentages,
but you do not write percentages: the exporter derives them from the pixel widths
(`nodeJsonExtractor.ts:1426`). A 560 wide group holding two 280 columns exports as 50% and 50%.
Do not reach for FILL sizing or try to express a percentage in Figma.

Those pinned pixels need **slack** when the column holds text: the width you measure on the Figma
canvas is measured in a different font binary from the one the email loads, and a pinned column
cannot grow, so a label that fits exactly on canvas wraps in Preview. Rule and numbers in
`render-spec.md` section 3.3.1.

To stop a whole section stacking without a group, set `stackColumns` = `'false'` on the section.
Wrapper-level `stackColumns`/`reverseStack` propagate down to child sections that lack their own.

**A group is not the vehicle for the Two Column Swap** (`render-spec.md` section 3.4.1, the
standard rebuild for an overlapping or bleeding image). That pattern wants the stacking a group
suppresses, so it uses a plain `mj-section` holding two `mj-column`s. Reach for a group only when
the design genuinely must stay side by side at 390px.

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
| `nodeType` = `mainFrame` | **email template root only** | marks an email template. **Never write it on a design-system module root**: the upload still runs and archives the block as a whole email |
| `name` | any node, **including a module root** (`mj-wrapper`) | the MJML tag |
| `backgroundColor`, `contentColor`, `textColor`, `linkColor`, `buttonTextColor`, `buttonContentColor` | email template root | theme colors. On a **child** node, including a module's own `mj-wrapper` component, the same keys are per-node **dark mode** overrides, not theme, and `buttonContentColor` / `buttonTextColor` export unconditionally rather than only when they differ from the enclosing email. Leave them off a module unless a designer asked for a dark-mode treatment on that block |
| `lightThemeBackgroundColor` | email template root | the `mj-body` background hex; defaults to `#ffffff` when empty (`code.ts:1137`) |
| `fallBackFontName` | email template root | the font the exported stack falls back to, `Arial` unless set (`code.ts:1148`). It is also what decides how much slack a pinned column needs (`render-spec.md` 3.3.1) |
| `href` | the tagged INNER node, never its `-Frame` wrapper: the `mj-button` frame, the `mj-image` rectangle, the hero | link. Each extractor is dispatched on the inner node's own tag and calls `getPD(node, 'href')` on it (`nodeJsonExtractor.ts:133` and `3687` for images, `209` and `3291` for buttons) |
| `altText` | the `mj-image` RECTANGLE, same as `href` | alt text |
| `emailSubject`, `emailPreHeader` | root | subject and preheader |
| `mobileStylesPaddingTop/Right/Bottom/Left` (+ `Inner*`) | wrapper, section, column, or element frame | mobile padding. **Inert without `isPaddingActive`** |
| `isPaddingActive` = `'true'` | same node as the padding | switches the padding override on. Omitting it is silent: values store, read back, and do nothing |
| `fontSize` + `fontSize_mode` = `'override'` | the `mj-text` / `mj-button-text` TEXT node | mobile font size. Note: bare property name + `_mode` switch, on the TEXT node, a different convention from the padding keys |
| `lineHeight` + `lineHeight_mode`, `letterSpacing` + `letterSpacing_mode` | the TEXT node | same pattern |
| `mobileStylesHideInMobileDevice` / `HideInDesktopDevice` = `'true'` | any node | per-device visibility |
| `mobileStylesTextAlign`, `mobileStylesAlign` | element frame | mobile alignment |
| `stackColumns`, `reverseStack` | section/wrapper | mobile stacking |
| `breakpoint` | root | when mobile styles switch on (defaults to frame width) |

Mobile keys are FLAT on the node. The exporter's serialised JSON groups them into
`mobileStylesCommonProperties` objects; that is the payload view, not the node store, and writing
objects back onto nodes does not work. All of the above were observed by having the plugin's
Mobile Styles tab write them and reading the node back; treat any key NOT in this table as
unverified until observed the same way.

There is **no** plugin data key that saves a component into a plugin section. Do not write
`saveName` or `saveCategory`; the plugin reads neither. See "Promoting a frame: an EMAIL
TEMPLATE and a MODULE are different shapes".

Empty theme colors on the root are **not neutral**: the exporter substitutes dark-theme
defaults, so a light email exports with dark globals.

## Promoting a frame: an EMAIL TEMPLATE and a MODULE are different shapes

Saving into a design system is **not** plugin data driven in the sense of a "save me" key. It is
an S3 upload driven through the plugin UI. But **what** you are allowed to select depends on
which of two things you built, and the plugin enforces the distinction with mutually exclusive
guards. This is the single most consequential structural decision in a conversion, so decide it
before you build, not at save time.

| | **EMAIL TEMPLATE** | **DESIGN-SYSTEM MODULE** |
| --- | --- | --- |
| What it is | one sendable email | one reusable block placed into many emails |
| Root node | FRAME or COMPONENT carrying no `mj-*` tag | COMPONENT that **is** the `mj-wrapper` |
| `nodeType` = `mainFrame` | **required** on the root | **must be absent.** With it the upload archives the block as a whole email |
| Shared `name` on the root | none | `mj-wrapper` |
| Theme color keys | all of them, on the root | per-node dark-mode overrides only; usually none |
| Directly inside it | `mj-wrapper` components | `mj-section` frames |
| Root layer name | the email name | the module name (becomes the component name and its S3 path) |

**A module is not a small email.** An email root *contains* wrapper components; a module *is* one
of those wrapper components. Every `mj-wrapper` the plugin itself renders is created as a
COMPONENT, not a FRAME (`UiParser.ts:1519-1522`:
`if (tag === MjmlNodeType.Wrapper || isStandalone) frameNode = figma.createComponent()`), so a
wrapper-as-component is the plugin's own shape, not an agent convention.

### The two guards, which are exact mirrors of each other

`select-component` in `code.ts` has two branches and they reject opposite things:

- **Email template** (`customType === 'customProperties'`, `code.ts:3226`): rejects any selection
  **without** `nodeType = 'mainFrame'`, with "Please select valid email template". This is the
  branch behind Custom Templates, Add New Template: `AddTemplate.tsx:62` is its only caller and
  it always sends `customType: 'customProperties'`.
- **Module** (the `else` branch, `code.ts:3297`): builds its own temporary frame, marks *that*
  `nodeType = 'mainFrame'`, clones your selection into it, and then rejects the save if the
  selected node itself carries `nodeType = 'mainFrame'`, with the same message. No UI reaches
  this branch today, so read it as intent rather than as the live route.

The live module route is the **Assets sidebar Upload button**
(`AssetsComponent.tsx:610-632`), which dispatches `syncTemplateUpload` (`code.ts:3861`). It
keys off the tag rather than the marker: `code.ts:3892` sets
`isTopLevel = getName(getMetaName(selectedNode)).tagName === 'mj-wrapper'`, and only a top-level
wrapper gets wrapped in the temp `mainFrame` envelope and gets the MCP companion JSON generated
(`code.ts:3934`). A module root that is not tagged `mj-wrapper` is archived as if it were a whole
email and produces no MCP JSON. Two more facts about that route: it refuses to start without a
selected design system ("Please select a design system first!"), and it takes a **multi
selection**, uploading every selected wrapper in one batch (`uploadParams.nodeId` is an array
when more than one node is selected).

Marking a node **both** ways is worse than either mistake: in both serializers the `mainFrame`
branch is tested before any wrapper handling (`nodeJsonExtractor.ts:282` versus the wrapper branch
at `1587`; `exportTemplate.ts:180` versus `285`), first match wins, so the output is a nested
`mjml` document inside `mj-body` that nothing downstream can compile.

### Saving an email template through the UI

1. Select the top-level frame. It must carry `nodeType = 'mainFrame'` or the sandbox rejects it
   with "Please select valid email template".
2. A design system must already be selected, or you get "Please select a design system first!"
3. In the Custom Templates panel, click **Add New Template**, pick a category, confirm.

The S3 key is `ai-users/{licenseKey}/{figmaId}/customs/{brand}/{category}/{name}_{uuid}/...`
(`awsS3Service.ts`), where `name` is **the raw Figma frame name**.

Two consequences worth knowing, and they apply to a module's component name just as much:

- **Rename the frame before saving.** The frame name becomes both the component name and the S3
  path, so saving straight after an AI Import produces a component literally named
  `EmailLove_clone`. There is no rename field in the dialog.
- **A promoted component carries no on-node record of where it went.** The source of truth is the
  S3 key. Nothing can be read back off the node.

### Saving a module through the UI

A different screen, and this is the one a conversion or a gap-fill block uses:

1. Select the design system in the plugin. Without one the upload refuses to start with
   "Please select a design system first!"
2. Open the Assets sidebar section the module belongs to. The section you are looking at is the
   category it uploads into, so there is no category picker at confirm time. The 13 predefined
   sections are Pre-Header, Header, Heroes, Single Column, Two Column, Three Column, Four
   Column, Buttons, Reviews, Images, Lists, Order Tables, Footer (`Assets.tsx`).
3. Select the `mj-wrapper` component (or several of them) on the canvas, click **Upload**, and
   confirm. A multi selection uploads as one batch.

Do NOT send a module through Custom Templates, Add New Template: that path tests for
`nodeType = 'mainFrame'` and rejects anything without it, which is every correctly built module.

## Frames created by AI Import

`createFrameInFigma` (`codeUtils.ts:6`) presets every new frame to a **dark palette**:
background `#000000`, content `#1f1f1f`, text and link `#ffffff`. These are defaults, not derived
from the imported design, so a light-brand import needs its Appearance corrected before export or
it exports with dark globals.

Position is hardcoded to `viewport.center.x - 640`, `viewport.center.y - 100` with **no per-frame
offset**, so a multi-frame batch import stacks every result at the same coordinates.
