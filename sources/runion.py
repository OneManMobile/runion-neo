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
    stroke: float = 50       # line thickness of the Regular — one width for everything …
    light: float = 32        # … and of the Light and Bold masters of the variable font
    bold: float = 74
    dot: float = 1.0         # a free-standing dot is this many pens wide: a small square reads lighter than a line
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


def _on_lines(g):
    """Every grid dot that some line of the glyph touches or crosses."""
    on = set()
    for pts in g.strokes:
        for a, b in zip(pts, pts[1:]):
            k = gcd(b[0] - a[0], b[1] - a[1])
            if k:
                on.update((a[0] + (b[0] - a[0]) // k * j, a[1] + (b[1] - a[1]) // k * j) for j in range(k + 1))
    return on


def _dot_halves(g, P):
    """Half-size of every lone dot of the glyph, by grid point.

    A free-standing dot is P.dot pens wide, so it reads as strongly as a line. Where a dot that
    big would come within half a pen of a line, it shrinks back towards one pen. A dot that
    sits on a line stays one pen.
    """
    h, dots = P.stroke / 2, [s[0] for s in g.strokes if len(s) == 1]
    if not dots:
        return {}
    on, lines = _on_lines(g), [s for s in g.strokes if len(s) > 1]
    ink = outline(Glyph(g.name, [], [], [], lines), P) if lines else Polygon()
    halves = {}
    for p in dots:
        c = P.pt(*p)
        fits = lambda r: ink.is_empty or _nib(c, r).distance(ink) >= h
        lo, hi = h, h * (1 if p in on else P.dot)
        if not fits(hi):
            for _ in range(12):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if fits(mid) else (lo, mid)
            hi = lo
        halves[p] = hi
    return halves


def outline(g, P=Params()):
    """Glyph → shapely geometry in font units.

    Lines are plain bands, cut square at the dot they end on. Then every dot is inked by
    looking at ALL the lines meeting there, whichever stroke they belong to: sort them by
    angle, and wherever two neighbours leave a gap of 180° or more, fill the outer corner
    (the mitre of those two lines), clipped to the dot's nib. One line alone → its end cap.
    Three lines meeting (the tip of ᛏ) → still just the one outer corner, no shoulders.
    """
    h, parts, arms, halves = P.stroke / 2, [], {}, _dot_halves(g, P)
    for pts in g.strokes:
        if len(pts) == 1:                                  # a dot
            parts.append(_nib(P.pt(*pts[0]), halves[pts[0]]))
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


_UNIT = {}


def _unit_corner(a, b):
    """The corner piece between arms a and b at a dot of half-stroke 1, centred on (0, 0)."""
    if (a, b) not in _UNIT:
        n = (0.0, 0.0)
        poly = orient(_line_band(n, a, 1).intersection(_line_band(n, b, 1)).intersection(_nib(n, 1)), sign=1.0)
        pts = []
        for p in list(poly.exterior.coords)[:-1]:
            if not pts or hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) > 1e-6:
                pts.append(p)
        if hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) <= 1e-6:
            pts.pop()
        turns = lambda p, q, r: abs((q[0] - p[0]) * (r[1] - q[1]) - (q[1] - p[1]) * (r[0] - q[0])) > 1e-9
        _UNIT[a, b] = [p for i, p in enumerate(pts) if turns(pts[i - 1], p, pts[(i + 1) % len(pts)])]
    return _UNIT[a, b]


def pieces(g, P=Params()):
    """Glyph → its ink as separate, overlapping pieces, outer contours counter-clockwise.

    The same ink as outline(), left unmerged: one band per straight run of line (lines that lie
    on one another are merged first), one corner per outer corner, one square per dot. Every
    piece is a fixed shape scaled by the half-stroke around a dot, so a glyph has the same
    contours and points at every stroke width — the masters of the variable font interpolate exactly.
    """
    h, out, arms, runs, halves = P.stroke / 2, [], {}, {}, _dot_halves(g, P)
    for pts in g.strokes:
        if len(pts) == 1:
            (x, y), half = P.pt(*pts[0]), halves[pts[0]]
            out.append([(x - half, y - half), (x + half, y - half), (x + half, y + half), (x - half, y + half)])
            continue
        for a, b in zip(pts, pts[1:]):
            k = gcd(b[0] - a[0], b[1] - a[1])
            if not k:
                continue
            for j in range(k + 1):                         # every dot the line touches or crosses
                n = (a[0] + (b[0] - a[0]) // k * j, a[1] + (b[1] - a[1]) // k * j)
                for far, on in ((b, j < k), (a, j > 0)):
                    if on:
                        t = atan2((far[1] - n[1]) * P.cell_h, (far[0] - n[0]) * P.cell_w)
                        arms.setdefault(n, set()).add(round(t + 2 * pi if t < -pi + 1e-9 else t, 9))
            d = ((b[0] - a[0]) // k, (b[1] - a[1]) // k)   # the line it lies on: direction + offset
            if d[0] < 0 or (d[0] == 0 and d[1] < 0):
                d, a, b = (-d[0], -d[1]), b, a
            pos = lambda p: p[0] * d[0] + p[1] * d[1]
            runs.setdefault((d, a[0] * d[1] - a[1] * d[0]), []).append((pos(a), pos(b), a, b))
    for key in sorted(runs):                               # overlapping or touching lines on one line → one band
        merged = []
        for s, e, a, b in sorted(runs[key]):
            if merged and s <= merged[-1][1]:
                if e > merged[-1][1]:
                    merged[-1] = (merged[-1][0], e, merged[-1][2], b)
            else:
                merged.append((s, e, a, b))
        for _, _, a, b in merged:
            (ax, ay), (bx, by) = P.pt(*a), P.pt(*b)
            L = hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / L * h, (bx - ax) / L * h
            out.append([(ax - nx, ay - ny), (bx - nx, by - ny), (bx + nx, by + ny), (ax + nx, ay + ny)])
    for n, angles in arms.items():
        x, y = P.pt(*n)
        th = sorted(angles)
        for i, a in enumerate(th):
            b = th[(i + 1) % len(th)]
            gap = 2 * pi if len(th) == 1 else (b - a) % (2 * pi)
            if len(th) == 1 or gap > pi + 1e-9:            # a straight run through a dot is already inked
                out.append([(x + h * ux, y + h * uy) for ux, uy in _unit_corner(a, b)])
    return out


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
