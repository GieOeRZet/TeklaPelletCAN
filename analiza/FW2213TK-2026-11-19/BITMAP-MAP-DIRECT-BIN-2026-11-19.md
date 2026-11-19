# BITMAP MAP — FW2213TK.bin — DIRECT RAW EXTRACTION — 2026-11-19

## HARD SOURCE FACTS

- Source: `FW2213TK_kopia.bin`
- Firmware size: 2,031,616 bytes = `0x1F0000`
- **Correct firmware load base: `0x08010000`**
- Bitmap descriptor table: file `0x54450`, runtime `0x08064450`
- Descriptor stride: `0x14` = 20 bytes
- Original bitmap records: **188**, IDs `000..187`
- `76b.png` is NOT a firmware bitmap; it is a generated historical repo asset.
- Data: RGB565, 2 bytes/pixel.
- ExtraData: A8 alpha, `width*height` bytes, when the second pointer is non-zero.

## CRITICAL CORRECTION

Earlier extraction using:

`file_offset = runtime_pointer - 0x08000000`

is WRONG for this firmware and produces noisy/garbage-looking images.

Correct:

`file_offset = runtime_pointer - 0x08010000`

This correction is independently confirmed by bitmap 160: with `0x08010000` it renders as the actual dark 241x49 bottom configuration button.

## DESCRIPTOR LAYOUT

20 bytes:

- +0x00 u32 = RGB565 data pointer
- +0x04 u32 = extraData/A8 pointer (or 0)
- +0x08 u16 = width
- +0x0A u16 = height
- +0x0C u16 = solidRect.x
- +0x0E u16 = solidRect.y
- +0x10 u16 = solidRect.width
- +0x12 u16 = solidRect.height

## FULL DIMENSION MAP

The following groups cover **all 188 firmware bitmap IDs**:

```text
1x47: 171
15x4: 106,107
10x9: 025,068
10x14: 072
20x7: 108,109
9x21: 047
12x18: 004
18x12: 003,005
11x21: 029,030
10x24: 064
241x1: 170
19x19: 138,139,140,141,142,143
367x1: 071
18x21: 026
20x20: 056,057
440x1: 080
5x89: 150
23x21: 162
17x31: 063
30x18: 039
34x19: 046
20x34: 016
20x35: 116
27x27: 002,156
32x23: 153,154,155
30x26: 077
38x21: 180,181
25x33: 044
39x23: 091,092,093,094
30x30: 018,033
45x20: 184,185
27x34: 173
34x27: 001,008,009,010,034,035,036,037,038,040,041,042,058,059,060,061,065,066,067,105
30x31: 019,020,151,152
34x29: 051,052,053
6x166: 164,166
12x89: 149
33x33: 070
29x38: 043,045
41x30: 182,183
8x158: 023
35x37: 055,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137
60x22: 177,178
41x36: 144,145
37x40: 175
31x49: 159
38x40: 174,176
43x36: 146,147
98x16: 158
41x40: 115
52x36: 104,110,111,119,168,169
68x28: 027,028,031,032
39x50: 078,082,083,084,085,086,087,088,089,090,095,096,097,098,099,100,101
181x11: 186,187
46x46: 069
38x56: 062
10x242: 112,113,114
57x43: 050
21x126: 015
31x89: 148
29x155: 048,049
301x16: 163,165,167
134x37: 006,007
68x75: 073,074,075,076
54x100: 014
155x38: 102,103,117,118
83x96: 172
370x24: 157
284x35: 022
67x151: 179
241x49: 160,161
82x145: 013
105x126: 011
149x99: 017
108x141: 012
279x61: 021,024
480x45: 079
440x50: 081
118x209: 054
270x124: 000
```

## KEY VERIFIED SEMANTIC IDs

- 011/012/013/014 — boiler-related original graphics traced in firmware.
- 019/020 — checkbox normal/selected.
- 056/057 — graph point normal/selected; used by the fan-modulation graph.
- 070 — slider handle.
- 102/103 — large minus normal/active.
- 104 + 168/169 — small minus composite.
- 110/111 — large OK normal/active.
- 112/113/114 — slider-dialog background left/right/center pieces.
- 117/118 — large plus normal/active.
- 119 + 168/169 — small plus composite.
- 120..137 — operating-mode/time icon family.
- 138..143 — circular selector/arrow family.
- 151/152 — **normal/selected state pair used directly by FUN_08047290**.
- 160/161 — **real bottom configuration/settings button normal/active**.
- 163 — slider track.
- 165 — mode-slider fill.
- 167 — value-slider fill.
- 168/169 — small button background normal/active.
- 184/185 — large toggle normal/active.
- 186/187 — thin/value-slider elements.

