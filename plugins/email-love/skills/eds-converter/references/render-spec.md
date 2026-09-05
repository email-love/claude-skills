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

**Read section 2 before you create anything.** This spec describes two different
things: an EMAIL TEMPLATE and a DESIGN-SYSTEM MODULE. They share every rule
except the root, and the root is where the difference is fatal. A migration
batch builds modules.

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
- `mj-spacer` is the single node that ENDS with a fixed height, and 0.2 says why.
  A frame passes through a fixed vertical size in exactly one other place, the
  instance-resize remedy in 0.8, which requires it and puts it back; nothing else
  is ever left FIXED.

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
| FILL | `mj-wrapper` under the root; `mj-section` under a wrapper; a single `mj-column` in its section; `mj-column-inner`; every leaf pair wrapper as a column child; the `mj-text` TEXT node inside its frame; the `mj-divider` LINE for a full-width rule; an `mj-button` frame chosen full width (0.4) |
| HUG | `mj-group` (its width comes from the fixed columns inside it); the `mj-button` frame when it is auto-width, which is 0.4's default rather than a rule of this table; `mj-button-text`; and the transient state of any frame you have created but not yet appended and set to FILL |
| FIXED | the four cases below, and nothing else except a button deliberately pinned per 0.4 |

FIXED width is correct for:

1. **The root node**, at the numeric `mj-body` width (usually 600). This is the
   canvas the whole email is measured against. It applies to an email-template
   root and to a module's own wrapper component alike (section 2): a module is
   measured against the same body width as the emails it will live in.
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

**And where a load-bearing FIXED width sits above text (cases 2 and 3, plus a
FIXED button in 0.4), pin it with slack, never at Figma's hug width.** The pixel
you measured is measured in the font Figma rendered; the email declares a
different stack and a pinned column cannot grow. Section 3.3.1 has the rule, the
numbers, and the failure signature.

#### 0.3.1 CONTENT WIDTH is a foundation, decided once for the library

Content width is the width text actually occupies inside a module: the body width
minus the side margins that hold the copy off the edge. **It is a FOUNDATION,
decided once for the whole library and used by every module, not a per-module
value taken from whatever the worker returned for that screenshot.** The sizing
modes above say which node owns the width; this says what the number is, and it is
the same number in every text-bearing module in the file.

**The mechanism of the failure, stated plainly, because it is structural rather
than careless.** The design-converter worker sees ONE screenshot at a time. It has
no knowledge of the module's siblings, no memory of the module converted before
it, and no access to the library's foundations, so the section and column padding
it returns is a guess made per module BY CONSTRUCTION. Each guess is individually
defensible. Accepting each one as authoritative therefore does not risk drift, it
guarantees it: six modules converted from six screenshots will carry several
different content widths unless something outside the worker fixes one number.

**Measured, across the modules of one assembled email:**

| Module | Content width | Side margin |
| --- | --- | --- |
| Logo header | 504 | 48 |
| Hero, text led | 560 | 20 |
| Testimonial | 520 | 40 |
| Cream section | 520 | 40 |
| Copy Block | 560 | 20 |
| Footer | 560 | 20 |

Three content widths in one email, out of six independently reasonable guesses.

**The failure signature, which is what a reviewer actually notices: the text left
edge MOVES as you scroll.** 20px in, then 40px, then back to 20px. Nobody reads
that as a padding value being wrong, because no individual padding value IS wrong:
48, 40, and 20 are all ordinary column paddings, and each one looks correct inside
the module it belongs to. What is wrong is that they are not the same number, and
that is only visible ACROSS modules. So it survives a per-module review, passes
every other check in this spec, and gets caught the first time somebody scrolls a
finished email, which is the most expensive moment to find it.

**The remedy: the foundations phase fixes ONE content width, and every module uses
it.** Foundations decides the number and records it (converter Phase 2); Phase 3
applies that number instead of the worker's. Section padding then follows from the
content width rather than the other way round, and what has to equal the library
number is the TOTAL side inset, the section's horizontal padding plus the outer
column's, because the worker splits that margin across the two levels however it
likes. Carry it on the section and leave the outer column's horizontal padding at 0
unless the design needs an inner gutter: with a 600 body and a 560 content width,
every text-bearing section carries 20/20 and every module's text starts at the same
x. Same discipline as the single scale factor in section 0.6 where a factor
applies, and for the same reason: uniformity is the whole point, and it is lost the
moment one value is arrived at some other way. **This rule holds on every fidelity
tier**, because it is about agreement between modules rather than agreement with the
source: on a reference-only source the number is simply 560 on a 600 body, taken from
the standards instead of derived from a source margin.

**Two sanctioned exceptions, and the invariant that covers both.** The invariant is
that the **outer edge of a text-bearing block** sits at the library content width.
Full-bleed image bands are the first exception and run to the full body width,
because bleeding is the design intent, not a padding difference: a 600 wide image
band beside a 560 content width is correct, and a 600 wide text row is not. A
**card or inset block** is the second: its own edge sits at the library content
width (or at a narrower width the audit's Spacing system named as an exception),
and its card padding insets its content further. A 540 card carrying 25px padding
around 490 of content is correct and is not a content-width violation; the audit's
Spacing system census defines "card or inset padding" as its own role for exactly
this case. What is still forbidden is a plain text section arriving at a different
total side inset from its siblings.

When verifying, compare the **band edge**, not the innermost content box, and
remember that columns inside an `mj-group` sum to the group's width, not to the
section content box (section 3.3). A literal ONLY-exception reading of this rule
produced two false failures on correct card modules and a third on a correct
centred group before it was rewritten this way.

For a multi-column row the content width is still the number the columns sum to
(sections 3.3, 3.4, 5.4): a 560 content width takes columns plus gutters summing to
560. Widening a row from 520 to 560 means the added 40 goes to the column that has
slack, normally the text column, holding the image column and the gutter fixed, so
the sum is re-derived rather than the margin quietly re-invented. Worked:
`40 + 136 + 24 + 360 + 40 = 600` becomes `20 + 136 + 24 + 400 + 20 = 600`.

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
| `mj-section` | 0 to 20, often 0 | Many designs keep section padding at 0 and control all spacing at column and element level. Horizontal section padding also defines the content box that column percentages are computed against (section 3.2), and its horizontal value comes from the library's one content width (0.3.1), not from the worker |
| `mj-column` | 0 horizontal, 10 to 20 vertical | The most commonly adjusted level for VERTICAL room around text, images, and buttons. Horizontal is different: a column's side padding is part of the TOTAL side inset that 0.3.1 fixes, and 0.3.1 carries that inset on the section, so this stays 0 unless the design needs an inner gutter (a multi-column row's gutter is exactly that case) |
| Leaf pair wrapper (`mj-text-Frame`, `mj-image-Frame`, `mj-button-Frame`, `mj-divider-Frame`) | sparingly | Fine tuning one element, for example 10px above a button but not above the text over it |
| `mj-button` `inner-padding` | from the MJML, symmetric only | This is the button's tap target, not layout spacing. Asymmetric values round-trip wrong (section 4.3) |

In a conversion the worker's paddings are authoritative with exactly ONE
exception, and the exception is horizontal: **the side inset that holds copy off the
body edge comes from the library's single content width (section 0.3.1), never from
the worker**, because that number is a foundation and the worker's is a per-module
guess by construction. That inset is the section's horizontal padding plus the outer
column's, since the worker puts the margin at either level, and 0.3.1 says to carry
it on the section. Every other padding in the JSON, every vertical value above
all, is transcribed exactly, as the number it already is. They come back at email
scale whatever resolution you sent the screenshot at, so there is no scale
conversion to apply to them (section 0.6). The ranges above are for gaps you have
to invent, and for judging when a converted value is obviously wrong.

Four things that keep padding honest:

- **Be consistent.** Pick a base unit (8px is a good one) and use multiples of
  it across the whole module rather than mixing 20 and 30 between rows.
- **Padding sits inside the box and eats content width.** Two 50 percent columns
  with 20px on each side lose 80px of content width in total.
- **Outlook** ignores very small values (under 5px) and handles even numbers more
  predictably.
- **Mobile padding is a separate override** (`mobileStylesPadding*`), not a
  reason to compromise the desktop value.

### 0.6 Every number here is at EMAIL scale, never source scale

Widths, type sizes, paddings, radii, and image dimensions in this spec are email
pixels: a 600 or 640 body, a 16px body copy, a 20px section padding. **How you
ARRIVE at those numbers has two answers, not one, and the audit's SOURCE FIDELITY
tier says which one you are under.** Read that tier before you read the rest of
this section, because half of what follows does not apply to a given migration.

- **AUTHORITATIVE or PARTIAL: the source's geometry is a specification, so you
  divide.** A source file that was never meant to export as email is often drawn at
  a multiple of email scale, and the migration audit settles the factor once (its
  **Scale factor** section, a number a designer confirmed) so every module in the
  library is built against the same one. Everything in this section about factors,
  ratios, and the two factor tension is written for these two tiers.
- **REFERENCE ONLY: the source's geometry is not a specification, so there is NO
  FACTOR and nothing to divide.** The numbers are email standards, stated rather
  than derived: a **600** body, **one content width for the whole library** at 560,
  a ramp with **body at 16** (12, 14, 16, 20, 24 to 30), and a **spacing scale in
  multiples of 8**. From the source you take the palette, the typefaces, the logo,
  the copy, and the module structure. You take no measurement, so there is no
  arithmetic to get wrong and no ratio to preserve. Skip to "REFERENCE ONLY: no
  factor, and no missing number" at the end of this section.

**The worker is scale-agnostic: its numbers do NOT arrive at the scale of the
screenshot you sent.** It classifies semantically at a canonical email scale
rather than measuring your pixels. Measured: a 768px wide screenshot sent for a
600px build target came back with `mj-body` width 600 and round email-scale values
throughout (24, 16, 40), with nothing in the payload tracking the input
resolution. Still send a PNG at the target email width, because that is the input
the worker was tuned for, but send it for reliability rather than as a lever on
the arithmetic.

Three consequences:

- **Do not compute a scale conversion on the worker's returned numbers expecting
  it to matter.** It is usually a no-op, and treating it as meaningful invites a
  second factor into a system whose whole rule is one factor (this section, plus
  the ratio test below).
- **Where a factor exists it still matters enormously, just not for worker
  output.** It is for reading the SOURCE, which is what the authored sizes divide
  by, and for cropping and sizing images taken out of the source file (section
  4.2.1). On a REFERENCE ONLY source it is the target width that does that second
  job: an image comes across at the width of the column it lands in, at the crop's
  natural aspect, with no factor in the arithmetic.
