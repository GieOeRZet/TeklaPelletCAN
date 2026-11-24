# PASS 86 — presenter offsets

FACT: tools/cg_presenter_offsets.py rozszerza PASS 58 o śledzenie r0=this, kopii przez r4/r5, add/add.w oraz ldr/str [base,#imm].
FACT: adresy są PROJECT; RUNTIME=PROJECT+0x10000; skaner używa RAW=PROJECT-0x08010000.
STRONG: niezależny skan potwierdził m.in. setter 0x08054848 -> +0xA69/+0xA95 oraz rodzinę offsetów setterów ekranowych.
OPEN: pełne rozgałęzione CFG dla wszystkich setterów pozostaje do dalszego automatycznego domknięcia; liniowy zakres 0x180 B może wejść w sąsiedni kod.