## ARTIFACTS / REPRODUCTION

The direct extraction package created in this analysis contains:
- 188 PNGs directly decoded from the BIN,
- four contact sheets,
- complete CSV manifest with pointers, offsets, dimensions, solid rectangles, alpha presence and SHA-256,
- extraction script using the correct `0x08010000` load base.

The contact sheets are orientation maps only. For a semantic claim, inspect the single PNG and then trace its firmware resource ID to the call-site.

## DO NOT REPEAT

1. Do not treat 151/152 as 056/057.
2. Do not treat 47290 as the real bottom bar.
3. Do not use `0x08000000` as the pointer-to-file base for this firmware.
4. Do not call 76b a firmware resource.
5. Do not infer semantics from bitmap number order alone.

## VISUAL PAIR CHECK — 056/057 vs 151/152 — 2026-11-19

Direct-BIN PNGs were visually checked side-by-side. There are **two genuinely similar circular indicator pairs** that must not be conflated:

### Pair A — bitmap 056/057
- 056 = 20x20, normal/unselected circular point, no colored center.
- 057 = 20x20, selected circular point, cyan/green colored center.
- Firmware/card evidence identifies this pair as the five-point fan-modulation graph marker.
- The five graph registers previously identified are 0x2261..0x2265 (20/40/60/80/100%).

### Pair B — bitmap 151/152
- 151 = 30x31, normal/unselected circular control, no colored center.
- 152 = 30x31, selected circular control, cyan/green colored center.
- Raw firmware call-site evidence identifies this pair specifically with FUN_08047290 / FUN_08047334.
- 47290 is the six-slot **vertical** list/selector; it is NOT the bottom bar.

### Important visual conclusion
The visual similarity is real, but the dimensions and firmware call-sites are different:
056/057 = 20x20 graph points
151/152 = 30x31 47290 selector states

The direct-BIN extraction currently shows the center as cyan/green in these selected variants. **Do not label it yellow without a separate color-space check or original display evidence.**

### Additional related state pair
- 184/185 = 45x20 large toggle normal/active. This is a different geometry and should not be grouped with the two circular pairs above.

## DIRECT-BIN EXTRACTED ARTIFACT SET

The working extraction produced the complete 188-image set from FW2213TK_kopia.bin under the local analysis path:
`/mnt/data/tekla_bitmap_extract_directbin_2026-11-19/png/000.png ... 187.png`

The set is accompanied by a generated manifest containing W/H, PNG byte size and SHA-256 for every image. The repository's canonical documentation records the extraction parameters and dimension map; the separate PNG set should be treated as the exact decoded output of that pass, not as the older web/img/panel atlas.

Extraction reproducibility:
- source: FW2213TK_kopia.bin
- load base: 0x08010000
- descriptor table: file 0x54450
- stride: 0x14
- records: 188
- RGB565 + optional A8

## HASH ANCHORS FOR THE TWO CONFUSABLE PAIRS

056.png SHA-256: 9d6fe5ce7f99495a1388be8bc97e29537fa1cd6d3ac9eecfa35ddb0286f4b3a2
057.png SHA-256: ae19e8557619fd9bbbf2caf49c3a7b6da00205bb244436662415abc595cdcb5f
151.png SHA-256: 6084705837b101fa56d4b5e517792037986e2f2440107cfa58f56b8dd1c79a16
152.png SHA-256: de91aab8b30f9eb29d0d4c0a7fc236e1d1fd606868e176fc4287d49a4b163b9c


## UI RESOURCE SEMANTICS — USER CONFIRMATION 2026-11-19

The user has now confirmed from the real UI/screens that bitmap resources 184/185 and 69/70 are reused across multiple controls/screens. Treat these as user-observed semantic evidence, separate from firmware call-site proof.

### 184/185 — large ON/OFF toggle
- 184/185 form the ON/OFF toggle itself.
- One state is used with the knob/selector resources 69/70 in the main Power view, lower-right corner, for boiler ON/OFF.
- The same 184/185 toggle mechanism is reused in settings such as DHW/CWU -> Menu -> Anti-legionella and other places, including 'heat now' and other ON/OFF-type controls.
- Therefore 184/185 must NOT be documented merely as a generic settings-row toggle; it is a reusable toggle control family used in the main power view and multiple settings/action screens.

