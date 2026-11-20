# RAW DATA PACK — EXTERNAL DEEP-ANALYSIS AGENT
Date: 2026-11-20
Target firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

## Purpose
This is an evidence packet for an independent high-compute reverse-engineering agent. The goal is to resolve the relation among:
- resolver index 0x68 / parameter 0x300B / UI label branch,
- graph registry entries 0x47 and 0x48,
- the two five-point characteristic families,
- model/record write/read paths and CAN parameter storage,
- actual configuration/equipment gate controlling the second fan curve page.

Do not restart asset extraction, graph geometry, resolver basics, or the 0x68 correction. Reconstruct full dataflow from committed source artifacts.

## Essential source files and object IDs
These artifacts are committed in this branch:

### Firmware outputs
- `firmware/FW2213TK-ghidra/decompiled.c`
  Git blob SHA: `9620d0c85259d34bb6a20d3b03b038945dfe4c1a`
  Size 1,095,461 bytes. Full Ghidra decompiled output.
- `firmware/FW2213TK-ghidra/functions.txt`
  Blob SHA: `f52c33cc8aa63e0cb377fb35715a2d8c3cdc4e8d`
- `firmware/FW2213TK-ghidra/strings.txt`
  Blob SHA: `402880a0cb4e398b4bfdb6cdf415effcc858abbf`

### Parameter/index mapping
- `rejestry/panel-fw-mapa-indeks-id.csv`
  Blob SHA: `952881d1905ff739ddf48047ff5a0017ad0ab766`
- `rejestry/panel-fw-parametry-FW2213TK.csv`
  Blob SHA: `af4b7f2bf9b5cf6214c22a5fbbc5a8fef612cb4a`
- `rejestry/REJESTRY.md`
  Blob SHA: `8993d90c261870f8ca2d9697e3dd543621ee1195`
- `rejestry/katalog-rejestrow.csv`
  Blob SHA: `73f225539901dabe7dd4413ca3547e5c6e4a070a`
- `rejestry/archiwum/igneo-katalog-calosc.csv`
  Blob SHA: `6860191b0c07c22e9d6ee187f699d17d2ede3ef7`

### Previous detailed analysis
- `analiza/FW2213TK-2026-11-20/MULTIPASS-19-0x68-RESOLVER-CORRECTION-2026-11-20.md`
  This is the correction report supplied by the user in the latest turn.
- `analiza/FW2213TK-2026-11-20/MULTIPASS-15-GRAPH-056-057-2261-227A-HARD-TRACE-2026-11-20.md`
- `analiza/FW2213TK-2026-11-20/MULTIPASS-16-REUSABLE-GRAPH-MARKERS-CONFIG-UI-2026-11-20.md`
- `analiza/FW2213TK-2026-11-20/MULTIPASS-17-BLOWER-FAMILIES-CONFIGURATION-2026-11-20.md`
- `analiza/FW2213TK-2026-11-20/MULTIPASS-18-DIRECT-STRING-AND-FAN-BRANCH-2026-11-20.md`
- `analiza/FW2213TK-2026-11-20/MASTER-HANDOFF-FOR-NEXT-AGENT-2026-11-20.md`
- `analiza/FW2213TK-2026-11-20/CHAT-CONTINUITY-INDEX-2026-11-20.md`

## Raw function snippets
An exact snippet bundle has been generated:
`analiza/FW2213TK-2026-11-20/RAW-DECOMPILED-SNIPPET-BUNDLE-0x68-GRAPH-REGISTRY-2026-11-20.md`

It preserves 25 function blocks from decompiled.c without semantic edits:
0803CF54
08043A36
0803EC18
08048624
0807EB36
0804752C
08047604
08048520
0803C064
08036FF2
080484B0
0803EECC
0803E5AC
08047D80
08047C1A
08047A8A
080307BC
08031CCC
08037212
080370C0
0803716E
08047BA6
08047B80
08043A74
08043B44

The full decompiled file is authoritative over the extracted snippet subset. Decompiled C is approximate; verify control flow/instruction semantics against raw Thumb disassembly.

## Established facts (do not re-derive unless testing contradictions)

### A. Resolver 0x68 correction
- `FUN_08036FF2(context, 0x68)` resolves to parameter ID `0x300B`.
- This mapping is at raw table around `0x37794`, specifically in the resolver's second lookup table.
- Do NOT confuse it with the first resolver table around `0x37B36`.
- `0x300B` is named **Stop burning wood**, type u8, range 0..1.
- Parameter definition occurs around raw `0x58DE`, with registration via `FUN_0801143C`.
- A writer path in firmware around `FUN_08031CCC` invokes `FUN_08037212(context, 0x68, 1)` (verify precise call-site and context from raw code).
- Therefore `0x68` is not an extra-fan ON/OFF/configuration gate. That earlier interpretation is REJECTED.

