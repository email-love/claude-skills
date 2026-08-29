#!/usr/bin/env python3
"""Validate the Email Love Claude skills repo.

Catches the failure classes that have actually bitten this repo: version drift across
manifests, em dashes (a house rule), customer identifiers leaking into public files, broken
references, and obsolete Codex install guidance. Runs in CI and locally. Standard library only.

Layout since the plugin restructure: one 'email-love' bundle plugin at plugins/email-love/
holding four skills (eds-converter, migration-audit, figma-builder, template-repair), plus four
DEPRECATED single-skill compatibility entries in marketplace.json, pointing at the same skill
directories. Entries exist so standalone installs and every shipped "Staying current" check keep
resolving; their versions must stay synced with each SKILL.md's own version line.

Usage:  python3 scripts/validate_repo.py
Exit 0 if everything passes, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "email-love" / "skills"
errors = []
def fail(msg): errors.append(msg)

EM_DASH = "—"
PUBLIC_CODEX_PLUGIN_URL = (
    "https://chatgpt.com/plugins/plugins_6a739f43c3b48191b1281a9b2d48b409"
)

# Shim entry name -> skill directory name. The shims carry the legacy names every shipped
# copy looks up; the directories carry the short names the bundle namespaces by.
STANDALONE_ENTRIES = {"emaillove-figma-quality-gates"}

SHIM_TO_DIR = {
    "emaillove-eds-converter": "eds-converter",
    "emaillove-figma-quality-gates": "figma-quality-gates",
    "emaillove-migration-audit": "migration-audit",
    "emaillove-figma-builder": "figma-builder",
    "emaillove-template-repair": "template-repair",
}

# Files that ship to users and must stay clean.
SHIPPED_TEXT = (
    list(SKILLS.glob("*/SKILL.md"))
    + list(SKILLS.glob("*/references/*.md"))
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
    """Returns {shim_name: version} for the four compatibility entries."""
    mk = ROOT / ".claude-plugin" / "marketplace.json"
    if not mk.exists():
        fail("marketplace.json missing"); return {}
    try:
        d = json.loads(mk.read_text())
    except json.JSONDecodeError as e:
        fail(f"marketplace.json does not parse: {e}"); return {}

    entries = {p.get("name"): p for p in d.get("plugins", []) if p.get("name")}

    # The bundle entry.
    bundle = entries.get("email-love")
    if not bundle:
        fail("marketplace.json has no 'email-love' bundle entry")
    else:
        src = ROOT / bundle.get("source", "").lstrip("./")
        pj = src / ".claude-plugin" / "plugin.json"
        if not pj.exists():
            fail(f"bundle source {bundle.get('source')} has no .claude-plugin/plugin.json")
        else:
            try:
                manifest = json.loads(pj.read_text())
                if manifest.get("version") != bundle.get("version"):
                    fail(f"bundle plugin.json version {manifest.get('version')} != "
                         f"marketplace {bundle.get('version')} (strict mode: plugin.json wins; keep them identical)")
            except json.JSONDecodeError as e:
                fail(f"bundle plugin.json does not parse: {e}")

    # The four compatibility entries. All must exist (deleting one silently kills the shipped
    # "Staying current" check for every old copy in the wild).
    shim_versions = {}
    for shim, dirname in SHIM_TO_DIR.items():
        entry = entries.get(shim)
        if not entry:
            fail(f"marketplace.json is missing legacy shim entry '{shim}'; old installs and "
                 f"shipped version checks go silently stale without it")
            continue
        expected_src = f"./plugins/email-love/skills/{dirname}"
        if entry.get("source") != expected_src:
            fail(f"shim '{shim}' source is {entry.get('source')}, expected {expected_src}")
        # Legacy shims (skills that predate the bundled plugin) must say
        # DEPRECATED so nobody installs them fresh. Skills introduced AFTER the
        # bundle are legitimate standalone entries; they must instead say the
        # bundle carries them.
        if shim in STANDALONE_ENTRIES:
            if "Bundled in the 'email-love' plugin" not in entry.get("description", ""):
                fail(f"standalone entry '{shim}' must say it is bundled in the email-love plugin")
        elif "DEPRECATED" not in entry.get("description", ""):
            fail(f"shim '{shim}' description does not say DEPRECATED")
        if not entry.get("version"):
            fail(f"shim '{shim}' has no version")
        shim_versions[shim] = entry.get("version")
        if not (SKILLS / dirname).is_dir():
            fail(f"shim '{shim}' points at skills/{dirname} which does not exist")
    return shim_versions

def check_skill(shim_name, shim_version):
    dirname = SHIM_TO_DIR[shim_name]
    d = SKILLS / dirname
    skill = d / "SKILL.md"
    if not skill.exists(): fail(f"{dirname}: SKILL.md missing"); return

    # Skill dirs stay PLAIN (SKILL.md + references). A per-skill plugin.json would make the
    # directory read as a plugin root and conflict with its role inside the bundle.
    if (d / ".claude-plugin" / "plugin.json").exists():
        fail(f"{dirname}: has a .claude-plugin/plugin.json; skill dirs must stay plain "
             f"(defined by their marketplace entries only)")

    text = skill.read_text()
    # frontmatter present with name + description
    if not text.startswith("---"):
        fail(f"{dirname}: SKILL.md has no frontmatter")
    else:
        fm = text.split("---", 2)[1] if text.count("---") >= 2 else ""
        m = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
        if not m: fail(f"{dirname}: frontmatter missing name")
        elif m.group(1) != dirname:
            fail(f"{dirname}: frontmatter name is '{m.group(1)}', expected '{dirname}' "
                 f"(frontmatter name determines the invocation name)")
        if "description:" not in fm: fail(f"{dirname}: frontmatter missing description")
        # Claude.ai skill upload rejects descriptions over 1024 chars
        dm = re.search(r"^description:\s*(.*?)(?=\n[a-z_]+:\s|\Z)", fm, re.DOTALL | re.MULTILINE)
        if dm:
            dlen = len(dm.group(1).strip())
            if dlen > 1024:
                fail(f"{dirname}: frontmatter description is {dlen} chars (claude.ai upload limit: 1024)")

    # "This is version X of this skill" matches the SHIM version (the shims are how every
    # shipped copy learns about updates; a shim that lags tells old copies they are current).
    m = re.search(r"This is version ([0-9]+\.[0-9]+\.[0-9]+) of this skill", text)
    if not m:
        fail(f"{dirname}: SKILL.md has no 'This is version X of this skill' line")
    elif m.group(1) != shim_version:
        fail(f"{dirname}: SKILL.md says version {m.group(1)} but shim '{shim_name}' is {shim_version}")

    # The Staying current check must look up the LEGACY entry name, since that is the entry
    # the shims keep alive for every copy in the wild.
    if "## Staying current" in text and shim_name not in text.split("## Staying current", 1)[1]:
        fail(f"{dirname}: Staying current section does not name its legacy marketplace entry "
             f"'{shim_name}'")

    # Cross-skill references by raw GitHub URL must resolve to a real file in this repo.
    for other, ref in re.findall(
        r"raw\.githubusercontent\.com/email-love/claude-skills/main/plugins/email-love/skills/"
        r"([A-Za-z0-9_\-]+)/references/([A-Za-z0-9_\-]+\.md)", text):
        if not (SKILLS / other / "references" / ref).exists():
            fail(f"{dirname}: cross-skill URL points at skills/{other}/references/{ref}, "
                 f"which does not exist")
    # Old-layout raw URLs are stale after the restructure.
    if re.search(r"raw\.githubusercontent\.com/email-love/claude-skills/main/skills/", text):
        fail(f"{dirname}: SKILL.md still carries a pre-restructure raw URL "
             f"(main/skills/...); update to main/plugins/email-love/skills/...")

    # Local references only apply to a skill that owns a references/ directory. A skill without
    # one (the builder) reaches another skill's references by the URLs checked above, so its bare
    # 'references/x.md' mentions are pointers, not local files.
    if (d / "references").is_dir():
        # Bundle-only runtime dependencies: packaged into the standalone .skill
        # by build.sh from their canonical source skills (byte-equality checked
        # by scripts/verify_dist.sh), so they intentionally do not exist under
        # this skill's source references/.
        bundle_deps = {
            "template-repair": {"render-spec.md", "structure.md", "figma-builder-skill.md"},
            "figma-builder": {"render-spec.md", "structure.md"},
        }.get(dirname, set())
        for ref in re.findall(r"(?<![./\w])references/([A-Za-z0-9_\-]+\.md)", text):
            if ref in bundle_deps:
                continue
            if not (d / "references" / ref).exists():
                fail(f"{dirname}: SKILL.md references references/{ref} which does not exist")

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
             "Codex uses the public plugin or the tagged Git marketplace")
    if "--ref v3.0.0" in t:
        fail("README.md still points Codex users at the obsolete v3.0.0 release")
    if "codex plugin marketplace add email-love/codex-agents --ref v4.9.0" not in t:
        fail("README.md must point Git-backed Codex installs at v4.9.0")
    if PUBLIC_CODEX_PLUGIN_URL not in t:
        fail("README.md must link to the public Email Love plugin")

    sources_path = ROOT / "sources.json"
    try:
        sources = json.loads(sources_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"sources.json cannot be read: {error}")
        return
    codex = sources.get("codexPlugin", {})
    if codex.get("publicPluginUrl") != PUBLIC_CODEX_PLUGIN_URL:
        fail("sources.json codexPlugin.publicPluginUrl is missing or incorrect")
    if codex.get("currentPublicRelease") != codex.get("currentRelease"):
        fail("sources.json public and source Codex releases are not aligned")
    if codex.get("currentGitRelease") != "v4.9.0":
        fail("sources.json codexPlugin.currentGitRelease must be v4.9.0")
    if codex.get("currentGitCommit") != "b383c3476c2c6908223c3e8ce483a26f36a06c35":
        fail("sources.json codexPlugin.currentGitCommit must record the v4.9.0 commit")
    if "GitHub push does not update directory users" not in codex.get("distributionModel", ""):
        fail("sources.json must record that the public plugin is a reviewed snapshot")
    checklist = codex.get("releaseChecklist", [])
    required_steps = ("validate", "GitHub release", "submission portal", "review", "public listing")
    combined = " ".join(checklist)
    for required_step in required_steps:
        if required_step not in combined:
            fail(f"sources.json Codex release checklist is missing {required_step!r}")

def check_build_completeness():
    # the converter delegates to references at runtime; those files must exist so a built
    # bundle is not missing them
    conv = SKILLS / "eds-converter" / "references"
    for needed in ("render-spec.md", "structure.md"):
        p = conv / needed
        if not p.exists() or p.stat().st_size == 0:
            fail(f"eds-converter references/{needed} missing or empty; the bundle would ship broken")

    repair = SKILLS / "template-repair"
    for needed in (
        "diagnostic-workflow.md",
        "symptom-cause-matrix.md",
        "repair-verification.md",
    ):
        p = repair / "references" / needed
        if not p.exists() or p.stat().st_size == 0:
            fail(f"template-repair references/{needed} missing or empty; the bundle would ship broken")

    evals_path = repair / "evals" / "evals.json"
    try:
        evals = json.loads(evals_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"template-repair evals cannot be read: {error}")
    else:
        if evals.get("skill_name") != "emaillove-template-repair":
            fail("template-repair evals skill_name must be emaillove-template-repair")
        if len(evals.get("evals", [])) < 11:
            fail("template-repair must contain at least eleven evals (the six routing/"
                 "regression cases plus wrong-target mapping, late-arriving source evidence, "
                 "binding preservation, missing mobile exporter proof, and permitted "
                 "reconstruction)")

def main():
    shim_versions = check_marketplace()
    for shim in SHIM_TO_DIR:
        if shim in shim_versions:
            check_skill(shim, shim_versions[shim])
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
