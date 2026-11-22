# Runtime RE Harness

## Cel

Zamienić emulator z prostego uruchamiacza firmware w narzedzie produkujace
dowody dla reverse engineeringu.

### Rejestrowane dowody

- kazdy zapis do krytycznych adresow RAM,
- PC/caller dla zapisu,
- indirect call + obiekt + offset,
- lancuch CAN RX -> parser -> parameter engine,
- lancuch parameter/UI -> TX,
- snapshoty RAM przed/po operacji.

### Pierwsze cele

| Target | Cel |
|---|---|
| 0x20008D60 | pierwszy producent obiektu/tabeli |
| 0x2002466C | obiekt pollera |
| 0x20024680 | [object+0x14] |
| 0x200114C0 | node 4 |
| 0x200244EC | TX queue boundary |

## Zasada

Harness nie nadaje znaczenia nieudowodnionym zdarzeniom. Najpierw zapisuje
obserwacje, potem buduje relacje. Hipoteza jest oznaczana osobno.

## Adapter emulatora

Docelowy adapter ARM ma wywolywac WatchpointSet.record_write dla kazdego store,
TraceLog.add dla call/return/BLX oraz eventy CAN_RX/CAN_TX na granicach kontrolera.

Jeden replay ma dostarczyc material do D60 source, vtable graph, parameter graph
i CAN graph.