- **Do not assume a future worker version behaves the same way.** Sanity check ONE
  returned number against the target width before trusting the whole payload; the
  root `mj-body` width is the cheapest. If that number is not the width you are
  building to, the payload is at some other scale and every number in it needs
  dividing.

**The rest of this section, down to the REFERENCE ONLY heading, is for an
AUTHORITATIVE or PARTIAL source.**

So divide source measurements by that factor before they become geometry here,
and never carry a source pixel across untouched. A module built at source scale
passes every other check in this spec: it hugs, it is tagged, it exports. It is
simply two or three times too big, which shows up as a body size no email uses
and a root wider than the body, and it only becomes obvious next to a module
built correctly. If you find yourself deriving the factor from the file rather
than reading it from the audit, stop: a fresh derivation silently overrules the
decision a human already made between two disagreeing derivations, and on a
REFERENCE ONLY source it manufactures a decision nobody made at all.

**One factor, chosen once, applied to EVERY quantity it governs.** Not type sizes
only: line heights, the spacing scale, paddings, spacer heights, radii, border
widths. Uniformity is the entire point of settling on a single number, and it is
lost the moment any one value is arrived at some other way. **Widths are the one
thing it does not govern, and THE TWO FACTOR TENSION below is why:** the body
width, and everything measured across it (content width, column splits, image
widths), comes from the target email width instead. Rounding is allowed,
but only to the nearest whole pixel, and only after the division. What is not
allowed is picking a converted value because it looks like a size email usually
uses. That is a second factor, invented for one style, wearing the costume of a
sensible number.

**Then check the result against the source's own RATIOS.** Divide the largest
converted type size by the smallest and compare that to the same ratio in the
source. Do it for the ends of the spacing scale too. If the two ratios differ by
more than a couple of percent, per-style rounding has crept in, and the drift is
somewhere between the number you divided and the number you wrote down.

**The failure this catches, measured in a real converted module.** The source was
drawn above email scale: headline 55, body 35. What got built at 600 wide:
headline 30, body 16. That is two different factors inside one module, 55/30 =
1.83 on the headline and 35/16 = 2.19 on the body, and the consequence is that
the source's own type relationship did not survive. The source
headline-to-body ratio is 55/35 = 1.57; the built one is 30/16 = 1.88. The
headline is 20 percent too large relative to the body.

The audit had done its job. It reported 1.815 from the canvas width and 2.2 from
the type ramp, named the 21 percent gap, and recommended 2.2. Foundations then
built the ramp style by style toward round email numbers, a 65 to 30, a 55 to 25,
a 35 to 16, and per-style factors came back in through that rounding, so the
recommended factor was never actually applied to anything.

What makes it expensive is the symptom, because it does not present as a type
problem. The module reads as though its padding is wrong: a headline 20 percent
oversized crowds the space around it, so the reviewer goes hunting through
padding values that are every one of them correct, and finds nothing. The ratio
check finds it in one division.

**A converted size that looks wrong is evidence against the FACTOR, not licence
to adjust one style.** If a 25px headline looks small, the reading is that 2.2 may
be the wrong factor for this library. Revisit the factor, put the whole ramp
through the new one, and re-run the ratio check. Never nudge the one style and
leave the rest where they were. One style nudged is this bug; the whole ramp
moved together is a decision, and it is a decision that belongs back with the
audit and the designer who confirmed the factor.

**THE TWO FACTOR TENSION: choosing a target email width AND a type factor
independently reintroduces two factors.** This is the exception the single-factor
rule above just named, and it has to be declared rather than resolved. The width ratio and the type ratio only agree when the source happens
to have been drawn at an exact multiple of the target width, and a mockup drawn
to present is not drawn to email proportions, so usually they do not agree.

Measured on the migration this note comes from: a 1092 wide source built to a
600px body has a width ratio of 1092/600 = 1.82, while the confirmed type factor
was 2.2, and 1092/2.2 = 496 rather than 600. So the build carried 2.2 on its type
and 1.82 across its width, and nothing in the process ever said so out loud. It
surfaced in the margins: the source's consistent 115px text margin is 52px through
the type factor and 63px through the width ratio, and the library was built at
20px, which is neither. The single-factor rule had been applied to the type ramp
and never to the width decision.

**The check, run once in foundations and stated in the report:** divide the source
width by the target email width, compare that ratio to the chosen type factor, and
if they differ by more than a couple of percent, SAY SO and name which factor
governs which quantities. Do not leave it implicit. The defensible split, and the
one to state unless a designer decides otherwise, is that the type factor governs
type sizes, line heights, and the spacing scale, while the target email width
governs the body width and everything measured across it (content width, column
splits, image widths). The reason is that the email width is a hard constraint from
the clients rather than a choice, and legibility is a hard constraint on type, so
neither quantity can be bent to make the two ratios meet. Write it down as a
sentence with both numbers in it.

**This is a genuine tension with no clean answer, not a bug with a fix.** No single
factor both preserves the source's type ramp and preserves its proportions across a
body width email can actually use, because the source was drawn at a width email
cannot use. Naming the split is the honest outcome. Picking one factor and pretending
it covered both quantities is how a converted library ends up with margins nobody
can trace back to a decision, which is the defect section 0.3.1 exists to prevent.

**REFERENCE ONLY: no factor, and no missing number.** On a source whose geometry was
never a specification, the tension above does not arise, because it is a tension
between two ways of preserving a proportion and this tier preserves none. So:

- **Derive nothing.** Not from the width, not from the ramp, and not "for
  information" beside the real numbers. A factor recorded anywhere gets applied by
  whoever reads it next, whatever caption sits next to it.
- **The numbers are the standards** listed at the top of this section: a 600 body,
  560 content width, body at 16 on a 12/14/16/20/24-to-30 ramp, spacing in multiples
  of 8, one content width for every module and one section padding library-wide. Rounding
  onto a multiple of 8 is not a second factor here, it is the specification.
- **There is no ratio check**, because the ratio test proves a single factor was
  applied uniformly and there is no factor. A ramp that was eyeballed style by style
  has no ratio worth matching. What replaces it is a read-back: the built ramp is the
  standard ramp, body at 16, each step present once.
- **A module whose margins do not match the source is CORRECT**, and the foundations
  report and every batch report have to say so in words. Otherwise the next person to
  open both files reads the difference as a defect and corrects the library back
  toward the source, which reintroduces exactly what this tier discarded.
- **The failure this branch exists to prevent, measured.** A factor was derived on a
  reference-only source and applied faithfully, and the result was a 16px body inside
  20px margins: both numbers correctly divided out of a source where nobody had chosen
  either. Every arithmetic step was right. The premise was wrong.

### 0.7 DOUBLE PADDING: a gap belongs to ONE block, never to both

The space between two stacked blocks is one decision, made once, on one node.
When the block above already carries a `paddingBottom`, the block below must NOT
add a `paddingTop` for the same gap, and the reverse. Setting both is not "a
little more room": the two values add, so a 40 below the section above plus a 30
above the block below renders as 70, and the module reads as broken to the
designer who drew it.

**Failure signature**, in the order you notice it:

- The gap looks roughly twice what the design shows, while each of the two
  paddings that produced it is individually plausible. That plausibility is why
  this survives review.
- A leaf frame's height exceeds its content by exactly the padding you wrote,
  and the module's total height is over by the same number. An `mj-image-Frame`
  measuring 362 around a 332 rectangle is a 30 that should not exist.
- Removing either value alone fixes the look. That is the proof there were two.

**Where to put it: on the preceding block's `paddingBottom`.** Prefer trailing
space over leading space so that each block owns the gap that follows it. Then a
block switched off (`visible = false`, or a BOOLEAN component property, section
8.2) takes its spacing away with it, instead of leaving a hole where lead-in
space on the next block used to be paid for by a neighbor that is now gone.

This holds at every level, not just section to section: wrapper to section,
section to column, column to leaf pair. Before writing any padding, read what
the sibling above it already carries. In a conversion the worker JSON paddings
are authoritative and already complete for vertical rhythm (section 0.5; the
horizontal section padding is the one value foundations overrides, section 0.3.1),
so a vertical padding you add on top of them is almost always this bug.

**At library level the inter-module gap has a fixed owner: the module
wrapper's `paddingBottom`.** Give every module's wrapper a `paddingBottom`
from the audit's spacing ladder (32 in the measured library) and the LAST
module (the footer) 0, so a module switched off takes its spacing with it
instead of leaving a hole paid for by a neighbour that is now gone. Then zero
any section-level vertical padding that was doing inter-module duty: three
modules in the measured library got SHORTER when their 24/24 section padding
stopped double-serving as the gap, while the space between modules grew. Two
modules touching with zero gap on the canvas is the tell that the owner is
missing.

### 0.8 A geometry write inside an INSTANCE can silently NO-OP, so read it back

`resize()` on a node nested three or more levels deep inside a component instance
does nothing. Measured while fixing an image band: no error is thrown, the call
returns as though it worked, and the dimensions read back unchanged, even after
explicitly setting `layoutSizingVertical = 'FIXED'` on that node first to rule out
a sizing mode overriding the write. **Only the instance root accepts an explicit
resize.**

**The symptom is that it looks like the write succeeded**, and that is the whole
cost of this bug. Nothing surfaces: no exception, no warning, no partial result.

**Range writes on text share the failure mode.** A `setRangeFills` (or any
`setRange*`) call can silently not take: measured, a two-color headline range
fill did not apply on the first call, no error raised, discovered only by
reading segments back. Treat range writes like geometry writes: after writing,
read back with `getStyledTextSegments` for the property you set and confirm the
segmentation is what you intended.
The time goes into re-checking the number you passed, the units, the order of the
calls, and the parent's sizing, because the one thing that is actually wrong, that
the write never landed at all, is the one thing the API did not tell you.

**The working pattern**, in this order:

1. Set `layoutSizingVertical = 'FILL'` down the whole descendant chain, from the
   instance's own child to the node you actually want to resize.
2. Set `primaryAxisSizingMode = 'FIXED'` on the top-level INSTANCE. On a VERTICAL
   auto-layout frame that is the same property 0.1 forbids, and the API leaves no
   way around it: a frame hugging its primary axis absorbs the resize and reads
   back unchanged. So this is the one sanctioned transient FIXED height in the
   spec, live only for steps 3 and 4, and step 5 is what makes it transient.
