# AUTONOMOUS RUNTIME — PACKAGE ACCEPTANCE + DYNAMIC SMOKE — 2026-11-24

## Cel

Dostarczenie do sandboxa pakietów wymaganych przez istniejący runtime reverse-engineeringu bez używania prywatnych zasobów użytkownika.

## Dostarczone artefakty

### Unicorn
- plik: unicorn-2.1.4-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
- SHA-256: 9d6e6dea140560de4ebd8446661f7ef84a357d428c14a3ef09dacd306ec8c239
- rozmiar: 16,436,886 B
- instalacja offline: OK
- import: OK
- wersja importu: 2.1.4

### Capstone
- plik: capstone-5.0.9-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
- SHA-256: 273fd8d747d2e35c88f91450be51a603ecfaafb00d96d9f315dcb8689c86193e
- rozmiar: 1,485,316 B
- instalacja offline: OK
- dystrybucja: 5.0.9
- import działa; moduł zgłasza capstone.__version__=5.0.7, co zostało odnotowane jako rozbieżność metadanych pakietu/modułu.

## Smoke tests

1. Unicorn ARM Thumb:
   - mapowanie pamięci
   - wykonanie MOVS + BX LR
   - wynik R0=1
   - PASS

2. Capstone ARM Thumb:
   - dekodowanie MOVS/BX
   - PASS

## Dynamiczny runtime firmware

Firmware:
- FW2213TK_kopia.bin
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071
- 2,031,616 B

Uruchomiono repozytoryjny rdzeń emulatora Cortex-M/FreeRTOS po dostarczeniu Unicorn:
- Board init: PASS
- SVC: 1
- SysTick: 53 po pierwszym przebiegu
- PendSV: 14
- exception returns: 67
- aktywne zadanie: IDLE
- fault: brak

Dodatkowo uruchomiono dynamiczny test modelu CAN2:
- inject CAN ID 0x584, payload 42 01 00 01 78 56 34 12
- IRQ CAN2 RX0: dostarczony (irq=64)
- po 100 kolejnych slice'ach:
  - irq: 1
  - SysTick: 120
  - PendSV: 24
  - returns: 145
  - aktywne zadanie: EstymaTas
  - fault: brak
  - TX: brak w tym konkretnym scenariuszu

## Status

Najważniejsza blokada z raportów preflight została usunięta bez dostępu do prywatnego komputera/serwera użytkownika.

Następny krok:
- uruchomienie pełnego zestawu modeli peryferiów repo (DMA2D, I2C/FT5x06, RTC, LTDC/render)
- boot -> framebuffer -> TAP -> diff
- następnie wieloprzebiegowa eksploracja UI i CAN.

UWAGA:
Ten raport nie oznacza jeszcze pełnego FACT-DYNAMIC dla UI. Powyższe wyniki dynamiczne dotyczą smoke/boot/core scheduler oraz dostarczenia IRQ CAN; pełny UI dynamiczny zostanie oznaczony dopiero po przejściu przez istniejący pełny pipeline UI.
