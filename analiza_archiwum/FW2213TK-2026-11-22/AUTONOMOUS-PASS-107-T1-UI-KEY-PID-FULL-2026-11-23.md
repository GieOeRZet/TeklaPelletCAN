# AUTONOMOUS-PASS-107-T1-UI-KEY-PID-FULL-2026-11-23

## Cel
Zamknięcie tabeli resolver_t1 dla kluczy UI rodziny obiegów CH. Źródłem jest dokładny plik `analiza_archiwum/FW2213TK-2026-11-22/data/resolver_t1.csv` z gałęzi roboczej ChatGPT.

## HARD
- Tabela zawiera **49 rekordów**, indeksy 0..48.
- Reguła wszystkich rekordów: `PID = value + instancja - 1`.
- Klucze obejmują bazę parametrów CH od `0x00A8` do `0x00D6`, plus testowe `0x0145` i `0x0146`.
- Przykłady: `0x00B0 -> 0x22A1` (Room temp sensor type), `0x00CB -> 0x22F5` (CH needed temp.), `0x00CD -> 0x2301` (CH thermostat state), `0x00D6 -> 0x2329` (CH circuit name part3).
- To jest tabela źródłowa T1; nie jest to zgadywanie semantyki na podstawie geometrii.

## Zakres
PASS zamyka pełny eksport T1. Reconciliation z T2 i wszystkie wystąpienia kluczy w presenterach pozostają osobnym zadaniem.

## Weryfikacja
Test sprawdza liczbę 49 rekordów, indeksy 0..48, unikalność kluczy oraz kilka reprezentatywnych mapowań.
