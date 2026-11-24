# AUTONOMOUS-RUNTIME-PREFLIGHT-UPDATE-2026-11-24

## Firmware received

The canonical firmware was supplied to the runtime as `FW2213TK_kopia.bin`.

Verified locally:

- size: 2,031,616 bytes (0x1F0000)
- SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071`

This exactly matches the canonical firmware hash used throughout the project.

## Runtime blocker after firmware arrival

The firmware is now available, but the execution environment still lacks the mandatory emulator dependencies:

- Python `unicorn`: NOT INSTALLED
- Python `capstone`: NOT INSTALLED

An installation attempt with pip was made and failed because this runtime has no usable DNS/network access to PyPI.

No substitute emulator was introduced.

## Repository cross-check

The repository already contains the established system emulator path:

- `tools/cortexm_rtos.py` — full Cortex-M/FreeRTOS execution model
- `tools/stm32_dma2d.py`
- `tools/stm32_can.py`
- `tools/stm32_rtc.py`
- `tools/ui_session.py`
- `tools/ui_explore.py`

The project documentation states that the system emulator executes the real firmware and has previously produced HARD dynamic results from this exact firmware hash.

## Current state

Firmware: READY

Runtime dependencies: BLOCKED

Dynamic execution in this runtime: NOT RUN

FACT-DYNAMIC produced in this update: NONE

Do not mark the runtime dynamic test complete until Unicorn/Capstone are actually importable and the firmware has been executed in the established emulator.
