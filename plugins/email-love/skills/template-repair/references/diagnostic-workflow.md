# Diagnostic workflow

Use this order so the visible symptom does not dictate an unmeasured structural change.

## 1. Establish the evidence surface

Capture each available surface independently:

1. Figma canvas screenshot.
2. Email Love plugin Preview.
3. Production HTML from `emaillove_export_figma` with `operationType: "preview"`.
4. Desktop and mobile renders from `emaillove_preview_email`.
5. Supplied exported HTML, ESP result, or inbox screenshot.

Write which surface first shows the failure. A canvas-only problem is not automatically an export
problem, and a clean canvas does not clear the exporter.

## 2. Classify the target before inspecting details

- **Email template:** root has `nodeType = mainFrame`; direct children are `mj-wrapper` nodes or
  instances.
- **Reusable module:** root is a COMPONENT tagged `mj-wrapper`; no `mainFrame` exists in its tree.
- **Library instance:** target is an INSTANCE whose main component carries valid Email Love tags.
- **Not Email Love:** no valid root or wrapper evidence. Route out of this skill.

Do not add a `mainFrame` marker to a reusable module or an `mj-wrapper` tag to an email root. That
changes the product shape rather than repairing it.

## 3. Walk from the root to the symptom

Record the full ancestor chain and check:

- shared `emaillove` tag or root marker;
- node type and direct-child relationship;
- visibility;
- auto-layout direction, sizing, padding, alignment, and `itemSpacing`;
- fills, strokes, and radii that the exporter interprets;
- component or instance boundary;
- mobile shared-plugin-data keys;
- href, alt text, raw token, and component-property bindings where relevant.

An unrecognized helper frame higher in the chain can flatten every correctly tagged leaf beneath
it. Always inspect ancestors before changing the leaf.

## 4. Compare against a known-good peer

Prefer evidence from the same file and library:

1. The main component behind the failing instance.
2. Another intact instance of that component.
3. A recent exported email using the same module.
4. The authoritative Email Love render contract.

Do not copy private plugin data assumptions from a peer. External tools cannot read private plugin
data, and an existing private value can override the shared value you write.

## 5. State the hypothesis before writing

Use this compact record:

```text
Symptom:
First failing surface:
Failing node and ancestor:
Measured mismatch:
Hypothesized mechanism:
One proposed change:
Expected desktop result:
Expected mobile result:
```

If the proposed change has no measurable expected result, it is not ready to apply.

## 6. Preserve repair integrity

- Make one change, read it back, then render.
- Treat an unchanged read-back as a failed write.
- Treat a clean read-back with a bad render as a disproven hypothesis.
- Revert disproven changes on the working copy.
- Compare text and image counts before and after a structural repair.
- Compare component-property counts and re-read every binding.
- Stop after two failed local patches on the same section and reconstruct that section from its
  authoritative source.
