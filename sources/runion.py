"""Runion Neo — the engine: glyph source → skeleton → outline.

The model
    dot      a grid point. Its ink is a square "nib" (stroke × stroke).
    line     a band of constant thickness between two dots.
    rule     at a dot, ink never leaves that dot's nib — so corners are
             mitred but clipped, terminals are cut flush with the grid,
             and EVERY glyph ends up in exactly the same ink box.
             A dot is inked once, from all the lines meeting there.
"""
import re
import unicodedata
from dataclasses import dataclass
from math import atan2, cos, gcd, hypot, pi, sin
from pathlib import Path

from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union


@dataclass
class Params:
    cols: int = 3            # grid points across
    rows: int = 7            # grid points up
    cell_w: float = 120      # distance between columns (font units)
    cell_h: float = 120      # distance between rows
    stroke: float = 50       # line thickness — one width for everything
    advance: int = 400       # the monospace cell — the dot lattice sits centred in it
    upm: int = 1000

    @property
    def h(self):
        return self.stroke / 2

    @property
    def side(self):
        """Side bearing of the stroke."""
        return (self.advance - self.stroke - (self.cols - 1) * self.cell_w) / 2

    @property
    def cap(self):
        return round(self.stroke + (self.rows - 1) * self.cell_h)

    def pt(self, gx, gy):
        """Grid point → font units."""
        return ((self.advance - (self.cols - 1) * self.cell_w) / 2 + gx * self.cell_w,
                self.h + gy * self.cell_h)


@dataclass
class Glyph:
    name: str
    chars: list          # single characters mapped to this glyph
    sequences: list      # lists of characters the font draws as this one glyph   (ᚨ+U+030A)
    optional: list       # characters shown as this glyph when the reader turns on ss01   (~ᛊ)
    strokes: list        # list of polylines, each a list of (gx, gy)
    mark: bool = False   # combining mark: zero width, sits over the glyph before it
    group: str = ""      # the "# ── title ──" section it was defined in


# ── source parsing ──────────────────────────────────────────────────
CELLAR = {"a": -1, "b": -2}          # rows below the baseline, for marks like cedilla
ATTIC = 2                            # rows above the top row, for marks like acute
GROUP = re.compile(r"#\s*──\s*(.+?)\s*──")


def _char(tok):
    return chr(int(tok[2:], 16)) if tok.upper().startswith("U+") and len(tok) > 2 else tok


def _point(tok):
    return int(tok[0]), CELLAR[tok[1]] if tok[1] in CELLAR else int(tok[1])


def parse(path, P=Params()):
    """Read the source → list of Glyphs (plain glyphs, then marks, then composites).

    "@key value"   sets a Param ·  "@charset file"  names characters the font must cover
    "# ── title ──" starts a group; every glyph below it belongs to that group
    combining      characters (U+0301 …) are split off into a zero-width "uniXXXX" mark
    "=name"        in the strokes field reuses another glyph's strokes
    accented       characters wanted by a charset are composed automatically from their
                   Unicode decomposition: base letter + mark(s). Every glyph fills the same
                   box, so a mark sits in the same place over all of them.
    """
    path = Path(path)
    glyphs, marks, wanted, by_name, group = [], [], [], {}, ""
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        if m := GROUP.match(raw.strip()):
            group = m.group(1)
        line = raw.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("@"):
            key, val = line[1:].split()
            if key == "charset":
                wanted += [_char(t) for t in (path.parent / val).read_text().split() if t.startswith("U+")]
            else:
                setattr(P, key, type(getattr(P, key))(float(val)))
            continue
        name, chars, strokes = (f.strip() for f in line.split("|"))
        g = by_name[name] = Glyph(name, [], [], [], [], group=group)
        for tok in chars.split():
            if len(tok) > 1 and tok.startswith("~"):              # ~ᛊ: ss01 alternate
                g.optional.append(_char(tok[1:]))
            elif len(tok) > 1 and "+" in tok.replace("U+", "U"):    # ᚨ+U+030A: a sequence
                g.sequences.append([_char(t.replace("U", "U+", 1) if t.startswith("U") else t)
                                    for t in tok.replace("U+", "U").split("+")])
            else:
                g.chars.append(_char(tok))
        for tok in strokes.split():
            if tok.startswith("="):
                g.strokes += by_name[tok[1:]].strokes
                continue
            pts = [_point(p) for p in tok.split("-")]
            for x, y in pts:
                if not (0 <= x < P.cols and min(CELLAR.values()) <= y < P.rows + ATTIC):
                    raise ValueError(f"{path}:{n} {name}: point {x},{y} is off the grid")
            g.strokes.append(pts)
        glyphs.append(g)
        for c in [c for c in g.chars if unicodedata.combining(c)]:
            g.chars.remove(c)
            marks.append(Glyph(f"uni{ord(c):04X}", [c], [], [], g.strokes, mark=True, group=group))

    glyphs = [g for g in glyphs if g.chars or g.sequences or g.optional or g.name in (".notdef", "space")]
    have = {c: g for g in glyphs + marks for c in g.chars}
    composed = []
    for ch in wanted:                                              # base letter + mark(s), straight from Unicode
        parts = unicodedata.normalize("NFD", ch)
        if ch in have or len(parts) < 2 or not all(c in have for c in parts):
            continue
        strokes = [s for c in parts for s in have[c].strokes]
        composed.append(Glyph(f"uni{ord(ch):04X}", [ch], [], [], strokes, group="Accented"))
    return glyphs + marks + composed


