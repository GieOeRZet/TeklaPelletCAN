# PASS 135 — C1 akcje przycisków — 2026-11-23

## Status
C1 wykonane jako statyczny audyt wymagany przez PROMPT_CHATGPT_UI. Emulator test środowiska niezaliczony, więc nie wykonuję T1 ani nie udaję dynamicznego handler trace.

## FACT
1. Rejestr wierszy używa `this+0x3B4+i*0x274`, licznik `this+0x3B8`.
2. `FUN_0807EB00` wybiera rekord i dispatchuje do `FUN_0803C064`; `FUN_0807EB36` wybiera ten sam rekord i dispatchuje do `FUN_0803EC18`.
3. `FUN_0803C064` ma pełny dispatch klas 0..20. Klasy 1..4 są wariantami wspólnej ścieżki; 5..11, 13, 15..20 mają osobne ścieżki; 12 i 15 są specjalne; 14 jest pustym branch.
4. Dla klas 1..4 kod ustawia `+0x12B=1..4` i `+0x12C=1..4`, a następnie wybiera descriptor z puli `0x8038708/0x8038710/0x8038718`.
5. Klasa 11 wybiera descriptor `0x8038798/0x80387A0` zależnie od `+0x12A`; klasy 13,19,20 analogicznie wybierają descriptor zależnie od `+0x12A`.
6. Klasa 12 wykonuje ścieżkę parametrową przez `FUN_080373BA` / `FUN_080373E6` i następnie `FUN_08037F5C`; jej znaczenie biznesowe pozostaje OPEN.
7. Klasa 15 omija wspólny konstruktor i wywołuje `FUN_0802EADE(param+0x0C+0x37B0,param+0x0C+0x422C)`; dokładny efekt UI OPEN.
8. Klasa 14 ma bezpośredni return.
9. `FUN_0803EC18` dla wybranych typów wykonuje operacje na obiekcie widoku przez `FUN_08048468/080484B0/080484F0/08048520`; te helpery zapisują/ustawiają stan obiektu i przekazują dalej do `FUN_0802EADE` lub `FUN_0803EECC`. Nie przypisuję im na siłę znaczenia PID/CAN.

## PORÓWNANIE Z POMIAREM CLAUDE
Claude's `actions_pass61_L0_partial.json` potwierdza, że rzeczywiste tapy potrafią wywołać nawigację do klas/vtable, np. Kocioł→Kaskada/PROGRAM/NASTAWY oraz lista→Kocioł. Statyczny C1 zamyka mechanizm dispatchu, ale nie pozwala uczciwie przypisać każdego fizycznego offsetu widgetu do konkretnego handlera dla wszystkich 12 klas. Te pozycje pozostają OPEN zamiast być zgadywane.

## REJECTED
Nie użyto `presenter_trace.py` ani samego `view_off` jako dowodu. Nie utożsamiono identyfikatora bitmapy z handlerem.

## ARTEFAKTY
- `data/cg_actions_<klasa>.csv` — per-class inventory.
- `data/cg_actions_all_classes.csv` — agregat.
