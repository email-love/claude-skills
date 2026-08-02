# ESP Migration v1: Codex Port Spec

Port the four v1 source adapters from the Claude `emaillove-migration-audit` skill into the
Codex `email-love-design-system-migration` skill.

## Context

Between commits `cb25519` and `48d085d` in
[email-love/claude-skills](https://github.com/email-love/claude-skills), the
`emaillove-migration-audit` skill grew from Figma-only to supporting four sources: Figma
(current), Local Folder, Klaviyo, Marketo, and Customer.io. The Claude changes shipped as
patch bumps `1.10.3 → 1.11.3`.

The Codex plugin at [email-love/codex-agents](https://github.com/email-love/codex-agents)
has one migration skill (`email-love-design-system-migration`) covering what Claude splits
into two (audit + eds-converter). All source-selector and source-adapter work lands in that
one skill, in a **new `references/sources/` subfolder** to fit Codex's progressive-disclosure
reference pattern.

Codex plugin currently at `v3.0.1`. This port bumps to `v3.1.0` (minor: new capability).

## Prerequisites

Before starting:

1. `cd` into a fresh checkout of `email-love/codex-agents`, or `git fetch origin && git
   checkout main && git pull`. Confirm clean working tree via `git status`.
2. Confirm the working branch is `main`.
3. Verify the plugin's current version is `3.0.1`:
   `grep '"version"' plugins/email-love/.codex-plugin/plugin.json`
4. Read `plugins/email-love/skills/email-love-design-system-migration/SKILL.md` in full,
   plus its existing `references/audit.md` file, before making any edits. You need to know
   the current structure to slot changes into it cleanly.

## What to build

**Files to create (4):**
- `plugins/email-love/skills/email-love-design-system-migration/references/sources/local-folder.md`
- `plugins/email-love/skills/email-love-design-system-migration/references/sources/klaviyo.md`
- `plugins/email-love/skills/email-love-design-system-migration/references/sources/marketo.md`
- `plugins/email-love/skills/email-love-design-system-migration/references/sources/customer-io.md`

**Files to modify (4):**
- `plugins/email-love/skills/email-love-design-system-migration/SKILL.md`: add Step 0
  source selector, and add the sources folder to the "Load references by phase" list.
- `plugins/email-love/skills/email-love-design-system-migration/references/audit.md`: at
  the top, add a pointer to the source-adapter-specific audit adjustments (which steps get
  replaced/skipped/adjusted per non-Figma source).
- `plugins/email-love/.codex-plugin/plugin.json`: version `3.0.1 → 3.1.0`.
- `CHANGELOG.md`: add a `3.1.0` entry at the top.
- `sources.json`: update `upstream.commit` and `migration_tag`.

## Authoritative content source

For each of the four source adapters, the authoritative content is the corresponding
section in the Claude-side migration-audit SKILL.md at commit `48d085d`:

**Raw file URL (pinned to the commit):**
```
https://raw.githubusercontent.com/email-love/claude-skills/48d085d/skills/emaillove-migration-audit/SKILL.md
```

Locate these four `### Source: ...` sections in that file:
- `### Source: Local Folder`
- `### Source: Klaviyo`
- `### Source: Marketo`
- `### Source: Customer.io`

Each section carries its own Discover, Fetch, audit-step adaptations, and report-shape
content. The content itself is what to port; the file structure is what to change.

## Step-by-step

### 1. Add Step 0 source selector to SKILL.md

Insert a new step at the top of Phase 1, before the current "Confirm the source Figma file"
step. Content is a compressed version of the Claude Step 0 section (found at commit
`48d085d`, near the top of the audit SKILL.md, headed `## Step 0: Pick your source`).

Compressed form for Codex's SKILL.md:

```
## Phase 0: Pick your source

Ask the customer where their emails live before touching anything else:

- (a) Figma file: current default, richest metadata, cross-source deduplication for free
- (b) Local folder of HTML / EML / PNG: Claude Code or Codex CLI required for file access
- (c) Klaviyo: via the official Klaviyo MCP
- (d) Marketo: via the customer's Marketo REST API credentials (no MCP exists)
- (e) Customer.io: via the Customer.io MCP

An unstated source is the failure mode that silently walks a folder as if it were a Figma
page. **Do not skip this question.**

Recommend Figma when the customer has one: it is the only source that produces a fully-
populated audit report (verdict rollup, scale-factor detection, structured brand
foundations). Other sources work and produce a real Email Love design system out the other
end, but the audit report is slimmer for them.

Load the corresponding source adapter from `references/sources/` for the customer's
choice: `local-folder.md`, `klaviyo.md`, `marketo.md`, or `customer-io.md`. For Figma,
proceed with the rest of this skill as-written; no adapter needed.
```

Adjust the phase number if the current SKILL.md uses different numbering (Codex plugin may
have renumbered from Claude's; check the existing structure and use the correct number so
subsequent phases stay stable).

### 2. Add the sources folder to "Load references by phase"

In the "Load references by phase" list (near the top of SKILL.md), add:

```
- **Non-Figma sources (adapter loaded on demand per Phase 0):**
  - [sources/local-folder.md](references/sources/local-folder.md)
  - [sources/klaviyo.md](references/sources/klaviyo.md)
  - [sources/marketo.md](references/sources/marketo.md)
  - [sources/customer-io.md](references/sources/customer-io.md)
```

Only load the one for the source the customer picked. Do not eagerly load all four.

### 3. Create the four source adapter files

For each of `local-folder.md`, `klaviyo.md`, `marketo.md`, and `customer-io.md`:

1. Fetch the raw Claude SKILL.md at commit `48d085d` (URL above).
2. Extract the `### Source: X` section for that adapter (top of section through the end,
   which is the start of the next `### Source:` or `## Staying current`).
3. Adapt it to Codex-reference conventions (below).
4. Save to `plugins/email-love/skills/email-love-design-system-migration/references/sources/{slug}.md`.

**Codex reference conventions (apply to all four adapter files):**

- **Top-level headings are `##`, not `###`.** In Claude's SKILL.md, source adapters live
  as `### Source: X` under a `## Source Adapters` parent. In Codex references, each file
  stands alone, so promote the top heading to `##`.
- **Rename headings from "Source: X" to "Source adapter: X"** for clarity when a Codex
  contributor sees just the filename.
- **Preserve exact rule numbers, endpoint paths, tool names, and code examples.** These are
  the load-bearing details; do not paraphrase them.
- **Preserve every "explicit v1 caveat" and "product-naming trap" callout verbatim.** These
  exist because they surfaced from real customer feedback; softening them defeats the point.
- **Cross-references**: where Claude's content says "Phase 3 step 3" or "the eds-converter
  skill," rewrite to Codex's equivalents (Codex has one migration skill, so the same info
  usually lives in `references/module-conversion.md` and `references/audit.md`; reword the
  cross-reference to point at the Codex file).
- **No em dashes** (Codex plugin follows the same rule as Claude side, and validate_repo.py
  will fail on any).
- **Preserve the "Requires Claude Code" / "Not usable from Claude.ai" callouts**, but
  Codex-adjust them: for Local Folder, "Requires Codex CLI (local file access)"; for
  Marketo, "Not usable from Codex without an environment that permits outbound HTTP." For
  Klaviyo and Customer.io, the MCP requirement replaces the surface requirement, so just
  say "Requires the Klaviyo MCP / Customer.io MCP connected to your Codex session."

### 4. Update `audit.md` to point at source adapters

At the top of `plugins/email-love/skills/email-love-design-system-migration/references/audit.md`,
after the file's opening context, add a short callout box or paragraph:

```
### Non-Figma sources: audit-step adjustments

When the customer's source is not a Figma file (see Phase 0), the audit steps below apply
with adjustments named in the loaded source adapter's "Audit-step adaptations" section.
Do not run the Figma-specific steps against a folder of HTML files or an ESP template list:
the source adapter tells you which steps are replaced, skipped, or reshaped for that
source, and why.
```

This is a small pointer, not a rewrite of `audit.md`. The per-source specifics live in the
source adapter files, not in `audit.md`.

### 5. Bump plugin version

In `plugins/email-love/.codex-plugin/plugin.json`, change:

```
"version": "3.0.1"
```

to:

```
"version": "3.1.0"
```

Minor bump because this is a new capability (four new sources), not a fix.

### 6. Add CHANGELOG entry

At the top of `CHANGELOG.md`, insert a new entry (adjust today's date):

```markdown
## 3.1.0 - YYYY-MM-DD

Ports ESP migration v1 from the Claude skills (claude-skills commits `cb25519` through
`48d085d`). The migration skill no longer assumes the source is a Figma file. New
Phase 0 asks the customer where their emails live, and per-source adapters in
`references/sources/` handle Discover, Fetch, and audit-step adaptations.

- **Phase 0: Pick your source.** Added to SKILL.md. Customer picks Figma (current
  behavior, unchanged), Local Folder, Klaviyo, Marketo, or Customer.io. Adapter for the
  chosen source is loaded on demand.
- **Local Folder source adapter** (`references/sources/local-folder.md`). Walks a folder
  of HTML/EML/PNG files, renders each to PNG via headless Chrome, feeds to the design-
  converter worker. Requires Codex CLI for file access.
- **Klaviyo source adapter** (`references/sources/klaviyo.md`). Uses the official Klaviyo
  MCP. Deliberately avoids `render_email_template` due to its 3/s burst rate limit. Names
  the v1 caveat: pulls Templates only, not the campaigns and flows where many customers
  keep active content.
- **Marketo source adapter** (`references/sources/marketo.md`). No Marketo MCP exists, so
  uses direct REST with OAuth 2.0 client-credentials. Explicit rate-limit guidance
  (100/20s serial fetch). Names the v1 caveat: pulls Templates only, not Emails or
  Content Blocks.
- **Customer.io source adapter** (`references/sources/customer-io.md`). Uses the CIO MCP
  (`cio_read_api` + `cio_schema` + `cio_prime`). Names the "Automations in UI ==
  campaigns in API" product-naming trap. Pulls Templates and Newsletters (customer picks
  one or both). Explicit v1 non-goals: does not pull Automations messages,
  Transactional, Design Studio emails, Layouts, or Snippets.
- `audit.md` gets a pointer at the top directing the reader to the source adapter's
  "Audit-step adaptations" section for non-Figma sources.
- No cross-source deduplication in v1: each source item processes independently. The
  design system that comes out has more components than the theoretical minimum (a header
  used in 5 emails becomes 5 near-identical components), collapsed during design review.
```

### 7. Update `sources.json`

Update the `upstream` block:

```json
{
  "upstream": {
    "repository": "https://github.com/email-love/claude-skills",
    "commit": "48d085d6068ad1665e6e78c7ce9c1f9e00e9c51d",
    "builder_tag": "emaillove-figma-builder-v2.9.2",
    "render_tag": "emaillove-eds-converter-v1.19.3",
    "migration_tag": "emaillove-migration-audit-v1.11.3"
  },
  ...
}
```

The other fields (`legacy_snapshots`) stay unchanged.

### 8. Validate

Run `python3 scripts/validate_repo.py`. It must pass before commit. If it fails on em
dashes or other content rules, fix and re-run.

### 9. Commit

Commit message template (use verbatim, adjust date only):

```
Port ESP migration v1 from Claude skills

Mirrors claude-skills commits cb25519 through 48d085d, which took the
migration audit from Figma-only to supporting four sources.

New Phase 0 "Pick your source" in SKILL.md asks the customer where
their emails live. Per-source adapters in references/sources/ handle
Discover, Fetch, and audit-step adaptations for the source they pick.
The Figma path is unchanged; the four new source paths are Local
Folder, Klaviyo, Marketo, and Customer.io.

Each adapter names its v1 scope honestly up front so a customer whose
active content mostly lives in an out-of-scope surface (Klaviyo
campaigns, Marketo Emails/Content Blocks, CIO Automations/Design
Studio) hears about it before running the migration.

No cross-source deduplication in v1: each source item processes
independently. Design review collapses near-duplicate components after
the fact. v2 will add structural dedup.

audit.md gets a top-of-file pointer at the source-adapter's audit-step
adjustments. Bumps plugin version 3.0.1 -> 3.1.0. sources.json
upstream commit and migration_tag bumped to match.
```

Then push to origin/main.

## Verification checklist

Before pushing, confirm:

- [ ] Four new files exist under `plugins/email-love/skills/email-love-design-system-migration/references/sources/`
- [ ] Each source adapter file starts with `## Source adapter: {name}` (H2, not H3)
- [ ] Each source adapter file contains a "V1 caveat" / "Not pulled in v1" section
- [ ] No em dashes anywhere in changed files:
      `grep -rn $'\xe2\x80\x94' plugins/ CHANGELOG.md sources.json`
- [ ] SKILL.md carries a Phase 0 section referencing the four sources
- [ ] SKILL.md's "Load references by phase" list mentions `sources/`
- [ ] `audit.md` has the top-of-file pointer at source-adapter audit-step adjustments
- [ ] `plugin.json` version is `3.1.0`
- [ ] `CHANGELOG.md` opens with `## 3.1.0 - YYYY-MM-DD`
- [ ] `sources.json` `upstream.commit` is `48d085d6068ad1665e6e78c7ce9c1f9e00e9c51d`
- [ ] `sources.json` `upstream.migration_tag` is `emaillove-migration-audit-v1.11.3`
- [ ] `python3 scripts/validate_repo.py` passes
- [ ] `git status` shows only intentional files staged

## Codex conventions cheat sheet

Enough to work from without consulting Claude source content beyond the raw file URL above:

- **Reference file structure**: each file is self-contained, top heading is `##`, filename
  is kebab-case matching the topic (`local-folder.md`, `customer-io.md`).
- **Voice**: short direct sentences, imperative mood, no em dashes. Same rule as Claude side.
- **File loading semantics**: SKILL.md's "Load references by phase" list is authoritative
  for what gets pulled into context. Files in `references/` are only loaded when SKILL.md
  routes to them, so an adapter in `references/sources/` only loads when Phase 0 picks it.
- **Cross-linking**: use relative Markdown links (`[foo.md](references/foo.md)` from
  SKILL.md, `[../foo.md](../foo.md)` from a sibling references file).
- **Rule numbers**: preserve exactly (`R0.3.1`, `R3.4.1`, etc.). They index into
  render-geometry.md and render-nodes.md; a wrong number becomes a broken cross-reference.
- **Tool names**: preserve exactly (`cio_read_api`, `get_email_template`, etc.). Adapters
  are read by agents that will call those tools verbatim.

## After the port lands

Update `sources.json` in the Claude repo (email-love/claude-skills) at
`sources.json` → `drift` → the four ESP migration entries (2026-08-01 timestamps): change
their `codexStatus` from "Not yet ported. Wait until commit N so all v1 adapters port as
one Codex commit" to "Ported in v3.1.0 (codex-agents commit `{hash}`)."

Also update `codexPlugin.currentRelease` to `v3.1.0` and `codexPlugin.portsClaudeCommit`
to `48d085d6068ad1665e6e78c7ce9c1f9e00e9c51d`.

That closes the loop.
