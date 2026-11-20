# TeklaPelletCAN — PIN / ACCESS / RESET — MULTIPASS FORENSIC BATCH
Date: 2026-11-20
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## EXECUTIVE RESULT

The PIN/access path is now substantially closed.

The firmware contains one concrete touch/PIN decoding path:

`FUN_08042024` converts four entered decimal digits into an integer:
  digit0*1000 + digit1*100 + digit2*10 + digit3.

That value is passed by the menu/PIN callback through `FUN_08042328` to `FUN_0803C21C`.

`FUN_0803C21C` then executes two distinct mechanisms:

1. `FUN_08018634(context, entered_code)` — special-code / state handler.
2. `FUN_08037E74(context_model, entered_code)` — explicit access-level mapping.

The explicit access-level mapping is:

- 0900 = decimal 900 = access level 1
- 0999 = decimal 999 = access level 2
- 6154 = decimal 6154 = access level 3

This is direct raw-BIN proof.

The 6154 code is `0x180A`, hardcoded in `FUN_08037E74`.

The mapping is cumulative in the sense that entering 0900 writes level 1; entering 0999 writes level 2; entering 6154 writes level 3. The function does not lower the level for an unmatched nonzero code: if no match occurs, it returns without changing the existing +0x158 byte.

Therefore the user's observed:
- level 0 = base interface
- 0900 = level 1
- 0999 = level 2
is confirmed by firmware.

A third explicit access code exists:
- 6154 = level 3.

This is the strongest new result of this batch.

---

# PASS 01 — FOUR-DIGIT PIN DECODER

Function `FUN_08042024`:

```
ldrb digit0
digit0 * 1000
ldrb digit1
digit1 * 100
ldrb digit2
digit2 * 10
ldrb digit3
sum
uxth
return
```

Raw sequence at 0x42024:

- 0x42024: load first digit
- 0x42028: multiplier 1000
- 0x42030: second digit
- 0x42032: multiplier 100
- 0x42038: third digit
- 0x4203C: fourth digit
- 0x42040: digit3*10
- 0x42044: final addition
- 0x42046: UXTH
- 0x42048: return

[FW][CLOSED]

This is important because the firmware does NOT compare the four PIN digits independently at the access resolver. It first creates one integer.

---

# PASS 02 — PIN ENTRY CALLBACK

At 0x42328:

- compares callback target/context;
- calls 0x42024;
- receives the assembled four-digit integer in r0;
- moves it to r1;
- calls `FUN_0803C21C`.

The only direct BL to `FUN_0803C21C` found is this path.

[FW][CLOSED]

Thus the four-digit decoder is the real access/PIN input path, not an unrelated utility.

---

# PASS 03 — ACCESS LEVEL MAPPER

`FUN_08037E74`:

```
if code == 0:
    level = 0
elif code == 900:
    level = 1
elif code == 999:
    level = 2
elif code == 6154:
    level = 3
else:
    leave existing level unchanged

store level at context/model +0x158
```

Raw proof:

0x37E74:
- CBZ r1 -> zero path
- 0x37E76: `mov.w r2,#0x384` = 900
- 0x37E7A: subtract 900
- 0x37E7C: BEQ -> level 1
- 0x37E7E: subtract 0x63 = 99
- combined with previous subtraction => original 999
- 0x37E80: BEQ -> level 2
- 0x37E82: `movw r2,#0x180A` = 6154
- 0x37E86: subtract
- 0x37E88: BEQ -> level 3
- otherwise return
- 0x37E96: store level byte at +0x158

[FW][CLOSED]

---

# PASS 04 — 0900 / 0999 / 6154 DECIMAL CONFIRMATION

Hex/decimal:

```
0x0384 = 900
0x03E7 = 999
0x180A = 6154
```

There are no ASCII strings `0900`, `0999`, or `6666` in the firmware, because the UI stores digits numerically and the access logic compares the assembled integer.

[DATA][FW][CLOSED]

---

# PASS 05 — INVALID CODE BEHAVIOR

