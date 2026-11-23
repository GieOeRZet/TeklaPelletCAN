# PASS 52 — ekran glowny (zaleznosci danych), RTC, narzedzia pokrycia

## Ekran glowny: odswiezanie (presenter `0x08041CC9..0x080420BE`, HARD)
`data/home_presenter_keys.txt` = 47 wywolan model_get z kluczem UI -> PID -> nazwa (tabele T1 49 kluczy + T2 372 kluczy, bez kolizji).
Wazniejsze: Is reset required (0x3728), Outside temperature (0x215F) + averaged (0x3721), Boiler on/off (0x2005), CH/Hot water program, Burner state (0x2007), Boiler temp (0x2001), Boiler set result temp (0x2004),
Refueling need request (0x2266), Reserve sensor state (0x3607), Heating/Hot water/Buffer configuration (0x2105/6/7), Boiler image selector (0x370A), Is fuel reserve (0x3602), Tank capacity (0x3600), Fuel reserve (0x3603), How much fuel left (0x3601),
Start settings recovery (0x3722) + Settings recovered count (0x3723) (te dwa PID-y handler RX 0x08072B22 POMIJA — nigdy nie sa nadpisywane z CAN), Out temp radio sensor (bateria 0x3724, sygnal 0x3725, wersja 0x372B/C, czas 0x3726), Is summer time (0x3729), 0x373C/0x373D (bez rekordu).
Mapa uzycia wszystkich kluczy UI: `data/ui_key_usage.csv` (168 kluczy, 273 wywolania; `tools/ui_key_usage.py`); lista wywolan w funkcji: `tools/fn_keys.py`.
- Burner state (0x2007) w emulatorze: wartosci 0..2 -> "Wylaczony", 3..4 -> "Moc 1" (kafel plomienia zolty); >=5 odrzucane (wraca 0) — pelna lista stanow do zbadania.

## RTC (`tools/stm32_rtc.py`, `UiSession(rtc_start=datetime)`)
TR/DR w BCD, czas plynie z licznikiem systick (1 tik = 1 ms), zapis w trybie INIT przesuwa zegar. **Konwencja WDU firmware: 0=poniedzialek..6=niedziela** (WDU=1 pokazuje "Wtorek"). Domyslnie (RTC=0) panel pokazuje 0:00, Poniedzialek, data alarmow 30.11.2000.

## Narzedzia pokrycia
`tools/gate_trace.py` (hook blokow -> `cov_*.json`), `tools/coverage_boot.py` (rozruch+ekran glowny+okna), `tools/coverage_report.py` (cele BL = funkcje; wykonane = poczatki blokow). Wynik: patrz kolejny raport po zakonczeniu przebiegow.
`UiSession.inject_param(pid, val)`: realistyczne wstrzykniecie przez RX handler (wymaga otwarcia okna `poller+0xC` i bramki `poller+0x10`; ramke trzeba powtorzyc 2-3x).

## Stany palnika (Burner state 0x2007) -> tekst na ekranie glownym (HARD: tabela `0x0803DBBC`, 11 par {stan, TypedText-57}, setter `0x0803D7A4`)
0 Wylaczony | 1 Rozpalanie | 2 Rozzarzanie | 3 Moc 1 | 4 Moc 2 | 5 Modulacja (+wartosc, jednostka kg) | 6 Wygaszanie (°C) | 7 Czyszczenie (s) | 8 Podtrzymanie (%) | 9 Postoj (kg) | 10 Alarm (%). Stan >=11 ignorowany.
Wartosci 9/10 daja wyjatki w logice kafla plomienia (`0x08041E28`: stan 0, 9 lub 10 -> wyzerowany znacznik). W emulatorze wstrzykniecie stanow >=5 nie utrwalilo sie w storage (do wyjasnienia: dodatkowa walidacja/nadpisanie lokalne).

