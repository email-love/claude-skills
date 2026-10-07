// Email Love documentation kit, for use_figma.
// Paste this whole file into a use_figma call, then append ONE call at the bottom:
//   return await buildCover({...})          for the Cover
//   return await buildScaffoldPage({...})   for Getting Started, Foundations, Type, Buttons
//   return await buildModulePage({...})     for each component category page
//   return await buildCampaignsPage({...})  for Campaigns
// The layout, type scale and components are fixed by references/documentation.md. Change content,
// not geometry. Every color on a doc page binds to the library's own semantic variables; the
// exceptions (cover glows, the dark-mode mock, the page canvas) are listed in documentation.md.

const DOC = {
  family: 'Arimo',            // set to the library's body family (the one the Type page specimens use)
  display: 'League Spartan',  // cover headline only; falls back to DOC.family when not installed
  canvas: '#F5F5F5',          // page background behind the boards (page backgrounds cannot bind variables)
  tokens: {                   // semantic variable name, fallback hex used only if the variable is missing
    ink:  ['color/text/primary',    '#000000'],
    mute: ['color/text/muted',      '#767676'],
    inv:  ['color/text/inverse',    '#FFFFFF'],
    bg:   ['color/bg/content',      '#FFFFFF'],
    sub:  ['color/bg/subtle',       '#F7F7F7'],
    blk:  ['color/bg/brand',        '#000000'],
    line: ['color/border/hairline', '#E6E6E6'],
  },
};

// ---------- primitives ----------
let VARS = [];
const HEX = h => ({ r: parseInt(h.slice(1, 3), 16) / 255, g: parseInt(h.slice(3, 5), 16) / 255, b: parseInt(h.slice(5, 7), 16) / 255 });
const MISSING = new Set();
function P(k) {
  const [name, hex] = DOC.tokens[k]; const v = VARS.find(x => x.name === name);
  const paint = { type: 'SOLID', color: HEX(hex) };
  if (!v) { MISSING.add(name); return paint; }
  return figma.variables.setBoundVariableForPaint(paint, 'color', v);
}
function T(s, { size = 14, bold = false, color = 'ink', lh = 150, ls = 0, upper = false, family = null } = {}) {
  const t = figma.createText(); t.fontName = { family: family || DOC.family, style: bold ? 'Bold' : 'Regular' };
  t.characters = s; t.fontSize = size; t.lineHeight = { unit: 'PERCENT', value: lh };
  t.letterSpacing = { unit: 'PIXELS', value: ls }; if (upper) t.textCase = 'UPPER'; t.fills = [P(color)]; return t;
}
// Auto layout frame. Primary axis HUGS by default: createAutoLayout + resize otherwise leaves it FIXED.
function AL(dir, { gap = 0, pad = [0, 0, 0, 0], fill = null, name = 'Frame', align = 'MIN', cross = 'MIN' } = {}) {
  const f = figma.createAutoLayout(dir, { name, itemSpacing: gap });
  [f.paddingTop, f.paddingRight, f.paddingBottom, f.paddingLeft] = pad;
  f.fills = fill ? [P(fill)] : []; f.primaryAxisAlignItems = align; f.counterAxisAlignItems = cross;
  f.primaryAxisSizingMode = 'AUTO'; f.counterAxisSizingMode = 'AUTO'; f.clipsContent = false; return f;
}
// appendChild returns nothing in the Plugin API; add() returns the child.
function add(p, c, fill = false) {
  p.appendChild(c);
  if (fill) { c.layoutSizingHorizontal = 'FILL'; if (c.type === 'TEXT') c.textAutoResize = 'HEIGHT'; }
  return c;
}
function fixedW(n, w) {
  if (n.type === 'TEXT') { n.resize(w, n.height); n.textAutoResize = 'HEIGHT'; }
  else if (n.layoutMode === 'HORIZONTAL') { n.resize(w, n.height); n.primaryAxisSizingMode = 'FIXED'; n.counterAxisSizingMode = 'AUTO'; }
  else { n.resize(w, n.height); n.counterAxisSizingMode = 'FIXED'; n.primaryAxisSizingMode = 'AUTO'; }
  return n;
}
function col(name, w, gap) { const f = AL('VERTICAL', { gap, name }); f.resize(w, 10); f.counterAxisSizingMode = 'FIXED'; f.primaryAxisSizingMode = 'AUTO'; return f; }
function rule(p, k = 'line') { const r = figma.createRectangle(); r.name = 'Hairline'; r.resize(10, 1); r.fills = [P(k)]; p.appendChild(r); r.layoutSizingHorizontal = 'FILL'; return r; }
function box(name, w, h, k) { const r = figma.createRectangle(); r.name = name; r.resize(w, h); r.fills = k ? [P(k)] : []; return r; }
const eyebrow = (p, s, color = 'mute') => add(p, T(s, { size: 12, bold: true, ls: 2.5, upper: true, color }));
const label = (p, s, color = 'mute') => add(p, T(s, { size: 12, bold: true, ls: 2, upper: true, color }));
const caption = (s, color = 'mute') => T(s, { size: 11, bold: true, ls: 1.2, upper: true, color });
const para = (p, s, o = {}) => add(p, T(s, { size: 15, lh: 155, ...o }), true);
const note = (p, s) => add(p, T(s, { size: 14, lh: 155, color: 'mute' }), true);

