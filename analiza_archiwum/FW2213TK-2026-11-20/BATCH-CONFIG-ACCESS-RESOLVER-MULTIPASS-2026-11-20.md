# TeklaPelletCAN — MULTIPASS CONFIGURATION + ACCESS RESOLVER
Data: 2026-11-20
Source: raw /mnt/data/FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Cel przebiegu

Wykonano wielotorowy trace surowego BIN na kilku poziomach:
1. tabela internal-index -> CAN,
2. katalog parametrów/stringów,
3. selector/gate UI,
4. konstruktor ekranu,
5. mapper parametrów,
6. access/PIN,
7. storage/model,
8. odczyty + zapisy,
9. warianty CO1..CO4,
10. syntetyczna macierz konfiguracji.

Źródło prawdy: firmware. Istniejący TeklaPelletCAN nie był używany jako specyfikacja zachowania.

---

# PASS 01 — pełna mapa konfiguracji internal -> CAN

Raw mapping table @ raw offset 0x37950+ daje:

- internal 0x112 -> CAN 0x3500
- internal 0x113 -> CAN 0x3502
- internal 0x10D -> CAN 0x3505
- internal 0x10E -> CAN 0x2105
- internal 0x10F -> CAN 0x2106
- internal 0x111 -> CAN 0x2107
- internal 0x110 -> CAN 0x2108
- internal 0x114 -> CAN 0x3501
- internal 0x115 -> CAN 0x2123
- internal 0x116 -> CAN 0x3606
- internal 0x117 -> CAN 0x3506
- internal 0x118 -> CAN 0x3508
- internal 0x119 -> CAN 0x3509
- internal 0x11A -> CAN 0x350A
- internal 0x11B -> CAN 0x350B
- internal 0x11C -> CAN 0x350C
- internal 0x11D -> CAN 0x350D
- internal 0x11E -> CAN 0x3707
- internal 0x11F -> CAN 0x3629
- internal 0x120 -> CAN 0x362B
- internal 0x121 -> CAN 0x370A
- internal 0x122 -> CAN 0x3525

Fuel block:
- 0x147 -> 0x3601
- 0x148 -> 0x3600
- 0x149 -> 0x3603
- 0x14A -> 0x3602
- 0x14B -> 0x3604
- 0x14C -> 0x3607

[FW][CLOSED]

---

# PASS 02 — string/catalog correlation

Firmware string catalog and project register snapshot close these semantic names:

- 0x3500 = Main module type
- 0x3501 = Autoconfig activation
- 0x3502 = CH expansion module type
- 0x3505 = Outside temperature sensor configuration
- 0x3506 = Sound alarm activation
- 0x3508 = Silence hours from
- 0x3509 = Silence hours to
- 0x350A = Return to boiler temperature sensor
- 0x350B = Profile number
- 0x350C = Is this device cascade master
- 0x350D = Pressure sensor
- 0x3525 = Additional fuel storage
- 0x3629 = Energy meter type
- 0x3707 = EGT sensor type
- 0x370A = Boiler image selector

The four functional configuration parameters are independently named in the firmware string catalog:
- 0x2105 = Heating configuration
- 0x2106 = Hot water configuration
- 0x2107 = Buffer configuration
- 0x2108 = Solar configuration

Fuel reserve input:
- 0x3606 = Input IN17 config
- 0x3607 = Reserve sensor state

Return sensor:
- 0x350A = Return to boiler temperature sensor

[FW][DATA][STRONG]

---

# PASS 03 — exact configuration dependency resolver

FUN_0803C178 is a UI eligibility/visibility resolver.

Only direct caller found:
- runtime 0x0804227A / raw 0x4227A.

Caller loop:
- selector/index in r1 = 0..20
- 21 row slots are processed.

The resolver reads active model through the normal accessor and applies:

selector 1:
- internal 0x10E / CAN 0x2105
- visible iff value >= 1

selector 2:
- 0x2105
- visible iff value >= 2

selector 3:
- 0x2105
- visible iff value >= 3

selector 4:
- 0x2105
- visible iff value >= 4

selector 5:
- internal 0x10F / CAN 0x2106
- visible iff value >= 1

selector 6:
- internal 0x110 / CAN 0x2108
- visible iff value >= 1

selector 7:
- internal 0x111 / CAN 0x2107
- visible iff value >= 1

