# ChatGPT SIEĆ / INFO / INTERNET — etap 1: odbiór zadania i audyt narzędzi

Data: 2026-11-24
Właściciel: ChatGPT
Branch: ccr-be8a1bcb-5t76j0-chatgpt-sii
Baza zadania: 0934933b8db218fc4a84493133ef3f88c9ee71ea
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071

## Co zostało sprawdzone

- `NewEstyma/METODYKA_EMULATOR.md` — przyjęta jako obowiązujący standard.
- `NewEstyma/AUDIT_SIEC_INFO_INTERNET_2026-11-24.md` — odczytany; zawiera wcześniejszy audyt Claude'a i rozdziela wyniki MEASURED od OPEN.
- `tools/sii_acceptance.py` — obecna wersja ma już poprawione: checkpointy 10/17/18, diff ciała, przebieg kontrolny, TX przed akcją, sprawdzenie stored.
- `tools/sii_editor_probe.py` — istnieje pomiar rzeczywistego edytora i zapisu pierwszego znaku.
- `tools/audit_siec.py` — istnieje przebieg SIEĆ dla 0x56, 0x57, 0x5B, 0x45 i UNKNOWN oraz timeout.
- Istnieją zapisane artefakty `sii_acceptance/*/RUN_SUMMARY.json` i PNG z wcześniejszego przebiegu.

## Istotna reguła

Artefakt lub wcześniejszy raport nie jest przez ChatGPT automatycznie uznawany za nowy FACT-DYNAMIC. Audyt cudzego wyniku wymaga ponownego uruchomienia testu na firmware + własnego testu kontrolnego zgodnie z pkt 8 metodyki.

## Co dodałem

`tools/strict_sii_acceptance.py` — zaostrzony runner:
- wymaga BEFORE -> CONTROL -> ACTION -> AFTER,
- diff tylko ciała y>=46,
- mierzy TX od punktu bezpośrednio przed akcją,
- sprawdza `stored`,
- wymaga powtórzenia,
- dla edytora nie dopuszcza docelowo koordynatów ze screenshotu; próbuje znaleźć element przez obiekty UI w RAM,
- zapisuje wynik jako dane.

## Stan wykonania

**Nie oznaczam jeszcze żadnego nowego wyniku jako FACT-DYNAMIC.**

W aktualnym sandboxie jest kanoniczny firmware i zainstalowane wheel'e Unicorn/Capstone, ale nie ma lokalnego checkoutu repo z kompletem `tools/`/punktów kontrolnych; lokalny dostęp sieciowy do GitHub jest zablokowany DNS/połączeniem. Samo posiadanie plików w GitHub nie pozwala uruchomić ich na lokalnej binarce. Dlatego nie będę udawał wykonania testów.

## Następny krok

Po uzyskaniu lokalnego checkoutu/narzędzi (bez umieszczania firmware w repo) uruchomić:
```
python3 -I tools/ui_prepare_cfg.py FW2213TK_kopia.bin /tmp/L1 1
python3 -I tools/strict_sii_acceptance.py FW2213TK_kopia.bin /tmp/L1 analiza/.../sii_strict all
```

Następnie osobno przejść edytor INTERNET, bo sama obecność overlayu nie zamyka kasowania, wieloznakowego zapisu, pełnych zestawów znaków, anulowania i trwałości.

**Status: IN PROGRESS / dynamic execution blocked in this runtime; no false FACT-DYNAMIC claims.**
