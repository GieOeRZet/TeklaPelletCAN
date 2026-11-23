# PASS 54 — ekran INTERNET (WiFi), moduly CAN (VIDE NET), co z lacznoscia (HARD: kod + emulator; wnioski oznaczone)

## Ekran INTERNET (render `screens` + `data/`)
Pola: **SSID**, **PASSWORD** (teksty, wartosci szare), **SERIAL: n**, **PIN: n**, przelaczniki **WiFi** i **Zmiany zdalne**, ikona zasiegu WiFi (prawy gorny rog, bitmapy 153/154).
Dane = PID-y panelu (rekordy w tabeli runtime):
- SSID = `0x3730..0x3735` (6 x u32 = 24 znaki, **kolejnosc bajtow big-endian w kazdym u32**: "Home" = 0x486F6D65), haslo = `0x3736..0x373B` (KEY part 1..6), obie grupy klasy 3 (ustawienia, 0..4294967295).
- `0x373C`/`0x373D` (u8, klasa 0, status; **0x373D = 2 pokazuje ikone WiFi**), `0x3746` (u8), `0x3744` (u8; po ustawieniu — etykieta SSID na czerwono), `0x3745` (u8), `0x373E` (u8 klasa 3 — przelacznik WiFi), `0x3741` (u8 klasa 3 — "Zmiany zdalne"), `0x373F`/`0x3740` (u32: SERIAL / PIN). Pelna zaleznosc wizualna (logika kolorow etykiet SSID/PASSWORD, ikona) zalezy od kombinacji flag — do zbadania; pojedyncze wstrzykniecia czesto nie zmieniaja obrazu.
- `0x372F` "Is automatic time synchronization" (u8, klasa 3, 0..1) — automatyczna synchronizacja czasu istnieje jako parametr (zrodlo czasu nie zbadane) — **istotne dla TODO synchronizacji zegara**.
- Prezenter: `0x0804DA00..0x0804DD56`.

## Skad WiFi? (wniosek)
- Panel NIE ma WiFi: w aplikacji uzywane sa tylko CAN, I2C (dotyk), RTC, LTDC, DMA2D, SDRAM, GPIO. Sterowniki UART5/UART8/I2C3 wystepuja tylko w nieuzywanym kodzie biblioteki HAL (blok `0x0802C000..0x08038000`, 0% wykonania) — brak aktywnej komunikacji szeregowej/USB/Ethernet.
- Firmware zna **moduly CAN Estyma** (tablica `0x0801F9B2`, `data/can_node_names.csv`): m.in. **0x5A=VIDE GSM, 0x5B=VIDE NET WIFI, 0x5C=VIDE NET**, 0x64..0x67 VIDE ROOM 1..4, 0x56/0x57 CAN IO BIG, 0x40..0x47 CAN IO 0..7, 0x50 MODUL LAMBDA, 0x51 IO BOARD PRO, 0x54/0x55 FLOWMETER 1/2, 0x6E..0x75 CAN GATEWAY 0..7, 0x78..0x7F CAN IO MINI 0..7, 0x08 RADIO GATEWAY, 0x05..0x07 SLAVE 1..3.
  => lacze WiFi/internet to **zewnetrzny modul na CAN ("VIDE NET WIFI")**; ekran INTERNET to jego konfiguracja i status po stronie panelu. Parametry SSID/KEY/SERIAL/PIN sa parametrami sterownika (wymieniane po CAN jak wszystkie PID-y); modul chmurowy czyta je/pisze po CAN. (Niezweryfikowane: dokladny protokol modulu — brak go w panelu.)
- Wniosek dla integracji (HA/ESP32): **jedyny zewnetrzny interfejs panelu to CAN** — brama ESP32 + transceiver CAN jest wlasciwa droga (jak planowane); mozliwy tez wariant "ESP32 jako wezel VIDE NET WIFI (0x5B)", zeby panel traktowal go jak oficjalny modul (alarm "Komunikacja z modulem ..." i identyfikacja wg `0x1018:02` — do przetestowania).
