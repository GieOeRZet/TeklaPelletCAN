# DOKUMENTACJA — spis treści

Ten folder zawiera dokumentację uzupełniającą projekt. Dokumenty poniżej mają umożliwić kontynuację pracy bez ponownego odkrywania wcześniejszych ustaleń.

## Gdzie czego szukać

| Temat | Dokument |
|---|---|
| **MASTER REVERSE ENGINEERING — pełny handoff NewEstyma/TeklaPelletCAN do kolejnego chatu/agenta** | [REVERSE_ENGINEERING_MASTER_2026-11-22.md](REVERSE_ENGINEERING_MASTER_2026-11-22.md) — **zacznij tutaj, jeśli kontynuujesz reverse engineering firmware Estyma**. Zawiera stan przez Pass 18, CAN2, node 4, parameter engine, 260-slot catalog, UI/resources, access levels, odrzucone hipotezy, luki i kolejność dalszej pracy. |
| **Rejestry kotła, CANopen, dekompilacja firmware panelu Igneo Touch, metodologia skanowania** | [../rejestry/README.md](../rejestry/README.md) i [../rejestry/REJESTRY.md](../rejestry/REJESTRY.md) |
| Ogólna architektura projektu | [../docs/ARCHITEKTURA.md](../docs/ARCHITEKTURA.md) |
| Firmware | [FIRMWARE.md](FIRMWARE.md) |
| Mapa bitmap panelu | [BITMAPY-PANELU.md](BITMAPY-PANELU.md) |
| Aplikacja Android | [APLIKACJA-ANDROID.md](APLIKACJA-ANDROID.md) |
| Integracja Home Assistant | [INTEGRACJA-HA.md](INTEGRACJA-HA.md) |
| Poziomy dostępu/PIN | [POZIOMY-DOSTEPU-PIN.md](POZIOMY-DOSTEPU-PIN.md) |
| CI i wydania | [CI-I-WYDANIA.md](CI-I-WYDANIA.md) |
| Lista otwartych zadań | [../docs/TODO.md](../docs/TODO.md) |

## Repozytoria projektu

- GieOeRZet/TeklaPelletCAN — źródło rozwojowe
- GieOeRZet/TeklaPelletCAN_HA — integracja HA
- GieOeRZet/TeklaPelletClassic-card — karta Classic
- GieOeRZet/TeklaPelletModern-card — karta Modern
- GieOeRZet/TeklaPelletDroid — Android

Źródłem prawdy dla kodu rozwojowego jest TeklaPelletCAN.

## Aktualne luki RE

- pełne drzewo menu i ekranów podrzędnych,
- zależności menu/podmenu od konfiguracji i access level,
- pełny layout rekordów 0x2C,
- pełny model 0x20008D84,
- resolver → descriptor → getter/setter,
- pełny CAN parameter catalog,
- 12 katalogowych ID bez znalezionego init,
- 512 non-catalog IDs z mechanizmu 0x08014700,
- heartbeat/presence,
- owner watchdog bitu 0x2.

Master handoff nie oznacza zakończenia analizy. Jest punktem wejścia do kolejnych Passów.
