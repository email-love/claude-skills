# Security and data handling

These skills build and convert emails inside your own Figma file. Most of what they do stays
local to that file. One route sends data to an Email Love service, and this document explains
exactly what, when, and how to avoid it.

## What leaves your environment, and when

There is exactly one outbound path: the **conversion route** (the builder's Path B, and the
converter's module conversion). It is used only when there is no existing component to instance,
so it never fires for a customer who already has a synced Email Love design system.

When it fires, the skill:

1. Renders the design region as a PNG.
2. Sends that PNG, plus a small `promptInputs` object (text content and node dimensions it read
   from the frame) and optionally a layer tree, to the Email Love design-converter:

   ```
   https://design-converter.andy-30d.workers.dev
   ```

3. Receives back a structured MJML document describing email structure, and rebuilds it in Figma.

Nothing else is transmitted. The audit never uses this route at all: it only reads and
screenshots your file, and writes a local report.

## What is NOT sent

- The skills do not send your Figma file, your account, your credentials, or your API keys.
- The audit is strictly read-only and transmits nothing off your machine beyond the screenshots
  the conversion route would send, which it does not use.
- The converter builds into a separate target file and never modifies your source file.

## Authentication and cache

- The conversion request authenticates as an anonymous free user (an empty bearer token with an
  `X-Auth-Provider: gumroad` header). No account identity is attached.
- The service caches a conversion by a hash of the screenshot, so re-sending the same design
  returns the previous result without a new model call. A skill can bypass this with a
  `nocache=1` query parameter (skips both the cache read and write) when a design must not be
  cached at all.

## What we cannot assert here

This document describes the request the skills make. It does not speak for the service's own
retention, logging, or deletion policy, which lives with the operator of the worker. If your
material is regulated or contractually restricted, treat any external send as external and get
that policy in writing before using the conversion route on it.

## Avoiding the conversion route entirely

If you cannot send design renders outside your environment:

- **Have a design system first.** With synced Email Love components, the builder instances them
  and never converts. This is the recommended path for sensitive work.
- **Use the plugin's own AI Import by hand** for the one-off case, so the send is a deliberate
  action you take rather than an automated step. See
  [AI Import](https://help.emaillove.com/plugin/ai/ai-import).
- **Strip sensitive content before converting.** Replace real copy and imagery with placeholders,
  convert to get the structure, then restore the real content locally.

## The source file stays read-only

Throughout an audit and a migration, your existing file is a source to read, never a place to
write. Screenshots and asset exports are reads. Every write goes to a separate target file. If a
migration goes wrong, your originals are exactly where they were.

## Reporting

Found a security issue in these skills or the conversion route? Email
[hello@emaillove.com](mailto:hello@emaillove.com).
