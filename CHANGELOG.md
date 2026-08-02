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

### 1.11.3

- **ESP migration v1, commit 4 (final adapter of the v1 series). Customer.io Source adapter
  added,** replacing the "Coming in v1 (next commit)" stub. Uses the Customer.io MCP
  (`cio_read_api` + `cio_schema` + `cio_prime`).
- Adapter directs the agent to call `cio_prime` first every session for latest authoritative
  usage instructions, then `cio_auth_status` to confirm the environment.
- Names the Customer.io product-naming trap up front: "Automations" in the UI == the
  `campaigns` API resource. Adapter tells the agent to speak the customer's language while
  using the API resource names in tool calls.
- v1 pulls **Templates and Newsletters only** (the two most direct "here's an email" places).
  Discover asks the customer which of the two, or both. Uses `cio_schema` to fetch current
  list-endpoint shapes before calling `cio_read_api`, so a schema drift doesn't silently
  produce wrong fields.
- Fetch: `cio_read_api` on the get-endpoint returns the resource with HTML body. Adapter
  notes the field name varies (`body`, `html`, `content`) and directs the agent to check
  the get-endpoint schema for the current field name.
- Explicit v1 non-goals named for the customer up front: does NOT pull Automations
  (campaigns) or their messages, Transactional messages, Design Studio emails, Layouts, or
  Snippets. If the customer's active content mostly lives in one of these surfaces, adapter
  says so before running so the customer doesn't get a silently-partial result. v1.1 will
  extend to campaign messages, transactional, and Design Studio.
- Two Customer.io-specific report additions per row: asset ID + resource type + direct edit
  URL, and the "templates vs newsletters" pool distinction.
- Warning against reading Customer.io's own agent skills (`design-studio`, `fly-api`)
  during a migration audit: they document CREATING content, not READING it out for
  migration, and mixing them in mid-audit introduces contradictions.
- Step 0's Customer.io load-reference stub updated (was "Coming in v1", now points to the
  real section at the end of the file).

### 1.11.2

- **ESP migration v1, commit 3 of the series. Marketo Source adapter added, prioritized
  ahead of Customer.io** for an enterprise onboarding on Marketo. No official Marketo MCP
  exists, so the adapter uses direct Marketo REST API calls with the customer's OAuth 2.0
  client-credentials.
- One-time credential collection: Munchkin ID, client ID, client secret, optional workspace
  name. The three secrets are treated as sensitive; adapter offers an environment-variable
  path so they never appear in the conversation.
- Auth: single OAuth token request at session start, cached and reused for `expires_in`
  seconds (typically 3600), re-auth only on 401.
- Discover: list `emailTemplates.json` with `status=approved` and `maxReturn=200`,
  paginated by offset until empty. Sort locally by `updatedAt` since the API has no native
  sort. Same 50-template threshold as Klaviyo: ask for a filter rather than pull the
  whole list, because Marketo template lists are dominated by legacy variants.
- Fetch: `emailTemplate/{id}/content.json` returns HTML directly. Render to PNG via
  headless Chrome at the target email width, feed to the design-converter worker on the
  same Path B route the other adapters use.
- Rate limits called out explicitly: 100 calls / 20 seconds, 10,000 / day. Adapter
  directs the agent to serial fetch (not parallel) to stay under the burst window without
  any bookkeeping, and to back off on error code 606.
- Marketo-specific report additions: template ID, direct edit URL, folder path, and
  workspace per row.
- Named the honest v1 caveat: pulls Marketo Templates only, not Emails (individual sends
  inside Programs, where most Marketo customers keep their active content) or Content
  Blocks (reusable header/footer snippets). v1.1 will extend to both.
- Step 0 updated to include Marketo as choice (d), Customer.io renumbered to (e).
- Customer.io adapter still to come as commit 4.

### 1.11.1

- **ESP migration v1, commit 2 of the series.** Klaviyo Source adapter added, replacing the
  "Coming in v1 (next commit)" stub. Uses the official Klaviyo MCP.
- Discover: `get_account_details` first to confirm staging vs production, then
  `list_email_templates` with minimal-payload discovery sort by `-updated`, paginated at
  Klaviyo's 10-per-page cap. Explicit safeguard: when the account has more than about 50
  templates, ask the customer to filter (by date range, name, or IDs) rather than pulling
  everything, since the majority of a Klaviyo template list is old drafts and one-off A/B
  splits.
- Fetch: `get_email_template` returns HTML directly. Skip templates whose `editor_type` is
  text-only. Render HTML to PNG via headless Chrome at the target email width, same command
  as the Local Folder adapter. Feed PNG to the design-converter worker.
- Explicitly do NOT default to `render_email_template`: it is rate-limited to 3/s burst and
  60/m steady (much stricter than the other endpoints), and for migration we care about
  structure, not substituted content. Only use it when a customer explicitly wants merge
  tags evaluated.
- Klaviyo-specific report additions: include the template ID and the direct edit URL for
  every row, and note the editor type (`SYSTEM_DRAGGABLE` templates convert more cleanly
  than raw HTML templates).
- Named the honest caveat about templates-only v1 scope: Klaviyo customers often keep their
  best current content inside campaigns and flows, not standalone templates. The adapter
  tells the customer this up front rather than silently pulling only templates.
- Customer.io adapter comes in commit 3.

### 1.11.0

- **ESP migration v1, commit 1 of the series.** The audit no longer assumes the source is a
  Figma file. New Step 0 ("Pick your source") at the top of the audit asks the customer where
  their emails live: a Figma file (current behavior), a local folder of HTML/EML/PNG, Klaviyo,
  or Customer.io.
- **Local Folder source adapter** added at the end of the skill. Discover walks the folder
  once, groups by inferred template intent, and confirms with the customer before proceeding.
  Fetch renders HTML/EML to PNG at the target email width via headless Chrome (or uses PNG
  directly), then hands each to the design-converter worker on the existing Path B route. The
  audit-step adaptations are named explicitly: no file to survey (Step 2 replaced), always
  REFERENCE ONLY (Step 3), no scale factor (Step 4), per-template modules with no cross-
  template dedup in v1 (Step 5), foundations from first 3 templates (Step 6), effort estimate
  higher than Figma path due to no dedup (Step 7).
- Report shape for local-folder sources is deliberately slimmer than the Figma report: no
  verdict-by-verdict rollup, no scale-factor block, no source-fidelity classification section.
- Klaviyo and Customer.io adapters come in commits 2 and 3.

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
