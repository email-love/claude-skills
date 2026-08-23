---
name: template-repair
description: Diagnose and repair an existing Email Love email template or reusable module in Figma when the plugin rejects it, the canvas and export disagree, content flattens into images, Outlook clips text, mobile stacking or spacing is wrong, links or images fail, dark mode breaks, or component properties stop working. Use for targeted repair of Email Love structures that already exist. Do not use to create a new campaign, convert an ordinary Figma comp, or migrate a legacy library; route those to figma-builder or migration-audit and eds-converter.
---

# Email Love Template Repair

Repair the smallest proven defect in an existing Email Love template or module, preserve what
already works, and verify the result through the production exporter before calling it fixed.

## Non-negotiable boundaries

- Diagnose before writing. Reproduce the reported failure and identify the node, breakpoint,
  and mechanism.
- Establish source fidelity before writing. Treat a failure screenshot as symptom evidence unless
  the user explicitly identifies it as the intended design. Name the visual authority and the
  structural authority separately. Never derive intended geometry from the broken canvas when an
  original comp, migration audit, supplied HTML, or approved source render exists.
- Preserve the original. For a campaign template, repair a duplicate unless the user explicitly
  authorizes editing the original. For a library module, ask whether to repair the source component
  in place, which updates its instances, or create a replacement.
- Never detach an instance, rewrite design-system foundations, rename pages or tokens, or clear
  deliberate dark-mode overrides.
- Never build unknown `mj-section`, `mj-column`, or leaf scaffolding from memory. Replace a broken
  component with an intact library instance, or reconstruct converter-built structure strictly from
  the Email Love render contract.
- Never treat a clean plugin-data read-back or a good canvas screenshot as proof of a good email.
  Desktop and mobile exporter renders are the arbiter.
- Never say `fixed` when exporter verification is deferred. Say exactly what remains unverified.

## Route the request

Confirm that the target is already an Email Love structure:

- A whole email has a root with `nodeType = mainFrame` and Email Love wrappers below it.
- A reusable module is a COMPONENT tagged `mj-wrapper` and carries no `mainFrame` marker.
- An Email Love component instance surfaces its main component's plugin data.

If none of those is true, stop. Use `figma-builder` for one ordinary Figma comp or new campaign,
`migration-audit` for a legacy library assessment, and `eds-converter` for an approved migration.
A random frame that merely looks like an email is not a broken Email Love template.

## Check the tools

Before promising a repair, confirm the Figma tool catalog includes `use_figma`, `get_metadata`, and
`get_screenshot`. If `use_figma` is absent, perform read-only diagnosis and give the user an exact
handoff; do not promise a canvas fix.

Probe for `emaillove_export_figma` and `emaillove_preview_email` before deferring export checks. The
Email Love MCP is a separate connection from this skill. When those tools are absent, give the
one-time connection step:

```bash
claude mcp add --transport http emaillove https://mcp.emaillove.com/mcp
```

On claude.ai, add `https://mcp.emaillove.com/mcp` under Settings, Connectors. The sign-in is Email
Love's normal account flow, shared with the Figma plugin. Start a fresh session after connecting.
An unavailable exporter makes the exporter state `deferred`, not `pass`.

## Load the repair references

Read these three local references for every task:

- [Diagnostic workflow](references/diagnostic-workflow.md)
- [Symptom and cause matrix](references/symptom-cause-matrix.md)
- [Repair verification and report](references/repair-verification.md)

Before any structural repair, read the authoritative Email Love render sources:

```text
https://raw.githubusercontent.com/email-love/claude-skills/main/plugins/email-love/skills/eds-converter/references/render-spec.md
https://raw.githubusercontent.com/email-love/claude-skills/main/plugins/email-love/skills/eds-converter/references/structure.md
```

When the target is composed from design-system instances, also read the current Builder skill:

```text
https://raw.githubusercontent.com/email-love/claude-skills/main/plugins/email-love/skills/figma-builder/SKILL.md
```

Keep its Path A discipline: do not open or restructure instance internals. Replace the instance or
fix the source component under the user's chosen scope. If the authoritative files cannot be read,
stop before structural work rather than reconstructing the rules from memory.

## Run the repair

### 1. Capture the failure

Record the file, page, target node id, root shape, reported symptom, affected breakpoint or email
client, and whether the issue appears on the canvas, in plugin Preview, in exported HTML, or only
after ESP delivery. Save a before screenshot and exporter render when available.

For HTML supplied by the user or exported by the plugin, treat the HTML as authoritative for the
structure it contains. Inspect its desktop DOM and mobile media behavior separately. A screenshot
does not overrule supplied HTML.

