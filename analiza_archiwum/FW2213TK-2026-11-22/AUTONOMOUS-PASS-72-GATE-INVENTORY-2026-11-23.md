# PASS 72 — inventory bramek poziomu i domknięcie kontekstu wrapperów

## Wynik

Statyczny przegląd istniejących artefaktów RE porządkuje pozostałe bramki bez udawania dowodu dynamicznego.

### 1. Czwarta bramka 0x08054AB8

Kodowa sygnatura jest jednoznaczna:
- wrapper: 0x08054AB8;
- warunek: ldrb.w r0,[model,#0x158]; cbz r0,...;
- wejście do gałęzi = poziom != 0;
- caller: 0x08054CA6;
- gałąź używa tego samego mechanizmu budowania UI (FUN_08040380) i dalej stałych 0x84 oraz 0x1498.

Nie ma jednak w repo dowodu dynamicznego, który pozwala uczciwie przypisać ten wrapper do konkretnego ekranu. 0x1498 pojawia się w mapie presenterów jako offset związany m.in. z Hot water 1 result temperature, ale nie jest to dowód, że cały wrapper jest ekranem CWU. Kontekst pozostaje OPEN.

### 2. Pozostałe bramki >=3

Repo ma już zamkniętą strukturę wspólnego kodu nagłówka:
- 0x0805A9EC — OPEN, ctx12A=2;
- 0x0805B1D4 — OPEN, ctx12A=4;
- 0x0805F400 — OPEN, ctx12A=5;
- 0x0805FE9C — OPEN, kontekst nieosiągnięty.

Wszystkie należą do tej samej rodziny wrapperów generujących element nagłówka +0x23C, czyli CPU load dla poziomu >=3. Nie ma podstaw, by traktować je jako niezależną funkcjonalność.

Dwa dawniej wymienione jako nietrafione są już zamknięte przez późniejszy PASS 52:
- 0x0806125C = Magazyn paliwa, ctx12A=2, ctx12B=9;
- 0x08061518 = Kaskada, ctx12A=2, ctx12B=8.

## Ważne rozróżnienie

0x08054AB8 jest bramką L>=1, natomiast 0x0805A9EC, 0x0805B1D4, 0x0805F400, 0x0805FE9C są bramkami L>=3. Nie należy mieszać ich w jednym mechanizmie dostępu.

## Status

| Obszar | Status |
|---|---|
| Warunek 0x08054AB8 | FACT — level != 0 |
| Kontekst 0x08054AB8 | OPEN |
| Wspólny efekt wrapperów >=3 | FACT — nagłówek CPU load |
| 0x0806125C | FACT — Magazyn paliwa |
| 0x08061518 | FACT — Kaskada |
| 0x0805A9EC | OPEN — ctx12A=2 |
| 0x0805B1D4 | OPEN — ctx12A=4 |
| 0x0805F400 | OPEN — ctx12A=5 |
| 0x0805FE9C | OPEN — kontekst nieosiągnięty |

## Narzędzia

Dodano tools/cg_gate_inventory.py oraz tools/test_cg_gate_inventory.py. Narzędzie nie próbuje zgadywać ekranów; jedynie konsoliduje dowody z access_gates_scan.csv.

## Następny kierunek

Najbardziej wartościowe statycznie jest teraz przejście po RTC setterze i jego callerach oraz po PID 0x372F / auto-sync, ponieważ to jedyny duży temat A3, którego nie da się domknąć samym katalogiem PID. Równolegle pozostaje dokładne znaczenie record+0x0C dla katalogu 23.