selector 8:
- internal 0x11C / CAN 0x350C
- visible iff value is nonzero

selector 9:
- internal 0x122 / CAN 0x3525
- visible iff value is nonzero

all other selectors 0 and 10..20:
- resolver returns visible=true unless another outer layer suppresses them.

This is a major closure: configuration does not merely label menu entries; it directly gates row creation/visibility.

[FW][CLOSED]

---

# PASS 04 — synthetic configuration matrix

Using the exact resolver above:

| Configuration | CO rows 1..4 | CWU row 5 | Solar row 6 | Buffer row 7 | Cascade-master row 8 | Additional-storage row 9 |
|---|---|---|---|---|---|---|
| Heating=0 | none | no | no | no | no | no |
| Heating=1 | CO1 | no | no | no | no | no |
| Heating=2 | CO1..CO2 | no | no | no | no | no |
| Heating=3 | CO1..CO3 | no | no | no | no | no |
| Heating=4 | CO1..CO4 | no | no | no | no | no |
| Heating=4 + HW=1 | CO1..4 | yes | no | no | no | no |
| + Solar=1 | CO1..4 | yes | yes | no | no | no |
| + Buffer=1 | CO1..4 | yes | yes | yes | no | no |
| + CascadeMaster=1 | CO1..4 | yes | yes | yes | yes | no |
| + AdditionalStorage=1 | CO1..4 | yes | yes | yes | yes | yes |

Important: this table is a resolver-level synthetic test, not a claim that all later screens are identical. Outer screen/menu dispatch can impose additional conditions.

This immediately defines the first machine-readable capability resolver for the new implementation.

---

# PASS 05 — access/PIN chain: major correction

A previous master note interpreted +0x158 as a UI variant and recorded the third code incorrectly. Raw BIN now closes this.

FUN_08042024:
- reads four decimal digits from an object,
- computes digit0*1000 + digit1*100 + digit2*10 + digit3,
- returns uint16.

Raw code:
- 0x42024 reads four bytes,
- first multiplier uses 0x3E8 = 1000,
- next uses 100,
- then 10,
- then final digit.

FUN_08042328 is a callback boundary:
- validates the relevant child/object pointer,
- calls FUN_08042024,
- passes resulting numeric code to FUN_0803C21C.

FUN_0803C21C calls FUN_08037E74(model, entered_code).

FUN_08037E74:
- code 0 -> access level 0
- 900 decimal (0x0384) -> level 1
- 999 decimal (0x03E7) -> level 2
- 0x180A decimal = 6154 -> level 3
- other nonzero values leave the previous level unchanged.

It writes the resulting level to model +0x158.

Therefore:

+0x158 = access level, not CO number and not generic UI variant.

The third access code is:
6154, not the previously recorded 0x1BF1.

Initialization:
FUN_08037CA4 explicitly writes level 0 to +0x158.

[FW][CLOSED]

---

# PASS 06 — access-level consumption

Many independent screens read model +0x158.

Observed thresholds:

