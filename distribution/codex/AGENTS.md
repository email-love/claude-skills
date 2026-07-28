# Email Love: building emails in Figma

Instructions for OpenAI Codex. This is the Codex port of the Email Love Figma Builder
skill (github.com/email-love/claude-skills). It teaches you to build real, export-ready
emails inside the user's Figma file from their Email Love design system.

Place this file at `~/.codex/AGENTS.md` to have it apply everywhere, or at the root of a
project you use for email work. If you already have an AGENTS.md, paste this in as a
section rather than replacing the file.

## Setup the user must do once

- Connect the **remote** Figma MCP server (`https://mcp.figma.com/mcp`). The local/desktop
  server does not expose the write tools this workflow needs.
- Export a Figma personal access token before launching Codex:
  `export FIGMA_TOKEN=figd_...`, generated at Figma → Account Settings → Personal Access
  Tokens, with at least these scopes: Current user, File content, File metadata, Library
  content.
- Install the Email Love Figma plugin (latest version) in Figma, with a synced design
  system in the file. See help.emaillove.com/plugin/components/design-systems.
- Expect many sequential write calls during a build. Run with an approval mode that does
  not stop on every MCP call, or the build will be a wall of confirmations.

## Before you start: check your tools

This workflow depends on `use_figma`, the general-purpose Figma write tool that executes
Plugin API code. Confirm it is in your Figma tool catalog before promising a build.
`get_metadata` and `get_screenshot` are also required.

If `use_figma` is missing, stop and tell the user plainly: their Figma MCP connection is
read-only, so you cannot build on the canvas. Offer to write the email plan (structure,
copy, subject lines) instead, and mention that Claude with the Email Love skill covers the
building workflow. Do not fake it by generating a picture of an email.

## Why structure matters more than looks

These are not mockups. The frames you assemble export to production HTML through the Email
Love plugin. A frame can look pixel-perfect in Figma and still fail to export if the
underlying structure is wrong, which is the entire reason these instructions exist.

The plugin decides whether a frame is an email template by reading a marker on the root
frame. It reads its own private plugin data first, then falls back to the shared
`emaillove` namespace, which is the one external tools like you can write.

## Step 1: Get the brief

Collect the essentials before touching the canvas. If the user's message already answers a
question, do not re-ask it. Ask what is missing, in one batch, with lettered options so the
user can answer in a single line:

1. What email or emails? (a) promo (b) announcement (c) newsletter (d) a sequence such as
   welcome, onboarding, or winback. If a sequence, how many and what each one does.
2. The goal and the one CTA. One visible button per email outperforms several competing
   ones, so push for one unless the user says otherwise.
3. Key content: the offer, dates, product names, proof points, links. Real facts, not vibes.
4. The Figma file link, if not already shared.

Go deeper only when it earns its keep: vague answers ("make it good") warrant asking for an
example email they like or a brand they admire; sequences warrant asking how the story
escalates between emails; a file with several synced brands warrants asking which brand;
lifecycle emails warrant asking what the recipient just did, since that shapes tone far
more than brand adjectives. Two rounds of questions maximum, then proceed on sensible
assumptions and state them.

## Step 2: Inventory the design system

Do a real inventory, not a glance at the nearest campaign frame. A shallow inventory
produces every email as a re-skin of one existing campaign; a real one produces emails whose
sections fit their content.

1. List every page in the file. Email Love design systems usually keep the component library
   on dedicated pages (Hero variants, Cards, Lists, Copy Blocks, Data/Stats, Footer),
   separate from the campaigns page.
2. Enumerate COMPONENT and COMPONENT_SET nodes across those pages, one call per page. Build
   a palette grouped by section type.
3. Study 2 or 3 of the user's existing email frames (top-level frames around 600 to 640px
   holding stacked sections). Learn their voice, copy length, section rhythm, imagery
   habits, and footer conventions, including whether the footer uses an `mj-raw` token block.
   These are also your donor candidates for the root frame.
4. Report the palette to the user in one compact list.

## Step 3: Ask who picks the components

Ask on every build whether the user wants to choose the sections themselves or have you
choose by content fit. Skip the ceremony only when the brief already dictates exact sections
(a numbered section-by-section brief): confirm that list in one line instead.

If they defer, pick by content fit and say what you chose and why. If they want to choose,
Codex runs in a terminal, so the strongest option is to let them pick on the canvas:

- **Pick in Figma (preferred here).** Lay out a temporary top-level frame named
  "Component menu, delete me" beside the build area, containing labeled instances of the 3
  or 4 candidates for the current section. Ask the user to click their choice in Figma and
  say "picked". Read `figma.currentPage.selection`, confirm what you saw by name, and move to
  the next section. Delete the menu frame when the picking is done. The user judges
  components at full size and never squints at a thumbnail.
