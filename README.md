# Runion Neo

Latin with rune-vibes, made on a 3 × 7 grid. Every line runs from dot to dot, with no curves. The face is monospaced, narrow and tall, and unicase: each capital is its lowercase letter ornamented with a dot or a line taken from the runes. It comes in every weight from Light to Bold, and it also draws the Elder Futhark.

![Runion Neo specimen](documentation/specimen.png)

To try it, open [`index.html`](index.html) or run `make serve`. The playground has a type tester with a weight slider, a table of every character and a sketchpad for drawing glyphs on the dots.

The font is one variable file, [`fonts/variable/RunionNeo[wght].ttf`](fonts/variable/RunionNeo%5Bwght%5D.ttf), with any weight from 300 to 700 and named Light, Regular, Medium, SemiBold and Bold. The web version is [`fonts/webfonts/RunionNeo[wght].woff2`](fonts/webfonts/RunionNeo%5Bwght%5D.woff2). The licence is the [SIL Open Font License 1.1](OFL.txt).

![Light to Bold](documentation/weights.png)

## The system

![Construction on the dot grid](documentation/grid.png)

The font is drawn on one grid of 3 columns and 7 rows of dots. A glyph is a list of lines between dots. Lowercase a is `00-16-20 02-22`: up from the bottom left to the top middle, down to the bottom right, and a bar across.

| Rule | What it means |
| --- | --- |
| Dot to dot | Every line starts and ends on a dot. Any dot can join any other dot, neighbour or not. There are no curves. |
| Full width | Every letter and digit touches both the left and the right column. |
| One pen | One line thickness for everything in a weight: 32 units in Light, 50 in Regular, 74 in Bold (`@light`, `@stroke`, `@bold` in the source). The dots never move between weights; only the pen changes. |
| The nib | Ink at a dot stays inside that dot's square, the nib. Corners are mitred and clipped to it, and line ends are cut flush with the grid, so every glyph has the same outer box. |
| Dots | A dot that stands free is 1.4 pens wide (`@dot`), because a small square reads lighter than a line of the same width. Where a dot that big would crowd a line, it shrinks back towards one pen. |
| Unicase | Lowercase and capitals are the same height. A lowercase letter is the plain letter, and its capital is the same letter with an ornament. |
| Marks | Accents sit outside the letter, in two rows above and two below. Every glyph fills the same box, so one mark position fits all of them. The 140 or so accented letters are composed by the build from Unicode: letter plus mark. |

### Lowercase

The lowercase is sharp. O is four lines, a diamond. C is two strokes and G is C with a stem and a short bar that stops short of the first strokes. D is a stave and a point. P is a flag on the stave; R is P with a leg, and B is P with the flag mirrored below. S runs from the upper right down to the middle left, across, and down to the lower left.

### Capitals

A capital is its lowercase letter ornamented with dots and/or lines. Many of the ornaments come from runes.

| Capitals | Ornament |
| --- | --- |
| A T | A second crossing bar, like the two arms of ansuz ᚨ: A's sits right above its own, T's below its top. |
| E | The middle line splits in two, one step up and one step down. |
| H | Dagaz ᛞ itself: the bar becomes a cross between the staves. |
| I | A crossbar through the middle of the stem. |
| L | A second bar right above its foot. |
| F | Fehu ᚠ itself. |
| K | The arms meet in the middle, like kaunan ᚲ. |
| M W | The cross of mannaz ᛗ. |
| N | A short branch from the middle of the first stave down to the bottom middle. |
| P | The flag's diagonal is doubled two steps lower and closed at the right. |
| D | Two lines from the stave, crossing inside the triangle. |
| J | A short stem hanging free under the top bar. |
| Y | Algiz ᛉ: the Y with its stave continued to the top. |
| X Z | A bar across. |
| B C G O Q R U V | One dot, in the counter or, for B, C and R, at the middle right. Medieval carvers made new letters from runes the same way, with a dot: the stung runes. |
| S | Two dots, one in each counter. |

The other letters follow the same rules. Æ, Œ and Ð split their middle bar like E. ø is the diamond with a slash; Ø has a cross through the middle of the diamond instead. Å is drawn, not built from A and a ring: the A comes down one step and the ring becomes a dot above its tip. Capital Þ is the rune thurisaz ᚦ, the rune the letter comes from.

All of it is defined in one text file, [`sources/glyphs.txt`](sources/glyphs.txt).

## Using the font

```css
@font-face {
  font-family: "Runion Neo";
  src: url("RunionNeo[wght].woff2") format("woff2");
  font-weight: 300 700;
}
.neo { font-family: "Runion Neo", monospace; font-weight: 300; }   /* any weight from 300 to 700 */
```

Runion Neo is made for display: headlines, titles, signs and short text. On an ordinary screen it reads well from 16 px. At 12–14 px, use Regular or Bold; Light needs about 18 px. On high-resolution screens such as phones and Retina displays, every size halves.

