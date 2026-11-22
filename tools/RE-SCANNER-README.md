# RE Scanner

`tools/re_scan.py` is the first deterministic static-analysis accelerator for NewEstymaCan.

Scope:
- direct BL/BLX/branch XREFs
- indirect BLX/BX candidates
- PC-relative literal loads
- MOVW/MOVT immediate candidates
- memory/object references
- exact LE32 literal occurrences for selected targets

Address model:
- TRUE base 0x08010000
- PROJECT = TRUE - 0x10000
- RAW = TRUE - 0x08010000

Example:
python3 tools/re_scan.py FW2213TK_kopia.bin --target 0x08010FCE --target 0x0806E59C --target 0x08057224 --target 0x080629FC --out analiza/generated/re_scan

Evidence rule: direct references are mechanical observations. Indirect edges are not resolved without independent runtime/object/vtable evidence.