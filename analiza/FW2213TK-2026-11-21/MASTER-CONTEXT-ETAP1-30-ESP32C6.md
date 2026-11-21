# TEKLAPELLET-CAN — MASTER CONTEXT ETAP 1–30
## Dokument startowy do kontynuacji reverse engineeringu

Data: 2026-11-21
Repozytorium: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0
Firmware: FW2213TK_kopia.bin
Rozmiar: 0x1F0000 = 2,031,616 B
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

---

# 0. CEL PROJEKTU

Celem TeklaPelletCAN jest odtworzenie na ESP32-C6 komunikacji z kotłem Estyma przez CAN oraz zbudowanie warstwy Home Assistant możliwie wiernie zachowującej zachowanie oryginalnego sterownika.

Docelowy model:

CAN2 → EstymaCanFrame → RX/TX protocol → parameter engine → resource/UI model → ESP32-C6 → Home Assistant

Obecny materiał jest wystarczający do rozpoczęcia implementacji głównej warstwy CAN/parametrów, ale nie wolno jeszcze twierdzić, że cały protokół urządzenia został rozkodowany 1:1.

# 1. ZASADY DALSZEJ ANALIZY

- Oddzielać FAKT od HIPOTEZY.
- [NEW-HARD] = nowy fakt bezpośrednio potwierdzony w BIN.
- [CONFIRMED-REPEAT] = wcześniej potwierdzony fakt.
- [NEW-STRONG] = bardzo mocna korelacja, ale bez pełnego dowodu semantycznego.
- [OPEN] = nierozwiązane.
- [REJECTED] = wcześniejsza hipoteza odrzucona.
- Nie nadawać semantyki CANopen/SDO tylko dlatego, że występują numery 0x600/0x580.
- Nie uznawać każdego BLX za TX CAN bez rozwiązania targetu.
- Nie zgadywać zawartości regionu 0x20005EF0..0x20005F5B.
- Przy dalszym RE najpierw wykorzystywać istniejące RAW dumpy i callgraphy; nie wykonywać bezcelowego skanu całej binarki.

# 2. INTEGRALNOŚĆ FIRMWARE

Wszystkie etapy wykonywane na fizycznym BIN-ie używały:
- rozmiar: 0x1F0000
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

# 3. WARSTWA CAN2

[CONFIRMED-REPEAT] CAN2 peripheral base: 0x40006800.

RX:
- queue storage: 0x200244BC
- queue handle: 0x200244DC
- producer: 0x0806F9F8 → FUN_080617DC
- consumer: CanRxTask @ 0x0806E94C → FUN_08063B80

TX:
- queue storage: 0x200244E0
- queue handle: 0x200244EC
- queue primitive: 0x08057224
- consumer: CanTxTask @ 0x080654A8
- hardware TX: FUN_08061734(0x40006800, record)

[NEW-HARD] 0x08057224 jest mechanizmem FreeRTOS queue send; nie jest sam w sobie protokołem CAN.

# 4. EstymaCanFrame — 20 BYTE

[NEW-HARD]

| Offset | Rozmiar | Znaczenie |
|---|---:|---|
| +0x00..+0x03 | u32 | StdId |
| +0x04..+0x07 | u32 | ExtId |
| +0x08 | u8 | IDE, raw 0x04 |
| +0x09 | u8 | RTR, raw 0x02 |
| +0x0A | u8 | DLC = RDTR & 0x0F |
| +0x0B..+0x12 | 8 B | Data[0..7] |
| +0x13 | u8 | RX metadata = RDTR >> 8 |

FUN_080617DC czyta CAN2 mailbox registers:
- RIR: base + mailbox*0x10 + 0x1B0
- RDTR: +0x1B4
- RDLR: +0x1B8
- RDHR: +0x1BC

Dla standard ID: StdId = RIR >> 21.
Dla extended ID: ExtId = RIR >> 3.

FUN_08061734 bierze rekord 20 B i zapisuje odpowiednie pola do TIR/TDTR/TDLR/TDHR oraz ustawia TX request.

# 5. GŁÓWNY TOR RX

CAN2 RX → FUN_080617DC → ReceivedCanMessages → CanRxTask → FUN_08063B80 → 12 rodzin handlerów.

Nie wszystkie 12 rodzin zostały jeszcze semantycznie rozkodowane.