3. `resize()` the INSTANCE. The height cascades to every FILL descendant.
4. Read the target node's dimensions back and confirm they moved.
5. Put the sizing back where section 0.1 wants it. The FILL chain and the FIXED
   instance root are how the height TRAVELS, not the shape you hand off: once the
   target node carries the height, set its own vertical sizing to FIXED (a
   RECTANGLE carries its pixels and has no hug, section 4.2), then return the
   descendant frames and the instance root to HUG, and read those back too. The
   finished module still has to pass checklist item 7, where nothing but an
   `mj-spacer` is left with a fixed height.

**The habit this implies, and it is the part that generalizes past this one bug:
after ANY geometry write inside an instance, READ IT BACK, and treat an unchanged
value as a FAILED WRITE rather than as a no-op that did not matter.** The same
holds for sizing modes and paddings written to instance internals. A build that
verifies its own writes catches this in seconds; a build that trusts them catches
it at design review, if at all.

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
   Never insert helper/group frames that are not one of the tags above. **The one
   sanctioned untagged frame is an editable-image region**, where a migration's
   inventory row carries verdict B or C and the design content is placed in a
   column deliberately untagged so the exporter flattens exactly that region. That
   is a decision you record in the report, not a frame you forgot; everywhere else,
   and in every email built outside a migration, untagged means broken.
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

## 2. WHICH ARE YOU BUILDING? Email template or design-system module

**Answer this before you create a single node.** There are exactly two root
shapes in an Email Love file. They are not variations on each other and they are
not interchangeable. Building the wrong one does not produce a slightly-off
file: it produces a module that uploads as a broken email, or an email the
plugin refuses to open.

| | **EMAIL TEMPLATE** | **DESIGN-SYSTEM MODULE** |
| --- | --- | --- |
| What it is | One sendable email | One reusable block that gets dropped into many emails |
| Root node | FRAME (or COMPONENT) that carries NO `mj-*` tag | COMPONENT that **is** the `mj-wrapper` |
| `nodeType` = `mainFrame` | **REQUIRED** on the root | **FORBIDDEN.** Nothing stops the upload: the marker makes the block archive as a whole email |
| Shared `name` on the root | none (the root is untagged) | `mj-wrapper` |
| Theme color keys | all eight, on the root, alongside the `nodeType` marker (2.1) | none by default (see 2.2) |
| Root layer name | the email name | **the module name** (it becomes the saved component name and its storage path) |
| What lives directly inside | `mj-wrapper` components, stacked | `mj-section` frames |
| Component properties | rarely; a campaign email is a one-off | **yes, they live here** (section 8) |

The one-line test: **is this a whole email someone will send, or one block
someone will place into many emails?** Heroes, footers, copy blocks, 2-up
product rows, banners: those are modules. Phase 3 of a migration builds
**modules**, not emails.

**A module is not a small email.** An email template root *contains* wrapper
components; a module *is* one of those wrapper components. So a module has no
wrapper inside it and no `mainFrame` above it. If your module root is a
`mainFrame` containing an `mj-wrapper`, you have built a one-wrapper email and
mislabelled it, and section 2.3 explains why the plugin will reject it.

Sections 3 through 6 apply identically to both shapes. Only the root differs.

### 2.1 EMAIL TEMPLATE root (one per MJML document)

Create a top-level FRAME on the target page. It may be a COMPONENT instead
(section 7) when the whole email is meant to be reused; nothing below changes.

- **Geometry:** `resize(W, 100)` where `W` = numeric `mj-body` `width`
  (usually `600`), then `layoutMode = 'VERTICAL'` and immediately
  `layoutSizingVertical = 'HUG'`, horizontal FIXED at `W`.
  `primaryAxisAlignItems = counterAxisAlignItems = 'MIN'`. `itemSpacing = 0`,
  all paddings 0.
  The `100` is a throwaway that gets the node onto the canvas; the root's real
  height is whatever its content hugs to, and it must never be left FIXED
  (section 0.1). The width is one of the four load-bearing FIXED widths (0.3).
- **Layer name:** the email name (this becomes the component name and S3 path
  if the frame is later saved, so keep it clean). Do NOT put a tag in the root
  layer name, and do NOT write a `name` key on it: the root is identified by
  `nodeType`, not by a tag.
- **Shared plugin data (namespace `emaillove`), all REQUIRED:**

  | key | value |
  | --- | --- |
  | `nodeType` | `mainFrame` (this is how the plugin recognizes the template; without it nothing else matters) |
  | `backgroundColor` | DARK MODE page background. House default `#000000` |
  | `contentColor` | DARK MODE content/section background. House default `#1F1F1F` |
  | `textColor` | DARK MODE text color. House default `#FFFFFF` |
  | `linkColor` | DARK MODE link color. House default `#FFFFFF` |
  | `buttonTextColor` | DARK MODE button label color. House default `#000000` |
  | `buttonContentColor` | DARK MODE button background. House default `#FFFFFF` |
  | `lightThemeBackgroundColor` | the LIGHT mj-body background hex; exports as mj-body `background-color` (defaults to `#ffffff` when empty). The one light value in the set |
  | `fallBackFontName` | `Arial` |

  **The six theme keys are DARK MODE values, and filling them with the light
  palette ships light-on-light.** An earlier revision of this table said to use
  the design's own light hexes ("so dark mode matches the design", "renders
  identical to light"); that was verified WRONG against the exporter's dark-mode
  CSS: those keys only fire inside the dark-mode media query, so a light
  `backgroundColor` puts light text on a light ground the moment a client flips
  to dark. Always set all of them. Where the values come from, in priority
  order:
  1. The audit's Palette section carries a dark-mode proposal per role with
     contrast ratios; use it on EVERY email root, identically.
  2. Where no audit proposal exists, use the house defaults above, which are
     the exporter's own dark CSS values, and flag for design review. Never
     substitute the light palette as a stand-in.
  3. Sanity-check the proposal's `contentColor` before writing it: in dark
     mode it is painted on the WRAPPER while section and column fills are
     forced to transparent, so every filled cell flattens into that ONE
     surface. A brand hex that belongs to one surface (a footer band that
     stays its color in both modes) is a per-node override on that module
     (section 2.2), not the global value. Measured: a proposal that promoted
     one surface's green to contentColor turned every card in the library
     green in dark mode and put brand-green image ink on that same green at
     near 1:1. The global key takes the neutral default; the surface keeps its
     color through the override.

  **And say in the hand-off that dark mode flattens module fills.** Whatever
  contentColor is, a mint card, a peach band, and a white plate all collapse
  into the one wrapper surface in dark mode; cards do not read as cards. That
  is exporter behaviour, unreachable from Figma; surface it as a product
  limitation instead of building around it. In particular an image background
  is NOT a workaround: images are not erased, so a baked card keeps its light
  colors under forced-white text.
- Optional: `emailSubject`, `emailPreHeader` (plain strings).
- Also give the root frame a visible SOLID fill of the body background so the
  canvas looks right.
- Children: the `mj-wrapper` components in document order (section 3.1 builds
  them). After appending each wrapper set its
  `layoutSizingHorizontal = 'FILL'`.

