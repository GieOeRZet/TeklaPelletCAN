# Katalog CAŁOŚCI rejestrów Estyma Igneo Touch – stan 2026-10-19 21:40

Plik: `igneo-katalog-calosc.csv` (611 wierszy: węzeł 4 = 593, węzeł 86 = 18). To jedyny katalog – zastępuje `igneo-baza-rejestrow-pelna.csv` i starsze. Zawiera KAŻDY rejestr, który kiedykolwiek odczytaliśmy (skany 0x0000–0xFFFF, katalog 538, odczyty ręczne, SCADA.pdf).

## Kolumny
węzeł, index, sub (zawsze 1 = wartość), nazwa, status, wartość ze skanu, wartość signed, typ (sub 2), min (sub 3), max (sub 4), skala/interpretacja, uwagi, użycie w firmware/karcie, grupa adresowa, „w SCADA.pdf", „do migawki (nieznane)", **wartość z migawki 19.10 21:16**, **zmiana względem skanu**, **opis automatyczny** (dla rejestrów bez nazwy: rodzaj wartości, zakres, sąsiedztwo znanych rejestrów).

## Suby (wszystkie, jak je mamy)
- sub 1 – wartość (wszystkie 593 rejestry).
- sub 2 – typ (skan 0x2000–0x4FFF), sub 3 – minimum, sub 4 – maksimum. Puste pole = sub nie istnieje (rejestr tylko do odczytu lub brak ograniczeń), nie „nie sprawdzone".
- Blok 0x0000–0x0FFF (30 rejestrów): suby 2–4 NIEODCZYTANE – do uzupełnienia (rejestry 0x0003–0x0005, 0x03E9–0x03ED, 0x07D1–0x07E1, 0x0803–0x0809, 0x0BB9–0x0BBB, 0x0FD2–0x0FD7).
- Sub 0 – sprawdzony, kocioł nie zwraca (CANopen: liczba pozycji nie jest używana).

## Liczby (węzeł 4)
POTWIERDZONY 127, PRZYPISANY 8, KANDYDAT 44, NIEZNANY 414. Rozpoznane razem 135 (w SCADA.pdf: 82 rejestry, z czego 76 rozpoznanych).
Nazwane ręcznie 180, pozostałe 413 mają opis automatyczny (kolumna ostatnia).

## Migawka 19.10 21:16 (katalogowa)
Odczytano 427 z 593 rejestrów węzła 4 (katalogowa 538 + blok 0x0003–0x0FD7); 166 brak: rejestry z listy poll firmware nie wchodzą do sensora SDO podczas migawki (np. harmonogramy 0x0803/0x0805/0x0808, 0x07D3/0x07D7). Zmiana względem skanu: 20 rejestrów: 0x2124, 0x2165, 0x2257, 0x2277, 0x2294, 0x2297, 0x22F5, 0x311C, 0x3610, 0x3617, 0x4006, 0x4007, znaczniki czasu 0x402D/0x4040/0x4041, harmonogram kotła 0x220A..0x220F (2097120 → 2097136 = 0x1FFFF0, godz. 4–20).

## Harmonogram kotła – wyjaśnione
0x2209–0x220F czytane z kotła: 0x1FFFF0 (godziny 4–20 = 4:00–21:00) dla wszystkich 7 dni. Skan z 15.10 miał 0x1FFFE0 (5–21) – różnica 1 godz., nowszy odczyt = prawda dziś. Firmware v2.19 (wgrany 21:12) potwierdza surowe bajty F0 FF 1F 00.

## Zakresy (węzeł 4)
Przeskanowane w całości: 0x0000–0xFFFF (sub 1). Puste: 0x1000–0x1FFF, 0x5000–0x6FFF, 0x7000+ poza kilkoma rejestrami.

## Otwarte
1. Antylegionella – rejestru brak.
2. Sloty harmonogramów 0x2127.. (21) i blok 0x0803–0x0809 (7) – nieznane.
3. Suby 2–4 bloku 0x0000–0x0FFF.
4. Migawka tylko NIEZNANYCH (428 + kandydaci) – następny krok, bez znanych.
5. Test wyjść węzła 86.

