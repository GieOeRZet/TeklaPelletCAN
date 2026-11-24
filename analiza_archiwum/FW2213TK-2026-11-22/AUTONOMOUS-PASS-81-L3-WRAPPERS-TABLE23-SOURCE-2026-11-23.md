# AUTONOMOUS PASS 81 — L>=3 WRAPPERS + TABLE23 SOURCE ARRAY — 2026-11-23

## Cel
Domknąć statycznie rodzinę czterech wrapperów poziomu dostępu >=3 oraz znaleźć rzeczywistą tablicę źródłową dla katalogu 23 wartości Parameters set Number.

## 1. Cztery wrappery L>=3

Wrappery artifact 0x0805A9EC -> RAW 0x4A9EC, 0x0805B1D4 -> RAW 0x4B1D4, 0x0805F400 -> RAW 0x4F400, 0x0805FE9C -> RAW 0x4FE9C mają ten sam szkielet: inicjalizacja widgetów/podobiektów; pobranie modelu przez FUN_080314BA; odczyt [model+0x158]; CMP #3; przy poziomie >=3 dołożenie pola pod [object+0x23C]; następnie inicjalizacja [object+0x210]; zakończenie przez vtable slot 0.

To jest twardy dowód wspólnej bramki L>=3 / CPU-load-header. Nie należy jeszcze przypisywać nazw konkretnych ekranów wyłącznie z tej bramki.

Caller-y: RAW 0x4A9EC z 0x40DD2; RAW 0x4B1D4 z 0x41318; RAW 0x4F400 z 0x4B4CC; RAW 0x4FE9C z 0x4BEAA.

Caller 0x40DD2 należy do obiektu z vtable runtime 0x0808F80C (RAW 0x7F80C). Vtable: slot0 0x08097709, slot1 0, slot2 0x08043A33, slot3 0x08050C4F, slot4 0x080A60EB, slot5 0x08050DF9, slot6 0x08043C73, slot7 0x08043E3B, slot8 0x08043F39, slot9 0x0807EDD5, slot10 0x080A60ED, slot11 0.

Caller 0x41318 należy do obiektu z vtable runtime 0x0808F910 (RAW 0x7F910). Vtable: slot0 0x08079CB5, slot1 0, slot2 0x08043A33, slot3 0x0805119D, slot4 0x080A60EB, slot5 0x0805135D, slot6 0x08043C73, slot7 0x08043E3B, slot8 0x08043F39, slot9 0x0807EE49, slot10 0x080A60ED, slot11 0.

## 2. Tabela 23 — rzeczywista tablica źródłowa

Katalog wskaźników: SRAM 0x20008C50, 23 wpisy po 4 bajty. record+0x08 = Parameters set Number, record+0x0C = zwracana wartość.

Nowe: literal SRAM 0x20008D84 występuje w kilku miejscach. FUN_080143DE traktuje 0x20008D84 jako tablicę rekordów o rozmiarze 0x14 (20) bajtów; index n -> base+n*0x14; używa record+0x04..+0x0C. FUN_08014416 i FUN_0801443E wykonują analogiczne przebiegi, a FUN_0801446C/FUN_08014494 budują/odświeżają katalog 0x20008C50.

Rekord #1 = 0x20008D84. Rekord #23 = 0x20008D84 + 22*0x14 = 0x20008EFC. Rekord #23 kończy się na 0x20008F0F.

To zamyka strukturę: 23 wartości nie są 23 statycznymi słowami w BIN. Są wskaźnikami do 23 rekordów runtime, zbudowanych w SRAM.

OPEN: nie znaleziono jeszcze statycznej wartości initial/default dla record #23 + 0x0C. Wartość musi być ustalona przez śledzenie inicjalizacji tablicy lub dynamiczny dump.

## 3. Status A2

Znaczenie katalogu CLOSED; liczba rekordów CLOSED=23; source array CLOSED=0x14-byte records; adres 23. rekordu CLOSED=0x20008EFC; wartość 23. record+0x0C OPEN.

## 4. Następny cel

1. Cross-reference wszystkich zapisów 0x20008D84..0x20008F0F.
2. Odnaleźć funkcję zasilającą 23 rekordy.
3. Zidentyfikować PID/Parameter Set Number rekordu #23 i jego +0x0C.
4. Zmapować cztery vtable do konkretnych ekranów przez slot0/handler/resource.
5. Domknąć B3: dokładny warunek pola Ochrona kotła oraz zależność od konfiguracji Bufora.