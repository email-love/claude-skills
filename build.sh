#!/usr/bin/env bash
# Package each skill into dist/<name>.skill for GitHub release download.
#
# A .skill bundle is a zip containing <skill-name>/ with SKILL.md and everything
# the skill references at runtime. Earlier bundles shipped SKILL.md alone, which
# broke every skill that delegates to references/: the instructions survived, the
# files they pointed at did not.
set -euo pipefail

cd "$(dirname "$0")"
rm -rf dist && mkdir -p dist

for dir in skills/*/; do
  name="$(basename "$dir")"
  # -workspace dirs hold customer data and are gitignored; never package them.
  case "$name" in *-workspace) continue ;; esac
  [ -f "$dir/SKILL.md" ] || { echo "skip $name (no SKILL.md)"; continue; }

  staging="$(mktemp -d)"
  mkdir -p "$staging/$name"
  cp "$dir/SKILL.md" "$staging/$name/"
  [ -d "$dir/references" ] && cp -R "$dir/references" "$staging/$name/"

  ( cd "$staging" && zip -qr "$OLDPWD/dist/$name.skill" "$name" )
  rm -rf "$staging"

  files=$(unzip -l "dist/$name.skill" | awk 'NR>3 && $4 != "" && $4 !~ /\/$/' | wc -l | tr -d ' ')
  echo "built dist/$name.skill  ($files files)"
done

echo
echo "Contents:"
for f in dist/*.skill; do
  echo "  $f"
  unzip -l "$f" | awk 'NR>3 && $4 != "" && $4 !~ /\/$/ {print "    " $4}'
done