The `mjml`, `mj-head`, `mj-body` tags themselves produce NO Figma nodes; the
exporter reconstructs them (body width comes from the root frame's width).

### 2.2 DESIGN-SYSTEM MODULE root: the mj-wrapper IS the component

There is no separate root. Create a COMPONENT and tag it `mj-wrapper`. That
component is not a container that holds a wrapper; it **is** the wrapper, so
section 3.1 describes this exact node, minus its "direct child of the root"
line: in a module there is nothing above it.

```js
const moduleRoot = figma.createComponent()
moduleRoot.name = 'Hero, text led'                                   // the module name
moduleRoot.setSharedPluginData('emaillove', 'name', 'mj-wrapper')    // the ONLY required key
// and NOT: setSharedPluginData('emaillove', 'nodeType', 'mainFrame')
```

- **Node:** COMPONENT (`figma.createComponent()`), a direct child of its
  category page. Not a FRAME: `addComponentProperty` does not exist on a
  FrameNode, so a frame module can never carry properties. Section 7 has the
  four rules that keep a COMPONENT root working (page child, never inside a
  COMPONENT_SET or a Figma SECTION, bind properties at the level that owns the
  node, never write `isStandalone`).
- **Shared `name` = `mj-wrapper`.** This single key is what makes the plugin
  treat the selection as a saveable top-level block rather than a fragment. A
  module tagged `mj-section` or left untagged is not a module.
- **`nodeType`: never write it.** Not `mainFrame`, not anything else. This is
  the rule the last conversion batch broke, and 2.3 is the evidence.
- **Layer name = the module name**, clean and human, because it becomes both the
  saved component name and its storage path, and there is no rename field in the
  save dialog. `Hero, text led` and `Footer, legal + social` are good;
  `EmailLove_clone`, `Frame 42`, and anything containing `mj-` are not. This is
  the one place in the spec where the layer name is load bearing rather than
  cosmetic.
- **Geometry:** identical to an email root. `resize(W, 100)`, then
  `layoutMode = 'VERTICAL'`, `layoutSizingVertical = 'HUG'`, horizontal FIXED at
  `W` (the email width), `primaryAxisAlignItems = counterAxisAlignItems = 'MIN'`,
  `itemSpacing = 0`. A module is measured against the same body width as the
  emails it will live in.
- **Paddings, fill, radius, `fullWidth`, `stackColumns` / `reverseStack`:** all
  per section 3.1. They are wrapper attributes and this node is the wrapper.
- **Children:** `mj-section` frames in order, each set to
  `layoutSizingHorizontal = 'FILL'` after append. **No `mj-wrapper` inside a
  module** (a wrapper inside a wrapper is not a shape the exporter maps), and no
  `mainFrame` anywhere in the subtree.
- **Component properties live here** (section 8). Every property a marketer will
  touch is added to this component, because it is the component that directly
  owns the section, column, and leaf nodes.
- **Theme color keys: leave them off unless a designer asked for a dark-mode
  treatment on this specific block.** They are not the email-level theme when
  they sit on a wrapper; they are per-node dark-mode *overrides*. The plugin
  writes `backgroundColor` / `contentColor` / `textColor` / `linkColor` onto
  every wrapper component it creates (`UiParser.ts:1570`), so those four are
  legitimate here, but they only ever mean "override the enclosing email for this
  block". `buttonContentColor` and `buttonTextColor` are worse: the exporter
  emits them unconditionally whenever they are non-empty, without comparing them
  to the enclosing email, so a module carrying them ships its own dark-mode CSS
  into every email it is placed in. A module inherits nothing and conflicts with
  everything, so the safe default for a converted module is **no theme keys at
  all**; the email root supplies them. The one sanctioned per-node use from a
  real migration: a module whose surface keeps its brand color in BOTH modes
  (a footer band, say). Write `contentColor` with that hex on the module's
  MAIN component, once: instances mirror shared plugin data (verified by
  writing only the main and reading the key back through the instances inside
  two QA emails). The four conditional keys are safe for this because they
  emit only when they differ from the enclosing email; `buttonContentColor`
  and `buttonTextColor` remain the unconditional pair to avoid.

### 2.3 The evidence, so this reads as ground truth rather than preference

Read at `origin/main` of `email-love/Figma-plugin`. All citations are
`path:line` under `src/`.

1. **Every `mj-wrapper` the plugin builds is already a COMPONENT.**
   `UiParser.ts:1519-1522`:
   `if (tag === MjmlNodeType.Wrapper || isStandalone) frameNode = figma.createComponent(); else frameNode = figma.createFrame();`
   So a wrapper-as-component is not an agent convention layered on top of the
   plugin; it is what the plugin itself produces every time it renders MJML into
   Figma. Purple wrapper components inside a plugin-built email are normal. Do
   not "fix" them into frames, and do not wrap one in something else to make it
   look like a root.
2. **The two shapes go in through two different screens, and each one rejects
   the other.** Custom Templates, Add New Template is the email-template route:
   `AddTemplate.tsx:62` is the only caller of `select-component` and it always
   sends `customType: 'customProperties'`, which lands in `code.ts:3226-3236` and
   rejects any selection *without* the marker, with "Please select valid email
   template". A module has no marker, so that dialog can never take one. The
   module route is the **Assets sidebar Upload button**
   (`AssetsComponent.tsx:610-632`), which needs a selected design system and
   dispatches `syncTemplateUpload` (`code.ts:3861`), taking an array of node ids
   when more than one node is selected, so a whole approved batch uploads at once.
   (`select-component` also has a mirror-image module branch at
   `code.ts:3280-3307` that rejects a selection carrying the marker. No UI reaches
   it today; read it as intent, and read point 3 as the live mechanism.)
3. **The design-system upload path keys off the `mj-wrapper` tag, not the marker.**
   `code.ts:3892-3893`:
   `const isTopLevel = getName(getMetaName(selectedNode)).tagName === 'mj-wrapper' || ...`
   Only when `isTopLevel` is true does the plugin wrap a clone in its own
   temporary `mainFrame` envelope and generate the MCP companion JSON
   (`code.ts:3934`, whose own comment notes that bare sections and columns "would
   emit a fragment the backend can't compile"). A module root that is not tagged
   `mj-wrapper` is archived as if it were a whole email and gets **no MCP JSON at
   all**.
4. **Marking a node both ways is worse than either mistake.** In both
   serializers the `mainFrame` branch is tested *before* any wrapper handling
   (`nodeJsonExtractor.ts:282` versus the wrapper branch at `1587`;
   `exportTemplate.ts:180` versus `285`). First match wins. So a node carrying
   `name = mj-wrapper` **and** `nodeType = mainFrame` passes the `isTopLevel`
   check, gets cloned into the temp envelope, and then still matches the
   `mainFrame` branch inside that envelope, producing a nested `mjml` document
   inside `mj-body` that nothing downstream can compile.

**Strip `nodeType` from every module component. Non-negotiable.**

---

## 3. Containers

### 3.1 mj-wrapper

**In an email template** this is a node inside the root. **In a design-system
module this node IS the root** (section 2.2): same tag, same attributes, same
auto-layout, but created as a COMPONENT with no `mainFrame` above it and none on
it. Everything below applies to both; only the "direct child of the root" line
and the node type change.

- Node: FRAME as a direct child of an email root; COMPONENT as a module root.
  The plugin itself creates every wrapper as a COMPONENT
  (`UiParser.ts:1519-1522`), so a COMPONENT here is normal in either shape.
- Shared `name` = `mj-wrapper`.
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG (never FIXED, section
  0.1), horizontal FILL under an email root or FIXED at the email width as a
  module root (section 2.2, and 0.3 case 1: a module root has no auto-layout
  parent to FILL against),
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
  (FILL under the wrapper), then set its horizontal padding from the library's
  content width rather than from the worker (section 0.3.1: a 560 content width
  on a 600 body is 20/20), keep its vertical padding as the worker gave it, and
  make each column's pixel width sum to that content width. Where the worker's
  side margin and the library's disagree, the library wins and the column widths
  are re-derived to the new sum (0.3.1 has the worked example).
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
- **Never fill the group itself: a filled `mj-group` goes white-on-white in
  dark mode.** The exporter's dark CSS forces every text span to `#FFFFFF`,
  paints `contentColor` on the WRAPPER, and forces section and column
  backgrounds to `transparent`; it has no group selector, so a group's own
  fill survives dark mode untouched while the text on it turns white.
  Measured: a white policy card whose fill sat on the group shipped `#FFFFFF`
  text on a `#FFFFFF` card, invisible in both batch renders because they were
  light mode. (An earlier reading said filled cells are RECOLORED to
  contentColor; a later read of the exported dark CSS corrected it: module
  fills are ERASED to transparent over the contentColor wrapper, visually the
  same flattening by a different mechanism.) So put the band fill on the
  group's columns instead: light mode is pixel-identical, and in dark mode the
  erased fill lets the card flatten into the wrapper surface with white text
  like every other filled cell. A filled
  `mj-group` is a verification FAIL (skill Phase 3 step 5, Group 4).
- Children: two or more `mj-column` frames with FIXED pixel widths.
- Width math: the exporter emits the group width as
  `group.width / (section.width - section horizontal padding) * 100%`, and
  each inner column as `column.width / (group.width - group horizontal padding) * 100%`.
  MJML requires percentage columns inside a group; you get that for free by
  setting exact pixel widths and letting the exporter divide. Example: group
  560 wide containing columns 280 + 280 exports 50%/50%.
- Columns inside a group keep their elements side by side on mobile.
- **A group may be NARROWER than the section content box**, and real libraries
  have them (a centred social row at 372 inside a 540 content box exports at
  68.9 percent). Its columns sum to the GROUP's width, never to the section
  content box; a verification that compares group columns against the section
  content width produces false failures on every centred cluster.
- **A group whose columns carry borders needs headroom.** Exported column
  percentages are computed from widths alone, so columns summing to exactly the
  group width plus 1px borders push the total past 100 percent and the last
  column wraps to a second row. Measured: 192 + 136 + 192 = 520 in a 520 group
  with two 1px divider borders wrapped its third column on desktop AND mobile,
  and every arithmetic check passed because a border is not a width. The fix,
  and a deliberate deviation from the group-is-HUG rule above: pin the group
  FIXED at its intended width and make the columns sum to LESS than it by at
  least the total border width (192 + 126 + 192 = 510 in the 520 group, 10px of
  headroom, percentages summing to 98.08). A HUG group always makes its columns
  sum to exactly 100 percent of itself, which leaves no room for a border, so a
  bordered group has to be pinned.
- **On mobile a group expands to the full viewport width** and its columns take
  their percentages OF THE VIEWPORT; the group's own width percentage is not
  honored below the breakpoint. A tight icon cluster therefore spreads across
  the full width on phones. That is documented exporter behavior, not a build
  error, and it is not reachable from the Figma side. If clustered mobile icons
  are a hard requirement, the only route is one combined image with a single
  href, which costs the per-icon links; say so in the batch report and let the
  designer choose.

#### 3.3.1 Pinned widths that carry text need slack

**Never pin a text-bearing column at the width Figma hugged to.** Pinning the
width is correct, and section 0.3 is right that the pixel IS the percentage.
What the pixel is NOT is a safe measurement. It was taken in the font Figma
rendered on canvas, the email declares a different one, and a pinned column
cannot grow. Text that fit by a hair on canvas wraps at send time, in a font the
canvas never showed you.

Three independent sources of drift stack up:

1. **Same family name, different binary.** Figma renders its own bundled Inter.
   The exporter writes `font-family: Inter, Arial` and also emits an `mj-font`
   link to `fonts.googleapis.com/css2?family=Inter`, so the email renders
   Google's Inter build, not Figma's. Measured on a real string: "Lorem Ipsum
   Dolor" at Inter Regular 16px fits inside a 143px content box on the Figma
   canvas and measures 143.39px in Chromium against Google's Inter. An overflow
   of 0.39px, 0.27 percent, is enough to wrap the row onto two lines.
2. **The webfont may not load at all.** Any client that blocks or fails the
   `mj-font` link falls back to the next entry in the stack, which is
   `fallBackFontName` and defaults to `Arial`. Measured drift on real strings
   against Figma's Inter runs as high as +11.5 percent, and it goes both ways:
   do not assume the fallback is always narrower or always wider than what you
   see.
3. **The whole family was substituted at foundations.** When the source face is
   not email-safe and the library swapped it (Theinhardt to the Arial clone
   Arimo, say), a column boundary measured in the SOURCE file was taken in a
   font the email will never use, and the metric-clone guarantee does not help:
   the clone matches ARIAL, not the face it replaced. Measured: a nav label
   that fit its 149px column in Theinhardt hugs at 146px in Arimo and wrapped
   to two lines at export, after passing every canvas check. Re-measure the
   hug width in the substituted face and feed THAT number to the formula
   below; never pin at a boundary measured in the source font.

So take the text node's natural hug width in Figma, then pin the column at:

```
column width = max( ceil(hugWidth * 1.12), hugWidth + 8 ) + the column's horizontal padding
```

The 12 percent covers the worst measured fallback drift **for Arial and
Helvetica**, which is what `fallBackFontName` resolves to unless someone changed
it. The `+ 8px` floor stops short strings ("Sale", "New", "Just In") from ending
up with one or two pixels of slack, which is no slack at all.

**Use 25 percent instead when the fallback is a wide face.** `fallBackFontName`
is a writable key, so a brand can set it to Verdana, Tahoma or Georgia. Those set
much wider than Arial at the same size: measured against Figma's rendering across
realistic label strings, Verdana reached +24.9 percent, Georgia +11.5 percent and
Tahoma +9.8 percent, so a 12 percent allowance is not enough to hold them. Read
the root's `fallBackFontName` before you pin anything, and if it names one of
those three, widen by 1.25 rather than 1.12. A brand webfont paired with a wide
fallback is a materially different risk from Inter paired with Arial, and should
not share one number.

Applying it: widen the FIXED columns only. Leave the group HUG and let Figma
recompute its width, and leave every FILL child alone, they cascade through the
layout engine on their own. Then re-derive the exported percentages by hand and
confirm the inner ones still sum to 100. Worked example from the fix that
produced this rule: a 66px badge column plus a 151px label column in a 217px
group became 74 + 169 in a 243px group, exporting 30.4527% + 69.5473%, which is
exactly 100.

**Failure signature, so you recognize it next time:** it looks right on the
Figma canvas and wraps in the plugin Preview, same machine, same session, same
minute. Nothing is mis-tagged, no width is "wrong" in Figma terms, and a diff of
the tree shows nothing at all. When a reviewer reports a line breaking that does
not break on canvas, suspect a pinned width first, and measure the string
against the **exported** font stack rather than trusting the canvas.

**Where else this bites.** Anywhere a FIXED width sits above text:

- Columns in a group (this section) and columns in a multi-column section
  (0.3 case 2). Group columns are the worse of the two, because they never stack
  on mobile, so the pinched width is what every reader gets.
- An `mj-button` pinned to FIXED (0.4) with a label inside it.

It does NOT apply to FILL columns or FILL buttons, which resolve against the
content box at render time and adapt. Do not pad those; the extra width would be
real design drift for no gain.

#### 3.3.2 Group columns shrink on mobile, and section 3.3.1 does not protect them

Section 3.3.1 protects a pinned column against font drift at the width you pinned
it. It does nothing about the other risk, which only exists for group columns: **a
group never stacks, so its columns shrink proportionally at every smaller
viewport.** The pixel you pinned is a percentage the moment the email is opened
on a phone.

Both risks are real, they are unrelated, and 3.3.1 only covers the first. A group
column that passed the 3.3.1 slack check with 12 or 25 percent headroom will still
break at 375 wide if the arithmetic below fails, because 3.3.1's percentage was
computed against the desktop pin, not against a shrunk phone width.

Before pinning any `mj-group` column, compute what it resolves to at phone width:

```
resolved = columnWidth / groupWidth * (mobileViewport - section horizontal padding at mobile)
```

At a 375px viewport with 20/20 mobile side padding, that denominator is 335. So a
137px column inside a 560px group resolves to `137 / 560 * 335 = 82px`.

Then require, per column:

- **Carrying text:** `resolved >= widthOf(longest unbreakable word) * 1.05`. The
  longest **word**, not the longest string: the string can wrap, a word cannot.
  Measure the word in the exported font (section 3.3.1 has the drift table); a
  word that fits by two pixels on canvas can be six pixels wide of the resolved
  column in Arial.
- **Carrying a fixed-aspect image:** `resolved >= image natural width`. Below
  that the image is compressed on one axis and the aspect ratio visibly breaks;
  no CSS renders it back proportionally inside a group column.

**When a column fails this, the group is the wrong container.** Three remedies,
in order of preference:

1. **Collapse the contents into one reflowing `mj-text` with per-range
   hyperlinks.** For a row of links this is the same construction section 6.1's
   note recommends for `mj-navbar`: one text node, `setRangeHyperlink` per label,
   labels separated by a normal space plus non-breaking spaces so the gap
   survives HTML whitespace collapsing while the line can break between labels
   but never inside one. Reflows cleanly, which pinned group columns cannot.
2. **Drop the group so the columns stack.** Mobile users get one item per row.
   Correct for card grids where stacking is the point; less good for a header
   nav where the intent is one strip of chrome.
3. **Hide the column below the breakpoint with
   `mobileStylesHideInMobileDevice`.** Reserved for decorative content the mobile
   view can lose: an icon beside a label where the label already carries the
   meaning.

Widening the column is not usually available, because the widths have to sum to
the content box. Moving pixels from a neighbour column shrinks that column
instead, and now that one may fail the check.

**Failure signature.** Words break character by character on a phone that read
fine on the Figma canvas and in the desktop preview. If you see `CHA / NGI / NG`,
`G / E / A / R`, `CLO / THIN / G`, `GI / F / T / S` in a mobile screenshot, the
group columns are shrinking below their longest words. That is this rule, not a
font issue and not a padding issue.

**Measured case.** A four-item nav pinned at 137 / 86 / 133 / 89 in a 560 group
rendered as `CHA NGI NG`, `G E A R`, `CLO THIN G`, `GI F T S` at 375px. The 86px
GEAR column resolved to `86 / 560 * 335 = 51px`, which cannot hold "GEAR" at 17px
in the exported font. Rebuilt as one reflowing `mj-text` with four
`setRangeHyperlink` ranges, it wraps to two clean lines at 375, and probing at
235, 210, 190 and 170px produced no mid-word break at any width.

**Also worth checking on an announcement bar or hero copy row**, not just navs:
any group whose contents include a word longer than a few characters against a
column that hugs its content. On the migration this rule came from, a second
module was caught the same way: an announcement bar whose text column resolved
to 190px carried copy that hugs at 191px. One pixel off, invisible on the canvas,
would have wrapped ugly on every phone. The arithmetic is cheap; run it.

### 3.4 mj-column

- Node: FRAME, child of `mj-section` or `mj-group`.
- Shared `name` = `mj-column`.
- Auto-layout: `layoutMode = 'VERTICAL'`, vertical HUG, never FIXED. A column
  is the frame most often left at a fixed height by mistake, and it is the one
  where Outlook clipping bites hardest, because every leaf in the email hangs
  off a column (section 0.1).
- Horizontal sizing, per section 0.3:
  - **Single column in its section: FILL.** It resolves to the section content
    box, which is the LIBRARY's content width once you have set the section's
    horizontal padding from it (section 0.3.1), and it exports `width: 100%`.
    FILL keeps tracking that content box if a padding value is later corrected,
    which is why a lone column takes FILL rather than a pixel. Never HUG, which
    collapses the column to its content, and never FIXED, which exports the same
    100 percent today and drifts silently the moment a padding changes (0.3).
  - **Two or more columns in one section, or any column inside an `mj-group`:
    FIXED (e.g. 280, 200).** This is load bearing. The exported percentage is
    derived from the pixel number, so unequal splits and group percentages only
    survive when every column is pinned. Start from the worker's `width` attrs
    for the RATIO between the columns, then re-derive the actual numbers so they
    sum to the library content width rather than to the worker's (0.3.1 has the
    worked example). When you are deriving a number from a Figma measurement,
    and the column contains text, add slack per section 3.3.1 before you pin it.
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

  **Exception, multi-column rows:** when a section holds two or more columns whose content
  heights differ, set `primaryAxisAlignItems = 'MIN'` (exports vertical-align: top) while
  keeping `counterAxisAlignItems` on the content's horizontal alignment. The two properties are
  independent exporter reads, so this does not disturb text-align. Top is the default for
  multi-column rows; matched axes remain the rule for single-column sections.
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

#### 3.4.0 Multi-column gutters: a section with more than one column needs one

Every rule above lets a multi-column section sum to the library content width
with zero gutter between columns: three 186.67 columns in a 560 content box add
to 560, and no attribute mapping catches that adjacent cards touch. The
content-width equation passes trivially. The visual result is a section whose
headlines from adjacent columns visually concatenate into one sentence, whose
card images abut the next card's edge, and whose buttons sit a pixel from a
neighbour. That is a gutter failure, not a typography problem, and the
arithmetic gate cannot see it.

**A section with more than one column and zero horizontal column padding is a
FAIL unless the source design has a measured zero gutter and the batch report
says so.** Record the source gutter as a distinct measurement (the audit's
Spacing system census already carries it as a role), express it in the built
module as horizontal padding on the `mj-column` frames rather than as Figma
`itemSpacing`, an absolute position, or a visual gap.

Section 3.4.1 (Two Column Swap) restates the same rule as "spacing on one side
of each boundary only, never both" for the image-beside-text case. This section
generalises it to every multi-column row: each internal column boundary carries
the source's measured gutter, on ONE side of the boundary, expressed as column
padding.

Worked example, three equal cards in a 560 content box with a 16px source
gutter:

```
card content = (560 - 32) / 3 = 176px
column box   = 186.67px, with 8px horizontal padding on each side
adjacent boundary  = 8 + 8 = 16px between adjacent card content
```

Do not infer card width by dividing content width by column count unless the
measured source gutter is zero. That inference is how the failure lands: an
agent computes `560 / 3 = 186.67`, builds three 186.67 columns with zero
padding, and the columns sum correctly to the content width while the built
module has no breathing room.

The batch verification for this rule is in the skill's Phase 3 step 5 checklist
under "Multi-column gutter present": list the horizontal padding on each column,
confirm at least one side of each internal boundary carries the source gutter,
and reject the module if not. Zero-padding multi-column layouts pass only with
an explicit batch-report note saying the source intentionally uses no gutter.

#### 3.4.1 THE TWO COLUMN SWAP: the standard rebuild for an overlapping or bleeding image

**The failure it replaces.** Source designs routinely place a photograph so it
overlaps or bleeds past the block it belongs to: a product shot entering from the
right behind body copy, an animal cropped off by the left edge of a cream band
with text beside it. In Figma that is z-order plus absolute position. Email has
neither, so it cannot be reproduced, and no attribute in this spec gets close.
**The standard remedy is to rebuild the block as a two column row: one
`mj-section`, two `mj-column`s, the image in one and the text in the other, in
the same left to right order the design implies.** The image stops at its column
edge instead of bleeding, and nothing overlaps. This is a settled decision rather
than a per-module judgment call, so do not re-argue it per module and do not go
hunting for a cleverer reproduction of the overlap.

**How to recognize it, because nothing in the source labels it.** Two tells,
either one of which is enough:

- **The photo's bounds extend past the bounds of the block it reads as part of.**
  It is wider or taller than the band, or its absolute x/y put part of it outside
  the frame that appears to contain it. Compare the image node's absolute box
  against the band's box; do not judge it from the screenshot, where the overflow
  is invisible by construction.
- **The photo is clipped by a sibling drawn over it rather than by a mask.** A
  rectangle of background color sits above it in z-order and hides one edge. The
  layer panel shows no mask and no crop, and the composite you see exists in no
  single node.

On an unstructured source neither tell is written down anywhere, and the
screenshot looks like an ordinary photo in a band, which is why recognizing this
is its own step rather than something you notice in passing.

**The construction.** One `mj-section`, two `mj-column` children, image column
and text column in source order.

- Both columns FIXED (0.3 case 2, 3.4), with their widths summing to the section
  content box: a 600 wide section carrying 20/20 padding takes columns summing to
  560. Unequal splits only survive because both numbers are pinned; the exporter
  derives the percentages from them.
- **Derive the widths in this order.** Pin the text column first, with the slack
  from 3.3.1, then give the image column the remainder, then size the image last.
  Worked: text hugs at 260 and pins to 292, so the image column is 268.
- **The image is a rendered crop of the source region (4.2.1), never the raw
  fill**, and it is cropped to its column rather than padded to fit, per 4.2.1's
  never-pad rule on aspect ratio. The `mj-image` rectangle is the image column's
  content width, and its height is the render's natural aspect at that width:
  continuing the example, a 780 x 660 render at 268 wide is 227 tall, and 227 is
  the number.
- Heights HUG throughout (0.1). Both alignment axes equal on the section and on
  each column (3.4, structure.md "Alignment: the trap").
- Spacing on one side of each boundary only (0.7). The gutter between the two
  columns is one column's horizontal padding, never both.
- **Not an `mj-group`.** A group exists to keep columns side by side on mobile
  (3.3), which is the opposite of what this pattern wants.

**Mobile.** Two columns stack, so the image lands above the text, which is a
normal email pattern and arguably better than a bleed that would have had to be
abandoned on a 390 wide screen anyway. Stacking follows column order, and column
order is the design's desktop order, not yours to choose: when the design reads
text then image on desktop but should read image then text on mobile, set
`reverseStack` = `'true'` on the section (3.2) rather than reordering the columns.

**Why this is the default, so nobody relitigates it.** It keeps the text LIVE:
the alternative, flattening the whole block to one editable image, gives up
selectable text, accessibility, and dark mode for the sake of an effect. It
degrades well, per the mobile note above. And the loss is small and nameable, the
overlap and nothing else, which is exactly what the concession field records.

**What this does to the verdict.** A block whose only obstacle is an overlap or
an edge bleed is **verdict A**, carrying
`A (concession: image bleed rebuilt as a two column row)`, and it is not a C.
Build it as live text like any other A, apply this substitute, and add nothing
further. C reads as a partial conversion, and this is not one.

**What stays verdict C.** Blocks that genuinely need splitting into live text
plus an editable image region: type set over a photographic collage where the
lettering is part of the artwork, or any treatment where copy and picture are one
composited whole with no boundary to cut on. The test: if you can name the
rectangle the image belongs in and the rectangle the text belongs in, it is this
pattern and it is an A. If you cannot, it is a C.

### 3.5 mj-column-inner (rarely needed)

Use ONLY when a column needs a second, inner background/border box distinct
from its own (card inside a colored column). Most card-in-column designs are
expressible without it: put the card fill, radius, and paddings directly on
the `mj-column` and the outer color on the section. Prefer that. The second
genuine case, measured: a FILLED card that needs a gutter beside it. A
column's fill covers its own padding, so the gutter cannot come from the
filled column's padding without the neighbouring cards touching. Build the
outer column fill-less with the gutter as its padding (271 wide with 22
`paddingRight`) and the inner column at FILL carrying the card's fill, radius,
and inner paddings (resolving to 249).

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
- Fill: an IMAGE fill, `scaleMode: 'FILL'`, from an image that is already in the
  target file. `figma.createImageAsync(src)` is NOT available to an external
  agent, so a worker `src` URL is not something you can turn into a fill
  directly, and section 4.2.1 has the route for anything coming from the
  customer's source file.
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
  (`nf`). So measure against the column content width you actually built, which
  is the library's (section 0.3.1) rather than the side margin the worker
  returned: an image meant to fill its column takes that number and stays fluid,
  a 134 logo does not. This is automatic; just get the px right.

### 4.2.1 Bringing an image across from the source file: RENDER the node, never the raw fill

An image in a source file is almost never the whole photograph the designer
started from. Two things routinely sit between the raw bytes and what you see on
the canvas, and neither one travels with the raw asset:

- **A crop transform.** An image fill with `scaleMode: 'CROP'` carries an
  `imageTransform` matrix: which part of the photograph is showing, and at what
  zoom. Export the raw fill and you get the full frame back with that transform
  discarded, including everything the designer cropped away. The symptom is dead
  space where the composition used to be tight: a subject that filled the band
  now floats small inside it or sits half out of view. Nothing about the
  rectangle's geometry is wrong, which is exactly why this gets misdiagnosed and
  reported as a spacing bug.
- **Clipping by overlapping siblings.** Unstructured sources clip by z-order and
  not by masks: a shape, a band of background, or another image sits on top and
  hides part of the picture. What you see is a composite of several nodes, and
  those pixels exist in none of them on its own. Only a render captures it.

So, for every image you bring across: **render the node as it appears and use the
render.** Never the raw fill, never the asset behind `fills[0].imageHash`. If the
audit's row for a module says its images are clipped by z-order rather than by
masks, or that they carry a crop, that is this rule and it is not optional.

The route, since `figma.createImageAsync` is unavailable to an agent:

1. `download_assets` on the NODE in the source file (`get_screenshot` on the
   node, or `node.exportAsync`, do the same job), at 2x, to a local PNG. Reading
   `fills[0].imageHash` and fetching that asset instead is the mistake, not the
   shortcut.
2. **Open the exported PNG before you upload it, and look at it.** Three failure
   modes each present as a layout bug rather than an asset bug, which is why they
   cost hours instead of minutes:
   1. **Baked-in white.** A node whose own background is white exports opaque,
      and dropped onto a colored band it reads as a white box. Symptom on
      Batch 4: a cart icon and a warranty diamond both rendered as white
      boxes on the blue and dark bands respectively, and the dry-bag product
      cutout rendered as a white block on the blue band. For line art, key the
      white to transparency and set the color explicitly; for a photographic
      cutout, flood-fill the surround from the border to the band color
      (preserves white highlights inside the product).
      **But before either: when the source node's own geometry defines the
      silhouette, rebuild that geometry as a mask instead of keying by color.**
      A `cornerRadius` at or above half the node's shorter side is a circle; an
      ELLIPSE node, a vector mask, or a clipping parent are the same case.
      Composite the render through that mask onto the band color. This is
      exact, needs no tolerance, and is the only approach that works when
      subject and background are within roughly 10 units per channel, which is
      the normal case for a white product on a cream ground. Measured: a
      border-connected flood fill at plus or minus 14/14/20 per channel
      converted 25.6 percent of a 909x909 render and still left a halo visible
      at 100 percent zoom, because background and subject rim were 11 units
      apart in one channel; a 4x supersampled elliptical mask from the node's
      own `cornerRadius: 369.4` gave a clean edge in one pass. Reach for color
      keying only when the silhouette is not recoverable from node geometry.
   2. **The neighbour's content.** When slicing out of a rendered parent frame
      (task #32's render-once-crop-locally technique), **check the crop's far
      edge against where the adjacent column starts**, not against the source
      node's declared width. A node can be wider than its visible content, and
      the difference will be somebody else's text. Symptom on batch 4: a
      T-shirt photo baked in 28px of the neighbouring column's text (`Lor`,
      `L`, `con`, and a button edge), and the geometry read correct at every
      level (columns at the right x, right widths, no overlapping siblings), so
      the layout got chased twice and the component rebuilt once before anyone
      thought to open the PNG.
   3. **A fused row that is not missing.** Section 4.2.2 already covers this.
      It is the same discipline: look at the pixels.
   A useful check on a sliced icon set is to composite each one onto its real
   band color and look at the result before uploading. It takes seconds and it is
   the difference between "the icons are broken" and "the icons are fine".
3. `upload_assets` to place that PNG onto the `mj-image` rectangle in the target
   file. The crop is baked into the pixels now, so the fill is a plain
   `scaleMode: 'FILL'` with an identity transform and there is no crop left to
   reproduce.
4. Verify against a screenshot of the SOURCE NODE, never against the source's
   raw asset.

**Aspect ratio: preserve the render's, never stretch to fit a chosen width.**
Measure the ratio on the rendered PNG and derive the height from the width you
picked: `height = round(targetWidth * renderH / renderW)`. A 995 x 550 render
placed at 600 wide is 332 tall, and 332 is not a number to round to something
tidier. If a height was decided earlier and it disagrees with the render, the
render wins and you re-derive the height. Forcing a render into the wrong box is
either a `scaleMode: 'FILL'` quietly cropping it a second time or a visibly
squashed photo.

**NEVER PAD AN ASSET TO FIT A CONTAINER.** An email image is declared with a
width and takes its height from the image. There is no container for it to fit
into: `mj-image` sets a width, the client scales the file, and the height that
appears is whatever the file's own aspect ratio produces. So the `mj-image`
rectangle has exactly one correct height, the one that matches the asset's
natural aspect, and the two ways of forcing a different one are both defects:

- **Padding the export.** Adding white, or any background, to the exported PNG so
  its ratio matches a rectangle you already have. The padding is now part of the
  asset. It uploads to S3, it renders in every client, and no later change to the
  rectangle can take it back out.
- **Stretching the asset.** Keeping the rectangle's ratio and letting the fill
  distort to cover it, or letting `scaleMode: 'FILL'` crop a second time. Either
  way what ships is no longer the photograph.

**The symptom is what makes this expensive: both read as a spacing bug, not an
image bug.** Baked-in padding looks exactly like dead space above or below the
subject, so it gets reported as "there is a gap over the headline" or "this band
has too much room at the top". Everyone then searches the auto layout paddings,
the frame heights, and the double-padding rule, all of which are correct, so the
search comes up empty while the real cause sits in the pixels of the asset, which
nobody is inspecting. Two separate defects on one observed build were this shape,
a dropped crop transform and a PNG padded with white to reach a component's
pinned ratio, and both were reported as spacing.

**The rule: size the container to the asset, never the asset to the container.**
Measure the render, choose the width deliberately, derive the height from the
render's ratio, and resize the rectangle to that height. When a height already on
the rectangle disagrees with the render, the rectangle is what changes. Nothing
is ever added to an asset or taken off one to make a number work.

**Corollary for design systems: a height that has to vary cannot live on the
component.** An image band component that pins its rectangle at one height serves
exactly one aspect ratio. Point it at a photograph of any other shape and whoever
builds the email has to pad the asset or squash it, which is to say the
component's own geometry is what produced the defect. So when a module is meant
to hold photographs of different shapes, the width belongs to the component and
**the height belongs to the instance**: build the master at the natural aspect of
one representative photo, and resize the `mj-image` rectangle on each instance to
that instance's own photo. Two instances of one component carrying different
heights is correct here, and nothing in the export cares. Note it on the module
so the next builder reads the master's height as a starting point rather than as
a constraint to honor.

Resizing that rectangle per instance runs straight into section 0.8: a `resize()`
on a node nested inside an instance reports success and changes nothing. Use the
pattern there, FILL the descendant chain and resize the INSTANCE, and read the
rectangle's dimensions back rather than trusting the call.

**Width is a decision, so make it deliberately and state it.** A source image
narrower than its canvas (995 in a 1089 wide design, so about 91 percent) is
inset by design, not full bleed. Either reproduce the inset as horizontal
padding on the `mj-image-Frame`, at email scale and snapped to the spacing scale
the foundations already use, or take it full bleed at the body width. Both are
defensible. Pick against the design system's own established patterns, and record
which you chose and why in the batch report so the next module makes the same
call. What this must never be is an accident of arithmetic.

### 4.2.2 Recovering assets from a combined raster

A source design will often carry a row of several small things as ONE image: a
strip of social icons, a row of payment badges, a set of app-store buttons, a
line of rating stars. The individual assets are in the file. They are fused. The
email needs them apart, because each icon is its own `mj-image` with its own
`href`, so the module cannot be finished from the strip as it stands.

**Slice the raster. Do not conclude the assets are missing.** "The icons are not
in the file" is the wrong finding and an expensive one: it turns a mechanical crop
into an ask the customer has to go and satisfy, and the module ships with empty
rectangles while everyone waits. The accurate finding is that the assets exist in
fused form and have to be cut out of a render.

The route:

1. **Render the strip large.** `download_assets` on the strip node at 3x or 4x. A
   plain screenshot is capped at the node's own pixel size, which on a small
   source strip leaves too few pixels per icon to crop from.
2. **Find the boundaries by inspecting the image, never by dividing the width
   into equal columns.** Glyph widths and the gaps between them differ, so equal
   columns cut into the wide icons and leave the narrow ones off-center. Profile
   the render instead: sum brightness, or alpha, per column, then read off the
   runs of ink separated by runs of background and take one cluster per icon.
   That also counts the icons for you, which is the check that catches a strip
   holding five when the structure you are filling expects six.
3. **Crop each cluster on a shared vertical band**, centered on that icon's own
   horizontal ink center, with the same padding on every crop. Icons in a row
   share a baseline and a scale in the source. Cropping each one tight to its own
   bounds throws that away, and once they are all placed at one size the wide
   ones come out small and the narrow ones large.
4. **Apply by name, on the master.** Name the crops in reading order, confirm the
   order visually before you apply anything, and match each crop to its rectangle
   by the rectangle's name rather than by child index. A row like this is
   identical in every email, so the fills belong on the COMPONENT rather than on
   one instance, where every existing instance inherits them.

**Resolution check, and state the answer either way.** Before slicing, divide the
render's width by the number of icons and compare that against the width they
will be placed at. A crop that arrives smaller than its `mj-image` width will be
visibly soft, and a strip drawn small in the source cannot be rescued by
rendering it larger, because those pixels were never there. When the raster is
too small to slice usefully, say so plainly and ask for the individual assets or a
vector source. Shipping blurry crops and calling the module done is the one
outcome that is not available, and neither is deciding this quietly: the report
says either "sliced at N px per icon for a 24px placement" or "the strip is too
low-resolution to slice, individual assets needed".

**The inverse rule: never CREATE a combined raster.** When assets are independently linked
or independently positioned in the source (brand logos, social icons, nav items), build one
`mj-image` per asset at its intended display dimensions and natural aspect ratio. Combining
them into one strip costs the per-item hrefs, softens every mark (an enlarged composite
shrunk responsively is resampled twice), and forecloses mobile recomposition, which is
exactly where logo rows change arrangement. This subsection exists for slicing strips a
SOURCE already fused; a build that fuses clean source assets manufactures that problem.

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
    Only when the design system pins a button width, and when you do, give the
    label slack per section 3.3.1: a pinned button cannot grow around a label
    that sets wider in the exported font than it did on the Figma canvas.
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
- `layoutMode = 'HORIZONTAL'`. Fills: `[]` for a plain gap; a single bound SOLID
  fill where the spacer IS a colored band, which exports as
  `container-background-color` and is the intended mechanism for that case. The
  two legitimate spacer reasons above (a colored band, a gap inside a bordered
  column) split exactly along this line.
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
JSON does not already specify. A gap the block above already pays for is not
yours to pay for again: section 0.7.

### 5.2 Colors

All colors are hex strings. One SOLID fill per background; TEXT fills for
text color. `transparent` or absent means `fills = []`. The exporter converts
`fills[0].color` back to hex and ignores opacity everywhere except the
text/button/spacer container checks, so never leave a "hidden" 0-opacity
fill lying around.

#### 5.2.1 Measuring a type size off a screenshot

When the worker returns a size and the ramp says a different one, or when two
plausible sizes disagree by 4 pixels, do not guess. Measure ink height off a
screenshot of the source and settle it arithmetically:

1. Crop tightly to one line of text in the source screenshot.
2. Threshold to isolate the glyphs from the background (any binarisation with
   the threshold set to catch the ink and reject the fill will do).
3. Measure the pixel height of the ink; call it `measuredCapHeight`.
4. Pick a reference line elsewhere in the source whose size you already know
   from the audit's ramp, in the same casing (all-caps for all-caps, mixed-case
   for mixed-case), and measure its ink height too; call these `knownSize` and
   `knownCapHeight`.
