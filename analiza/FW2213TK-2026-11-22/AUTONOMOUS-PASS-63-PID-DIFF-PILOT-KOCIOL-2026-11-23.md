# PASS 63 — pilot PID-diff, ekran Kocioł (poziom 0) — 2026-11-23 (Claude)

Narzędzia: `tools/pid_diff.py` (fazy cands/diff), `tools/pid_diff_report.py` (analiza). Dane i dowody: `data/pass63_pilot_kociol/` (JSON wyników, cands.json, arkusze przed/po `sheet_*.png`).
Metoda: punkt kontrolny ekranu Kocioł (węzeł 0_screen) → kandydaci PID z `enable_trace()["pids"]` (14) → dla każdego 2–5 wartości `inject_param` → 200 tików → odczyt vis/touch/rect/bitmapa/tekst 54 widżetów. Bez haków w callbackach; jedyny hak (odczyt PID) tylko w fazie cands.

## Kandydaci PID ekranu Kocioł (FACT, 14)
0x2001 0x2002 0x2004 0x2005 0x216A 0x216F 0x2277 0x3333 0x350A 0x350D 0x3628 0x3629 0x370A 0x4000

## Kryteria
- K1 determinizm: **PASS** — dwa niezależne przebiegi dają identyczne stany wszystkich widżetów (0 różnic).
- K2 czas: **PASS** — cands 12 s, diff ~60 s (limit 10 min).
- K4 brak wiązań hurtowych: **PASS** — maks. 2 widżety na PID.
- K5 dowody: **PASS** — zrzuty dla każdej pary (PID, wartość), arkusze przed/po dla wiązań.
- K3 zgodność z oczekiwaniami: **CZĘŚCIOWO**.

## Wiązania (FACT, widżet → PID → reguła)
| PID | widżet (this, pozycja) | reguła |
|---|---|---|
| 0x370A Boiler image selector | 0x20016894 obraz (40,70) | wartość 1/2/3 → bitmapa 11/12/13 (zrzuty: trzy różne kotły) |
| 0x350D Pressure sensor | 0x20016a94 tekst „Ciśnienie=” (80,180) | 0 → vis=0; 1 → vis=1 |
| 0x350A Return to boiler temp sensor | 0x20016a24 tekst „T. powrotu=” (230,180) | 0 → vis=0; 1 → vis=1 |
| 0x2005 Boiler on/off | 0x20016918 ikona (398,53) | 0 → bmp 120, 1 → bmp 122 |
| 0x2002 Boiler program | 0x20016918 ikona; 0x200169ec tekst (358,53) | 0 → bmp 133, tekst „7”; 1 → bmp 135; 3 → bmp 128 (tekst „65” dla 1 i 3) |
| 0x216F CH mixer state | 0x20016acc vis (81,234); 0x20016b24 bmp (100,234) | 0 → vis 0, bmp 107; 1 → vis 1, bmp 106; 2 → vis 1, bmp 107 |
| 0x3629 Energy meter type | 0x20016274 tekst nagłówka (439,0); 0x20016a5c tekst (7,43) vis | 0 → „43”, ukryty; 1/2 → „44”, widoczny |

Zgodne z oczekiwaniami K3: 0x350D („Ciśnienie=”), 0x350A („T. powrotu=”), 0x370A (obraz kotła).
UWAGA (konflikt do rozstrzygnięcia): handoff ChatGPT wymienia „370A 1/2/3 → bitmapa 011/012/013” jako REJECTED; pomiar emulatora (pole +0x26 widżetu i zrzuty) daje dokładnie 1→11, 2→12, 3→13. Prawdopodobnie odrzucona była interpretacja „bitmap ID = widget ID”, nie sama zależność. Do potwierdzenia z ChatGPT.

## Czego pilot NIE potrafi (OPEN / ograniczenie metody)
1. **PID-y klasy live (0x2001 temperatura, 0x2277 pompa, 0x3333 ciśnienie, 0x4000, 0x3628) — wstrzyknięcie przez 0x584 nie dociera do UI.** FACT (emulator): wartość jest przyjęta przez CanRxTask, ale EstymaTask (funkcja RUNTIME 0x08068FE4, strh/strb przy 0x08068FFE/0x08069022, ~co 90 tików) odświeża ją ze źródła `[this+0xB4]` (slot 1 vtable, RUNTIME 0x0801EBA1 / obiekt czujnika 0x200103F8, flaga bramki `[0x20023F54+0xA]`) i przy statusie 3 („brak danych”) czyści do 0. Zapis wprost do obiektu czujnika też jest nadpisywany (producent niżej: źródło `[obj+0x18]` slot 2/3, kanał `[obj+0x1C]`, prawdopodobnie dane z modułów CAN, SDO węzłów 5/6/7 — patrz PASS 43/54). Wniosek: wiązania live (duży tekst temperatury, ikona/animacja pompy) wymagają symulacji ramek modułów, nie 0x584. Ikona pompy (widżet 0x200162f8) to ANIMACJA klatek 138→142 zależna od czasu, nie prosta bitmapa.
2. 0x3333: etykieta „Ciśnienie=” widoczna tylko przy 0x350D=1; wiązanie wartości wymaga wstrzyknięcia warunkowego (para PID) — nie zrobione.
3. Wartości min/max/środek mogą być poza realnym zakresem; zastosować wartości typowe przy skalowaniu.

## Werdykt pilota
K1, K2, K4, K5 spełnione; K3 spełnione dla PID-ów typu nastawa/konfiguracja (7 wiązań, 11 widżetów), niespełnione dla live (przyczyna ustalona, patrz wyżej). Skalowanie na Palnik/Ogrzewanie 1/Woda jest sensowne dla warstwy nastaw; dla live trzeba najpierw modułowego źródła danych.
