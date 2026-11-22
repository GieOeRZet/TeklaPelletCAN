# AUTONOMOUS PASS 26 — PID 0x0117 RESOLVER NEGATIVE CLOSURE — 2026-11-22

## Objective

Resolve the remaining uncertainty from PASS 25 around PROJECT 0x08037212 and the value 0x0117 passed by the 0x0E access-table path.

## HARD — exact resolver behavior

PROJECT 0x08037212 receives:

- r1 = 0x0117 from PROJECT 0x0803C270
- r2 = row[i]+0x124 value
- manager pointer = 0x20008D84

The function first scans a 0x31-entry table at an ADR-derived address.

For each entry it compares:

- table[i].key against r8 = 0x0117

On a match it derives a PID from the entry and calls:

- PROJECT 0x08011812(manager, resolved_pid, value, type=5, ...)

If no match exists, the first loop is exhausted.

The second loop scans 0x174 entries from a second ADR-derived table and again compares its key against r8.

## NEW-HARD — 0x0117 has no static resolver-key match

Whole canonical BIN table inspection shows:

- first 0x31-entry resolver table: no key 0x0117;
- second 0x174-entry resolver table: no key 0x0117.

Therefore, for the canonical static tables:

0x08037212(r1=0x0117, ...)
-> no resolver-table match
-> no call to 0x08011812.

This is a negative closure and must be preserved.

The previous PASS 25 wording that the 0x0E path "reaches the parameter manager" is therefore corrected:

- it reaches the parameter-key resolver 0x08037212;
- it does NOT statically resolve to 0x08011812 for key 0x0117.

## Important related observation

The second resolver table does contain the pair:

- key 0x2123
- value/PID 0x0117

at RAW 0x3797A..0x3797D.

Therefore 0x0117 appears as a resolved value in the table, not as the key that the 0x08037212 input comparison expects.

This strongly suggests that 0x0117 is a final/derived identifier in this mapping structure, while 0x2123 is the corresponding resolver key.

Do not promote the semantic label beyond this machine-level relationship.

## Revised chain

The exact HARD chain is now:

0x20005F08[i] == 0x0E
-> row[i]+0x124
-> state object +0x10 == 1
-> PROJECT 0x0803C270
-> resolver key 0x0117
-> PROJECT 0x08037212
-> no static key match
-> no 0x08011812 call

The branch is therefore a non-resolving path under the canonical static resolver tables.

## HARD

- 0x0117 is absent as a key from both resolver tables used by 0x08037212.
- 0x0117 occurs as the value paired with key 0x2123 at RAW 0x3797A.
- The 0x0E access-table path therefore does not statically commit a parameter through 0x08011812 for key 0x0117.

## STRONG

- 0x0117 is likely an internal/final identifier rather than a resolver key.
- The 0x0E path may be a capability/update path that is inactive or intentionally non-resolving in this firmware configuration.

## OPEN

1. Identify what 0x0117 represents elsewhere in the firmware.
2. Identify the producer of row[i]+0x124 and determine whether 0x0E rows can actually produce a different key/value in runtime.
3. Resolve key 0x2123 -> value 0x0117 in the larger mapping and connect it to the 260-slot catalog.
4. Continue runtime-class 0..20 -> page/widget handlers.
5. Continue table writer/alias search.

## REJECTED

- "0x0117 is the final PID written by the 0x0E path" — unsupported.
- "0x08037212 always reaches 0x08011812 from this path" — disproven by the static table contents.