1. ldrb [model,#0x158] followed by cbz:
   - level 0 suppresses the object,
   - level >=1 allows it.

2. ldrb [model,#0x158] followed by cmp #2 + blt:
   - level >=2 required.

3. ldrb [model,#0x158] followed by cmp #3 + blt:
   - level >=3 required.

This occurs in multiple constructor families across raw offsets:
- 0x3E772 / 0x3E79C / 0x3E7C6 / 0x3E7F2
- 0x3E83C
- 0x3E8B8 / 0x3E940 / 0x3E9C8
- 0x3EA2A
- 0x4A566 / 0x4AA42
- 0x4C15A
- 0x4EA32
- 0x4F456 / 0x4F79A
- 0x4FEF2 / 0x501F2
- 0x504AE / 0x5076A
- 0x50A7E / 0x50D3A
- 0x50FF6 / 0x512B2
- 0x5156E
- 0x5FB0A
- plus many level-parameter consumers.

Strong interpretation:
- level 0 = normal/user
- level 1 = PIN 0900
- level 2 = PIN 0999
- level 3 = service/installer-level functionality.

The exact human label "service" is not assigned to level 3 solely from these bytes; the access hierarchy is closed, the UI label remains [OPEN] until string/call-chain proof.

[FW][STRONG]

---

# PASS 07 — access gate integrated with configuration gate

The firmware therefore has at least two orthogonal UI filters:

A) installation/capability resolver:
FUN_0803C178(selector, model)
- depends on heating/HW/buffer/solar/cascade/additional-storage config.

B) access resolver:
model+0x158
- depends on PIN.

A menu row can therefore be suppressed because:
1. installation does not support it,
2. user lacks access level,
3. both,
4. or an outer screen dispatcher imposes another condition.

This is exactly why the final ESP implementation must not hard-code menu membership.

---

# PASS 08 — 0x350C / 0x3525 are not decorative labels

The configuration gate directly reads:
- 0x350C = Is this device cascade master
- 0x3525 = Additional fuel storage

Thus these parameters are proven to control actual UI availability.

Similarly:
- 0x2105 controls selectors 1..4,
- 0x2106 controls selector 5,
- 0x2108 controls selector 6,
- 0x2107 controls selector 7.

The order in the raw resolver is not the same as the string catalog order; do not sort by text order.

---

# PASS 09 — heating/CO instance architecture cross-check

Independent raw evidence still closes:

+0x12B = class/type
+0x12C = active instance 1..4

FUN_08036FF2(context,panel_index):
- reads active object,
- uses +0x12C,
- resolves family-of-4.

Independent runtime lookup:
FUN_080470C0:
- base index + instance - 1,
- then record lookup.

Examples:
- 0x2032 + instance - 1 -> 2032..2035
- 0x2048 + instance - 1 -> 2048..204B
- 0x2064 + instance - 1 -> 2064..2067
- 0x4001 + instance - 1 -> 4001..4004

This means the synthetic capability resolver should output not only CO_count, but an explicit instance list:
CO[1], CO[2], CO[3], CO[4].

[FW][CLOSED]

---

# PASS 10 — access code generation is UI-side, not CAN-side

The PIN path is local to the panel object:
- four digit bytes,
- local arithmetic,
- callback,
- access-level setter.

No CAN ID is involved in the code-generation path itself.

Therefore the new ESP implementation must reproduce:
- 4-digit input semantics,
- exact code mapping,
- access level state,
- access-dependent widget creation,
while CAN remains the transport for the actual boiler parameters.

This is a separate domain from parameter mapper/record engine.

---

# PASS 11 — correction of old master

Withdraw:
+0x158 = generic UI variant
Withdraw:
0x1BF1 -> level 3

Replace with:
+0x158 = access level
0 -> 0
0900 -> 1
0999 -> 2
6154 -> 3

The previous master text must be treated as stale on this point.

---

# PASS 12 — first implementation-level model

The firmware-derived resolver can now be represented conceptually as:

installation:
- heating_config: 0..4
- hot_water_config: 0/1+
- solar_config: 0/1+
- buffer_config: 0/1+
- cascade_master: 0/1
- additional_storage: 0/1

access:
- level: 0..3

capabilities:
- CO1..CON where N=heating_config, subject to any later screen-specific gate
- CWU if hot_water_config >= 1
- Solar if solar_config >= 1
- Buffer if buffer_config >= 1
- Cascade-master branch if 350C != 0
- Additional-storage branch if 3525 != 0

access:
- level>=1 gates some advanced widgets
- level>=2 gates deeper settings
- level>=3 gates service-level widget families.

This is NOT yet the final menu. It is the first firmware-proven capability layer.

---

# OPEN ITEMS

1. Exact outer screen/menu dispatcher.
2. Exact 21-row screen class and row labels.
3. Which selectors 0 and 10..20 correspond to which named rows.
4. Exact access-level timeout/reset behavior.
5. Exact human label for level 3.
6. Whether all CO rows are controlled exclusively by 2105 or also by hardware/profile gates.
7. Exact CWU/buffer/solar/cascade screen trees.
8. Exact touch callback/write path for each row.
9. Exact profile/module interactions with capability resolver.
10. Final synthetic screen snapshots for every matrix state.

---

# Next multipass targets

Priority 1:
FUN_0804227A -> identify all 21 rows -> exact widget/bitmap/text/callback tree.

Priority 2:
FUN_0803C178 callers/consumers -> determine which screen/menu this is.

Priority 3:
+0x158 consumers -> map level 0/1/2/3 to actual menu families.

Priority 4:
configuration strings -> exact screen entries:
- heating
- hot water
- buffer
- solar
- cascade
- additional storage
- sensors
- hardware/profile.

Priority 5:
synthetic configuration engine + test matrix.

No renderer work until these semantic branches are closed.


# PASS 13 — raw 21-entry menu row table

The constructor around FUN_0804227A uses a 21-entry table at raw 0x42348. Each entry is 6 bytes:

[selector, bitmap_A, bitmap_B]

Raw entries:

0  -> 60,83
10 -> 61,85
1  -> 62,86
2  -> 63,86
3  -> 64,86
4  -> 65,86
5  -> 66,88
6  -> 71,87
7  -> 67,84
8  -> 70,82
9  -> 69,99
11 -> 72,78
13 -> 74,89
17 -> 77,159
15 -> 76,96
0  -> 12,73
90 -> 14,75
97 -> 18,78
100 -> 16,79
98 -> 19,80
95 -> 20,81

The first field is consumed as the row/menu selector; the other two fields are passed to the row/icon builder FUN_0804BC6C, which installs bitmap resources through the normal Bitmap resource setter.

The selector order is therefore NOT numerical. The firmware's actual menu order is encoded by this table.

[FW][DATA][CLOSED]

---

# PASS 14 — selector -> menu semantic correlation

Using:
A) the raw selector/gate function,
B) the icon resources,
C) the firmware menu strings,
D) official IGNEO Touch documentation only as external corroboration,

