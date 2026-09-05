# Email Love Claude Skills

Official [Claude](https://claude.com) skills for [Email Love](https://emaillove.com). Install them to make Claude an expert at building, repairing, and migrating emails with your Email Love design system.

## Start here

Two things are separate, and you may need both:

1. **The skills** (this repo) teach Claude the Email Love workflows.
2. **The connections** give Claude tools: the [official Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559) to read and write your Figma file (required for canvas work), and optionally the Email Love MCP (`https://mcp.emaillove.com/mcp`) for AI Import conversion, headless export verification, and campaign research. Installing a skill does not create a connection, and connecting a tool does not install a skill.

**Claude Code** (recommended, one-time, from any terminal):

```bash
claude plugin marketplace add email-love/claude-skills
claude plugin install email-love@email-love
```

**Claude.ai** (web and desktop): enable **code execution** under **Settings → Capabilities**, download the `.skill` bundles from the [latest release](https://github.com/email-love/claude-skills/releases/latest), and upload them under **Customize → Skills → + → Create skill → Upload a skill**.

Then try these, in order:

> Check whether Email Love is set up correctly. Don't change my Figma file.

> Build a welcome email in [Figma link]. I don't have an Email Love template yet. Tell me what you need.

> This Email Love template fails to export: [Figma link]. Diagnose it first and preserve the original.

The first is a non-mutating setup check: Claude reports which tools it can see and what is missing before it touches anything. Full installation detail, team setup, ESP add-ons, and Codex/ChatGPT guidance are further down this page.

## Read the skills

You do not have to install anything to read what these skills actually tell Claude to do. Each one is a single markdown file:

| Skill | What it does | Read it |
| --- | --- | --- |
| **emaillove-figma-builder** | Builds emails in Figma from your design system | [SKILL.md](plugins/email-love/skills/figma-builder/SKILL.md) |
| **emaillove-template-repair** | Diagnoses and repairs existing Email Love templates and modules | [SKILL.md](plugins/email-love/skills/template-repair/SKILL.md) |
| **emaillove-migration-audit** | Read-only audit of an existing library | [SKILL.md](plugins/email-love/skills/migration-audit/SKILL.md) |
| **emaillove-eds-converter** | Converts that library into an Email Love design system | [SKILL.md](plugins/email-love/skills/eds-converter/SKILL.md) |
| **emaillove-figma-quality-gates** | Independent acceptance audit of migration batches and reusable modules | [SKILL.md](plugins/email-love/skills/figma-quality-gates/SKILL.md) |

The converter also ships two reference documents, which are the most useful things here if you want to understand how Email Love's Figma structure actually works:

- [references/structure.md](plugins/email-love/skills/eds-converter/references/structure.md): the plugin's frame structure as ground truth, extracted from the plugin source rather than inferred. What each `mj-` tag is, how the exporter identifies a node, and the failure modes that are silent.
- [references/render-spec.md](plugins/email-love/skills/eds-converter/references/render-spec.md): the full specification for turning a design into frames the plugin exports correctly. Sizing, spacing, images, columns, component properties, and a checklist.

Prefer prose to specifications? The same material is written for humans at [help.emaillove.com](https://help.emaillove.com/plugin/ai/agents-in-figma).

## Skills

### emaillove-figma-builder

Claude builds real, export-ready emails inside your Figma file, assembled from your synced Email Love design system. It interviews you for a brief, inventories your component library, optionally pulls inspiration from Email Love's library of 500,000+ real brand emails, lets you pick components (or picks for you), and builds emails your team can review in Figma and export to your ESP through the [Email Love plugin](https://www.figma.com/community/plugin/1109792894837528369). No design system yet? It generates the structure with Email Love AI Import instead and transcribes it, so the first email doubles as the first piece of your design system.

**Requirements**

- The [official Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559) connected to Claude, with access to your file
- The Email Love Figma plugin (latest version). A synced design system in that file for the design-system path; without one it takes the AI Import path
- Optional but recommended: the free [Email Inspiration MCP](https://help.emaillove.com/plugin/ai/email-inspiration-mcp) for brand inspiration

### emaillove-template-repair

Claude diagnoses and repairs an Email Love email, reusable module, or component instance that
already exists. It reproduces the failure first, preserves campaign originals by default, and asks
before changing a shared source component that may update many instances. It changes one measured
cause at a time and verifies the canvas, structure, desktop export, and mobile export separately.
It uses the word `fixed` only when all three verification states pass.

The repair skill handles invalid template roots, exporter flattening, Outlook clipping, doubled or
missing spacing, mobile stacking and recomposition, broken buttons or images, dark-mode regressions,
private link values, and lost component-property bindings. Ordinary Figma comps route to Builder;
legacy libraries route to Migration Audit and EDS Converter.

### emaillove-migration-audit

Already have a Figma design system or template library that was not built with Email Love? This skill scopes the migration before anyone commits. It is strictly read-only: it splits your designs into a deduplicated module inventory and classifies every module (live-text convertible, editable-image candidate, hybrid, or not emailable, with any design concession named), works out whether your file is drawn at email scale, extracts your brand foundations (type ramp with email-safe fallbacks, palette, proposed theme colors, spacing, buttons), flags risks like unlicensed fonts or components living in unshared library files, and produces a shareable migration report with an effort estimate and a hand-off into conversion.

One install (see **Start here** above) carries all five skills: `/email-love:migration-audit`, `/email-love:eds-converter`, `/email-love:figma-builder`, `/email-love:template-repair`, and `/email-love:figma-quality-gates`.

Want ESP templating too? The same marketplace carries `emaillove-esp`, which installs all ten Email Love ESP skills (Braze Liquid, Customer.io Liquid, HubSpot HubL, Iterable Handlebars, Klaviyo Django, Marketo Velocity, MoEngage Jinja, Sailthru Zephyr, SFMC AMPscript, Zeta ZML) in one step, sourced at a pinned commit from their canonical home in [email-love/esp-skills](https://github.com/email-love/esp-skills):

```bash
claude plugin install emaillove-esp@email-love
```

Prefer one platform at a time? Add the esp-skills marketplace directly and install individually: `claude plugin marketplace add email-love/esp-skills`.

On Claude.ai, upload the `.skill` file from [releases](https://github.com/email-love/claude-skills/releases) instead. Using Codex or ChatGPT? See the section near the end of this page.

### emaillove-eds-converter

The conversion engine. Takes a completed migration audit and rebuilds your legacy templates as a working Email Love design system in a new Figma file: foundations first (pages, type mapping on email-safe fallbacks, buttons, spacers, assets, a marked root template), then modules in batches through a full loop of rebuild, mobile merge, componentize and add properties, and side-by-side verification, with design review gating each batch. Your source file is treated as read-only throughout. Requires the audit report from emaillove-migration-audit.

Prefer it done for you, design review included? That is Email Love Enterprise onboarding: [hello@emaillove.com](mailto:hello@emaillove.com).

## Your file does not need to be tidy

A common assumption is that a migration needs a well organised source library, and that a file drawn years ago before anyone knew the tool is a lost cause. It is not. Both cases work; what changes is which parts of the file get carried across.

The audit judges this first and says so in the report, because everything after it depends on the answer.

- **The file is authoritative about geometry.** Already drawn at real email widths, with text styles, components, variables, mobile variants, and consistent margins. The geometry is your specification, so it is preserved: widths, margins, type sizes and spacing all come across as drawn, and any deviation needs a reason.
- **The file is a reference.** Not at an email width, no styles or components, no auto layout, spacing that was eyeballed rather than decided. Here the geometry is an artefact of how the file happened to get made, not a decision worth reproducing, so it is rebuilt to email standards. What comes across is the part that was deliberate: your palette, your typefaces, your logo, your copy, and the module structure, meaning which blocks exist and in what order.
- **Mixed.** Most real libraries. What is demonstrably consistent is preserved, the rest is standardised, and every judgement of that kind is flagged for a designer rather than made silently.

The reason this matters: faithfully preserving the proportions of a file that was guessing reproduces the guesses. A migration should give you your brand on a sound email foundation, not a pixel-accurate copy of an old mockup.

## Installation

### Claude.ai (web and desktop)

Works on every plan, including Free (web and desktop, not mobile).

1. Enable **code execution** under **Settings → Capabilities** (Team/Enterprise: an org owner must enable code execution and skills in Organization Settings first).
2. Download the `.skill` file you need from the [latest release](https://github.com/email-love/claude-skills/releases/latest). Every release attaches all five skill bundles.
3. Go to **Customize → Skills → + → Create skill → Upload a skill** and upload the file.
4. Ask Claude to build an email in your Figma file.

### Claude Code (recommended: plugin marketplace)

This repo is a Claude Code plugin marketplace. Install once and the plugin loads across all your Claude Code surfaces, with automatic updates.

**From a terminal** (any shell, no interactive session needed):

```bash
claude plugin marketplace add email-love/claude-skills
claude plugin install email-love@email-love
```

One install, five skills, namespaced `email-love:`:

| Skill | What it does |
| --- | --- |
| `/email-love:migration-audit` | Read-only audit of an existing Figma design system: module inventory, verdicts, scale factor, brand foundations |
| `/email-love:eds-converter` | Converts an audited system into a working Email Love design system, in batches with design review |
| `/email-love:figma-builder` | Builds export-ready campaigns from your design system |
| `/email-love:template-repair` | Diagnoses and repairs existing Email Love templates and modules without damaging the original |
| `/email-love:figma-quality-gates` | Independent acceptance audit of migration batches and reusable modules before approval |

Update with `/plugin marketplace update email-love`. (The old per-skill installs, `emaillove-figma-builder@email-love` and friends, still resolve as deprecated single-skill plugins and keep updating; new installs should use the bundle.)

Inside an interactive `claude` terminal session, the same two commands work as `/plugin` slash commands.

**In the Claude Code desktop app:** `/plugin` is not available in chat, and the plugin browser (**+** button next to the prompt box, then **Plugins**) can only install from marketplaces it already knows; it cannot add a new one. Run the two terminal commands above once (the plugin then loads in the desktop app automatically), or add the `extraKnownMarketplaces` snippet below to `~/.claude/settings.json` and restart the app, then install from the plugin browser.

**Team setup:** add this to your project's `.claude/settings.json` so teammates get the plugin on workspace trust:

```json
{
  "extraKnownMarketplaces": {
    "email-love": {
      "source": { "source": "github", "repo": "email-love/claude-skills" }
    }
  },
  "enabledPlugins": {
    "email-love@email-love": true
  }
}
```

**Manual alternative:**

```bash
git clone https://github.com/email-love/claude-skills.git
cp -r claude-skills/plugins/email-love/skills/figma-builder ~/.claude/skills/
```

Then ask Claude Code to build an email in your Figma file.

## Using Codex or ChatGPT instead?

**OpenAI Codex** can run the same workflows. The Email Love Codex plugin contains the Builder, Template Repair, Design System Migration, and Figma Quality Gates skills (the public directory version adds the ten ESP templating skills and the Email Love MCP connection). The public plugin is the recommended customer install:

[Install Email Love from the Plugins Directory](https://chatgpt.com/plugins/plugins_6a739f43c3b48191b1281a9b2d48b409)

For development or an exact tagged version, use the Git-backed marketplace instead:

```bash
codex plugin marketplace add email-love/codex-agents --ref v4.9.0
codex plugin add email-love@email-love
```

See [email-love/codex-agents](https://github.com/email-love/codex-agents).

The public plugin is a reviewed snapshot. Pushing a Codex change to GitHub does not update directory users. A maintainer must upload the new skill bundle through the OpenAI submission portal, submit it for review, and publish the approved version. Test the published update from a new chat or Codex task.

A Figma canvas build still requires a supported Codex surface where the official Figma MCP exposes `use_figma`, `get_metadata`, and `get_screenshot`. Without `use_figma`, the plugin offers its documented plan or AI Import handoff. See [`distribution/chatgpt-gpt-instructions.md`](distribution/chatgpt-gpt-instructions.md) for the planning-only companion GPT.

## Documentation

Full walkthrough: [help.emaillove.com/plugin/ai/agents-in-figma](https://help.emaillove.com/plugin/ai/agents-in-figma)

Related guides:

- [Build with the Figma MCP](https://help.emaillove.com/plugin/ai/agents-in-figma)
- [Email Creation MCP](https://help.emaillove.com/plugin/ai/email-creation-mcp)
- [Email Inspiration MCP](https://help.emaillove.com/plugin/ai/email-inspiration-mcp)

## Security and data handling

Most of what these skills do stays inside your own Figma file. The routes that can send data
outside it - conversion, the optional Email Love MCP's export and preview tools, and the research
tools - are enumerated one by one in [SECURITY.md](SECURITY.md): what each sends, when it fires,
and how to avoid it for sensitive material.

## Support

Email [hello@emaillove.com](mailto:hello@emaillove.com) and we'll respond within a business day.