The unmatched path in `FUN_08037E74` reaches BX LR without writing +0x158.

Therefore:

- invalid nonzero PIN does NOT inherently force access level to zero;
- current access level is preserved unless a recognized code changes it;
- entering 0900 can raise level from 0 to 1;
- entering 0999 can raise level to 2;
- entering 6154 can raise level to 3;
- entering 0 explicitly writes level 0.

This matches the user's cumulative-access observation and is an important implementation requirement.

[FW][CLOSED]

---

# PASS 06 — GLOBAL "HAS ACCESS" FLAG

`FUN_0803C21C` after `FUN_08037E74`:

- calls model getter;
- reads model +0x158;
- computes boolean(level >= 1);
- stores the boolean at global context address +0x10.

The literal pool at 0x3C248 resolves to RAM 0x2002466C.

Thus there are at least two distinct concepts:

1. access level byte = 0..3 at model/context +0x158;
2. has-any-access boolean at RAM 0x2002466C + 0x10.

[FW][STRONG]

This explains why the UI can have multiple access tiers while also having a simple "restricted vs unlocked" gate.

---

# PASS 07 — SPECIAL-CODE HANDLER

`FUN_08018634(context, code)` is separate from the 0..3 access mapping.

It contains direct constants:

- 0x7C8 = 1992
- 0x1A0A = 6666

and also handles code 0.

Raw sequence:

```
if code == 1992:
    special context+0x24 adjustment

then:
    inspect context+0x1A / +0x1C state
    check code through FUN_080144B4
    if matched:
        set context+0x07 = 1
        store code in context+0x1A
    elif code == 6666:
        set context+0x07 = 1
    elif code == 0:
        set context+0x07 = 0
        restore context+0x1A from +0x1C
```

[FW][CLOSED as control flow]

The exact semantic names of +0x07/+0x1A/+0x1C/+0x24 remain OPEN.

---

# PASS 08 — 6666 IS A REAL SPECIAL CODE

`0x1A0A = 6666` is loaded with:

0x18668: `movw r0,#0x1A0A`

then compared directly against the entered code.

Only one such direct 6666 literal was found in executable code.

When it matches:

0x18670:
`movs r0,#1`

0x18672:
`strb r0,[r4,#0x7]`

and the function returns.

[FW][CLOSED]

This confirms 6666 is not a random data occurrence.

---

# PASS 09 — 6666 / FACTORY-RESET INTERPRETATION

The user's observation says:

> 6666 restores factory settings without changing boiler type.

The raw firmware proves 6666 activates the special state flag at context +0x07.

However, the exact downstream operation that converts this flag into "restore defaults" has not yet been closed.

`FUN_08018684`, called from a periodic/state-management path at 0x18268, reads +0x07.

When +0x07 == 1 it increments +0xE6; after 0x3D ticks it clears +0x07 and restores a stored value from +0x1C into +0x1A.

Therefore the special-code state is definitely consumed asynchronously.

[USER] 6666 = factory reset without boiler type change.
[FW] 6666 = special-state flag activation.
[OPEN] exact reset/write sequence downstream of that flag.

Do not yet claim that 0x18684 itself performs the factory reset.

---

# PASS 10 — 1992

1992 = 0x7C8 is directly tested in `FUN_08018634`.

When matched:

```
context+0xE0
    -> [ +0x0C ]
    -> plus literal from 0x18760
    -> context+0x24
```

This is a real special code, but its semantic purpose is not yet proven.

[FW][CLOSED code path]
[OPEN] meaning.

Do not call 1992 "service PIN", "factory PIN", or "boiler PIN" without a downstream semantic proof.

---

# PASS 11 — SEARCH FOR ADDITIONAL FIXED ACCESS PINS

Searches performed:

- direct ASCII 0900/0999/6666;
- BCD forms;
- uint16/uint32 forms;
- immediate comparisons;
- MOVW constants;
- all callers of the PIN decoder;
- all callers of FUN_0803C21C;
- all callers of FUN_08037E74;
- all callers of FUN_08018634.

Result:

