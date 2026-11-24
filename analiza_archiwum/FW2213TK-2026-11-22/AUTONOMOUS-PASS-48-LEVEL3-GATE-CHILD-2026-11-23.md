# PASS 48 — co dodaje PIN 6154 (poziom 3): wskaznik "NN%" w naglowku = obciazenie CPU

## Wynik (HARD, emulator + kod)
- Na poziomie dostepu >=3 **kazdy ekran poza Home** ma w prawym gornym rogu naglowka (x~412..479, y~3..19, nad ikona domu) **liczbe z "%"** (np. "39%"). Na poziomie 2 tego nie ma.
  Porownanie 142 zrzutow L2 vs L3: **141 roznych tylko tym polem**, Home bez roznicy. (Wczesniej maskowalem ten obszar jako "zmienny wskaznik %" — to byl on.)
- To dziecko `+0x23C` 17 wrapperow bramki (`ldrb [model+0x158]; cmp #3; blt`): pole tekstowe 40x30 przy x=439, y=0. NIE przycisk "+" (stare BATCH-6154-LEVEL3 mylilo klase 0x0803FB04).
  Pole `+0x26`=454 jest identyczne w kazdej klasie (nie etykieta; "Prog zmniejszania stopnia mocy" to blad wczesniejszego raportu).
- Tekst jest formatowany w handlerze ticka bazy wiersza (np. 0x0807EC78 i 16 kopii): `snprintf(this+0x274, 6, "%d", *(u8*)0x200243E4)`, po czym `invalidate(+0x23C)`.
- Wartosc `0x200243E4` (u8) liczy petla glowna EstymaTask (0x08072C94): co 10 obrotow `value = 100 - licznik` , licznik `0x20024874` zeruje; licznik inkrementuje
  **hook bezczynnosci** (0x08066AD0: petla kalibrowana 20000 iteracji, `++[0x20024874]`).
  => **"NN%" = obciazenie procesora panelu (100 - procent bezczynnosci)**. W emulatorze ~37-40% (wartosc zalezy od szybkosci emulacji; na sprzecie wynik rzeczywisty).
- Zamyka to trop "config-gap" `0x200243E4` (19 literalow) z audytu zewnetrznego: to **nie pole ustawien**, tylko zmienna diagnostyczna RAM.
- `0x20021FA0` (39 literalow) = blok ustawien; w handlerach tick czytane `+7` = `0x20021FA7` = **PID 0x0005 "Default settings request"** (u8, 0..1, domyslnie 1, klasa 3); handler cacheuje flage w `this+0x235` i odswieza dziecko `+0x210` przy zmianie (cel wizualny +0x210 NIE zbadany — otwarte).

## Dla testu na prawdziwym kotle
1. Wpisz PIN 0900 (poz.1) i 0999 (poz.2): w naglowku (prawy gorny rog, nad domkiem) **brak** liczby %.
2. Wpisz PIN 6154 (poz.3): na kazdym ekranie poza Home w tym miejscu pojawi sie **liczba z %**, odswiezana co ~sekunde/dwie; zmienia sie sama, bez dotyku.
3. Poza tym L2 i L3 sa (wg emulacji) wizualnie takie same na 141 sprawdzonych ekranach (przy wartosciach domyslnych) — UWAGA: nie sprawdzono ekranow nieosiagnietych (patrz nizej) ani zachowania przy realnych danych z CAN.

## Pokrycie 17 wrapperow
Trafione na L3: 11 z 17 (tabela: `data/level3_gate_wrappers_17.csv`). Nietrafione: 0x0805A9EC, 0x0805B1D4, 0x0805F400, 0x0805FE9C, 0x0806125C, 0x08061518 — ekrany nieosiagniete w eksploracji (Kaskada, Dod. magazyn, inne konteksty). Te same bramki, ten sam efekt (kopie tego samego kodu naglowka) — nie sprawdzone dynamicznie.
Narzedzia: `tools/gate_trace.py` (trafienia wrapperow), `tools/header_cpu_probe.py` (skan instancji + sledzenie zapisu bufora i snprintf).

## Uzupelnienie (PASS 52)
Trafione na L3 (dodatkowo): **Kaskada** -> wrapper 0x08061518 (12B=8), **Magazyn paliwa** -> 0x0806125C (12B=9). Lacznie 13 z 17. Nietrafione: 0x0805A9EC (12A=2), 0x0805B1D4 (12A=4), 0x0805F400 (12A=5), 0x0805FE9C — ekrany o kontekscie 12A=4/5 nieosiagniete (do zbadania). Efekt bramki identyczny (kopie kodu naglowka).
