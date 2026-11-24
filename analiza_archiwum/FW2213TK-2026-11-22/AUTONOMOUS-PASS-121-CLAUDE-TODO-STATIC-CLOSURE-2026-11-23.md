# AUTONOMOUS PASS 121 — CLAUDE TODO STATIC CLOSURE AUDIT — 2026-11-23

## Purpose
Close every Claude-origin TODO that is already provable from committed static evidence, while explicitly isolating the items that require firmware execution/dynamic observation.

## A1 — hidden PINs
STATICALLY CLOSED.
- `FUN_08047E74`: only 900 -> level 1, 999 -> level 2, 6154 -> level 3; other values do not change access level.
- `FUN_08018634`: exact special constants are 1992, 6666 and 0, with lookup through the 23-entry runtime catalog.
- 6666 is the factory-reset request path: `FUN_08018634` sets storage PID 0x0005 (`0x20021FA7`) to 1.
- No fourth fixed access-level PIN is present in the proven handler.
- Do not promote unrelated firmware literals to hidden PINs.

## A2 — table of 23 values
MECHANISM/ROLE CLOSED, VALUE #23 STILL OPEN.
- `FUN_080144B4` iterates exactly 23 entries.
- The lookup is keyed by Parameters set Number (PID 0x0004), not a proven list of boiler powers.
- The 23-value catalog is used by the same special-reset path.
- Exact 23rd runtime value remains unavailable from current committed static artifacts and is therefore not guessed.

## B3 — level-gated UI
PARTIALLY CLOSED.
- Level != 0 gates are statically proven for main menu `0x0803C294`, Heating `0x08053DDC`, Buffer `0x08055A8C`, plus the already identified fourth gate `0x08054AB8`.
- Heating `7°C` is now HARD: presenter reads UI key `0xCB`, resolver maps it to PID `0x22F5` (CH needed temp), and setter `0x0805454E` formats the value into the view.
- Therefore the Heating-screen 7°C is NOT Buffer PID 0x2114.
- Buffer `0%` and Buffer `7°C` remain OPEN at widget->setter/PID level.
- `Ochrona kotła` helper inputs `0xB0`/`0xCD` and outputs A69/A95 are HARD, but exact label/image visibility binding remains OPEN.

## B4 — level-gate family
MECHANISM CLOSED, SPECIFIC REMAINING CONTEXTS OPEN.
- `0x08054AB8` is a level != 0 gate and its gated presenter/view offset `0x1498` maps to PID `0x201A` Hot water result temperature; context is therefore CWU.
- L>=3 wrappers form a common CPU-load/header gating family; exact individual screen contexts remain open where no callsite/resource proof exists.

## B1/B2 — dynamic-only
REMAIN WSTRZYMANE.
- B1: 6666 -> actual CAN PID 0x0005 frame and header +0x210 reaction.
- B2: whether `[0x2002466C+0x10] = (level != 0)` is the effective poller-enable condition.
These cannot be marked closed from static evidence alone.

## Verdict
Claude-origin static TODOs are now reduced to explicit evidence boundaries. No dynamic result is fabricated. The remaining closure requires either the firmware execution environment with `FW2213TK_kopia.bin` or a new raw CFG/XREF artifact.