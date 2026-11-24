# TEKLAPELLET-CAN — ETAP 23 — RAPORT WYKONANIA
**Data:** 2026-11-21  
**Repozytorium:** GieOeRZet/TeklaPelletCAN  
**Branch:** ccr-be8a1bcb-5t76j0  
**Firmware:** FW2213TK_kopia.bin  
**Rozmiar:** 0x1F0000 = 2,031,616 B  
**SHA-256:** 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 1. Zakres
Wykonano dostarczony skrypt Etapu 23 bez zmiany jego zakresu, bezpośrednio na fizycznym BIN-ie. Wygenerowano ETAP23_RAW_DUMP.zip zawierający dokładnie trzy wymagane pliki:
- param_tx_engine_08011160_08011560.txt
- init_0800FF44_and_080100D0_080104B0.txt
- can_blx_targets_080635E0_08063E10.txt

## 2. Integralność firmware
- rozmiar: 2,031,616 B / 0x1F0000
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
- wynik: zgodny ze specyfikacją Etapu 23.

## 3. Narzędzie disassembly
W środowisku obecny był llvm-objdump, natomiast import capstone nie był dostępny. Wywołanie llvm-objdump w dostarczonym skrypcie nie zwróciło poprawnego wyjścia dla zastosowanego trybu binary/Thumb, dlatego skrypt zgodnie z przewidzianą logiką przeszedł do **RAW HEX FALLBACK + własnego dekodera BL/literałów**.

To istotne: wynik nie jest podpisywany jako pełny disassembly Capstone/objdump. Surowe okna i dekodowane BL są zachowane dokładnie w artefaktach.

## 4. Wyniki P1 — PARAM TX ENGINE
Plik: `param_tx_engine_08011160_08011560.txt`

Zakres disassembly/raw: 0x08011160..0x08011560 (0x400 B).

Wykonano pełny skan BIN-u pod kątem bezpośrednich BL do 0x08011100..0x08011560.

Wygenerowany plik zawiera 453 wpisy BL znalezione przez dekoder w tym skanie.

Literal pool: 0x080119E0..0x08011B00.

## 5. Wyniki P2 — INIT / 0x200114C0 / odpowiedź
Plik: `init_0800FF44_and_080100D0_080104B0.txt`

Wygenerowano trzy wymagane okna:
- 0x08000D40..0x08000E20
- 0x0800FF40..0x0800FF60
- 0x080100C0..0x080104B0

W sumie plik zawiera 25 dekodowanych BL w zadanych oknach.

Ponieważ fallback był użyty dla disassembly, zachowano pełny RAW HEX oraz osobną listę BL.

## 6. Wyniki P3 — CAN / BLX / MOVW
Plik: `can_blx_targets_080635E0_08063E10.txt`

Okna:
- 0x080635E0..0x080636A0
- 0x08063D40..0x08063E10

Znaleziono 6 dekodowanych BL w tych oknach.

Pełny skan BIN-u dla MOVW z wartościami 0x0580 / 0x0584 / 0x0600 / 0x0604 dał 5 trafień:
- 0x0801118A: MOVW r8, #0x0584
- 0x08011312: MOVW r2, #0x0584
- 0x08062AB4: MOVW r1, #0x0584
- 0x08062B0C: MOVW r0, #0x0604
- 0x0806E5F2: MOVW r1, #0x0604

## 7. Ważna uwaga interpretacyjna
Sam artefakt Etapu 23 jest RAW/DUMP-em. Nie zamykam na jego podstawie semantyki BLX ani nie utożsamiam automatycznie każdego pośredniego wywołania z TX CAN.

Najważniejsze potwierdzone dane z tego przebiegu to:
- istnieją dwa miejsca w silniku parametrów związane z wartością 0x0584,
- pełny BIN zawiera konkretne MOVW 0x0584/0x0604 wskazane powyżej,
- okna inicjalizacji i odpowiedzi zostały zabezpieczone,
- dalsze rozwiązanie vtable/object -> BLX target pozostaje zadaniem analitycznym.

## 8. Status
[NEW-HARD] Etap 23 wykonany zgodnie ze skryptem.
[CONFIRMED-REPEAT] SHA firmware zgodny.
[NEW-HARD] ETAP23_RAW_DUMP.zip zawiera dokładnie 3 wymagane pliki.
[NEW-HARD] 453 bezpośrednie BL trafiające do zakresu 0x08011100..0x08011560.
[NEW-HARD] 25 BL w trzech oknach P2.
[NEW-HARD] 5 trafień MOVW dla 0x0580/0x0584/0x0600/0x0604.
[OPEN] Semantyka pośrednich BLX i ich konkretne targety vtable.
[OPEN] Pełna ścieżka UI parameter write -> CAN TX.

## 9. Artefakt lokalny
`ETAP23_RAW_DUMP.zip` — 6,334 B, dokładnie trzy pliki wynikowe.

## 10. Następny priorytet
Najwyższa wartość analityczna: połączyć wyniki P1/P2/P3 z istniejącymi vtable/objectami i rozwiązać konkretne targety BLX, szczególnie punkty związane z 0x0584/0x580 oraz mostem zmiana parametru -> CAN TX.
