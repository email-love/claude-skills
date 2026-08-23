#!/usr/bin/env bash
# Package each skill into dist/<name>.skill for GitHub release download.
#
# A .skill bundle is a zip containing <skill-name>/ with SKILL.md and everything
# the skill references at runtime. Earlier bundles shipped SKILL.md alone, which
# broke every skill that delegates to references/: the instructions survived, the
# files they pointed at did not.
#
# Builds are DETERMINISTIC: files are staged through an explicit allowlist,
# ordered by sorted path, stripped of extra zip attributes, and stamped with one
# fixed timestamp — so the same source tree produces byte-identical archives on
# any machine, and a published asset can be independently re-derived and
# checksum-compared. Every bundle carries the repository LICENSE, because each
# archive is installable on its own. Symlinks refuse the build outright.
set -euo pipefail

cd "$(dirname "$0")"
rm -rf dist && mkdir -p dist

SKILLS_ROOT="plugins/email-love/skills"
# One fixed timestamp for reproducibility (zip stores local mtimes).
STAMP="202601010000"

# A symlink inside a package is a portability problem and a path-traversal risk
# once unpacked elsewhere. Refuse to build rather than publish one.
if find "$SKILLS_ROOT" -type l -print | grep -q .; then
  echo "refusing to build: symlink(s) found under $SKILLS_ROOT" >&2
  find "$SKILLS_ROOT" -type l -print >&2
  exit 1
fi

# Bundle names keep the LEGACY emaillove-* prefix on purpose: release asset URLs,
# docs links, and every already-uploaded claude.ai copy know those names. The short
# directory names are the plugin-bundle namespace, not the .skill distribution name.
# claude.ai reads the invocation name from SKILL.md frontmatter, not the folder.
built=0
for dir in "$SKILLS_ROOT"/*/; do
  short="$(basename "$dir")"
  name="emaillove-$short"
  # -workspace dirs hold customer data and are gitignored; never package them.
  case "$short" in *-workspace) continue ;; esac
  [ -f "$dir/SKILL.md" ] || { echo "skip $short (no SKILL.md)"; continue; }

  staging="$(mktemp -d)"
  mkdir -p "$staging/$name"
  # Explicit allowlist: SKILL.md, references/ (markdown only), and the LICENSE.
  install -m 0644 "$dir/SKILL.md" "$staging/$name/SKILL.md"
  install -m 0644 LICENSE "$staging/$name/LICENSE"

  # Cross-skill runtime dependencies: a standalone bundle must execute its
  # documented workflow without fetching instruction files from GitHub, so the
  # render contract (and, for repair, the Builder skill) is packaged into the
  # bundle. The SKILL.md text instructs a local-first lookup that matches this
  # layout. verify_dist.sh asserts byte-equality with the canonical source.
  mkdir -p "$staging/$name/references"
  case "$short" in
    template-repair)
      install -m 0644 "$SKILLS_ROOT/eds-converter/references/render-spec.md" \
        "$staging/$name/references/render-spec.md"
      install -m 0644 "$SKILLS_ROOT/eds-converter/references/structure.md" \
        "$staging/$name/references/structure.md"
      install -m 0644 "$SKILLS_ROOT/figma-builder/SKILL.md" \
        "$staging/$name/references/figma-builder-skill.md"
      ;;
    figma-builder)
      install -m 0644 "$SKILLS_ROOT/eds-converter/references/render-spec.md" \
        "$staging/$name/references/render-spec.md"
      install -m 0644 "$SKILLS_ROOT/eds-converter/references/structure.md" \
        "$staging/$name/references/structure.md"
      ;;
  esac
  if [ -d "$dir/references" ]; then
    ( cd "$dir" && find references -type f -name '*.md' -print0 ) \
      | while IFS= read -r -d '' f; do
          mkdir -p "$staging/$name/$(dirname "$f")"
          install -m 0644 "$dir/$f" "$staging/$name/$f"
        done
    # Anything under references/ that the allowlist would drop is an error,
    # not a silent omission.
    unshipped="$(cd "$dir" && find references -type f ! -name '*.md' 2>/dev/null || true)"
    if [ -n "$unshipped" ]; then
      echo "refusing to build $name: files present that the allowlist would drop:" >&2
      echo "$unshipped" >&2
      exit 1
    fi
  fi

  # Deterministic: fixed mtime, sorted entry order, no extra attributes.
  find "$staging" -exec touch -t "$STAMP" {} +
  ( cd "$staging" && find "$name" \( -type f -o -type d \) | LC_ALL=C sort \
      | zip -qX "$OLDPWD/dist/$name.skill" -@ )
  rm -rf "$staging"

  files=$(unzip -l "dist/$name.skill" | awk 'NR>3 && $4 != "" && $4 !~ /\/$/' | wc -l | tr -d ' ')
  built=$((built + 1))
  echo "built dist/$name.skill  ($files files)"
done

# Every skill directory must have produced a bundle.
expected="$(find "$SKILLS_ROOT" -maxdepth 2 -name SKILL.md -not -path '*-workspace/*' | wc -l | tr -d ' ')"
if [ "$built" -ne "$expected" ]; then
  echo "expected $expected bundles, built $built" >&2
  exit 1
fi

# sha256sum on Linux, shasum -a 256 on macOS.
if command -v sha256sum >/dev/null 2>&1; then
  ( cd dist && sha256sum ./*.skill > SHA256SUMS )
else
  ( cd dist && shasum -a 256 ./*.skill > SHA256SUMS )
fi

echo
echo "Contents:"
for f in dist/*.skill; do
  echo "  $f"
  unzip -l "$f" | awk 'NR>3 && $4 != "" && $4 !~ /\/$/ {print "    " $4}'
done
echo
echo "$built bundle(s) in dist/, checksums in dist/SHA256SUMS"