The explicit access-level mapping contains exactly three fixed access codes:
- 0900 -> level 1
- 0999 -> level 2
- 6154 -> level 3

No fourth fixed access-level PIN was found in this path.

The special-code handler separately contains 1992 and 6666.

[FW][STRONG/CLOSED for current PIN-entry path]

---

# PASS 12 — "BOILER-DEPENDENT PINS"

This is the important unresolved branch.

Because the firmware's complete PIN input path is:

```
digits
  -> FUN_08042024
  -> FUN_08042328
  -> FUN_0803C21C
       ├─ FUN_08018634
       └─ FUN_08037E74
```

any additional accepted PIN must ultimately be handled by one of those two functions.

`FUN_08037E74` is fixed and contains only:
900, 999, 6154.

`FUN_08018634` contains:
1992, 6666, 0,
plus a lookup through `FUN_080144B4`.

The lookup searches a runtime registry of records. The registry pointer is at RAM 0x20008C50.

This means the only remaining plausible location for additional non-fixed/special codes in this exact PIN path is the `FUN_080144B4` lookup/state machinery.

However, the currently proven registry record keys from the initialization path are not obviously four-digit PINs. Therefore:

**[OPEN] boiler-dependent PIN mechanism is not yet closed.**

Next attack must determine whether the registry keys can be modified/generated from boiler type/profile/device identity, or whether "boiler-dependent PINs" belong to a different service mechanism.

---

# PASS 13 — IMPORTANT ARCHITECTURAL CONSEQUENCE

The access system must NOT be implemented as:

```
if pin == 0900 -> level 1
if pin == 0999 -> level 2
```

only.

Correct model:

```
special-code handler
        +
access-level resolver
        +
persistent/current access level
        +
has-access boolean
```

with current closed values:

```
900  -> 1
999  -> 2
6154 -> 3
0    -> 0
```

and special:

```
1992 -> special state
6666 -> special state
```

The special state is distinct from access level.

---

# PASS 14 — CONTRADICTION CHECK AGAINST USER OBSERVATION

User observation:
- level 0 sees base interface;
- 0900 gives base + level 1;
- 0999 gives previous + level 2.

Firmware:
- access level byte stores 0..3;
- 900 writes 1;
- 999 writes 2;
- no-match preserves current level.

This is internally consistent with the observed cumulative behavior.

No firmware evidence contradicts it.

---

# PASS 15 — STALE-HYPOTHESIS CHECK

Withdraw/avoid:

- "0900 and 0999 are merely UI passwords."
- "access is a binary flag."
- "there are only two access levels."
- "6666 is just a fourth access level."
- "1992 is definitely service mode."
- "6154 is definitely factory reset."

Replace with:

- access level is a numeric state 0..3;
- 900/999/6154 are explicit level selectors;
- 6666 and 1992 belong to a separate special-code path;
- exact special-code semantics remain partly OPEN.

---

# IMPLEMENTATION CONTRACT — CURRENT

Machine-readable target:

```
access_level: uint8  // 0..3

PIN:
  0    -> access_level = 0
  900  -> access_level = 1
  999  -> access_level = 2
  6154 -> access_level = 3
  other nonzero -> preserve current access_level

special_code:
  1992 -> special state
  6666 -> special state
```

Do not collapse special_code into access_level.

---

# NEXT MULTIPASS TARGETS

A. Fully trace FUN_08018634 downstream state.
B. Trace all reads/writes of context +0x07.
C. Trace all reads/writes of +0x1A/+0x1C/+0xE6.
D. Identify the object/class behind context 0x20021FA0.
E. Resolve FUN_080144B4 registry semantics.
F. Determine whether registry keys can become boiler-dependent PINs.
G. Trace "Default settings request" parameter from string registration to write path.
H. Connect 6666 special state to that parameter/reset operation.
I. Identify whether boiler type is preserved by the reset path.
J. Search all other PIN-related UI resources and callbacks.
K. Build synthetic access matrix 0/1/2/3 + special codes.
L. Persist every closed/open distinction in MASTER and START-HERE.

