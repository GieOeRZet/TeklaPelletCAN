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
