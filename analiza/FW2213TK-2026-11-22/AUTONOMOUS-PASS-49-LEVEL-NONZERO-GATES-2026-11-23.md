# PASS 49 — bramki "poziom != 0" (PIN 0900 vs brak PIN) oraz kody specjalne

## Kody PIN
- `0x08047E74`: 0 -> poziom 0; 900 -> 1; 999 -> 2; 6154 -> 3; inne -> bez zmiany. Tylko te trzy kody ustawiaja poziom.
- **6666 = reset ustawien fabrycznych (potwierdzone przez wlasciciela)**: `0x08028634` (z handlera PIN `0x0804C21C`) ustawia flage `0x20021FA7` = PID 0x0005 "Default settings request". TODO na koniec RE (przed ESP32) w `NewEstyma/00_AGENT_START_HERE.md`. Tabela 23 liczb `0x20008C50` tez ustawia te flage — znaczenie do zbadania.
- Handler PIN zapisuje tez `[0x2002466C+0x10] = (poziom != 0)` (bramka pollera) — do weryfikacji.

## Co dodaje poziom >= 1 (porownanie zrzutow L0 vs L1 + trace funkcji bramek)
Funkcje z bramka `ldrb [model+0x158]; cbz` : `0x0803C294` (menu), `0x08053DDC` (ekran Ogrzewania CO1..4, ctx12A=1), `0x08054AB8` (nie trafiona), `0x08055A8C` (ekran Bufor, ctx12A=1/12B=7). Brak trafien na: Kociol, Palnik, Alarmy, Info, Konfiguracja, Statystyki, Test wyjsc, Siec.
- **Naglowek (kazdy ekran)**: L0 = ikona czlowieka; L>=1 = klucz + cyfra poziomu (bitmapa 94 tylko na L0).
- **Ogrzewanie 1..4 (L>=1)** dochodzi: napis **"Ochrona kotla"** (TypedText 87) w srodku i **"7°C"** w prawym dolnym rogu. Zrzut: `screens/pass49_co1_L0_vs_L1.png`.
- **Bufor (L>=1)** dochodzi: **"0%"** po lewej od zbiornika i **"7°C"** w prawym dolnym rogu. Zrzut: `screens/pass49_bufor_L0_vs_L1.png`.
- "7°C" jest wspolne dla obu ekranow (prawdopodobnie jedna wartosc globalna — nie ustalone, ktora; `set_local` na PID 0x22f5/2166/22ad/2016/4001 jej nie zmienil).
- Nie ustalono zrodla danych "Ochrona kotla" (czy tekst jest warunkowy) ani "0%" (poziom naladowania bufora?).
## Poziom 3 (PASS 48)
- naglowek: dodatkowo "NN%" = obciazenie CPU; zrzut `screens/pass48_header_L3_vs_L2.png`.

## Zrodlo "7°C" na ekranie Ogrzewanie (HARD, sledzenie snprintf + presenter)
- Setter widoku `0x0805454E` (formatuje `%d` do bufora `view+0x1694`, odswieza `+0x165C`) jest wolany z presentera `0x0804D3D0..0x0804D41C` z wartoscia `model_get(0xCB)` (`0x08046FF2`).
- Klucz UI `0x00CB` -> `resolver_t1` -> **PID 0x22F5 "CH needed temp. [C]"** (PID = 0x22F5 + instancja - 1; u16 0..150, domyslnie 5678=brak danych). Czyli "7°C" na ekranie CO = **zadana temperatura obiegu CO** (w emulatorze 7 = wartosc zastepcza).
- Obok presenter czyta klucze 0xAB (CH res [dC] 0x2166), 0xAC (CH program 0x2064), 0xC6 (Room measured temp 0x2016), 0xB0 (Room temp sensor type 0x22A1), 0xA8 (CH status 0x22FD).
- NIEZWERYFIKOWANE: skad warunek napisu "Ochrona kotla" (TypedText 87) — prawdopodobnie zalezy od CH status (0x22FD); "0%" na Buforze i "7°C" na Buforze (inna klasa 0x08055A8C) nie prześledzone.
- `set_local(0x22F5, 31)` nie zmienilo wyswietlanej wartosci (ograniczenie narzedzia: zapis do storage nie odswieza cache modelu) — do wyjasnienia.
