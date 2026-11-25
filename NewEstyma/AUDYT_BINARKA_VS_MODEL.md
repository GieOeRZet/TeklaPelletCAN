# Audyt: binarka FW2213TK vs wiedza w projekcie (2026-11-25)

Narzedzie: `tools/audit_bin_vs_model.py` (statyczny przekroj `decompiled.c` + tabele + dane `ui_model`; wynik JSON: `NewEstyma/audyt_binarka_vs_model.json`). Dowod: MEASURED (liczenie), interpretacje oznaczone osobno.

## Liczby

| Przekroj | Wynik |
|---|---|
| PID-y w katalogu | 655 (bez wzmianki w modelu UI: 211) |
| PID-y czytane przez kod UI (presentery) | 154, z tego BEZ wzmianki w modelu: 24 |
| Presentery (funkcje czytajace model, >=3 klucze) | 13 |
| Teksty TypedText | 496; widziane w emulatorze 301; niewidziane 195, z tego nieopisane w danych 75 |
| Bitmapy | 188; widziane 119; niewidziane i nieopisane 39 |

## Zamkniete przy tym audycie (z kodu/binarki)

- Tabele stanow z binarki: stan palnika 0-10 (Wylaczony..Alarm), stan solarow 0-9, ikony programu kotla (0x2002 -> bitmapy 133/135/122/128/120). Zapis: `real_panel_screens.json` -> `status_tables_from_binary_2026_11_25`. To domyka wiekszosc 'niewidzianych' tekstow stanow (Postoj, Przeplukiwanie, Zamarzanie, Woda max, Wylaczone, Chlodzenie...).
- Ekran INTERNET: 0x373C (sygnal), 0x373D (stan polaczenia), 0x3744/0x3745 (kolory), 0x3746 (widocznosc) - korekta wczesniejszego 'not_sources'. Zapis: `internet_screen.json` -> `code_analysis_2026_11_25`.
- Dolne belki: mapa komorka -> PID dla 8 ekranow, 21 par test->stan (poprzednie wpisy).

## Luki: PID-y czytane przez kod, bez wzmianki w modelu (24)

| PID | nazwa | tryb | presentery |
|---|---|---|---|
| 0x200d | Remote boiler 1 requested temp[C] | live | 0803e45c |
| 0x200e | Remote boiler 2 requested temp[C] | live | 0803e45c |
| 0x2119 | Exhaust gas temperature (2) [C] | live | 0803cf54 |
| 0x2309 | Room temp. radio sensor batt. volt [mV] | live | 0803d37c |
| 0x230d | Room temp. radio sensor signal [%] | live | 0803d37c |
| 0x2311 | Room temp. radio sensor time since lasr rec. | live | 0803d37c |
| 0x2319 | Room temp. radio sensor soft. ver. before dot | live | 0803d37c |
| 0x231d | Room temp. radio sensor soft. ver. after dot | live | 0803d37c |
| 0x2325 | CH circuit name part2 | setting | 0803d37c, 0803eb4a, 0803ec18 |
| 0x2329 | CH circuit name part3 | setting | 0803d37c, 0803eb4a, 0803ec18 |
| 0x300a | Sec. air mixer position [%] | live | 0803cf54 |
| 0x300b | Stop burning wood | command | 0803cf54 |
| 0x351b | Cascade timer to inc power lvel [s] | live | 0803e45c |
| 0x3602 | Is fuel reserve | live | 08031ccc |
| 0x3721 | Outside temperature averaged | live | 08031ccc |
| 0x3723 | Settings recovered count | command | 08031ccc |
| 0x3724 | Out temp. radio sensor batt. volt [mV] | live | 08031ccc |
| 0x3725 | Out temp. radio sensor signal [%] | live | 08031ccc |
| 0x3726 | Out temp. radio sensor time since lasr rec. | live | 08031ccc |
| 0x3728 | Is reset required | live | 08031ccc |
| 0x3729 | Is summer time | live | 08031ccc |
| 0x372b | Out temp. radio sensor sw. ver. before dot | live | 08031ccc |
| 0x372c | Out temp. radio sensor sw. ver. after dot | live | 08031ccc |
| 0x400a | Virt. energy consumer set temp [C] | command | 0803e45c |

