# Snapshot validation rules

## Contents

- How to apply the rules
- Batch rules
- Module rules: source and structure
- Module rules: census and inventories
- Image rules
- Group rules and the mobile inner-box calculation
- Property rules
- Reporting the result
- Icon and social asset perimeter check

Apply these rules to the audit snapshot described in [snapshot-schema.md](snapshot-schema.md).
You are the validator: read the snapshot, work through every rule below in order, and record
each failure. Nothing here is run as a program.

## How to apply the rules

- **Fail closed.** A value that is missing, the wrong type, or not a finite number is an
  error. Never substitute zero, never assume a default, and never skip a rule because the
  field it needs is absent.
- **A measurement** means a JSON number that is finite and not a boolean. Unless a rule says
  otherwise it must be at least 0. A string such as `"unknown"`, `null`, or a missing field is
  `UNKNOWN_MEASUREMENT`. A negative number is `MEASUREMENT_NEGATIVE`. Either one also stops
  any calculation that needed the value.
- **Record every failure** as severity, code, location, and one sentence. Location is the JSON
  path, with the module name in brackets, for example
  `modules[0] (Feature row).groups[0].columns[1]@320px`.
- **Show the arithmetic** for every aspect-ratio, width-sum, and mobile inner-box check. Do
  not round before comparing.
- Do not stop at the first failure. Report all of them.

## Batch rules

| Code | Fails when |
|---|---|
| `BATCH_MISSING` | `batch` is not an object. |
| `MODULES_MISSING` | `modules` is not an array. |
| `PHASE_INVALID` | `batch.phase` is not `proof` or `normal`. |
| `MODULES_EMPTY` | The phase is valid and `modules` is empty. An empty list is absent evidence. |
| `PROOF_TOO_LARGE` | Phase is `proof` and there are more than four modules. |
| `PROOF_NOT_ACCEPTED` | Phase is `normal` and `batch.proofBatchAccepted` is not exactly `true`. |
| `LIST_TYPE_INVALID` | Phase is `proof` and `riskClassesPresent` or `proofRisksCovered` is not an array of strings. |
| `PROOF_RISK_INVALID` | Either list holds a value other than `photo-crop`, `grouped-icon-text`, `multi-column-properties`, `footer-social`. |
| `PROOF_RISK_UNCOVERED` | A class in `riskClassesPresent` is absent from `proofRisksCovered`. |
| `VIEWPORTS_INVALID` | `batch.mobileViewports` is not a non-empty array of positive numbers. Skip the per-viewport group checks if so. |
| `STATUS_INVALID` | `batch.statusClaim` is not one of the four completion states in the skill. |
| `EXPORT_STATUS_INVALID` | `batch.exporter.desktop` or `batch.exporter.mobile` is not `pass`, `fail`, or `deferred`. |
| `COMPLETE_WITHOUT_EXPORT` | The status is `complete` and desktop or mobile is not `pass`. |
| `FAILED_EXPORT_NOT_REJECTED` | Desktop or mobile is `fail` and the status is not `batch rejected, repair required`. |

Warning: `STALE_DEFERRED_STATUS` when the status is
`canvas and structure ready, exporter verification deferred` but desktop and mobile both pass.

## Module rules: source and structure

Check every entry in `modules`. An entry that is not an object is `MODULE_INVALID`.

| Code | Fails when |
|---|---|
| `SOURCE_MISSING` | `sourceRef` is empty or missing. |
| `PARITY_MISSING` | `sourceParity` is not an object. |
| `PARITY_FAILED` | Any of `content`, `order`, `crop`, `type`, `color`, `spacing`, `desktop`, `mobileIntent` is not exactly `true`. One failure per key. |
| `STRUCTURE_MISSING` | `structure` is not an object. Continue with the remaining rules as if it were empty, so each missing count fails too. |
| `ARTIFACT_KIND_INVALID` | `artifactKind` is present and is not `module` or `email`. When absent it is `module`. |

For `artifactKind` `module`:

| Code | Fails when |
|---|---|
| `MODULE_ROOT_INVALID` | `structure.rootTag` is not `mj-wrapper`, or `structure.nodeType` is anything other than empty or absent. |
| `MODULE_NOT_PAGE_CHILD` | `structure.directPageChild` is not exactly `true`. |