# 6. PARAMETER ENGINE

## FUN_08011812

[CONFIRMED-REPEAT]

Funkcja:
- wyszukuje rekord parametru,
- sprawdza typ,
- zapisuje wartość przez record + 0x0C,
- respektuje typy 1..5,
- przy param_5 != 0 wykonuje dodatkową kontrolę stanu,
- przy param_6 == 1 wykonuje dodatkową walidację zakresu.

Przy param_5=1:
- record = base + index*0x2C,
- byte record+0x2C musi być 0x01 albo 0x03,
- inaczej status 0x09.

Przy param_6=1:
- dodatkowa walidacja pól wokół record+0x1C i record+0x14.

[REJECTED] FUN_08011812 nie jest potwierdzonym dirty-bit setterem i sama nie:
- wywołuje 0x0806E59C,
- wywołuje 0x08057224,
- wysyła CAN,
- wykonuje potwierdzonego callbacku TX.

## FUN_08037212

[CONFIRMED-REPEAT] Ma 33 bezpośrednich callerów w blokach UI.

Potwierdzony tor lokalnego zapisu:
UI → FUN_08037212 → FUN_08011812 → parameter record + 0x0C → local RAM.

Pełny most:
UI parameter change → local parameter storage → ? → CAN TX
pozostaje [OPEN].

# 7. TABELA 188 RESOURCE RECORDS

Tabela DAT_0804866C:
- dokładnie 188 rekordów,
- idx 0..187,
- 16 B/rekord,
- raw 0x4866C..0x4921C.

Rozkład typów:
- type 0: 139
- type 1: 31
- type 2: 3
- type 3: 12
- type 4: 1
- type 5: 2

f07:
- 0x00: 148
- 0x01: 40

# 8. TYPEDTEXT

[CONFIRMED-REPEAT]

Poprawiona baza tabeli TypedText:
0x5BE64 = 0x5BD80 + 57*4.

Nie używać starego 0x5BD80.

Etap 30 wygenerował esp32_resources_188.json z dokładnie 188 rekordami oraz rozwiniętymi polami extra dla typów 2/3/5.

# 9. RESOURCE/UI BUILDER

## FUN_080480C0

Potwierdzone:
- korzysta z resource table,
- rekord ma 16 B,
- wyszukuje rekordy po wartościach wejściowych,
- typ rekordu steruje dispatch,
- widget base = param_1 + 0x42C,
- stride widgetów = 0x338,
- używane są pola obiektu około +0x334 i +0x270.

Dispatch:
- type 1 → FUN_0804E598
- type 2 → FUN_0804E740
- type 3 → FUN_0804E75A
- type 5 → FUN_0804E740
- końcowo FUN_0804E5BC(widget,10)

[OPEN] Pełne mapowanie resource → TypedText/Bitmap/callback/widget nie jest jeszcze kompletne.

## FUN_0803E714

Buduje wejście dla stron 1..4 z DAT_0803EEC0 +0x62 oraz opcjonalnie +0x6E, następnie używa FUN_080480C0, FUN_08036FF2 i FUN_0804842C.

Widget base:
+0x42C + N*0x338.

# 10. PROTOKÓŁ 0x0604 / 0x0584

## Obiekt 0x200114C0

[CONFIRMED-REPEAT]

Globalny obiekt: 0x200114C0.
Literal reference: 0x08063D04.
Konstruktor: FUN_0800FF44.

Według dotychczasowego RE konstruktor ustawia:
[obj+0x00] = r1  (adapter TX)
[obj+0x04] = r2  (tablica parametrów)
[obj+0x08] = 4   (Node ID)

[OPEN] Dokładny runtime path ustanawiający [0x200114C0+0] nie został całkowicie odzyskany.

## READ

[NEW-HARD / CONFIRMED-REPEAT]

Poller: 0x080629FC.
Wspólna vtable: 0x08094508.
Slot 8 → 0x080629FC.

Tor:
0x080629FC → table + counter*0x2C + 0x08 → 0x08062AE4 → CAN frame.

Znany format:
- StdId = 0x0604
- DLC = 8
- Data[3] = 0x40
- Data[4..5] = parameter index
- Data[6] = 0x01

W konkretnych analizowanych przypadkach występował indeks 0x2001.

