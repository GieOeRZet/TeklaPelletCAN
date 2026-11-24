# NewEstymaCan — autonomous progress update — 2026-11-22

## Cel
Odtworzenie zachowania firmware Estyma/Igneo Touch możliwie 1:1 na ESP32 + CAN. RAW firmware pozostaje źródłem prawdy.

## Stan na 2026-11-22

### CAN TX — ~85% zamknięte
Potwierdzone:
- CanTxTask: 0x080654A8
- hardware TX: 0x08061734
- CAN2: 0x40006800
- kolejka TX: 0x200244EC, 100 x 20 B
- adapter TX: 0x0806E59C
- gate: 0x2002466C
- producent: 0x08062AE4
- ramka produkowana przez producenta ma StdId 0x0604
- obiekt pośredni: 0x20008D60
- wywołanie ma charakter virtual dispatch
- brak bezpośrednich BL do 0x0806E59C nie jest już traktowany jako dowód, że funkcja jest martwa.

Pozostaje:
- definitywne potwierdzenie runtime vptr obiektu 0x20008D60 i tym samym krawędzi virtual dispatch -> 0x0806E59C.

### CAN RX / parametr engine — ~90%
Potwierdzone:
- CAN2 RX -> 0x080617DC -> ReceivedCanMessages -> CanRxTask
- dispatcher -> 12 rodzin handlerów
- parametr engine i resolver
- zapis parametrów przez 0x08011812
- 0x08011812 nie jest ukrytym CAN TX.

Pozostaje:
- pełna macierz parametr <-> CAN oraz komplet producentów TX dla wszystkich klas zapisu.

### UI / zasoby — ~55%
Potwierdzone:
- 188 rekordów zasobów/bitmap
- renderer RGB565 + A8
- TypedText
- widget records
- centralny dispatcher zasobów
- duża część ścieżki parameter -> widget -> refresh
- CO1..CO4 instance-aware machinery.

Pozostaje:
- pełne mapowanie resource -> widget -> bitmap/TypedText/callback
- kompletna nawigacja
- pełne runtime instance semantics.

### MenuTree / capability — ~60%
Potwierdzone:
- 21 rekordów MenuTree
- kolejność i selektory pierwszych 15
- access gate
- capability/visibility resolver
- 0x2105 i część selectorów
- część konstrukcji klas/child state.

Pozostaje:
- pełne połączenie touch -> callback -> selector -> navigation
- semantyka wszystkich pól runtime.

### Home screen — ~95% dla samego Home
Potwierdzone główne elementy, bitmapy, hopper, alarm, fill level, readings, zegar/data, WiFi, Summer/Winter itd.
Nie oznacza to 95% całego firmware.

### Graph engine — ~70%
Mechanizm rodzin wykresów i identyfikatory parametrów są dobrze ustalone.
Pozostaje pełne gating/visibility/consumer/write semantics.

## Ogólny szacunek
Nie jest to formalna metryka matematyczna; procent oznacza udział funkcjonalnej architektury, dla której mamy wystarczające dowody RAW do implementacji bez zgadywania.

**Cały projekt reverse-engineeringu 1:1: ~65%**

Orientacyjnie:
- transport CAN: ~85%
- parametr engine / CAN RX: ~90%
- UI/resources: ~55%
- MenuTree/capability: ~60%
- Home: ~95%
- Graphs: ~70%

Największy brak nie leży już w podstawowym transporcie CAN, tylko w pełnym modelu UI/runtime oraz w zamknięciu wszystkich producentów zapisu CAN.

## Zasada dalszej pracy
Nie wykonywać kolejnych globalnych skanów, jeżeli nie zamykają konkretnej otwartej krawędzi grafu. Każdy kolejny pass ma kończyć się:
1. nowym HARD/STRONG findingiem,
2. zamknięciem konkretnej krawędzi,
3. albo jednoznacznym odrzuceniem hipotezy.

## Ostatni konkretny postęp
Pass 03 potwierdził startup/global-object constructor context:
- startup base r8 = 0x20008CD0
- r5 = 0x20008D60
- gate+0x14 otrzymuje 0x20008D60
- kandydat vtable runtime = 0x080A4544
- pozostaje odzyskanie rzeczywistego vptr obiektu 0x20008D60 z IAR .data initialization/object construction.
