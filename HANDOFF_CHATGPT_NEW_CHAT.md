# CHATGPT NEW CHAT HANDOFF — TeklaPelletCAN / NewEstymaCan

## Cel projektu
Możliwie pełne odtworzenie Estyma 1:1 jako uniwersalnej implementacji, nie rozwiązania jednorazowego. Zakres obejmuje firmware, Cortex-M/FreeRTOS, peryferia STM32, UI/framebuffer, CAN i późniejszą integrację Home Assistant.

## Zasady pracy
1. Działać autonomicznie i wykonywać tyle przebiegów/testów, ile potrzeba do realnego postępu; nie zatrzymywać się po arbitralnych 20/100 przebiegach.
2. Jeśli potrzebne jest nowe narzędzie, skaner lub poprawa istniejącego — stworzyć/poprawić automatycznie.
3. Nie prosić użytkownika o uruchamianie Dockera, udostępnianie prywatnego serwera ani zasobów, jeśli zadanie można wykonać w środowisku ChatGPT.
4. Wyniki dynamiczne oznaczać jako FACT-DYNAMIC tylko wtedy, gdy rzeczywiście zostały wykonane w runtime. Nigdy nie zastępować dynamicznego testu wnioskiem ze statycznej analizy.
5. Static / inferred / dynamic rozdzielać jasno.
6. Aktualizować dokumentację i repozytorium wraz z istotnym postępem.
7. Przy zmianie chatu zachować ten dokument jako punkt startowy i nie wymagać od użytkownika ponownego tłumaczenia projektu.

## Canonical firmware
- Plik: FW2213TK_kopia.bin
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071
- Size: 0x1F0000 = 2,031,616 B
- Firmware nie jest przechowywany w repo; użytkownik może dostarczyć go jako upload.

## Repo
GitHub: GieOeRZet/TeklaPelletCAN
Robocza gałąź ChatGPT: ccr-be8a1bcb-5t76j0-chatgpt (jeśli dostępna); aktualny kontekst może używać ccr-be8a1bcb-5t76j0.
Nie zakładać, że każdy wynik istnieje w main — sprawdzać aktualną gałąź.

## Ustalony runtime
Istniejące narzędzia obejmują m.in.:
- tools/cortexm_rtos.py
- tools/stm32_dma2d.py
- tools/stm32_can.py
- tools/stm32_rtc.py
- tools/ui_session.py
- tools/ui_explore.py
- oraz inne probe/render tools.

Docelowy pipeline:
real firmware → istniejący emulator Cortex-M/FreeRTOS → boot → UI session → framebuffer snapshot → real TAP/input → BEFORE/AFTER snapshot + diff → wieloprzebiegowa eksploracja UI i CAN.

NIE zastępować tego prostym, fikcyjnym emulatorem.

## Aktualny stan runtime — 2026-11-24
Użytkownik dostarczył:
- unicorn-2.1.4-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
- capstone-5.0.9-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

Pakiety zostały zainstalowane offline w sandboxie i przeszły smoke testy:
- Unicorn import/version 2.1.4 — PASS
- ARM Thumb execution — PASS
- Capstone import/disassembly — PASS
- Uwaga: dystrybucja Capstone 5.0.9 zgłaszała w module __version__=5.0.7; traktować jako rozbieżność metadanych, nie jako blokadę.

Zweryfikowano firmware SHA-256 — PASS.

Dynamiczny smoke runtime:
- Board init — PASS
- SVC: 1
- SysTick: 53 po pierwszym przebiegu
- PendSV: 14
- exception returns: 67
- active task: IDLE
- fault: brak

Dynamiczny CAN2 smoke:
- injected CAN ID 0x584
- payload: 42 01 00 01 78 56 34 12
- CAN2 RX0 IRQ delivered, irq=64
- po 100 kolejnych slice:
  - irq=1
  - SysTick=120
  - PendSV=24
  - returns=145
  - active task=EstymaTas
  - fault=brak
  - TX=brak w tym scenariuszu

To są rzeczywiście wykonane testy dynamiczne, ale NIE oznaczają jeszcze pełnego dynamicznego odtworzenia UI.

Raport został zapisany w:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-RUNTIME-PACKAGE-ACCEPTANCE-2026-11-24.md
Commit: e338b343f100475ac71bea490de245c0969c6ce5

Wcześniejszy preflight:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-RUNTIME-PREFLIGHT-UPDATE-2026-11-24.md
Commit: 2eb4988708e86c1e8af7d7349fc2ed991fc55ac5

## Co robić dalej
Nie wracać do problemu instalacji Unicorn/Capstone — blokada została usunięta.

Następny priorytet:
1. uruchomić pełny zestaw modeli peryferiów repo:
   - DMA2D
   - I2C / FT5x06
   - RTC
   - LTDC / framebuffer / rendering
2. doprowadzić firmware do pierwszego wiarygodnego framebuffer snapshot.
3. uruchomić realny TAP/input.
4. wykonać BEFORE/AFTER framebuffer diff.
5. zautomatyzować wiele przebiegów eksploracji UI.
6. równolegle rozszerzać dynamiczne testy CAN i korelować je z zachowaniem UI.
7. dokumentować nowe FACT-DYNAMIC, FACT-STATIC i INFERENCE.
8. po możliwie pełnym reverse engineeringu przejść do uniwersalnej implementacji oraz późniejszej karty/integracji Home Assistant.

## Ważne
Jeśli środowisko ChatGPT nie ma konkretnej biblioteki, najpierw szukać sposobu dostarczenia artefaktu do sandboxa (np. upload użytkownika, dostępny artefakt/release), zamiast żądać dostępu do prywatnych zasobów użytkownika. Użytkownik może dostarczyć brakujące wheel'e jako załączniki.

Nie twierdzić, że dynamiczny test został wykonany, jeśli faktycznie wykonano tylko analizę statyczną.
