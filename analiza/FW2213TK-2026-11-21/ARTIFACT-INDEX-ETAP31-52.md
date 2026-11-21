# Artifact index — ETAP31–52

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## RAW packages
ETAP31 through ETAP52 are preserved in the handoff archive. ETAP44 and ETAP45 also have independent/final variants.

## Scope
- ETAP31–32: P0 TX-chain evidence
- ETAP33: P1 RX-family evidence
- ETAP34: P2 frame/parameter windows
- ETAP35: P3 local parameter-write windows
- ETAP36: P4 resource/subtable evidence
- ETAP37: P5 UI-build evidence
- ETAP38: P6 tail windows
- ETAP39–44: OPEN-1 object/initialization/xref investigation
- ETAP45–52: extended RAW windows and xref/context checks around OPEN-1/TX dispatch

## Important
RAW dumps are evidence, not automatically interpreted conclusions. Existing master documents contain the evidence classification and rejected hypotheses.


## OPEN1-P4
- `RAW_PACKET7_OPEN1_P4.txt` — RAW evidence from canonical `FW2213TK_kopia.bin`; confirms vtable `0x080A4568 -> 0x080629FC`, exact `+0x0A := 1` store at `0x08062A86`, CAN2_RX0 path and startup findings; D60 slot-0 target remains OPEN.
- `CONTINUATION-PROMPT-OPEN1-P5.md` — next-agent task focused exclusively on finding the first runtime write to `[0x20008D60]` and proving its slot-0 TX path.

## Source discipline
For current OPEN1 work, the canonical BIN is the evidence source. RE_PACK is not to be used as a byte source; it may only serve as auxiliary address mapping when explicitly useful.


## OPEN1-P5
- `RAW_PACKET8_OPEN1_P5.txt` — pełny lokalny RAW wynik Pass 1 + autonomicznego Pass 2 na canonical BIN. Zawiera dispatcher 0x08063B80, 12 rodzin handlerów / 36 BL, startup 0x0808B4A8 i 0x08089440 oraz pełny parser 0x08062B22.
- P5 potwierdził, że 0x0808B4A8 to FPU enable, nie .data/.bss init. 0x08089440 jest względnym iteratorem wywołań i wymaga osobnego domknięcia formatu/scatter-loading.
- D60 first runtime write nadal OPEN.

**Uwaga:** pełny tekstowy RAW P5 jest przekazany użytkownikowi jako plik wynikowy. GitHubowy katalog `analiza/` pozostaje miejscem prowadzenia kontekstu i indeksu projektu.