For `artifactKind` `email`:

| Code | Fails when |
|---|---|
| `EMAIL_ROOT_INVALID` | `structure.rootTag` is not empty, or `structure.nodeType` is not `mainFrame`. |
| `EMAIL_THEME_KEYS` | `structure.themeKeyCount` (a measurement) is below 9. |
| `EMAIL_CHILDREN_INVALID` | `structure.directChildrenAllWrappers` is not exactly `true`. |

Counts that must each be a measurement and equal 0:

| Field | Code when not 0 |
|---|---|
| `structure.untaggedFrameCount` | `UNTAGGED_FRAMES` |
| `structure.unknownTagCount` | `UNKNOWN_TAGS` |
| `structure.incompleteLeafPairCount` | `INCOMPLETE_LEAVES` |
| `structure.unintendedFixedHeightCount` | `FIXED_HEIGHTS` |

Unequal auto-layout axes:

- `structure.unequalAxisCount` is a required measurement.
- `structure.axisExceptions`, when present, must be an array (`AXIS_EXCEPTIONS_INVALID`
  otherwise). Each entry must be an object with a non-empty `node` and a `reason` of
  `top-aligned-multi-column`, the only documented reason today. Any other entry is
  `AXIS_EXCEPTION_INVALID` and does not count.
- `UNEQUAL_AXES` when `unequalAxisCount` is greater than the number of valid exceptions.

## Module rules: census and inventories

- `CENSUS_MISSING` when `census` is not an object.
- For each of `images`, `groups`, `properties`:
  - `INVENTORY_MISSING` when the array is absent or not an array. The array is required even
    when it was audited empty.
  - `census.<field>` is a required measurement.
  - `CENSUS_MISMATCH` when the census count differs from the array's length.

## Image rules

Check every entry in `images`. An entry that is not an object is `IMAGE_INVALID`.

| Code | Fails when |
|---|---|
| `IMAGE_FILL_INVALID` | `fillType` is not `IMAGE`. |
| `IMAGE_HASH_MISSING` | `imageHash` is empty or missing. |
| `ALT_TEXT_MISSING` | `altText` is empty or missing, unless `meaningful` is explicitly `false`. |

`rectWidth`, `rectHeight`, `assetWidth`, and `assetHeight` are required measurements. If any
is missing, stop the geometry checks for that image (the missing value is already an error).
Otherwise:

- `IMAGE_GEOMETRY_INVALID` when any of the four is 0.
- Compute `rectRatio = rectWidth / rectHeight` and `assetRatio = assetWidth / assetHeight`,
  then `drift = |rectRatio - assetRatio| / assetRatio`.
- `IMAGE_ASPECT_MISMATCH` when `drift` is greater than 0.02 and `cropApproved` is not `true`.
- `ICON_NOT_SQUARE` when `role` is `icon` or `social`, `nonSquareApproved` is not `true`, and
  `|rectRatio - 1|` is greater than 0.02.

## Group rules and the mobile inner-box calculation

Check every entry in `groups`. An entry that is not an object is `GROUP_INVALID`.

- `GROUP_GEOMETRY_INVALID` when `width` is not a positive measurement, or `columns` is not an
  array of at least two entries. Skip the rest of this group.
- Each column must be an object (`COLUMN_INVALID` otherwise) with a `width` measurement.
- **Headroom.** When `borderHeadroom` is present it is a measurement. If it is greater than 0
  and `headroomReason` is empty, that is `HEADROOM_UNDOCUMENTED`. When absent, headroom is 0.
- **Width sum.** If every column width was readable: `GROUP_WIDTH_SUM` when
  `|sum of column widths + headroom - group width|` is greater than 0.5.
- `mobileSectionPaddingLeft` and `mobileSectionPaddingRight` are required measurements. If
  either is missing, skip the per-viewport checks for this group.

Then, for every viewport in `batch.mobileViewports` and every column:

1. `mobileContent = viewport - mobileSectionPaddingLeft - mobileSectionPaddingRight`.
   `MOBILE_CONTENT_INVALID` when this is 0 or less; skip this viewport.
2. The column's `width`, `paddingLeft`, and `paddingRight` are required measurements.
3. `resolved = column width / group width * mobileContent`.
4. `inner = resolved - paddingLeft - paddingRight`.
   `MOBILE_INNER_INVALID` when `inner` is 0 or less.
