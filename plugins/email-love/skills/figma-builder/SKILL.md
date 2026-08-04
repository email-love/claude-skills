---
name: figma-builder
description: Build export-ready marketing and lifecycle emails inside a Figma file for export through the Email Love plugin, either by instancing the customer's existing Email Love design system or, when they do not have one yet, by generating the structure with Email Love AI Import and transcribing it. Use this skill whenever the user wants to create, assemble, draft, or build an email or email campaign in Figma, mentions Email Love, their email design system, email components, mj-wrapper or mj-section frames, wants emails their team can review in Figma and export to an ESP (Klaviyo, Customer.io, Braze, Iterable, and so on), is starting from scratch with no email design system, or asks to base an email on how another brand does it. Trigger even when the user just says "build me a promo email in Figma", "turn this brief into emails", or shares a campaign brief alongside a Figma file link, without naming Email Love explicitly.
---

# Email Love Figma Builder

Build real, export-ready emails in the user's Figma file. These are not mockups: the frames you
assemble export to production HTML through the Email Love plugin, so the underlying structure
matters more than what the canvas looks like. A frame can look pixel perfect and still export
broken, which is why this skill exists.

## The one rule: you do not hand-author structure

**Never assemble `mj-section` / `mj-column` / leaf scaffolding from your own mental model of how
an email should be built.** Every structural bug in this pipeline has the same origin: an agent
that was right about the containers and wrong about the content, because the plugin keeps its
real conventions in **private plugin data that you cannot read**. A frame you build by eye looks
correct from the outside and silently drops content on export.

Structure comes from exactly two places, and nowhere else:

- **Path A: instance published components from the customer's Email Love design system.** The
  components already contain the correct `mj-*` structure internally. You place, fill, and
  write copy. You do not open them up.
- **Path B: generate the structure with the design-converter worker (the engine behind AI
  Import), then transcribe the returned MJML JSON per the render spec.** This is the path for a
  customer with no design system yet.

If neither path can produce a section, stop and ask. "No component fits so I will build it
myself" is the single failure mode this skill exists to prevent.

The only frame you ever create from nothing is the **root** (see "Root frame"), and it is an
empty container: everything inside it arrives by instancing or by transcription.

## Before you start

You need the Figma MCP connected to the user's file and the Email Love plugin installed in that
file (latest version). If the Figma MCP exposes a `figma-use` skill or a
`skill://figma/figma-use/SKILL.md` resource, read it before running any plugin-API code.

**Then decide the path, by checking, not assuming.**

1. If the Email Love MCP is connected, call `list_brands`, then `list_components` for the
   relevant brand, then `list_templates` (tool names may be prefixed `emaillove_`). A brand new
   account commonly returns a single `Default` brand with **zero** components and **zero**
   templates. An empty list is a real answer: it means Path B.
2. Otherwise look in the Figma file: library pages holding COMPONENT / COMPONENT_SET nodes, and
   existing email frames carrying the plugin's root marker.
3. Components exist, in the plugin or in the file: **Path A**. Nothing exists: **Path B**.
   A partial library (a few components, nothing for the section you need): Path A for what fits,
   Path B for the gap, and say so.

Tell the user which path you are on and why, in one line, before you build.

## Which model to run this with

The two paths carry very different risk, so they are worth different model budgets.

**Path B, and the migration-audit and eds-converter skills, deserve your strongest model.** That
work holds a large rule set at once (the render spec alone runs tens of thousands of tokens) and
a dropped rule becomes a component that silently breaks on export later, for someone who was not
in this conversation to catch it. This is also work a customer does once, not daily, so the extra
cost is small next to the cost of getting it wrong.

**Path A, once a design system is already synced and verified, is a smaller job.** Instance a
component, load its font, set text, done. A faster, cheaper model handles routine campaign
builds reliably here, because mistakes are cheap and obvious: wrong copy in a button is visible
the moment you look at it.

If your environment lets you choose a model per task: your most capable model to build or
migrate a design system, once. A faster model for the campaigns you build on it, every day after.

## How long a build takes, and telling the user first

Building an email in Figma is **minutes, not seconds**, and a user expecting an instant result
reads a normal build as a hang. **Before the first write to the canvas, say in one line what you
are building and roughly how long to expect.** A short line at each section boundary after that
is the right rhythm: not silence, not a running commentary.

Almost all of that time is round trips to Figma, not model thinking. Every node you create or
read back is a tool call, so **the node count predicts the time far better than how complicated
the design looks**. A one-section reminder is quick; a multi-section email with a hero, several
content blocks, and a footer is meaningfully longer; a sequence multiplies by the number of
emails. Path A is the faster path, because instancing a finished component is a handful of calls
where transcribing the same block node by node is dozens.

The design-converter worker on Path B is not the slow part: it returns MJML JSON in a few
seconds to about half a minute per design. Never leave a user thinking the AI is what is slow.
The AI is waiting on the canvas.

Give ranges, never promises, and keep the scale straight. One email is minutes. Converting a
whole design system is a different job: a batch of five design-system modules has been measured
at tens of minutes per pass, which is why a library migration is a separate batched process with
design review between batches, not something to fold into a build (hello@emaillove.com).

### Report progress while it runs

The estimate is the promise; these lines are how you keep it. A build is minutes rather than tens
of minutes, so the granularity is the **section**, not the whole email and not the node. Post one
line at each of these points and nowhere else:

1. **Before the first write to the canvas:** the path and why (you owe that line anyway), the
   section plan by name, and the estimate. **The section count you give here is the denominator
   for every line after it**, so name them: "Path A, 9 sections: preheader, logo header, hero,
   three product cards, testimonial, CTA, footer. Roughly 8 minutes."
2. **After each section lands:** count, percentage, section name.
3. **On Path B, either side of the design-converter call** (B3): one line before it and one after.
   This is the single wait in a build where nothing at all happens on the canvas, so it is the one
   place a user reasonably concludes the run has hung. Say the same thing the moment you re-run
   with `recache=1` or retry an `X-Trivial-Response`, rather than mentioning it in the hand-off.
