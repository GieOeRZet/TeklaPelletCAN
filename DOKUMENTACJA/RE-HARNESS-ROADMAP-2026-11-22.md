# NewEstyma — RE Harness Roadmap — 2026-11-22

## Zmiana kierunku

Dotychczasowy emulator byl przede wszystkim szkieletem wykonawczym. Priorytetem
staje sie produkcja dowodow runtime.

## Faza 1 — instrumentacja

- [x] strukturalny TraceEvent
- [x] watchpointy krytycznych RAM
- [x] lista celow CAN/object/parameter
- [x] rozdzielenie obserwacji od hipotez
- [ ] adapter dla konkretnego backendu ARM

## Faza 2 — automatyczne closure

- [ ] pierwszy writer 0x20008D60
- [ ] pelny obiekt 0x2002466C
- [ ] [0x2002466C+0x14] -> vptr -> slot0
- [ ] implementacje +0x7178/+0x7180
- [ ] CAN replay matrix
- [ ] snapshot diff -> PID/RAM correlation

## Faza 3 — differential runtime

- [ ] snapshot baseline
- [ ] replay READ/WRITE
- [ ] compare traces
- [ ] export evidence Markdown/JSON
- [ ] feed evidence into software model

## Kryterium sukcesu

Emulator ma po jednym przebiegu dostarczyc slad umozliwiajacy odpowiedz:
kto zapisal, co wywolal, jaki obiekt, jaki PID i jaki CAN.

Closure wymaga sladu lub statycznego dowodu zgodnego z firmware.
