# Runion Neo

Latin with rune-vibes, made on a 3 × 7 grid.

Runion Neo is a monospaced display typeface built from straight lines between dots. It is narrow and tall, unicase, and sharp: every letter fills the full width of its cell, every corner is cut, and every capital is its lowercase letter ornamented with dots and/or lines. It comes in every weight from Light to Bold.

![Runion Neo specimen](documentation/specimen.png)

## Get it

- **Font:** [`fonts/variable/RunionNeo[wght].ttf`](fonts/variable/RunionNeo%5Bwght%5D.ttf), one variable file with every weight from 300 to 700 and named Light, Regular, Medium, SemiBold and Bold.
- **Web:** [`fonts/webfonts/RunionNeo[wght].woff2`](fonts/webfonts/RunionNeo%5Bwght%5D.woff2).
- **Playground:** open [`index.html`](index.html) or run `make serve`. It has a type tester with a weight slider, every character, and a sketchpad for drawing glyphs on the dots.
- **Licence:** [SIL Open Font License 1.1](OFL.txt).

![Light to Bold](documentation/weight-range.png)

## How it is built

![Letters on the dot grid](documentation/grid.png)

Every glyph is drawn on the same grid of 3 columns and 7 rows of dots, and a glyph is nothing more than a list of lines between them. Lowercase a is `00-16-20 02-22`: up from the bottom left to the top middle, down to the bottom right, and a bar across.

| Rule | What it means |
| --- | --- |
| Dot to dot | Every line starts and ends on a dot. Any dot can join any other dot. There are no curves. |
| Full width | Every letter and digit touches both the left and the right column. |
| One pen | One line thickness per weight: 32 units in Light, 50 in Regular, 74 in Bold. The dots never move between weights; only the pen changes. |
| The nib | Ink at a dot stays inside that dot's square. Corners are mitred and clipped to it and line ends are cut flush, so every glyph has the same outer box. |
| Dots | A free-standing dot is 1.4 pens wide, so it reads as strongly as a line. Where that would crowd a line, it shrinks back towards one pen. |
| Unicase | Lowercase and capitals are the same height. A capital is its lowercase letter plus an ornament. |
| Accents | Accents sit outside the letter, in two rows above and two below. Because every glyph fills the same box, one position fits them all, and the 140 or so accented letters are composed automatically. |

### Lowercase

O is four lines, a diamond. C is two strokes; G is C with a stem and a short bar that stops short of the first strokes. D is a stave and a point. P is a flag on the stave, R is P with a leg, and B is P with the flag mirrored below. S runs from the upper right down to the middle left, across, and down to the lower left.

### Capitals

A capital is its lowercase letter with an ornament. The ornaments follow a few rules:

- **Add, don't redraw.** Most capitals keep the lowercase letter as it is and add something to it: a dot, a bar, a branch or a cross.
- **A line where a line fits.** Where the letter has room for one more line, it gets one: a second bar, a crossbar, a branch.
- **A dot where it doesn't.** Letters with no room for a line get one dot, in the counter or at the middle right. A few take two.
- **Vibes trump rules.** A handful of capitals change the letter itself because it looks better: E splits its middle line, H turns its bar into a cross, F raises its arms, D nests a second triangle and squares off its point.

| Capitals | Ornament |
| --- | --- |
| A T | A second crossing bar: A's right above its own, T's below its top. |
| E | The middle line splits in two, one step up and one step down. |
| H | The bar becomes a cross between the staves. |
| I | A crossbar through the middle of the stem. |
| L | A second bar right above the foot. |
| F | The arms rise as diagonals. |
| M W | A cross between the staves. |
| N | A short branch from the middle of the first stave down to the bottom. |
| P | The flag's diagonal is doubled and closed at the right. |
| D | A smaller triangle nested inside, and the point squared off at the right edge. |
| J | A short stem hanging free under the top bar. |
| Y | The stave runs on to the top. |
| X Z | A bar across. |
| B C G K O Q R U V | One dot, in the counter or, for B, C, K and R, at the middle right. |
| S | Two dots, one in each counter. |

The rest follow the same logic. Æ, Œ and Ð split their middle bar like E. ø is the diamond with a slash, and Ø has a small cross through the middle instead. Å is drawn as a lower A with a dot above its tip.

Everything is defined in one text file, [`sources/glyphs.txt`](sources/glyphs.txt).

## Using the font

```css
@font-face {
  font-family: "Runion Neo";
  src: url("RunionNeo[wght].woff2") format("woff2");
  font-weight: 300 700;
}
.neo { font-family: "Runion Neo", monospace; font-weight: 300; }   /* any weight from 300 to 700 */
```

Runion Neo is made for headlines, titles, signs and short text. On an ordinary screen it reads well from 16 px; at 12–14 px use Regular or Bold, and give Light about 18 px. On high-resolution screens, such as phones and Retina displays, these sizes halve.

It covers the Google Fonts Latin Core character set (319 characters).

## Building

```bash
make venv     # once: Python environment with fontmake, ufoLib2, shapely, pillow, gftools, fontbakery
make build    # glyphs.txt → UFOs → fonts/variable, fonts/webfonts, playground data
make gftools  # the Google Fonts path: gftools builder compiles fonts/ from sources/config.yaml
make proof    # contact sheet (out/) and documentation images
make test     # fontbakery, Google Fonts profile
```

`sources/glyphs.txt` is the source. `sources/build.py` turns it into three master UFOs (`sources/RunionNeo-Light.ufo`, `-Regular.ufo`, `-Bold.ufo`) and `sources/RunionNeo.designspace`, and compiles the variable font with fontmake. In the masters every line, corner and dot is a separate piece, so each glyph has the same points at every weight and the masters interpolate exactly. `sources/runion.py` turns the dots and lines into outlines.

The masters and the designspace are committed, so the font can also be built without `glyphs.txt`: `sources/config.yaml` lets `gftools builder` compile it (`make gftools`). After changing `glyphs.txt`, run `make build` first. Every push is built and checked with fontbakery by GitHub Actions.

To change a glyph, edit its line in `glyphs.txt` and run `make build`. The playground's sketchpad writes the stroke code for you.

## How it was made

Runion Neo grew out of [Runion Basic](https://github.com/OneManMobile/Runion-Font), an experiment with the same grid. It was made with AI: I worked with Claude, Anthropic's AI model, in Claude Code. I set the concept and the rules — the dot grid, full-width letters, one pen per weight, the ornamented capitals — and the letterforms themselves, decided what to keep and what to change, and reviewed the results as we went. Claude drew constructions on the grid, wrote the build code and the playground, and drafted this README. No existing font data or outlines were used; every outline is generated from `sources/glyphs.txt`.

## Licence

Copyright 2026 The Runion Neo Project Authors (https://github.com/OneManMobile/runion-neo).

This Font Software is licensed under the SIL Open Font License, Version 1.1. The licence is in [`OFL.txt`](OFL.txt) and is also available with a FAQ at https://openfontlicense.org.

---

**A historical footnote.** The look comes from runes. Their angular shapes were cut into wood and stone with straight strokes, and several of the capital ornaments are runes: H is dagaz ᛞ, M is mannaz ᛗ, F is fehu ᚠ, Y is algiz ᛉ, the second bar of A echoes the arms of ansuz ᚨ, and the dotted capitals follow the medieval stung runes, which made new letters by adding a dot. The font also draws the 24 runes of the Elder Futhark and a few later ones at their own Unicode codepoints, with an optional older form of ᛊ (`ss01`); the playground can convert text into them. Runion Neo is a typeface and makes no claim to be a reconstruction.
