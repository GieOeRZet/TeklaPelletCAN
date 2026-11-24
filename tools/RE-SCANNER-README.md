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
python3 tools/re_scan.py FW2213TK_kopia.bin --target 0x08010FCE --target 0x0806E59C --target 0x08057224 --target 0x080629FC --out analiza_archiwum/generated/re_scan

Evidence rule: direct references are mechanical observations. Indirect edges are not resolved without independent runtime/object/vtable evidence.

## Extended analysis tools

For the current runtime/object OPENs, the scanner suite now includes:

- `tools/vtable_scan.py` — finds executable-pointer table candidates and exact vptr literal occurrences.
- `tools/runtime_trace_analyzer.py` — turns RE-Harness `INDIRECT_CALL` and object metadata into concrete runtime edges.
- `tools/re_scan.py` additionally emits register-relative object operations as `object_ops`, allowing `base register + offset` tracking.

Recommended order:

1. `re_scan.py` for static candidates.
2. `vtable_scan.py` for vptr/vtable correlation.
3. `runtime_trace_analyzer.py` for runtime confirmation.
4. Only mark an indirect edge HARD when static object/vtable evidence and runtime evidence agree.
