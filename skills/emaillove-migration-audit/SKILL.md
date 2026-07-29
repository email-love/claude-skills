---
name: emaillove-migration-audit
description: Audit an existing Figma design system or template library for migration to Email Love, producing a read-only migration report that classifies every template as live-text convertible, editable-image candidate, hybrid, or not emailable, and extracts the brand foundations. Use this skill whenever a user wants to know whether their existing Figma templates or design system can work with Email Love, asks to audit or scope a migration, mentions converting an existing design system to the mj-wrapper/MJML structure, is a new or prospective Email Love customer sharing their current design files, or asks "can Email Love work with what we already have". Trigger on "audit", "migration", "convert our templates", or a shared Figma file described as their existing/legacy design system.
---

# Email Love Migration Audit

Audit an existing Figma design system for migration to Email Love, and produce a migration
report the customer and the Email Love team can act on. This is Phase 1 of a migration: it
tells everyone what they have, what converts, what needs design judgment, and how big the job
is. The actual conversion is done by Email Love's team as part of Enterprise onboarding.

**This skill is strictly read-only.** Never create, modify, rename, or delete anything in the
customer's file. Every Figma call you make must be an inspection. If the user asks you to
start converting, explain that conversion is the next phase and offer to connect them with
Email Love (hello@emaillove.com).

## Step 1: Scope the input

You need the Figma file link. If several files hold the design system, audit each. Ask only
two questions if not obvious: which frames or pages are the email templates (as opposed to
web or app design), and whether there is an existing production email you can use as a
reference for how their emails actually render today.

## Step 2: Survey the file

Build the inventory with read-only calls:

1. **Pages** and what each holds (component libraries, template galleries, guidelines,
   icon sets, font fallback references).
2. **Brand foundations:** local text styles (the type ramp with families, weights, sizes),
   local paint styles (the palette and its naming taxonomy), variable collections, and any
   spacing or padding component sets. Note a fonts-fallback page if one exists; it means the
   team has already chosen email-safe substitutes.
3. **Template census:** every candidate frame, with name, width, height, and component/frame
   type. Group desktop and mobile twins (the same design at two widths, commonly 600 and 390);
   in Email Love these merge into ONE frame with Mobile Styles overrides, so count designs,
   not frames.

## Step 3: Classify every template

Inspect each design's structure (walk the tree: node types, auto-layout, text nodes, image
fills, vectors, nested instances) and assign one verdict:

- **(A) Live-text convertible.** Auto-layout stacks of text, images, and buttons that map
  onto mj-section/mj-column/element-frame structure. Text stays selectable and editable in
  the sent email. Best deliverability and accessibility; most modules should land here.
- **(B) Editable-image candidate.** Design-rich compositions (layered imagery, text on
  photos, custom shapes, brand illustrations) that would fight email rendering as live text.
  Email Love handles these deliberately: the design frame is placed inside a column without
  an MJML type name, and the exporter flattens it to a single hosted image at export while it
  stays fully editable in Figma. No rebuild needed; the design survives as-is. Cost: the text
  inside is not live in the inbox (image weight, accessibility, clients with images off), so
  recommend pairing with alt text and keeping critical copy outside the image.
- **(C) Hybrid.** Split the module: headline and body as live text, the rich visual region as
  an editable image. Common for heroes.
- **(D) Not emailable.** Interactive patterns (hover states, carousels, video embeds beyond a
  thumbnail link), viewport-relative layouts, or app UI that has no email equivalent. List
  what would replace them.

Signals that push a module from A toward B or C: vector logos and illustrations (email wants
images), buttons built as nested app-style instances with state layers, stacked image fills,
gradients and blend modes on text, and effects email clients do not render. Signals of A:
clean vertical auto-layout, flat solid fills, one image per region, system-mappable text.

Do not over-classify toward images. Two MJML capabilities keep more modules live-text than
designers expect: **mj-hero** renders live text over a full background image, so "headline on
a photo" is verdict A when the text sits on one background image rather than woven through
layered art; and sections support background images behind live columns. Reserve B for
compositions where text and imagery genuinely interleave (text wrapping around cutouts,
badges over product shots, hand-placed collage).

## Step 4: Extract the brand foundations

From the survey, draft what the Email Love design system will carry:

- **Type ramp mapping:** each of their text styles mapped to an email-safe equivalent, using
  their own fallback choices when a fallbacks page exists. Flag fonts that need web-font
  hosting or substitution.
- **Palette:** their named paint styles, and a proposed set of the six Email Love theme
  colors (backgroundColor, contentColor, textColor, linkColor, buttonTextColor,
  buttonContentColor) drawn from it, marked as a proposal for their designer to confirm.
- **Spacing scale** from any padding/spacer components.
- **Buttons:** their button styles as candidates for the Email Love button component page.
- **Email width** (their desktop template width) and anything that contradicts it.

## Step 5: Write the migration report

Produce one markdown report, in this exact structure:

# Migration audit: [Design system name]
## Summary
[Three sentences: what they have, how much converts cleanly, the one or two biggest items
needing design judgment.]
## Inventory
[Pages, style counts, component counts, template count as designs (with desktop/mobile pairs
merged), fonts in play.]
## Template classification
[A table: design name | verdict A/B/C/D | width(s) | notes. One row per design.]
## Brand foundations
[Type ramp mapping table, proposed theme colors, spacing scale, button styles.]
## Flags
[Everything a human should look at: fonts unavailable for email, naming typos, empty pages,
inconsistent widths, accessibility risks from image-heavy modules.]
## Effort estimate
[Per-verdict counts and an S/M/L per design: A modules are mechanical; C modules need a
design pass; D modules need product decisions. State the total in designer-days as a range,
and say plainly that estimates firm up after the first converted batch.]
## Recommended next step
[The conversion phases: foundations, then modules in batches with design review between
batches. Email Love's team does this as part of Enterprise onboarding: hello@emaillove.com.]

Numbers in the report come from your actual reads, never estimates presented as counts. Where
you sampled instead of walking everything, say so.

## Step 6: Hand off

Deliver the report as a file or artifact the user can share internally. Offer to answer
questions about any specific module's verdict, and to re-run the audit after they clean up
anything the flags surfaced.