// ---------- content blocks (each takes the section's content column) ----------
const KIT = {
  para, note,
  // Header row in small caps, then rows split by hairlines. rows: arrays of strings. widths: px per column except the last, which fills.
  table(p, head, rows, widths) {
    const t = AL('VERTICAL', { name: 'Table' }); add(p, t, true);
    const line = (cells, isHead) => {
      const r = AL('HORIZONTAL', { gap: 20, pad: [12, 0, 12, 0], name: isHead ? 'Head' : cells[0] }); add(t, r, true);
      cells.forEach((c, i) => {
        const n = isHead ? caption(c) : T(c, { size: 14, bold: i === 0, color: i === 0 ? 'ink' : (i === cells.length - 1 && cells.length > 2 ? 'mute' : 'ink') });
        r.appendChild(n);
        if (i === cells.length - 1) { n.layoutSizingHorizontal = 'FILL'; n.textAutoResize = 'HEIGHT'; } else fixedW(n, (widths && widths[i]) || 120);
      });
    };
    if (head) { line(head, true); }
    rule(t, 'ink');
    for (const r of rows) { line(r, false); rule(t); }
    return t;
  },
  // Big-number tiles. items: [[value, label], ...] or [[value, label, detail], ...]
  stats(p, items) {
    const row = AL('HORIZONTAL', { gap: 24, name: 'Stats' }); add(p, row, true);
    const vals = [];
    for (const [v, l, d] of items) {
      const c = AL('VERTICAL', { gap: 8, pad: [24, 24, 24, 24], fill: 'sub', name: 'Stat / ' + l }); add(row, c);
      c.layoutSizingHorizontal = 'FILL';
      vals.push([c, add(c, T(v, { size: 48, bold: true, lh: 100, ls: -1 }))]);
      add(c, T(l, { size: 11, bold: true, ls: 1.2, upper: true, color: 'ink' }), true);
      if (d) add(c, T(d, { size: 13, color: 'mute', lh: 150 }), true);
    }
    // A value never wraps: when one ("24 / 40 / 48") is too wide for its tile, every value in the row steps down together.
    const size = Math.max(20, Math.min(48, ...vals.map(([c, n]) => Math.floor(48 * (c.width - 48) / n.width))));
    for (const [, n] of vals) n.fontSize = size;
    return row;
  },
  // Numbered steps. items: [[title, detail], ...]
  steps(p, items) {
    const s = AL('VERTICAL', { name: 'Steps' }); add(p, s, true); rule(s, 'ink');
    items.forEach(([title, detail], i) => {
      const r = AL('HORIZONTAL', { gap: 24, pad: [20, 0, 20, 0], name: 'Step ' + (i + 1) }); add(s, r, true);
      fixedW(add(r, T(String(i + 1).padStart(2, '0'), { size: 22, bold: true, lh: 120 })), 48);
      const b = AL('VERTICAL', { gap: 6, name: 'Body' }); add(r, b); b.layoutSizingHorizontal = 'FILL';
      add(b, T(title, { size: 16, bold: true, lh: 140 }), true); if (detail) add(b, T(detail, { size: 14, color: 'mute', lh: 155 }), true);
      rule(s);
    });
    return s;
  },
  // Checklist: one row per item with an empty check box. items: [string]
  checklist(p, items) {
    const s = AL('VERTICAL', { gap: 16, name: 'Checklist' }); add(p, s, true);
    for (const it of items) {
      const r = AL('HORIZONTAL', { gap: 14, name: 'Check', cross: 'MIN' }); add(s, r, true);
      const b = box('Box', 16, 16, null); b.strokes = [P('ink')]; b.strokeWeight = 1.5; b.strokeAlign = 'INSIDE'; r.appendChild(b);
      add(r, T(it, { size: 15, lh: 135 }), true);
    }
    return s;
  },
  // Bullet list. items: [string]
  bullets(p, items) {
    const s = AL('VERTICAL', { gap: 10, name: 'Bullets' }); add(p, s, true);
    for (const it of items) {
      const r = AL('HORIZONTAL', { gap: 12, name: 'Bullet', cross: 'CENTER' }); add(s, r, true);
      r.appendChild(box('Dot', 6, 6, 'ink')); add(r, T(it, { size: 15 }), true);
    }
    return s;
  },
  // Two panels: Do on the subtle fill, Don't on the brand fill.
  doDont(p, dos, donts, heads = ['Do', "Don't"]) {
    const row = AL('HORIZONTAL', { gap: 24, name: 'Do and dont' }); add(p, row, true);
    [[heads[0], dos, 'sub', 'ink'], [heads[1], donts, 'blk', 'inv']].forEach(([h, items, fill, ink]) => {
      const c = AL('VERTICAL', { gap: 14, pad: [28, 28, 28, 28], fill, name: h }); add(row, c); c.layoutSizingHorizontal = 'FILL';
      add(c, T(h, { size: 12, bold: true, ls: 2, upper: true, color: ink }));
      for (const it of items) add(c, T(it, { size: 15, lh: 150, color: ink }), true);
    });
    return row;
  },
  // Color swatches. items: [{name, variable, hex, use}]. Binds the chip to the variable itself.
  swatches(p, items) {
    const row = AL('HORIZONTAL', { gap: 16, name: 'Swatches' }); add(p, row, true); row.layoutWrap = 'WRAP'; row.counterAxisSpacing = 24;
    for (const it of items) {
      const c = AL('VERTICAL', { gap: 10, name: 'Swatch / ' + it.name }); add(row, c); fixedW(c, 140);
      const chip = box('Chip', 140, 120, null);
      const v = VARS.find(x => x.name === it.variable);
      chip.fills = [v ? figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: HEX(it.hex) }, 'color', v) : { type: 'SOLID', color: HEX(it.hex) }];
      if (!v) MISSING.add(it.variable);
      chip.strokes = [P('line')]; chip.strokeWeight = 1; chip.strokeAlign = 'INSIDE'; c.appendChild(chip);
      add(c, T(it.hex.toUpperCase(), { size: 14, bold: true }), true);
      add(c, T(it.name + (it.use ? '\n' + it.use : ''), { size: 12, color: 'mute', lh: 150 }), true);
    }
    return row;
  },
  // Semantic token table with a small chip per row. items: [{token, points, hex, use}]
  tokens(p, items) {
    const t = AL('VERTICAL', { name: 'Tokens' }); add(p, t, true);
    const head = AL('HORIZONTAL', { gap: 20, pad: [12, 0, 12, 52], name: 'Head' }); add(t, head, true);
    [['Token', 200], ['Points at', 120], ['Hex', 90], ['Use for', 0]].forEach(([h, w]) => { const n = caption(h); head.appendChild(n); if (w) fixedW(n, w); else { n.layoutSizingHorizontal = 'FILL'; n.textAutoResize = 'HEIGHT'; } });
    rule(t, 'ink');
    for (const it of items) {
      const r = AL('HORIZONTAL', { gap: 20, pad: [10, 0, 10, 0], cross: 'CENTER', name: it.token }); add(t, r, true);
      const chip = box('Chip', 32, 32, null); const v = VARS.find(x => x.name === it.token);
      chip.fills = [v ? figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: HEX(it.hex) }, 'color', v) : { type: 'SOLID', color: HEX(it.hex) }];
      if (!v) MISSING.add(it.token);
      chip.strokes = [P('line')]; chip.strokeWeight = 1; chip.strokeAlign = 'INSIDE'; r.appendChild(chip);
      fixedW(add(r, T(it.token, { size: 14, bold: true })), 200);
      fixedW(add(r, T(it.points, { size: 14, color: 'mute' })), 120);
      fixedW(add(r, T(it.hex.toUpperCase(), { size: 14 })), 90);
      add(r, T(it.use, { size: 14, color: 'mute' }), true);
      rule(t);
    }
    return t;
  },
  // Spacing bars drawn to scale. items: [{token, px, use}]
  spacing(p, items) {
    const t = AL('VERTICAL', { name: 'Spacing' }); add(p, t, true); rule(t, 'ink');
    for (const it of items) {
      const r = AL('HORIZONTAL', { gap: 20, pad: [12, 0, 12, 0], cross: 'CENTER', name: it.token }); add(t, r, true);
      fixedW(add(r, T(it.token, { size: 14, bold: true })), 200);
      fixedW(add(r, T(it.px + 'px', { size: 14, color: 'mute' })), 60);
      const lane = AL('HORIZONTAL', { name: 'Lane', cross: 'CENTER' }); add(r, lane); fixedW(lane, 260);
      lane.appendChild(box('Bar', Math.min(260, Math.max(2, it.px * 4)), 16, 'blk'));
      if (it.use) add(r, T(it.use, { size: 14, color: 'mute' }), true);
      rule(t);
    }
    return t;
  },
  // Type specimens, largest first. items: [{style: 'Title', sample, caption}]. Applies the real text style.
  async specimens(p, items) {
    const styles = await figma.getLocalTextStylesAsync();
    const t = AL('VERTICAL', { name: 'Specimens' }); add(p, t, true); rule(t, 'ink');
    for (const it of items) {
      const r = AL('VERTICAL', { gap: 12, pad: [28, 0, 28, 0], name: it.style }); add(t, r, true);
      const top = AL('HORIZONTAL', { gap: 16, name: 'Meta' }); add(r, top, true);
      add(top, caption(it.style)); const cp = add(top, T(it.caption, { size: 12, color: 'mute' })); cp.layoutSizingHorizontal = 'FILL'; cp.textAutoResize = 'HEIGHT'; cp.textAlignHorizontal = 'RIGHT';
      const s = T(it.sample, {}); const st = styles.find(x => x.name === it.style);
      if (st) { await figma.loadFontAsync(st.fontName); await s.setTextStyleIdAsync(st.id); } else MISSING.add('text style ' + it.style);
      add(r, s, true); rule(t);
    }
    return t;
  },
  // Grey panel for an aside or a font note.
  panel(p, title, lines) {
    const c = AL('VERTICAL', { gap: 12, pad: [32, 32, 32, 32], fill: 'sub', name: 'Panel / ' + (title || 'Note') }); add(p, c, true);
    if (title) add(c, T(title, { size: 16, bold: true, lh: 140 }), true);
    for (const l of lines) add(c, T(l, { size: 14, lh: 155 }), true);
    return c;
  },
  // Nested anatomy diagram. layers outermost first: [[name, tag, note]]; leaves: ['Text block', ...].
  // Each layer is drawn inside the one before it, so long tag names stack and never truncate.
  anatomy(p, layers, leaves) {
    let parent = p, outer = null;
    layers.forEach(([name, tag, nt], i) => {
      const f = AL('VERTICAL', { gap: 14, pad: [24, 24, 24, 24], fill: i % 2 ? 'sub' : 'bg', name: 'Layer / ' + tag });
      f.strokes = [P('line')]; f.strokeWeight = 1; f.strokeAlign = 'INSIDE';
      add(parent, f, true); if (!outer) outer = f;
      const h = AL('HORIZONTAL', { gap: 12, name: 'Label', cross: 'CENTER' }); add(f, h, true);
      label(h, name, 'ink'); add(h, T(tag, { size: 12, color: 'mute' }));
      if (nt) add(f, T(nt, { size: 13, color: 'mute', lh: 150 }), true);
      parent = f;
    });
    if (leaves && leaves.length) {
      const row = AL('HORIZONTAL', { gap: 12, name: 'Leaves' }); add(parent, row, true);
      for (const l of leaves) {
        const c = AL('VERTICAL', { pad: [16, 16, 16, 16], fill: layers.length % 2 ? 'sub' : 'bg', name: 'Leaf / ' + l, cross: 'CENTER' });
        c.strokes = [P('line')]; c.strokeWeight = 1; c.strokeAlign = 'INSIDE';
        add(row, c); c.layoutSizingHorizontal = 'FILL'; add(c, caption(l, 'ink'));
      }
    }
    return outer;
  },
  // Body and content width, drawn to scale. o: {body, content, margin, mobileBody, mobileMargin, note}
  layout(p, o) {
    const row = AL('HORIZONTAL', { gap: 32, name: 'Layout' }); add(p, row, true);
    const draw = (title, body, margin, scale) => {
      const c = AL('VERTICAL', { gap: 10, name: title }); add(row, c);
      add(c, caption(title));
      const w = Math.round(body * scale), m = Math.round(margin * scale);
      const outer = AL('HORIZONTAL', { pad: [0, m, 0, m], fill: 'sub', name: 'Body ' + body, cross: 'CENTER' }); add(c, outer); outer.resize(w, 120); outer.primaryAxisSizingMode = 'FIXED'; outer.counterAxisSizingMode = 'FIXED';
      const inner = AL('HORIZONTAL', { fill: 'blk', name: 'Content', align: 'CENTER', cross: 'CENTER' }); add(outer, inner); inner.layoutSizingHorizontal = 'FILL'; inner.layoutSizingVertical = 'FILL';
      add(inner, T((body - 2 * margin) + ' content', { size: 13, bold: true, color: 'inv' }));
      add(c, T(`${body}px body, ${margin}px side margins`, { size: 13, color: 'mute' }));
    };
    draw('Desktop', o.body, o.margin, 1);
    if (o.mobileBody) draw(`Mobile (${o.mobileBody} viewport)`, o.mobileBody, o.mobileMargin, Math.min(1, (924 - 32 - o.body) / o.mobileBody));
    if (o.note) note(p, o.note);
    return row;
  },
  // Light and dark mock emails drawn from the root's theme values (plugin data, not variables, so hex here is expected).
  // t: {light: {page, content, text, button, buttonText}, dark: {...}, headline, body, cta}
  themePair(p, t) {
    const row = AL('HORIZONTAL', { gap: 24, name: 'Theme pair' }); add(p, row, true);
    for (const [k, title] of [['light', 'Light'], ['dark', 'Dark']]) {
      const th = t[k]; const solid = h => [{ type: 'SOLID', color: HEX(h) }];
      const c = AL('VERTICAL', { gap: 10, name: title }); add(row, c); c.layoutSizingHorizontal = 'FILL';
      add(c, caption(title + (k === 'dark' ? ' (as Apple Mail renders it)' : '')));
      const pg = AL('VERTICAL', { pad: [32, 32, 32, 32], name: 'Page' }); pg.fills = solid(th.page); add(c, pg, true);
      const ct = AL('VERTICAL', { gap: 14, pad: [28, 28, 28, 28], name: 'Content' }); ct.fills = solid(th.content); add(pg, ct, true);
      const tx = (s, o) => { const n = T(s, o); n.fills = solid(th.text); return add(ct, n, true); };
      tx(t.headline, { size: 24, bold: true, lh: 120 }); tx(t.body, { size: 14, lh: 150 });
      const b = AL('HORIZONTAL', { pad: [14, 20, 14, 20], name: 'Button', align: 'CENTER', cross: 'CENTER' }); b.fills = solid(th.button); add(ct, b, true);
      const bl = T(t.cta, { size: 12, bold: true, ls: 1.2, upper: true }); bl.fills = solid(th.buttonText); b.appendChild(bl);
    }
    return row;
  },
  // A live instance of a component beside a bullet list of its measurements (Buttons 4.2).
  async specimen(p, compId, bullets) {
    const row = AL('HORIZONTAL', { gap: 40, name: 'Specimen', cross: 'CENTER' }); add(p, row, true);
    const comp = await figma.getNodeByIdAsync(compId);
    const target = comp.type === 'COMPONENT_SET' ? comp.defaultVariant : comp;
    const inst = target.createInstance(); row.appendChild(inst);
    const b = AL('VERTICAL', { name: 'Measurements' }); add(row, b); b.layoutSizingHorizontal = 'FILL'; KIT.bullets(b, bullets);
    return row;
  },
  // Status chip. Only write "Verified" when the module's acceptance matrix is all pass.
  badge(p, s) { const b = AL('HORIZONTAL', { pad: [6, 12, 6, 12], fill: 'blk', name: 'Status', cross: 'CENTER' }); add(b, T(s, { size: 11, bold: true, ls: 1.2, upper: true, color: 'inv' })); p.appendChild(b); return b; },
};

