#!/usr/bin/env python3
"""Check exported icon PNGs for clipped alpha at the asset perimeter."""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - dependency failure is environment-specific
    print("Pillow is required: install the Python package 'Pillow'.", file=sys.stderr)
    raise SystemExit(2)


def inspect_icon(path: Path, min_inset_pct: float) -> dict[str, object]:
    try:
        with Image.open(path) as source:
            rgba = source.convert("RGBA")
    except (OSError, ValueError) as exc:
        return {"path": str(path), "passed": False, "error": str(exc)}

    width, height = rgba.size
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return {
            "path": str(path),
            "passed": False,
            "width": width,
            "height": height,
            "error": "No visible pixels were found.",
        }

    left, top, right, bottom = bbox
    insets = {
        "left": left,
        "top": top,
        "right": width - right,
        "bottom": height - bottom,
    }
    minimum = min(insets.values())
    required = max(1, math.ceil(min(width, height) * min_inset_pct))
    touches_edge = minimum == 0
    passed = minimum >= required
    return {
        "path": str(path),
        "passed": passed,
        "width": width,
        "height": height,
        "alphaBounds": [left, top, right, bottom],
        "transparentInsets": insets,
        "minimumInsetPx": minimum,
        "requiredInsetPx": required,
        "touchesEdge": touches_edge,
        "message": (
            "Transparent perimeter is safe."
            if passed
            else "Visible alpha reaches or sits too close to the file perimeter; inspect the crop or source asset."
        ),
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        safe_path = root / "safe.png"
        clipped_path = root / "clipped.png"

        safe = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        ImageDraw.Draw(safe).ellipse((8, 8, 55, 55), fill=(20, 120, 80, 255))
        safe.save(safe_path)

        clipped = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        ImageDraw.Draw(clipped).ellipse((-4, 8, 43, 55), fill=(20, 120, 80, 255))
        clipped.save(clipped_path)

        safe_result = inspect_icon(safe_path, 0.04)
        clipped_result = inspect_icon(clipped_path, 0.04)
        if safe_result.get("passed") is not True or clipped_result.get("passed") is not False:
            print(json.dumps([safe_result, clipped_result], indent=2))
            print("self-test failed", file=sys.stderr)
            return 1
    print("check_icon_perimeter.py self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="*", type=Path)
    parser.add_argument(
        "--min-inset-pct",
        type=float,
        default=0.04,
        help="Minimum transparent inset as a fraction of the shorter edge (default: 0.04).",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.images:
        parser.error("at least one image is required unless --self-test is used")
    if not 0 <= args.min_inset_pct < 0.5:
        parser.error("--min-inset-pct must be at least 0 and less than 0.5")

    results = [inspect_icon(path, args.min_inset_pct) for path in args.images]
    passed = all(result.get("passed") is True for result in results)
    print(json.dumps({"passed": passed, "results": results}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

