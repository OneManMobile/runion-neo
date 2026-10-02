/* Runion Neo — specimen + dot-to-dot sketchpad. Data comes from build.py (specimen/data.js). */
(() => {
  const { params: P, glyphs, built, weights: W } = window.RUNION;
  // load the variable font stamped with its build time, so a rebuild is never hidden by the browser cache
  new FontFace("Runion Neo", `url("fonts/webfonts/RunionNeo[wght].woff2?v=${built}")`, { weight: "300 700" })
    .load().then((f) => document.fonts.add(f));
  const h0 = P.stroke / 2, $ = (id) => document.getElementById(id);
  let pen = P.stroke;                                     // sketchpad pen: the dots never move, only the line swells
  const X = (gx) => P.side + h0 + gx * P.cell_w;          // grid → font units, y flipped for SVG
  const Y = (gy) => P.cap - (h0 + gy * P.cell_h);
  const LOW = 2, HIGH = P.rows + 1;                       // mark rows: cellar -1,-2 (written a,b) · attic 7,8
  const rowCode = (y) => (y < 0 ? "ab"[-y - 1] : "" + y), rowOf = (c) => ("ab".includes(c) ? -("ab".indexOf(c) + 1) : +c);

  // ── transliteration: Latin text → real runes (Unicode Runic block). The font never does this;
  //    the text itself changes, so copy, search and screen readers get runes too ──
  const RUNE = {
    th: "ᚦ", ng: "ᛜ", aa: "ᚨ\u030a",
    a: "ᚨ", b: "ᛒ", c: "ᚳ", d: "ᛞ", e: "ᛖ", f: "ᚠ", g: "ᚷ", h: "ᚺ", i: "ᛁ", j: "ᛃ", k: "ᚲ", l: "ᛚ", m: "ᛗ",
    n: "ᚾ", o: "ᛟ", p: "ᛈ", q: "ᛩ", r: "ᚱ", s: "ᛊ", t: "ᛏ", u: "ᚢ", v: "ᚡ", w: "ᚹ", x: "ᚲᛊ", y: "ᛇ", z: "ᛉ",
    "å": "ᚨ\u030a", "æ": "ᛅ", "ä": "ᛅ", "ø": "ᚯ", "ö": "ᚯ", "œ": "ᚯ", "ð": "ᚧ", "đ": "ᚧ", "þ": "ᚦ",
    "ü": "ᛇ", "ß": "ᛊᛊ", "ł": "ᛚ", "ħ": "ᚺ", "ı": "ᛁ", "ȷ": "ᛃ",
  };
  const toRunes = (line) => {                             // → [[runes, the letters they came from], …]
    const out = [], ch = [...line.normalize("NFC").toLowerCase()];
    for (let i = 0; i < ch.length; i++) {
      const pair = ch[i] + (ch[i + 1] || ""), bare = ch[i].normalize("NFD").replace(/\p{M}/gu, "");
      if (RUNE[pair] && pair.length === 2) { out.push([RUNE[pair], pair]); i++; }
      else out.push([RUNE[ch[i]] || RUNE[bare] || ch[i], ch[i]]);
    }
    return out;
  };

  // ── type tester: Latin as typed, or written in runes; optionally with the source letters underneath ──
  const esc = (t) => t.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const cl = (text, label, attrs = "") => `<span class="cl"${attrs}>${esc(text)}<span class="l">${esc(label)}</span></span>`;
  const typeset = () => {
    const out = $("out"), text = $("tester").value, runes = $("runes").checked;
    out.style.fontFeatureSettings = $("kylver").checked ? '"ss01"' : "normal";
    const lines = text.split("\n").map((line) => (runes ? toRunes(line) : [...line].map((c) => [c, c])));
    if (!$("sub").checked) { out.textContent = lines.map((l) => l.map(([r]) => r).join("")).join("\n"); return; }
    out.innerHTML = lines.map((line) => {
      let html = "", word = "";
      const flush = () => { if (word) html += `<span class="w">${word}</span>`; word = ""; };
      for (const [shown, typed] of line) {
        if (/^\s$/.test(shown)) { word += cl("\u00a0", " "); flush(); } else word += cl(shown, typed);   // a space rides with its word, so wrapped lines never start indented
      }
      flush();
      return `<div>${html || "\u00a0"}</div>`;
    }).join("");
  };
  for (const id of ["tester", "sub", "runes", "kylver"]) $(id).addEventListener("input", typeset);
  $("size").oninput = (e) => ($("out").style.fontSize = e.target.value + "px");
  const named = Object.fromEntries(Object.entries(W).map(([name, w]) => [w, name]));
  $("weight").oninput = (e) => {
    $("out").style.fontWeight = e.target.value;
    $("weightv").textContent = named[e.target.value] || e.target.value;
  };
  typeset();

  // ── showcase: every character the font answers to, set in the real font, grouped as in glyphs.txt ──
  const rows = {};
  for (const g of glyphs) {
    if (g.mark || ["settings", "Marks"].includes(g.group)) continue;
    const row = (rows[g.group] ||= []);
    for (const c of g.chars) if (!/\s/.test(c)) row.push({ text: c, label: c, name: g.name });
    for (const s of g.sequences) row.push({ text: s, label: [...s].map((c) => (/\p{M}/u.test(c) ? "◌" + c : c)).join("+"), name: g.name });
    for (const c of g.optional) row.push({ text: c, label: c + "°", name: g.name, opt: true });
  }
  $("showcase").innerHTML = Object.entries(rows).filter(([, items]) => items.length).map(([title, items]) =>
    `<div class="group">${title}  ·  ${items.length}</div><div class="runes show">` +
    items.map((it) => cl(it.text, it.label, ` data-name="${it.name}"${it.opt ? ` style="font-feature-settings:'ss01'"` : ""}`)).join("") + "</div>").join("");

  // ── the engine, re-enacted in SVG: bands between dots + ink clipped to each dot's nib ──
  const clips = () => {
    let s = "";
    const h = pen / 2;
    for (let x = 0; x < P.cols; x++) for (let y = -LOW; y <= HIGH; y++)
      s += `<clipPath id="n${x}${y}"><rect x="${X(x) - h}" y="${Y(y) - h}" width="${2 * h}" height="${2 * h}"/></clipPath>`;
    return `<defs>${s}</defs>`;
  };
  const toward = (a, b, d) => {                           // point at distance d from a, heading to b
    const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    return [a[0] + ((b[0] - a[0]) / L) * d, a[1] + ((b[1] - a[1]) / L) * d];
  };
  const gcd = (a, b) => (b ? gcd(b, a % b) : Math.abs(a));
  const ink = (strokes) => {
    const h = pen / 2, arms = new Map(), onLine = new Set();
    let s = "";
    for (const pts of strokes)                            // a lone dot sitting on a line stays one pen wide
      for (let i = 0; i + 1 < pts.length; i++) {
        const a = pts[i], b = pts[i + 1], k = gcd(b[0] - a[0], b[1] - a[1]);
        for (let j = 0; k && j <= k; j++) onLine.add(`${a[0] + ((b[0] - a[0]) / k) * j},${a[1] + ((b[1] - a[1]) / k) * j}`);
      }
    const arm = (n, to) => {                              // a line leaving dot n towards `to`
      let t = Math.atan2(Y(n[1]) - Y(to[1]), X(to[0]) - X(n[0]));
      if (t < -Math.PI + 1e-9) t += 2 * Math.PI;
      const key = n.join("");
      if (!arms.has(key)) arms.set(key, { n, set: new Set() });
      arms.get(key).set.add(Math.round(t * 1e6) / 1e6);
    };
    for (const pts of strokes) {
      if (pts.length === 1) {
        const d = onLine.has(pts[0].join(",")) ? h : h * P.dot;
        s += `<rect x="${X(pts[0][0]) - d}" y="${Y(pts[0][1]) - d}" width="${2 * d}" height="${2 * d}" fill="currentColor" stroke="none"/>`;
        continue;
      }
      for (let i = 0; i + 1 < pts.length; i++) {
        const a = pts[i], b = pts[i + 1], k = gcd(b[0] - a[0], b[1] - a[1]);
        if (!k) continue;
        s += `<line x1="${X(a[0])}" y1="${Y(a[1])}" x2="${X(b[0])}" y2="${Y(b[1])}"/>`;
        for (let j = 0; j <= k; j++) {                    // every dot the line touches or crosses
          const n = [a[0] + ((b[0] - a[0]) / k) * j, a[1] + ((b[1] - a[1]) / k) * j];
          if (j < k) arm(n, b);
          if (j > 0) arm(n, a);
        }
      }
    }
    for (const { n, set } of arms.values()) {             // ink each dot once, from all lines meeting there
      const th = [...set].sort((p, q) => p - q), N = [X(n[0]), Y(n[1])];
      const out = (t, sign) => [N[0] + Math.cos(t) * 3 * h * sign, N[1] - Math.sin(t) * 3 * h * sign];
      th.forEach((t, i) => {
        const u = th[(i + 1) % th.length];
        const gap = th.length === 1 ? 2 * Math.PI : (u - t + 2 * Math.PI) % (2 * Math.PI);
        if (gap < Math.PI - 1e-6) return;                 // only the outer corner gets a mitre
        s += `<polyline clip-path="url(#n${n[0]}${n[1]})" points="${out(t, 1)} ${N} ${th.length === 1 ? out(t, -1) : out(u, 1)}"/>`;
      });
    }
    return `<g fill="none" stroke="currentColor" stroke-width="${pen}" stroke-linejoin="miter" stroke-miterlimit="100">${s}</g>`;
  };

  // ── sketchpad ─────────────────────────────────────────────────────
  let strokes = [], active = null, current = null;       // current: the glyph picked from the table, if any
  // a character as glyphs.txt writes it: awkward ones (space, |, #, combining marks) as U+XXXX
  const tok = (c) => /[\s|#\p{M}\p{C}]/u.test(c) ? "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0") : c;
  const charsField = (g) => [...g.chars.map(tok), ...g.sequences.map((s) => [...s].map(tok).join("+")),
                             ...g.optional.map((c) => "~" + tok(c))].join(" ");
  const line = () => current ? `${current.name} | ${charsField(current)} | ${$("code").value.trim()}` : $("code").value.trim();
  function showPicked() {
    const shown = [...current.chars, ...current.sequences, ...current.optional];
    $("sym").textContent = shown.join(" ");
    $("pickinfo").textContent = [current.name, ...[...current.chars, ...current.optional].map((c) =>
      "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0"))].join(" · ") + (current.optional.length ? " (ss01)" : "");
  }
  const encode = () => strokes.map((s) => s.map((p) => p[0] + rowCode(p[1])).join("-")).join(" ");
  const decode = (t) => t.trim().split(/\s+/).filter(Boolean).map((s) => s.split("-").map((p) => [+p[0], rowOf(p[1])]));
  const valid = (t) => new RegExp(`^\\s*(([0-${P.cols - 1}][0-${HIGH}ab])(-[0-${P.cols - 1}][0-${HIGH}ab])*\\s*)*$`).test(t);

  function draw(fromInput) {
    const pad = 70, last = active !== null ? strokes[active][strokes[active].length - 1] : null;
    let dots = "", skeleton = "";
    for (let x = 0; x < P.cols; x++) for (let y = -LOW; y <= HIGH; y++) {
      const on = last && last[0] === x && last[1] === y, rune = y >= 0 && y < P.rows;
      dots += `<text x="${X(x) + 16}" y="${Y(y) - 14}" font-size="26" fill="var(--soft)" opacity="${rune ? 1 : 0.5}">${x}${rowCode(y)}</text>
        <circle class="hit" data-p="${x}${rowCode(y)}" cx="${X(x)}" cy="${Y(y)}" r="${P.cell_w / 2.2}"/>
        <circle cx="${X(x)}" cy="${Y(y)}" r="${on ? 16 : rune ? 9 : 6}" fill="var(--accent)" opacity="${rune || on ? 1 : 0.45}" pointer-events="none"/>`;
    }
    for (const s of strokes)
      skeleton += `<polyline points="${s.map(([x, y]) => [X(x), Y(y)]).join(" ")}" fill="none" stroke="var(--accent)" stroke-width="4"/>`;
    $("stage").setAttribute("viewBox", `${-pad} ${-pad - (HIGH - P.rows + 1) * P.cell_h} ${P.advance + 2 * pad} ${P.cap + 2 * pad + (HIGH - P.rows + 1 + LOW) * P.cell_h}`);
    $("stage").innerHTML = clips() +
      `<rect x="${P.side}" y="0" width="${P.advance - 2 * P.side}" height="${P.cap}" fill="none" stroke="var(--line)" stroke-width="3" stroke-dasharray="10 10"/>` +
      `<g opacity=".82">${ink(strokes)}</g>${skeleton}${dots}`;
    if (!fromInput) $("code").value = encode();
    $("line").textContent = current ? line() : "";
    const xs = strokes.flat().map((p) => p[0]), full = xs.includes(0) && xs.includes(P.cols - 1);
    // the full-width rule binds Latin letters and digits only; runes and symbols keep their own width
    const bound = !current || current.chars.some((c) => /[\p{Script=Latin}\p{Nd}]/u.test(c));
    $("rule").className = full || !bound ? "ok" : "bad";
    $("rule").textContent = !xs.length || (!bound && !full) ? "" : full ? "✓ fills the full width" : "✗ a letter or digit must touch both the left and right column";
  }

  $("stage").onclick = (e) => {
    const p = e.target.dataset && e.target.dataset.p;
    if (!p) return;
    const pt = [+p[0], rowOf(p[1])];
    if (active === null) { strokes.push([pt]); active = strokes.length - 1; }
    else {
      const s = strokes[active], l = s[s.length - 1];
      if (l[0] === pt[0] && l[1] === pt[1]) active = null; else s.push(pt);
    }
    draw();
  };
  $("undo").onclick = () => {
    if (!strokes.length) return;
    const s = strokes[strokes.length - 1];
    s.pop();
    if (!s.length) { strokes.pop(); active = null; } else active = strokes.length - 1;
    draw();
  };
  $("clear").onclick = () => { strokes = []; active = null; draw(); };
  $("copy").onclick = () => navigator.clipboard && navigator.clipboard.writeText(line());
  $("code").oninput = (e) => { if (valid(e.target.value)) { strokes = decode(e.target.value); active = null; draw(true); } };
  const setPen = (v) => { pen = +v; $("pen").value = pen; $("penv").textContent = pen; draw(); };
  $("pen").oninput = (e) => setPen(e.target.value);
  $("penreg").onclick = () => setPen(P.stroke);
  $("penlight").onclick = () => setPen(P.light);
  $("penbold").onclick = () => setPen(P.bold);

  // ── glyph table (exact outlines from the build), grouped by the "# ── title ──" lines of glyphs.txt ──
  const sets = {}, NOTE = { Accented: "Accented — never drawn: the build composes letter + mark from Unicode" };
  for (const g of glyphs) if (g.strokes.length && !g.mark && g.name !== ".notdef") (sets[g.group] ||= []).push(g);
  let html = "";
  for (const [group, set] of Object.entries(sets)) {
    html += `<div class="group">${NOTE[group] || group}</div><div class="grid">` + set.map((g) => {
      const keys = [g.chars[0] || "", ...g.sequences, ...g.optional.map((c) => c + "°")];
      return `<div class="cell" data-name="${g.name}"><svg viewBox="0 ${-2 * P.cell_h - 50} ${P.advance} ${P.cap + 4 * P.cell_h + 100}">
        <path transform="translate(0 ${P.cap}) scale(1 -1)" d="${g.path}" fill="currentColor"/></svg>
        <b>${keys.join(" ").replace(/&/g, "&amp;").replace(/</g, "&lt;") || "·"}</b><i>${g.name}</i></div>`;
    }).join("") + "</div>";
  }
  $("glyphs").innerHTML = html;
  const pick = (e) => {                                   // showcase tile or table cell → open on the grid
    const hit = e.target.closest("[data-name]");
    if (!hit) return;
    document.querySelectorAll(".cell.on").forEach((c) => c.classList.remove("on"));
    const cell = document.querySelector(`.cell[data-name="${hit.dataset.name}"]`);
    if (cell) cell.classList.add("on");
    const g = glyphs.find((g) => g.name === hit.dataset.name);
    current = g;
    showPicked();
    strokes = JSON.parse(JSON.stringify(g.strokes));
    active = null;
    setPen(P.stroke);
    $("stage").closest(".lab").scrollIntoView({ behavior: "smooth", block: "start" });   // grid and the picked character both in view
  };
  $("glyphs").onclick = pick;
  $("showcase").onclick = pick;

  current = glyphs.find((g) => g.name === "A");
  showPicked();
  strokes = JSON.parse(JSON.stringify(current.strokes));
  setPen(P.stroke);
})();
