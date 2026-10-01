# Runion Neo

Latin and the Elder Futhark on a grid of 3 × 7 dots. Straight lines only, from any dot to any dot. Monospace, narrow and tall, every letter fills the full width of a cell.

![Runion Neo specimen](documentation/specimen.png)

Runion Neo is a Latin typeface built from runes. Type ordinary text and you get Latin letters. Each capital is drawn as its lowercase letter plus a rune accent. The runes have their own Unicode codepoints (ᚠᚢᚦᚨᚱᚲ…), and the font draws them too.

Runion Neo comes from [Runion Basic](https://github.com/OneManMobile/Runion-Font), which shows runes when you type Latin letters. Neo keeps Basic's grid, engine and runes. It adds a real Latin alphabet, so Latin text is Latin and runic text is runic.

To try it, open [`index.html`](index.html) or run `make serve`. The playground has a type tester (with a switch that writes your text in runes), a table of every character and a sketchpad for drawing glyphs on the dots.

The font files are [`fonts/ttf/RunionNeo-Regular.ttf`](fonts/ttf/RunionNeo-Regular.ttf) and [`fonts/webfonts/RunionNeo-Regular.woff2`](fonts/webfonts/RunionNeo-Regular.woff2). The licence is the [SIL Open Font License 1.1](OFL.txt).

## The system

![Construction on the dot grid](documentation/grid.png)

The font is drawn on one grid of 3 columns and 7 rows of dots. A glyph is a list of lines between dots. Lowercase a is `00-16-20 02-22`: up from the bottom left to the top middle, down to the bottom right, and a bar across.

| Rule | What it means |
| --- | --- |
| Dot to dot | Every line starts and ends on a dot. Any dot can join any other dot, neighbour or not. There are no curves. |
| Full width | Every Latin letter and digit touches both the left and the right column. |
| One stroke | One line thickness for everything (`@stroke` in the source). |
| The nib | Ink at a dot stays inside that dot's square, the nib. Corners are mitred and clipped to it, and line ends are cut flush with the grid, so every glyph has the same outer box. |
| Unicase | Lowercase and capitals are the same height. A lowercase letter is the plain letter, and its capital is the same letter with a rune accent. |
| Marks | Accents sit outside the letter, in two rows above and two below. Every glyph fills the same box, so one mark position fits all of them. The 140 or so accented letters are composed by the build from Unicode: letter plus mark. |

### Capitals

A capital is its lowercase letter with a rune accent: an added or split stroke, or a rune's own shape. Where nothing can be added, it gets a dot.

| Capitals | Accent |
| --- | --- |
| A T | A second crossing bar, like the two arms of ansuz ᚨ: A's sits right above its own, T's below its top. |
| E H | The middle line splits in two, one step up and one step down, and the old line becomes the space between them. |
| I | The bars stay, and the diamond of ingwaz ᛜ fills the space between them. |
| P | Wunjo's ᚹ shape: the bowl comes to a point on the stave. |
| F | Fehu ᚠ itself. |
| K | Branches: the arms meet in the middle like kaunan ᚲ. |
| L | A second bar right above its foot. |
| N | A middle stave through the diagonal, like the stave of naudiz ᚾ crossed by its bar. |
| M W | The cross of mannaz ᛗ. |
| Y | Algiz ᛉ: the Y with its stave continued to the top. |
| X Z | A bar across. |
| J | A short stem under the top bar, hanging free between the bar and the hook. |
| B C D G O Q R U V | These have no line to add, so they get one dot, in the counter or, for B, C and R, at the middle right in the open mouth. Medieval carvers made new letters from runes the same way, with a dot: the stung runes. |
| S | Two dots, one in each counter: upper right and lower left. |

Æ, Œ, Ð, Ø, Þ, ẞ, Ħ and Ł follow the same rules. Æ, Œ and Ð split their middle bar like E. Ø gets two slashes, the strokes of the medieval ø rune ᚯ. Capital Þ is thurisaz ᚦ itself, the rune the Latin letter comes from.

The lowercase letters are sharp too. O is four lines, a diamond, the same shape as ingwaz ᛜ. C is two strokes, the angle of kaunan ᚲ. G is four: C, then up to the middle and a bar inwards that stops short of the first strokes. Capital G's dot sits in the mouth above that bar. D is three strokes: a stave and a point. P is three strokes too, a flag on the stave; R is P with a leg (four strokes) and B is P with the flag mirrored below. S is three strokes: from the upper right down to the middle left, across to the middle right, and down to the lower left.

All of it is defined in one text file, [`sources/glyphs.txt`](sources/glyphs.txt).

## Historical ties

![The 24 runes of the Elder Futhark](documentation/futhark.png)

The Elder Futhark is the oldest runic alphabet. It has 24 runes and was used by Germanic peoples from about the 2nd to the 8th century. The oldest securely dated inscription is the Vimose comb, from about 160 AD. The name comes from the first six runes: f, u, þ, a, r, k. The angular shapes are presumably an adaptation to cutting in wood and metal. Runion follows the same constraint.

These are not the Viking runes. The Elder Futhark belongs to the Roman Iron Age and the Migration Period, and it was already being replaced when the Viking Age began. The Vikings wrote with the Younger Futhark, which has only 16 runes, so one rune covers several sounds: ᚢ stood for u, o, v, w, y and ø, and ᚴ for k, g and ŋ. Towards the end of the Viking Age carvers started adding stung runes, a rune marked with a dot or a bar to show a second sound. By the early 13th century these medieval runes matched the Latin alphabet letter for letter. The Anglo-Saxon futhorc went the other way and added new runes.

The rune names used here (fehu, uruz, thurisaz and the rest) are scholarly reconstructions of Proto-Germanic words, worked out from later rune poems. None of them is attested in an Elder Futhark inscription.

Some of the objects the shapes come from:

- The Kylver Stone (Gotland, Sweden, c. 400) is a slab that sealed a grave. It carries the earliest known listing of all 24 runes in order.
- The Vadstena bracteate (Sweden, c. 500) is a gold pendant. It lists the row with dots dividing it into three groups of eight, the *ættir*. It was stolen from the Swedish Museum of National Antiquities in 1938 and has not been found.
- The Golden Horns of Gallehus (Denmark, early 5th century) carried one of the earliest full sentences in runes, *ek hlewagastiz holtijaz horna tawido*: "I Hlewagastiz Holtijaz made the horn". The horns were stolen in 1802 and melted down for the gold.
- Codex Runicus (c. 1300) is a law book, the Scanian Law, written entirely in medieval runes. Runes were still a working script long after the Viking Age.

### The runes in the font

All 24 Elder Futhark runes are at their own Unicode codepoints. They keep their historical structure and orientation and were checked against reference glyphs for the Unicode Runic block. A few later runes are included as well:

| Rune | Notes |
| --- | --- |
| ᚳ cen, ᚻ haegl, ᛝ ing | From the Anglo-Saxon futhorc. Haegl has two bars where hagalaz ᚺ has one. |
| ᛅ ár | The Younger Futhark a/æ rune. It developed from jera ᛃ: when Proto-Norse *\*jāra* lost its initial j, the rune's sound changed from j to a. |
| ᚯ ø, ᚧ eth, ᚡ v | Medieval stung runes: a stave struck twice, thurisaz with a bar, fehu with a dot. The reference form of ᚧ has a dot. Runion uses a bar because a dot clogs inside the bowl. |
| ᛩ q | The medieval q rune. |
| ᚨ + ◌̊ | Typing ansuz followed by a combining ring above (U+030A) gives ansuz with a third arm, for å. Fonts without this drawing show ᚨ with a ring, which means the same thing. |

The differences come from the narrow grid:

| Glyph | Status |
| --- | --- |
| ᚲ kaunan, ᛃ jera, ᛜ ingwaz | These runes have no stave, and reference charts usually draw them smaller than the rest. Here they are full height. |
| ᛒ berkanan | Two symmetric 45° bowls would need nine rows, so the bowls are steep on the outside and shallow on the inside. ᚹ wunjo and ᚱ raido use the same bowl. |
| ᛞ dagaz | A cross from corner to corner clogs at this width, so a smaller 45° cross joins the staves. |
| ᛊ sowilo | Drawn in the three-stroke form, which is more common from the 5th century on (the Gallehus horns). The older four-stroke form of the Kylver Stone is the `ss01` alternate. |

Runion is a typeface and makes no claim to be a scholarly reconstruction.

## Using the font

```css
@font-face {
  font-family: "Runion Neo";
  src: url("RunionNeo-Regular.woff2") format("woff2");
}
.neo { font-family: "Runion Neo", monospace; }
```

| Feature | Default | Effect |
| --- | --- | --- |
| `ccmp` | on | Draws ᚨ + U+030A as ansuz with a third arm. |
| `ss01` | off | The four-stroke ᛊ of the Kylver Stone. Turn it on with `font-feature-settings: "ss01"`. |
| `mark` | on | Combining accents attach to any letter or rune. |

The font covers the Google Fonts Latin Core set (319 characters), the 24 Elder Futhark runes, the later runes above and the runic punctuation ᛫ ᛬ ᛭.

### Writing in runes

The font never turns Latin letters into runes. To write in runes, the text itself has to contain runes, so that copying, searching and screen readers get runes too. The playground's "write in runes" switch converts what you type to runic codepoints. Letter by letter it follows the Elder Futhark, `th` becomes ᚦ and `ng` becomes ᛜ, and later runes fill the gaps: ᚳ for c, ᛩ for q, ᚡ for v, ᛅ for æ and ä, ᚯ for ø and ö. For y it uses eihwaz ᛇ, the yew rune; its sound value is disputed and it was not a y. You can also type runes directly with a keyboard layout that has the Runic block.

## Building

```bash
make venv     # once: Python environment with fontmake, ufoLib2, shapely, pillow
make build    # glyphs.txt → UFO → fonts/ttf, fonts/webfonts, playground data
make proof    # contact sheet (out/) and documentation images
make test     # fontbakery, Google Fonts profile
```

`sources/glyphs.txt` is the source. `sources/build.py` converts it to `sources/RunionNeo-Regular.ufo` and compiles that with fontmake, so the font can be built and reviewed with standard tools. `sources/runion.py` turns the dots and lines into outlines.

To change a glyph, edit its line in `glyphs.txt` and run `make build`. The sketchpad in the playground writes the stroke code for you.

## How it was made

Runion Neo was made with AI. I worked with Claude, Anthropic's AI model, in Claude Code. I set the concept and the rules: the dot grid, full-width letters, one stroke width, the rune accents on the capitals, and specific letterforms such as A, E and H. I decided what to keep and what to change, and reviewed the results as we went. Claude drew the glyph constructions on the grid, wrote the build code and the playground, researched the history and drafted this README. No existing font data or outlines were used. Every outline is generated from `sources/glyphs.txt`.

## Licence

Copyright 2026 The Runion Neo Project Authors (https://github.com/OneManMobile/Runion-Neo).

This Font Software is licensed under the SIL Open Font License, Version 1.1. The licence is in [`OFL.txt`](OFL.txt) and is also available with a FAQ at https://openfontlicense.org.
