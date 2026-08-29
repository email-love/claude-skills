#!/usr/bin/env bash
# Post-build assertions on the bundles in dist/.
#
# Everything here is a property a broken release would violate: the right number
# of bundles, readable zip data, no symlinks or executables smuggled in, no entry
# escaping its own directory, the LICENSE present in each one, every runtime
# reference a SKILL.md names actually inside its own bundle, exact source parity
# for the allowlisted files, checksums that match the files on disk, and
# byte-identical output when the build runs twice (determinism).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
SKILLS_ROOT="$ROOT/plugins/email-love/skills"
expected="$(find "$SKILLS_ROOT" -maxdepth 2 -name SKILL.md -not -path '*-workspace/*' | wc -l | tr -d ' ')"

shopt -s nullglob
archives=("$DIST"/*.skill)
if [ "${#archives[@]}" -ne "$expected" ]; then
  echo "expected $expected .skill bundles in dist/, found ${#archives[@]}" >&2
  exit 1
fi

for a in "${archives[@]}"; do
  name="$(basename "$a" .skill)"
  short="${name#emaillove-}"
  src="$SKILLS_ROOT/$short"

  unzip -tq "$a" >/dev/null || { echo "corrupt archive: $a" >&2; exit 1; }

  listing="$(unzip -Z1 "$a")"
  for required in "$name/SKILL.md" "$name/LICENSE"; do
    grep -qxF "$required" <<<"$listing" || {
      echo "$a is missing $required" >&2; exit 1; }
  done

  # Nothing may escape the bundle's own directory (traversal / stray roots).
  if grep -v "^$name/" <<<"$listing" | grep -q .; then
    echo "$a contains entries outside $name/:" >&2
    grep -v "^$name/" <<<"$listing" >&2
    exit 1
  fi
  if grep -q '\.\.' <<<"$listing"; then
    echo "$a contains a path with '..'" >&2; exit 1
  fi

  # Long-form listing: reject symlinks (l) and any executable bit.
  if unzip -Z "$a" | grep -Eq '^[lL]'; then
    echo "$a contains a symlink" >&2; exit 1
  fi
  if unzip -Z "$a" | grep -Eq '^-.{0,8}x'; then
    echo "$a contains an executable file" >&2; exit 1
  fi

  # Runtime containment: every local references/ path the SKILL.md names must
  # be inside this bundle. (A skill that reads a file the bundle lacks installs
  # broken — the failure class this repository has already hit once.)
  while IFS= read -r ref; do
    grep -qxF "$name/$ref" <<<"$listing" || {
      echo "$a: SKILL.md names $ref but the bundle does not contain it" >&2
      exit 1
    }
  done < <(grep -oE '\(references/[A-Za-z0-9._/-]+\.md\)' "$src/SKILL.md" \
             | tr -d '()' | LC_ALL=C sort -u)

  # Same containment for runtime scripts the SKILL.md tells the agent to run.
  while IFS= read -r ref; do
    grep -qxF "$name/$ref" <<<"$listing" || {
      echo "$a: SKILL.md names $ref but the bundle does not contain it" >&2
      exit 1
    }
  done < <(grep -oE 'scripts/[A-Za-z0-9._/-]+\.py' "$src/SKILL.md" \
             | LC_ALL=C sort -u)

  # Cross-skill runtime dependencies each bundle must carry, as
  # bundle-path=canonical-source pairs. Kept in lockstep with build.sh.
  deps=""
  case "$short" in
    template-repair)
      deps="references/render-spec.md=$SKILLS_ROOT/eds-converter/references/render-spec.md
references/structure.md=$SKILLS_ROOT/eds-converter/references/structure.md
references/figma-builder-skill.md=$SKILLS_ROOT/figma-builder/SKILL.md" ;;
    figma-builder)
      deps="references/render-spec.md=$SKILLS_ROOT/eds-converter/references/render-spec.md
references/structure.md=$SKILLS_ROOT/eds-converter/references/structure.md" ;;
  esac

  # Every mapped dependency is present AND byte-identical to its canonical
  # source (a stale packaged copy is drift, not resilience).
  if [ -n "$deps" ]; then
    tmpx="$(mktemp -d)"
    while IFS='=' read -r bundle_rel canon; do
      [ -n "$bundle_rel" ] || continue
      grep -qxF "$name/$bundle_rel" <<<"$listing" || {
        echo "$a is missing packaged runtime dependency $bundle_rel" >&2; exit 1; }
      ( cd "$tmpx" && unzip -qo "$a" "$name/$bundle_rel" )
      cmp -s "$tmpx/$name/$bundle_rel" "$canon" || {
        echo "$a: packaged $bundle_rel differs from canonical $canon" >&2; exit 1; }
    done <<<"$deps"
    rm -rf "$tmpx"
  fi

  dep_paths="$(printf '%s\n' "$deps" | cut -d= -f1)"

  # Source parity: every allowlisted source file is in the archive, path for
  # path, and no archive file lacks a source counterpart (mapped dependencies
  # excepted — their counterpart is the canonical file checked above).
  while IFS= read -r -d '' f; do
    rel="${f#"$src/"}"
    grep -qxF "$name/$rel" <<<"$listing" || {
      echo "$a is missing source file $rel" >&2; exit 1; }
  done < <(find "$src" -maxdepth 1 -name SKILL.md -print0; \
           if [ -d "$src/references" ]; then find "$src/references" -type f -name '*.md' -print0; fi; \
           if [ -d "$src/scripts" ]; then find "$src/scripts" -type f -name '*.py' -print0; fi)
  while IFS= read -r entry; do
    case "$entry" in
      */|"$name/LICENSE") continue ;;
      "$name/SKILL.md") [ -f "$src/SKILL.md" ] || { echo "$a: no source for $entry" >&2; exit 1; } ;;
      "$name/references/"*)
        rel="${entry#"$name/"}"
        if grep -qxF "$rel" <<<"$dep_paths"; then continue; fi
        [ -f "$src/$rel" ] || {
        echo "$a contains $entry with no source counterpart" >&2; exit 1; } ;;
      "$name/scripts/"*)
        rel="${entry#"$name/"}"
        [ -f "$src/$rel" ] || {
        echo "$a contains $entry with no source counterpart" >&2; exit 1; } ;;
      *) echo "$a contains unexpected entry $entry" >&2; exit 1 ;;
    esac
  done <<<"$listing"

  echo "ok $(basename "$a")"
done
echo "ok runtime containment + source parity"

if command -v sha256sum >/dev/null 2>&1; then SHACMD="sha256sum"; else SHACMD="shasum -a 256"; fi
( cd "$DIST" && $SHACMD -c SHA256SUMS >/dev/null ) || {
  echo "checksums in dist/SHA256SUMS do not match" >&2; exit 1; }
echo "ok SHA256SUMS"

# Determinism: a second build from the same tree must be byte-identical.
before="$(cd "$DIST" && $SHACMD ./*.skill)"
( cd "$ROOT" && bash build.sh >/dev/null )
after="$(cd "$DIST" && $SHACMD ./*.skill)"
if [ "$before" != "$after" ]; then
  echo "build is not deterministic: checksums changed on rebuild" >&2
  diff <(echo "$before") <(echo "$after") >&2 || true
  exit 1
fi
echo "ok deterministic rebuild"

echo
echo "${#archives[@]} bundle(s) verified"
