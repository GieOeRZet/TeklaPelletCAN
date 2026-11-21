# TeklaPelletCAN / NewEstymaCan — pełne podsumowanie pracy OpenAI
## Zakres: Etap 1–52, ze szczególnym uwzględnieniem OPEN-1

**Cel projektu:** reverse engineering firmware Estyma i rekonstrukcja protokołu CAN oraz zachowania dodatkowego modułu Estyma.  
**Docelowo:** ESP32-C6 ma działać jako **dodatkowy moduł Estyma**, a nie jako zamiennik kontrolera. Home Assistant jest etapem późniejszym.

---

## 1. Najważniejsza decyzja architektoniczna

Aktualny cel nie brzmi „zrobić integrację HA”, tylko:

> Najpierw odtworzyć zachowanie firmware/protokołu wystarczająco dokładnie, aby ESP32-C6 można było później włączyć do magistrali jako kolejny moduł Estyma.

Dopiero potem:
- implementacja ESP32-C6,
- generowanie karty HA,
- MQTT/API/UI,
- dodatkowe funkcje.

Proponowana architektura:

```text
        Oryginalny kontroler Estyma
                    |
                  CAN BUS
                    |
        +-----------+-----------+
        |           |           |
    Vide Room    Vide Net    ESP32-C6
                             dodatkowy
                          moduł Estyma
                                |
                         później HA/API
```

---

# 2. Firmware referencyjny

Plik:
`FW2213TK_kopia.bin`

Parametry:
- rozmiar: `0x1F0000` = 2 031 616 B
- SHA-256:
`1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

To jest firmware traktowany jako źródło prawdy dla dotychczasowej analizy.

---

# 3. Najważniejszy odkryty tor CAN2

## CAN2

Baza peryferium:
`0x40006800`

### RX

- storage kolejki: `0x200244BC`
- handle kolejki: `0x200244DC`
- producer: `0x0806F9F8 -> FUN_080617DC`
- consumer: `CanRxTask @ 0x0806E94C -> FUN_08063B80`

### TX

- storage kolejki: `0x200244E0`
- handle kolejki: `0x200244EC`
- primitive kolejki: `0x08057224`
- consumer: `CanTxTask @ 0x080654A8`
- hardware TX: `FUN_08061734(0x40006800, record)`

### Ważne twarde ustalenie z ETAP41

Literal:
`0x200244DC`

występuje dokładnie raz:
`0x0806FA4C`

Nie znaleziono exact 32-bit little-endian:
- `0x0800FF44`
- `0x0800FF45`

---

# 4. EstymaCanFrame

Rozpoznana struktura 20 B:

| offset | znaczenie |
|---|---|
| +0x00..+0x03 | StdId u32 |
| +0x04..+0x07 | ExtId u32 |
| +0x08 | IDE, raw `0x04` |
| +0x09 | RTR, raw `0x02` |
| +0x0A | DLC = RDTR & 0x0F |
| +0x0B..+0x12 | Data[0..7] |
| +0x13 | RX metadata = RDTR >> 8 |

RX odczytuje:
- RIR = base + mailbox*0x10 + `0x1B0`
- RDTR = `+0x1B4`
- RDLR = `+0x1B8`
- RDHR = `+0x1BC`

StdId:
`RIR >> 21`

ExtId:
`RIR >> 3`

---

# 5. RX dispatcher — 12 rodzin handlerów

Główna ścieżka:

```text
CAN2 RX
  -> FUN_080617DC
  -> ReceivedCanMessages
  -> CanRxTask
  -> FUN_08063B80
  -> 12 rodzin handlerów
