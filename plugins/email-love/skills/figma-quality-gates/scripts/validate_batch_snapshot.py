#!/usr/bin/env python3
"""Validate a machine-readable Email Love Figma QA snapshot."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_STATES = {
    "complete",
    "canvas and structure ready, exporter verification deferred",
    "batch rejected, repair required",
    "audit incomplete, missing source authority",
}
ALLOWED_RISKS = {
    "photo-crop",
    "grouped-icon-text",
    "multi-column-properties",
    "footer-social",
}
PARITY_KEYS = {
    "content",
    "order",
    "crop",
    "type",
    "color",
    "spacing",
    "desktop",
    "mobileIntent",
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    location: str
    message: str


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def number(value: Any, default: float = 0.0) -> float:
    return float(value) if is_number(value) else default


def validate(snapshot: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []

    def add(severity: str, code: str, location: str, message: str) -> None:
        issues.append(Issue(severity, code, location, message))

    batch = snapshot.get("batch")
    modules = snapshot.get("modules")
    if not isinstance(batch, dict):
        add("error", "BATCH_MISSING", "batch", "Expected a batch object.")
        batch = {}
    if not isinstance(modules, list):
        add("error", "MODULES_MISSING", "modules", "Expected a modules array.")
        modules = []

    phase = batch.get("phase")
    if phase not in {"proof", "normal"}:
        add("error", "PHASE_INVALID", "batch.phase", "Use 'proof' or 'normal'.")
    if phase == "proof" and len(modules) > 4:
        add("error", "PROOF_TOO_LARGE", "modules", "A proof batch may contain at most four modules.")
    if phase == "normal" and batch.get("proofBatchAccepted") is not True:
        add("error", "PROOF_NOT_ACCEPTED", "batch.proofBatchAccepted", "A normal batch requires an accepted proof batch.")

    present = batch.get("riskClassesPresent")
    covered = batch.get("proofRisksCovered")
    if phase == "proof":
        if not isinstance(present, list) or not isinstance(covered, list):
            add("error", "PROOF_RISKS_MISSING", "batch", "Record riskClassesPresent and proofRisksCovered.")
        else:
            unknown = (set(present) | set(covered)) - ALLOWED_RISKS
            if unknown:
                add("error", "PROOF_RISK_INVALID", "batch", f"Unknown risk classes: {sorted(unknown)}")
            missing = set(present) - set(covered)
            if missing:
                add("error", "PROOF_RISK_UNCOVERED", "batch.proofRisksCovered", f"Proof batch does not cover: {sorted(missing)}")

    viewports = batch.get("mobileViewports")
    if not isinstance(viewports, list) or not viewports or not all(is_number(v) and v > 0 for v in viewports):
        add("error", "VIEWPORTS_INVALID", "batch.mobileViewports", "Provide one or more positive mobile viewport widths.")
        viewports = []

    state = batch.get("statusClaim")
    if state not in ALLOWED_STATES:
        add("error", "STATUS_INVALID", "batch.statusClaim", "Use one of the quality-gate completion states.")
    exporter = batch.get("exporter") if isinstance(batch.get("exporter"), dict) else {}
    desktop = exporter.get("desktop")
    mobile = exporter.get("mobile")
    for channel, value in (("desktop", desktop), ("mobile", mobile)):
        if value not in {"pass", "fail", "deferred"}:
            add("error", "EXPORT_STATUS_INVALID", f"batch.exporter.{channel}", "Use pass, fail, or deferred.")
    if state == "complete" and (desktop != "pass" or mobile != "pass"):
        add("error", "COMPLETE_WITHOUT_EXPORT", "batch.statusClaim", "Complete requires desktop and mobile production passes.")
    if "fail" in {desktop, mobile} and state != "batch rejected, repair required":
        add("error", "FAILED_EXPORT_NOT_REJECTED", "batch.statusClaim", "A failed production render requires batch rejection.")
    if state == "canvas and structure ready, exporter verification deferred" and desktop == mobile == "pass":
        add("warning", "STALE_DEFERRED_STATUS", "batch.statusClaim", "Both production renders pass; update the status after remaining gates pass.")

    for index, module in enumerate(modules):
        loc = f"modules[{index}]"
        if not isinstance(module, dict):
            add("error", "MODULE_INVALID", loc, "Expected an object.")
            continue
        name = module.get("name") or f"module {index + 1}"
        mloc = f"{loc} ({name})"

        if not str(module.get("sourceRef") or "").strip():
            add("error", "SOURCE_MISSING", f"{mloc}.sourceRef", "Record the exact source authority.")
        parity = module.get("sourceParity")
        if not isinstance(parity, dict):
            add("error", "PARITY_MISSING", f"{mloc}.sourceParity", "Record every source-parity dimension.")
        else:
            for key in sorted(PARITY_KEYS):
                if parity.get(key) is not True:
                    add("error", "PARITY_FAILED", f"{mloc}.sourceParity.{key}", "Parity is missing or did not pass.")

        structure = module.get("structure")
        if not isinstance(structure, dict):
            add("error", "STRUCTURE_MISSING", f"{mloc}.structure", "Record measured structure results.")
            structure = {}
        artifact_kind = module.get("artifactKind", "module")
        root_tag = structure.get("rootTag", "")
        node_type = structure.get("nodeType", "")
        if artifact_kind == "module":
            if root_tag != "mj-wrapper" or node_type not in {"", None}:
                add("error", "MODULE_ROOT_INVALID", f"{mloc}.structure", "A module is an mj-wrapper with no nodeType marker.")
            if structure.get("directPageChild") is not True:
                add("error", "MODULE_NOT_PAGE_CHILD", f"{mloc}.structure.directPageChild", "A module root must be a direct page child.")
        elif artifact_kind == "email":
            if root_tag not in {"", None} or node_type != "mainFrame":
                add("error", "EMAIL_ROOT_INVALID", f"{mloc}.structure", "An email root has mainFrame and no MJML tag.")
            if number(structure.get("themeKeyCount")) < 9:
                add("error", "EMAIL_THEME_KEYS", f"{mloc}.structure.themeKeyCount", "An email root needs all nine root keys.")
            if structure.get("directChildrenAllWrappers") is not True:
                add("error", "EMAIL_CHILDREN_INVALID", f"{mloc}.structure", "An email root's direct children must all be wrappers.")
        else:
            add("error", "ARTIFACT_KIND_INVALID", f"{mloc}.artifactKind", "Use module or email.")

        for field, code in (
            ("untaggedFrameCount", "UNTAGGED_FRAMES"),
            ("unknownTagCount", "UNKNOWN_TAGS"),
            ("incompleteLeafPairCount", "INCOMPLETE_LEAVES"),
            ("unequalAxisCount", "UNEQUAL_AXES"),
            ("unintendedFixedHeightCount", "FIXED_HEIGHTS"),
        ):
            value = structure.get(field)
            if not is_number(value):
                add("error", "STRUCTURE_COUNT_MISSING", f"{mloc}.structure.{field}", "Record a numeric count.")
            elif value != 0:
                add("error", code, f"{mloc}.structure.{field}", f"Expected 0, found {value}.")

        images = module.get("images", [])
        if not isinstance(images, list):
            add("error", "IMAGES_INVALID", f"{mloc}.images", "Expected an array.")
            images = []
        for image_index, image in enumerate(images):
            iloc = f"{mloc}.images[{image_index}]"
            if not isinstance(image, dict):
                add("error", "IMAGE_INVALID", iloc, "Expected an object.")
                continue
            meaningful = image.get("meaningful", True)
            if image.get("fillType") != "IMAGE":
                add("error", "IMAGE_FILL_INVALID", f"{iloc}.fillType", "A meaningful image must use an IMAGE fill.")
            if not str(image.get("imageHash") or "").strip():
                add("error", "IMAGE_HASH_MISSING", f"{iloc}.imageHash", "Read back a non-empty image hash.")
            if meaningful and not str(image.get("altText") or "").strip():
                add("error", "ALT_TEXT_MISSING", f"{iloc}.altText", "Meaningful imagery needs alt text.")

            rw, rh = number(image.get("rectWidth")), number(image.get("rectHeight"))
            aw, ah = number(image.get("assetWidth")), number(image.get("assetHeight"))
            if min(rw, rh, aw, ah) <= 0:
                add("error", "IMAGE_GEOMETRY_INVALID", iloc, "Rectangle and asset dimensions must be positive.")
            else:
                rect_ratio, asset_ratio = rw / rh, aw / ah
                ratio_drift = abs(rect_ratio - asset_ratio) / asset_ratio
                if not image.get("cropApproved", False) and ratio_drift > 0.02:
                    add("error", "IMAGE_ASPECT_MISMATCH", iloc, f"Rectangle/asset aspect ratios drift by {ratio_drift:.1%} without an approved crop.")
                if image.get("role") in {"icon", "social"} and not image.get("nonSquareApproved", False):
                    if abs(rect_ratio - 1.0) > 0.02:
                        add("error", "ICON_NOT_SQUARE", iloc, "Icon rectangle is not square and has no exception.")

        groups = module.get("groups", [])
        if not isinstance(groups, list):
            add("error", "GROUPS_INVALID", f"{mloc}.groups", "Expected an array.")
            groups = []
        for group_index, group in enumerate(groups):
            gloc = f"{mloc}.groups[{group_index}]"
            if not isinstance(group, dict):
                add("error", "GROUP_INVALID", gloc, "Expected an object.")
                continue
            group_width = number(group.get("width"))
            columns = group.get("columns")
            if group_width <= 0 or not isinstance(columns, list) or len(columns) < 2:
                add("error", "GROUP_GEOMETRY_INVALID", gloc, "A group needs a positive width and at least two columns.")
                continue
            column_sum = sum(number(column.get("width")) for column in columns if isinstance(column, dict))
            if abs(column_sum - group_width) > 0.5:
                add("error", "GROUP_WIDTH_SUM", gloc, f"Column widths total {column_sum:g}, not group width {group_width:g}.")
            section_left = number(group.get("mobileSectionPaddingLeft"))
            section_right = number(group.get("mobileSectionPaddingRight"))
            for viewport in viewports:
                mobile_content = float(viewport) - section_left - section_right
                if mobile_content <= 0:
                    add("error", "MOBILE_CONTENT_INVALID", gloc, f"Viewport {viewport:g}px has no positive content box.")
                    continue
                for column_index, column in enumerate(columns):
                    cloc = f"{gloc}.columns[{column_index}]@{viewport:g}px"
                    if not isinstance(column, dict):
                        add("error", "COLUMN_INVALID", cloc, "Expected an object.")
                        continue
                    column_width = number(column.get("width"))
                    resolved = column_width / group_width * mobile_content
                    inner = resolved - number(column.get("paddingLeft")) - number(column.get("paddingRight"))
                    if inner <= 0:
                        add("error", "MOBILE_INNER_INVALID", cloc, f"Resolved inner width is {inner:.2f}px.")
                        continue
                    content = column.get("content") if isinstance(column.get("content"), dict) else {}
                    kind = content.get("kind")
                    if kind == "image":
                        required = number(content.get("naturalWidth"))
                        if required <= 0:
                            add("error", "IMAGE_NATURAL_WIDTH_MISSING", cloc, "Record the image's minimum natural display width.")
                        elif inner + 0.01 < required:
                            add("error", "MOBILE_IMAGE_TOO_NARROW", cloc, f"Inner width {inner:.2f}px is below image requirement {required:.2f}px.")
                    elif kind == "text":
                        required = number(content.get("longestUnbreakablePx"))
                        if required <= 0:
                            add("error", "TEXT_WIDTH_MISSING", cloc, "Record the exported-font unbreakable width.")
                        elif inner + 0.01 < required:
                            add("error", "MOBILE_TEXT_TOO_NARROW", cloc, f"Inner width {inner:.2f}px is below text requirement {required:.2f}px.")
                    else:
                        add("warning", "GROUP_CONTENT_UNMEASURED", cloc, "Content kind is not image or text; disposition manually.")

        properties = module.get("properties", [])
        if not isinstance(properties, list):
            add("error", "PROPERTIES_INVALID", f"{mloc}.properties", "Expected an array.")
            properties = []
        for property_index, prop in enumerate(properties):
            ploc = f"{mloc}.properties[{property_index}]"
            if not isinstance(prop, dict):
                add("error", "PROPERTY_INVALID", ploc, "Expected an object.")
                continue
            prop_type = prop.get("type")
            if prop_type not in {"TEXT", "BOOLEAN", "INSTANCE_SWAP", "VARIANT"}:
                add("error", "PROPERTY_TYPE_INVALID", f"{ploc}.type", "Use a Figma component-property type.")
            if not str(prop.get("evidence") or "").strip():
                add("error", "PROPERTY_EVIDENCE_MISSING", f"{ploc}.evidence", "Every property needs a stated use case.")
            if number(prop.get("bindingCount")) < 1:
                add("error", "PROPERTY_UNBOUND", f"{ploc}.bindingCount", "Read back at least one binding.")
            if prop_type == "BOOLEAN":
                if prop.get("hideScope") != "complete-region":
                    add("error", "BOOLEAN_SCOPE_INCOMPLETE", f"{ploc}.hideScope", "Bind the complete optional semantic region.")
                if prop.get("remainingLayoutComplete") is not True:
                    add("error", "BOOLEAN_FALSE_STATE_BROKEN", ploc, "The false state must leave a finished layout.")
                if prop.get("ancestorRequiredFixedColumn") is True:
                    add("error", "BOOLEAN_EMPTY_COLUMN_RISK", ploc, "The binding sits inside a required fixed column.")
            if prop_type == "TEXT":
                if prop.get("boilerplate") is True:
                    add("error", "TEXT_PROPERTY_BOILERPLATE", ploc, "Do not expose standing boilerplate as campaign copy.")
                if prop.get("linkBearing") is True:
                    add("error", "TEXT_PROPERTY_LINK_RISK", ploc, "Replacing this text can destroy its hyperlink.")

    return issues


def good_fixture() -> dict[str, Any]:
    return {
        "batch": {
            "name": "proof",
            "phase": "proof",
            "emailWidth": 600,
            "contentWidth": 520,
            "mobileViewports": [320, 375, 390],
            "riskClassesPresent": ["grouped-icon-text"],
            "proofRisksCovered": ["grouped-icon-text"],
            "proofBatchAccepted": True,
            "statusClaim": "complete",
            "exporter": {"desktop": "pass", "mobile": "pass"},
        },
        "modules": [{
            "id": "1:1",
            "name": "Safe icon row",
            "artifactKind": "module",
            "sourceRef": "source frame 1:2",
            "sourceParity": {key: True for key in PARITY_KEYS},
            "structure": {
                "rootTag": "mj-wrapper",
                "nodeType": "",
                "directPageChild": True,
                "untaggedFrameCount": 0,
                "unknownTagCount": 0,
                "incompleteLeafPairCount": 0,
                "unequalAxisCount": 0,
                "unintendedFixedHeightCount": 0,
            },
            "images": [{
                "name": "sparkle",
                "role": "icon",
                "meaningful": True,
                "fillType": "IMAGE",
                "imageHash": "hash",
                "scaleMode": "FILL",
                "rectWidth": 32,
                "rectHeight": 32,
                "assetWidth": 64,
                "assetHeight": 64,
                "cropApproved": False,
                "altText": "Odor filtration",
            }],
            "groups": [{
                "name": "feature row",
                "width": 520,
                "mobileSectionPaddingLeft": 40,
                "mobileSectionPaddingRight": 40,
                "columns": [
                    {"name": "icon", "width": 96, "paddingLeft": 0, "paddingRight": 10,
                     "content": {"kind": "image", "naturalWidth": 32}},
                    {"name": "text", "width": 424, "paddingLeft": 16, "paddingRight": 0,
                     "content": {"kind": "text", "longestUnbreakablePx": 90}},
                ],
            }],
            "properties": [{
                "name": "Show feature row",
                "type": "BOOLEAN",
                "evidence": "Source family contains a shorter version",
                "bindingCount": 1,
                "hideScope": "complete-region",
                "remainingLayoutComplete": True,
                "ancestorRequiredFixedColumn": False,
            }],
        }],
    }


def self_test() -> int:
    good_issues = validate(good_fixture())
    if any(issue.severity == "error" for issue in good_issues):
        print(json.dumps([asdict(issue) for issue in good_issues], indent=2))
        print("self-test failed: good fixture did not pass", file=sys.stderr)
        return 1

    bad = good_fixture()
    bad["batch"]["statusClaim"] = "complete"
    bad["batch"]["exporter"]["mobile"] = "deferred"
    module = bad["modules"][0]
    module["images"][0]["fillType"] = "SOLID"
    module["groups"][0]["columns"][0]["width"] = 72
    module["groups"][0]["columns"][1]["width"] = 448
    module["properties"][0]["hideScope"] = "leaf-only"
    module["properties"][0]["remainingLayoutComplete"] = False
    module["properties"][0]["ancestorRequiredFixedColumn"] = True
    bad_codes = {issue.code for issue in validate(bad) if issue.severity == "error"}
    expected = {
        "COMPLETE_WITHOUT_EXPORT",
        "IMAGE_FILL_INVALID",
        "MOBILE_IMAGE_TOO_NARROW",
        "BOOLEAN_SCOPE_INCOMPLETE",
        "BOOLEAN_FALSE_STATE_BROKEN",
        "BOOLEAN_EMPTY_COLUMN_RISK",
    }
    if not expected.issubset(bad_codes):
        print(f"self-test failed: missing expected codes {sorted(expected - bad_codes)}", file=sys.stderr)
        return 1
    print("validate_batch_snapshot.py self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.snapshot is None:
        parser.error("snapshot is required unless --self-test is used")
    try:
        snapshot = json.loads(args.snapshot.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, indent=2))
        return 1
    if not isinstance(snapshot, dict):
        print(json.dumps({"passed": False, "error": "Top-level JSON must be an object."}, indent=2))
        return 1
    issues = validate(snapshot)
    errors = sum(issue.severity == "error" for issue in issues)
    warnings = sum(issue.severity == "warning" for issue in issues)
    print(json.dumps({
        "passed": errors == 0,
        "errors": errors,
        "warnings": warnings,
        "issues": [asdict(issue) for issue in issues],
    }, indent=2))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