async function setup(pageId) {
  const page = await figma.getNodeByIdAsync(pageId); await figma.setCurrentPageAsync(page);
  for (const s of ['Regular', 'Bold']) await figma.loadFontAsync({ family: DOC.family, style: s });
  VARS = await figma.variables.getLocalVariablesAsync('COLOR');
  page.backgrounds = [{ type: 'SOLID', color: HEX(DOC.canvas) }];
  return page;
}
function pageHeader(parent, { eyebrow: eb, title, lede, intro }, w) {
  const h = col('Page header', w, 24); parent.appendChild(h);
  eyebrow(h, eb); add(h, T(title, { size: 72, bold: true, lh: 100, ls: -2 }), true);
  if (lede) add(h, fixedW(T(lede, { size: 22, color: 'mute', lh: 145 }), 880));
  if (intro) add(h, fixedW(T(intro, { size: 15, lh: 155 }), 880));
  rule(h, 'ink'); return h;
}
// Top-level nodes that are not ours and not components: reported, never deleted.
function strays(page, ours) {
  return page.children.filter(n => !ours.has(n.id) && n.type !== 'COMPONENT' && n.type !== 'COMPONENT_SET')
    .map(n => ({ id: n.id, type: n.type, name: n.name }));
}
function placeStage(page, name, x, y, w, h, index) {
  const st = figma.createFrame(); st.name = name; st.fills = [P('sub')]; st.clipsContent = false;
  st.resize(w, h); page.insertChild(index, st); st.x = x; st.y = y; return st;
}