def uses_full_width(g, P=Params()):
    xs = {x for s in g.strokes for x, _ in s}
    return 0 in xs and P.cols - 1 in xs


# ── geometry ────────────────────────────────────────────────────────
def _band(a, b, h, ext=0.0):
    """Rectangle of half-width h around a→b, optionally extended past both ends."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy * h, ux * h
    ax, ay = a[0] - ux * ext, a[1] - uy * ext
    bx, by = b[0] + ux * ext, b[1] + uy * ext
    return Polygon([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)])


def _nib(p, h):
    return box(p[0] - h, p[1] - h, p[0] + h, p[1] + h)


def _line_band(n, theta, h):
    """Band around the line through node n at angle theta (long enough to cross the nib)."""
    ux, uy = cos(theta) * 3 * h, sin(theta) * 3 * h
    return _band((n[0] - ux, n[1] - uy), (n[0] + ux, n[1] + uy), h)


def outline(g, P=Params()):
    """Glyph → shapely geometry in font units.

    Lines are plain bands, cut square at the dot they end on. Then every dot is inked by
    looking at ALL the lines meeting there, whichever stroke they belong to: sort them by
    angle, and wherever two neighbours leave a gap of 180° or more, fill the outer corner
    (the mitre of those two lines), clipped to the dot's nib. One line alone → its end cap.
    Three lines meeting (the tip of ᛏ) → still just the one outer corner, no shoulders.
    """
    h, parts, arms = P.stroke / 2, [], {}
    for pts in g.strokes:
        if len(pts) == 1:                                  # a dot
            parts.append(_nib(P.pt(*pts[0]), h))
            continue
        for a, b in zip(pts, pts[1:]):
            k = gcd(b[0] - a[0], b[1] - a[1])
            if not k:
                continue
            A, B = P.pt(*a), P.pt(*b)
            parts.append(_band(A, B, h))
            for j in range(k + 1):                         # every dot the line touches or crosses
                n = P.pt(a[0] + (b[0] - a[0]) // k * j, a[1] + (b[1] - a[1]) // k * j)
                for far, on in ((B, j < k), (A, j > 0)):
                    if on:
                        t = atan2(far[1] - n[1], far[0] - n[0])
                        arms.setdefault(n, set()).add(round(t + 2 * pi if t < -pi + 1e-9 else t, 9))
    for n, angles in arms.items():
        th = sorted(angles)
        for i, a in enumerate(th):
            b = th[(i + 1) % len(th)]
            gap = 2 * pi if len(th) == 1 else (b - a) % (2 * pi)
            if gap >= pi - 1e-9:
                parts.append(_line_band(n, a, h).intersection(_line_band(n, b, h)).intersection(_nib(n, h)))
    if not parts:
        return Polygon()
    # tiny close-open pass welds float-precision seams without rounding any corner
    shape = unary_union(parts).buffer(0.2, join_style="mitre").buffer(-0.2, join_style="mitre")
    return shape.simplify(0.05)


def _turns(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) != (b[1] - a[1]) * (c[0] - b[0])


def contours(shape, clockwise=True):
    """Geometry → list of integer point lists. Outer contours clockwise (TrueType) by default;
    pass clockwise=False for the UFO convention (outer counter-clockwise, fontmake reverses it)."""
    polys = getattr(shape, "geoms", [shape])
    out = []
    for poly in polys:
        if poly.is_empty or poly.geom_type != "Polygon":
            continue
        poly = orient(poly, sign=-1.0 if clockwise else 1.0)
        for ring in [poly.exterior, *poly.interiors]:
            pts = []
            for x, y in list(ring.coords)[:-1]:
                q = (round(x), round(y))
                if not pts or pts[-1] != q:
                    pts.append(q)
            if len(pts) > 1 and pts[0] == pts[-1]:
                pts.pop()
            pts = [p for i, p in enumerate(pts) if _turns(pts[i - 1], p, pts[(i + 1) % len(pts)])]
            if len(pts) >= 3:
                out.append(pts)
    return out
