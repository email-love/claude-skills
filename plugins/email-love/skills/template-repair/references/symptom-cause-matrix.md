# Symptom and cause matrix

Use this as a starting hypothesis list, never as permission to skip measurement.

| Symptom | Inspect first | Common mechanism | Safe repair direction |
| --- | --- | --- | --- |
| Plugin says the selection is not a valid template | Selected root and shared `nodeType` | Wrong selection, missing `mainFrame`, nested root, or module selected as an email | Select the real root; restore the email root contract only when evidence shows it was lost |
| A module uploads as a whole email | Module root | `mainFrame` incorrectly present on an `mj-wrapper` component | Remove the marker from the module root after confirming its intended shape |
| Live text or a whole section exports as an image | Ancestor chain and shared tag names | Untagged or unknown helper frame triggers exporter flattening | Replace the unknown frame with intact structure or transcribe it from the render contract |
| Text clips in Outlook or after copy changes | Every ancestor frame's vertical sizing | Fixed height above text, wrong line height, or instance geometry write did not land | Restore HUG height; use the documented instance-resize pattern and read it back |
| Gap is roughly double the design | Adjacent siblings' padding | Both blocks pay for one gap | Give the gap one owner, normally the preceding block's bottom padding |
| Canvas spacing disappears in export | Auto layout and `itemSpacing` | Manual positioning or nonzero `itemSpacing` is not portable | Express the measured gap as padding on one recognized node |
| Columns stack when they should stay together | Section children and mobile render | Loose columns used for a lockup, or untrusted `stackColumns` behavior | Use an intact `mj-group` structure and verify the production mobile render |
| Columns stay together when they should stack | Section children | `mj-group` used for ordinary content columns | Restore loose columns from authoritative structure |
| Mobile header or footer order is wrong | Desktop and mobile source composition | Mobile needs recomposition, not stacking | Use paired sections with the two observed mobile visibility keys |
| Button is an image, unclickable, or the wrong mobile width | Full three-node button chain | Missing direct TEXT child, wrong tag, href on the wrapper, or wrong sizing mode | Restore the complete pair, put href on `mj-button`, and choose HUG/FILL from intended mobile behavior |
| Image is missing, stretched, soft, or loses its link | Image pair and rendered asset | Empty wrapper, wrong aspect ratio, raw fill used instead of rendered crop, combined raster, or href on wrapper | Restore the pair, natural aspect, one asset per link, and metadata on the rectangle |
| Footer is absent from Preview or export fails | `mj-raw` block and first child | Raw content is intentionally hidden in Preview, or raw frame has no text child | Distinguish Preview behavior from failure; restore exactly one raw text child when missing |
| Dark mode colors are wrong | Root theme keys and per-node overrides | Empty root keys, light values used as dark values, or deliberate overrides cleared | Restore audited root values; preserve existing node overrides |
| Component controls disappeared | Main component property definitions and bindings | Structural repair dropped `componentPropertyReferences` | Restore bindings from the pre-repair record and confirm property counts |
| Link change appears to succeed but export keeps the old URL | Plugin panel and shared/private data precedence | Existing private plugin data overrides shared data | Tell the user to change the value in the Email Love plugin control |
| Figma looks right but Preview is wrong | Pinned widths, exported font, and mobile render | Canvas and exported font metrics differ, or shared mobile key is ignored | Measure the production render, add documented width slack, or choose authoritative recomposition |
| A card has a notch, crescent, or stepped seam between rows | Bounds, insets, fills, strokes, and all four radii on both adjoining rows | Rows intended as one continuous surface have different resolved outer bounds or independent corner radii | Align the rows' resolved outer bounds and keep radii on the outer perimeter only; verify the seam in BOTH production desktop and mobile renders before promising it is gone (the full continuous-surface contract is forward-test-gated, not yet an exporter-proven rule) |

When more than one row fits, inspect the earliest shared ancestor. Several leaf symptoms often come
from one unrecognized or incorrectly sized container.
