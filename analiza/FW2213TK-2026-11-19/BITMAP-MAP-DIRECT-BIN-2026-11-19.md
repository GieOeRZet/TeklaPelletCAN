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
