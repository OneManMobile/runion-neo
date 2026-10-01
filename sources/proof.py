"""Documentation images, drawn from the built font and the glyph source → documentation/*.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from runion import Params, contours, outline, parse

SRC = Path(__file__).parent
ROOT = SRC.parent
DOC = ROOT / "documentation"
TTF = str(ROOT / "fonts/ttf/RunionNeo-Regular.ttf")
PAPER, INK, SOFT, ACCENT = (244, 240, 232), (24, 22, 20), (139, 131, 119), (196, 72, 48)


def label_font(size):
    for path in ("/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def specimen():
    lines = [("RUNION Neo", 190), ("The North Wind sings", 112), ("through the Stones", 112),
             ("Rødgrød med fløde på Ærø", 92), ("ᚱᚢᚾᛁᛟᚾ ᚾᛖᛟ · ᚠᚢᚦᚨᚱᚲ", 92),
             ("0123456789 & @ § € $ % ( ) [ ] { }", 62)]
    img = Image.new("RGB", (2000, 1050), PAPER)
    d, y = ImageDraw.Draw(img), 40
    for text, size in lines:
        d.text((70, y), text, font=ImageFont.truetype(TTF, size), fill=INK)
        y += int(size * 1.5)
    img.save(DOC / "specimen.png")


def futhark():
    runes = ["fehu ᚠ", "uruz ᚢ", "thurisaz ᚦ", "ansuz ᚨ", "raido ᚱ", "kaunan ᚲ", "gebo ᚷ", "wunjo ᚹ",
             "hagalaz ᚺ", "naudiz ᚾ", "isa ᛁ", "jera ᛃ", "eihwaz ᛇ", "perthro ᛈ", "algiz ᛉ", "sowilo ᛊ",
             "tiwaz ᛏ", "berkanan ᛒ", "ehwaz ᛖ", "mannaz ᛗ", "laguz ᛚ", "ingwaz ᛜ", "dagaz ᛞ", "othala ᛟ"]
    cw, ch = 250, 330
    img = Image.new("RGB", (8 * cw, 3 * ch + 40), PAPER)
    d, big, small = ImageDraw.Draw(img), ImageFont.truetype(TTF, 190), label_font(24)
    for i, entry in enumerate(runes):
        name, rune = entry.split()
        x, y = (i % 8) * cw, (i // 8) * ch + 20
        d.text((x + 125, y + 20), rune, font=big, fill=INK, anchor="ma")
        d.text((x + 125, y + 262), name, font=small, fill=INK, anchor="ma")
        d.text((x + 125, y + 292), f"U+{ord(rune):04X}", font=small, fill=SOFT, anchor="ma")
    img.save(DOC / "futhark.png")


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
    specimen(), futhark(), grid()
    print("→ documentation/specimen.png · futhark.png · grid.png")
