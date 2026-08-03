#!/usr/bin/env python3
"""Validate the Email Love Claude skills repo.

Catches the failure classes that have actually bitten this repo: version drift across
manifests, em dashes (a house rule), customer identifiers leaking into public files, broken
references, and obsolete Codex install guidance. Runs in CI and locally. Standard library only.

Usage:  python3 scripts/validate_repo.py
Exit 0 if everything passes, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []
def fail(msg): errors.append(msg)

EM_DASH = "—"

# Files that ship to users and must stay clean.
SHIPPED_TEXT = (
    list((ROOT / "skills").glob("*/SKILL.md"))
    + list((ROOT / "skills").glob("*/references/*.md"))
    + [ROOT / "README.md", ROOT / "CHANGELOG.md", ROOT / "SECURITY.md"]
)

# Identifiers that must never appear in shipped files. Specific on purpose: a bare "seed"
# is a legitimate word ("seed the theme colors"), so only distinctive strings are listed.
FORBIDDEN = [
    "Seed LCM", "StreetEasy", "JustFoodForDogs", "just-food-for-dogs",
    "jWCW0M3wEe3reFgkHTQSLY", "fslU7JfL4yS6dvnMYIDi1b",
    "BgzGQBoKCua2IO8zbBsQ8t", "5Y8DQjgx49rXVmj7qsvqGz",
]

def check_marketplace():
    mk = ROOT / ".claude-plugin" / "marketplace.json"
    if not mk.exists():
        fail("marketplace.json missing"); return {}
    try:
        d = json.loads(mk.read_text())
    except json.JSONDecodeError as e:
        fail(f"marketplace.json does not parse: {e}"); return {}
    versions = {}
    for p in d.get("plugins", []):
        name, ver = p.get("name"), p.get("version")
        if not name or not ver:
            fail(f"marketplace plugin entry missing name/version: {p}"); continue
        versions[name] = ver
        if not (ROOT / "skills" / name).is_dir():
            fail(f"marketplace lists '{name}' but skills/{name} does not exist")
    return versions

def check_skill(name, marketplace_version):
    d = ROOT / "skills" / name
    pj = d / ".claude-plugin" / "plugin.json"
    skill = d / "SKILL.md"
    if not pj.exists(): fail(f"{name}: plugin.json missing"); return
    if not skill.exists(): fail(f"{name}: SKILL.md missing"); return
    try:
        manifest = json.loads(pj.read_text())
    except json.JSONDecodeError as e:
        fail(f"{name}: plugin.json does not parse: {e}"); return

    mver = manifest.get("version")
    if mver != marketplace_version:
        fail(f"{name}: plugin.json version {mver} != marketplace {marketplace_version}")

    text = skill.read_text()
    # frontmatter present with name + description
    if not text.startswith("---"):
        fail(f"{name}: SKILL.md has no frontmatter")
    else:
        fm = text.split("---", 2)[1] if text.count("---") >= 2 else ""
        if "name:" not in fm: fail(f"{name}: frontmatter missing name")
        if "description:" not in fm: fail(f"{name}: frontmatter missing description")
        # Claude.ai skill upload rejects descriptions over 1024 chars
        dm = re.search(r"^description:\s*(.*?)(?=\n[a-z_]+:\s|\Z)", fm, re.DOTALL | re.MULTILINE)
        if dm:
            dlen = len(dm.group(1).strip())
            if dlen > 1024:
                fail(f"{name}: frontmatter description is {dlen} chars (claude.ai upload limit: 1024)")

    # "This is version X of this skill" matches the manifest
    m = re.search(r"This is version ([0-9]+\.[0-9]+\.[0-9]+) of this skill", text)
    if not m:
        fail(f"{name}: SKILL.md has no 'This is version X of this skill' line")
    elif m.group(1) != mver:
        fail(f"{name}: SKILL.md says version {m.group(1)} but manifest is {mver}")

    # Cross-skill references by raw GitHub URL must resolve to a real file in this repo.
    for other, ref in re.findall(
        r"raw\.githubusercontent\.com/email-love/claude-skills/main/skills/"
        r"([A-Za-z0-9_\-]+)/references/([A-Za-z0-9_\-]+\.md)", text):
        if not (ROOT / "skills" / other / "references" / ref).exists():
            fail(f"{name}: cross-skill URL points at skills/{other}/references/{ref}, "
                 f"which does not exist")

    # Local references only apply to a skill that owns a references/ directory. A skill without
    # one (the builder) reaches another skill's references by the URLs checked above, so its bare
    # 'references/x.md' mentions are pointers, not local files.
    if (d / "references").is_dir():
        for ref in re.findall(r"(?<![./\w])references/([A-Za-z0-9_\-]+\.md)", text):
            if not (d / "references" / ref).exists():
                fail(f"{name}: SKILL.md references references/{ref} which does not exist")

def check_shipped_text():
    for f in SHIPPED_TEXT:
        if not f.exists(): continue
        t = f.read_text()
        rel = f.relative_to(ROOT)
        if EM_DASH in t:
            n = t.count(EM_DASH)
            fail(f"{rel}: contains {n} em dash(es) (house rule: none)")
        for token in FORBIDDEN:
            if token in t:
                fail(f"{rel}: contains forbidden identifier '{token}'")

def check_readme_codex():
    r = ROOT / "README.md"
    if not r.exists(): return
    t = r.read_text()
    # obsolete Codex guidance: telling users to curl or install a flat AGENTS.md
    if re.search(r"curl[^\n]*AGENTS\.md", t) or "project-scoped `AGENTS.md`" in t:
        fail("README.md still contains obsolete Codex AGENTS.md install guidance; "
             "Codex uses the v3.0.0 plugin")

def check_build_completeness():
    # the converter delegates to references at runtime; those files must exist so a built
    # bundle is not missing them
    conv = ROOT / "skills" / "emaillove-eds-converter" / "references"
    for needed in ("render-spec.md", "structure.md"):
        p = conv / needed
        if not p.exists() or p.stat().st_size == 0:
            fail(f"eds-converter references/{needed} missing or empty; the bundle would ship broken")

def main():
    versions = check_marketplace()
    for name in versions:
        check_skill(name, versions[name])
    check_shipped_text()
    check_readme_codex()
    check_build_completeness()

    if errors:
        print(f"FAIL: {len(errors)} problem(s)\n")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: all checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