4. **At the end:** what was built, what you assumed or had to ask about, and anything skipped.

How each line is written:

- **A count and a percentage, never prose.** "Section 4 of 9 done, 44 percent" is the format.
  "Almost there" is not a checkpoint.
- **Name the section.** "Section 4 of 9: testimonial" lets the user click it in Figma. "Section 4
  of 9" does not.
- **Two counters for a sequence, not one.** "Email 2 of 4, section 3 of 7: hero" locates someone
  in a campaign. A single percentage of the whole sequence does not.
- **Say what is happening now, in the user's language.** "Transcribing the footer, 43 nodes" tells
  them why it is slow. "Calling the plugin API" does not.
- **Section boundaries only.** Never per node, per instance, per property, or per screenshot. A
  hero with thirty nodes gets one line when it is finished, not thirty.
- **Revise the estimate when the pace disagrees with it.** Most builds are short enough that the
  opening number holds. But if sections are landing at double what you opened with, say so at the
  next section boundary with the new number instead of at the end, and revise upward without
  apology: Path B transcription in particular runs slower than it looks.

Two lines, the format to copy. Path A, after a section:

> Section 4 of 9 done, 44 percent: testimonial, instanced and filled. Sections are averaging about
> 50 seconds, so the remaining 5 are roughly 4 minutes. Next: section 5 of 9, CTA.

Path B, before the worker:

> Sending the hero comp to the design converter now. It takes a few seconds to about half a
> minute, then transcribing what comes back is the longer part.

### Say when you STOP, too

Those four points cover a build that is still building. Nothing in them covers a build that has
stopped, and that asymmetry is worse than having neither half: **an agent that reports progress but
not its own stop is worse than one that does neither, because the user infers continuation from the
last progress line.** Line 2 fires at every section boundary, so its absence reads as the next
section being written right now. Silence is indistinguishable from still working.

**Never stop silently.** If you stop, for any reason, say so in the SAME message as the last of the
work, not in a later reply and not only once the user asks. Four things, every time: what you
completed in the line 2 format so it reconciles with what came before, what remains by section name,
why you stopped, and the exact thing needed to resume, phrased so the user can send it straight back.
The reasons that qualify are a blocker, a decision only the user can make, a limit you have hit, or
reaching the end of a unit of work. Finishing the email is that last one, and line 4 is how it gets
announced.

**Do not stop between the sections of one email.** The email is the unit of work, so the section plan
you gave at line 1 is a plan to finish, not a menu to stop partway down. In a sequence the unit is
still the email: between emails is a defined boundary, mid-email is not, so finish the one you are in
before you stop and report it with both counters. The exceptions are the two this file already names,
and both are a question put to the user at the section it belongs to rather than a build abandoned
quietly: A5, where no component fits and they are the one who knows, and "The one rule" at the top,
where neither path can produce the section at all. Announce either in the shape below rather than
trailing off.

**If you wrote resumable state, name its path in that message.** Write one whenever the build is a
sequence or you expect it to cross a session boundary, alongside the converter JSON you already save
on Path B, and treat it as expected behaviour rather than extra credit. On a one-off email the
sections already on the canvas are most of the state, so name the frame instead. Either way the user
has to be told where it is: state they cannot see does not make the build resumable, it only makes
you feel that it is.

One worked example, the format to copy. It is one message, sent unprompted, not an answer to "are you
still working on it":

> Stopped, not still building. Email 2 of 4, 5 of 7 sections done, 71 percent: preheader, logo header,
> hero, two product cards, all in the `Email 2 - Winback` frame. Remaining in this email: countdown
> banner and footer. Why I stopped: no component in the design system covers a countdown banner and
> the converter flattens it to a single image, so neither path can produce it and I am not
> hand-building the structure. To resume, point me at a component to use, or say "place it as a static
> image with a fallback line", and I will finish from the saved state at `./build-state.json`.

## Step 1: The brief (adaptive interview)

Collect the essentials before touching the canvas. If the user's message already answers a
question, do not re-ask it. Ask what is missing from these four, in one batch:

1. **What email or emails?** One-off promo, announcement, newsletter, or a sequence (welcome,
   onboarding, winback). If a sequence, how many emails and what does each one do?
2. **The goal and the one CTA.** What should the reader do? One primary call to action per email
   produces measurably better emails than several competing buttons, so push for one.
3. **Key content.** The offer, dates, product names, proof points, links to source material.
   Actual facts, not vibes.
4. **The Figma file link**, if not already shared.

**Make answering feel like a short survey, not an essay assignment.** If an interactive question
tool is available (for example AskUserQuestion in Claude Code), use it for the choice-shaped
questions in a single call, and keep the free-text items (file link, key content) as plain
asks. Where no such tool exists, give each choice question lettered options so the user can
answer everything in one short line.

Go deeper only when it earns its keep: vague answers ("make it good") need one example email
they like or the landing page the email supports; a sequence needs timing per email and how the
story escalates; a multi-brand file needs to know which brand; a lifecycle email needs to know
what the recipient just did (signed up, purchased, went quiet), which drives tone far more than
brand adjectives do.

Two rounds of questions maximum, then build with sensible assumptions and say what you assumed.

## Step 2: Inspiration (shapes the brief, never the build)

Email Love's Inspiration MCP exposes a curated library of 500,000+ real marketing emails. Look
for tools named like `search_emails`, `fetch_email`, `get_brand_insights`, `list_journeys`, and
in environments where connector tools load on demand, actively search for them before concluding
they are absent. Use them when the user names a brand to draw from, when the brief is thin on
direction, or when you are building a sequence and want to see how real brands pace the same
flow (`list_journeys` / `get_journey` return actual lifecycle sequences by type).

Mine those emails for **structure rhythm** (how many sections a real welcome runs, where proof
sits relative to the CTA), subject line patterns, offer framing, and tone. Tell the user which
emails informed your choices.

Three hard rules:

- Inspiration informs the **brief**. The build still comes from Path A or Path B.
- Never copy another brand's copy verbatim. Adapt the pattern, write original words.
- **Never send a library email's preview image to the design-converter worker.** It is
  mechanically easy and it is wrong: the converter is a transcriber, not an abstracter, so what
  comes back is that brand's email with the pictures removed, headline, benefit lines, footer
  disclosure and postal address included. Path B input must be the customer's own material or a
  comp you designed for them.

If the inspiration tools are not connected and the user explicitly asked for brand inspiration,
say so up front, link the setup guide (help.emaillove.com/plugin/ai/email-inspiration-mcp), and
offer to wait or proceed on general best practice. If they did not ask, continue and mention it
once at hand-off.

---

# PATH A: the customer has an Email Love design system

Instance-only discipline. The components are the ground truth; your job is selection, copy, and
imagery.

## A1: Inventory the library properly

A shallow inventory produces every email as a re-skin of one existing campaign. A real one
produces emails whose sections fit their content.

1. **Enumerate the components.** From `list_components` if the Email Love MCP is connected (it
   returns them grouped by the customer's own categories, which are the names you should reuse
   everywhere), otherwise by listing every page in the file and searching each for COMPONENT and
   COMPONENT_SET nodes. Email Love design systems usually keep the library on dedicated pages
   (Heroes, Cards, Lists, Copy Blocks, Data, Footer) separate from the campaigns page.
2. **Study 2 or 3 of their past emails.** Screenshot and read the frames the user named as their
   best, or the most recent. Learn voice, copy length, section rhythm, imagery habits, and
   footer conventions. These are also your donor candidates for the root frame.
3. **Report the palette** to the user in one compact list.

## A2: Ask who picks the components

Every build, unless the Step 1 survey already answered it or the brief already dictates the
exact sections (then confirm that list in one line). If they defer, pick by content fit and say
what you chose and why. Use the strongest picker your environment supports:

- **Clickable card gallery.** Where a widget tool can render inline HTML with a chat bridge
  (a `sendPrompt`-style function): one card per candidate, component screenshot embedded as a
  data URI, one-line note on fit, Recommended badge on your pick. One section at a time, 3 or 4
  candidates, stable order.
- **Previews inside the question**, where the interactive question tool supports per-option
  preview content: one question per section, screenshot per option.