```

Rodziny:

1. `0x0800E2D2`
2. `0x0800DFC6`
3. `0x08063E10`
4. `0x08063F30`
5. `0x0800FEB4`
6. `0x0800FF50`
7. `0x0800F894`
8. `0x0806369E`
9. `0x0800F0D0`
10. `0x08062A90`
11. `0x08063FBA`
12. `0x08064008`

Rozpoznane filtry obejmują m.in.:
- base + `0x180` / `0x280`
- base + `0x380` / `0x480`
- base + `0x600`
- `0x0584`
- `0x01EE`
- `0x0584`
- zakres `0x0701..0x077F`
- zakres `0x0581..0x0600`
- `0x0288`
- zakres `0x0240..0x0257`

Pełna semantyka wszystkich 12 rodzin nadal nie jest zamknięta.

---

# 6. Parametry — silnik zapisu

`FUN_08011812`

Potwierdzone:
- znajduje rekord parametru,
- sprawdza typ,
- zapisuje przez `record + 0x0C`,
- obsługuje typy 1..5,
- przy `param_5 != 0` wykonuje kontrolę stanu,
- przy `param_6 == 1` wykonuje walidację zakresu.

Dla `param_5=1`:
- rekord = base + index * `0x2C`
- `record+0x2C` musi być `0x01` albo `0x03`
- inaczej status `0x09`

Dla `param_6=1`:
- dodatkowa walidacja pól wokół `record+0x1C` i `record+0x14`.

### Ważne odrzucenie hipotezy

Nie potwierdzono, że `FUN_08011812` jest samodzielnym dirty-bit/TX setterem.

Nie stwierdzono w niej bezpośrednio:
- `0x0806E59C`,
- `0x08057224`,
- wysyłania CAN,
- potwierdzonego callbacku TX.

---

# 7. Lokalny zapis parametru

`FUN_08037212`

Ma 33 bezpośrednich callerów UI.

Potwierdzony lokalny tor:

```text
UI
 -> FUN_08037212
 -> FUN_08011812
 -> parameter record +0x0C
 -> local RAM
```

OPEN nadal dotyczy pełnego mechanizmu publikacji CAN po takim zapisie.

---

# 8. Zapis przychodzący z CAN

`FUN_08062B22`

Tor:

```text
CAN frame
 -> 0x08062AE4 / handler
 -> FUN_08062B22
 -> index z frame +4/+5
 -> FUN_080115F6
 -> type
 -> FUN_08011812
 -> record +0x0C
```

Typy:
- 1 = 1 byte
- 2 = 16 bit
- 3 = 32 bit
- 4 = signed 16 bit
- 5 = 32 bit

---

# 9. Obiekt 0x200114C0 — klucz OPEN-1

Obiekt:
`0x200114C0`

Konstruktor:
`FUN_0800FF44`

Zostało twardo potwierdzone:

```text
FUN_0800FF44(
    0x200114C0,
    0x20008D60,
    0x20008D84
)
```

Konstruktor ustawia:

```text
[0x200114C0 + 0x00] = 0x20008D60
[0x200114C0 + 0x04] = 0x20008D84
[0x200114C0 + 0x08] = 4
```

Ostatnie słowo to Node ID `4`.

---

# 10. Kluczowa inicjalizacja z ETAP44

W inicjalizacji:
- `r8 = 0x20008CD0`
- `r5 = r8 + 0x90 = 0x20008D60`
- `[sp+0x30] = r8 + 0xB4 = 0x20008D84`

Następnie:

```text
FUN_0800FF44 @ 0x08000D94
```

dostaje:

```text
r0 = 0x200114C0
r1 = 0x20008D60
r2 = 0x20008D84
```

To jest HARD.

---

# 11. Najważniejsza luka OPEN-1

W odpowiedzi/publikacji znajduje się twarde wywołanie pośrednie:

```text
0x080100BE:
    add r1, sp, #8

0x080100C0:
    ldr r0, [r4]

0x080100C2:
    ldr r2, [r0]

0x080100C4:
    ldr r2, [r2]

0x080100C6:
    blx r2
```

Dla:
`r4 = 0x200114C0`

oznacza to:

```text
r0 = [0x200114C0]
   = 0x20008D60

r2 = [0x20008D60]
r2 = [r2]

BLX r2
```

Czyli istnieje interfejs/vtable pod `0x20008D60`, a slot `+0x00` jest wywoływany pośrednio.

### Czego NIE wolno jeszcze twierdzić

Nie ma bezpośredniego dowodu, że:

```text
slot +0x00 == FUN_0806E59C
```

To pozostaje OPEN.

---

# 12. FUN_0806E59C — wrapper TX

`FUN_0806E59C` jest twardo potwierdzonym wrapperem kolejki TX.

Buduje lokalną strukturę 20 B, pobiera:

```text
CanMessagesToTransmit = 0x200244EC
```

i wywołuje:

```text
0x08057224
```

czyli primitive kolejki TX.

Dalszy tor:

```text
FUN_0806E59C
 -> 0x200244EC / CanMessagesToTransmit
 -> CanTxTask @ 0x080654A8
 -> FUN_08061734
 -> CAN2 @ 0x40006800