// ---------- cover ----------
// cfg: { pageId, brand: 'Prada', meta: 'v1.0   ·   600px email   ·   October 2026', note: '6 modules, 6 verified', rootId }
// rootId: the Campaigns root. Its rendered image sits on the right as the cover preview.
async function buildCover(cfg) {
  const page = await setup(cfg.pageId);
  for (const n of [...page.children]) if (n.name === 'Cover' && n.type === 'FRAME') n.remove();
  let display = DOC.display;
  try { await figma.loadFontAsync({ family: display, style: 'Bold' }); } catch (e) { display = DOC.family; }
  const W = 1280, H = 720;
  const cover = figma.createFrame(); cover.name = 'Cover'; cover.resize(W, H); cover.fills = [P('blk')]; cover.clipsContent = true;
  page.insertChild(0, cover); cover.x = 0; cover.y = 0;
  // Two blurred glows, the Email Love cover signature. Fixed Email Love colors, not brand tokens (documentation.md 1).
  for (const [hex, x, y] of [['#2BA3D6', -260, -220], ['#EB3656', 760, 360]]) {
    const g = figma.createEllipse(); g.name = 'Glow'; g.resize(720, 720); g.fills = [{ type: 'SOLID', color: HEX(hex) }]; g.opacity = 0.45;
    g.effects = [{ type: 'LAYER_BLUR', blurType: 'NORMAL', radius: 260, visible: true }]; cover.appendChild(g); g.x = x; g.y = y;
  }
  const left = col('Title block', 640, 0); cover.appendChild(left); left.x = 96;
  const mark = AL('HORIZONTAL', { gap: 12, name: 'Email Love', cross: 'CENTER' }); add(left, mark);
  const heart = figma.createNodeFromSvg('<svg width="34" height="30" viewBox="0 0 34 30" xmlns="http://www.w3.org/2000/svg"><path d="M17 30C17 30 0 19.5 0 9.2C0 4.1 4 0 9 0C12.4 0 15.4 1.9 17 4.7C18.6 1.9 21.6 0 25 0C30 0 34 4.1 34 9.2C34 19.5 17 30 17 30Z" fill="#EB3656"/></svg>');
  heart.name = 'Heart'; mark.appendChild(heart);
  add(mark, T('Email Love', { size: 26, bold: true, lh: 100, color: 'inv', family: display === DOC.display ? display : null }));
  left.itemSpacing = 40;
  // Two lines, never three: the title keeps its natural width and steps down until it fits the block.
  const title = add(left, T(cfg.brand + '\nEmail Design System', { size: 76, bold: true, lh: 100, ls: -1.5, color: 'inv', family: display === DOC.display ? display : null }));
  if (title.width > 600) title.fontSize = Math.floor(76 * 600 / title.width);
  const meta = AL('VERTICAL', { gap: 8, name: 'Meta' }); add(left, meta, true);
  add(meta, T(cfg.meta, { size: 16, bold: true, ls: 0.5, color: 'inv' }), true);
  if (cfg.note) add(meta, T(cfg.note, { size: 14, color: 'inv', lh: 150 }), true);
  left.y = Math.round((H - left.height) / 2);
  if (cfg.rootId) {
    // Instances only render once their main components' pages are loaded.
    for (const pg of figma.root.children) await pg.loadAsync();
    const root = await figma.getNodeByIdAsync(cfg.rootId);
    const bytes = await root.exportAsync({ format: 'PNG', constraint: { type: 'WIDTH', value: 800 } });
    const img = figma.createImage(bytes); const w = 400, h = Math.round(root.height * (w / root.width));
    const prev = figma.createRectangle(); prev.name = 'Preview / ' + root.name; prev.resize(w, h); prev.cornerRadius = 8;
    prev.fills = [{ type: 'IMAGE', imageHash: img.hash, scaleMode: 'FILL' }];
    prev.effects = [{ type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.35 }, offset: { x: 0, y: 24 }, radius: 64, spread: 0, visible: true, blendMode: 'NORMAL' }];
    cover.appendChild(prev); prev.x = W - w - 120; prev.y = 72;
  }
  return { cover: cover.id, size: [W, H], displayFont: display, strays: strays(page, new Set([cover.id])), missingTokens: [...MISSING] };
}

