# BATCH — HOME/MAIN ROOT + 0x47290 + GRAFIKA KOTŁA — 2026-11-19

## Cel
Przerwać zawężanie analizy do CO i przejść na cały ekran Home/Main. Szczególny cel: znaleźć rzeczywiste miejsce osadzenia grafiki kotła oraz jej zależność od wariantu.

## 1. Twardy root Home/Main

Z surowego `decompiled.c`:

```
FUN_0803e5ac(root)
  +0x0E0  -> FUN_08038ed0
  +0x107  -> FUN_08047230
  +0x10B  -> FUN_0800dcd4(... 0x338, 0x28)
  +0x213D -> FUN_0802e716
  +0x23DC -> FUN_08047244
  +0x24B7 -> FUN_08047290
  +0x258F -> FUN_08047604
  +0x289B -> FUN_08047e54
  +0x297F -> FUN_08038ed0
  +0x298A -> FUN_08038ed0
```

To jest znacznie mocniejszy punkt zaczepienia niż dalsze szukanie CO.

## 2. Korekta znaczenia FUN_08047290

`FUN_08047290` NIE tworzy sześciu niezależnych widgetów od zera.

Kod:

```
FUN_0802e620();
*param_1 = DAT_08047320;
FUN_0804dc58(param_1 + 0x18);
FUN_0800dcd4(param_1 + 0x2A, DAT_0804732C, 0x40, 6);
FUN_0800dcd4(param_1 + 0x8A, DAT_08047330, 0x34, 6);
uVar4 = FUN_080314ba();
FUN_080318b4(uVar4,param_1);

iVar6 = 0;
do {
    ...
    puVar5[10] = param_1 + 0x20;
    puVar5[0xF] = param_1 + 0x24;
    iVar6++;
    uVar1 = *(ushort *)(param_1 + 0x1F);
    *(ushort *)(param_1 + 0x1F) = uVar1 + 1;
    param_1[uVar1 + 0x19] = puVar5;
    puVar5 += 0x10;
} while (iVar6 < 6);
```

Czyli mamy:
- tablicę 6 rekordów,
- stride rekordu = `0x40`,
- drugi blok 6 elementów stride `0x34`,
- każdy z 6 rekordów dostaje wskaźnik do wspólnego `root+0x20` i `root+0x24`,
- licznik/indeks jest inkrementowany w `+0x1F`.

To wygląda jak sześć wpisów/slotów jednego komponentu, a nie sześć osobnych klas C++.

## 3. Co to zmienia dla grafiki kotła

Ważne: `0x47290` nie wygląda na miejsce, gdzie bezpośrednio siedzi bitmapa kotła.

W samym konstruktorze Home/Main mamy osobno:
- `0x47244` — mały komponent z obiektem `+0x18`, geometrią ustawianą przez vtable +0x2C/+0x30,
- `0x47290` — sześcioslotowy komponent,
- `0x47604` — bardzo duży komponent zawierający wiele obiektów,
- `0x47E54` — kolejny komponent,
- trzy proste obiekty `FUN_08038ED0`.

Dlatego następny pionowy atak na grafikę powinien iść przez wszystkie te dzieci, a nie przez CO.

## 4. FUN_08038ED0 — ważna identyfikacja granicy

`FUN_08038ED0`:

```
FUN_0802dd4c();
*param_1 = DAT_08038ee4;
param_1[10] = 0;
```

To jest krótki konstruktor obiektu z własnym vptr, nie konstruktor bitmapy jako taki.

W Home/Main wywołania:
- root+0x0E0
- root+0x297F
- root+0x298A

Nie wolno już zakładać, że `FUN_08038ED0` = WheelSelectorExtra bez vptr proof.

## 5. FUN_08047604 — cztery duże obiekty o geometrii 480x200

W konstruktorze `FUN_08047604` powstaje blok:

```
param_1 + 0x1D7
stride = 0x15 * 4 = 0x54
liczba = 4
```

Dla każdego z czterech obiektów wykonywane są wywołania vtable:
- +0x34(X,Y)
- +0x38(W=0x1E0 = 480)
- +0x3C(H=200)
- `FUN_0804de80()` przy zmianach geometrii.

Następnie obiekty są dołączane do rodzica przez `FUN_08030380`.

To jest realny, duży komponent Home/Main, ale na obecnym etapie nie mamy dowodu, że te cztery obiekty są bitmapami kotłów. Ich geometria wygląda raczej jak szerokie pola/warstwy.

## 6. Realne bitmapy kotłów nadal są twardym tropem

Firmware ma:
- `0x370A = Boiler image selector`
- zakres 1..3
- RAM `0x20021FA6`
- snapshot = wartość 3.

Pakiet prawdziwych bitmap zawiera:
- 011.png 105x126
- 012.png 108x141
- 013.png 82x145
- 014.png 54x100

Nie utożsamiamy jeszcze 1:1 `370A=1/2/3` z `011/012/013/014`.

## 7. Najważniejszy wniosek dla dalszej analizy

Cały Home/Main jest już na tyle konkretnie rozpoznany, że dalszy postęp powinien iść tak:

```
FUN_0803E5AC
  |
  +-- 0x23DC -> 47244
  +-- 0x24B7 -> 47290 (6 slotów)
  +-- 0x258F -> 47604 (duży komponent)
  +-- 0x289B -> 47E54
  +-- 0x297F -> 38ED0
  +-- 0x298A -> 38ED0
       |
       +--> vptr / klasy
       +--> Bitmap / BitmapData
       +--> TypedText
       +--> geometry
       +--> callback
       +--> 0x370A
```

Dopiero znalezienie konkretnego call-site Bitmap/BitmapData, który jest zależny od wartości `0x370A`, zamknie:
`selector -> bitmap ID -> widget -> pozycja na Home`.

## 8. Zakaz regresji

Nie wracać do samego CO jako głównego toru. CO jest już zamkniętym kręgosłupem parametr/instance/record. Teraz priorytetem jest Home/Main i grafika wariantu kotła.