## Konfiguracja sprzetowa / profil / moduly — wynik: parametry PRZELOTOWE (HARD dla panelu)
Blok ustawien `0x20021FA0..0x20021FC0`: jedyny literal w kodzie to baza `0x20021FA0` (39 odwolan), a odczytywane z niej jest wylacznie pole `+7` (= PID 0x0005 Default settings request; wskaznik naglowka/tick handlery) oraz pomocnicze `0x08024470/0x08024498` (tracker klawiszy) i `0x0804C220` (handler PIN).
Pozostale PID-y bloku — **Main module type 0x3500, CH expansion module type 0x3502, Profile number 0x350B, Autoconfig 0x3501, Outside temperature sensor configuration 0x3505, Return to boiler sensor 0x350A, Is this device cascade master 0x350C, Pressure sensor 0x350D, Is reset required 0x3728** — poza rejestracja w tabeli rekordow (`0x08011B4C`, `0x08011BB4`, `0x08011C1A`, `0x0801A4E6`, `0x0801A540`, `0x0801A802`, `0x0801A924`, `0x0801A98A`, `0x0801D68E`) NIE sa interpretowane przez logike panelu: panel je przechowuje, edytuje na ekranie Konfiguracja i synchronizuje po CAN; znaczenie (np. co daje Profile 1..3, typ modulu) lezy po stronie sterownika kotla.
Kilka z nich ma wplyw na UI przez klucz UI: Return to boiler sensor (`0x0804CBBC`), Pressure sensor (`0x0804CB70`), Is this device cascade master (`0x0804E466`, 2 miejsca — widocznosc/lista Kaskady), Is reset required (ekran glowny `0x08041D46`).
PID-y 0x3722 "Start settings recovery" i 0x3723 "Settings recovered count" sa wyjete spod zapisu z CAN (`0x08072B38`) — wlasne mechanizmy panelu (odzyskiwanie ustawien), do zbadania razem z 6666.

## Widocznosc wierszy MENU (HARD: funkcja `0x0804C178`, klasa wiersza -> warunek)
Klasa 1..4 (Ogrzewanie obwod 1..4): widoczna gdy Heating configuration (0x2105) >= numer obwodu. Klasa 5 (Ciepla woda): Hot water configuration (0x2106) != 0. Klasa 6 (Solary): Solar configuration (0x2108) != 0.
Klasa 7 (Bufor): Buffer configuration (0x2107) != 0. **Klasa 8 (Kaskada): Is this device cascade master (0x350C) != 0.** **Klasa 9 (Dodatkowy magazyn paliwa): Additional fuel storage (0x3525) != 0.** Pozostale klasy: zawsze widoczne.
Tabela klasa<->wiersz: `data/menu_click_effects_21.csv` (wiersze 9 i 10 w kolejnosci konstruktora = Kaskada i Dod. magazyn; w eksploracjach L0..L3 byly ukryte konfiguracja domyslna).
Prezenter ekranu Kaskada: `0x0804E45C` (klucze 0x11C, 0x157, 0x153..0x156, 0x158, 0x0C, 0x31..0x37...).

## Ekrany Kaskada i Magazyn paliwa — wyrenderowane (HARD, `screens/pass52_kaskada_magazyn_paliwa.png`)
Wlaczone przez `set_local`: Is this device cascade master (0x350C)=1, Additional fuel storage (0x3525)=1, Cascade slaves number (0x351A)=2 (poziom 2).
- **KASKADA**: trzy "kotly" (MASTER, SLAVE 1, SLAVE 2; slave z "---" czerwonym = brak danych), temperatura, "Stopien mocy N"; kafel NASTAWY: Liczba kotlow slave, Master/Slave 1..3 stopien mocy (+ progi) — lista klasa 8 (`panel_lists_by_level.md`).
- **MAGAZYN PALIWA**: schemat zasobnika z dwoma silnikami (1 transport, 2 podajnik); NASTAWY: Praca/Pauza silnika transportujacego (1) [s], Praca/Pauza silnika podajnika (2) [s] (klasa 9).

## Edycja wartosci (HARD, emulator): dialog numeryczny -> zapis -> CAN
Kociol / NASTAWY, wiersz "Temperatura zadana [°C]" (PID 0x2003, 60..80, 65): dotkniecie wiersza otwiera dialog (tytul = nazwa, suwak z min/max z deskryptora, duza wartosc, przyciski "-" (125,205), "+" (295,205), "OK" (415,230)).
3x "+" i OK -> storage 0x2003 = 68 i panel wysyla **CAN 0x584: `42 03 20 01 44 00 00 00`** (cmd 0x42, indeks PID LE `03 20`, subindeks 1, wartosc u32 LE = 68). Zapis uzytkownika = ta sama ramka co odpowiedz sterownika.