```

To jest HARD jako ścieżka wrappera TX.

Nie jest HARD, że właśnie ten wrapper jest metodą slotu `+0x00` obiektu `0x20008D60`.

---

# 13. Vtable 0x08094508

Rozpoznano tabelę:

`0x08094508`

Istotne sloty:
- slot 5 → `0x0806E59C`
- slot 8 → `0x080629FC`

`0x080629FC` jest pollerem READ.

Ważne:
- `FUN_0806E59C` nie ma zwykłego bezpośredniego BL w analizowanym miejscu,
- `FUN_080629FC` również jest używany przez mechanizm pośredni.

---

# 14. READ — 0x0604

Poller:
`0x080629FC`

Common vtable:
`0x08094508`

Slot 8:
`0x080629FC`

Tor:

```text
poller
 -> parameter table + counter*0x2C + 0x08
 -> 0x08062AE4
 -> CAN frame
```

Znany request:

```text
StdId = 0x0604
DLC   = 8
Data[3] = 0x40
Data[4..5] = parameter index
Data[6] = 0x01
```

Znany przykład:
`index = 0x2001`

Nie należy automatycznie nazywać tego CANopen/SDO — to nie zostało dowiedzione.

---

# 15. WRITE / RESPONSE / ACK / ERROR

Rozpoznane kody:

- `0x20` — write
- `0x40` — read
- `0x42` — response z wartością
- `0x60` — acknowledgement
- `0x80` — error

W analizowanym torze:
- request/write używa `0x0604`
- response/publication używa `0x0584`

Przeanalizowany przykład:
- index `0x3004`
- subindex `0x01`

Pełny katalog 0x0604/0x0584 pozostaje OPEN.

---

# 16. FUN_0800FF50

Potwierdzony tor:

```text
StdId == object+0x08+0x600
    |
    +-- (data[3] >> 5) == 1 lub 2
    |
    +-- parameter index = data[4..5]
    |
    +-- type = data[6]
    |
    +-- value = data[7..]
    |
    +-- FUN_080115F6
    |
    +-- FUN_08011812
    |
    +-- response
    |
    +-- object 0x200114C0
    |
    +-- vtable slot 0
    |
    +-- BLX
