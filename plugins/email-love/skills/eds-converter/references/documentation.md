# Documentation pages: the visual spec

SKILL.md says what each scaffolding page has to contain. This file says what every page looks
like, so two customers' libraries look like the same product. Read it before building
foundations, and again before documenting a batch.

**Don't design these pages from scratch on each run.** Build them with `references/doc-kit.js`,
which already implements every measurement below. Paste the kit into a `use_figma` call and end
the call with exactly one builder:

| Builder | Builds |
| --- | --- |
| `buildCover({...})` | The Cover |
| `buildScaffoldPage({...})` | Getting Started, Foundations, Type, and Buttons (with its `stage`) |
| `buildModulePage({...})` | One component category page |
| `buildCampaignsPage({...})` | Campaigns |

You supply the content for each page. The kit handles layout, type and color. Set `DOC.family`
at the top of the kit to the library's body family before the first call. One page per call: the
kit switches page once, and a call that builds two pages is the one that times out halfway.

Every builder returns `missingTokens` and `strays`. `missingTokens` must come back empty (section
1, Color). `strays` lists top-level nodes on the page that the kit didn't make and that aren't
components. The kit never deletes them: read the list, and either move each one to where it
belongs or tell the user it's there.

This spec was taken from the Prada build (October 2026, file `jKarPVviJ89oyZhbeE75G5`). Its
Getting Started, Foundations, Type, Buttons, category and Campaigns pages are the reference for
"done". The Cover follows the Email Love covers on the Prada and Ultimate Email Design System
files. Every builder was run end to end against a seeded test file before this version shipped.

## 1. The visual system

### Canvas

| Board | Width | Padding | Structure |
| --- | --- | --- | --- |
| Cover | 1280 x 720 | 96 left | Brand fill, two blurred glows, title block centered vertically on the left, the Campaigns root rendered on the right |
| Scaffolding page (Getting Started, Foundations, Type, Buttons) | 1440, height hugs | 112 top, 96 sides, 128 bottom | Vertical auto layout, 88 between blocks |
| Section row inside a scaffolding page | 1248 | none | Horizontal: 260 label column, 64 gap, content column fills the remaining 924 |
| Buttons component stage | 744, beside the board at x 1520 | 112 top | Grey frame holding the button main components, centered, captioned |
| Component category page | 120 + 600 card + 96 + stage + 120 | 120 top | Absolute: spec card at x 120, main component at x 856 on a grey stage that starts at x 816 |
| Campaigns page | grows to fit every root | 120 | Guide column at x 120 (600 wide), each root on a stage starting at x 816 and then 840 apart |

