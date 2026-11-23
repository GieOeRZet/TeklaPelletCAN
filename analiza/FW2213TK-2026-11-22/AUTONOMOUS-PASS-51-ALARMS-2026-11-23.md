# PASS 51 — alarmy: pamiec alarmow, format wpisu, kody -> teksty (HARD: kod + emulator)

## Pamiec alarmow (runtime, 20 wpisow)
- PID `0x4010+i` "Alarm register" (u32), `0x4024+i` "Alarm date timestamp" (u32), `0x4038+i` "Alarm confirm timestamp" (u32), i=0..19; storage `0x20021E9C + 12*i` (trojki rejestr/data/potwierdzenie); `0x404C` Alarm next index (u8 0..19, `0x20021F8C`), `0x404D` Number of alarms (u8 0..20, `0x20021F8D`), `0x404E` Request reset alarm memory (u8, `0x20021F94`).
- Rejestracja rekordow: `0x0801D2E2..` (`0x802143C` x60); klucze `0x4010` itd. NIE maja kluczy UI (brak w resolver_t1/t2) — widok czyta je wprost.
- Presenter: `0x08047448` buduje liste 20 wpisow (struktura 0x18 B/wpis) czytajac 3 PID-y na wpis (`0x80215F6`): 
  `+0` u32 = rejestr (**low16 = kod alarmu**, bit16 = flaga "aktywny" -> bajt `+0x11`), `+4..` data zdarzenia {u8 min? , u8 dzien, u8 miesiac, u8 0, u16 rok} i czas {u8 0, min, godz}, ditto dla potwierdzenia.
  Konwersja `timestamp -> data` = `0x08049370` (gmtime: rok+1900/`+0x76C`, miesiac+1): **timestamp = Unix epoch sekundy, UTC** (1700000000 -> 14.11.2023 22:13). Data 1970 (0x7B2) = brak -> wyswietla "00.00.0000".
- Widok "Historia alarmow" (`0x0805049C` format daty `%d%d.%d%d.%d`, `0x080503FC` czas `%d:%d%d`, `0x0805037A` kod + tekst): ekran pokazuje jeden wpis: NR, KOD, tekst, "Powstanie: DD.MM.RRRR G:MM", POTWIERDZ, status (AKTYWNY czerwony). Strzalki gora/dol = nawigacja.
- Stan domyslny po starcie: wpisy 3..5 maja fabryczne dane przykladowe: rejestry `0x30064/0x30069/0x3006E` (kody 100,105,110), data `30.11.2000` — to widac na ekranie bez zadnych danych z kotla.
- Wstrzykiwanie: `UiSession.inject_param` (zwalnia okno `poller+0xC` i bramke `poller+0x10`); `0x404D` nie dala sie ustawic ta droga (klasa 1/obliczana lokalnie — do zbadania).

## Kody alarmow -> teksty
`data/alarm_codes_texts.csv`: 68 pozycji (tabela `0x0805098C`, pary u16 {kod, id_tekstu-57}; TypedText = pole+57). Przyklady: 1 Uszkodzenie czujnika kotla, 2 Przegrzanie kotla, 5 STB, 110 Komunikacja z modulem BIG, 140 Brak ognia/opalu, 130 Blad czyszczenia, 200 Blad czyszczenia rusztu.

## Otwarte
- sposob wyboru "biezacego" wpisu (next index/number of alarms), sortowanie, znaczenie bit17 rejestru;
- akcja POTWIERDZ (ramka CAN / zapis `0x4038+i`), "!" na ekranie glownym i dzwiek (PID 0x3506), reset pamieci (0x404E);
- RTC: panel pokazuje czas `0:00` (brak modelu RTC w emulatorze).