```

Dodatkowo z ETAP45:
- brak literalnego wskaźnika 32-bit do `0x0800FF50`
- wykryto bezpośredni caller `0x08063C3E`

To wzmacnia obraz, że część architektury korzysta z bezpośrednich BL, a część z interfejsów/pośrednich wywołań.

---

# 17. 0x20008CD0 — główny anchor

`0x20008CD0` ma wiele literalnych xrefów.

Wykryte wcześniej:
- `0x08000DE8`
- `0x08001AD8`
- `0x0800473C`
- `0x08006288`
- `0x08007838`
- `0x0800C60C`
- `0x0800D7E0`

`0x20008D60` nie występuje jako literal — jest wyliczany:

```text
0x20008CD0 + 0x90
```

`0x20008D84` ma literalne xrefy m.in.:
- `0x08001CA4`
- `0x08002C40`
- `0x08014528`
- `0x0803754C`
- `0x08062908`
- `0x080632B8`

---

# 18. Powiązanie z Vide Room

W tabeli wokół `0x0800D7A0` występują:

- `0x20008CD0`
- `0x20008D4C`
- `0x40024000`
- `"Vide room 2 sw. ver. after dot"`
- `"Vide room 3 sw. ver. after dot"`
- `"Alarm date timestamp"`

To jest mocny dowód, że `0x20008CD0` należy do większej struktury/obszaru danych powiązanego z modułami/konfiguracją Vide Room.

Nie należy jednak na tej podstawie zakładać, że cały obszar jest jednym obiektem CAN.

---

# 19. Dodatkowe pola obszaru 0x20008CD0

W analizowanej inicjalizacji pojawiają się m.in.:

- `+0x80 = 0x20008D50` → `FUN_0800D9AC`
- `+0x90 = 0x20008D60`
- `+0x94 = 0x20008D64` → `FUN_0800DB08`
- `+0x98 = 0x20008D68` → `FUN_0800DC44`

Dla `FUN_0800DC44` wiadomo z analizy, że jest elementem sekwencji inicjalizacyjnej i wywołuje dalej `0x08014824`.

ETAP46 wykonał RAW dump funkcji pomocniczych:
- `0x0800D9AC..0x0800DA2C`
- `0x0800DB08..0x0800DB88`
- `0x0800DC9C..0x0800DD38`

ETAP45 wykonał dodatkowo:
- `0x080A6000..0x080A6120`
- `FUN_0800DC44`
- literal xrefy `0x0800FF50`, `0x0806E59C`, `0x080629FC`

---

# 20. Obszar 0x080A6000

W ETAP45 sprawdzono:
`0x080A6000..0x080A6120`

Wynik nie wyglądał jak kod; obserwowany był powtarzalny wzorzec danych.

Wykryto m.in. odwołania:
- `0x0805CDD0 -> 0x080A6000`
- `0x08000DF8 -> 0x080A60BF`
- `0x08000DFC -> 0x080A60C1`

Nie został na tej podstawie ustalony jednoznacznie sens całego obszaru.

---

# 21. ETAP47 — 0x200114C4 / 0x200114C8

Wykonano literal scan:
- `0x200114C4`
- `0x200114C8`

oraz RAW:
- `0x080A4420..0x080A4460`
- `0x080A31E0..0x080A3220`

Cel: sprawdzenie sąsiednich pól obiektu `0x200114C0` i potencjalnych struktur pomocniczych.

Wnioski z samego etapu RAW nie zostały awansowane ponad materiał dowodowy.

---

# 22. ETAP48 — pełny zakres literalny 0x20008D00..0x20008E00

Wykonano scan wszystkich wyrównanych co 4 B wartości:

```text
0x20008D00 .. 0x20008E00
```

Celem było znalezienie:
- wszystkich literalnych wskaźników do pól struktury,
- wyłapanie pól pomiędzy `0x20008CD0` i `0x20008E00`,
- odnalezienie możliwych vtable/interface pointerów.

To doprowadziło do rozszerzenia analizy na xrefy:
- `0x20008D24 @ 0x0800C614`
- `0x20008D28 @ 0x0800C6DC`
- `0x20008D44 @ 0x080632C0`
- `0x20008D4C @ 0x0800D7E4`

---

# 23. ETAP49 — rozszerzone okna 0x8Dxx

Zrzucono:

```text
0x0800C580..0x0800C6E0
0x08063240..0x08063300
0x0800D760..0x0800D840
```

Cel:
- zobaczyć instrukcje wokół xrefów,
- ustalić, czy pola `0x8D24`, `0x8D28`, `0x8D44`, `0x8D4C` są:
  - danymi,
  - wskaźnikami,
  - elementami tablicy,
  - częścią obiektów,
  - argumentami konstruktorów.

---

# 24. ETAP50 — 0x0800FF40..0x08010100

Zrzucono szerokie okno obejmujące:
- `FUN_0800FF44`
- okolice `FUN_0800FF50`
- dispatch końcowy
- konstrukcję odpowiedzi.

Drugie okno:
`0x08063C00..0x08063C80`

obejmuje caller/tor wejściowy do `FUN_0800FF50`.

To było kluczowe dla rozdzielenia:
- konstruktora,
- handlera,
- vtable dispatch,
- bezpośredniego caller.

---

# 25. ETAP51 — wrapper TX

Zrzucono:

```text
0x0806E580..0x0806E6C0
0x080103B0..0x08010400
```

Pierwszy zakres obejmuje `FUN_0806E59C` i sąsiedni kod.

Drugi obejmuje dalszy fragment logiki wywołania pośredniego / odpowiedzi.

---

# 26. ETAP52 — końcowe szerokie okna

Zrzucono:

```text
0x08010040..0x080100E0
0x08010340..0x080103F0
```

Cel:
- pełniejszy kontekst instrukcji `0x080100BE..0x080100C6`,
- ustalenie sposobu przekazywania struktury do interfejsu,
- korelacja z sąsiednimi fragmentami odpowiedzi.

To jest ostatni wykonany RAW etap w tej serii.

---

# 27. 0x080702DC — poller/object graph

`0x0800DCD4` tworzy cztery instancje `0x080702DC`:

- `0x200208EC`
- `0x200209C4`
- `0x20020A9C`
- `0x20020B74`

Subobiekty `+0x30`:
- `0x2002091C`
- `0x200209F4`
- `0x20020AD0`
- `0x20020BA4`

Twardo wynika:
- istnieją cztery obiekty z taką strukturą,
- mają podobne subobiekty.

Nie udowodniono, że cały `0x080702DC` jest wyłącznie menedżerem CAN.

---

# 28. 0x2002466C

Literalne wystąpienia:
- `0x080019E0`
- `0x0800BAA4`
- `0x0803C248`
- `0x08063D1C`
- `0x0806E60C`

Istotne:
`0x08063D1C -> kod około 0x08063C6C -> BL 0x08062A90`

`0x0806E60C` znajduje się w `FUN_0806E59C` i odwołuje się do pól tego obiektu.

Pełne znaczenie/inicjalizacja `0x2002466C` nadal jest OPEN.

---

# 29. Resource/UI — wcześniejsza część projektu

Firmware ma:
`DAT_0804866C`

Dokładnie:
- 188 rekordów,
- indeksy 0..187,
- 16 B / rekord.

Typy:
- type 0: 139
- type 1: 31
- type 2: 3
- type 3: 12
- type 4: 1
- type 5: 2

f07:
- `0x00`: 148
- `0x01`: 40

TypedText:
`0x5BE64 = 0x5BD80 + 57*4`

Ważne:
**nie używać starego `0x5BD80` jako bazy TypedText.**

---

# 30. FUN_080480C0

Potwierdzono:
- resource table,
- rekordy 16 B,
- wyszukiwanie po wejściowych wartościach,
- typ rekordu steruje dispatch.

Widget:
- base = `param_1 + 0x42C`
- stride = `0x338`
- istotne pola około `+0x334` i `+0x270`

Dispatch:
- type 1 → `FUN_0804E598`
- type 2 → `FUN_0804E740`
- type 3 → `FUN_0804E75A`
- type 5 → `FUN_0804E740`
- final → `FUN_0804E5BC(widget,10)`

Pełna mapa resource → TypedText/Bitmap/callback/widget pozostaje osobnym OPEN.

---

# 31. FUN_0803E714

Buduje wejście dla stron 1..4 z:

`DAT_0803EEC0 +0x62`

oraz opcjonalnie:

`+0x6E`

Następnie:
- `FUN_080480C0`
- `FUN_08036FF2`
- `FUN_0804842C`

Widget:
`+0x42C + N*0x338`

---

# 32. Ważne odrzucone hipotezy

Nie używać ponownie jako faktów:

- `0x68 = extra-fan gate` — odrzucone; rzeczywisty tor prowadzi do `0x300B -> Stop burning wood`
- `0x10E = 0x3505` — odrzucone
- `0x10F = 0x2105` — odrzucone
- `47290 = graph` — odrzucone
- `47290 = Home seven horizontal zones` — odrzucone
- `056/057 = 151/152` — odrzucone
- Bitmap ID = widget ID — odrzucone
- `370A 1/2/3 -> bitmap 011/012/013` — odrzucone
- `174 = Home-only` — odrzucone
- interpretacja `0x47/0x48` wyłącznie z numeracji — odrzucona
- `FUN_08011812` jako samodzielny dirty-bit/TX setter — odrzucone
- `0x08078578 == 0x08094508` — odrzucone

---

# 33. Aktualny stan OPEN-1

## HARD / bezpośrednio potwierdzone

1. CAN2 = `0x40006800`.
2. RX/TX queue architecture.
3. `EstymaCanFrame` 20 B.
4. `0x200114C0` jest konstruowany przez `FUN_0800FF44`.
5. Konstruktor dostaje:
   - `0x20008D60`
   - `0x20008D84`
6. Node ID = `4`.
7. `[0x200114C0] = 0x20008D60`.
8. Istnieje pośrednie wywołanie przez `[0x20008D60]`.
9. `FUN_0806E59C` pobiera `0x200244EC` i przekazuje ramkę do `0x08057224`.
10. `CanTxTask` odbiera z tej kolejki.
11. Hardware TX kończy się w `FUN_08061734`.
12. `FUN_080629FC` jest READ pollerem.
13. vtable `0x08094508` ma slot 5=`FUN_0806E59C`, slot 8=`FUN_080629FC`.
14. `0x0604` jest używane dla znanego READ/write path.
15. `0x0584` występuje w znanym response/publication path.
16. `FUN_0800FF50` obsługuje określony tor parametrowy zależny od Node ID i danych ramki.

## STRONG

1. `0x20008CD0` jest większym anchorem struktury/obszaru danych.
2. `0x20008D60` i `0x20008D84` są polami wyliczanymi względem `0x20008CD0`.
3. `0x20008CD0` jest związane z otoczeniem Vide Room/configuration.
4. `0x20008D60` jest interfejsem/obiektem z vtable-like pierwszym słowem.
5. `FUN_0806E59C` jest bardzo mocnym kandydatem do jednego z interfejsowych slotów TX, ale nie jest to jeszcze dowód slotu `+0`.

## OPEN

Najważniejsze:

> **Jaki dokładnie adres jest zapisany do `[0x20008D60]` i jaki jest adres vtable/interfejsu, którego slot 0 jest wywoływany w `0x080100C6`?**

Następnie:

> **Czy slot 0 prowadzi bezpośrednio do `FUN_0806E59C`, czy do kolejnego wrappera?**

Dalej:
- pełny katalog 0x0604/0x0584,
- pełna semantyka 12 rodzin RX,
- inicjalizacja `0x2002466C`,
- pełny graf pollerów `0x080702DC`,
- pełne zachowanie modułu przy starcie, obecności/nieobecności i timeoutach.

---

# 34. Najkrótsza droga do dalszego domknięcia

Nie należy teraz wracać do szerokiego losowego skanowania BIN.

Priorytet:

### A. `[0x20008D60]`

Znaleźć **pierwszy rzeczywisty zapis** do:

```text
*(uint32_t *)0x20008D60
```

oraz zapisy do:
- `0x20008D64`
- `0x20008D68`
- `0x20008D6C`
- itd.

Trzeba rozróżnić:
- literal write,
- computed write,
- memcpy/memset,
- konstruktor,
- inicjalizację przez funkcję.

### B. Obiekt źródłowy

Prześledzić funkcje związane z:
- `0x0800D9AC`
- `0x0800DB08`
- `0x0800DC44`
- dalszymi funkcjami inicjalizacyjnymi.

### C. Vtable

Gdy znajdziemy wartość `[0x20008D60]`:
1. potraktować ją jako adres vtable/interface,
2. zrzucić cały blok,
3. wyznaczyć sloty,
4. sprawdzić wszystkie sloty,
5. znaleźć slot odpowiadający TX,
6. potwierdzić cały łańcuch do `0x200244EC`.

### D. Dopiero wtedy zamknąć OPEN-1

Nie awansować na HARD na podstawie:
- podobieństwa,
- sąsiedztwa,
- nazwy funkcji,
- samego vtable slotu,
- heurystyki C++.

---

# 35. Co Gemini ma dostać z tego dokumentu

Jeżeli Gemini „zapomniał czego szuka”, kluczowe zdanie jest:

> **Nie szukamy już ogólnie CAN. Szukamy brakującego ogniwa OPEN-1: skąd bierze się pierwsze słowo `[0x20008D60]`, jaki jest jego vtable/interfejs i czy slot 0 prowadzi do `FUN_0806E59C`/wrappera TX.**

Kontekst:
```text
FUN_0800FF44
      |
      v
