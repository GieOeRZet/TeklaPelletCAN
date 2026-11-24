# BATCH — CO2 / 0x080612E0: rozdzielenie UI helperów od aktywnego obiektu — 2026-11-19

## Wynik

[FW] Kontynuując łańcuch:

`CO2 0x08056D2C -> 0x0805D948 -> 0x080612E0`

nie wszystkie calle z `0x080612E0` są funkcjami TouchGFX. Kluczowa korekta: `FUN_080314BA` jest już wcześniej niezależnie potwierdzona jako accessor aktywnego obiektu modułu/regulatora:

```
FUN_080314BA()
  -> *DAT_08031A8C
```

Dlatego obecność `0x080314BA` w otoczeniu `0x080612E0` nie może być interpretowana jako „kolejny konstruktor widgetu”.

## 1. Co mamy twardo

`0x080612E0` ma 224 B i wykonuje m.in. BL do:

- `0x080393B2`
- `0x08030354`
- `0x08030358`
- `0x08039474`
- `0x080307BC`
- `0x080314BA`
- `0x08027DEC`
- `0x080313A4`
- `0x08039424`
- `0x08031426`
- `0x0804272C`
- `0x080347DC`
- `0x0803A0F8`

[FW] `0x08030358` jest helperem geometrii:

`object, X, Y, W, H`.

[FW] `this+0x48` dostaje:

`X=0, Y=0, W=480, H=272`.

[FW] `0x080314BA` zwraca aktywny obiekt z globalnego `DAT_08031A8C`.

## 2. 0x080313A4 — bardzo mocny setter TypedText

Mamy dwa niezależne call-site'y w komponentach CO:

```
CO2:
r5 = r4 + 0xA4
FUN_080313A4(r5, 0x3A)

CO1:
r5 = r4 + 0xA4
FUN_080313A4(r5, 0x39)
```

oraz:

- `0x39` = TypedText 57 = „Ogrzewanie 1”
- `0x3A` = TypedText 58 = „Ogrzewanie 2”

[STRONG] `FUN_080313A4(object, typedTextId)` jest więc setterem/konfiguratorem pola tekstowego albo wrapperem setter-a TypedText. To jest znacznie mocniejsza identyfikacja niż samo występowanie ID w bazie.

Nie nadajemy jeszcze konkretnej nazwy TouchGFX klasy bez vtable.

## 3. Nowy model 0x080612E0

Zamiast traktować cały blok jako „budowę widgetów”, właściwszy model jest:

```
0x0805D948
   |
   +--> 0x080612E0
          |
          +--> UI object construction/configuration
          |      |
          |      +--> setGeometry(0,0,480,272)
          |      +--> text/resource helpers
          |      +--> other UI methods
          |
          +--> FUN_080314BA()
                 |
                 +--> aktywny obiekt modułu/regulatora
```

[STRONG] To oznacza, że granica między UI i parameter/module engine przebiega wewnątrz tego komponentu, a nie dopiero po jego zakończeniu.

## 4. Dlaczego to jest ważne dla 1:1

Mamy już dwa różne rodzaje danych w jednym łańcuchu:

**UI:**
- child +0x48,
- 480×272,
- TypedText 57/58,
- helper geometrii.

**Model/regulator:**
- aktywny singleton `*DAT_08031A8C`,
- pola +0x12A/+0x12B/+0x12C,
- parameter mapper `FUN_08036FF2`.

To jest dokładnie miejsce, którego szukaliśmy: nie tylko „jak narysować ekran”, ale gdzie obiekt UI pobiera stan modelu.

## 5. Korekta planu dalszego trace

Nie skanujemy już `0x080314BA` jako potencjalnego widgetu.

Teraz:

```
0x080612E0
  |
  +--> 0x080313A4 -> konkretny Text/TypedText child
  |
  +--> 0x08030358 -> konkretna geometria
  |
  +--> 0x080314BA -> aktywny model object
  |
  +--> 0x0804272C / 0x080347DC
          -> ustalić, czy są value/format/visibility helpers
```

Następny dowód ma być:

```
0x080612E0
 -> konkretny child
 -> vptr
 -> setter/value/visibility
 -> panel index
 -> FUN_08036FF2
 -> CAN
```

## Pewność

[FW] `FUN_080314BA` = accessor aktywnego obiektu.

[FW] `FUN_08030358` = geometria X/Y/W/H.

[FW] `this+0x48` = 0,0,480,272.

[STRONG] `FUN_080313A4(object,id)` jest setterem/konfiguratorem TypedText, potwierdzone przez ID 57/58.

[HYPOTHESIS] Dokładna klasa TouchGFX obiektu przekazywanego do `FUN_080313A4`.

[HYPOTHESIS] Semantyczne role `0x0804272C` i `0x080347DC` — wymagają dalszego call-convention/vtable proof.