- **Numbered list fallback.** If the user would rather not switch to Figma, list candidates
  per section with a one-line note on fit and your recommendation tagged, and let them answer
  with numbers. You can also save `get_screenshot` output to local files and tell the user
  the paths so they can open them.

Choose section types by matching content to component: statistics want a stats or data card,
steps want a list, social proof wants a testimonial, product roundups want grid or listing
cards, a single announcement wants a hero plus a copy block. If your section stack is
identical to an existing campaign's, that is a signal you matched the donor, not the content.

## Step 4: Build

### Root frame

**Preferred: duplicate an existing Email Love email frame.** The copy carries every plugin
setting with it. But the donor's value is its root settings, not its body, and duplicating
also duplicates its flaws, so vet what you inherit: keep inherited sections only if they are
component instances or an `mj-raw` block. A hand-built section inside the donor (a plain
frame that is not a component instance) is invisible to the exporter and must be replaced
with a library component instance or removed. Freely delete inherited sections you do not
need and instantiate fresh ones from the palette.

**If you create the root frame from scratch,** opt it in with the shared marker, then seed
the six theme colors, because empty color settings silently export with dark-theme defaults:

```js
frame.setSharedPluginData('emaillove', 'nodeType', 'mainFrame')
frame.setSharedPluginData('emaillove', 'backgroundColor', '#ffffff')
frame.setSharedPluginData('emaillove', 'contentColor', '#ffffff')
frame.setSharedPluginData('emaillove', 'textColor', '#000000')
frame.setSharedPluginData('emaillove', 'linkColor', '#000000')
frame.setSharedPluginData('emaillove', 'buttonTextColor', '#ffffff')
frame.setSharedPluginData('emaillove', 'buttonContentColor', '#000000')
```

Those values are for a light email. For a dark email invert them: backgroundColor `#000000`,
contentColor `#1f1f1f`, textColor and linkColor `#ffffff`, buttonTextColor `#000000`,
buttonContentColor `#ffffff`. All stay editable in the plugin's settings panel afterward.
The root should be a top-level vertical auto-layout frame at the design system's email width,
usually 640px.

### Filling the email

- Instantiate from the library palette. Do not settle for whatever sections the donor
  happened to contain.
- Include the `mj-raw` block. If any email frame in the file carries a small frame holding
  ESP tokens like `{{Footer}}`, copy it into every email you build, even when your donor
  lacks one. It is how the ESP footer gets injected.
- Never detach an instance. Change its text instead; detaching severs the structure the
  exporter reads.
- Load fonts before editing text: read the node's current fonts, await the load, then mutate.
  Skipping this is the most common build failure. Get fonts from the text node itself rather
  than assuming.
- One visible CTA button per email unless the user asked for more. Hide competing built-in
  buttons and text links via component properties.
- Imagery: place user-supplied images as fills on the components' image blocks at their
  existing dimensions, watching crop and focal point; the plugin handles hosting at export.
  With nothing supplied, set image blocks to flat gray fills and say so in your report.
- Leave final CTA URLs alone. Links are wired at export time in the plugin.
- Lay out multiple emails side by side, each in its own frame.

### Writing the content

Write like a person, not a template. Front-load the value in the first section, keep one
primary CTA, make everything scannable. For sequences, each email must escalate or advance
the story; if two emails in one recipient's path repeat a theme, rewrite the later one to
build on the first. Match the brand voice from existing copy in the file. Never use em
dashes. Never invent statistics; flag any placeholder figures clearly.

## Step 5: Verify before you hand off

Screenshot every email you built and inspect it for clipped text, overlapping elements, and
spacing consistent with the file's real campaigns. Then check structure programmatically:

- Root frame is a duplicated Email Love frame, or carries the shared marker plus theme colors.
- Every section is a component instance, `mj-raw` excepted. This includes inherited ones: no
  hand-built frames survived the donor vetting.
- The `mj-raw` block is present if any email in the file has one.
- No detached instances.
- Exactly one visible CTA button per email, unless the user asked otherwise.

Fix what fails before presenting. Report what you built, which components you chose and why,
what you assumed, and anything left as a placeholder.

## Step 6: Hand off

Tell the user to review in Figma and comment like any design work, then select a finished
frame, open the Email Love plugin to set the subject line and preheader, and export to their
ESP. Propose a subject (under 45 characters) and a preheader that extends rather than repeats
it, for every email you built. Building on the canvas is free; exports are what count against
the Free plan.

If the plugin says "Please select valid email template" on a frame you built, the root frame
is missing the marker or the user's plugin predates shared-marker support, so ask them to
update the plugin.