the following are strongly closed:

- selector 0 -> Kocioł / Boiler
- selector 10 -> Palnik / Burner
- selector 1 -> Ogrzewanie obwód 1
- selector 2 -> Ogrzewanie obwód 2
- selector 3 -> Ogrzewanie obwód 3
- selector 4 -> Ogrzewanie obwód 4
- selector 5 -> Ciepła woda użytkowa / Hot Water
- selector 6 -> Solary / Solar
- selector 7 -> Bufor / Buffer
- selector 8 -> cascade branch (installation-gated by 0x350C)
- selector 9 -> Additional fuel storage (installation-gated by 0x3525)
- selector 11 -> Historia alarmów
- selector 13 -> Informacje o programie
- selector 15 -> Poziom menu (PIN)
- selector 90 -> Język / Language
- selector 97 -> Alarm dźwiękowy / Sound alarm
- selector 17 -> Konfiguracja
- selector 100 -> Test wyjść
- selector 98 -> Statystyki
- selector 95 -> Sieć / Net

For selectors 8 and 9 the firmware gate is stronger than documentation: selector 8 is tied directly to 0x350C and selector 9 directly to 0x3525.

For selectors 0,10,11,13,15,90,97,17,100,98,95 the exact semantic labels are corroborated by the firmware string catalog and the documented menu structure, while the raw selector/bitmap table provides the actual implementation order.

[FW][DATA][STRONG][DOC]

---

# PASS 15 — configuration gate + main menu order

The main menu can now be represented as a firmware-derived ordered list:

1. selector 0 — Kocioł
2. selector 10 — Palnik
3. selector 1 — CO1
4. selector 2 — CO2
5. selector 3 — CO3
6. selector 4 — CO4
7. selector 5 — CWU
8. selector 6 — Solar
9. selector 7 — Buffer
10. selector 8 — Cascade branch
11. selector 9 — Additional fuel storage
12. selector 11 — Alarm history
13. selector 13 — Program info
14. selector 15 — Menu level/PIN
15. selector 90 — Language
16. selector 97 — Sound alarm
17. selector 17 — Configuration
18. selector 100 — Output test
19. selector 98 — Statistics
20. selector 95 — Network

The raw table contains 21 records because selector 0 occurs twice with different bitmap pairs. This indicates that the table is not a simple unique-ID catalog; one occurrence is a distinct row/resource state or alternate context.

Do not collapse the two selector-0 records until their parent/row construction context is proven.

---

# PASS 16 — visual asset cross-check of the menu table

Extracted firmware assets independently show:

- 62–65 are distinct small UI symbols used by selectors 1..4.
- 86 is shared by selectors 1..4 and visually matches a heating/radiator family.
- 88 is a faucet symbol, matching selector 5 / CWU.
- 87 is a solar-panel-like symbol, matching selector 6 / Solar.
- 84 is a tall tank symbol, matching selector 7 / Buffer.
- 82 is a multi-module/cascade-like symbol, matching selector 8.
- 99 is a storage/silo-like symbol, matching selector 9 / Additional fuel storage.
- 96 is a user+lock symbol, matching selector 15 / Menu level.
- 159 is a gears symbol, matching selector 17 / Configuration.

This is an independent asset-level corroboration of the configuration gates and menu selector semantics.

The exact pixel appearance remains governed by the raw RGB565/A8 assets; no generated graphics are used as specification.

[DATA][STRONG]

---

# PASS 17 — external documentation sanity check, not source of truth

Official/producer documentation for IGNEO Touch describes the menu families:
Kocioł, Palnik, Heating circuits 1..4, Hot Water, Solar, Buffer, Alarm history, Program info, Menu level/PIN, Language, Sound alarm, Configuration, Output test, Statistics and Network. Some versions additionally show Additional fuel storage.

This matches the raw selector table's semantic order.

Important:
- documentation versions differ,
- some older manuals show different PINs,
- therefore documentation is NOT used to override the raw FW access-code mapping.
For FW2213TK the raw BIN remains authoritative.

[DOC][STRONG]

---

# PASS 18 — capability matrix now has exact main-menu order

The synthetic resolver should emit an ordered menu vector, not a dictionary sorted by ID.

Example for Heating=2, HW=1, Solar=0, Buffer=0, CascadeMaster=0, AdditionalStorage=0:

[0,10,1,2,5,11,13,15,90,97,17,100,98,95]

For maximum configuration with all branches enabled:

[0,10,1,2,3,4,5,6,7,8,9,11,13,15,90,97,17,100,98,95]

This is the first directly firmware-derived menu ordering usable by the final implementation.

---

# New open issue

The duplicate selector 0 needs separate trace:
- identify which of the two selector-0 rows is the normal Kocioł menu item,
- identify the second context/state,
- prove whether it is a home/quick-action row or a duplicate menu resource.

Do not remove it from the model until the parent screen/callback path is closed.


# 2026-11-20 CORRECTION — 21-ENTRY TABLE ≠ 21 ROWS CONSUMED BY THIS CONSTRUCTOR

The previous wording "21-row main menu closed" was too strong and is corrected here.

Raw table at 0x42348 contains 21 triples (selector, bitmap_A, bitmap_B):

0:(60,83)
10:(61,85)
1:(62,86)
2:(63,86)
3:(64,86)
4:(65,86)
5:(66,88)
6:(71,87)
7:(67,84)
8:(70,82)
9:(69,99)
11:(72,78)
13:(74,89)
17:(77,159)
15:(76,96)
0:(12,73)
90:(14,75)
97:(18,78)
100:(16,79)
98:(19,80)
95:(20,81)

However, the constructor at 0x42160 initializes its first-pass count to 15 (movs r5,#15) and the loop at 0x421e8 processes exactly the first 15 table records. The second loop also uses count 15. Therefore this constructor does NOT consume all 21 records.

The first 15 selectors are:
0,10,1,2,3,4,5,6,7,8,9,11,13,17,15

The remaining six:
0,90,97,100,98,95

must NOT yet be assigned to this constructor's main-menu row set. They are currently an unresolved secondary/alternate context or another resource group.

This correction supersedes any statement that the complete 21-entry table has already been proven as one 21-row screen.

## Evidence for two-pass structure

At 0x421dc:
- r5 = 15
- r9 = ADR 0x42348
- r10 = ADR 0x42346 (two bytes before table)

First loop:
- r9 advances +6 each iteration
- row builder FUN_0804BC6C gets table[selector], table[bitmap_A], table[bitmap_B]

After first loop:
- access-level byte copied to model/UI object
- second loop starts with r7=0 and count still 15
- r10 advances +6
- row builder receives selector from r10+2 and bitmap_A from r10+4
- special checks test r10[0] against 0x0C/0x0E

Thus the second pass is not a generic continuation over records 16..21.

## Evidence that the six trailing records are not yet closed

No independent code reference to table start 0x42348 was found besides the 0x42160 constructor's ADR setup. The six trailing records are therefore retained as data, but their consumer is OPEN.

Do not remove them. Do not call them normal main-menu rows until another consumer/call path proves it.