## Aktualizacja 19.10 22:10 – Test wyjść
- Lista z panelu (po PIN): Pompa CWU, Pompa kotłowa, Pompa solarna, Podajnik (A/OFF/ON); Ruszt (A/CLOSE/OPEN); Wymiennik, Zapalarka, Podajnik palnika, (jeszcze 1 wiersz A/OFF/ON), Magazyn paliwa transporter, Magazyn paliwa podajnik (A/OFF/ON); Dm. i WentWyc (suwak + A/OFF/ON); Pompa CO1..CO4 (A/OFF/ON); Mieszacz CO1..CO4 i Mieszacz powrotu (A/CLOSE/OPEN).
- Zapalarka – tryb = 0x2284: A 256, OFF 257, ON 258 (wszystkie trzy potwierdzone odczytem).
- 0x226D (0..1000) rośnie przy rozpalaniu (0 → 11 → 24): kandydat na jasność płomienia.
- Podajnik = 0x2259, Dmuchawa = 0x2283, Pompa CWU stan = 0x2278.

## Ekran Palnik – ustalenia 19.10 22:12
- jasność = **0x2250** (0..100; 0 zimny, 100 przy płomieniu) – potwierdzone odczytem 100 przy panelu 100.
- moc[%] = 0x4005 (już w firmware). moc[kW] = moc[%] × 0,17 (panel: 44% → 7,5 kW; 47% → 8,0 kW), czyli 17 kW mocy nominalnej – wyliczane, rejestru nie znaleziono.
- spalanie[kg/h]: panel 1,9 / 2,1 przy 7,5 / 8,0 kW (≈ kW ÷ 3,9) – też wyliczane, brak rejestru. 0x22B1 (261) i 0x22E1 (271) są stałe, więc to nie one.
- 0x226D to nie jasność (korekta); rośnie w czasie pracy palnika, nieznany.
- T. palnika = 0x226C (27 °C).

## Ustalenia 19.10 23:40–00:00 (FW v2.20)
- **Antylegionella: rejestr NIEZNANY.** 0x216F było przypisane błędnie (odczyt 256 przy włączonej na panelu, zapis 257 bez efektu) – wycofane w fw v2.21; 0x216F pozostaje nieopisanym rejestrem 256/257. 0x300B i 0x311C to fałszywe tropy.
- **0x2290 Czas rozżarzania [min]**: flaga+bajt, zakres 0–20 (panel: 2→7 = raw 258→263). **0x299A Rozżarzanie paliwo [%]**: zakres 20–100 (20→22 = 276→278).
- **Poziomy menu (PIN)**: 0 użytkownik; 1 = PIN 0900 (klucz 1); 2 = PIN 0999 (klucz 2). Palnik: poziom 0 = korekta powietrza, moc min/max, wartość opałowa, ilość paliwa test; poziom 1 = krzywa dmuchawy, podawanie max, wstępna dawka, próg foto, moce dmuchawy, czasy rozżarzania/wygaszania, rozżarzanie paliwo, lambda, tlen 30/100, liczba czyszczeń, wentylator wspomagający, odstęp czyszczenia, czas pauzy, moc/dmuchawa w pauzie; poziom 2 = bezwładność, czas ruchu rusztu, pod. palnika, okres podajnika, min. obroty. CWU: poziom 0 = komfort/eko/zagrzej teraz/histereza/antylegionella/priorytet; poziom 1 = źródło, zwiększenie temp. źródła, delta pompy, temp. max (rejestry nieznane). Menu główne: poziom 1 dodaje Język, Alarm dźwiękowy, Konfiguracja, Test wyjść, Statystyki, Sieć.
- Moc [kW] = test × podawanie max / okres × wartość opałowa × 0,90 × moc[%]; spalanie [kg/h] = kW / (wartość opałowa × 0,85) – 0,85 empiryczne.