Nie nadawać automatycznie semantyki CANopen bez dodatkowego dowodu.

## TX wrapper 0x0604

FUN_0806E59C:
- buduje lokalny rekord,
- pobiera handle CanMessagesToTransmit z 0x200244EC,
- wysyła przez 0x08057224,
- posiada kontrolę związaną z ID 0x0604.

Literal pool:
0x0806E60C → 0x2002466C
0x0806E610 → 0x200244EC

Wspólna dispatch table:
0x08094508
slot 5 → 0x0806E59C
slot 8 → 0x080629FC

## WRITE / RESPONSE

W analizowanym materiale występują:
- 0x20 — zapis,
- 0x40 — odczyt,
- 0x42 — odpowiedź z wartością,
- 0x60 — potwierdzenie,
- 0x80 — błąd.

W konkretnych ścieżkach:
- request write wykorzystuje 0x0604,
- response/publication wykorzystuje 0x0584,
- analizowany tor obejmuje indeks 0x3004 / subindex 0x01.

Nie traktować tego jako kompletnego katalogu całego protokołu.

# 11. FUN_08062B22 — RX WRITE ENGINE

Potwierdzony tor:

CAN frame → 0x08062AE4 / handler → 0x08062B22 → parameter index z frame+4/+5 → parameter lookup 0x080115F6 → type → FUN_08011812 → record+0x0C.

Typy:
- type 1: 1 B
- type 2: 16-bit
- type 3: 32-bit
- type 4: signed 16-bit
- type 5: 32-bit

# 12. 0x08062A90

Warunki:
- StdId 0x0240..0x0257, albo
- StdId 0x0584.

Dla 0x0584:
- object+0x0C != 0,
- object+0x10 == 1,
- (data[3] >> 5) == 2,
- następnie BL 0x08062B22,
- potem increment object+0x06.

# 13. 12 RODZIN HANDLERÓW RX

Zidentyfikowano:
1. 0x0800E2D2
2. 0x0800DFC6
3. 0x08063E10
4. 0x08063F30
5. 0x0800FEB4
6. 0x0800FF50
7. 0x0800F894
8. 0x0806369E
9. 0x0800F0D0
10. 0x08062A90
11. 0x08063FBA
12. 0x08064008

Znane filtry obejmują m.in.:
- base +0x180/+0x280,
- base +0x380/+0x480,
- base +0x600,
- base +0x584,
- base +0x1EE,
- absolutne 0x0584,
- zakres 0x0701..0x077F,
- zakres 0x0581..0x0600,
- 0x0288,
- StdId 0x0240..0x0257.

Pełna semantyka wszystkich rodzin pozostaje [OPEN].

# 14. 0x0800FF50 — PARAMETER MESSAGE RECEIVER

Potwierdzony schemat:

StdId == object+0x08+0x600
→ (data[3] >> 5) == 1 lub 2
→ parameter index = data[4..5]
→ type = data[6]
→ value = data[7..]
→ FUN_080115F6
→ type lookup
→ FUN_08011812
→ response
→ object 0x200114C0
→ vtable slot 0
→ BLX

Końcowy dispatch:
0x080100BE: add r1,sp,#8
0x080100C0: ldr r0,[r4]
0x080100C2: ldr r2,[r0]
0x080100C4: ldr r2,[r2]
0x080100C6: blx r2

[NEW-HARD] Jest to slot +0x00 vtable obiektu wskazanego przez field +0 obiektu 0x200114C0.

Response jest budowany z bazą object+0x08+0x580 i zawiera m.in. command/status bytes oraz parameter index/type/value/result.

# 15. VTABLE 0x08094508

Potwierdzone istotne sloty:
- slot 5 → 0x0806E59C
- slot 8 → 0x080629FC

Tabela fizyczna: 0x08094508.

# 16. POLLER / OBIEKTY 0x080702DC

Brak bezpośrednich BL/B.W do 0x080629FC.
Wywołanie następuje przez vtable slot 8.

0x0800DCD4 tworzy cztery instancje 0x080702DC:
- 0x200208EC
- 0x200209C4
- 0x20020A9C
- 0x20020B74

Subobiekty +0x30:
- 0x2002091C
- 0x200209F4
- 0x20020AD0
- 0x20020BA4

