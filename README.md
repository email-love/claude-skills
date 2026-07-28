# Email Love Claude Skills

Official [Claude](https://claude.com) skills for [Email Love](https://emaillove.com) — install them to make Claude an expert at building emails with your Email Love design system.

## Skills

### emaillove-figma-builder

Claude builds real, export-ready emails inside your Figma file, assembled from your synced Email Love design system. It interviews you for a brief, inventories your component library, optionally pulls inspiration from Email Love's library of 500,000+ real brand emails, lets you pick components (or picks for you), and builds emails your team can review in Figma and export to your ESP through the [Email Love plugin](https://www.figma.com/community/plugin/1109792894837528369).

**Requirements**

- The [official Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559) connected to Claude, with access to your file
- The Email Love Figma plugin (latest version) and a synced design system in that file
- Optional but recommended: the free [Email Inspiration MCP](https://help.emaillove.com/plugin/ai/email-inspiration-mcp) for brand inspiration

## Installation

### Claude.ai (web and desktop)

1. Download `emaillove-figma-builder.skill` from the [latest release](https://github.com/email-love/claude-skills/releases/latest).
2. In Claude, open **Settings → Capabilities → Skills** and upload the file.
3. Ask Claude to build an email in your Figma file.

### Claude Code (recommended: plugin marketplace)

This repo is a Claude Code plugin marketplace. Install once and the plugin loads across all your Claude Code surfaces, with automatic updates.

**From a terminal** (any shell, no interactive session needed):

```bash
claude plugin marketplace add email-love/claude-skills
claude plugin install emaillove-figma-builder@email-love
```

Inside an interactive `claude` terminal session, the same two commands work as `/plugin` slash commands.

**In the Claude Code desktop app:** `/plugin` is not available in chat. Click the **+** button next to the prompt box, then **Plugins**, to open the plugin browser, or run the terminal commands above once.

**Team setup:** add this to your project's `.claude/settings.json` so teammates get the plugin on workspace trust:

```json
{
  "extraKnownMarketplaces": {
    "email-love": {
      "source": { "source": "github", "repo": "email-love/claude-skills" }
    }
  },
  "enabledPlugins": {
    "emaillove-figma-builder@email-love": true
  }
}
```

**Manual alternative:**

```bash
git clone https://github.com/email-love/claude-skills.git
cp -r claude-skills/skills/emaillove-figma-builder ~/.claude/skills/
```

Then ask Claude Code to build an email in your Figma file.

## Documentation

Full walkthrough: [help.emaillove.com/plugin/ai/agents-in-figma](https://help.emaillove.com/plugin/ai/agents-in-figma)

Related guides:

- [Build with the Figma MCP](https://help.emaillove.com/plugin/ai/agents-in-figma)
- [Email Creation MCP](https://help.emaillove.com/plugin/ai/email-creation-mcp)
- [Email Inspiration MCP](https://help.emaillove.com/plugin/ai/email-inspiration-mcp)

## Support

Email [hello@emaillove.com](mailto:hello@emaillove.com) and we'll respond within a business day.