5. Solve:

   ```
   size = knownSize * (measuredCapHeight / knownCapHeight)
   ```

**Compare all-caps against all-caps and mixed-case against mixed-case.**
Ascenders and descenders change the cap-to-em ratio, so mixing casings drops a
constant into the arithmetic and the answer shifts by two or three px. Two
measured references from the batch 4 migration: an all-caps line at 28px
measured 20px of ink; a mixed-case line at 36px measured 33px.

**Round the result onto the audit's ramp, never to the nearest round number.**
The point of measuring is to choose between ramp steps, not to invent one. A
computed 39.2 that rounds to 40 introduces a 40 step the audit never had; the
same 39.2 rounded onto the ramp lands on either 36 or 44 depending on where the
next step is, and one of the two is correct. A step the audit is missing is
task #45's foundations decision, not this step's discovery.

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
  column (which resolves to 560) exports `width: 100%`. A lone column is FILL,
  never a pinned pixel, because FILL keeps tracking
  the content box (section 0.3). Set the section's horizontal px from the
  library's content width, per the last bullet in this list, so that content box
  is the same in every module.
- Multi column: widths export as percentages of the section content box.
  280 + 280 in a 560 content box gives 50% + 50%. The worker may bake gutters
  as column paddings (e.g. `padding-right: 10px` on the left column); keep
  those as paddings, do NOT convert them to itemSpacing.
