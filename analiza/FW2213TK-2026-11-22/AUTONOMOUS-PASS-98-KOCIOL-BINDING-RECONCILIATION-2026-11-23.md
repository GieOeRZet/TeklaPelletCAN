# AUTONOMOUS PASS 98 — KOCIOŁ UI BINDING RECONCILIATION

## Result
Cross-checking the static presenter findings against the independent PASS 63 PID-diff pilot closes four concrete Kocioł widget bindings and one partial binding.

### HARD closures
- PID 0x370A -> widget 0x20016894, image; values 1/2/3 select bitmap 11/12/13.
- PID 0x350D -> widget 0x20016A94, text Ciśnienie=; 0 hides and 1 shows.
- PID 0x350A -> widget 0x20016A24, text T. powrotu=; 0 hides and 1 shows.
- PID 0x2005 -> widget 0x20016918, boiler on/off icon; 0 -> bitmap 120, 1 -> bitmap 122.

### Partial closure
PID 0x2277 is confirmed as Boiler pump state and its visible effect is bitmap 138, but the exact widget address is not present in the recovered PASS 63 fragment. It is therefore not fabricated here.

## Evidence boundary
PASS 63 supplies deterministic two-run PID-diff evidence. PASS 89 supplies the independent static condition/presenter interpretation. Agreement between the two is used as reconciliation, not as replacement for missing static evidence.

## S4 status
Kocioł pressure/return/boiler-image/on-off bindings are closed. Pump widget address remains OPEN. Palnik/Ogrzewanie/Woda still require their own closure.


## CORRECTION — PASS 98 post-audit
The earlier draft incorrectly attributed bitmap 138 directly to PID 0x2277. PASS 63's actual pilot data shows widget `0x200162F8` is a live pump animation (frames 138→142), while the explicit static/PID-diff binding for bitmap 138 is **PID 0x22A1 Room temp sensor type**: value 5 hides that widget; values 0/1/2 show it. Therefore the old `0x2277 -> bitmap 138` statement is REJECTED. PID 0x2277 remains a live pump-state source, but its isolated widget binding is not proven by the 0x584 pilot. This correction is now the authoritative result.