| Feature | Default | Effect |
| --- | --- | --- |
| `mark` | on | Combining accents attach to any letter or rune. |
| `ccmp` | on | Draws a/A + U+030A (combining ring) as å/Å, and ᚨ + U+030A as ansuz with a third arm. |
| `ss01` | off | The older four-stroke form of the rune ᛊ. Turn it on with `font-feature-settings: "ss01"`. |

The font covers the Google Fonts Latin Core set (319 characters) and the runes described below.

## Building

```bash
make venv     # once: Python environment with fontmake, ufoLib2, shapely, pillow, gftools, fontbakery
make build    # glyphs.txt → UFOs → fonts/variable, fonts/webfonts, playground data
make gftools  # the Google Fonts path: gftools builder compiles fonts/ from sources/config.yaml
make proof    # contact sheet (out/) and documentation images
make test     # fontbakery, Google Fonts profile
```

`sources/glyphs.txt` is the source. `sources/build.py` turns it into three master UFOs (`sources/RunionNeo-Light.ufo`, `-Regular.ufo`, `-Bold.ufo`) and `sources/RunionNeo.designspace`, and compiles the variable font from them with fontmake. In the masters every line, corner and dot is a separate piece, so each glyph has the same points at every weight and the masters interpolate exactly. `sources/runion.py` turns the dots and lines into outlines.

The master UFOs and the designspace are committed, so the font can also be built without `glyphs.txt`: `sources/config.yaml` lets `gftools builder` compile it (`make gftools`). After changing `glyphs.txt`, run `make build` first so the masters are up to date. Every push is built and checked with fontbakery by GitHub Actions; the font and the report are attached to each run.

To change a glyph, edit its line in `glyphs.txt` and run `make build`. The sketchpad in the playground writes the stroke code for you.

## The runes

![The 24 runes of the Elder Futhark](documentation/futhark.png)

The font draws the 24 runes of the Elder Futhark, the oldest runic alphabet (2nd–8th century), on the same grid. They sit at their own codepoints in the Unicode Runic block and keep their historical structure. A few later runes are included as well: ᚳ ᚻ ᛝ from the Anglo-Saxon row, ᛅ from the Younger Futhark, the medieval ᚯ ᚧ ᚡ ᛩ, and the runic punctuation ᛫ ᛬ ᛭.

The font never turns Latin letters into runes. To write in runes, the text itself has to contain runes, so that copying, searching and screen readers get runes too. The playground's "write in runes" switch converts what you type: letter by letter it follows the Elder Futhark, `th` becomes ᚦ and `ng` becomes ᛜ, and later runes fill the gaps (ᚳ for c, ᛩ for q, ᚡ for v, ᛅ for æ, ᚯ for ø). A keyboard layout with the Runic block works too.

Where the narrow grid made a choice necessary:

| Rune | Choice |
| --- | --- |
| ᚲ ᛃ ᛜ | These runes have no stave, and reference charts usually draw them smaller. Here they are full height. |
| ᛒ ᚹ ᚱ | Two symmetric 45° bowls would need nine rows, so the bowls are steep on the outside and shallow on the inside. |
| ᛞ | A cross from corner to corner clogs at this width, so a smaller 45° cross joins the staves. |
| ᛊ | The three-stroke form; the older four-stroke form of the Kylver Stone (c. 400) is the `ss01` alternate. |
| ᚧ | The reference form has a dot; a bar reads better inside the bowl. |
| ᚨ + ◌̊ | Ansuz followed by a combining ring draws ansuz with a third arm, for å. Fonts without this drawing show ᚨ with a ring, which means the same. |

Some letters share their shape with a rune on purpose: o and ᛜ, c and ᚲ, F and ᚠ, H and ᛞ, M and ᛗ, Þ and ᚦ. They are separate glyphs at their own codepoints. Runion is a typeface and makes no claim to be a scholarly reconstruction.

## How it was made

Runion Neo grew out of [Runion Basic](https://github.com/OneManMobile/Runion-Font), which shows runes when you type Latin letters. Neo keeps its grid, engine and runes and adds a real Latin alphabet, so Latin text is Latin and runic text is runic.

Runion Neo was made with AI. I worked with Claude, Anthropic's AI model, in Claude Code. I set the concept and the rules: the dot grid, full-width letters, one pen per weight, the ornamented capitals, and the letterforms themselves. I decided what to keep and what to change, and reviewed the results as we went. Claude drew constructions on the grid, wrote the build code and the playground, researched the history and drafted this README. No existing font data or outlines were used. Every outline is generated from `sources/glyphs.txt`.

## Licence

Copyright 2026 The Runion Neo Project Authors (https://github.com/OneManMobile/runion-neo).

This Font Software is licensed under the SIL Open Font License, Version 1.1. The licence is in [`OFL.txt`](OFL.txt) and is also available with a FAQ at https://openfontlicense.org.
