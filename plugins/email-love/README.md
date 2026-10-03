# Email Love

Official [Email Love](https://emaillove.com) plugin for Claude. It teaches Claude to build, repair, audit, and migrate export-ready emails and design systems inside your own Figma file, using the Email Love Figma plugin's frame structure, so what Claude builds exports to any ESP.

## What is inside

Five skills, namespaced `email-love:` in Claude Code:

| Skill | What it does |
| --- | --- |
| `figma-builder` | Builds export-ready campaigns in Figma from your synced Email Love design system |
| `template-repair` | Diagnoses and repairs existing Email Love templates and modules without damaging the original |
| `migration-audit` | Read-only audit of an existing design system or template library before migration |
| `eds-converter` | Converts an audited library into a working Email Love design system, in batches with design review |
| `figma-quality-gates` | Independent acceptance audit of migration batches and reusable modules before approval |

Each skill is a single Markdown file you can read before you install anything. The converter and the quality gates also ship reference documents and two small Python scripts that run locally on JSON you give them.

## What you need

- The [official Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559) connected to Claude, with access to your file. Required for any canvas work.
- The Email Love Figma plugin, latest version, with a synced design system in the file. Without one, the builder takes the AI Import path and generates the structure first.
- Optional: the Email Love MCP (`https://mcp.emaillove.com/mcp`), connected and authenticated by you, for AI Import conversion, headless export verification, and brand inspiration.

Try it with: "Check whether Email Love is set up correctly. Don't change my Figma file." Claude reports which tools it can see and what is missing before it touches anything.

## What the plugin connects to and sends

Nothing runs in the background. Every route below fires only while a skill is working on your request.

- **Figma** (`mcp.figma.com`): reads and writes your Figma file through the official Figma MCP, under your Figma account.
- **Email Love MCP** (`mcp.emaillove.com`), only if you connect it: design conversion, export preview, and inspiration search, under your Email Love account.
- **Email Love design converter** (`convert.emaillove.com`), fallback when the MCP is not connected: a PNG or JPEG render of the design region plus its text content and dimensions, sent anonymously, so Claude can transcribe a design into Email Love frames.
- **Version check** (`raw.githubusercontent.com/email-love/claude-skills`): once per conversation, each skill may fetch this plugin's public `marketplace.json` to tell you when a newer version exists. Nothing about you is sent.
- **Your own ESP or file store, during a migration audit only**: the `migration-audit` skill can read templates from a source you choose (a local folder, Google Drive, SharePoint, Klaviyo, Marketo, Customer.io, Brevo, Kit, ActiveCampaign, Iterable, Omnisend, or HubSpot) through the MCP, CLI, or API you connect and authenticate yourself. The skill never reads credentials from your environment or files; where a value is needed, it asks you in the session.

The plugin stores no credentials and keeps no data outside your Figma file and your conversation. The full route-by-route description, including what each request contains and how to avoid the optional ones, is in [SECURITY.md](https://github.com/email-love/claude-skills/blob/main/SECURITY.md).

## Support and license

Documentation: [help.emaillove.com](https://help.emaillove.com/plugin/ai/agents-in-figma). Questions: [hello@emaillove.com](mailto:hello@emaillove.com). Source and changelog: [github.com/email-love/claude-skills](https://github.com/email-love/claude-skills). MIT License.
