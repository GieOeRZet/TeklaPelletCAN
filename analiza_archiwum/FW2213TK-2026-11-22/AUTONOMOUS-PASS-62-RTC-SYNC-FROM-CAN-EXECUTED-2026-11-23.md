# AUTONOMOUS PASS 62 — SYNCHRONIZACJA ZEGARA PANELU Z CAN (PID 0x2165 + 0x372F) — WYKONANE W EMULATORZE — 2026-11-23

Cel: dynamiczna weryfikacja statycznego toru ChatGPT (PASS 73–78): CAN 0x584 -> PID 0x2165 "Compatibility timestamp" -> obiekt auto-sync 0x20008D1C -> bramka 0x372F -> RTC.
Narzedzie: `tools/rtc_timestamp_probe.py` (nowe). Poprawka modelu: `tools/stm32_rtc.py` (zapis TR/DR przyjmowany przy ISR.INIT **lub** ISR.INITF; hak MEM_WRITE Unicorn dziala przed zapisem, wiec firmware widzi juz INIT=0, INITF=1).
Dane: `data/rtc_timestamp_probe.json`; obraz: `screens/pass62_rtc_sync_from_can_0x2165.png`.

## Przebieg
Rozruch z modelem RTC (2000-11-30 00:00), `set_local(0x372F, 0|1)`, ramka `0x584: 42 65 21 01 <u32 LE>` (ts = 1795437296 = 2026-11-23 12:34:56 UTC) przez prawdziwy handler RX, 1500 tikow.

| przypadek | storage 0x2165 (0x20008D28) | zapis RTC | zegar panelu po |
|---|---|---|---|
| 0x372F=0, ramka ts | = ts | NIE | 2000-11-30 (bez zmian), obj+0x0C nadpisane z RTC |
| 0x372F=1, ramka ts | = ts | **TAK**: TR=0x123456, DR=0x261123 | **2026-11-23 12:34:56**, ekran: "12:34 Poniedzialek" |
| 0x372F=1, bez ramki | — | NIE | bez zmian |

## FACT (wykonanie)
- Ramka `0x584 42 65 21 01 <u32 LE unix>` zapisuje PID 0x2165 (storage 0x20008D28) — potwierdza PASS 77/78.
- Przy 0x372F=1 funkcja `0x08072638` (PROJECT 0x08062638) wykrywa [obj+0x10] != [obj+0x0C] i zapisuje sprzetowy RTC przez `0x08028E94` (HAL SetTime/SetDate, klucze WPR 0xCA/0x53). Przy 0x372F=0 RTC nie jest zapisywany, a obj+0x0C wraca do czasu z RTC.
- **Brak strefy czasowej**: RTC dostaje dokladnie godzine UTC z timestampu (12:34:56 dla ...12:34:56 UTC). Nadawca musi wyslac czas lokalny zakodowany jako "unix", jesli panel ma pokazywac czas lokalny.
- Funkcja synchronizacji pracuje co 10. wywolanie schedulera (licznik [obj+0x14], `cmp #0xa`): opoznienie zastosowania ~kilkaset tikow (tu tick 1118 po wstrzyknieciu ~550).
- Kod 0x08072638 przy okazji co cykl zbiera bity stanu pomp/wyjsc (0x2299, 0x229A..0x229C, 0x311C, 0x2277, 0x2278) do [obj+8] — znaczenie OPEN.

## Odpowiedz na pytania ChatGPT (COORDINATION)
- Q3 (toggle 0x372F -> ruch CAN?): w tym przebiegu panel nie nadal zadnej ramki zwiazanej z czasem; 0x372F tylko otwiera zapis RTC. (Ramek panelu nie rozroznialem od tla w tym tescie — OPEN dla pelnej pewnosci.)
- Q4 (23. wartosc tabeli 0x20008C50 po rozruchu): **16**. Pelna kolejnosc wpisow [wsk+8]: 10,18,120,180,230,12,15,25,35,50,75,2000,2500,3000,16,30,150,220,300,500,1550,1220,1300 (RAM po rozruchu, emulator).

## Znaczenie dla ESP32 (etap odlozony)
Synchronizacja czasu z naszego modulu: wyslac `0x584 42 65 21 01 <ts LE>` przy 0x372F=1 na panelu. To jest gotowa, sprawdzona w emulatorze droga dla TODO "synchronizacja czasu" z 00_AGENT_START_HERE.md. Weryfikacja na zywym urzadzeniu: OPEN.

## OPEN
- Czy sterownik kotla sam nadaje 0x2165 (kto jest producentem w realnej sieci).
- Ramka TX panelu po zmianie czasu z dialogu "Ustaw czas" (pytanie Q1/Q2 ChatGPT).
