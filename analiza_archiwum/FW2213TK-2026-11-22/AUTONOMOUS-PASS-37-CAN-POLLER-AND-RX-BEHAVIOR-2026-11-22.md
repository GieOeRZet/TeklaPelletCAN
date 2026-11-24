# AUTONOMOUS PASS 37 — SEKWENCJA ODCZYTU 0x0604 I ZACHOWANIE RX 0x0584 (WYKONANE W KODZIE FIRMWARE) — 2026-11-22

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Metoda: po emulacji startupu (PASS 35) wywołano **funkcje firmware bezpośrednio** w emulatorze
(function-level harness: LR = adres wartownika, `emu_start` do wartownika). Adresy w nawiasach: PROJECT (RUNTIME = +0x10000).
Narzędzia: `tools/poller_trace.py`, `tools/can_rx_inject.py` (z asercjami). Dane: `data/poll_sequence_655.csv`.

## HARD — bajty ramki odczytu na szynie
Poller `FUN_080629FC` (obiekt `0x2002466C`) → `FUN_08062AE4` → adapter TX `FUN_0806E59C` → prymityw kolejki `0x08057224`. Przechwycony 20-bajtowy rekord przekazany do kolejki:
`04 06 00 00 | 00 00 00 00 | 00 00 08 | 40 PL PH 01 00 00 00 00` czyli **StdId `0x0604`, DLC 8, Data = `40 idx_lo idx_hi 01 00 00 00 00`**
(rekord: +0 StdId u32, +8 IDE, +9 RTR, +0xA DLC, +0xB..+0x12 Data[0..7]). Przykład: Language → `0x604: 40 03 00 01 00 00 00 00`.
**Korekta zapisu w dokumentach:** „Data[3]=0x40, Data[4..5]=indeks, Data[6]=1” dotyczy wewnętrznej struktury kompaktowej `{u16 StdId; u8 DLC; u8 Data[8]}` (offsety +3..+6), a nie numeracji bajtów na szynie.
Na szynie: **Data[0]=komenda, Data[1..2]=indeks LE, Data[3]=subindeks (1), Data[4..7]=wartość LE.**

## STRONG — struktura zgodna z CANopen SDO (expedited)
COB-ID `0x600+4` (żądanie) i `0x580+4` (odpowiedź) przy node ID 4 (HARD z PASS 9), komendy `0x40` żądanie odczytu, `0x42` odpowiedź z wartością 4-bajtową, `0x20` zapis, `0x60` potwierdzenie, `0x80` błąd,
indeks 16-bit LE, subindeks 1 — odpowiada ramkom SDO wg CiA 301. Ograniczenie: nie sprawdzono stanu maszyny (segmentacja, abort codes, timeouty) ani obiektów 0x1xxx; traktować jako „SDO-podobny protokół z indeksami = PID”,
dopóki nie ma dowodu pełnej zgodności.

## HARD — sekwencja odpytywania
Poller (po ustawieniu `+0x08=1` i `+0x10=1` w obiekcie) wysyła **jedno żądanie na wywołanie**, w kolejności slotów tabeli runtime (manager `0x20008D84`, `obj+0x18`),
i kończy po **655 żądaniach — każdy PID z tabeli dokładnie raz** (klasy 0/1/2/3 bez filtra: 354+208+49+44). Pierwsze: `0x3500, 0x3502, 0x350B, 0x0003, 0x0004, 0x215F…`; ostatnie: `0x3728, 0x0005`.
Pełna lista: `data/poll_sequence_655.csv` (order, pid, name, can_id, dlc, data). Pole `+0x0C` ustawiane na 10 po starcie cyklu działa jak okno oczekiwania na odpowiedź (kolejne kroki w kodzie `0x08072A4E..`).
Uwaga: `+0x08/+0x10` ustawia harness; producent tych pól w prawdziwym runtime OPEN, podobnie jak okres wywołań pollera.

## HARD (zachowanie wykonane w firmware) — przyjmowanie odpowiedzi 0x0584
Handler `FUN_08062A90` → `0x08062B22` → `0x08011812` wywołany na wstrzykniętych ramkach (`tools/can_rx_inject.py`, 13 asercji):
- `0x584`, cmd `0x42`, subindeks 1 → wartość zapisana w storage rekordu (np. Language `0→5`, Main module type `0→1`).
- **Walidacja zakresu min/max z rekordu na RX**: Language 200 i 31 (max 30) odrzucone, 30 przyjęte; Main module type 7 (max 1) odrzucone;
  s16 `0x2016` (−100..1500): −50 przyjęte, −200 odrzucone, 1500 przyjęte, 1501 odrzucone — **także dla klasy live (0)**.
- Ignorowane: cmd `0x60`, subindeks ≠ 1, StdId `0x585`.
To jest wprost zachowanie, które musi odtworzyć implementacja modułu (przyjmuj odpowiedź tylko z poprawnym ID/cmd/subindeksem i w granicach z deskryptora).

## Implikacje dla ESP32-C6
1. Klient odczytu: dla każdego PID wysłać `0x604: 40 idx 01 ..`; odpowiedź `0x584: 42 idx 01 val32`.
2. Odpowiedzi mają trafiać do magazynu z walidacją min/max z deskryptora (`pid_matrix_655.csv`), bez dodatkowej polityki zapisu dla klasy.
3. Lista 655 PID i ich kolejność jest znana (poll_sequence); częstotliwość/pacing jest OPEN.

## OPEN
1. Okres wywołań pollera i producent `+0x08/+0x10`; zachowanie przy braku odpowiedzi (timeout, `+0x0C`).
2. Czy zapis lokalny (komenda `0x20`) i odpowiedź `0x60` działają jak w SDO — nie wykonano w tym passie (publikacja `0x0584 0x42` z PASS 20 bez zmian).
3. Pełna zgodność z CiA 301 (segmentacja, abort codes) — nie badano.
4. Wpływ klasy (0..3) na ścieżkę RX: tu wszystkie przyjęte równo; różnice dotyczą zapisu lokalnego z UI.
