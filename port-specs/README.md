# Port specs

Specs for porting Claude-side changes to the Codex plugin at
[email-love/codex-agents](https://github.com/email-love/codex-agents).

## Why this folder exists

The Email Love skills ship on two surfaces: Claude (this repo) and Codex (a separate repo).
Changes usually land on Claude first, then get mirrored to Codex. Hand-porting every change
consumes Claude tokens on work that has already been done once, so for anything larger than
a one-line tweak, the pattern is:

1. Ship the change on Claude with a normal commit.
2. Drop a **port spec** into this folder describing exactly what needs to happen in the
   Codex repo to mirror it.
3. Run that spec through a Codex session against the Codex repo. Codex executes the port,
   commits it, pushes.
4. Update `sources.json`'s drift entry to mark the port done.

## What a port spec should contain

- **Context**: what changed on Claude side, the commit range, why it matters.
- **Prerequisites**: fetch state, branch, anything to check before starting.
- **Files to modify or create**: a concrete list, not "figure it out."
- **Step-by-step**: exact edits, keyed to Codex conventions (progressive-disclosure
  references, voice, `references/` folder structure).
- **Version bump**: exact old and new numbers.
- **CHANGELOG entry**: the bullets to add.
- **`sources.json` update**: which fields change.
- **Validation**: run `python3 scripts/validate_repo.py`.
- **Commit message template**: so provenance is consistent.
- **Verification checklist**: what to check before pushing.
- **Codex conventions cheat sheet**: enough that Codex doesn't have to consult the Claude
  repo to figure out voice or structure.

## When to skip the spec (and hand-port instead)

- Very small changes (a bullet, a rule tweak): writing a spec is more work than doing it.
- Design-decision changes where Codex would need cross-tool judgment calls: keep those on
  Claude and hand-port them yourself.

Everything else: write a spec, put it here.

## Naming

`{topic}.md`, kebab-case. Example: `esp-migration-v1.md`.

Ports are usually one spec per Claude commit-batch, not one per Claude commit. Batch ports
when the Claude changes belong together (a whole feature, a set of related defect fixes)
rather than shipping each individual patch as its own port.