// ---------- scaffolding pages ----------
// cfg: { pageId, name, eyebrow: '02   ·   Foundations', title, lede, intro, sections: [{ num: '2.1', title, note, build: async (content, KIT) => {...} }],
//        stage: { title: 'Main components', items: [{ id, caption, backdrop }] } }   (stage is for the Buttons page)
async function buildScaffoldPage(cfg) {
  const page = await setup(cfg.pageId);
  for (const n of [...page.children]) if ((n.name === cfg.name || n.name === 'Component stage') && n.type === 'FRAME') n.remove();
  const board = AL('VERTICAL', { gap: 88, pad: [112, 96, 128, 96], fill: 'bg', name: cfg.name });
  board.resize(1440, 10); board.counterAxisSizingMode = 'FIXED'; board.primaryAxisSizingMode = 'AUTO';
  page.insertChild(0, board); board.x = 0; board.y = 0;
  pageHeader(board, cfg, 1248).layoutSizingHorizontal = 'FILL';
  for (const s of cfg.sections) {
    const row = AL('HORIZONTAL', { gap: 64, name: 'Section / ' + s.title }); add(board, row, true);
    const l = col('Section label', 260, 12); row.appendChild(l);
    add(l, T(s.num, { size: 12, bold: true, ls: 2, color: 'mute' })); add(l, T(s.title, { size: 22, bold: true, lh: 120 }), true);
    if (s.note) add(l, T(s.note, { size: 14, color: 'mute', lh: 155 }), true);
    const c = AL('VERTICAL', { gap: 24, name: 'Section content' }); add(row, c); c.layoutSizingHorizontal = 'FILL';
    await s.build(c, KIT);
  }
  const ours = new Set([board.id]); const placed = [];
  if (cfg.stage) {
    // Main components stay direct children of the page, on a stage to the right of the board.
    const SX = 1520, SW = 744; let y = 112;
    const st = placeStage(page, 'Component stage', SX, 0, SW, 10, 1); ours.add(st.id);
    const head = caption(cfg.stage.title || 'Main components'); st.appendChild(head); head.x = 72; head.y = y; y += 48;
    for (const it of cfg.stage.items) {
      const comp = await figma.getNodeByIdAsync(it.id); page.appendChild(comp);
      const bandPad = it.backdrop ? 48 : 0;
      if (it.backdrop) { const band = box('Backdrop / ' + comp.name, SW, comp.height + 40 + bandPad * 2, 'blk'); st.appendChild(band); band.x = 0; band.y = y; }
      const cap = caption(it.caption || comp.name, it.backdrop ? 'inv' : 'mute'); st.appendChild(cap); cap.x = Math.round((SW - comp.width) / 2); cap.y = y + bandPad;
      comp.x = SX + Math.round((SW - comp.width) / 2); comp.y = y + bandPad + 28;
      y += comp.height + 28 + bandPad * 2 + 72; placed.push(comp.name);
    }
    st.resize(SW, Math.max(y + 40, 400));
  }
  return { board: board.id, size: [board.width, board.height], placed, strays: strays(page, ours), missingTokens: [...MISSING] };
}

