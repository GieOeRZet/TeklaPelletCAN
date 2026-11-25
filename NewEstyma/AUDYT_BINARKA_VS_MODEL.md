# Audyt: binarka FW2213TK vs wiedza w projekcie (aktualizacja 2026-11-25)

Narzedzia: `tools/audit_bin_vs_model.py` (przekroj pokrycia; wynik `NewEstyma/audyt_binarka_vs_model.json`) i `tools/presenter_widget_map.py` (klucz UI -> PID -> setter -> widgety; wynik `ui_model/presenter_widget_map.json`). Dowod: MEASURED (liczenie) / STRONG (analiza statyczna kodu).

## Liczby po tej rundzie

| Przekroj | Wynik |
|---|---|
| PID-y w katalogu | 655 (nie czytane przez UI i bez wzmianki: 187) |
| PID-y czytane przez kod UI | 154, **bez opisu w modelu: 0** (bylo 27) |
| Presentery | 13; rozebrane do widgetow: HOME, KOCIOL, PALNIK, OGRZEWANIE, CWU, KASKADA, MAGAZYN (7); zostaja BUFOR, SOLARY, INTERNET (tabela setterow opisana recznie), edytor nazwy CO, charakterystyki dmuchawy |
| Teksty TypedText | 496; niewidziane i nieopisane 74 (bylo 78) |
| Bitmapy | 188; niewidziane i nieopisane 39 (rozpoznane z wygladu: ikony trybow, przyciski) |

## Zamkniete z kodu/binarki w tej serii

- Tabele stanow z binarki: palnik 0-10, solary 0-9, ikony programu kotla `0x2002` (`real_panel_screens.json` -> `status_tables_from_binary_2026_11_25`).
- Dolne belki: mapa komorka -> PID dla wszystkich ekranow, 21 par test->stan, regula stanu = mlodszy bajt SDO.
- HOME: temperatura zewnetrzna (0x215F + srednia 0x3721, tylko gdy 0x3505 != 0), ikona lato/zima 0x3729, WiFi 0x373D/0x373C, tankowanie 0x2266/0x2267, reset 0x3728, dioda palnika dla stanow 1-8 (`home_indicators.json`).
- INTERNET: 0x373C zasieg, 0x373D stan, 0x3744/0x3745 kolory, 0x3746 widocznosc (`internet_screen.json`).
- Mapa presenterow (`presenter_widget_map.json`): 7 ekranow, kazdy setter z PID-ami i widgetami; wszystkie 154 PID-y czytane przez UI sa teraz w modelu.

## Co nadal jest OPEN (z powodami)

1. **Pogoda**: PID-y `0x2161-0x2163` (Weather forecast 0..2, u16, komenda) i `0x2164` (Weather validity left time [min]) istnieja w katalogu, ale ZADEN presenter nie czyta ich przez wspolny getter modelu (klucz 0x6 -> 0x2164 jest w resolverze, brak odczytu w presenterach). Zrodlo ikony pogody na HOME nie jest ustalone - hipoteza: dane pogodowe zapisuje master/modul WiFi (to bylaby funkcja dla ESP), ikona rysowana w funkcjach HOME `0x0802df80`/`0x0802e716` (nieprzejrzane).
2. Widgety nieobecne w inwentarzu emulatora (PALNIK: 0x228C, 0x2119, 0x300A, 0x300B, 0x218B '%d.%dV', 0x371A/0x362B przeplyw; KASKADA: poziomy mocy 0x3511-0x3513): settery znane, brak pozycji widgetu - trzeba je wywolac w emulatorze (konfiguracje: tlen, spaliny, przeplywomierz, kaskada master).
3. PID `0x218B` czytany przez PALNIK (format `%d.%dV`, wartosc +50 mV) NIE istnieje w katalogu 655 (`pid_poza_macierza_655`).
4. 187 PID-ow nie czytanych przez UI: kopie instancji CO2-CO4 (0x2017-0x2019, 0x22AF..., czujniki radiowe, 0x2302-0x2304), rejestry/znaczniki alarmow 0x4011-0x404B (opisane w `alarms.json`), wersje modulow CAN IO/VideRoom, ustawienia bez ekranu (Kp/Ki/Kd 0x227B-0x228A, drewno 0x3001/0x3005/0x3007, powietrze wtorne 0x3008/0x3009, 0x3123/0x3124/0x3713/0x3714/0x3125/0x3126/0x3743 bez nazw) - wymagaja ekranow poziomu 3 (listy przestaja sie przewijac po ~3 wierszach, BACKLOG).
5. Nieprzejrzane funkcje HOME z tabelami: `0x0802da54`, `0x0802dbf4`, `0x0802df80` (4,7 KB), `0x0802e484`, `0x0802e716` (3 KB), `0x0802ea1e`, `0x0802eade`, `0x0802ed08`, `0x0802ef32`.
6. Teksty/bitmapy bez opisu: listy w `audyt_binarka_vs_model.json` (`texts_unseen_and_undocumented`, `bitmaps_never_seen_undocumented`); w wiekszosci parametry glebokich list, teksty alarmow, klawiatury edytora.
