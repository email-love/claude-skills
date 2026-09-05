# Security and data handling

These skills build, convert, audit, and repair emails inside your own Figma file. This document
lists every route through which data can leave your environment, what each one sends, when it
fires, and how to avoid the ones you do not want. Several routes are optional: which ones apply
to you depends on which connections you have added.

## The routes, one by one

### 1. Your Claude host (always)

The skills run inside Claude (claude.ai, Claude Code, or Cowork). Everything Claude reads while
working - file contents, screenshots it takes, your messages - is processed by Anthropic under
your own Claude plan's data terms. That is a property of using Claude, not of these skills.

### 2. The Figma connection (always, for canvas work)

Reading and writing your Figma file goes through the official remote Figma MCP
(`mcp.figma.com`), authenticated with your own Figma account. Screenshots and node reads are
Figma API calls; they travel between Claude and Figma.

### 3. The direct conversion route (Path B fallback, optional)

When the builder or converter has no existing component to instance and the Email Love MCP is
not connected, it can send a design render to the Email Love design-converter:

```
https://convert.emaillove.com
```

What is sent: a PNG or JPEG render of the design region, a small `promptInputs` object (text
content and node dimensions read from the frame), and optionally a plain-text layer tree. The
request authenticates as an anonymous free user; no account identity is attached. The service
caches conversions by a hash of the screenshot; a `nocache=1` query parameter skips the cache
read and write when a design must not be cached.

### 4. The Email Love MCP (optional, connected and authenticated by you)

If you add `https://mcp.emaillove.com/mcp` as a connection, its tools run under your Email Love
account (OAuth or license key). Depending on which tools a skill uses:

- `emaillove_convert_design` sends the conversion the same place route 3 does, but authenticated
  and server-side: you pass a file key and node id, and the SERVER renders the node through the
  Figma API and forwards it to the converter.
- `emaillove_export_figma` reads your Figma file over the Figma REST API server-side, compiles
  it through the production Email Love export pipeline, and HOSTS the images it extracts on
  Email Love's CDN so the exported HTML can reference them. The compiled HTML is stored briefly
  under a preview token so a preview URL works.
- `emaillove_preview_email` renders compiled HTML to desktop and mobile screenshots server-side.
- The research tools (`search_emails`, `fetch_email`, brand and journey tools) only QUERY the
  public emaillove.com library; they send your search terms, not your designs.

### 5. The Email Love Figma plugin (your own action)

Exporting or previewing through the plugin itself, including its manual AI Import, sends your
design to the same Email Love services under your plugin account. Manual AI Import makes the
external send a deliberate action you take; it is not an offline alternative - it uses the same
external conversion service as route 3.

## What is NOT sent

- The skills never send your Figma credentials, Claude credentials, or API keys anywhere.
- The audit is strictly read-only on your source file and writes a local report; it uses none of
  routes 3-5 by itself.
- No route sends your whole Figma file. Conversion sends a render of the selected region;
  headless export reads the selected template's nodes.

## What we cannot assert here

This document describes the requests the skills make. It does not speak for each service's
retention, logging, or deletion policy: the converter and MCP are operated by Email Love, Figma
by Figma, and Claude by Anthropic. Those policies are theirs, and where they are unknown to this
document they remain unknown - no guarantee is implied. If your material is regulated or
contractually restricted, treat every route above as an external transfer and get the relevant
policy in writing first.

## Avoiding external conversion entirely

If you cannot send design renders outside your environment:

- **Have a design system first.** With synced Email Love components, the builder instances them
  and never converts. This is the recommended path for sensitive work.
- **Strip sensitive content before converting.** Replace real copy and imagery with placeholders,
  convert to get the structure, then restore the real content locally.
- Note that skipping automation does not avoid the service: the plugin's manual AI Import is the
  same external conversion, initiated by hand.

## The source file stays read-only

Throughout an audit and a migration, your existing file is a source to read, never a place to
write. Screenshots and asset exports are reads. Every write goes to a separate target file. If a
migration goes wrong, your originals are exactly where they were.

## Reporting

Found a security issue in these skills or the services they call? Email
[hello@emaillove.com](mailto:hello@emaillove.com).
