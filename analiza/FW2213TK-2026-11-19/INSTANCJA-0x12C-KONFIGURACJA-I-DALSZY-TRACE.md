# FW2213TK — dalszy trace instancji modułu CH, 2026-11-19

## Nowe potwierdzenia z firmware

### 1. +0x12C jest aktywnie konfigurowane
Runtime/raw 0x08048130 / raw 0x38130:
- r1 jest normalizowane do 1..4 (>=5 -> 4, pozostałe -> 1),
- module+0x10C+0x1F dostaje mapowanie zależne od r1,
- module+0x12C = r1.

To jest bezpośredni zapis numeru instancji do obiektu modułu.

### 2. Konkretne ścieżki ustawiające instancję 1 i 2
Runtime/raw 0x08042146 / raw 0x32146: po sprawdzeniu parametru wewnętrznego 0x10E wywołuje 0x38130 z r1=1.
Runtime/raw 0x08042166 / raw 0x32166: analogicznie wywołuje 0x38130 z r1=2.

### 3. Jest też bezpośredni wybór 1..4
Runtime/raw 0x0803C0B6 / raw 0x3C0B6 zawiera ścieżki z r1=1,2,3,4, wszystkie kończące się w 0x38130.

### 4. +0x12A i +0x12C są różnymi polami
Runtime/raw 0x08037DEC / raw 0x37DEC odczytuje module+0x12A+2 i na tej podstawie klasyfikuje moduł. +0x12C nie bierze udziału w tej klasyfikacji.

Najbezpieczniejszy opis:
- +0x12A = typ/konfiguracja modułu,
- +0x12C = numer instancji 1..4.

### 5. RAM CO2 nadal nie jest dowiedziony
Dynamiczny lookup 0x1167A wykonuje dokładnie lookup_index = baza + module_instance - 1 i szuka indeksu w strukturze rekordów.
Indeks CAN CO2 (np. 0x2033 dla bazy 0x2032) jest pewny, ale źródło RAM CO2 nadal nie.

## Następny krok
Trace miejsca, gdzie po ustawieniu +0x12C moduł dostaje źródło danych / rekord parametru. Priorytet: 0x37212, 0x36FF2, funkcje 0x37F88–0x3A440 oraz miejsca przekazujące module+... jako r2 do mechanizmu rekordów.