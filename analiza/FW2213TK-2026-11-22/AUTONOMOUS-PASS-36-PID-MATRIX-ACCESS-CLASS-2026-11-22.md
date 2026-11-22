# AUTONOMOUS PASS 36 — MACIERZ PID I KLASA DOSTĘPU (SIDECAR +0x24) — 2026-11-22

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Dane: `data/pid_matrix_655.csv` (generator `tools/pid_matrix.py`), wejście z PASS 35.

## HARD — klasa sidecar = tryb dostępu parametru
Bajt klasy rekordu (mój offset +0x24; w PASS 5 „R(i)+0x2C”) przyjmuje 0..3. Dla 448 PID z katalogu panelu **klasa == kolumna `access` katalogu w 448/448 przypadków**;
dla 197 PID ze snapshotu `dostep` (0=live, 1=komenda, 3=nastawa) zgadza się bez wyjątku. Kod potwierdza bramki: `0x08011812` z kontrolą (`param_5!=0`) przyjmuje klasy 1 i 3 (inaczej status 9),
synchronizacja `0x08011368` obejmuje klasy 2 i 3 (PASS 5).

| klasa | tryb | zapis z kontrolą | sync z centralą | liczba PID (z 655) |
|---|---|---|---|---|
| 0 | live (odczyt) | nie | nie | 208 |
| 1 | komenda | tak | nie | 49 |
| 2 | lustro z centrali | nie | tak | 44 (znaczniki czasu historii alarmów 0x4024.., 0x4038.., `0x404C Alarm next index`, `0x3712 Blower type`, `0x3125/0x3126`) |
| 3 | nastawa | tak | tak | 354 |

(nazwy trybów to etykiety robocze; HARD są bramki kodu i zgodność z `access` katalogu).

## HARD/STRONG — rola key 3 i `0x300B`
- `0x0003 Language` (klasa 3, nastawa) **nie ma klucza UI** w żadnej z tabel rezolwera — class 12 odwołuje się do niego bezpośrednio kluczem 3 (spójne z PASS 33/35).
- `0x300B Stop burning wood` jest klasy **1 (komenda)**, default „brak” (sentinel 5678), bez synchronizacji, klucz UI `0x0068` (tabela 2). Etykieta „Podajnik palnika” / „Wentylator wspomagający” (PASS 19) zależy więc od **stanu komendy w czasie pracy**, a nie od zapisanej konfiguracji sprzętowej.
  Interpretacja „kocioł hybrydowy: wentylator w fazie drewna, podajnik po komendzie stop” jest INFERENCE (nazwy sąsiadów „Start/Stop burning wood”, „Burning type”); wymaga dowodu z wartością w czasie pracy.
  To koryguje wcześniejsze przypuszczenie, że o etykiecie decyduje konfiguracja sprzętu.

## HARD — pokrycie UI
557/655 PID ma klucz UI (tabela 2: 372 rekordy wprost; tabela 1: 49 baz × instancje 1..4). 98 bez klucza UI to głównie rejestry alarmów, statystyki, wartości wewnętrzne oraz `0x0003`.
Rezolwer `FUN_08036FF2` mapuje więc klucz UI → PID → rekord, a klasa rekordu decyduje, czy UI może zapisać (`checked_write`) i czy wartość jest synchronizowana (`synced`).

## Zastosowanie dla implementacji ESP32/HA
Macierz `pid_matrix_655.csv` jest wprost tabelą parametrów dla modułu: PID = indeks w ramkach `0x0604/0x0584`, `type/min/max/default` = walidacja zapisu, `mode` = czy wolno pisać i czy odpytywać.
Uwaga: mapowanie „PID == indeks CAN” zakładamy z `0x08062B22` (ID = Data[4]|Data[5]<<8, HARD w PASS 5/16); nie zweryfikowano dla każdego z 655 na żywym CAN.

## OPEN
1. Wartość `0x300B` w czasie pracy (czy 0/1 zmienia etykietę) — wymaga emulacji zadań UI albo logu CAN.
2. Dlaczego 44 rekordy klasy 2 nie pozwalają na zapis z kontrolą (czy centrala jest jedynym źródłem — INFERENCE).
3. 98 PID bez klucza UI: czy są używane przez inne widgety niż rezolwer (bezpośrednie klucze, jak key 3).
4. Weryfikacja PID == indeks CAN dla wszystkich 655 na żywym busie.
