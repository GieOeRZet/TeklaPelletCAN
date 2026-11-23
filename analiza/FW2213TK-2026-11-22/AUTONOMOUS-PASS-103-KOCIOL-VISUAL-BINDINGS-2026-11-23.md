# AUTONOMOUS PASS 103 — KOCIOŁ STATIC/PILOT VISUAL BINDING MATRIX

PASS 63 pilot evidence was re-read after the PASS 98 correction. This matrix records only bindings explicitly present in the pilot data. It separates configuration-driven visual bindings from live-source limitations.

### Key correction
Bitmap 138 is a configuration-driven visual associated with PID 0x22A1 in the pilot. The same widget address is also used by the live pump animation path, so widget identity alone must not be equated with one PID. PID 0x2277 remains a live pump source whose value cannot be injected through local 0x584.

### Closed matrix
0x350A, 0x350D, 0x2005, 0x2002, 0x216F, 0x3629, 0x370A and 0x22A1 have explicit widget/effect evidence. 0x2277 has explicit live-animation role but not an isolated value→widget diff.
