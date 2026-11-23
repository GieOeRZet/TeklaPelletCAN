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