0x200114C0
      |
      +0x00 -> 0x20008D60
      |
      +0x04 -> 0x20008D84
      |
      +0x08 -> Node ID 4

response path
      |
      v
[0x200114C0]
      |
      v
0x20008D60
      |
      v
[r0]
      |
      v
[r0]
      |
      v
BLX slot 0
      |
      v
???  <-- TO TRZEBA UDOWODNIĆ
      |
      v
TX queue 0x200244EC
      |
      v
0x08057224
      |
      v
CanTxTask
      |
      v
FUN_08061734
      |
      v
CAN2
```

Najważniejsza zasada:
**`FUN_0806E59C` jest potwierdzonym wrapperem TX, ale nie wolno jeszcze pisać, że jest slotem 0 `0x20008D60`, dopóki firmware nie pokaże tego bezpośrednio.**

---

# 36. Materiały zawarte w tym ZIP-ie

W katalogu `evidence_packages/` znajdują się najważniejsze pakiety:
- MASTER Etap 1–38,
- Gemini handoff,
- ETAP44 independent,
- ETAP45,
- ETAP46,
- ETAP47,
- ETAP48,
- ETAP49,
- ETAP50,
- ETAP51,

---

# ADDENDUM — ETAP39–52 / RE PACK / CURRENT HANDOFF 2026-11-21

## 37. Firmware RE pack

User supplied `FW2213TK_RE_PACK (1).zip`. It is an automatically prepared RE index for the same firmware. It contains, among other things:
- `literals.txt` / `literals_index.txt`
- `disasm_thumb2.txt`
- `bl_calls.txt`
- strings and other indexed data
- a raw memory window around the beginning of the image.

Important methodology:
- authoritative source remains `FW2213TK_kopia.bin`;
- RE pack is an index/accelerator;
- automatic disassembly must be verified against raw bytes for critical conclusions;
- missing literal-index entries must never be interpreted as zero bytes.

A custom OpenAI-side `OPENAI_RE_EXPLORER.zip` was created to query the pack using windows, literal-value searches and related cross-reference views.

## 38. ETAP39–44

ETAP39–40 concentrated on the runtime establishment of `0x200114C0`, `0x20008CD0`, `0x20008D84`, and the CAN queue objects.

ETAP41 established that the exact literal `0x200244DC` occurs once at `0x0806FA4C`, while exact 32-bit little-endian literals for `0x0800FF44` and `0x0800FF45` were absent.

ETAP42–43 expanded raw windows around `0x0806E59C` and adjacent code. The raw bytes must be preferred over automated decoding.

ETAP44:
- exact raw windows around `0x20008CD0` references;
- `0x20008CD0` xrefs: `0x08000DE8, 0x08001AD8, 0x0800473C, 0x08006288, 0x08007838, 0x0800C60C, 0x0800D7E0`;
- `0x20008D60` has no literal xref because it is computed as `0x20008CD0+0x90`;
- `0x20008D84` xrefs include `0x08001CA4, 0x08002C40, 0x08014528, 0x0803754C, 0x08062908, 0x080632B8`;
- the table around `0x0800D7E0` contains `0x20008CD0`, `0x20008D4C`, `0x40024000` and strings such as “Vide room 2 sw. ver. after dot” and “Vide room 3 sw. ver.”.

ETAP44 did not close OPEN-1.

## 39. ETAP45–52 raw evidence

ETAP45:
- `0x080A6000..0x080A6120`
- `0x0800DC44..0x0800DCA0`
- literal xrefs for `0x0800FF50`, `0x0806E59C`, `0x080629FC`
- additional follow-up contexts.

ETAP46:
- `0x0800D9AC..0x0800DA2C`
- `0x0800DB08..0x0800DB88`
- `0x0800DC9C..0x0800DD38`

ETAP47:
- literal xrefs `0x200114C4`, `0x200114C8`
- `0x080A4420..0x080A4460`
- `0x080A31E0..0x080A3220`

ETAP48:
- aligned 32-bit literals throughout `0x20008D00..0x20008E00`
- notable xrefs: `0x20008D24 @ 0x0800C614`, `0x20008D28 @ 0x0800C6DC`, `0x20008D44 @ 0x080632C0`, `0x20008D4C @ 0x0800D7E4`.

ETAP49:
- `0x0800C580..0x0800C6E0`
- `0x08063240..0x08063300`
- `0x0800D760..0x0800D840`

ETAP50:
- `0x0800FF40..0x08010100`
- `0x08063C00..0x08063C80`

ETAP51:
- `0x0806E580..0x0806E6C0`
- `0x080103B0..0x08010400`

ETAP52:
- `0x08010040..0x080100E0`
- `0x08010340..0x080103F0`

These stages were deliberately kept as RAW evidence. They do not by themselves prove the slot-0 target.

## 40. Current lead-agent protocol

The user explicitly decided:
- Gemini is the lead RE agent and may be attempting to close OPEN-1;
- OpenAI should execute the requested scripts/tasks as instructed and preserve RAW evidence;
- do not independently change the lead/authority model;
- do not add speculative conclusions when the task is an execution-only Gemini task.

Therefore, for continuation:
1. read this master;
2. inspect the requested existing RAW packages first;
3. execute the exact requested script;
4. package RAW output;
5. only interpret when explicitly requested or when a handoff requires concise evidence classification;
6. never promote a hypothesis without direct firmware evidence.

## 41. Current OPEN list

### OPEN-1 — highest priority
Find the first actual initialization/write of:
`[0x20008D60]`
Then identify the pointed vtable/interface, enumerate its slots, and prove the slot-0 target.

Required final chain:
`0x200114C0 -> [obj+0] -> 0x20008D60 -> vtable/interface -> slot 0 -> exact target -> TX adapter -> 0x200244EC -> CanTxTask -> FUN_08061734 -> CAN2`.

### Other OPENs
- complete remaining RX-family semantics;
- complete `0x0604/0x0584` catalogue;
- complete local parameter-write to CAN publication;
- complete `0x2002466C` initialization/meaning;
- complete `0x080702DC` poller/object graph;
- complete resource/UI/TypedText/Bitmap/callback mapping;
- resolve `0x20005EF0..0x20005F5B`;
- later validate behavior on live CAN.

## 42. Confidence discipline

Use:
- HARD / CONFIRMED = directly established by raw firmware/control-flow evidence;
- STRONG = multiple consistent clues, but not a complete direct proof;
- OPEN = unresolved;
- REJECTED = disproven by later evidence.

Never use names such as “CANopen/SDO” merely from opcode similarity. Do not infer semantic meaning from numeric adjacency alone.

## 43. Immediate next step

Do not restart the whole project. Continue exactly from:
`0x20008CD0 + 0x90 = 0x20008D60`.

The critical question is:
> What writes the first word at `0x20008D60`, what value does it write, and what does that value point to?

Only after that can the slot-0 TX target be closed.

## 44. Artifact inventory

Local handoff package contains:
- authoritative firmware BIN;
- RE pack;
- OpenAI RE Explorer;
- ETAP31–52 RAW packages;
- ETAP44/45 final variants;
- Gemini handoff package;
- MASTER ETAP1–38;
- full OpenAI summary.

GitHub documentation should remain text-based and evidence-focused; large binary/RAW packages are preserved locally as the current handoff archive unless separately committed through an appropriate binary mechanism.


# 45. OPEN1-P4 — wykonanie bezpośrednio na canonical BIN (2026-11-21)

Źródło: `FW2213TK_kopia.bin` wyłącznie; RE_PACK nie był używany jako źródło bajtów. SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`.