### B. UI label branch
- `FUN_0803CF54` calls:
  `value = FUN_08036FF2(*(param_1+8), 0x68)`
  `FUN_08043A36(*(param_1+0x0C), value)`
- `FUN_08043A36` sets label:
  - value == 1 → TypedText 182 = `Podajnik palnika`
  - value != 1 → TypedText 183 = `Wentylator wspomagający [%]`
- ID 183 EN = `Extra exhaust fan [%]`.
- It builds/replaces text object at parent +0xF74, with TypedText 168/169 also involved for the neighbouring -20/-10°C labels.
- The exact meaning of the parent/screen owning +0xF74 remains OPEN.
- The safe interpretation is: 0x300B selects a label variant between burner feeder and extra/exhaust fan, not proof of fan visibility/control.

### C. Graph parameter families
Family A (burner blower modulation):
| Resolver | Parameter | Meaning | Firmware default |
|---:|---:|---|---:|
| 0x4A | 0x2261 | blower curve point 1 / X=20% boiler power | 20 |
| 0x4B | 0x2262 | blower curve point 2 / X=40% | 30 |
| 0x4C | 0x2263 | blower curve point 3 / X=60% | 40 |
| 0x4D | 0x2264 | blower curve point 4 / X=80% | 50 |
| 0x4E | 0x2265 | blower curve point 5 / X=100% | 60 |

Family B (exhaust/extra fan curve):
| Resolver | Parameter | Meaning | Firmware default |
|---:|---:|---|---:|
| 0x4F | 0x2268 | exh. fan char. 1 | 20 |
| 0x50 | 0x226E | exh. fan char. 2 | 30 |
| 0x51 | 0x226F | exh. fan char. 3 | 40 |
| 0x52 | 0x2275 | exh. fan char. 4 | 50 |
| 0x53 | 0x227A | exh. fan char. 5 | 60 |

Important: panel index catalogue has non-contiguous external indices:
75..79 for family A; 80..83 and 87 for family B. The internal resolver sequence 0x4F..0x53 is a different namespace; do not pretend the CAN/PANEL indexes are contiguous.

Both are five values, not one ten-point curve.

### D. Shared graph machinery
- `FUN_0803EC18` iterates registry/table records based on caller context and current slot.
- It reads panel ID from record offset +0x20.
- It scans table at raw `0x3F008`, record stride `0x10`.
- For type byte = 5 and selector/panel key 0x47 or 0x48, it builds five X values (20,40,60,80,100), five runtime Y values from Family A or B and calls graph path `FUN_08048520`.
- The graph content is installed into dynamic host `parent + 0x84F4`, graph object `parent + 0x963C`.
- `FUN_08047604` constructs reusable graph widget.
- Five point objects are constructed/updated in that component.
- `FUN_08047C1A` computes point geometry.
- `FUN_08047D80` contains the direct write of bitmap 056 for graph point normal state.
- Bitmap 057 is a reusable selected-state resource but its direct writers `FUN_0804752C` and `FUN_080475A4` are in a separate consumer family; do not claim 057 is only written by graph update.
- `FUN_08047290` is unrelated six-slot vertical selector/list (151/152), not the graph.

### E. Registry / refresh dispatchers
- `FUN_08048624` iterates records beginning at object +0x84EC, stride 0x338, and dispatches into `FUN_0803EC18` when the event object matches.
- `FUN_0807EB36` iterates registry at object +0x3B4, stride 0x274, count byte +0x3B8 and dispatches into `FUN_0803EC18`.
- These are two caller contexts of the same general model/registry refresh routine.
- Do not assume +0x84EC registry and +0x3B4 registry are the same registry or same record class. Their differing strides are evidence of different registration layers.

## Questions for heavy agent — highest priority

1. **Decode the complete record table at raw 0x3F008.**
   - Parse all 16-byte entries, not just 0x47 and 0x48.
   - For each: key/secondary IDs, type, pointer, trailing flags, candidate string/data xrefs.
   - Resolve exactly what 0x47 vs 0x48 select.
   - Follow shared function pointer 0x0807F5EC: code/data references, incoming/outgoing calls, object type, constructor/factory, TypedText and screen title.
   - Verify whether 0x47 is Family A and 0x48 Family B, or if both are variants of the same graph/page content under a separate dynamic selector.

