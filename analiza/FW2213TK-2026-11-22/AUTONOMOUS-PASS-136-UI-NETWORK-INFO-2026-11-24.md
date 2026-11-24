# PASS 136 — UI: SIEĆ + INFORMACJE — 2026-11-24

## Cel
Domknięcie punktu 2 z kolejki Claude'a: ekran **Sieć** oraz ekran **Informacje**. Zakres ograniczony do danych potrzebnych do odtworzenia UI. Nie przypisuję PID-ów bez dowodu.

## FACT — SIEĆ
- Klasa ekranu: vtable **0x808f770**.
- Dostęp: **L1+**.
- Menu: wiersz **17**, pozycja „Sieć”.
- Inwentarz: **17_screen, 133 widgety**, 1 wariant w katalogu widgetów.
- Zawartość jest listą modułów/urządzeń CAN, a nie klasycznym ekranem wartości PID.
- Katalog nazw węzłów: `data/can_node_names.csv`.
- Znane nazwy:
  - 0x05..0x07: SLAVE 1..3
  - 0x08: RADIO GATEWAY
  - 0x40..0x47: CAN IO 0..7
  - 0x50: MODUL LAMBDA
  - 0x51: IO BOARD PRO
  - 0x54..0x55: FLOWMETER 1/2
  - 0x56: CAN IO BIG
  - 0x5A: VIDE GSM
  - 0x5B: VIDE NET WIFI
  - 0x5C: VIDE NET
  - 0x64..0x67: VIDE ROOM 1..4
  - 0x6E..0x75: CAN GATEWAY 0..7
  - 0x78..0x7F: CAN IO MINI 0..7
- Dokumentacja menu odnotowuje, że przy braku partnerów w emulatorze lista ma puste linie.
- PASS 64 niezależnie potwierdza, że moduły CAN IO mają własne obiekty z node ID oraz watchdog/offline state. To jest źródło statusu modułów, ale **nie przypisuję jeszcze konkretnego widgetu SIEĆ do pola offline**.

## FACT — INFORMACJE
- Klasa ekranu: vtable **0x808f638**.
- Menu: wiersz **12**, selector/runtime class 13.
- Inwentarz: **2 warianty**.
- Widok ma:
  - tytuł „INFO”, TypedText 52;
  - „igneoTouch v2.213 TE”, TypedText 82, wildcard „2.213 TE”;
  - „Bio Compact 10kW”, TypedText 492;
  - „videRoom PIN 0”, TypedText 492;
  - „Controller by Estyma (www.estyma.pl)”, TypedText 83.
- Są to dane renderowane w katalogu widgetów; ich finalne źródła PID/danych runtime nie są obecnie dowiedzione.

## OPEN — świadomie nie dopisuję
1. Sieć: dokładne widget→node→status-field oraz sposób kodowania statusu wizualnego.
2. Sieć: ewentualne wersje firmware poszczególnych modułów na tym ekranie, jeśli są pokazywane tylko po wykryciu urządzenia.
3. Info: źródła wildcardów wersji/nazwy kotła/videRoom PIN.
4. Info: ewentualna akcja dotyku, jeśli istnieje poza standardowym nagłówkiem.

## Wniosek dla przyszłego ui_model
Sieć należy modelować jako:
`network.nodes[] = {node_id, name, detected/status}`
z `detected/status` jako źródłem modułu CAN, a nie jako sztucznym PID.

Info jako:
`info.version`, `info.boiler_name`, `info.vide_room_pin`, `info.manufacturer`
z osobnym polem `source/evidence`, ponieważ wartości widoczne na ekranie nie mają jeszcze zamkniętego źródła danych.

## Artefakt
`data/cg_network_info.csv`
