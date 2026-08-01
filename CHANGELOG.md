# Changelog

User-visible changes to the Email Love Claude skills, newest first, by skill. Versions are
independent per skill. Every release attaches all three `.skill` bundles.

## emaillove-figma-builder

### 2.9.2
- A "Which model to run this with" note: strongest model for Path B (and for the
  migration-audit/eds-converter skills), a faster model for routine Path A campaign builds once a
  design system is already synced and verified.

### 2.9.1
- The downloadable bundle now carries the stop-and-resume rules that shipped after 2.9.0.
- The update check reads `marketplace.json` rather than the repo-wide latest release, so a
  builder no longer compares itself against another skill's release.

### 2.9.0 and earlier (same day)
- Announce when you stop: report completed work, what remains, why, and how to resume, in the
  same message. Do not stop between the sections of one email.
- Two build paths made explicit: instance a published design system, or generate structure
  through AI Import and transcribe it. Never hand-author structure.
- Path B derives the source scale before converting, and states the content width once.
- Progress reporting with counts, a named section, and an estimate revised from observed pace.
- Runtime expectations stated up front, so a normal multi-section build does not read as a hang.

## emaillove-eds-converter

### 1.19.3
- **Mobile stacking now has a mandatory checkpoint** (Portsmouth batch 1 defect). Phase 3
  step 3 renamed from "Merge the mobile twin" to "Decide mobile behavior" and split into
  Part A (always runs: record a stacking decision per multi-column section) and Part B
  (conditional: merge the mobile twin if one exists). The old skill silently skipped step 3
  when there was no mobile twin, which is the common case on unstructured legacy sources,
  and shipped header lockups that stacked on mobile as a result.
- **The mj-group rule has concrete visual tells now** (Portsmouth defect same class). New
  bullet in the "visual pattern" section names three tells for a lockup: unequal columns
  with one small and fixed, columns sharing a continuous background, or the block being a
  header or footer strip. Patterned on the bleed concession's "recognizing this is its own
  step" treatment.
- **Step 5 verification catches stacking defects.** Mobile check reworded from "list the
  mobile keys you set" (empty list read as a pass) to require an explicit stacking decision
  per multi-column section plus the keys that produce it. Visual check now takes a second
  screenshot at mobile width so group-vs-loose-columns mistakes surface visually.
- **Wrapper instance sizing documented** (Portsmouth defect 2). Phase 2 step 7 and Phase 3
  step 5 both state: a wrapper is FIXED at the target email width, as a component and as
  every instance of it. Section 0's FILL rule applies inside a wrapper, not to the wrapper
  itself. Previously silent, so the inside-a-module default got misapplied one level up.

### 1.19.2
- A model-choice note: use your most capable model for this skill, since a migration runs once
  and a dropped rule becomes a component that silently breaks on export later.

### 1.19.1
- Bundle and update-check fixes as above.

### 1.19.0 and earlier (same day)
- A prescribed, non-optional library structure: cover, getting started, foundations with real
  Figma variables, a type specimen sheet, buttons, one page per category, campaigns.
- One content width for the whole library, applied to every module, because the conversion
  worker guesses padding per screenshot with no knowledge of sibling modules.
- One scale factor applied to every number, with a ratio acceptance test that catches per-style
  drift. On a reference-only source there is no factor: build to email standards.
- The two-column swap: the standard rebuild for a photo that overlaps or bleeds past its block,
  which email cannot express. Such a block stays live text with a named concession, not an image.
- Images come across as rendered nodes, never raw fills, so crops and transparency survive.
- Heights hug, spacing is auto-layout padding, and a gap belongs to one block, never both.
- Pinned text columns carry slack for font substitution at send time.
- A single consolidation pass resolved 19 contradictions that accumulated across the day, and
  corrected a wrong ground-truth claim about where the exporter reads button alignment.

## emaillove-migration-audit

### 1.10.3
- **Lockup rows are now a recognized build constraint** (Portsmouth batch 1 defect,
  audit-side half). The build-constraints vocabulary now includes "a two-column row that
  reads as a visual lockup" (logo + headline, icon + copy, shared background, header or
  footer strips), which the row records as "`mj-group`; keep side by side on mobile".
  Reason: the audit walks the whole library at once and is much better placed to notice
  that six header rows across six emails are all the same lockup than the converter is,
  meeting each one alone with only a desktop screenshot.

### 1.10.2
- A model-choice note: use your most capable model here too, since the whole conversion phase
  builds on this report's classifications.

### 1.10.1
- Bundle and update-check fixes as above.

### 1.10.0 and earlier (same day)
- Source fidelity classification: whether a file's geometry is a specification to preserve
  (authoritative), partly (partial), or only a reference to take brand and structure from. A
  messy library does not block a migration; it changes what gets carried across.
- A deduplicated module inventory as the unit of work, with a per-design roll-up, rather than a
  per-template list. A repetitive library reduces to far fewer distinct modules than designs.
- Verdicts recorded per module, with a named concession where a block converts cleanly apart
  from one effect email cannot reproduce.
- Scale detection with a ratio check, skipped entirely on a reference-only source.
- Announce when you stop, and name the state file, the same as the other skills.