Every board is a white frame bound to `color/bg/content`, set on a light grey page canvas
(`#F5F5F5`, which the kit sets because page backgrounds can't bind variables). **Keep
`clipsContent` off** on every board and row, and keep the board height on hug where it can be. A
fixed-height doc frame clips text without warning. The Cover is the one exception: it clips, so
the glows and the email preview stop at its edge.

### Type

Doc pages are set in the library's own body family, Regular and Bold only, so the file reads as
the brand. That's Arimo for an Arial brand and the webfont for a webfont brand. It's never Inter
by default. Line heights are percent. The one exception is the Cover headline and the Email Love
mark, which are set in League Spartan Bold (the Email Love display face) when the workspace has
it, and in the body family when it doesn't.

| Role | Size | Weight | Line height | Tracking | Color | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Eyebrow | 12 | Bold | 150 | 2.5 | muted | Uppercase. `02   ·   Foundations`: page number, three spaces, a middle dot, three spaces, then the page name |
| Page title | 72 | Bold | 100 | -2 | primary | One line. For a scaffolding page, says what's on it (`Color, layout and spacing`, `Six styles, one family`) |
| Lede | 22 | Regular | 145 | 0 | muted | 880 wide, one or two sentences |
| Section number | 12 | Bold | 150 | 2 | muted | `2.1`, `2.2`: page number, then the section number |
| Section title | 22 | Bold | 120 | 0 | primary | Sentence case |
| Section note | 14 | Regular | 155 | 0 | muted | One sentence under the section title that says why the section matters |
| Body | 15 | Regular | 155 | 0 | primary | Paragraphs in the content column |
| Table cell | 14 | Regular, first column Bold | 150 | 0 | primary, last column muted when there are 3+ columns | |
| Label | 12 | Bold | 150 | 2 | muted | Uppercase. Block labels such as `Use it for`, `Properties`, `Specs` |
| Caption | 11 | Bold | 150 | 1.2 | muted | Uppercase. Under stages and as table headers |
| Module name | 40 | Bold | 110 | -0.5 | primary | On the spec card |
| Module purpose | 18 | Regular | 150 | 0 | muted | One sentence |
| Stat value | 48 | Bold | 100 | -1 | primary | Inside a stat tile. Never wraps: if one value is too wide, every value in the row steps down together |
| Cover title | 76 | Bold | 100 | -1.5 | inverse | `<Brand>` on one line, `Email Design System` on the next. Steps down to keep it to two lines |

### Color

Doc pages use the library's own semantic variables, so the docs change when the brand
changes. Seven roles:

| Role | Variable | Used for |
| --- | --- | --- |
| ink | `color/text/primary` | Titles, body, table first column, bars |
| mute | `color/text/muted` | Eyebrows, ledes, notes, captions, labels |
| inv | `color/text/inverse` | Text on the brand fill (Don't panel, status badge) |
| bg | `color/bg/content` | Boards |
| sub | `color/bg/subtle` | Stages, stat tiles, Do panel, notes panels |
| blk | `color/bg/brand` | Don't panel, status badge, spacing bars |
| line | `color/border/hairline` | Row dividers, swatch outlines |

**If the brand palette has no light neutral for `line`, add one during foundations:** a
`grey/200` primitive (or the brand's nearest equivalent) plus a `color/border/hairline` semantic.
Record it in the report as a documentation token. Every hex on these pages must have a variable
behind it, and that includes the hairlines. The kit returns `missingTokens`. Anything listed
there is a fail, so create the variable and rebuild the page.

Three things on the doc pages carry fixed colors on purpose, and only these three:

- **The Cover glows and heart.** Email Love blue `#2BA3D6` and red `#EB3656`. They're the Email
  Love frame around the customer's brand, not part of it, so they don't move with the brand.
- **The dark mode mock on Foundations.** It draws the root's theme values, which live in plugin
  data on the Campaigns root, not in variables.
- **The page canvas.** `#F5F5F5`, because Figma page backgrounds can't bind a variable.

### Blocks

These are the only building blocks. Each one is a `KIT` function in `doc-kit.js`.

| Block | Looks like | Use for |
| --- | --- | --- |
| `table(head, rows, widths)` | A small caps header, a 1px ink rule, then rows with hairlines between them | Theme keys, contrast, page index, mobile ramp, properties, specs, troubleshooting, decisions |
| `stats([[value, label, detail]])` | A row of grey tiles: a big number, a small caps label, an optional muted line | At a glance numbers |
| `steps([[title, detail]])` | Numbered 01, 02 rows with hairlines between them | How to build an email, starting a new send |
| `checklist([text])` | One row per item with an empty check box | Before you send |
| `bullets([text])` | Dotted list | Use it for, button measurements |
| `doDont(dos, donts, heads)` | A grey panel next to a brand-fill panel. `heads` defaults to Do and Don't | Habits, button labels (`['Use', 'Avoid']`) |
| `swatches([{name, variable, hex, use}])` | 140 x 120 chips bound to the variable, hex in bold, then the name and use | The palette |
| `tokens([{token, points, hex, use}])` | Table rows with a 32px chip bound to the semantic variable | Semantic tokens |
| `themePair({light, dark, headline, body, cta})` | Two small mock emails side by side, light and dark | Dark mode |
| `layout({body, content, margin, mobileBody, mobileMargin, note})` | Desktop and mobile bodies drawn to scale with the content width filled | Layout |
| `spacing([{token, px, use}])` | One row per token: name, value, a bar at 4x the value (capped at 260), and its use | The spacing scale |
| `specimens([{style, sample, caption}])` | One row per text style: style name, the caption on the right, and a sample set in the real style | The Type page |
| `anatomy(layers, leaves)` | Nested boxes, outermost layer first, with the leaf blocks in the innermost | Anatomy of a module |
| `specimen(componentId, bullets)` | A live instance beside a list of its measurements | Button anatomy |
| `panel(title, lines)` | A grey box with 32 padding | Font notes, asides |
| `badge(text)` | A small brand-fill chip with an uppercase label | Module status |

Each block takes the section's content column as its first argument: inside a section's
`build: (c, K) => ...`, call `K.table(c, ...)`. `specimens` and `specimen` are async, so return
or await them.

Don't add new block types for a single page. If something doesn't fit a block, it probably
belongs in a table or a panel.

## 2. Page blueprints

Use these section lists as the default. A section can be dropped only when it would be empty
for this customer (no dark mode keys, say), and the report has to say which one and why.

### Cover

Built with `buildCover`. It matches the Email Love covers on the Prada and Ultimate Email Design
System files: a 1280 x 720 frame (the size Figma shows as the file thumbnail) filled with
`color/bg/brand`, a blurred blue glow top left and a red one bottom right, and on the left the
Email Love heart and wordmark, then the title `<Brand>` over `Email Design System`, then the
metadata line the contract requires (`v1.0   ·   600px email   ·   October 2026`), then one
status line (`24 modules, 18 verified on desktop and mobile`). On the right sits the Campaigns
root, rendered as an image 400 wide with an 8px radius and a soft shadow, running off the bottom
edge.

```js
return await buildCover({ pageId, brand: 'Prada', meta: 'v1.0   ·   600px email   ·   October 2026',
  note: '6 modules, 6 verified on desktop and mobile', rootId: '<Campaigns root id>' });
```

Build it once at foundations without `rootId` (the root is still empty), then again after batch 1
with it, and again after every batch so the status line stays true. Don't add art, ESP logos or
photography of your own: the rendered email is the picture. If the customer later replaces the
cover with their own artwork, leave it in place, don't rebuild it, and keep the metadata facts
somewhere on the page.

### Getting Started (eyebrow `01   ·   Start here`)

| # | Section | Block |
| --- | --- | --- |
| 1.1 | At a glance | `stats`, four tiles: email width, content width (detail: the side margins, desktop and mobile), vertical rhythm, scale factor, or "email standards" on REFERENCE ONLY |
| 1.2 | Build an email in five steps | `steps`: duplicate a root on Campaigns, drag in instances, edit text through properties, replace images by selecting the image rectangle inside the instance, preview and export in the plugin |
| 1.3 | Anatomy of a module | `anatomy`: Module `mj-wrapper` > Row `mj-section` > Column `mj-column`, with the leaf blocks (Text, Image, Button) inside. The note says never ungroup, detach or rename these layers |
| 1.4 | Do and don't | `doDont`: instance, don't copy. Edit through properties, don't edit text in place. Use tokens, don't type hex values |
| 1.5 | What is on each page | `table`: page name, what it holds |
| 1.6 | Before you send | `checklist`: subject and preheader set, alt text on every image, real links, unsubscribe pointing at the placeholder the ESP swaps, preview at desktop and mobile, dark mode readable |
| 1.7 | When something looks wrong | `table`: symptom, fix. At least: exports as a flat image (detached or renamed, drag in a fresh instance), copy didn't change (edited on a detached copy), text cramped on phones (instance was resized), photo stretched (resize the image rectangle, not the fill), and still stuck (hello@emaillove.com) |
| 1.8 | Decisions log | `table`: decision, why, status. Every standardisation and concession the audit and batches recorded, with who approved it, so nobody "fixes" the library back toward the source later |

### Foundations (eyebrow `02   ·   Foundations`)

| # | Section | Block |
| --- | --- | --- |
| 2.1 | Palette | `swatches` of the primitives. The note says primitives are named by value and modules never bind to them directly |
| 2.2 | Semantic tokens | `tokens`: token, points at, hex, use |
| 2.3 | Dark mode | `themePair` built from the root's theme values, then a `table` of the theme keys from the Campaigns root, then a `note` that section fills flatten to the content color in dark mode |
| 2.4 | Contrast | `table`: pairing, ratio, pass or fail. **Show a fail as a fail**, with the open question it raises |
| 2.5 | Layout | `layout`: the body with the content width filled and the margins labeled, desktop and mobile. The note says full-bleed images are the only exception |
| 2.6 | Spacing scale | `spacing`, with each token's use |
| 2.7 | Radius | A one-row `table`: the radius token, its value, and where it applies |

### Type (eyebrow `03   ·   Type`)

| # | Section | Block |
| --- | --- | --- |
| 3.1 | Specimens | `specimens`, largest to smallest. Use real copy from the source sends as samples, never lorem ipsum |
| 3.2 | Desktop and mobile | `table`: style, desktop size, mobile size, line height |
| 3.3 | About the font | `panel`: the family, the email-safe fallback stack, and any stand-in (such as Arimo for Arial) with what it means at export |

### Buttons (eyebrow `04   ·   Buttons`)

The left 1440 board uses the scaffolding layout. Pass `stage` to `buildScaffoldPage` and the main
components move onto a stage frame at x 1520 (744 wide, bound to `sub`), centered, each with its
name as a caption above it. Set `backdrop: true` on an inverse button and it sits on a brand-fill
band so you can see it. The components stay direct children of the page.

```js
stage: { items: [{ id: '<Button/Primary id>' }, { id: '<Button/Inverse id>', backdrop: true },
                 { id: '<Button, full width module id>', caption: 'Button, full width   ·   600 x 102' }] }
```

| # | Section | Block |
| --- | --- | --- |
| 4.1 | Styles | `table`: component, fill, label, where to use it |
| 4.2 | Anatomy | `specimen`: a primary button instance beside its measurements (height from padding, width, border, radius, label style) |
| 4.3 | Writing labels | `doDont` with heads `['Use', 'Avoid']`, filled with the brand's own labels from the source sends against generic ones |
| 4.4 | Dark mode | `para`: the dark button color, its contrast, and why it isn't white |
| 4.5 | In modules | `para`: how buttons appear inside modules, and which property changes the label |

Buttons-category modules go on the same stage after the styles, in inventory order.

### Component category pages (eyebrow `05   ·   Modules`)

Build these with `buildModulePage`, one call per page, after every batch that touched the page.
The page title is the category name and the lede is one sentence on what the category is for.
Each module gets a spec card (600 wide) with these parts in this order:

1. A top row with the label `Module · <category>` and a status badge.
2. The module name, then one sentence on what it's for.
3. `Use it for`: two to four concrete placements ("Opening image of a launch send").
4. `Properties`: one row per component property (name, type, what it changes). If there are
   none, say why in one sentence (text that carries links can't be a property without losing
   the links).
5. `Specs`: width, height, padding desktop and mobile, the type styles used, the mobile behavior,
   and the links.
6. `Source`: which send and node it came from, plus any standardisation applied.

The main component stays a direct child of the page, on a grey stage 40px larger than it on
every side (the stage starts at x 816, so the component sits at x 856). Under the stage goes a
caption: `600 x 128   ·   Main component, instance this`. Leave 120 between rows. Pass every
module on the page in inventory order, not only the new ones; a rebuild replaces the board and
leaves the components where it puts them.

```js
return await buildModulePage({ pageId, category: 'Heroes', number: '05',
  lede: 'The opening image of a send.', intro: 'Each module sits on the right with its spec card on the left.',
  modules: [{ comp: '<component id>', name: 'Hero, full-bleed image', purpose: '...', uses: ['...'],
    props: [['Headline', 'Text', 'The headline copy']], specs: [['Width', '600px, 48px side margins']],
    source: 'Eyewear Collection FW26, node 2:7.', status: 'Verified  ·  desktop + mobile' }] });
```

**The badge tells the reader what state the module is in, so it has to be accurate.** Use one of
three values:

- `Verified  ·  desktop + mobile`: every acceptance matrix row is `pass`.
- `Built  ·  export deferred`: one or more rows are `deferred`.
- `Awaiting review`: an open concession or question applies to this module.

The kit defaults to `Awaiting review` when `status` is left out, so a forgotten status never
claims more than the report does.

### Campaigns (eyebrow `06   ·   Templates`)

The guide column at x 120 (600 wide) holds a `Template` label with an `Export verified` badge
once the sends have passed. Below that come a title naming the sends, one sentence on what they
are, `steps` for starting a new send, a `table` of the settings on the root (light background,
dark page, dark content, dark text and links, dark button, fallback font, and subject and
preheader per root), and a closing note that a send must start from a root to keep its settings.
Each root sits on its own stage with a caption: `<root name>   ·   600 x <height>   ·   Email
root`. When a root is added, the board grows to fit it. Build it with `buildCampaignsPage`:

```js
return await buildCampaignsPage({ pageId, lede: 'The root email every send starts from.',
  guide: { badge: null, title: 'Two rebuilt sends', intro: '...', steps: [['Duplicate the frame', '...']],
    settings: [['Light background', '#F7F7F7'], ['Dark page', '#19181C']], note: '...' },
  roots: [{ id: '<root id>' }] });
```

Leave `badge` null until the sends have passed the export check, then set it to
`Export verified`.

## 3. Writing rules

- Use plain, matter-of-fact English. Sentence case everywhere except the uppercase labels.
- A heading says what's in the section. It isn't a tagline.
- Every number is concrete and matches the file: `504px content width, 48px side margins`,
  never "generous margins".
- Use the customer's own words for samples: their headlines, their button labels, their
  footer copy.
- Never use em dashes. Use a comma, a colon or a new sentence.
- Name decisions and who made them ("Legal raised from 10px to 12px, approved by the brand
  lead"), using the real name from the conversation.
- Never write "verified" on a page unless the report says so.

## 4. Build gotchas (all hit on real builds)

| Symptom | Cause | Fix |
| --- | --- | --- |
| A header or card collapses to 10px tall | `createAutoLayout` followed by `resize()` leaves the primary axis FIXED | Set `primaryAxisSizingMode = 'AUTO'` after every resize (`col()`) |
| Swatch rows or tables get clipped | The counter axis is fixed and clipping is on | `counterAxisSizingMode = 'AUTO'` and `clipsContent = false` |
| A text block runs off the column | A TEXT node set to FILL keeps `WIDTH_AND_HEIGHT` | Set `textAutoResize = 'HEIGHT'` after FILL (`add(p, n, true)`) |
| A button measures 56 when the spec says 54 | Strokes count in layout | Set `strokesIncludedInLayout = false` when you build a bordered button in Phase 2 |
| Spacing rows come out 100px tall | `resize()` on a horizontal auto layout frame, then fixing the counter axis, pins the height | `fixedW` fixes the primary axis on a horizontal frame and the counter axis on a vertical one |
| A stat value wraps to two lines | A long value ("24 / 40 / 48") in a quarter-width tile | `stats` measures every value and steps the whole row down together |
| The cover title wraps to three lines | `Email Design System` at 76px is wider than the title block | `buildCover` measures it and steps it down to fit two lines |
| The cover's email preview is blank | Instances only render once their main components' pages are loaded | `buildCover` loads every page before exporting the root |
| Long tag names get truncated in the anatomy block | The label rows are horizontal | `anatomy` nests one box per layer, so each tag gets its own row |
| White modules disappear on the white board | No contrast between the module and the board | Grey stage behind every module and root. The kit draws it on category pages, Campaigns and the Buttons stage |
| Rebuilding a page duplicates it, or deletes something the customer made | The cleanup step was too broad or too narrow | Each builder removes only the board it made before (matched by name) and lists anything else in `strays`. It never deletes a node it didn't make |
| `appendChild(...)` returns undefined | The Plugin API's `appendChild` returns nothing | Use `add()`, which returns the child |
| A hex on the page has no variable | The doc chrome used a raw color | The kit binds everything and reports `missingTokens` |

## 5. Acceptance

Run this after foundations and after every batch's documentation pass. Record the result in the
report.

- [ ] Every doc page was screenshotted at full height and looked at. Nothing is clipped, nothing
      overlaps, and no text runs past its column.
- [ ] `missingTokens` came back empty for every page the kit built.
- [ ] Every module in the library appears on its category page with a spec card, a stage and a
      caption, and its badge matches the acceptance matrix.
- [ ] Every main component is a direct child of its page and sits on its stage. No loose
      instances or scratch frames are left on any page, and every builder's `strays` came back
      empty or each entry was explained to the user.
- [ ] The Cover's status line and the Campaigns guide match the current state of the library,
      and the Cover shows the current Campaigns root.
- [ ] No em dashes anywhere on the pages.