### 69/70 — selector/knob resources with multiple roles
- 69/70 are used as part of the 184/185 ON/OFF selector/knob mechanism in the main Power view and elsewhere.
- The pair is also reused in sliders for temperature and heating mode for CO/DHW (CWU), and in additional slider controls elsewhere.
- Do not assign 69 or 70 exclusively to one widget. Their exact per-state/per-widget role must be established from firmware call-sites and visual geometry.

### Important correction to previous documentation
Previous notes that described 184/185 simply as a generic 'large toggle' were incomplete. The canonical interpretation is now: **reusable ON/OFF toggle family, including main Power-screen boiler ON/OFF and multiple settings/action screens**.
Previous notes that treated 69/70 only as a slider/knob pair were also incomplete: **they participate both in toggle controls and in multiple slider controls**.


## USER-CONFIRMED SLIDER MODE ICONS — 2026-11-19

User confirms that bitmap IDs **130–137** are the four mode icons used above the sliders. The UI composition has four icon positions per slider, with active/inactive states (4x2 states). The previously supplied screenshot is only a visual reference; exact dimensions, colors and layout must still come from the direct-BIN bitmap data and firmware call-sites.

Do not treat 130–137 as generic unrelated mode/time icons anymore: they are now user-confirmed as the slider mode-icon family. The exact mapping of each ID to icon position and active/inactive state remains to be established from firmware/resource references.


## USER-CONFIRMED 130–137 STATE RULE — 2026-11-19

For the slider mode-icon family 130–137, the user confirms the visual state convention:
- **thinner icon = OFF / inactive**
- **thicker/bold icon = ON / active**

This is user-observed UI evidence. Exact ID-to-icon-position pairing remains to be established from firmware/resource call-sites. Do not infer the individual numeric ordering from thickness alone until the BIN/reference analysis confirms it.


## USER-CONFIRMED CONFIG WINDOW TILE CONSTRUCTION — 2026-11-19

User confirms that bitmap resources **112, 113, 114** form a reusable construction used by some configuration windows, including the type of configuration window shown in the supplied screen/reference.

Confirmed semantic assembly:
- **112 = left element**
- **113 = right element**
- **114 = repeated fill/middle element** (114, 114, 114, ...)

Thus the window/background is assembled as a tiled/segmented structure:
**112 + 114×N + 113**.

The supplied screen is a visual reference for how the composed window looks; it is not authoritative for exact dimensions, colors, spacing, or repetition count. Exact geometry must still be taken from the direct-BIN resource dimensions and firmware construction code.


## USER-CONFIRMED BITMAP 051/052 — PELLET BIN TILE — 2026-11-19

User confirms that bitmap resources **051 and 052** are displayed on the **second tile from the left**, with the selected/used resource depending on the register that describes the amount/level of pellets in the hopper (pellet reservoir).

Semantic interpretation to preserve:
- location: second tile from the left;
- controlling data: a register describing pellet quantity/level in the hopper;
- resources: 051/052;
- exact state-to-ID mapping (which of 051/052 corresponds to which pellet level/state) is not yet asserted unless confirmed by firmware call-site or further user evidence.

Do not infer the exact threshold or register address from this note alone. The next firmware pass should trace references to resource IDs 051 and 052 and connect them to the pellet-quantity register/model value.


# 2026-11-19 — USER SEMANTIC CONFIRMATIONS / HANDOFF OVERRIDE

- 051/052: second tile from left; state depends on pellet hopper amount/level register. Exact threshold and 051-vs-052 state still OPEN.
- 130..137: four slider mode icons, each OFF/ON; thinner = OFF, thicker/bold = ON. Exact ID-to-position mapping OPEN.
- 112/113/114: reusable configuration-window construction: 112 left, 114 repeated middle/fill, 113 right.
- 184/185: reusable ON/OFF toggle family across Power screen and settings/action screens.
- 069/070: reusable selector/knob family, used with 184/185 and multiple sliders.
- 47290: vertical six-slot list/selector, never bottom bar.
- 160/161: real lower configuration/settings button.
- 056/057 and 151/152 are distinct circular pairs (20x20 vs 30x31).

For immediate visual orientation use:
`analiza/FW2213TK-2026-11-19/BITMAP-PREVIEW-MAP-2026-11-19.md`.