- Inside `mj-group`: same math against the group's content box; MJML gets the
  required percentage widths automatically.
- **The content box itself is a library decision, not a per-module one.** The
  number the single column resolves to, and the number a multi-column split sums
  to, is the one content width foundations settled for the whole library, not the
  side margin the worker happened to return for this screenshot (section 0.3.1).
  Reproduce the worker's paddings everywhere else; this is the one padding you
  override; full-bleed image bands and card insets are the two sanctioned exceptions (0.3.1).

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

The root is the one node whose naming depends on which shape you are building
(section 2):

- **An EMAIL TEMPLATE root gets no tag at all.** It is identified by
  `nodeType = mainFrame`, and its layer name is the email name. Do not put a tag
  in it and do not write a `name` key on it.
- **A DESIGN-SYSTEM MODULE root is tagged `mj-wrapper`** like any other wrapper,
  and this is the one node where the friendly-name rule inverts: its layer name
  is not the display string `Wrapper (Groups rows and sets the background for
  this section )` but **the module name**, because that name becomes the saved
  component name and its storage path.

Either way the root layer name is the thing a human sees in the plugin's picker,
so keep it clean and never put a tag in it.

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

**Finding these nodes again later: `query()` does not match a layer name that
contains a space.** Measured: `query('FRAME[name*=Text Block]')` returns nothing
against frames genuinely named `Text Block`. Every display name in the table above
contains a space, so `query()` is unusable for finding nodes by the names this spec
prescribes, and the spec is what created the trap. Traverse `children`, or use
`findAllWithCriteria` and filter on `node.name` yourself.

