# AUTONOMOUS PASS 15 — RE TOOLCHAIN UPGRADE — 2026-11-22

## Cel

Usunięto wąskie gardło ręcznego przeszukiwania dla trzech aktualnych OPEN:
- konkretny obiekt za +0x7178,
- konkretny obiekt za +0x7180,
- runtime scheduler → FUN_08010FCE.

## Zmiany

### 1. tools/re_scan.py
Rozszerzono wynik o `object_ops`:
- instrukcja,
- rejestr bazowy,
- offset obiektu,
- adres TRUE/RAW.

To pozwala automatycznie wyłapywać wzorce typu `[this,#offset]` i łączyć je z dalszym vtable/object-flow.

### 2. tools/vtable_scan.py
Nowe narzędzie:
- wykrywa kandydatów na tablice wskaźników do kodu Thumb,
- wyznacza liczbę kolejnych slotów,
- wyszukuje wystąpienia adresu vtable jako LE32,
- wspiera targety do korelacji.

Narzędzie nie uznaje samego wzorca za dowód vtable. Wymaga niezależnego potwierdzenia przez konstruktor/vptr lub runtime.

### 3. tools/runtime_trace_analyzer.py
Nowe narzędzie:
- czyta TraceLog JSON/JSONL,
- agreguje `INDIRECT_CALL pc → target`,
- koreluje object_address + offset,
- obsługuje focus targets,
- generuje JSON + Markdown.

### 4. tools/test_re_tools.py
Dodano testy:
- wykrywanie tablicy wskaźników,
- wykrywanie runtime indirect-call edge i object offset.

## Evidence policy

Nie zamykamy OPEN na podstawie samego statycznego skanera.

HARD dla indirect edge wymaga:
1. statycznego wskazania obiektu/vtable,
2. zgodności slotu/funkcji,
3. niezależnego potwierdzenia runtime.

## Status

Narzędzia są przygotowane do kolejnego pełnego przebiegu. Ten pass nie zmienia jeszcze procentów RE — nie dodaje dowodu o firmware, tylko zwiększa automatyzację i powtarzalność zbierania dowodów.

## Commits

- vtable scanner: `775557a1184ad6a2b329910f9121a050f7395458`
- runtime analyzer: `ba517c78098130de30649c78d03de1338b94400e`
- tests: `8ea5ebf83726e4c5b233d705d326c4f65a864b4a`
- re_scan object-flow: `bd435236942f644a9f0024e2b745fc2b72050ecf`
- scanner docs: `1b77bc896a678d12dad02fe5c4c93bed1828401b`
