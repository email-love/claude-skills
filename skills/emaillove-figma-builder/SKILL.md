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
5. **Ask who picks the components. Every build.** Before building, ask the user: do they want to choose the sections themselves, or should you pick for them? If they want to choose, present the palette visually as a contact sheet: screenshot the candidate components for the section types this email needs (not every page), compose them into one numbered image or a tight set of images, and pair it with a numbered list so the user can answer with numbers or names. Build from their picks. If they defer ("you choose"), pick by content fit and say what you chose and why. One exception keeps this from being annoying: when the brief already dictates the exact sections (a numbered section-by-section brief), confirm that list in one line instead of presenting a menu.

Then compose with a clear split between the two references. Past emails teach voice and polish: how this brand writes, how dense their sections run, how they treat imagery. The palette plus the content decides structure: statistics want a stats or data card, steps want a list component, social proof wants a testimonial or review card, product roundups want grid or listing cards, a single announcement wants a hero plus copy block. Studying past emails is not a license to re-skin the nearest one; if your section stack is identical to an existing campaign's, that is a signal you matched the donor, not the content. Variety that serves the content beats uniformity.

Never design freehand. Everything you build must be instances of the library's components or duplicated Email Love structure. Agents assemble far better than they draw, and only Email Love structure exports.

## Step 4: Build

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
- **Include the mj-raw block.** If any email frame in the file carries a small frame holding ESP tokens like `{{Footer}}`, copy it into every email you build, even when your donor lacks one; it is how the ESP footer gets injected.
- **Never detach an instance.** Change its text instead. Detaching severs the structure the exporter reads.
- **Load fonts before editing text.** Every text edit follows: load the node's current fonts, await, then mutate. Skipping the font load is the most common build failure. Get the current fonts from the text node itself rather than assuming.
- **One visible CTA button per email** unless the user asks for more. If a component carries extra built-in buttons or text links that compete with the CTA, hide them via component properties.
- **Imagery: use what the user gives you, placeholder the rest.** When the user supplies images (files, URLs, or points at assets in the file), place them as fills on the components' image blocks at their existing dimensions, at 2x resolution for crispness, watching crop and focal point. The Email Love plugin picks up image fills at export and handles hosting automatically. When no imagery was provided, set image blocks to flat gray fills at their existing dimensions and say so in the report; a human art-directs later. If the user explicitly asks for AI-generated imagery and the Email Love creation tools (`generate_image`, `upload_image`) are connected, generate on their prompt and place the result, noting that image generation is metered on the Free plan.
- **Leave final CTA URLs alone.** Links are wired at export time in the plugin.
- **Lay out multiple emails side by side** on the canvas, each in its own frame, so the team can review the sequence at a glance.

### Writing the content

Write like a person, not a template. Front-load the value in the first section, keep one primary CTA, make everything scannable. For sequences, each email must escalate or advance the story; if two emails in one recipient's path repeat the same theme, rewrite the later one to build on the first. Match the brand voice from existing copy in the file, informed by any Step 2 inspiration.

## Step 5: Verify

Screenshot every email you built and inspect it: no clipped text, no overlapping elements, spacing consistent with the file's real campaigns. Then check structure:

- Root frame is a duplicated Email Love frame, or carries the shared marker plus theme colors.
- Every section is a component instance (mj-raw excepted). This includes inherited ones: no hand-built frames survived the donor vetting.
- The mj-raw/footer block is present if any email in the file has one.
- No detached instances.
- Exactly one visible CTA button per email, unless the user asked otherwise.

Fix what fails before presenting. Report what you built, which components you chose and why, what you assumed, which inspiration emails informed the work (if any), and anything you left as a placeholder.

## Step 6: Hand off

Tell the user to:

1. Review the emails in Figma and comment or edit like any design work.
2. Select a finished frame and open the Email Love plugin to set subject line and preheader in the settings panel (propose subject and preheader copy for each email: subject under 45 characters, preheader that extends rather than repeats it).
3. Export through the plugin to their ESP. Building on the canvas is free; exports are what count against the Free plan (5 per month, unlimited on paid plans).

If the plugin says "Please select valid email template" on a frame you built, the root frame is missing the marker (see Step 4) or the plugin version predates shared-marker support: ask the user to update the plugin.