5. Compare `inner` with what the column's content needs:
   - `content.kind` is `image`: `content.naturalWidth` must be a positive measurement
     (`IMAGE_NATURAL_WIDTH_MISSING` otherwise). `MOBILE_IMAGE_TOO_NARROW` when
     `inner + 0.01` is less than `naturalWidth`.
   - `content.kind` is `text`: `content.longestUnbreakablePx` must be a positive measurement
     (`TEXT_WIDTH_MISSING` otherwise). `MOBILE_TEXT_TOO_NARROW` when `inner + 0.01` is less
     than `longestUnbreakablePx`.
   - Any other kind: warning `GROUP_CONTENT_UNMEASURED`. Disposition it manually.

Worked example, from the schema's example snapshot at a 320px viewport: section padding
40 + 40 leaves `mobileContent = 240`. The icon column is 96 of 520, so
`resolved = 96 / 520 * 240 = 44.31`, and `inner = 44.31 - 0 - 10 = 34.31`, which clears the
icon's `naturalWidth` of 32. The text column is 424 of 520, so `resolved = 195.69` and
`inner = 195.69 - 16 - 0 = 179.69`, which clears `longestUnbreakablePx` of 90. Narrow the icon
column to 72 (and widen the text column to 448) and the icon's inner width becomes
`72 / 520 * 240 - 10 = 23.23`, below 32: `MOBILE_IMAGE_TOO_NARROW`.

## Property rules

Check every entry in `properties`. An entry that is not an object is `PROPERTY_INVALID`.

| Code | Fails when |
|---|---|
| `PROPERTY_TYPE_INVALID` | `type` is not `TEXT`, `BOOLEAN`, `INSTANCE_SWAP`, or `VARIANT`. |
| `PROPERTY_EVIDENCE_MISSING` | `evidence` is empty or missing. |
| `PROPERTY_UNBOUND` | `bindingCount` (a required measurement) is below 1. |
| `BOOLEAN_SCOPE_INCOMPLETE` | Type is `BOOLEAN` and `hideScope` is not `complete-region`. |
| `BOOLEAN_FALSE_STATE_BROKEN` | Type is `BOOLEAN` and `remainingLayoutComplete` is not exactly `true`. |
| `BOOLEAN_EMPTY_COLUMN_RISK` | Type is `BOOLEAN` and `ancestorRequiredFixedColumn` is `true`. |
| `TEXT_PROPERTY_BOILERPLATE` | Type is `TEXT` and `boilerplate` is `true`. |
| `TEXT_PROPERTY_LINK_RISK` | Type is `TEXT` and `linkBearing` is `true`. |

## Reporting the result

Report the count of errors and warnings, then every issue with its code, location, and
message. The snapshot passes only when there are no errors. State alongside the result:
"Snapshot validation only; production acceptance still requires the recorded desktop and
mobile render evidence."

If the snapshot is not valid JSON or its top level is not an object, the result is a failure
with that one reason.

## Icon and social asset perimeter check

This is a heuristic. It applies only when transparency isolates the artwork.

For each icon or independently linked social icon, export the node at 2x as a PNG and view
it over a background that contrasts with the artwork, so the transparent area is visible.
Then classify it:

- `error`: the file cannot be read, or it has no visible pixels.
- `not-applicable`: the asset is fully opaque. Alpha cannot isolate the artwork, so an
  opaque asset is not evidence of a bad crop. Compare the source crop and the production
  render by eye.
- Otherwise, find the smallest gap between the visible artwork and each of the four file
  edges, in pixels. The required inset is 4% of the file's shorter edge, rounded up, and at
  least 1px (a 64px icon needs 3px).
  - `pass`: the smallest gap is at least the required inset.
  - `needs-review`: the artwork touches an edge, or the smallest gap is under the required
    inset. Compare the source asset, the crop, and the production render before approving.
    A design that deliberately reaches the edge may be dispositioned as a documented visual
    exception.

When the gap is close to the threshold and you cannot measure it with confidence, classify
the icon `needs-review`. Only `pass` is automatic; `needs-review` and `not-applicable` need a
human comparison against the source and the production render. Never add transparent padding
or alter approved brand artwork to satisfy this check.