RAW artifact: `analiza/FW2213TK-2026-11-21/RAW_PACKET7_OPEN1_P4.txt`.

Najważniejsze nowe HARD:
- vtable `0x080A4568` -> slot 0 `0x080629FC` dla obiektu `0x2002466C`;
- w `0x080629FC`, dokładnie `0x08062A86`, znajduje się `strb r0,[r4,#0x0A]` po `movs r0,#1`; warunek: wynik `0x08062C78 >= 0x1F`;
- `0x08062AE4` buduje request READ: StdId `0x0604`, marker `0x40`, index w Data[4..5], Data[6]=1;
- CAN2_RX0 vector -> `0x0806F9F8` -> hardware serializer `0x080617DC` -> kolejka RX -> dispatcher `0x08063B80`;
- startup `0x08094644 -> 0x0808F74C -> 0x08062D82`; `0x08062D82` nie jest klasycznym copy .data/.bss do `0x20008D60`;
- w całym BIN brak LE32 dla `0x20008D60` i `0x080A4544`; `0x080A4568` występuje raz jako literal konstruktora `0x2002466C`.

OPEN pozostaje bez zmian:
> znaleźć pierwszy rzeczywisty runtime write do `[0x20008D60]`, ustalić jego wartość, wskazany vtable/interface i slot 0, a następnie udowodnić cały łańcuch do TX queue `0x200244EC`.

Metodologia na dalsze etapy: **pracujemy na canonical BIN**. Adresy RE_PACK mogą być podawane wyłącznie jako pomocnicze mapowanie, nie jako źródło dowodów.