You may append a short human qualifier when a module holds several of the same
block and the distinction helps a reviewer ("Text Block / eyebrow"). Avoid the
comma form there, since `Label, (mjml:mj-text)` is the parsed tag syntax and a
comma reads as the start of one. Never prepend anything that looks like a tag,
and never let the qualifier replace the display name.

**The tags below the transcription set.** `mj-hero`, `mj-social`, `mj-navbar`,
`mj-table`, and their children are real plugin node types, which is why they
appear in the table above and in the skill's visual-pattern mapping. This spec's
detailed attribute mapping covers the core set only (sections 3 and 4). When the
worker returns one of the others, compose the row from mapped primitives instead
(the visual-pattern mapping in the skill's transcription step), and reserve
`mj-hero` for the case where a design genuinely needs live text over a
full-bleed background image.

**A band with decorative art needs neither `mj-hero` nor a baked bitmap.**
`mj-section` has no background-image mapping in this spec, so the tempting
"bake band and art into one section background image" route trades live text
for a picture of text. Build it as a full-bleed `mj-group` instead: the copy
column carries the band fill and any rounded edge, and a narrow decorative
column carries the art, marked `mobileStylesHideInMobileDevice` so it drops
cleanly below the breakpoint. Measured build: a 535px copy column plus a 65px
decoration column (one of 0.3.1's sanctioned full-bleed exceptions; the copy
inside still starts at the content margin) rendered exactly as designed on
desktop and cleanly absent on mobile with no gap, using only mapped
primitives.

`mj-column` has no background-image mapping either, so art BEHIND live text
inside a card has no supported construction. When the art is an overlapping
glyph or ornament, place it as an in-flow `mj-image` inside the card above the
content (the loss is the overhang only, the shape of the bleed concession) and
bind its visibility to a BOOLEAN when the source itself ships variants without
it. Do not bake the card into an image to keep the overlap: images are not
erased by dark mode, so a baked card keeps its light colors under forced-white
text.

**Specifically for `mj-navbar`, do not invent a mapping. Rebuild as one
`mj-text` with per-label hyperlinks.** The worker returns `mj-navbar` for any
row of links, and if there is no `mj-navbar` attribute mapping here (and there
is not), an agent that leaves it as `mj-navbar` in the tree gets a node the
plugin rejects and an agent that improvises a mapping produces a group whose
columns fail section 3.3.2 at phone width. The construction that reflows and
survives:

- One `mj-text` node whose characters carry every label in one string.
- One `setRangeHyperlink` per label pointing at that label's href.
- Between labels, a normal space plus one or more non-breaking spaces (` `)
  so the visible gap survives HTML whitespace collapsing while the line can
  still break between labels but never inside one.
- Type styling from the audit's Nav Link ramp entry, aligned per the design
  (centre for a nav strip, left for an inline row).

Two independent reasons this shape wins over the alternatives on any nav past
three items: it reflows, which a group of pinned columns cannot (section 3.3.2
has the arithmetic), and it satisfies audit constraints of the form "split the
single text run into N separately linked items" without a per-item column.
Task #42's four-item nav shipped this way after `CHA / NGI / NG`, `G / E / A / R`
failed the group build twice.

---

## 7. Components: when a node is a COMPONENT instead of a FRAME

**Make it a COMPONENT when it is meant to be reused**: a converted design-system
module (always), a section you built to fill a gap and intend to save into the
library, a foundations button or badge that other modules instance. Keep it a
FRAME when it is a one-off campaign email that nobody will instance.

This is safe. Confirmed against the plugin source:

- **Export accepts a COMPONENT everywhere it accepts a FRAME.** The export
  gate whitelists `FRAME`, `INSTANCE`, `COMPONENT` at the root and at every
  container level, and the email-root branch is `nodeType === 'mainFrame'` plus
  that whitelist. The HTML export path has no node-type check on the root at all.
- **Add New Template accepts a COMPONENT.** The whole-email branch tests plugin
  data only (`nodeType === 'mainFrame'`), never `node.type`.
- **The plugin already does this.** Every `mj-wrapper` the plugin renders is
  created as a COMPONENT, not a FRAME (`UiParser.ts:1519-1522`). Purple
  components inside a plugin-built email are normal. Do not "fix" them into
  frames.
- **Instances work.** `INSTANCE` is in the same whitelist and an instance
  surfaces the main component's plugin data, so a customer who places an
  instance of a componentized module still exports correctly.

The calls, either at creation or by promoting a finished frame. **Which plugin
data you write depends entirely on section 2**, and the two sets are mutually
exclusive:

```js
// build it as a component from the start...
const root = figma.createComponent()          // instead of figma.createFrame()
// ...or promote the frame you already finished:
const root = figma.createComponentFromNode(frame)

// A DESIGN-SYSTEM MODULE (section 2.2): the component IS the mj-wrapper.
root.name = 'Hero, text led'                                // the saved component name
root.setSharedPluginData('emaillove', 'name', 'mj-wrapper')
// no nodeType key. Writing 'mainFrame' here breaks the module upload (2.3).

// A REUSABLE WHOLE EMAIL (section 2.1): the component is the untagged root.
root.name = 'Welcome email'
root.setSharedPluginData('emaillove', 'nodeType', 'mainFrame')
// plus the eight theme keys. No 'name' key on this node.
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
3. **Properties go on the component that owns the node** (section 8), which is
   the MODULE, never the email root. Because every `mj-wrapper` is itself a
   COMPONENT, an email root cannot bind a property to anything inside its wrapper
   components: Figma rejects `componentPropertyReferences` on an instance
   sublayer. That is the structural reason properties belong on the wrapper-level
   module component (section 2.2) and one more reason a module must not be built
   as a `mainFrame` wrapping a wrapper: the properties would have nowhere valid
   to live. Bind at the level that directly owns the node.
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
  primaryButton.id,           // node id: a local component's `key` is empty
  {
    preferredValues: [
      { type: 'COMPONENT', key: primaryButton.id },
      { type: 'COMPONENT', key: inverseButton.id },
      { type: 'COMPONENT', key: textLink.id },
    ],
  },
)
buttonInstance.componentPropertyReferences = { mainComponent: style }
```

In a freshly converted library every component is local and unpublished, so its
`key` is an **empty string** and `type: 'LOCAL_COMPONENT'` is rejected outright.
Use the node id and `type: 'COMPONENT'`, which is what runs (measured: the
key-based form failed twice before the error was read). Switch to published keys
only once the library has been published.

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

1. **The root matches the shape you meant to build** (section 2), and only one
   of these two lines is true of it:
   - **EMAIL TEMPLATE:** shared `nodeType = mainFrame`, ALL theme color keys
     plus `lightThemeBackgroundColor` and `fallBackFontName`, no `name` key, and
     its direct children are `mj-wrapper` components.
   - **DESIGN-SYSTEM MODULE:** shared `name = mj-wrapper`, **no `nodeType` key
     anywhere in the tree**, no theme keys unless a designer asked for a
     dark-mode treatment on this block, layer name is the module name, and its
     direct children are `mj-section` frames. Read `nodeType` back off the root
     and confirm it is empty; a leftover `mainFrame` uploads as a whole email.
2. Every FRAME/RECT/LINE/TEXT you created has shared `name` set to exactly
   one known tag; zero untagged frames anywhere in the tree, except a deliberate
   editable-image region for a verdict B or C module (ground rule 3), which your
   report names. No node is relying on the layer-name fallback.
3. Every node's layer name is the display name for its tag (section 6.1), and
   no friendly string was written into the plugin data `name` key. The one
   exception is a module root, whose layer name is the module name (section 6).
4. Every leaf is a complete pair; every `mj-button` has a direct TEXT child;
   no empty wrapper frames.
5. `primaryAxisAlignItems === counterAxisAlignItems` on every auto-layout
   frame, WITH the documented multi-column exception: a section whose columns
   have unequal content heights keeps `primaryAxisAlignItems = 'MIN'`
   (vertical-align: top) alongside the content's horizontal alignment, per the
   alignment rules above. Record each such top-align exception as intentional;
   any OTHER axis mismatch fails this check.
6. All nodes `visible = true` (except a region you deliberately left off via a
   BOOLEAN default); `itemSpacing = 0` everywhere; no stray fills.
7. **Every frame in the tree has `layoutSizingVertical === 'HUG'`.** Walk the
   whole tree and check, root included. The only FIXED height allowed is on an
   `mj-spacer`; the only hard heights are on the `mj-image` rectangle and the
   `mj-divider` line, neither of which is a frame. Anything else pinned is an
   Outlook clip waiting to happen (section 0.1).
8. **Every FIXED width is one of the four load-bearing cases** (root, columns
   in a multi-column section, columns in a group, the image rectangle). Lone
   columns are FILL and groups are HUG (section 0.3). A button is not one of the
   four: its width is 0.4's mobile-behavior decision, so HUG, FILL, and a
   deliberately pinned FIXED are all valid there, and item 10 is where it is
   checked.
9. **Every pinned-width column that contains text has slack, and every pinned
   string was sanity-checked against the exported font, not the canvas font**
   (section 3.3.1). Columns in a group above all, since those never stack on
   mobile. `max(ceil(hug * 1.12), hug + 8)` plus horizontal padding, or 1.25 in
   place of 1.12 where the root's `fallBackFontName` is Verdana, Tahoma, or
   Georgia (section 3.3.1), and the
   inner group percentages still sum to 100. A label that fits exactly on the
   Figma canvas is a wrap in the plugin Preview, because the canvas font and the
   font the email loads are different binaries. FILL columns are exempt.
10. **Every button's width sizing was a decision.** HUG unless the design calls
    for a full-width CTA, in which case FILL, which is also what makes it full
    width on mobile (section 0.4). Buttons are at least 44px tall, from
    `inner-padding` rather than a set height.
11. All vertical spacing is padding: no gaps produced by a taller frame, by
    `itemSpacing`, or by a manually positioned node (which exports as nothing).
12. Root width equals the mj-body width; vertical section paddings equal the
    worker attrs. All of those numbers are at email scale (section 0.6), which on
    an authoritative or partial source means the audit's confirmed factor was
    applied and on a reference-only source means the email standards were built to
    and no factor exists: either way the root is 600 or 640, and body copy is a
    size email actually uses.
    **And the text-bearing column resolves to the library's ONE content width**,
    not to the side margin the worker returned for this screenshot (section
    0.3.1): read the resolved width back off the column, compare it to the
    foundations number, and check that a multi-column split still sums to it.
    Full-bleed image bands and card insets are the two sanctioned exceptions (0.3.1). That is the
    check you cannot do by looking at the module, only by comparing it to the
    library.
13. If it is a module: the root is a COMPONENT tagged `mj-wrapper`, a direct
    child of its category page, not inside a COMPONENT_SET or a Figma SECTION,
    with no stray instances of it left on the page, and there is no second
    `mj-wrapper` nested inside it.
14. Every component property you added was re-read back off the node to confirm
    the binding landed, and each one has a reason you can state in the report.
15. No em dashes in any layer name, plugin data value, or text characters.
16. Compare a fresh screenshot of the frame against the source screenshot you
    converted from, for spacing, alignment, and color parity. Small color and
    font-metric differences are acceptable; missing content, zero-height
    sections, clipped text, and alignment flips are not.
17. **No gap is paid for twice.** For every pair of stacked siblings, exactly one
    of them carries the padding that separates them, and it is the one above
    (section 0.7). Any frame whose height exceeds its content by exactly a
    padding you wrote is this bug.
18. **Every image is a render of its source node, not a raw fill** (section
    4.2.1), so any crop or z-order clipping is baked into the pixels. Each
    rectangle's height is the render's aspect ratio at the width you chose, and
    the width itself was a recorded decision (full bleed or the source's inset),
    not an accident. **No asset was padded or stretched to fit a rectangle**: the
    rectangle was sized to the asset, per instance where one component holds
    photos of different shapes. Look at the edges of each PNG you exported, since
    baked-in white reads on the canvas as a spacing bug nobody can find in the
    auto layout. **Every per-instance resize was read back off the node**, because
    a resize aimed inside an instance fails silently and reports success (section
    0.8); an unchanged dimension is a failed write, not a harmless one.
19. **Every overlap or edge bleed in the source became a two column row**
    (section 3.4.1), never an improvised container and never a flattened image.
    Per swap: both columns FIXED with their widths summing to the section content
    box, the text column pinned with section 3.3.1 slack, the
    image column the remainder, the `mj-image` height the render's natural aspect
    at the image column's content width, no `mj-group`, and the gutter paid by
    one column only. Your report names the swap and states that the overlap is
    the whole of what was lost.
20. **No `mj-image` rectangle was left without an image fill because its asset
    looked missing** (section 4.2.2). Where the source carried a row of icons or
    badges as one raster, it was sliced out of a high-multiple render, with the
    boundaries found by inspecting the image rather than by equal columns, the
    crops applied to the master by rectangle name, and the per-icon resolution
    stated. If it genuinely could not be sliced, the report says so and names the
    ask.
