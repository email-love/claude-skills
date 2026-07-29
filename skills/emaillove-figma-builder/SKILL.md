---
name: emaillove-figma-builder
description: Build export-ready marketing and lifecycle emails inside a Figma file using the customer's Email Love design system and the Figma MCP, optionally pulling inspiration from Email Love's library of 500,000+ real brand emails. Use this skill whenever the user wants to create, assemble, draft, or build an email or email campaign in Figma, mentions Email Love, their email design system, email components, mj-wrapper frames, wants emails their team can review in Figma and export to an ESP (Klaviyo, Customer.io, Braze, Iterable, etc.), or asks to base an email on how another brand does it. Trigger even when the user just says "build me a promo email in Figma", "turn this brief into emails", or shares a campaign brief alongside a Figma file link, without naming Email Love explicitly.
---

# Email Love Figma Builder

Build real, export-ready emails in the user's Figma file from their Email Love design system. These are not mockups: the frames you assemble export to production HTML through the Email Love plugin, so underlying structure matters more than what the canvas looks like. A frame can look pixel-perfect and still fail to export if the structure is wrong, which is why this skill exists.

Requirements before starting: the Figma MCP connected to the user's file, the Email Love plugin installed in that file (latest version), and a synced Email Love design system in the file (email frames and components built as mj-wrapper stacks). If the Figma MCP provides a `figma-use` skill or the `skill://figma/figma-use/SKILL.md` resource, read it before running any plugin-API code.

## Step 1: Get the brief (adaptive interview)

Collect the essentials before touching the canvas. If the user's message already answers a question, do not re-ask it. Ask what is missing from these four, in one batch:

1. **What email or emails?** One-off promo, announcement, newsletter, or a sequence (welcome, onboarding, winback). If a sequence, how many emails and what does each one do?
2. **The goal and the one CTA.** What should the reader do? One primary call to action per email produces measurably better emails than several competing buttons, so push for one. "One CTA" means one visible button unless the user says otherwise, not "one destination with several buttons".
3. **Key content.** The offer, dates, product names, proof points, links to source material. Actual facts, not vibes.
4. **The Figma file link**, if not already shared.