[NEW-STRONG] Cztery poller-bearing subobjects są tworzone.
[OPEN] Nie udowodniono, że cała klasa 0x080702DC jest wyłącznie managerem CAN.

# 17. OBIEKT 0x2002466C

Literal 0x2002466C występuje dokładnie w:
- 0x080019E0
- 0x0800BAA4
- 0x0803C248
- 0x08063D1C
- 0x0806E60C

Istotne użycia:
- 0x08063D1C → kod w okolicy 0x08063C6C → BL 0x08062A90.
- 0x0806E60C → FUN_0806E59C odczytuje pola +9/+0xA.

[OPEN] Pełne znaczenie i inicjalizacja tego obiektu.

# 18. VTABLE 0x08078578

Potwierdzone sloty:
- +0x00 → 0x080314C2
- +0x04 → 0x08031792
- +0x08 → 0x080317A0
- +0x0C → 0x08031A74
- +0x10 → 0x0806FC7C
- +0x14 → 0x080894D4
- +0x28 → 0x080314D4

Nie utożsamiać tego vtable z 0x08094508.

# 19. ETAPY 21–30 — ARTEFAKTY

Etap 21:
- resource_table_full.csv
- write_callers_raw.txt
- can_handlers_and_vtables.txt
- raw dump 12 handler families.

Etap 22:
ETAP22_RAW_DUMP.zip:
- resource_table_188_clean.csv
- write_and_init_windows.txt
- can_blx_indirect_scan.txt
Wynik BLX: 121 w zadanych zakresach.

Etap 23:
ETAP23_RAW_DUMP.zip:
- param_tx_engine_08011160_08011560.txt
- init_0800FF44_and_080100D0_080104B0.txt
- can_blx_targets_080635E0_08063E10.txt
MOVW:
0x0801118A → 0x0584
0x08011312 → 0x0584
0x08062AB4 → 0x0584
0x08062B0C → 0x0604
0x0806E5F2 → 0x0604

Etap 24:
ETAP24_RAW_DUMP.zip:
- caller_08010F80_08011040_and_init_08000D40.txt
- can_080635B0_080636A0_and_08063D40_08063E10.txt
- resource_188_summary_and_can_ids.csv
21 UI resource-ID candidates.

Etap 25:
ETAP25_RAW_DUMP.zip:
- movw_protocol_constants.txt
- subfuncs_and_init_pool.txt
5 MOVW hits.

Etap 26:
ETAP26_RAW_DUMP.zip:
- ui_and_param_blx_scan.txt
- param_write_and_ctx_windows.txt
655 BLX hits w zadanym obszarze UI/parameter.

Etap 27:
ETAP27_RAW_DUMP.zip:
- ui_resource_literals.txt
- ui_builders_windows.txt
0 trafień dla wskazanych pełnych adresów 32-bitowych.

Etap 28:
ETAP28_RAW_DUMP.zip:
- full_bin_literals.txt
- subtables_0x0807f5e0_0x0807f680.txt
0 trafień dla wskazanych pełnych adresów 32-bitowych.

Etap 29:
ETAP29_RAW_DUMP.zip:
- low16_all_bin_hits.txt
8 trafień dla zadanych dolnych 16 bitów.

Etap 30:
ETAP30_RAW_DUMP.zip:
- esp32_resources_188.json
188 rekordów.

# 20. RAW/DISASSEMBLY UWAGA

Etap 23 wykazał brak działającego Capstone dla tego przebiegu oraz brak użytecznego wyniku z zastosowanego llvm-objdump. Skrypt przeszedł do RAW HEX FALLBACK + własnego dekodera BL/literałów.

Dlatego:
- RAW dump jest źródłem prawdy,
- własny decoder BL nie zastępuje pełnego disassemblera,
- trudne BLX należy rozkodowywać bezpośrednio z bajtów.

# 21. CO JUŻ WYSTARCZA DO ESP32-C6

Można rozpocząć implementację:
1. CAN driver,
2. EstymaCanFrame,
3. RX/TX queues,
4. parameter protocol 0x0604/0x0584,
5. parameter engine typów 1..5,
6. resource database 188 rekordów,
7. generator metadata dla Home Assistant.

Nie trzeba kopiować architektury FreeRTOS firmware 1:1. Należy odtworzyć zachowanie i protokół.

