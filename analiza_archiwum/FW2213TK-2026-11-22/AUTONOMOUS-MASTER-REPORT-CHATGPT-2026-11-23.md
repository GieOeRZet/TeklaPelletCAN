# AUTONOMOUS MASTER REPORT — CHATGPT STATIC REVERSE ENGINEERING — 2026-11-23

## Scope
Continuation of the delegated static NewEstyma/FW2213TK work. Existing analysis was reused; no raw-Ghidra restart was performed. Claude-owned runtime/UI files were not modified.

## Passes completed in this autonomous run
- PASS 86 — presenter offsets scanner / initial verified offsets.
- PASS 87 — UI key→PID pilot mappings.
- PASS 88 — menu/view callback pattern.
- PASS 89 — visibility rules.
- PASS 90 — formatter examples.
- PASS 91 — alarm audit.
- PASS 92 — missing screens inventory.
- PASS 93 — dialog inventory.
- PASS 94 — 23-entry Parameters-set catalog.
- PASS 95 — live-source audit.
- PASS 96 — menu row→class→first-level handler closure.
- PASS 97 — generic alarm state-machine closure.
- PASS 98 — Kocioł binding reconciliation, subsequently corrected.
- PASS 99 — dual menu callback closure.
- PASS 100 — complete named alarm code/site inventory.
- PASS 101 — complete valid T2 internal UI-key→PID export (372 rows).
- PASS 102 — complete 137-setter presenter offset inventory.
- PASS 103 — Kocioł visual binding matrix.
- PASS 104 — presenter-level UI format inventory (174 variants).
- PASS 105 — four dialog-family mechanics closure.
- PASS 106 — four L3 wrapper structural closure.

## Critical correction
The earlier PASS 98 statement that PID 0x2277 directly corresponded to bitmap 138 was wrong and is REJECTED.

The recovered PASS 63 pilot explicitly shows:
- PID 0x22A1 (Room temp sensor type) controls widget 0x200162F8 visibility; value 5 hides it, 0/1/2 show it, with bitmap 138 as the baseline visual.
- The same widget 0x200162F8 is also the live pump-animation widget with frames 138→142.
- PID 0x2277 is the live Boiler pump state, but its value cannot be isolated by the local 0x584 pilot because EstymaTask refreshes live sensor values from the sensor-source path.

All PASS 98 artifacts and project-state text were corrected. Coordination contains an explicit REJECTED note.

## Major static closures
### Presenter/UI
- 137 unique presenter setters are indexed with all widget offsets already proven by the repository presenter map.
- T2 resolver now has a complete exported 372-row internal-key→PID table.
- Presenter-side formatting evidence is exported for 174 PID/format/div10 variants.
- Kocioł bindings closed for 0x350A, 0x350D, 0x2005, 0x2002, 0x216F, 0x3629, 0x370A and 0x22A1.
- 0x2277 remains a live-source binding requiring module/sensor-path dynamic evidence.

### Menu / callbacks
- Both menu callbacks are closed:
  - 0x0807EB00 → 0x0803C064 → runtime class table.
  - 0x0807EB36 → 0x0803EC18 → parameter/widget resolver.
- Rows 11–20 are closed at the first-level dispatch boundary.
- Final handler→page-constructor/resource chains remain open where the firmware uses indirect object graphs.

### Alarms
- Generic raise/active/unack/ACK/clear/reset state machine is closed.
- 31 named alarm codes have normalized Polish text and all recovered raise/clear sites.
- Per-site boolean business predicates remain open; they must be recovered from local CFG around each call site rather than inferred from alarm names.

### Dialogs
- PIN: 4 digits, +/- and OK; 0/0900/0999/6154 map to levels 0/1/2/3.
- Fuel: +/- and OK, PID 0x3601.
- Time: hour/minute selection and OK; panel RTC update confirmed.
- Generic value edit: descriptor-driven min/max/step and +/-/OK, CAN write path confirmed.
- Exact CAN TX caused by changing the time dialog remains open.

### Level-3
- Four previously open wrappers are structurally closed: >=3 gate, child +0x23C, init +0x210, common vtable slot-0 tail.
- Final semantic page identity remains open.

## Important carried-forward static OPENs
1. Final page constructor/resource/widget graph for menu classes 11/13/18/19/20.
2. Exact semantics of provider vtable slot 4 at 0x080422C8.
3. Exact per-alarm clear predicates.
4. Exact live-source PDO/module → PID mapping for live values such as 0x2001, 0x2277, 0x3333 and 0x4000.
5. Exact time-dialog TX/source direction.
6. Exact widget association of Ogrzewanie flags +0xA69/+0xA95 and the Buffer 7°C field.
7. Complete final screen inventories for PROGRAM, time dialog, charts/statistics and some service/configuration pages.
8. Full 655-PID formatter coverage beyond the presenter fields that have actual formatter evidence.
9. Full CFG proof for every instruction candidate in the 137 setter functions where the existing presenter map did not already establish the widget offset.
10. Exact semantics of some indirect class/selector fields in MenuTree.

## Dynamic dependency boundary
Where static code alone cannot safely resolve the result, the remaining work depends on Claude's dynamic emulator/module simulation or real CAN captures. The most important example is the live sensor source chain behind 0x2277 and related live PIDs.

## Repository artifacts
Every pass above has its own report/data/tool/test where applicable. Coordination was updated continuously on the coordination branch. No firmware binary was committed.

## Final assessment
The static delegated scope was driven forward through all actionable independent passes instead of stopping at the first OPEN. Remaining OPENs are now narrowed to concrete indirect/dynamic boundaries or per-site CFG work, not generic unknowns.
