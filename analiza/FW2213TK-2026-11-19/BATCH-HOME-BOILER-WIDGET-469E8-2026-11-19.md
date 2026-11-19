# BATCH — REALNY WIDGET GRAFIKI KOTŁA: 0x080469E8 — 2026-11-19

## 1. Twardy wynik

Z surowego `firmware/FW2213TK-ghidra/decompiled.c` znaleziono klasę/komponent `FUN_080469E8`, która **jawnie ustawia Bitmap ID = 0x0E (14)**:

```
local_28._0_2_ = 0x0e;
FUN_080307bc(puVar4,local_28);
```

W repo `DOKUMENTACJA/bitmap_sizes.tsv` bitmapa:

```
014.png = 54x100
```

To jest bardzo mocna zgodność z grafiką kotła ze screenu użytkownika: widoczny kocioł ma właśnie skalę około 54x100 px.

## 2. Geometria komponentu

Ten sam `FUN_080469E8` tworzy kompozyt z bitmapą i czterema obiektami TypedText.

Bitmap:
- ID = 14
- rozmiar zasobu = 54x100
- Y = 0x14 = 20
- X jest wyliczane z `0x46 = 70` oraz wysokości/szerokości zasobu przez vtable +0x2C, więc komponent ma lokalną szerokość około 70 px i centruje bitmapę.

Teksty:
- TypedText `0x1ED = 493`, geometria X=0, Y=130, W=70, H=70
- TypedText `0x1ED = 493`, geometria X=25, Y=40, W=50, H=45
- TypedText `0x1EE = 494`, geometria X=0, Y=50, W=50, H=70
- TypedText `0x1ED = 493`, geometria X=30, Y=100, W=100, H=45

Ważne: 493/494 są **TypedText ID / style-resource**, a nie treścią wyświetlanego napisu. Treści są podpinane przez osobne pola obiektu.

## 3. Co dokładnie buduje 469E8

W skrócie:

```
FUN_080469E8
  |
  +-- FUN_0802dd4c()              child/base init
  |
  +-- Bitmap child @ +0x4F
  |      |
  |      +-- FUN_080307bc(..., 14)
  |      +-- vtable +0x2C -> X
  |      +-- vtable +0x30 -> Y=20
  |
  +-- TypedText child @ +0x17
  |      +-- ID 493
  |      +-- X=0, Y=130, W=70
  |
  +-- TypedText child @ +0x33
  |      +-- ID 493
  |      +-- X=25, Y=40, W=50
  |
  +-- TypedText child @ +0x25
  |      +-- ID 494
  |      +-- X=0, Y=50, W=50
  |
  +-- TypedText child @ +0x41
         +-- ID 493
         +-- X=30, Y=100, W=100
```

Na końcu:
```
uVar1 = FUN_080314ba();
FUN_080318b4(uVar1,param_1);
```
czyli komponent zostaje związany z aktywnym modelem/regulatorem.

## 4. Cztery instancje

`FUN_0803E34C` tworzy **cztery kopie** tego samego komponentu:

```
FUN_080469E8(param_1 + 0x251);
FUN_080469E8(param_1 + 0x2B8);
FUN_080469E8(param_1 + 799);   // 0x31F
FUN_080469E8(param_1 + 0x386);
```

Ponieważ `param_1` jest `undefined4*`, rzeczywisty stride bajtowy wynosi:

```
0x2B8 - 0x251 = 0x67 words = 0x19C bytes
0x31F - 0x2B8 = 0x67 words = 0x19C bytes
0x386 - 0x31F = 0x67 words = 0x19C bytes
```

Czyli jest to **cztery identyczne sloty/komponenty o stałym rozmiarze ~0x19C bajta**.

Nie wolno jeszcze twierdzić, że są to cztery widoczne kotły na Home. To wymaga połączenia `FUN_0803E34C` z konkretnym ekranem/rodzicem.

## 5. Krytyczna granica: 370A

Na tym etapie mamy:

```
0x370A = Boiler image selector (u8, 1..3)
        |
        |   [NIEZAMKNIĘTE]
        v
Home/Main boiler widget
        |
        v
FUN_080469E8
        |
        v
Bitmap ID 14 -> 014.png -> 54x100
```

**Nie mamy jeszcze dowodu, że wartość 0x370A jest bezpośrednio zapisywana do Bitmap ID w `469E8`.**

Wręcz przeciwnie: konstruktor `469E8` ustawia domyślnie ID 14 na sztywno. Następny cel to znaleźć metodę aktualizującą ten child, która po zmianie modelu/parametru może podmienić Bitmap ID.

## 6. Bardzo ważna korelacja ze screenshotem

Na screenie użytkownika górna część ma:
- grafikę kotła po lewej,
- około 70 px szerokości lokalnej strefy,
- wysokość grafiki około 100 px,
- pod/nad nią kilka niezależnych tekstów/liczników.

`FUN_080469E8` ma dokładnie taki układ: **70-pikselowy kompozyt z bitmapą 54x100 + 4 niezależne elementy tekstowe**.

To jest obecnie najlepszy znaleziony w firmware kandydat na rzeczywisty widget grafiki kotła.

## 7. Następny atak

Nie wracamy do CO.

Następny pionowy trace:
1. ustalić rodzica/ekran `FUN_0803E34C`,
2. znaleźć metody klasy z vptr `DAT_08046CC4`,
3. znaleźć writer Bitmap ID dla childa `+0x4F`,
4. znaleźć warunek/model field,
5. dopiero wtedy spiąć:
   `0x370A -> value -> bitmap ID 11/12/13/14`.