2. **Reconstruct caller object and registry model.**
   - Compare caller A `FUN_08048624` (stride 0x338, base +0x84EC) to caller B `FUN_0807EB36` (stride 0x274, base +0x3B4).
   - Identify record offsets +0x20, +0x07, +0x08, +0x0C and their constructors/writers.
   - Follow pointer/registration lifecycle for 0x0807F5EC and all registry entries.
   - Do not assume either is CAN's 0x2C record engine.

3. **Trace the actual extra-fan visibility/configuration gate.**
   - Search every consumer of Family B values 0x2268/0x226E/0x226F/0x2275/0x227A.
   - Trace upstream configuration parameters/module type/profile/IO add-on/boiler type.
   - Determine whether graph Family B is exposed by:
     a) hardware module class,
     b) configured actuator,
     c) 0x3500 main module / 0x3502 expansion / 0x350B profile,
     d) another specific setting.
   - The correct gate may be an object-presence registry instead of a single boolean parameter. Test this.
   - Do not reuse 0x68/0x300B as that gate.

4. **Trace 0x300B completely and separately.**
   - Follow writer FUN_08037212 from UI input to record store, commit/persist and CAN parameter 0x300B.
   - Verify whether 0x300B actually controls stopping a wood-burning mode or just changes label variant in a hybrid boiler configuration.
   - Identify all writers, readers and callers of FUN_08037212 with resolver index 0x68.
   - Investigate whether this param is specific to mixed-fuel/wood mode rather than fan hardware.

5. **Prove the dynamic content/page selection.**
   - Trace `FUN_0802EADE(host, content)` and determine how old/current page is swapped.
   - Identify which event/navigation key selects registry keys 0x47/0x48.
   - Recover page title TypedText IDs and touch callback path.

6. **Inspect function 0x0807F5EC**.
   - This is the shared pointer for entries 0x47/0x48.
   - It may be a callback/refresh method or an object method. Identify xrefs and vtable/class.
   - Check code region and function bounds in functions.txt. Do not assume it is a literal direct call just because stored in a record.

7. **Audit potential confusion between panel indices and internal resolver indexes.**
   - Internal resolver IDs 0x4A..0x53 are not the same as table keys 0x47/0x48.
   - Panel index values 75..83 and 87 in CSV are a third layer.
   - Build a 3-column mapping with proof for each conversion.

## Raw extraction tasks
The bundle includes source snippets, but heavy agent should independently verify and expand:
- dump bytes at 0x3F008 for a sufficient window (at least 0x100 bytes);
- dump words at 0x37794 and 0x37B36;
- dump 0x58D0..0x5900 around parameter 0x300B registration;
- dump code around 0x3D050..0x3D0A0 and 0x43A36;
- enumerate all Thumb BL/BLX references to 0x0807F5EC and 0x0802EADE;
- recover xrefs of 0x2268/0x226E/0x226F/0x2275/0x227A and 0x300B;
- compare all 16-byte records in the 0x3F008 table to functions and strings.

## Confidence and stale hypothesis ledger
HARD:
- 0x68 -> 0x300B
- 0x300B name/type/range
- branch 1 -> TypedText 182 and branch !=1 -> TypedText 183
- 0x4A..0x4E -> Family A values
- 0x4F..0x53 -> Family B values
- registry type=5 and key 0x47/0x48 go to the five-point graph construction branch
- graph UI is installed via dynamic host +0x84F4 / content +0x963C
- 47290 is not that graph

REJECTED:
- 0x68 is the extra fan ON/OFF/config gate
- 47290 is the graph
- the two five-point families are one ten-point curve
- internal resolver IDs are the same namespace as panel IDs/registry keys
- graph point Bitmap 057 is exclusive to the graph

OPEN:
- semantic meaning of 0x47 and 0x48
- exact hardware/configuration gate for Family B
- actual class and lifecycle behind 0x0807F5EC
- page title/content identity
- full 0x300B user interaction and persistence behavior

## Expected heavy-agent deliverables
Return:
1. raw disassembly excerpts with addresses and register provenance;
2. parsed table for all 16-byte entries at 0x3F008;
3. caller/vtable/constructor graph;
4. complete Family B gate dependency graph;
5. 0x300B write and persistence chain;
6. conclusions split HARD / STRONG / OPEN / REJECTED;
7. exact file names and Git commit hashes for new results.

Do not merely summarize this prompt. Perform the raw data analysis.
