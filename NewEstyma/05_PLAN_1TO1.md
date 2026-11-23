# PLAN: co zostalo do wiernej repliki 1:1 panelu igneoTouch v2.213 TE (stan 2026-11-23)
Zakres: ekrany, dane, zachowanie, protokol CAN panelu. Poza zakresem (odlozone): ESP32/HA, skalowanie, poziom 3 (6154), kod 6666 (patrz TODO w 00_AGENT_START_HERE.md).
Szacunki gotowosci (nie metryki): dane/protokol ~85%, zachowanie ~70%, wyglad (geometria/czcionki/kolory) ~35%, test akceptacyjny ~15%.

## A. WYGLAD (najwiekszy brak)
A1. **Czcionki** — NIE wyeksportowane. Trzeba: znalezc tablice czcionek TouchGFX (glify, metryki, kerning, interlinia) w obrazie, wyeksportowac do plikow + podglad; bez tego tekst nie bedzie 1:1. (nowe narzedzie: `tools/export_fonts.py`)
A2. **Inwentarz widgetow dla KAZDEGO ekranu i wariantu**: klasa (Image/TextArea/Box/Button/Slider/Toggle/ScrollList/...), pozycja, rozmiar, bitmapa, TypedText, kolor, wyrownanie, widocznosc, dotykowosc. Narzedzie jest (`tools/widget_dump.py`, `widget_inventory.py`, `widget_catalog.py`); do poprawy: odczyt id tekstu (offset zalezy od klasy TextArea/z wildcardem — dzis tytuly bywaja bledne), rozpoznanie klas po vptr, uruchomienie na wszystkich stanach (poziomy 0/1/2, konfiguracje, jezyki).
A3. **Kolory i tla**: paleta tekstow/tel; zagadka tla szare(0x2945)/czerwone(0xF945) — ustalic regule (funkcja 0x08049390 wybiera wg ctx+0x129 i wartosci z RAM 0x20024888; znalezc kto ustawia).
A4. **Wszystkie 8 jezykow**: eksport TypedText (PL EN LT SK CZ ES RO EST) do CSV + zachowanie wildcardow (jednostki, wartosci), zawijanie, wyrownanie.
A5. **Animacje/przejscia** (przesuniecie ekranow, okna) i **fizyka przewijania list**: stale TouchGFX (wczesniej odlozone przez wlasciciela — wymagane dopiero dla ostatecznego 1:1 zachowania).
A6. **Pozostale ekrany do uchwycenia**: Test wyjsc, lista Jezyk, Siec z modulami, Statystyki (pelna lista), PROGRAM (tygodniowy — edycja slotow), dialog czasu/daty ("Ustaw czas"), dialog Paliwo (wszystkie warianty), wykresy (strony 0x47/0x48), Info (warianty), okna potwierdzen/bledow.

## B. DANE NA EKRANACH (reguly formatowania)
B1. Dla kazdego pola: PID/klucz -> format (jednostka, miejsca po przecinku, skala 0.1, "---" przy 5678/brak danych, kolory ostrzezen). Mamy: ekran glowny (47 kluczy), Kaskada (20), alarmy, Internet (czesc). Brakuje: Kociol/Palnik/CO/CWU/Solar/Bufor/Statystyki/Info (prezentery), wartosci "7°C"/"0%"/"Ochrona kotla" (warunki).
B2. Stany/enumy: tabela stanow palnika (jest), statusy CO/CWU/Solar/Bufor/pompy/mieszacze, stany kaskady.

## C. ZACHOWANIE
C1. **Alarmy**: wybor biezacego wpisu (next index/number), kasowanie aktywnosci, potwierdzanie (jest), wskaznik na ekranie glownym (jest), dzwiek (PID 0x3506), warunki 36 miejsc raise (`data/alarm_raise_clear_sites.csv`) — kazdy ma warunek w kodzie panelu do wypisania.
C2. **Zapisy uzytkownika**: kazdy typ wiersza/dialogu (liczba, przelacznik, lista wyboru, czas, tekst) -> reguly, krok, min/max, ramka CAN (jest dla liczby), walidacja, odrzucenia (kody 6/7/9).
C3. **Tryby ekranu glownego/okna power**: wplyw suwakow trybu i AUTO na PID-y i ramki CAN (nie prześledzone).
C4. **Poziomy dostepu 0/1/2**: specyfikacja jest (`SPEC-POZIOMY-DOSTEPU-0-1-2.md`); dopisac etykiety PL wszystkich list i mapowanie etykieta->PID; trwalosc poziomu.
C5. **Protokol CAN panelu**: semantyka ramek PDO-podobnych 0x2xx..0x5xx, skan wezlow/heartbeat/identyfikacja, sekwencja startu, timeouty -> alarmy "Komunikacja z modulem".
C6. **Czas**: RTC panelu, dialog ustawienia czasu, parametr 0x372F (auto-synchronizacja) — zrodlo czasu.
C7. **Internet/WiFi**: pelna logika flag (ikona, kolory etykiet), znaczenie 0x373C..0x3746.

## D. TEST AKCEPTACYJNY 1:1 (jeszcze nie istnieje)
D1. Korpus zrzutow z emulatora (wszystkie ekrany x poziomy x konfiguracje x jezyki x stany danych), deterministyczny (RTC, dane wstrzykniete).
D2. Narzedzie porownania replika<->emulator piksel po pikselu z maskami (wskaznik CPU, zegar) i progiem; raport roznic.
D3. Kryterium: 0 roznic na zdefiniowanej liscie ekranow/stanow.

## E. DOMKNIECIE ANALIZY KODU
E1. Prawdziwe pokrycie funkcji (po odsianiu danych udajacych kod: `tools/coverage_static.py`) -> lista nieodwiedzonych galezi UI i ich scenariusze; eksploracja `tools/ui_fuzz.py`.
E2. Wyjasnic: kloda znika po ~3400 tikach; zrodlo 7°C i 0%; warunek "Ochrona kotla"; slider/tekstury (jest).

## Kolejnosc (proponowana)
1) UI-MODEL: view_off -> presenter/PID (narzedzie PASS 59 gotowe; pozostaje pelny przebieg na wszystkich stanach) -> 2) graf akcji widgetow -> 3) warunki widocznosci i dialogi jako dane -> 4) A6 brakujace ekrany -> 5) B1/B2 formatowanie danych -> 6) C1/C2/C3 zachowanie -> 7) D harness -> 8) E zamkniecie.