**Make answering feel like a short survey, not an essay assignment.** If an interactive question tool is available in your environment (for example AskUserQuestion in Claude Code), use it for the choice-shaped questions in a single call: email type (promo / announcement / newsletter / sequence), who picks the components later (I'll choose from a visual menu / you choose for me), and inspiration (name a brand / skip). Keep only the inherently free-text items, the file link and the key content, as plain chat asks alongside it. Where no such tool exists, give each choice question lettered options so the user can answer everything in one short line ("1a, components: you pick, no inspiration") instead of writing paragraphs.

Go deeper only when it earns its keep:
- Answers are vague ("make it good"): ask for one example email they like, a brand whose emails they admire, or a link to the landing page the email supports. An admired brand feeds Step 2 directly.
- The file holds many past emails: ask which one or two they consider their best, so you study the right examples in Step 3 instead of the nearest one.
- It is a sequence: ask about timing/trigger per email and how the story escalates from one email to the next, so the emails build on each other instead of repeating.
- Multiple brands are synced in the file: ask which brand.
- Audience is unclear for lifecycle emails: ask what the recipient just did (signed up, purchased, went quiet), because that determines tone and content far more than brand adjectives do.

Do not interrogate. Two rounds of questions maximum, then build with sensible assumptions and say what you assumed.

## Step 2: Pull inspiration (when it helps)

Email Love's Inspiration MCP exposes a curated library of 500,000+ real marketing emails from thousands of brands. Check whether it is connected: look for tools named like `search_emails`, `fetch_email`, `get_brand_insights`, or `list_journeys` in your tool list, and in environments where connector tools load on demand (such as Claude Code), actively search for them before concluding they are absent. When available, use them when:

- The user names a brand to draw from ("make it feel like Patagonia's emails", "pull inspiration from Glossier").
- The brief is thin on content direction and real examples would sharpen it.
- You are building a sequence and want to see how real brands pace the same flow (`list_journeys` / `get_journey` return actual lifecycle sequences by type: welcome, winback, abandoned cart, and so on).

What to do with it: search the named brand or the user's category for the same email type you are building, fetch 2 or 3 strong examples, and mine them for structure rhythm (how they order hero, proof, and CTA), subject line patterns, offer framing, and tone. Tell the user which emails informed your choices.

Two hard rules. First, inspiration shapes structure and angle only: the build still uses the customer's own synced components exclusively, never another brand's layout rebuilt freehand. Second, never copy another brand's copy verbatim; adapt the pattern ("stat-led subject line", "problem-agitation opener"), write original words.

If the inspiration tools are not connected, how you respond depends on what the user asked. If they explicitly requested brand inspiration ("pull from Patagonia"), say up front that this needs the free Email Inspiration MCP connected, link the setup guide (help.emaillove.com/plugin/ai/email-inspiration-mcp), and offer to either wait while they connect it or proceed on general best practices. If they did not ask for inspiration, just continue, and mention the MCP once at hand-off as a way to make future builds sharper. There is also a REST API for programmatic access if the user asks.

## Step 3: Inventory the design system

Do a real inventory before building, not a glance at whatever the nearest campaign frame contains. The difference shows in the output: a shallow inventory produces every email as a re-skin of one existing campaign; a real one produces emails whose sections fit their content.

1. **List every page in the file.** Email Love design systems usually keep the component library on dedicated pages (Hero variants, Cards, Lists, Copy Blocks, Data/Stats, Footer, and so on), separate from the campaigns page.
2. **Enumerate the components** across those library pages (search for COMPONENT and COMPONENT_SET nodes, fanning out one call per page). Build a palette list grouped by section type.
3. **Study the customer's past emails.** Screenshot and read 2 or 3 existing email frames (the ones the user named as their best, or the most recent; check a Templates page if the file has one). Learn their voice, copy length, section rhythm, imagery habits, and footer conventions (does the footer use an mj-raw token block, what width is standard). These are also your donor candidates for the root frame.
4. **Report the palette to the user** in one compact list, so they see what you have to work with.
5. **Ask who picks the components. Every build.** If the user already answered this in the Step 1 survey, do not re-ask; act on their choice. Otherwise ask now: do they want to choose the sections themselves, or should you pick for them? If they defer ("you choose"), pick by content fit and say what you chose and why. One exception keeps this from being annoying: when the brief already dictates the exact sections (a numbered section-by-section brief), confirm that list in one line instead of presenting a menu.

When the user wants to choose, use the strongest selection experience your environment supports, in this order:

- **Clickable card gallery.** If a widget or visualization tool that renders inline HTML with a chat bridge (a `sendPrompt`-style function) is available, build the picker as cards: one card per candidate with the component's screenshot embedded as a data URI, the component name, a one-line note on fit, and a Recommended badge on your pick. Clicking a card sends the selection to chat (for example `sendPrompt('Use header 1 for the header section')`). Present one section at a time to keep payloads small, cap candidates at 3 or 4, and keep card order stable. This is the best experience where it works; capturing screenshots adds a little latency, which is worth it.
- **Previews inside the question.** If your interactive question tool supports per-option preview content, ask one question per section with each candidate's screenshot attached as that option's preview, so focusing an option shows the component itself. Cap it at 3 or 4 candidates per section, lead with your recommendation as a label tag, and keep descriptions to one line on fit and trade-offs.
- **Pick in Figma (offer it, many users prefer it).** The components already sit at full fidelity in the user's own file, and you can read their current selection through the Figma MCP. Lay out a temporary, clearly named frame ("Component menu, delete me") containing labeled instances of the candidates next to the build area, ask the user to click their choice for the current section and say "picked", read the selection, confirm what you saw, and move to the next section. Delete the menu frame when done. No thumbnails, no letter-mapping, and the user judges components at real size.
- **Contact sheet fallback.** Where neither works, screenshot the candidates for the section types this email needs (not every page) into one numbered image plus a matching lettered list. The letters and ordering in the list must match the sheet exactly; mark your recommendation with a tag in its description rather than reordering.

Then compose with a clear split between the two references. Past emails teach voice and polish: how this brand writes, how dense their sections run, how they treat imagery. The palette plus the content decides structure: statistics want a stats or data card, steps want a list component, social proof wants a testimonial or review card, product roundups want grid or listing cards, a single announcement wants a hero plus copy block. Studying past emails is not a license to re-skin the nearest one; if your section stack is identical to an existing campaign's, that is a signal you matched the donor, not the content. Variety that serves the content beats uniformity.

Never design freehand. Everything you build must be instances of the library's components or duplicated Email Love structure. Agents assemble far better than they draw, and only Email Love structure exports.

## Step 4: Build

### How the frame structure works

The plugin resolves what each layer *is* from a plugin data key called `name`, and falls back
to the Figma layer name when that key is absent. Getting this wrong produces a frame that
looks perfect on the canvas and silently drops content on export, so it is worth understanding
before you build anything.

Every email nests in this order:

```
mainFrame                          the root; carries the marker and theme colors
└── section component instance     Header, Hero, Copy block: your library's sections
    └── mj-section
        └── mj-column
            └── mj-text-Frame | mj-image-Frame | mj-button-Frame
                └── the content: a TEXT node, an image RECTANGLE, or an
                    instance of a button style component
```

An `mj-wrapper` may sit above `mj-section` when a section needs a full-width background.

**Rule 1: declare the tag, do not just name the layer after it.** There are two supported
conventions, and you should prefer the first:

- **Metadata (what the plugin itself uses, and the most robust).** Write the MJML tag into the
  `name` key: `node.setSharedPluginData('emaillove', 'name', 'mj-section')`. The layer name is
  then free, so you can label it anything a human will understand ("Report CTA row"). This is
  why the design system's own sections have friendly names like "Hero — FARE Act" and still
  export correctly, and why the docs say you can rename layers without breaking the export.
- **Layer name (the fallback, used when no `name` key exists).** The layer name must resolve to
  the tag on its own, either exactly (`mj-section`) or in the parenthesized form the plugin
  parses (`Report CTA, (mjml:mj-section)`).

The trap sits between the two. `mj-section — Report CTA` with no `name` key fails, because the
entire string is read as the tag and matches nothing. Never append a suffix to a bare tag name;
either set the metadata key or use the parenthesized form.

**Rule 2: content lives in a leaf element frame, never directly in a column.** Button styles
in a design system (for example "Blue Text White") are **sub-components, not sections**. They
carry no email structure of their own, which is deliberate: the team updates the button style
in one place and every email inherits it. A button instance must sit inside an
`mj-button-Frame`, which is what the exporter recognizes. Dropping a button component straight
into an `mj-column` exports nothing. The same holds for text and images, which belong in
`mj-text-Frame` and `mj-image-Frame`.

Because both mistakes are invisible on the canvas, the safest path is to **not hand-build this
scaffold at all**. Duplicate a section that already has the correct structure and replace its
content. Only assemble the hierarchy yourself when no existing section fits, and then copy the
naming from a working section rather than inventing it.

### Do not change the template's foundations

Read these before building and preserve them exactly: the **email width** (the root frame's
width, usually 600 or 640), the **breakpoint**, and the **fonts** already in use. These are
brand decisions someone made, not defaults to improve on.

Fonts deserve specific care. If a font in the file will not load in your environment, do not
substitute a different one to get the edit through. Report that the font was unavailable and
leave the layer as you found it, because a silent swap changes the brand's typography
everywhere it lands and is easy to miss in review.

### Root frame: duplicate for settings, then treat the body as replaceable

**Preferred: duplicate an existing Email Love email frame** to get a root that carries every plugin setting (structure markers, theme colors, subject/preheader slots). But the donor's value is its root settings, not its body. Duplicating also duplicates the donor's flaws, so vet what you inherited:

- Keep inherited sections only if they are component instances (or an mj-raw block). 
- A hand-built section inside the donor (a plain frame that is not a component instance) is invisible to the exporter and must be replaced with a library component instance or removed. This is the single most common way an inherited email silently loses content on export.
- Freely delete inherited sections you do not need and instantiate fresh ones from the library palette (create instances from the main components you found in Step 3).

**If you create the root frame from scratch** (no donor exists), opt it in with the shared marker, then seed the six theme colors, because empty color settings silently export with dark-theme defaults:

```js
frame.setSharedPluginData('emaillove', 'nodeType', 'mainFrame')
// Light background email:
frame.setSharedPluginData('emaillove', 'backgroundColor', '#ffffff')
frame.setSharedPluginData('emaillove', 'contentColor', '#ffffff')
frame.setSharedPluginData('emaillove', 'textColor', '#000000')
frame.setSharedPluginData('emaillove', 'linkColor', '#000000')
frame.setSharedPluginData('emaillove', 'buttonTextColor', '#ffffff')
frame.setSharedPluginData('emaillove', 'buttonContentColor', '#000000')
```

For a dark email, invert: backgroundColor '#000000', contentColor '#1f1f1f', textColor and linkColor '#ffffff', buttonTextColor '#000000', buttonContentColor '#ffffff'. All of these stay editable in the plugin's settings panel afterward. The frame should be a top-level vertical auto-layout frame at the design system's email width (usually 640px).

### Filling the email

- **Instantiate from the library palette**, choosing section types that fit the content (Step 3). Do not settle for whatever sections the donor happened to contain.
- **Include the mj-raw block.** If any email frame in the file carries a small frame holding ESP tokens like `{{Footer}}`, copy it into every email you build, even when your donor lacks one; it is how the ESP footer gets injected. See "Custom code sections" below for how to build one from scratch.
- **Never detach an instance.** Change its text instead. Detaching severs the structure the exporter reads.
- **Load fonts before editing text.** Every text edit follows: load the node's current fonts, await, then mutate. Skipping the font load is the most common build failure. Get the current fonts from the text node itself rather than assuming.
- **One visible CTA button per email** unless the user asks for more. If a component carries extra built-in buttons or text links that compete with the CTA, hide them via component properties.
- **Imagery: use what the user gives you, placeholder the rest.** When the user supplies images (files, URLs, or points at assets in the file), place them as fills on the components' image blocks at their existing dimensions, at 2x resolution for crispness, watching crop and focal point. The Email Love plugin picks up image fills at export and handles hosting automatically. When no imagery was provided, set image blocks to flat gray fills at their existing dimensions and say so in the report; a human art-directs later. If the user explicitly asks for AI-generated imagery and the Email Love creation tools (`generate_image`, `upload_image`) are connected, generate on their prompt and place the result, noting that image generation is metered on the Free plan.
- **Leave final CTA URLs alone.** Links are wired at export time in the plugin.
- **Lay out multiple emails side by side** on the canvas, each in its own frame, so the team can review the sequence at a glance.

### Links, alt text, subject, and preheader

These live in plugin data, so you can set them as you build rather than leaving them all to
the user:

```js
// Link: on the element frame (mj-button-Frame, mj-image-Frame, hero image)
el.setSharedPluginData('emaillove', 'href', 'https://example.com/pricing')
// Alt text: on the same image frame
el.setSharedPluginData('emaillove', 'altText', 'Two-bedroom in Park Slope')
// Subject and preheader: on the ROOT frame
root.setSharedPluginData('emaillove', 'emailSubject', '20% off Premium ends Sunday')
root.setSharedPluginData('emaillove', 'emailPreHeader', 'Use code SPRING20 at checkout')
```

Put `href` and `altText` on the **element frame**, not the nested style component. Element
types are read slightly differently and a couple of them look at the frame's first child
instead, so when you are unsure write the same value to both the frame and its first child.
Extra plugin data on a node nothing reads is harmless.

**Existing values win, and you cannot change them.** The plugin reads its own private data
first and falls back to the shared namespace only when the private value is empty. A link or
alt text a person set by hand in the plugin lives in private data you can neither read nor
overwrite, so your value is silently ignored. Setting these on elements that do not have them
works; "changing" one that does will appear to succeed and do nothing. When a user asks you to
change an existing link, say plainly that they need to change it in the plugin.

Because you cannot verify which nodes already carry private values, treat every link you set as
provisional: list them in your report so the user can spot any that did not take.

### The full element vocabulary

Beyond text, image, and button, the plugin has first-class element types. Use them rather than
imitating them, because a faked element looks right on the canvas and exports wrong:

- `mj-divider` for a horizontal rule. Never fake one with a thin rectangle.
- `mj-spacer` for vertical space. Never fake it with an empty frame.
- `mj-navbar` containing `mj-navbar-link` for a link row.
- `mj-table` containing `mj-table-row` for tabular data.
- `mj-hero` for a hero with a background image.
- `mj-raw` for raw passthrough code, covered below.

If the design system has a component for one of these, instantiate that instead of assembling
the frame by hand; the library version carries styling the raw type does not.

### Custom code sections (mj-raw)

Some content cannot be built from components: ESP-specific markup, Handlebars or merge-field
blocks, dynamic listing or product cards, tracking snippets. For those, build an **mj-raw**
section, which the plugin passes through to the export verbatim.

The structure the exporter looks for is exact:

- A **frame** whose name is `mj-raw`. (The plugin resolves the name from the `name` plugin
  data key first and falls back to the layer name, so naming the layer `mj-raw` is enough.)
- Containing **exactly one text node** as its first child, conventionally named `mj-raw-text`.
- That text node's characters are the raw code, emitted as-is into the email.

Two things that will bite you:

- **The frame must contain that text child.** The exporter reads the first child without
  checking it exists, so an empty `mj-raw` frame breaks the export rather than exporting
  nothing. Never create the frame without its text node.
- **mj-raw content is skipped in the plugin's preview but included in the export.** A raw
  section that looks missing in Preview is usually working correctly. Tell the user this
  when you build one, so they do not report it as a bug.

Keep raw sections small and purposeful. Everything that can be a component should be a
component, because raw blocks skip the plugin's structure handling, mobile styles, and dark
mode entirely. When you add one, say in your report what it contains and that it needs
testing in a real inbox, since hand-written markup is where cross-client rendering breaks.

### Dark mode

The plugin supports per-node dark mode overrides, and they live in the same five keys as the
root frame's theme colors, set on the individual node rather than the root: `contentColor`,
`textColor`, `linkColor`, `buttonContentColor`, `buttonTextColor`. A node carrying any of
these has a deliberate dark mode treatment that someone chose.

Treat existing dark mode settings as read-only. Never clear or overwrite these keys on nodes
that already have them, and do not strip them when you duplicate a donor frame; they should
ride along with the copy. When your build inherits nodes that carry dark mode overrides, say
so in your report and name the sections, so the user knows what is already handled and what
still needs a designer.

If the user explicitly asks you to set dark mode on a section, write those keys on that
node and tell them to verify in the plugin's dark mode preview, because dark mode rendering
varies enough across clients that it warrants a human check.

### Writing the content

Write like a person, not a template. Front-load the value in the first section, keep one primary CTA, make everything scannable. For sequences, each email must escalate or advance the story; if two emails in one recipient's path repeat the same theme, rewrite the later one to build on the first. Match the brand voice from existing copy in the file, informed by any Step 2 inspiration.

### Saving components into the plugin's design system

Users sometimes want a section you built (or a whole new component set) saved into the
plugin's design system so it becomes reusable from the Customs tab and syncs to the AI
backend. Know the boundary: **saving is an authenticated plugin action that runs on the
user's current selection.** You cannot push components into the plugin's storage yourself.
What you can do is make each save a single click:

1. **Finish each component as a clean, standalone unit** with correct structure and naming,
   placed on the appropriate library page (Heroes with heroes, and so on), spaced apart so
   each is easy to select.
2. **Pre-tag every finished component** with your proposed metadata, so the intent travels
   with the node:
   `node.setSharedPluginData('emaillove', 'saveCategory', 'Hero')` and
   `node.setSharedPluginData('emaillove', 'saveName', 'Hero — text led, portrait')`.
   Today the plugin's save dialog does not read these; they document intent for the human and
   are ready for the plugin's bulk-save to consume once it ships.
3. **Drive the saves like pick-in-Figma in reverse.** Give the user a checklist ordered by
   page, then walk it: "Select 'Hero — text led, portrait', open the plugin, Save Component,
   category Hero, name as listed; say done and I'll queue the next." The plugin generates the
   thumbnail automatically at save, so the user only selects, clicks, and picks the category
   you specified.

Report the full save checklist even if the user defers the saves; it is the hand-off artifact.

## Step 5: Verify

Screenshot every email you built and inspect it: no clipped text, no overlapping elements, spacing consistent with the file's real campaigns. Then check structure:

- Root frame is a duplicated Email Love frame, or carries the shared marker plus theme colors.
- Every section is a component instance (mj-raw excepted). This includes inherited ones: no hand-built frames survived the donor vetting.
- The mj-raw/footer block is present if any email in the file has one, and every mj-raw frame
  you created contains its text child.
- Dark mode overrides on inherited nodes are intact, not cleared.
- No detached instances.
- Exactly one visible CTA button per email, unless the user asked otherwise.

Fix what fails before presenting. Report what you built, which components you chose and why, what you assumed, which inspiration emails informed the work (if any), and anything you left as a placeholder.

## Step 6: Hand off

Tell the user to:

1. Review the emails in Figma and comment or edit like any design work.
2. Select a finished frame and open the Email Love plugin to set subject line and preheader in the settings panel (propose subject and preheader copy for each email: subject under 45 characters, preheader that extends rather than repeats it).
3. Export through the plugin to their ESP. Building on the canvas is free; exports are what count against the Free plan (5 per month, unlimited on paid plans).

If the plugin says "Please select valid email template" on a frame you built, the root frame is missing the marker (see Step 4) or the plugin version predates shared-marker support: ask the user to update the plugin.

## Staying current

This is version 1.6.0 of this skill. If you have web access, check once per conversation (quietly, without narrating it) whether a newer version exists: fetch https://api.github.com/repos/email-love/claude-skills/releases/latest and compare the tag. If a newer version exists, mention it once at hand-off with the right update path for the user's surface: claude.ai users re-upload the .skill file from that release; Claude Code plugin users run the marketplace update. If you have no web access, skip this silently.
