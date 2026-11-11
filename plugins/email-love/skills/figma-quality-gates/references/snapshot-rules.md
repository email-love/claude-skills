# Snapshot rules

## Contents

- How to apply the rules
- Batch rules
- Module rules
- Image rules
- Group rules and the mobile width calculation
- Property rules
- Icon and social asset perimeter check

Apply these rules by hand to the audit snapshot described in
[snapshot-schema.md](snapshot-schema.md). Work through every rule for every module; do not
sample. Report each failure as `CODE at location: what was found`.

## How to apply the rules

- **Fail closed.** A measurement that is missing, not a number, not finite, or negative is an
  error (`UNKNOWN_MEASUREMENT` or `MEASUREMENT_NEGATIVE`). Never treat it as zero.
- **Errors fail the gate.** Every error is a failed gate. Every warning needs a written
  disposition.
- **Show the arithmetic.** For each group, write out the mobile width calculation per viewport
  so a reviewer can check it.
- **This is snapshot validation only.** A clean snapshot is never production acceptance, which
  still requires the recorded desktop and mobile render evidence.

## Batch rules

| Code | Error when |
|---|---|
| `BATCH_MISSING`, `MODULES_MISSING` | `batch` is not an object, or `modules` is not an array. |
| `PHASE_INVALID` | `batch.phase` is not `proof` or `normal`. |
| `MODULES_EMPTY` | `modules` is empty. An empty list is absent evidence, not a pass. |
| `PROOF_TOO_LARGE` | A proof batch has more than four modules. |
| `PROOF_NOT_ACCEPTED` | A normal batch does not have `proofBatchAccepted: true`. |
| `LIST_TYPE_INVALID` | In a proof batch, `riskClassesPresent` or `proofRisksCovered` is not an array of strings. |
| `PROOF_RISK_INVALID` | A risk class is not one of `photo-crop`, `grouped-icon-text`, `multi-column-properties`, `footer-social`. |
| `PROOF_RISK_UNCOVERED` | A class in `riskClassesPresent` is missing from `proofRisksCovered`. |
| `VIEWPORTS_INVALID` | `mobileViewports` is missing, empty, or holds a value that is not a positive number. |
| `STATUS_INVALID` | `statusClaim` is not one of the four completion states in SKILL.md. |
| `EXPORT_STATUS_INVALID` | `exporter.desktop` or `exporter.mobile` is not `pass`, `fail`, or `deferred`. |
| `COMPLETE_WITHOUT_EXPORT` | `statusClaim` is `complete` but desktop or mobile is not `pass`. |
| `FAILED_EXPORT_NOT_REJECTED` | Desktop or mobile is `fail` and `statusClaim` is not `batch rejected, repair required`. |

Warning `STALE_DEFERRED_STATUS`: the status is the deferred state but both renders are `pass`.

## Module rules

| Code | Error when |
|---|---|
| `MODULE_INVALID` | A module entry is not an object. |
| `SOURCE_MISSING` | `sourceRef` is empty. |
| `PARITY_MISSING` | `sourceParity` is not an object. |
| `PARITY_FAILED` | Any of `content`, `order`, `crop`, `type`, `color`, `spacing`, `desktop`, `mobileIntent` is not exactly `true`. |
| `STRUCTURE_MISSING` | `structure` is not an object. |
| `ARTIFACT_KIND_INVALID` | `artifactKind` is not `module` or `email` (it defaults to `module`). |
| `MODULE_ROOT_INVALID` | A module's `rootTag` is not `mj-wrapper`, or it carries a `nodeType` marker. |
| `MODULE_NOT_PAGE_CHILD` | A module's `directPageChild` is not `true`. |
| `EMAIL_ROOT_INVALID` | An email root has an MJML tag, or its `nodeType` is not `mainFrame`. |
| `EMAIL_THEME_KEYS` | An email root's `themeKeyCount` is below 9. |
| `EMAIL_CHILDREN_INVALID` | An email root's `directChildrenAllWrappers` is not `true`. |
| `UNTAGGED_FRAMES` | `untaggedFrameCount` is not 0. |
| `UNKNOWN_TAGS` | `unknownTagCount` is not 0. |
| `INCOMPLETE_LEAVES` | `incompleteLeafPairCount` is not 0. |
| `FIXED_HEIGHTS` | `unintendedFixedHeightCount` is not 0. |
| `AXIS_EXCEPTIONS_INVALID` | `axisExceptions` is present but not an array. |
| `AXIS_EXCEPTION_INVALID` | An exception lacks a `node`, or its `reason` is not `top-aligned-multi-column`. |
| `UNEQUAL_AXES` | `unequalAxisCount` is greater than the number of valid exceptions. Undocumented mismatches are defects. |
| `CENSUS_MISSING` | `census` is not an object. |
| `INVENTORY_MISSING` | `images`, `groups`, or `properties` is not an array. The array is required even when audited empty. |
| `CENSUS_MISMATCH` | `census.images`, `census.groups`, or `census.properties` does not equal the length of that array. |

## Image rules

For each entry in `images`:

| Code | Error when |
|---|---|
| `IMAGE_INVALID` | The entry is not an object. |
| `IMAGE_FILL_INVALID` | `fillType` is not `IMAGE`. |
| `IMAGE_HASH_MISSING` | `imageHash` is empty. |
| `ALT_TEXT_MISSING` | The image is meaningful (`meaningful` defaults to `true`) and `altText` is empty. |
| `IMAGE_GEOMETRY_INVALID` | `rectWidth`, `rectHeight`, `assetWidth`, or `assetHeight` is not above 0. |
| `IMAGE_ASPECT_MISMATCH` | `cropApproved` is not `true` and the aspect drift is above 2%. |
| `ICON_NOT_SQUARE` | `role` is `icon` or `social`, `nonSquareApproved` is not `true`, and the rectangle ratio differs from 1 by more than 0.02. |

Aspect drift is `abs(rectWidth / rectHeight - assetWidth / assetHeight) / (assetWidth / assetHeight)`.

## Group rules and the mobile width calculation

For each entry in `groups`:

| Code | Error when |
|---|---|
| `GROUP_INVALID`, `COLUMN_INVALID` | The group, or one of its columns, is not an object. |
| `GROUP_GEOMETRY_INVALID` | `width` is not above 0, or there are fewer than two columns. |
| `HEADROOM_UNDOCUMENTED` | `borderHeadroom` is above 0 and `headroomReason` is empty. |
| `GROUP_WIDTH_SUM` | The column widths plus `borderHeadroom` (0 when absent) differ from the group `width` by more than 0.5. |
| `MOBILE_CONTENT_INVALID` | For a viewport, the mobile content width is not above 0. |
| `MOBILE_INNER_INVALID` | For a column at a viewport, the inner width is not above 0. |
| `IMAGE_NATURAL_WIDTH_MISSING` | An image column has no positive `content.naturalWidth`. |
| `MOBILE_IMAGE_TOO_NARROW` | The inner width is below `content.naturalWidth`. |
| `TEXT_WIDTH_MISSING` | A text column has no positive `content.longestUnbreakablePx`. |
| `MOBILE_TEXT_TOO_NARROW` | The inner width is below `content.longestUnbreakablePx`. |

Warning `GROUP_CONTENT_UNMEASURED`: a column's `content.kind` is neither `image` nor `text`.
Disposition it manually.

Run this calculation for every column at every viewport in `batch.mobileViewports`:

```text
mobile content = viewport - mobileSectionPaddingLeft - mobileSectionPaddingRight
resolved       = column width / group width * mobile content
inner          = resolved - column paddingLeft - column paddingRight
```

`inner` must be at least the column's required width, with a tolerance of 0.01. The check is
deliberately conservative about grouped icons: it subtracts both section and column padding
before comparing the resolved mobile box to the asset's natural width.

Worked example: a 520-wide group with section padding 40 and 40, at a 320 viewport. The mobile
content is 240. A 96-wide icon column with padding 0 and 10 resolves to 96 / 520 * 240 = 44.31,
so its inner width is 34.31, which clears a 32 natural width. The 424-wide text column with
padding 16 and 0 resolves to 195.69, inner 179.69, which clears a 90 unbreakable width.

## Property rules

For each entry in `properties`:

| Code | Error when |
|---|---|
| `PROPERTY_INVALID` | The entry is not an object. |
| `PROPERTY_TYPE_INVALID` | `type` is not `TEXT`, `BOOLEAN`, `INSTANCE_SWAP`, or `VARIANT`. |
| `PROPERTY_EVIDENCE_MISSING` | `evidence` is empty. Every property needs a stated use case. |
| `PROPERTY_UNBOUND` | `bindingCount` is below 1. |
| `BOOLEAN_SCOPE_INCOMPLETE` | A BOOLEAN's `hideScope` is not `complete-region`. |
| `BOOLEAN_FALSE_STATE_BROKEN` | A BOOLEAN's `remainingLayoutComplete` is not `true`. |
| `BOOLEAN_EMPTY_COLUMN_RISK` | A BOOLEAN's `ancestorRequiredFixedColumn` is `true`. |
| `TEXT_PROPERTY_BOILERPLATE` | A TEXT property has `boilerplate: true`. |
| `TEXT_PROPERTY_LINK_RISK` | A TEXT property has `linkBearing: true`. |

## Icon and social asset perimeter check

Take a `get_screenshot` of each icon node on its own and look at its edges. Inspect one image
per independently linked social icon. Give each exactly one outcome:

- `pass`: the artwork sits on a transparent background with clear space on all four sides.
  The clear space on each side should be at least 4% of the shorter edge, and never under one
  pixel. On a 64 by 64 icon that is 3 pixels.
- `needs-review`: the artwork touches an edge, or the clear space is thinner than that. Compare
  the source crop and the production render before approving. A deliberately edge-reaching
  design may be dispositioned as a documented visual exception.
- `not-applicable`: the asset is fully opaque, so transparency says nothing about the crop. A
  visual comparison against the source is still required.
- `error`: the asset cannot be read or has no visible pixels.

Only `pass` is automatic. Judging by eye is less exact than measuring pixels, so when the clear
space is close to the threshold, record `needs-review`. Do not approve an unverified sprite
crop, and never add transparent padding or alter approved brand artwork to satisfy this check.