### 2. Protect the working state

For a campaign, duplicate the whole email root and name the copy `Repair working copy - <name>`.
Keep the original untouched. Record the new root id.

For a module or main component, stop before the first write and settle impact with the user:
repairing the source in place changes every instance; a replacement changes none until swapped.
Never make that choice silently.

Record node ids, component-property counts, property bindings, and the last verified state. This is
the resumable record if the task is interrupted.

Complete every pending read-only investigation that could change the target node, source authority,
breakpoint intent, or repair dimensions before the first write. Parallel discovery does not permit
early mutation: wait for those checks, or record why an unavailable check cannot change the repair.
Then freeze a compact Repair Contract before writing:

```text
Repair Contract
- target: <node id> (<email root | module | instance | leaf>)
- class: property_patch | instance_replacement | section_reconstruction
- evidence: <the observed facts this repair rests on>
- allowed nodes: <exactly the ids this class may touch>
- change: <node id>: <before> -> <after>   (one line per intended change)
- preserved invariants: <the ones this class can affect - root shape, node census, content
  counts, tags, property bindings, tokens, assets>
- rollback: <how the working copy reverts>
- required checks: structure read-back; exporter desktop; exporter mobile
  (+ canvas mobile when a mobile source exists)
```

Keep the record proportional to the repair: a link fix or root-marker fix needs no geometry
fields; geometry and proof-instance mapping belong in the contract only when they can affect the
mutation. One contract covers one scoped repair, and a user request that already clearly
authorizes that exact repair is its authorization - do not ask again for what was asked for.
New contradictory evidence invalidates the contract and stops further mutation until it is
re-frozen. `property_patch` is the default class; `instance_replacement` and
`section_reconstruction` are the two escalation classes and each requires its own contract naming
what it may rebuild.

### 3. Form one measured hypothesis

Use the symptom matrix to identify the narrowest plausible mechanism. Inspect the complete ancestor
chain around the failing node, not only the visible leaf. State the evidence and expected render
change before writing.

Apply one repair at a time. Read every geometry write back. Re-read
`componentPropertyReferences` and compare property counts after structural changes. Shared plugin
data cannot override an existing private plugin value; when private data wins, direct the user to
the exact Email Love plugin control instead of repeating a write that cannot land.

### 4. Escalate instead of patching indefinitely

If a rendered result disproves a change, revert that change on the working copy and do not repeat
the same idea elsewhere. After two failed local patches on the same section, stop patching.

Escalate by re-freezing the contract under the next class: `instance_replacement` swaps the broken
component for an intact library instance; `section_reconstruction` rebuilds only that section from
the user's own source plus the converter and authoritative render rules. Both name exactly what
they may rebuild and what they must preserve. Never flatten a section or rebuild it from memory to
make the symptom disappear.

### 5. Verify all three states

Run the verification reference. Report five states, each on its own evidence:

- `canvas desktop`: the Figma screenshot matches the authoritative desktop intent;
- `canvas mobile`: compared only when a mobile source exists - otherwise `deferred`, never
  inferred from desktop;
- `structure`: the root, tags, geometry, bindings, and content checks pass;
- `exporter desktop` and `exporter mobile`: the production renders pass, each verified
  independently. An untested viewport is `deferred`, not `pass`, and success at one viewport
  cannot compensate for failure at the other.

A repair is `fixed` only when every required state is `pass`.

If the issue was reported in a named inbox client or ESP, exporter Preview is necessary but may not
be sufficient. State when a real inbox or ESP test still belongs to the user.

## Progress contract

Before the first write, tell the user which target and copy you will repair, the suspected class of
failure, and a rough range in minutes. Update only at these boundaries:

1. Failure reproduced and baseline captured.
2. Structural repair applied and read back.
3. Desktop and mobile exporter verification completed or explicitly deferred.

Revise the estimate when the evidence changes the repair scope.

## Hand off

Return the repair report from the verification reference. Include the original and working-copy
node ids, the proven cause, every node changed, before and after evidence, the three verification
states, any private-data or inbox-test handoff, and whether the original remained untouched.

## Staying current

This is version 1.1.0 of this skill. If you have web access, check once per conversation quietly
whether a newer version exists: fetch
https://raw.githubusercontent.com/email-love/claude-skills/main/.claude-plugin/marketplace.json
and compare this skill's version to the entry named `emaillove-template-repair`. If a newer version
exists, mention it once at hand-off. claude.ai users re-upload `emaillove-template-repair.skill`
from the newest release; Claude Code plugin users run the marketplace update. If you have no web
access, skip this silently.