Grupy: czujnik radiowy temp. zewnetrznej (0x3724-0x372C: bateria, sygnal, czas od odbioru, wersja) i pokojowy (0x2309-0x231D) - ekran/okno szczegolow czujnika (nieopisane); kaskada (0x200D/0x200E/0x351B/0x400A); 0x3602 'Is fuel reserve'; 0x3728 'reset required'; 0x3729 'summer time'; 0x3723 'settings recovered count'; 0x300A/0x300B (powietrze wtorne, 'stop burning wood'); 0x2119 spaliny(2); nazwy obwodu CO (0x2325/0x2329).

## Luki: presentery vs znane ekrany

| funkcja | wywolan modelu | PID-y | z tego opisanych |
|---|---|---|---|
| 0x8031ccc | 47 | 33 | 23 |
| 0x803cf54 | 33 | 28 | 24 |
| 0x803d37c | 25 | 21 | 14 |
| 0x803e45c | 19 | 19 | 15 |
| 0x803cb2c | 14 | 14 | 14 |
| 0x803ec18 | 13 | 13 | 11 |
| 0x803df78 | 10 | 10 | 10 |
| 0x803d744 | 7 | 7 | 7 |
| 0x803dcc6 | 7 | 7 | 7 |
| 0x803e148 | 6 | 6 | 6 |
| 0x803e2e8 | 5 | 5 | 5 |
| 0x803d516 | 3 | 3 | 3 |
| 0x803eb4a | 3 | 3 | 1 |

Presentery z nizszym pokryciem: 0x0803dcc6 (INTERNET - uzupelnione), 0x0803eb4a (edytor nazwy obwodu CO), 0x0803ec18 (charakterystyki dmuchawy/wentylatora wyciagowego).

## Luki: bitmapy niewidziane i nieopisane (39)

Rozpoznane z wygladu (INFERENCE): 12 duzy rysunek kotla (wybor wg 0x370A), 16 drzwi/ikona, 18 kopiowanie, 19/20 pole wyboru (puste/zaznaczone), 26/57/151/152 kontrolki okragle, 27 pomaranczowy pasek, 33 dom, 43/45 plomien (aktywny/zgaszony), 102/103/117/118 przyciski -/+ (155x38), 111 OK, 115 przycisk zasilania, 116 drzwi/wyjscie, 119 plus, 120/121 platek sniegu, 125 slonce 'comf', 136/137 zegar (M / zwykly), 140/142 strzalki lewo/prawo, 144/146/147 grzejnik 1/2 (aktywny/nieaktywny), 160 tlo 241x49, 164/166 suwak pionowy, 173 kominiarz, 174/176 kran (CWU), 182/183 palnik z zaplonem / z STOP. Pelne ID: JSON `bitmaps_never_seen_undocumented`.

## Luki: teksty niewidziane i nieopisane (75)

Glownie: parametry gleboko w listach ustawien (lista przestaje sie przewijac po ~3 wierszach, BACKLOG), teksty alarmow (Zwarcie/Przerwa czujnika CWU/pokojowego, Przegrzanie solarow, Reset procesora, STB), klawiatury edytora tekstu (zestawy znakow). Lista: JSON `texts_unseen_and_undocumented`.

## Nieprzejrzane funkcje widoku HOME (tabele DAT, do rozkodowania)

Settery w zakresie 0x0802d238-0x0802ef32 z tabelami danych: 0x0802d238/2f4 (zegar/data), 0x0802d440/572 (formaty temperatur), 0x0802da54, 0x0802dbf4, 0x0802df80 (4,7 KB), 0x0802e484, 0x0802e716 (3 KB), 0x0802ea1e, 0x0802eade, 0x0802ed08, 0x0802ef32. Tam leza m.in. ikona pogody (0x3721 srednia temp. zewn.), ikony trybow CO/CWU na kafelkach i logika kafelkow. Nastepny krok audytu.
