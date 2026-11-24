# AUTONOMOUS-RUNTIME-PREFLIGHT-2026-11-24

## Status

Etap A — diagnostyka runtime wykonana. Dynamiczny test firmware NIE został uruchomiony, ponieważ aktualny runtime nie posiada wymaganych bibliotek emulacji, a kanoniczny firmware nie jest dostępny jako plik w aktywnym środowisku.

## FACT-DYNAMIC

Brak. Nie wykonano boot/tap/snapshot, więc nie przypisuję żadnych wyników emulatorowi.

## FACT-STATIC

- Repozytorium: GieOeRZet/TeklaPelletCAN
- Aktywna gałąź projektu: ccr-be8a1bcb-5t76j0
- Gałąź robocza ChatGPT: ccr-be8a1bcb-5t76j0-chatgpt
- Kanoniczny firmware: FW2213TK_kopia.bin
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071
- Rozmiar: 0x1F0000 = 2,031,616 B
- Dokumentacja repo wyraźnie wskazuje, że firmware nie jest przechowywany w repo i należy dostarczyć go obok narzędzi.
- Istniejące narzędzia dynamiczne obejmują cortexm_rtos.py, ui_session.py, ui_explore.py oraz narzędzia probe/render.

## Runtime

- Python: 3.13.5, x86_64 Linux
- unicorn: BRAK
- capstone: BRAK
- PIL/Pillow: DOSTĘPNE
- numpy: DOSTĘPNE
- lokalny pip cache: brak znalezionych wheel/pakietów unicorn/capstone
- systemowe pakiety python3-unicorn/python3-capstone: brak dostępnych pakietów w lokalnym apt cache
- bezpośredni dostęp sieciowy z runtime do GitHub/PyPI: niedostępny (DNS)
- próba git ls-remote do GitHub zakończyła się błędem DNS

## Ważne ograniczenie

Nie należy zastępować Unicorn/Capstone uproszczonym emulatorem ani deklarować dynamicznego testu na podstawie statycznych artefaktów. Istniejący emulator wymaga rzeczywistego wykonania firmware.

## Następny krok

Po udostępnieniu kanonicznego FW2213TK_kopia.bin w runtime oraz unicorn + capstone należy uruchomić:

1. import/preflight,
2. emu_startup / cortexm_rtos boot,
3. UiSession boot,
4. pierwszy framebuffer snapshot,
5. realny TAP,
6. snapshot BEFORE/AFTER + diff,
7. dopiero potem pełne przebiegi UI.

Do tego czasu status dynamiczny pozostaje OPEN/BLOCKED BY RUNTIME, a nie CLOSED.