# 22. GŁÓWNE BRAKI

[OPEN-1] 0x200114C0 → [obj+0] → vptr → slot 0 → konkretny BLX target → TX adapter → CanMessagesToTransmit → CAN2.

[OPEN-2] Pełna semantyka pozostałych 11 rodzin RX.

[OPEN-3] Kompletny katalog CAN ID/command/type/index/subindex/value/response.

[OPEN-4] Pełny UI → CAN TX bridge.

[OPEN-5] Semantyczne mapowanie:
resource ID ↔ parameter index ↔ CAN index/subindex ↔ local RAM.

[OPEN-6] Region 0x20005EF0..0x20005F5B.

[OPEN-7] Pełny resource/widget/TypedText/Bitmap/callback mapping.

# 23. PRIORYTET DALSZEGO RE

PRIORYTET 1:
Rozwiązać 0x200114C0 → vptr → slot 0 → BLX target → TX queue → CAN2.

PRIORYTET 2:
Z korelacji Etapu 26 analizować tylko BLX związane z:
- FUN_08037212
- FUN_08011812
- 0x0800FF50
- 0x08063648
- 0x0801117C
- 0x080112A4
- 0x080629FC
- 0x0806E59C

Nie traktować 655 BLX jako 655 równorzędnych problemów.

PRIORYTET 3:
Zbudować tabelę:
ID | DIR | CMD | INDEX | SUB | TYPE | VALUE | RESPONSE | SIDE EFFECT
Każdy wpis musi mieć dowód adresowy w BIN.

PRIORYTET 4:
Dopiero po tym automatyczny generator encji Home Assistant.

# 24. ZALECANA ARCHITEKTURA ESP32-C6

src/
  can/
    estyma_can_frame.*
    estyma_can_driver.*
    estyma_can_rx.*
    estyma_can_tx.*
  protocol/
    estyma_param_protocol.*
    estyma_dispatch.*
    estyma_messages.*
  parameters/
    parameter_record.*
    parameter_engine.*
    parameter_types.*
    parameter_validation.*
  resources/
    resources_188.json
    resource_loader.*
    ui_metadata.*
  homeassistant/
    entity_generator.*
    number_entities.*
    select_entities.*
    switch_entities.*
    sensor_entities.*
  diagnostics/
    raw_can_logger.*
    protocol_trace.*

# 25. STATUS KOŃCOWY

Twardo potwierdzone:
- firmware identity,
- CAN2 = 0x40006800,
- RX queue,
- TX queue,
- 20-byte CAN record,
- CAN2 RX → dispatcher,
- parameter lookup/write engine,
- parameter types 1..5,
- 188 resource records,
- TypedText base 0x5BE64,
- główne ścieżki 0x0604/0x0584,
- vtable 0x08094508 slot 5/8,
- 0x080629FC read/poll path,
- 0x0806E59C queue/TX wrapper,
- 0x0800FF50 parameter receiver/response construction,
- FUN_08011812 jako local parameter write/validation, nie jako samodzielny CAN TX.

Nadal OPEN:
- exact TX BLX target z 0x200114C0,
- pełny UI → CAN TX bridge,
- pełna semantyka pozostałych 11 handlerów RX,
- pełny katalog CAN,
- mapowanie parameter indices do CAN objects,
- pełny widget/resource mapping,
- 0x20005EF0..0x20005F5B.

# 26. INSTRUKCJA DLA NOWEGO CHATA

Ten dokument jest punktem wejścia. Nowy chat:
1. nie zaczyna RE od zera,
2. nie powtarza Etapów 1–30 bez potrzeby,
3. zachowuje HARD/STRONG/OPEN/REJECTED,
4. zaczyna od OPEN-1,
5. następnie przechodzi do OPEN-2/OPEN-3,
6. dopiero później rozszerza mapę parametrów/UI,
7. nie zamyka OPEN bez bezpośredniego dowodu z firmware.

Najważniejszy następny łańcuch:
0x200114C0 → [obj+0] → vptr → vtable slot 0 → BLX target → TX adapter → CanMessagesToTransmit → CanTxTask → FUN_08061734 → CAN2.

Nie uznawać głównej architektury TX za zamkniętą, dopóki ten łańcuch nie zostanie rozwiązany.