// ---------- component category pages ----------
// cfg: { pageId, category, number: '05', lede, intro, modules: [{ comp: nodeId, name, purpose, uses: [...], props: [[name, type, note]], propsNote, specs: [[k, v]], source, status }] }
async function buildModulePage(cfg) {
  const page = await setup(cfg.pageId);
  const boardName = cfg.category + ' page';
  for (const n of [...page.children]) if (n.name === boardName && n.type === 'FRAME') n.remove();
  const board = figma.createFrame(); board.name = boardName; board.fills = [P('bg')]; board.clipsContent = false;
  page.insertChild(0, board); board.x = 0; board.y = 0;
  const X = 120, CARD = 600, GAP = 96, STAGE_PAD = 40, ROW_GAP = 120;
  const hdr = pageHeader(board, { eyebrow: cfg.number + '   ·   Modules', title: cfg.category, lede: cfg.lede, intro: cfg.intro }, CARD * 2 + GAP);
  hdr.x = X; hdr.y = 120;
  let y = 120 + hdr.height + 96, maxW = 600; const placed = [];
  for (const m of cfg.modules) {
    const c = col('Spec / ' + m.name, CARD, 28); board.appendChild(c); c.x = X; c.y = y;
    const top = AL('HORIZONTAL', { gap: 16, name: 'Top', cross: 'CENTER' }); add(c, top, true);
    label(top, 'Module  ·  ' + cfg.category); KIT.badge(top, m.status || 'Awaiting review');
    add(c, T(m.name, { size: 40, bold: true, lh: 110, ls: -0.5 }), true); add(c, T(m.purpose, { size: 18, color: 'mute', lh: 150 }), true);
    const u = AL('VERTICAL', { gap: 10, name: 'Use it for' }); add(c, u, true); label(u, 'Use it for'); KIT.bullets(u, m.uses);
    const pp = AL('VERTICAL', { gap: 12, name: 'Properties' }); add(c, pp, true); label(pp, 'Properties');
    if (m.props && m.props.length) KIT.table(pp, null, m.props, [130, 80]);
    if (m.propsNote) note(pp, m.propsNote);
    const sp = AL('VERTICAL', { gap: 12, name: 'Specs' }); add(c, sp, true); label(sp, 'Specs'); KIT.table(sp, null, m.specs, [150]);
    const so = AL('VERTICAL', { gap: 8, name: 'Source' }); add(c, so, true); label(so, 'Source'); note(so, m.source);
    // The main component stays a direct child of the page, on top of a grey stage, so white modules read on a white board.
    const comp = await figma.getNodeByIdAsync(m.comp); page.appendChild(comp); comp.x = X + CARD + GAP + STAGE_PAD; comp.y = y + STAGE_PAD;
    const st = box('Stage / ' + m.name, comp.width + STAGE_PAD * 2, comp.height + STAGE_PAD * 2, 'sub');
    board.appendChild(st); st.x = X + CARD + GAP; st.y = y;
    const cap = caption(`${Math.round(comp.width)} x ${Math.round(comp.height)}   ·   Main component, instance this`); board.appendChild(cap); cap.x = st.x; cap.y = st.y + st.height + 12;
    maxW = Math.max(maxW, comp.width);
    placed.push(m.name); y += Math.max(c.height, st.height + 40) + ROW_GAP;
  }
  board.resize(X + CARD + GAP + maxW + STAGE_PAD * 2 + X, y);
  return { board: board.id, size: [board.width, board.height], placed, strays: strays(page, new Set([board.id])), missingTokens: [...MISSING] };
}

