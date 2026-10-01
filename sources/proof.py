"""Documentation images, drawn from the built font and the glyph source → documentation/*.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from runion import Params, contours, outline, parse

SRC = Path(__file__).parent
ROOT = SRC.parent
DOC = ROOT / "documentation"
VF = str(ROOT / "fonts/variable/RunionNeo[wght].ttf")
PAPER, INK, SOFT, ACCENT = (244, 240, 232), (24, 22, 20), (139, 131, 119), (196, 72, 48)


def label_font(size):
    for path in ("/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_construction(d, g, P, ox, top, S, ink=(208, 200, 186), dots=range(0, 7), line=5, r=9):
    """A glyph on its grid: the ink, the skeleton dot to dot, and the dots. top = y of the grid's top row."""
    to = lambda x, y: (ox + x * S, top + (P.cap - P.h - y) * S - (P.cap - P.h - P.pt(0, P.rows - 1)[1]) * S)
    shape = outline(g, P)
    for ring in contours(shape):
        d.polygon([to(x, y) for x, y in ring], fill=ink)
    for poly in getattr(shape, "geoms", [shape]):
        for hole in getattr(poly, "interiors", []):
            d.polygon([to(x, y) for x, y in hole.coords], fill=PAPER)
    for s in g.strokes:
        pts = [to(*P.pt(*p)) for p in s]
        if len(pts) > 1:
            d.line(pts, fill=ACCENT, width=line, joint="curve")
    for gx in range(P.cols):
        for gy in dots:
            x, y = to(*P.pt(gx, gy))
            rr = r if 0 <= gy < P.rows else r * 0.6
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=ACCENT if 0 <= gy < P.rows else (214, 170, 150))


def specimen():
    """The showcase: lowercase leads, the system on the right, capitals only where they explain themselves."""
    K = 2                                                     # drawn at 2× and scaled down, for clean edges
    img = Image.new("RGB", (2000 * K, 1050 * K), PAPER)
    d = ImageDraw.Draw(img)

    def vf(size, w=400):
        font = ImageFont.truetype(VF, size * K)
        font.set_variation_by_axes([w])
        return font

    x = 80 * K
    d.text((x, 100 * K), "runion neo", font=vf(250, 400), fill=INK)
    d.text((x + 6 * K, 395 * K), "Latin with rune-vibes, made on a 3 × 7 grid", font=label_font(26 * K), fill=SOFT)
    d.text((x, 490 * K), "the north wind sings", font=vf(84, 300), fill=INK)
    d.text((x, 615 * K), "through the stones", font=vf(84, 300), fill=INK)
    y, cx = 765 * K, x
    for word, w in (("light", 300), ("regular", 400), ("bold", 700)):
        d.text((cx, y), word, font=vf(66, w), fill=INK)
        cx += int(vf(66, w).getlength(word + "  "))
    d.text((x, 885 * K), "THE RUNION NEO FONT ALSO HAS CAPITALS", font=vf(66, 400), fill=INK)

    P = Params()                                              # the system: a and its capital, dot to dot
    glyphs = {g.name: g for g in parse(SRC / "glyphs.txt", P)}
    S = 0.62 * K
    for i, name in enumerate(("a", "A")):
        draw_construction(d, glyphs[name], P, 1330 * K + i * 300 * K, 180 * K, S, line=5 * K // 2, r=8 * K // 2 + 2)
    small = label_font(24 * K)
    d.text((1345 * K, 735 * K), "a                  A", font=small, fill=INK)
    d.text((1345 * K, 790 * K), "Every line runs dot to dot,", font=small, fill=SOFT)
    d.text((1345 * K, 830 * K), "capitals are ornamented with", font=small, fill=SOFT)
    d.text((1345 * K, 870 * K), "dots and/or lines.", font=small, fill=SOFT)
    img.resize((2000, 1050), Image.LANCZOS).save(DOC / "specimen.png")


def weights():
    img = Image.new("RGB", (2000, 900), PAPER)
    d, small = ImageDraw.Draw(img), label_font(26)
    for i, (name, w) in enumerate([("Light", 300), ("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]):
        font = ImageFont.truetype(VF, 112)
        font.set_variation_by_axes([w])
        y = 40 + i * 170
        d.text((70, y + 70), f"{name} {w}", font=small, fill=SOFT)
        d.text((360, y), "runion neo  Runion Neo", font=font, fill=INK)
    img.save(DOC / "weights.png")


def grid():
    P = Params()
    glyphs = {g.name: g for g in parse(SRC / "glyphs.txt", P)}
    show, S = ["a", "A", "h", "H", "d", "D", "uni00C9"], 0.5
    attic, cw = 2 * P.cell_h, 330
    img = Image.new("RGB", (len(show) * cw * 2, int((P.cap + 2 * attic) * S + 120) * 2), PAPER)
    d = ImageDraw.Draw(img)
    for i, name in enumerate(show):
        g, ox = glyphs[name], i * cw * 2 + 130
        top = 60 * 2 + (P.cap + attic) * S * 2
        to = lambda x, y: (ox + x * S * 2, top - y * S * 2)
        shape = outline(g, P)
        for ring in contours(shape):
            d.polygon([to(x, y) for x, y in ring], fill=(208, 200, 186))
        for poly in getattr(shape, "geoms", [shape]):
            for hole in getattr(poly, "interiors", []):
                d.polygon([to(x, y) for x, y in hole.coords], fill=PAPER)
        for s in g.strokes:                                   # the skeleton: dot to dot
            pts = [to(*P.pt(*p)) for p in s]
            if len(pts) > 1:
                d.line(pts, fill=ACCENT, width=5, joint="curve")
        for gx in range(P.cols):
            for gy in range(-2, P.rows + 2):
                x, y = to(*P.pt(gx, gy))
                r = 9 if 0 <= gy < P.rows else 5
                d.ellipse([x - r, y - r, x + r, y + r], fill=ACCENT if 0 <= gy < P.rows else (214, 170, 150))
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    img.save(DOC / "grid.png")


if __name__ == "__main__":
    DOC.mkdir(exist_ok=True)
    specimen(), weights(), grid()
    print("→ documentation/specimen.png · weights.png · grid.png")
