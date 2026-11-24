# BATCH — SCREENSHOT 480x272 → BOTTOM 7 ZONES + SEPARATE RIGHT BUTTON — 2026-11-19

## New grounded evidence

User supplied a screenshot of the real panel UI. Screenshot is 954x547, approximately 1.9875x the firmware canvas of 480x272.

### Canvas / zones

- Firmware canvas: 480x272.
- Screenshot content transition from main area to bottom bar is at about y=412 px.
- 412 / 1.9875 ≈ 207 px, leaving ≈65 px; with border/rounding this is consistent with the already recovered bottom region of about 72 px.
- Bottom bar visibly contains 7 vertical zones:
  1. MENU
  2. fuel/hopper
  3. burner/flame
  4. heating CO1 (radiator + superscript 1)
  5. empty/other zone
  6. DHW/tap
  7. power
- This is strongly consistent with the firmware construction:
  - FUN_08047244 = one separate bottom component
  - FUN_08047290 creates exactly 6 repeated slots
  - total = 1 + 6 = 7 zones.
- Exact semantic mapping of all seven firmware slots remains a source-trace task; the screenshot itself confirms the visual count and the CO1 radiator location.

### CO/heating icon

The screenshot's heating tile is the fourth bottom zone and shows a radiator with superscript 1.

The repository's web implementation explicitly maps the bottom-bar bitmap IDs:
- MENU = 77
- CO = 144
- CWU = 174
- power = 115

Repository bitmap dimensions:
- 144.png = 41x36
- 115.png = 41x40

Therefore 144.png is the first direct asset candidate for the screenshot's CO/heating bottom-bar icon. This is much more plausible than bitmap 122.

### Important correction: bitmap 122 is NOT the bottom heating icon

Earlier investigation of the C33E/C5B4 object established:
- +0x8E0 is a Bitmap child.
- C5B4 writes resource ID 0x7A to +0x8E0.
- 0x7A decimal = 122.
- repository asset 122.png = 35x37.
- +0x8E0 X = 398, Y = runtime.

This places bitmap 122 in a completely different UI location: x=398 on the 480px canvas, i.e. around 83% of screen width. The screenshot's right-side 60 AUTO control is indeed a separate visual element in that region.

### Right-side control

The user explicitly identifies the right side as a separate button-like element, probably attached to the main/root parent rather than being part of the bottom CO tile.

This matches the architecture direction already recovered:
- C33E is a composite containing multiple child objects.
- +0x85C and +0x8E0 are separate Bitmap children.
- +0x8E0 is attached through parent+0x04.
- The right-side control should therefore be traced as its own child/widget hierarchy rather than folded into the bottom 7-zone component.

The 60 and AUTO text are not yet assigned to exact firmware TypedText/widget objects from this screenshot alone.

## Next trace priorities

1. Recover exact firmware construction of the 7 bottom zones and identify which child/resource is the CO1 radiator tile.
2. Trace Bitmap ID 144 from actual firmware construction/use, not only the web reconstruction.
3. Trace the right-side 60 AUTO control separately:
   - parent constructor
   - background/button resource
   - 60 TypedText/value widget
   - AUTO TypedText/value/state widget
   - exact X/Y/W/H
   - touch callback
   - parameter/model source.
4. Revisit C33E +0x8E0/bitmap 122 in light of the screenshot and determine exactly what the 35x37 asset represents.
5. Do not use screenshot colors as evidence; geometry and component boundaries are the useful evidence.

## Status

- 122.png remains a real firmware asset, 35x37.
- It is NOT accepted as the bottom heating icon.
- Bottom heating icon candidate is 144.png (41x36), with screenshot and repository web mapping supporting the identification.
- Exact original firmware call-site for 144 remains to be closed.