// ---------- campaigns ----------
// cfg: { pageId, number: '06', lede, guide: { badge, title, intro, steps: [[t, d]], settings: [[k, v]], note }, roots: [{ id, caption }] }
async function buildCampaignsPage(cfg) {
  const page = await setup(cfg.pageId);
  for (const n of [...page.children]) if (n.name === 'Campaigns page' && n.type === 'FRAME') n.remove();
  const board = figma.createFrame(); board.name = 'Campaigns page'; board.fills = [P('bg')]; board.clipsContent = false;
  page.insertChild(0, board); board.x = 0; board.y = 0;
  const X = 120, COL = 600, RX = 816, STEP = 840, STAGE_PAD = 40;
  const hdr = pageHeader(board, { eyebrow: (cfg.number || '06') + '   ·   Templates', title: 'Campaigns', lede: cfg.lede }, COL * 2 + 96);
  hdr.x = X; hdr.y = 120;
  const top = 120 + hdr.height + 96;
  const g = col('Guide', COL, 28); board.appendChild(g); g.x = X; g.y = top + STAGE_PAD;
  const tr = AL('HORIZONTAL', { gap: 16, name: 'Top', cross: 'CENTER' }); add(g, tr, true); label(tr, 'Template');
  if (cfg.guide.badge) KIT.badge(tr, cfg.guide.badge);
  add(g, T(cfg.guide.title, { size: 40, bold: true, lh: 110, ls: -0.5 }), true);
  if (cfg.guide.intro) add(g, T(cfg.guide.intro, { size: 18, color: 'mute', lh: 150 }), true);
  const s1 = AL('VERTICAL', { gap: 12, name: 'Start a new send' }); add(g, s1, true); label(s1, 'Start a new send'); KIT.steps(s1, cfg.guide.steps);
  const s2 = AL('VERTICAL', { gap: 12, name: 'Settings on the root' }); add(g, s2, true); label(s2, 'Settings on the root'); KIT.table(s2, null, cfg.guide.settings, [170]);
  if (cfg.guide.note) note(g, cfg.guide.note);
  let bottom = g.y + g.height, right = X + COL; const placed = [];
  for (let i = 0; i < cfg.roots.length; i++) {
    const r = await figma.getNodeByIdAsync(cfg.roots[i].id); page.appendChild(r);
    const sx = RX + i * STEP; r.x = sx + STAGE_PAD; r.y = top + STAGE_PAD;
    const st = box('Stage / ' + r.name, r.width + STAGE_PAD * 2, r.height + STAGE_PAD * 2, 'sub'); board.appendChild(st); st.x = sx; st.y = top;
    const cap = caption(cfg.roots[i].caption || `${r.name}   ·   ${Math.round(r.width)} x ${Math.round(r.height)}   ·   Email root`); board.appendChild(cap); cap.x = sx; cap.y = st.y + st.height + 12;
    bottom = Math.max(bottom, cap.y + 40); right = Math.max(right, st.x + st.width); placed.push(r.name);
  }
  board.resize(Math.max(1536, right + X), bottom + 120);
  const ours = new Set([board.id, ...cfg.roots.map(r => r.id)]);
  return { board: board.id, size: [board.width, board.height], placed, strays: strays(page, ours), missingTokens: [...MISSING] };
}
