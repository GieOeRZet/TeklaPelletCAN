# BATCH — HOME NEXT: 2E716 / 47E54 / 370A GRANICA — 2026-11-19

[FW] 47604 is ruled out as boiler graphics: 1158 B graph component, five-series logic, X/Y normalization, four moving 480x200 areas.

[FW] 47290 is ruled out as the six-zone bottom bar: six entries are vertically positioned around Y=50,84,118,152,186,220.

[FW] 47E54 -> 2DF80 remains an unresolved small composite. 47E54 has TypedText 468 at X=135,Y=60,W=200; no hard Bitmap ID yet.

[FW] FUN_0802E716 is now the next strong Home target: 648 B, instantiated at Home root +0x84F4. Nearby helper block: FUN_08034A2C/34A40/34A54/34A68/34A7C (16 B each), FUN_08034A90 (740 B), FUN_08034D74 (420 B). Resolve child creation/resource/geometry here.

[STRONG] 0x370A is a real configuration parameter named Boiler image selector: u8, 1..3, default 1, RAM 0x20021FA6, registration/callback 0x0801AB7E, snapshot raw 259 => value 3, group 0x3700. Do not assume it is derived from Device type/serial.

[FW] Hardware/profile 0x3500/3502/350B is a separate variant-selection layer. It may influence UI, but no direct 370A derivation is proven.

[FW] Bitmap writer is closed: FUN_080307BC writes resource ID to child+0x26; FUN_080469E8 uses child +0x4F and sets ID 14 -> 014.png (54x100). The unresolved problem is the caller supplying a variable resource ID.

Next priority: 2E716 -> bitmap/resource/geometry -> callback 0x0801AB7E/RAM 0x20021FA6 -> variable Bitmap ID -> 011..014. No 370A-to-asset mapping is accepted until a direct call-site is found.
