# AUTONOMOUS PASS 99 — DUAL MENU CALLBACK DISPATCH CLOSURE

## Result
The previously OPEN sibling callback is now closed at machine/dataflow level. `FUN_0807EB36` uses the same sender registry (`this+0x3B4`, stride `0x274`) and row-index extraction as `FUN_0807EB00`, but dispatches to `FUN_0803EC18` rather than `FUN_0803C064`.

### Closed
- Primary callback: `FUN_0807EB00` → row index → `FUN_0803C064` → runtime class table `0x20005EF0` → first-level destination family.
- Secondary callback: `FUN_0807EB36` → row index → `FUN_0803EC18` → parameter/widget-list resolver path.
- Sender records are not individually assigned callbacks; the parent screen owns the callback and identifies the row by pointer arithmetic.

### Boundary
This closes the second callback's dispatch target, not the final semantic identity of every registry row or the final widget constructor chain. Those remain data/indirect-call questions.
