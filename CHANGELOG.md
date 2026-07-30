# Changelog

User-visible changes to the Email Love Claude skills, newest first, by skill. Versions are
independent per skill. Every release attaches all three `.skill` bundles.

## emaillove-figma-builder

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
