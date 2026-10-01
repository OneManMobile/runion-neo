"""Build Runion Neo.

    sources/glyphs.txt ─► sources/RunionNeo-Regular.ufo ─ fontmake ─► fonts/ttf/*.ttf ─► fonts/webfonts/*.woff2
                                                                                   └─► specimen/data.js (playground)

glyphs.txt is the real source: dots and the lines between them. The UFO is generated from it
on every build so the font can be compiled — and reviewed — with the standard fontmake tooling.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.ttProgram import Program
from ufoLib2 import Font

from runion import Params, contours, outline, parse, uses_full_width

SRC = Path(__file__).parent
ROOT = SRC.parent
FAMILY, STYLE, VERSION = "Runion Neo", "Regular", (1, 0)
REPO = "https://github.com/OneManMobile/Runion-Neo"
DESIGNER = "Andreas Rudolph"
COPYRIGHT = f"Copyright 2026 The {FAMILY} Project Authors ({REPO})"
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"
DESCRIPTION = ("A monospaced Latin and Elder Futhark face on a grid of 3 by 7 dots. Straight lines only, dot to dot. "
               "Unicase: each capital is its letter with a rune accent.")
SS01 = "Four-stroke sowilo"
NUDGE = 10                            # combining marks are drawn this much low; their anchor lifts them back, so
                                      # shapers see a real attachment and non-shaping apps are off by 1% of an em
ASCENT, DESCENT = 1030, -270          # room for the attic and cellar marks; win metrics follow the real bbox
P = Params()
STEM = f"{FAMILY.replace(' ', '')}-{STYLE}"


def features(glyphs, cmap):
    """OpenType features: drawn sequences (ccmp), alternates (ss01), mark attachment, GDEF classes."""
    seqs = [f"    sub {' '.join(cmap[ord(c)] for c in s)} by {g.name};" for g in glyphs for s in g.sequences]
    alts = [f"    sub {cmap[ord(c)]} by {g.name};" for g in glyphs for c in g.optional]
    fea = "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nlanguagesystem runr dflt;\n"
    if seqs:
        fea += "feature ccmp {\n" + "\n".join(seqs) + "\n} ccmp;\n"
    if alts:
        fea += f'feature ss01 {{\n    featureNames {{ name "{SS01}"; }};\n' + "\n".join(alts) + "\n} ss01;\n"

    # combining marks: every glyph fills the same box, so ONE anchor above and ONE below serve all bases
    top = [g.name for g in glyphs if g.mark and max(y for s in g.strokes for _, y in s) > P.rows - 1]
    bottom = [g.name for g in glyphs if g.mark and g.name not in top]
    bases = [g.name for g in glyphs if not g.mark and g.strokes and g.name != ".notdef"]
    mid, hi, lo = P.advance // 2, P.cap + 60, -60
    fea += (f"markClass [{' '.join(top)}] <anchor {mid - P.advance} {hi - NUDGE}> @TOP;\n"
            f"markClass [{' '.join(bottom)}] <anchor {mid - P.advance} {lo - NUDGE}> @BOTTOM;\n"
            f"feature mark {{\n    pos base [{' '.join(bases)}] <anchor {mid} {hi}> mark @TOP <anchor {mid} {lo}> mark @BOTTOM;\n}} mark;\n"
            f"table GDEF {{\n    GlyphClassDef [{' '.join(bases)}], , [{' '.join(top + bottom)}], ;\n}} GDEF;\n")
    return fea, len(seqs), len(alts)


def main():
    glyphs = parse(SRC / "glyphs.txt", P)
    names = [g.name for g in glyphs]
    assert names[0] == ".notdef" and len(set(names)) == len(names), "duplicate glyph name"

    ufo, cmap, data, ys = Font(), {}, [], []
    for g in glyphs:
        for c in g.chars:
            assert ord(c) not in cmap, f"{c!r} mapped twice ({cmap.get(ord(c))}, {g.name})"
            cmap[ord(c)] = g.name
        rings = contours(outline(g, P), clockwise=False)
        if g.mark:                                         # zero-width: the ink sits back over the glyph before it
            rings = [[(x - P.advance, y - NUDGE) for x, y in r] for r in rings]
        ys += [y for r in rings for _, y in r]
        glyph = ufo.newGlyph(g.name)
        glyph.width = 0 if g.mark else P.advance
        glyph.unicodes = [ord(c) for c in g.chars]
        pen = glyph.getPen()
        for ring in rings:
            pen.moveTo(ring[0])
            for pt in ring[1:]:
                pen.lineTo(pt)
            pen.closePath()
        data.append({
            "name": g.name, "chars": g.chars, "mark": g.mark, "group": g.group,
            "sequences": ["".join(s) for s in g.sequences], "optional": g.optional,
            "strokes": g.strokes, "fullWidth": uses_full_width(g, P),
            "path": " ".join("M" + " L".join(f"{x} {y}" for x, y in r) + " Z" for r in rings),
        })

    ufo.features.text, n_seq, n_alt = features(glyphs, cmap)
    ufo.lib["public.glyphOrder"] = names
    ufo.lib["public.openTypeMeta"] = {"dlng": ["Latn", "Runr"], "slng": ["Latn", "Runr"]}
    i = ufo.info
    i.familyName, i.styleName, i.versionMajor, i.versionMinor = FAMILY, STYLE, *VERSION
    i.unitsPerEm, i.ascender, i.descender, i.capHeight, i.xHeight, i.italicAngle = P.upm, ASCENT, DESCENT, P.cap, P.cap, 0
    i.copyright, i.openTypeNameDesigner, i.openTypeNameDesignerURL = COPYRIGHT, DESIGNER, REPO
    i.openTypeNameManufacturer, i.openTypeNameManufacturerURL = DESIGNER, REPO
    i.openTypeNameLicense, i.openTypeNameLicenseURL, i.openTypeNameDescription = LICENSE, LICENSE_URL, DESCRIPTION
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = ASCENT, DESCENT, 0
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = ASCENT, DESCENT, 0
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = max(ys + [ASCENT]), -min(ys + [DESCENT])
    i.openTypeOS2Selection, i.openTypeOS2Type, i.openTypeOS2VendorID = [7], [], "NONE"
    i.openTypeOS2Panose = [2, 0, 5, 9, 0, 0, 0, 0, 0, 0]
    i.openTypeOS2WeightClass, i.openTypeOS2WidthClass = 400, 5
    i.postscriptIsFixedPitch, i.postscriptUnderlinePosition, i.postscriptUnderlineThickness = True, -100, int(P.stroke)

    ufo_path = SRC / f"{STEM}.ufo"
    ufo.save(ufo_path, overwrite=True)
    run = subprocess.run([sys.executable, "-m", "fontmake", "-u", str(ufo_path), "-o", "ttf", "--keep-overlaps",
                          "--no-production-names", "--output-dir", str(ROOT / "fonts/ttf")], capture_output=True, text=True)
    if run.returncode:
        sys.exit(run.stdout + run.stderr)

    ttf = ROOT / "fonts/ttf" / f"{STEM}.ttf"               # unhinted: same fix-ups as `gftools fix-nonhinting`
    font = TTFont(ttf)
    font["gasp"] = gasp = newTable("gasp")
    gasp.gaspRange = {0xFFFF: 15}
    font["prep"] = prep = newTable("prep")
    prep.program = Program()
    prep.program.fromAssembly(["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"])
    font["head"].flags |= 1 << 3
    font.save(ttf)
    font.flavor = "woff2"
    (ROOT / "fonts/webfonts").mkdir(parents=True, exist_ok=True)
    font.save(ROOT / "fonts/webfonts" / f"{STEM}.woff2")

    params = {k: getattr(P, k) for k in ("cols", "rows", "cell_w", "cell_h", "stroke", "side", "advance", "cap")}
    (ROOT / "specimen").mkdir(exist_ok=True)
    (ROOT / "specimen/data.js").write_text(
        "window.RUNION = " + json.dumps({"built": int(time.time()), "params": params, "glyphs": data}, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    for line in (SRC / "glyphs.txt").read_text().splitlines():     # coverage of every required character set
        if line.startswith("@charset"):
            want = [int(t[2:], 16) for t in (SRC / line.split()[1]).read_text().split() if t.startswith("U+")]
            miss = [cp for cp in want if cp not in cmap]
            print(f"{line.split()[1]}: {len(want) - len(miss)}/{len(want)}" + (" · missing " + " ".join(f"U+{cp:04X}" for cp in miss) if miss else " ✓"))
    narrow = [g.name for g in glyphs if g.strokes and (g.group.startswith("Latin") or g.group == "Numbers")
              and not uses_full_width(g, P)]
    print(f"{len(names)} glyphs · {len(cmap)} characters · {n_seq} drawn sequences (ccmp) · {n_alt} alternates (ss01)")
    print(f"advance {P.advance} · cap height {P.cap} · stroke {P.stroke:g} · ink y {min(ys)}…{max(ys)}")
    print(f"letters and digits not full width ({len(narrow)}): {' '.join(narrow) or '—'}")
    print(f"→ {ttf.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
