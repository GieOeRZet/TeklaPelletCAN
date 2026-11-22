# NewEstyma — PAGE/WIDGET FACTORY + 188 RESOURCE REGISTRY — CLOSURE 01 — 2026-11-22

Firmware SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 1. 188-resource registry — HARD

Registry base:
DAT_0804866C

Exactly 188 resource records were recovered.

Correct TypedText base:
0x5BE64

Record width:
16 bytes.

Type distribution:
- type 0: 139
- type 1: 31
- type 2: 3
- type 3: 12
- type 4: 1
- type 5: 2

This is the firmware resource registry used by the UI/resource dispatch layer.

## 2. Resource dispatch — HARD

FUN_080480C0 is the central presenter/resource dispatcher used by FUN_0803E714.

It consumes 16-byte resource descriptors and branches by resource type.

Confirmed routes:
- type 1 -> FUN_0804E598
- type 2 -> FUN_0804E740
- type 3 -> FUN_0804E75A
- type 5 -> FUN_0804E740
- general path -> FUN_0804E5BC

The exact internal bodies of several helpers are not fully recovered, therefore helper-specific final field semantics remain OPEN.

## 3. Type-5 graph family — HARD

FUN_0803EC18 recognizes:
- type 5 -> FUN_08048520
- type 0 -> FUN_08048468
- type 3 -> FUN_080484B0
- type 4 -> FUN_080484F0

For type 5:
- key 0x47 resolves IDs 0x4A..0x4E
- key 0x48 resolves IDs 0x4F..0x53
- both feed FUN_08048520.

The interpretation of 0x47/0x48 solely from numeric values is rejected.

## 4. Page/Widget value factory — HARD

FUN_0803E714 builds parameter-ID lists for page families.

For each selected parameter ID:
FUN_08036FF2(context, parameter_id)
 -> FUN_0804842C(...)
 -> widget record
 -> FUN_0804E5BC(value)
 -> FUN_08032316(widget)

The widget record addressing is:

widget_base + 0x42C + index * 0x338

FUN_080480C0 independently uses the same widget geometry:
+0x42C + N*0x338.

This proves the factory is instance/record based, not one widget object per parameter ID.

## 5. CO1..CO4 — HARD/STRONG

The repeated page/list architecture is instance-aware.

Established:
- active instance selector +0x12C has values 1..4 in traced paths;
- +0x12B is a separate variant/context selector;
- CO1..CO4 use common list/factory machinery;
- TypedText 119..122 correspond to Ogrzewanie obwód 1..4.

Do NOT model CO1..CO4 as four unrelated hard-coded screen classes.

## 6. Important rejected mappings

Do not use without new evidence:
- bitmap ID = widget ID;
- 0x47/0x48 interpreted only from numbering;
- 0x0037 / TypedText 55 = TypedText 119..122;
- 174 = Home-only.

A specific type-5 record at 0x0807F5EC has value 0x0037 / TypedText 55, but this is not proof for CO1..CO4.

## 7. What is actually closed

CLOSED:
- registry size and base;
- descriptor width;
- type distribution;
- primary resource dispatcher;
- primary type routing;
- page parameter-list -> widget-record factory path;
- widget record base/stride;
- instance-aware common machinery.

OPEN:
- complete field-by-field semantics of all 16-byte resource records;
- exact bodies/field writes of FUN_0804E598, FUN_0804E740, FUN_0804E75A, FUN_0804E5BC;
- final widget-specific Bitmap/TypedText/callback mapping for every resource;
- complete screen parent/child navigation.

## 8. Implementation consequence

The ESP32/HA architecture should model:

ResourceRegistry[188]
 -> ResourceDescriptor(type,...)
 -> ResourceFactory(type)
 -> PageInstance
 -> WidgetRecord[index]
 -> parameter/value binding
 -> render/refresh callback.

For repeated pages:
PageInstance(instance_id, context_id)
 -> common widget records
 -> per-instance parameter IDs.

Do not duplicate the complete widget class tree for CO1..CO4.