- **Pick in Figma**, which many users prefer: lay out a temporary frame ("Component menu, delete
  me") of labeled instances next to the build area, ask them to click their choice and say
  "picked", read the selection through the Figma MCP, confirm, move on, delete the menu at the
  end. No thumbnails, no letter mapping, real size.
- **Contact sheet fallback:** one numbered screenshot plus a matching lettered list, for the
  section types this email needs only.

Compose with a clear split: past emails teach voice and polish, the palette plus the content
decides structure. Statistics want a stats card, steps want a list component, social proof wants
a testimonial card, a single announcement wants a hero plus copy block. If your section stack is
identical to an existing campaign's, you matched the donor rather than the content.

## A3: Root frame from a donor, then vet what you inherited

**Duplicate an existing Email Love email frame.** That gives you a root carrying every plugin
setting (marker, theme colors, subject and preheader slots). The donor's value is its root
settings, not its body:

- Keep inherited sections only if they are component instances (or a raw footer block).
- **A hand-built section inside the donor** (a plain frame that is not an instance) is invisible
  to the exporter and must be replaced with a library instance or removed. This is the most
  common way an inherited email silently loses content.
- Delete inherited sections you do not need and instantiate fresh ones from the palette.

If no donor exists in the file, build the root per "Root frame" in the shared section below and
append the instances straight into it, in order. Never wrap an instance in a frame of your own:
an untagged frame between the root and an instance flattens everything below it into one image.

## A4: Assemble by instancing

The complete list of edits you may make to an instance:

- **Text content.** Load the node's current fonts, await, then mutate. Read the fonts off the
  node rather than assuming. Skipping the font load is the most common build failure.
- **Image fills** on the component's image blocks, at their existing dimensions, 2x resolution,
  watching crop and focal point. The plugin picks up image fills at export and handles hosting.
  If a geometry write inside the instance is ever unavoidable (an image band whose height has to
  match a photo's aspect), know that `resize()` on a node nested inside an instance silently does
  nothing: no error, and the value unchanged when you read it back. Render spec section 0.8 has
  the working pattern, FILL the descendant chain then resize the INSTANCE, and the habit it
  implies, which is to read every geometry write back and treat an unchanged value as a failed
  write.
- **Component properties**: toggle booleans to hide optional regions, swap instance-swap slots,
  set text properties. Because the plugin exports what is visible, a boolean that hides a region
  genuinely removes it from the sent email.
- **Plugin data**: `href`, `altText`, mobile style keys, per the shared section below.

Everything else is forbidden: **never detach**, never add, delete, or reparent layers inside an
instance, never retag anything inside it, never change its internal auto-layout, never apply a
fill to a structural frame inside it. Detaching severs the structure the exporter reads, and
restructuring internals reintroduces exactly the hand-authoring this skill forbids.

**Naming inside an instance is not your problem, so leave it alone.** A component the plugin
built carries the plugin's own naming on every node, the MJML tag in plugin data and the
friendly display name on the layer, and an instance surfaces the main component's plugin data.
Do not rename layers inside an instance to "clarify" them, and do not write plugin data onto
instance internals. The naming rules in the render spec (section 6) are for nodes you create,
and on Path A the only node you create is the root. If a component's internals look wrong,
that is a design-system fix in the source component, not something to patch per instance.

Also: **one visible CTA button per email** unless the user asks otherwise (hide competing
buttons via component properties); **leave final CTA URLs to the plugin** unless the user gave
you real URLs; **placeholder missing imagery** as flat gray fills at the existing dimensions and
say so in the report; **lay multiple emails side by side**, each in its own frame, so the team
can review a sequence at a glance.

## A5: When no component fits, stop

In order:

1. Reconsider. Most "no component fits" moments are a copy problem, not a component problem.
   Fit the content to the closest component and check with the user.
2. Ask the user directly, showing what you have and what the section needs. They often know a
   component you did not find, on a page you did not check.
3. Only if they confirm nothing exists: build that one section through **Path B** (generate and
   transcribe, not freehand), then offer to save it into their design system so it exists next
   time (see B6). A gap-fill section is a design-system asset by definition, which means it is a
   **module**, not a tiny email: build it as an `mj-wrapper` COMPONENT with **no**
   `nodeType = 'mainFrame'` marker, friendly layer names inside, the module name on the
   component itself, and properties for the parts that will change (render spec section 2.2).
   It should be indistinguishable from the components around it.

Never assemble the section by hand, and never flatten it to an image to make the problem go
away. An image in place of a section is a decision for the customer to make, not for you.

---

# PATH B: the customer has no design system yet

The new-customer path. Structure comes from the design-converter worker; styling comes from the
brand foundations and is applied on top. Say plainly at the start that you are generating a
first email and that it doubles as the first piece of their design system.

## B1: A short brand interview

Four questions, one batch, on top of the Step 1 brief:

1. **Brand basics:** logo file, primary and secondary colors as hex, and the brand fonts. Ask
   for an email-safe fallback for any font that is not web-safe (Arial, Georgia, Helvetica,
   Times, Verdana, Tahoma, Trebuchet, Courier). Never invent a substitution silently.
2. **Email width:** 600 or 640. Everything downstream is measured against this.
3. **Footer requirements:** postal address, unsubscribe mechanism, and whether their ESP injects
   the footer with a merge token (see "The footer token block" below).
4. **Do they have anything to start from?** This is the important one, and it decides B2.

## B2: Where the design comes from, best first

- **Their own past email.** The strongest input: real brand colors, real type, real logo, no
  clone risk. Accept an HTML file from their ESP, an `.eml`, or a screenshot. If they give HTML,
  render it headlessly to PNG at the email width with `--force-device-scale-factor=2`. If they
  give a screenshot, use it as is.
- **Their own non-Email-Love Figma design.** Screenshot the frame via the Figma MCP
  (`get_screenshot`) and convert that. Their file stays read-only.
- **A comp you design for them.** When they have nothing. Write the layout as a single HTML file
  at the email width using their real colors, fonts, and copy, render it headless at 2x, and
  convert that render. Let the Step 2 inspiration decide the section order and pacing; let the
  brand interview decide every color and typeface.

**First judge whether the design you were handed is AUTHORITATIVE about geometry, because only then
are its proportions worth preserving.** This is the short version of a question the migration audit
asks in full, and Path B meets it every time somebody hands over a Figma frame. Their own past email,
or a comp you wrote at the email width, is authoritative by construction: it was made to send. An old
mockup drawn to present usually is not. Four cheap signals answer it: is the design at a standard
email width, does it use real text styles rather than sizes typed per layer, is it built with auto
layout rather than absolute positioning, and are its equivalent margins identical rather than merely
similar.

- **Mostly yes: the geometry is a specification.** Derive the scale factor as below, carry the
  source's margins, ramp, and spacing across, and tell the user what you preserved. Convert its
  side margin ONCE, through the target email width, and use that one content width in every
  section (render spec 0.3.1), because the worker returns a side margin per screenshot and three of
  those in one email is a text edge that moves as the reader scrolls.
- **Mostly no: take the brand and build to email standards.** What you keep is the palette, the
  typefaces, the logo, the copy, and the order the blocks come in. **Do not derive a scale factor at
  all**, and do not preserve a source proportion: build a 600 wide email with body copy at 16 on a
  conventional ramp (12, 14, 16, 20, 24 to 30), spacing in multiples of 8, and one content width for
  every section, normally 560 with 20/20 padding. Scaling the screenshot to 600 before you send it is
  still right, but that is framing one PNG rather than a factor entering the email. Say so to the
  user in a sentence, because it is good news rather than a compromise: a margin nobody chose carries
  no decision, and dividing it faithfully reproduces a guess more precisely than it was made.

**The rest of this section is for a design you judged authoritative.**

**Check that the source is at email scale before you convert it.** A past email or a comp you wrote
yourself is at email width by construction. A Figma design drawn for presentation, or a web-first
canvas, is often some multiple of it, which means every size authored in it (a 35px body, a 53px
headline) carries that multiple, and anything you read off it or hand the worker in `promptInputs`
carries it too until you divide it out. Two cheap derivations catch
it: the frame width divided by the email width from B1, and the authored type sizes divided by the
sizes email actually uses (a 35px body over 16, a 53px headline over 24). Land near 1 and the source
is at email scale. Land near some other number and that number is your scale factor. When the two
derivations disagree by more than a few percent, trust the type ramp: a designer picks type sizes
deliberately off a ramp, while a canvas width absorbs bleed, margins, and whatever artboard someone
happened to start on. Then do two things: scale the screenshot down to the email width before you
send it, because that is the input the worker was tuned for rather than a lever on its output (the
worker classifies at a canonical email scale and returns email numbers whatever resolution you send,
so do not expect its payload to carry the factor either way: render spec section 0.6), and pin
`emailWidth` in `promptInputs` (B3), which is the setting that actually fixes the body width. Tell
the user the factor you derived; it is a judgment they may want to correct.

**A factor you derive here is ONE number, applied to EVERY quantity it governs.** Whether you scale
the screenshot before sending it or divide a source measurement you carry across by hand, the same
factor governs type
sizes, line heights, the spacing scale, paddings, and spacer heights. Rounding is allowed,
to the nearest whole pixel, after the division. Choosing a converted value because it looks like a
size email usually uses is not rounding; it is a second factor invented for one element.

**Widths are the exception, and the render spec's two factor tension (0.6) is why.** Divide the
source width by the target email width and compare that ratio to the type factor you just derived.
They agree only when the source was drawn at an exact multiple of the email width, so usually they
do not: a 1092 wide source at a 600px body is 1.82 across the width against a 2.2 type factor. When
they differ by more than a couple of percent, say so to the user and name the split rather than
picking one: the type factor governs type sizes, line heights, and the spacing scale, and the target
email width governs the body width and everything measured across it (content width, column splits,
image widths).

**Check it against the source's own ratios.** Divide the largest type size you ended up with by
the smallest, do the same in the source, and compare. More than a couple of percent apart means
something got rounded toward a pleasant number instead of divided. The failure looks like this,
measured on a real conversion: a source headline of 55 and body of 35, a ratio of 1.57, came out
as 30 and 16, a ratio of 1.88, so 1.83 on the headline and 2.19 on the body. The email read as
though its padding were wrong even though every padding value was correct, which is why this is
worth a deliberate check rather than a glance. If a converted size looks wrong, the factor is the
suspect and not the style: re-derive the factor, re-divide everything, re-run the check.

Rendering, whichever HTML you start from: headless Chrome with
`--headless=new --screenshot=<out.png> --window-size=<email width>,<tall enough for the whole
email> --force-device-scale-factor=2`, then trim any trailing blank space before sending. A
screenshot padded with empty page invites the worker to invent spacers.

Never convert a competitor's email or an Email Love library preview. Same clone problem, and the
customer has no design system to restyle it into, so a clone stays a clone.

## B3: Send it to the design-converter worker

POST to `https://design-converter.andy-30d.workers.dev`:

- **Headers:** `Content-Type: application/json`, `Authorization: Bearer` with an **empty** token,
  and `X-Auth-Provider: gumroad`. That combination is an anonymous Free user, which is allowed;
  no license key is needed.
- **Body:** `{ "screenshot": "<raw base64, no data: prefix>", "screenshotMime": "image/png" }`.
  **Set the mime correctly.** It defaults to PNG and is passed straight through, so a JPEG
  declared as PNG is a silent quality loss.
- **`promptInputs` (optional, and worth it whenever you know the design).** The worker treats
  these as truth and the screenshot as a lossy reference, so anything you pin comes back exact
  and anything you leave unpinned gets re-derived from pixels and drifts. Supported fields:
  `emailWidth` (number), `textNodes` (per text run: `content`, `fontFamily`, `color`,
  `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `textAlign`, `textCase`,
  `textDecoration`, `hyperlink`), `imageNodes` (`{ width, height, name }`), `bgColors` (array of
  hex strings), `layoutText` (a plain-text frame tree with paddings and gaps). When you authored
  the comp yourself in B2 you know all of this: send it.
- **Query params:** `nocache=1` skips the cache entirely, read and write (results otherwise cache
  for 24h on the screenshot hash); `recache=1` skips the read but still writes, which is how you
  overwrite a bad cached result; `decomposeRasterized=1` asks the worker to OCR flat image-only
  regions into live text and buttons instead of one big image, for sources that are a single
  baked screenshot.
- **Response:** the MJML JSON. `X-Cache` says HIT or MISS. `X-Trivial-Response: true` means the
  result collapsed to a single image; re-run with `recache=1` and usually
  `decomposeRasterized=1`. A full-length email takes 20 to 40 seconds.

Save the JSON to disk before transcribing, so the transcription and any later re-verification
work from a stable input.

**If your Figma MCP is read-only**, B4 cannot run and Path B is not dead: have the user paste the
render into their Figma file, select it, and hit Convert on the plugin's AI Import screen. That
calls this same worker and writes the frame for them, structure included. You then pick up at B5
and B6 by reading the resulting frame back and telling them precisely what to fix. Say up front
that this is the route you are taking and why.

## B4: Transcribe per the render spec

Follow the render spec exactly (see "References" at the end). It maps every MJML tag and
attribute to the Figma node, auto-layout, fill, and shared plugin data the exporter reads back.
Do not improvise a mapping. Run its post-build checklist per email before moving on.

**Name every node twice** (render spec, section 6). The MJML tag goes in the `name` shared
plugin data key; the layer name gets the plugin's own friendly display name for that tag
("Row (Contains columns that sit side by side)", "Text Block", "Button Text"). The exporter
resolves the tag from plugin data and never reads the layer name for dispatch, so this costs
nothing and it is the difference between a file a designer can read and a wall of `mj-`
strings. The spec has the full table. Never rely on the layer-name fallback: a node with no
plugin data tag can have the friendly label baked in as its tag by the plugin's own naming
helper, and it stops exporting.

What it maps: `mj-wrapper`, `mj-section`, `mj-group`, `mj-column`, `mj-column-inner`, and the
text, image, button, divider, and spacer leaves. **When the worker returns a tag the spec does
not map**, which in practice means a social icon row coming back as `mj-social` with
`mj-social-element` children, do not invent a node for it and do not silently drop it. Rebuild
that row from tags the spec does map: for social icons, an `mj-group` of one-column `mj-image`
pairs, each with its own `href`, which also keeps the icons side by side on mobile. Composing
from mapped primitives is the same move as rebuilding a pill as a button; inventing an unmapped
node is not. List every row you rebuilt this way in your report.

## B5: Repair what the worker gets wrong (every time, these are known)

The worker returns structure, not a finished email. Five gaps, all observed repeatedly:

1. **Pills and badges come back as `mj-text`** with an inline-styled `<div>` carrying a
   background color and a border radius. Rebuild every one as an `mj-button` (see the standing
   corrections below). A pill needs no link to be a button.
2. **The worker never emits `mj-group`.** Its whole vocabulary is `mj-wrapper`, `mj-section`,
   `mj-column`, `mj-text`, `mj-image`, `mj-button`, `mj-divider`, `mj-spacer`, and `mj-social`
   with `mj-social-element` children. Anything that must stay side by side on mobile comes back
   as plain sibling columns, which will stack. Decide which rows must not stack (badge rows, icon
   rows, two-up cards) and rebuild those as an `mj-group` per section 3.3 of the render spec.
   The columns inside that group are pinned to pixel widths, so pin them with slack rather than
   at the width Figma hugged to (section 3.3.1: a pinned column cannot grow, and the email
   renders a different font binary than the canvas does).
3. **Every `src` is `"placeholder"`.** Place the customer's real logo and imagery yourself; use
   flat gray fills at the correct dimensions everywhere else and list them in your report.
4. **Unpinned colors, radii, and fonts drift** by a few units between runs, and unpinned fonts
   flatten to Arial. Correct them against the brand foundations rather than accepting what came
   back.
5. **A photo that overlaps or bleeds past its band comes back as neither of the two things it
   could be.** Customer designs do this constantly: a product shot entering from the right behind
   body copy, an animal cropped off by the left edge of a cream band with text beside it. Email has
   no z-order and no absolute positioning, so it cannot be reproduced, and the worker only ever saw
   the flat composite, so it returns the band as one image or as text over an image that would have
   to extend past its column. **Rebuild it as a two column row per render spec 3.4.1, the Two
   Column Swap**: one `mj-section`, two `mj-column`s, image in one and text in the other in source
   order, both columns FIXED with their widths summing to the section content box, the image a
   rendered crop at its column's content width, no `mj-group` (the stack is the point, and it puts
   the image above the text on mobile). This is Email Love's standard substitute rather than a
   judgment call, so do not attempt the overlap and do not leave the band as a flattened image. When
   the source is their own Figma design you can confirm the case before converting: compare the
   image node's absolute box against the band's box, and look for a background-colored sibling
   clipping the photo by z-order rather than a mask. Say in your report that the overlap was traded
   for the two column row, since it is a visible difference from the design they handed you.

## B6: Apply the design system on top, then make it reusable

AI Import produces structure, not styling. It is not a pixel copier. Once the tree is correct,
apply the brand colors and type from B1 across every text node, button, and section fill, and
set the root frame's theme keys to the real brand values.

Then offer to make it reusable. Saving into the plugin's design system is an authenticated
plugin action on the user's current selection; you cannot push components into it. What you can
do is set it up so the save is one click.

**First decide what they are saving, because the two are different shapes and they go in
through different screens** (render spec section 2):

- **The whole email, as a starting template.** That is the `mainFrame` root you already built.
  It stays exactly as it is; the marker is required.
- **One block, as a reusable module.** That is the `mj-wrapper` inside the email, not the email
  root. Uploading a `mainFrame` as a module does not fail, it archives as a whole email, so do
  not "promote the email frame" when what they wanted was a hero. Copy the wrapper out to a
  library page, make that copy a COMPONENT tagged `mj-wrapper`, and make sure it carries **no**
  `nodeType` key. Section 2.2 has the exact calls and 2.3 the plugin evidence.

Then, either way:

- **Rename it first.** The raw Figma layer name becomes both the component name and its storage
  path, and there is no rename field in the save dialog. A frame left at its import name saves
  as a component literally called `EmailLove_clone`.
- **Add properties to anything meant for reuse.** A one-off campaign email can stay a frame with
  no properties. A module gets the two to five properties a marketer will actually change, added
  to the wrapper component itself, since that is the component that directly owns the nodes.
  Sections 7 and 8 of the render spec cover why a COMPONENT root is safe (the plugin builds every
  wrapper as one), the rules that keep it working, and the exact per-element bindings. A property
  whose binding is wrong is worse than no property, so re-read each binding back off the node
  before you present.
- **The upload route depends on which of the two shapes it is, so do not mix them up.** A whole
  email template goes in through **Custom Templates**: select the `mainFrame` root, make sure a
  design system is selected in the plugin, click **Add New Template**, pick a category. A
  **module** goes in through the **Assets sidebar**: pick the design system, open the section it
  belongs to (Header, Heroes, Single Column, Footer, and so on), select the `mj-wrapper`
  component on the canvas, click **Upload**, confirm. Selecting several wrappers at once uploads
  them as a single batch. **That Upload button only renders for a user on a paid plan**
  (`AssetsComponent.tsx` gates the whole Assets header on the subscribed state), so a Free user
  will not find it; say so rather than sending them hunting. Custom Templates refuses a module
  with "Please select valid email template", because that path requires the `mainFrame` marker a
  module must not carry.
- Do not write `saveCategory` or `saveName` plugin data. The plugin reads neither key today.

For a whole legacy library rather than one email, that is a migration, not a build: point the
user at Email Love's migration flow (hello@emaillove.com) instead of converting template after
template here.

---

# What always applies, on both paths

## The standing corrections

These are the mistakes that keep recurring. Check every build against all six. On Path A they
apply to the root and to anything you build outside an instance; they are never a reason to open
an instance and correct its internals, which the components already got right.

- **A pill, badge, tag, or chip is an `mj-button`, never a radiused column.** `mj-button` renders
  a padded, rounded, background-filled box with centered text **and the Outlook VML fallback**.
  A column with a border radius does not survive Outlook.
- **Elements that must stay side by side on mobile go in an `mj-group`.** The group is a child of
  `mj-section` and **never** of a column. MJML requires the columns inside a group to be sized in
  percentages rather than pixels, and you get that by giving each inner column an exact **fixed
  pixel width in Figma** and letting the exporter divide it by the group's content box (280 + 280
  in a 560 group exports 50/50). Do not reach for FILL sizing to express the percentage. To stop
  a whole section stacking without a group at all, set `stackColumns` to `'false'` on the section
  instead.
- **An image is an `mj-image-Frame` containing a tagged `mj-image` rectangle**, as a pair. Never
  a frame with an image fill on itself: a childless wrapper exports as an empty cell. The same
  pairing applies to text, buttons, and dividers.
- **Alignment: set both axes to the same value.** The exporter reads `primaryAxisAlignItems` for
  **horizontal** alignment, so a vertical column that looks centered on canvas exports as left.
  Every auto-layout frame you create must have `primaryAxisAlignItems === counterAxisAlignItems`.
- **Sizing is not cosmetic: heights hug, widths are a decision.** Every frame you create, from
  the root down, is vertical HUG. A fixed height clips content in Outlook and breaks the first
  time the copy runs a line longer. Vertical rhythm is auto layout padding, never a taller
  frame and never manual positioning, which does not export at all. Widths are FILL or HUG
  except where a pixel number is load bearing (the root width, columns in a multi-column
  section, columns in a group, the image rectangle). And a button sized **FILL** is what makes
  it full width on mobile, while HUG or FIXED keeps its width there, so size buttons from the
  design, not from what tidies the canvas. **Section 0 of the render spec** has the full rule,
  the padding levels, and the one exception (`mj-spacer`).
- **Colors and type come from the design system and are applied on top of the structure.**
  Generated structure is a starting shape, not a styled email.

And the reason all of this is invisible: **untagged content does not fail loudly, it gets
flattened into a picture.** Anything the exporter does not recognize hits its render-the-unknown-
as-an-image path, and an unrecognized frame takes its entire subtree with it. If your export
shows images where you expected live text, that is the first thing to check.

## Root frame

**This skill builds EMAILS, so everything here is the email-template shape**: a `mainFrame` root
with `mj-wrapper` components stacked inside it. A reusable module is a different shape (the
wrapper IS the component, no `mainFrame` marker), and it only comes up when you save a block
into the design system in B6 or A5. Section 2 of the render spec has both side by side; do not
mix them.

Preferred: duplicate an existing Email Love email frame, which carries all of this already. When
you create a root from scratch, it is a top-level vertical auto-layout frame with its width
FIXED at the email width (600 or 640), its **height Hug** (render spec section 0.1: never a
fixed height, on the root or on anything inside it), and **all nine** keys set. Empty theme keys
are not neutral: the exporter substitutes dark defaults, which wrecks a light email.

```js
frame.setSharedPluginData('emaillove', 'nodeType', 'mainFrame')
frame.setSharedPluginData('emaillove', 'backgroundColor', '#ffffff')        // dark-mode page bg
frame.setSharedPluginData('emaillove', 'contentColor', '#ffffff')           // dark-mode section bg
frame.setSharedPluginData('emaillove', 'textColor', '#000000')
frame.setSharedPluginData('emaillove', 'linkColor', '#000000')
frame.setSharedPluginData('emaillove', 'buttonTextColor', '#ffffff')
frame.setSharedPluginData('emaillove', 'buttonContentColor', '#000000')
frame.setSharedPluginData('emaillove', 'lightThemeBackgroundColor', '#ffffff') // exports as mj-body bg
frame.setSharedPluginData('emaillove', 'fallBackFontName', 'Arial')
```

Setting the dark keys equal to the light design colors makes dark mode render like light, which
is the right default for a first pass. For a genuinely dark email, invert them. All of these stay
editable in the plugin's settings panel afterward.

## Links, alt text, subject, and preheader

These live in plugin data, so set them as you build. **Node placement matters and is easy to get
wrong:**

```js
imageRect.setSharedPluginData('emaillove', 'href', 'https://example.com/pricing')  // the mj-image RECTANGLE
imageRect.setSharedPluginData('emaillove', 'altText', 'Spring collection lookbook')
buttonFrame.setSharedPluginData('emaillove', 'href', 'https://example.com/pricing') // the mj-button frame
root.setSharedPluginData('emaillove', 'emailSubject', '20% off Premium ends Sunday')
root.setSharedPluginData('emaillove', 'emailPreHeader', 'Use code SPRING20 at checkout')
```

`href` goes on the `mj-image` **rectangle** and on the `mj-button` **frame** (the inner one, not
the `-Frame` wrapper). `altText` goes on the `mj-image` rectangle. Subject and preheader go on
the root.

**Existing values win, and you cannot change them.** The plugin reads its own private data first
and falls back to the shared namespace only when the private value is empty. A link someone set
by hand in the plugin lives in private data you can neither read nor overwrite, so your value is
silently ignored. Setting these where nothing was set works; changing an existing one appears to
succeed and does nothing. Treat every link you set as provisional and list them in your report,
and when a user asks you to change an existing link, tell them plainly to change it in the
plugin.

## Mobile styles

Same pattern, on the element frame, same private-data caveat: `mobileStylesPaddingTop` /
`Right` / `Bottom` / `Left` (and `mobileStylesInnerPadding*`), `mobileStylesHideInMobileDevice` /
`mobileStylesHideInDesktopDevice` set to `'true'` (a desktop-only and mobile-only variant of a
region is two sibling nodes, one hidden each way), `mobileStylesTextAlign` / `mobileStylesAlign`,
and `stackColumns` on sections and wrappers. Use them when the brief calls for mobile-specific
behavior, and list every key you set so the user can check the plugin's mobile preview.

## The footer token block

If any email in the file carries a small frame holding ESP tokens like `{{Footer}}`, that is an
`mj-raw` block and it is how the ESP footer gets injected. **Copy that existing block into every
email you build**, rather than writing one from scratch. Three things to know:

- An `mj-raw` frame **must** contain its text child. The exporter reads the first child without
  checking, so an empty one breaks the export.
- Raw content is **skipped in the plugin's preview but present in the export**. Tell the user, so
  they do not report it as a bug.
- **If the file has no such block yet**, which is the normal Path B case, and the customer told
  you in B1 that their ESP injects the footer with a token, this is the one structure you may
  create by hand: a frame tagged `mj-raw` whose single child is a TEXT node tagged `mj-raw-text`
  holding exactly the token string they gave you, and nothing else. Everything else in the footer,
  the address, the unsubscribe wording, the social icons, is ordinary structure and comes from
  Path A or Path B like the rest of the email. If they do not use a token, skip the raw block
  entirely.

Keep raw blocks small: they skip the plugin's structure handling, mobile styles, and dark mode
entirely, and hand-written markup is where cross-client rendering breaks. Say in your report that
any raw block needs a real inbox test.

## Foundations you do not change

The **email width**, the **breakpoint**, and the **fonts** already in use are brand decisions
someone made, not defaults to improve on. If a font will not load in your environment, do not
substitute one to get the edit through. Report it and leave the layer as you found it; a silent
swap changes the brand's typography everywhere it lands.

**Dark mode overrides are read-only.** Per-node `contentColor`, `textColor`, `linkColor`,
`buttonContentColor`, `buttonTextColor` on a child node are a deliberate treatment someone chose.
Never clear or overwrite them, and do not strip them when you duplicate a donor. Name the
sections that carry them in your report. If the user explicitly asks you to set dark mode on a
section, write the keys and tell them to verify in the plugin's dark mode preview.

## Writing the content

Write like a person, not a template. Front-load the value in the first section, keep one primary
CTA, make everything scannable. For sequences, each email must escalate or advance the story; if
two emails in one recipient's path repeat the same theme, rewrite the later one. Match the brand
voice from existing copy in the file, informed by any Step 2 inspiration.

## Verify before you present

Screenshot every email and inspect it: no clipped text, no overlapping elements, spacing
consistent with the file's real campaigns. Then check structure:

- Root frame is a duplicated Email Love frame, or carries `nodeType = mainFrame` plus the eight
  theme keys, which is the nine of "Root frame" less the marker itself. It is an email, so the
  marker belongs there; the only nodes that must NOT carry it are
  any reusable modules you split out in A5 or B6.
- **Path A:** every section is a component instance (raw footer excepted), including inherited
  ones. No detached instances. No hand-built frames survived the donor vetting. No instance
  internals were restructured.
- **Path B:** the render spec's post-build checklist passes: every node tagged, every leaf a
  complete pair, every `mj-button` with a direct TEXT child, both alignment axes equal on every
  auto-layout frame, all nodes visible, and column widths summing to the email's one content width
  rather than to the side margin the worker returned per screenshot (render spec 0.3.1). Plus the five B5
  repairs done, and any tag the spec does not map rebuilt from mapped primitives per B4. If the
  source had an overlapping or bleeding photo, that band is a two column row per render spec 3.4.1,
  not a flattened image and not an attempted overlap.
- **Sizing, on both paths, for every frame you created:** vertical HUG everywhere, no fixed
  height except an `mj-spacer`, no FIXED width outside the load-bearing cases, every pinned
  width that carries text given slack (render spec section 3.3.1), all spacing expressed as
  padding, and every button's width chosen for how it should behave on mobile (render spec
  section 0).
- **Path B naming and components:** every node carries the display name for its tag and a real
  tag in plugin data, with no friendly string in the plugin data key. Anything built for reuse
  is an `mj-wrapper` COMPONENT with **no `nodeType` key**, named for the module rather than the
  wrapper display string, a direct child of its page, with every property binding re-read and
  confirmed.
- Every `mj-raw` frame contains its text child. Dark mode overrides intact. Exactly one visible
  CTA button per email unless the user asked otherwise.

Fix what fails before presenting. Then report: what you built, which path and why, which
components you chose or what the converter returned and what you repaired, what you assumed,
which inspiration emails informed the work, and everything left as a placeholder.

## Hand off

1. Review the emails in Figma and comment or edit like any design work.
2. Select a finished frame, open the Email Love plugin, and set subject line and preheader in the
   settings panel. Propose copy for both: subject under 45 characters, preheader that extends it
   rather than repeating it.
3. Export through the plugin to their ESP. Building on the canvas is free; exports count against
   the Free plan (5 per month, unlimited on paid plans).

If the plugin says "Please select valid email template" on a frame you built, the root frame is
missing its marker (see "Root frame") or the plugin version predates shared-marker support: ask
the user to update the plugin.

## References

Two reference files carry the ground truth this skill deliberately does not restate:

- **`render-spec.md`**, the complete MJML JSON to Figma mapping: sizing, which governs every
  frame you create (section 0: hug heights, padding for rhythm, when a width is FILL, HUG, or
  FIXED, button width as a mobile decision, padding by level), then **the two root shapes and
  which one you are building** (section 2: an EMAIL TEMPLATE, which is what this skill produces,
  versus a DESIGN-SYSTEM MODULE, which is what a saved block must be), then every tag, every
  attribute, alignment, fills, fonts, column width math, the Two Column Swap for a photo that
  overlaps or bleeds past its band (section 3.4.1), layer naming (section 6, with the full
  tag to display-name table), when a node is a COMPONENT rather than a FRAME (section 7),
  component properties per element type (section 8), and the post-build checklist. Path B
  transcription follows it exactly.
- **`structure.md`**, the plugin's own conventions read out of its source: how a node is
  identified, the full node type list, the leaf pair rules, and every writable plugin data key.

Both ship in the **Email Love EDS Converter skill's `references/` directory**, in this same public
repository and marketplace. **Path B does not work without them.** If they are not already in your
environment, read them from the repo before you transcribe anything:

```
https://raw.githubusercontent.com/email-love/claude-skills/main/plugins/email-love/skills/eds-converter/references/render-spec.md
https://raw.githubusercontent.com/email-love/claude-skills/main/plugins/email-love/skills/eds-converter/references/structure.md
```

If you cannot reach them and cannot install that skill, say so and stop rather than transcribing
from memory: reconstructing those rules is hand-authoring by another name.

One framing note when you read the render spec. It was written for migrations, where a customer's
legacy file is a read-only source and a separate file is the target. Here the target is the user's
own build file, and the read-only source is whatever design you converted from in B2. One rule reads
in migration vocabulary and still binds here: its **section 0.3.1**, the single content width, says
a migration's foundations phase fixes that number for the whole library. On Path A the design system
already fixed it, so read it off the components you are instancing; on Path B you fix it in B2 and
use it in every section. Every other rule applies to this skill unchanged.

## Staying current

This is version 2.9.2 of this skill. If you have web access, check once per conversation
(quietly, without narrating it) whether a newer version exists: fetch
https://raw.githubusercontent.com/email-love/claude-skills/main/.claude-plugin/marketplace.json
and compare this skill's own version to the entry named `emaillove-figma-builder` (the legacy name this skill is versioned under, kept in that file deliberately). That file lists each skill's current
version, so the check stays correct no matter which skill released most recently; the old
repository-wide latest-release check reported whichever skill shipped last, which could be a
different skill entirely. If a newer version exists, mention it once at hand-off with the right
update path for the user's surface: claude.ai users re-upload the .skill file from the newest
release, which attaches all three bundles, and Claude Code plugin users run the marketplace
update. If you have no web access, skip this silently.
