# BATCH-C064-CHAIN-37D00-INSTANCJA-2026-11-19

## Nowe twarde ustalenie

Pełna dekompilacja została ponownie przeanalizowana bez polegania wyłącznie na wcześniejszych notatkach.

### 1. C064 materializuje jednocześnie typ i instancję
`FUN_0803C064(param_1,param_2)`:

```
class = *(DAT_0803C218 + param_2)
```

Dla klas 1..4:
- class 1 -> object+0x12B = 1, object+0x12C = 1
- class 2 -> object+0x12B = 2, object+0x12C = 2
- class 3 -> object+0x12B = 3, object+0x12C = 3
- class 4 -> object+0x12B = 4, object+0x12C = 4

Po ustawieniu tych pól C064 dobiera descriptor przez `FUN_08039494` zależnie od `object+0x12A` i zapisuje go do `+0x110/+0x10C`.

Czyli C064 nie tylko „ustawia numer CO”. Jest dispatcherem, który:
1. klasyfikuje obiekt,
2. wpisuje typ,
3. wpisuje instancję,
4. wybiera descriptor/implementację.

### 2. Jest druga, niezależna ścieżka materializacji +0x12C
`FUN_08037D00(param_1)` odczytuje:

```
type = object+0x12B
```

i dla typów 1..4 ustawia:

```
object+0x12C = type
```

następnie ponownie dobiera descriptor przez `FUN_08039494`.

To jest ważniejsze niż wcześniejsze stwierdzenie „C064 jest jedynym miejscem ustawiającym instancję”.

Nowy model:

```
classification / setup
        |
        v
+0x12B = type 1..4
        |
        v
FUN_08037D00
        |
        +--> +0x12C = 1..4
        |
        +--> descriptor
```

C064 może wykonać ten etap częściowo już sam, ale D00 pokazuje, że system ma także osobny etap normalizacji/materializacji typu -> instancja.

### 3. +0x12C jest używane bezpośrednio przez cały engine parametrów
`FUN_08036FF2`:
- znajduje parametr w `DAT_08037B4C`,
- dla pierwszej rodziny robi:
  `base + object+0x12C - 1`,
- następnie odczytuje wartość.

`FUN_08037212` robi analogiczne indeksowanie przy zapisie:
`base + object+0x12C - 1`.

`FUN_080370C0` również odczytuje +0x12C i używa go do:
`base + instance - 1`.

Zatem po materializacji +0x12C dalsza warstwa nie potrzebuje wiedzieć, skąd numer instancji pochodzi.

### 4. Konstruktor singletona nadal potwierdza jeden aktywny obiekt
`FUN_08061020`:
- tworzy jeden obiekt pod `param_1 + 0x2A17`,
- wywołuje `FUN_08037CA4`,
- inicjalizuje parametry,
- kończy `FUN_08037E9C`.

`FUN_08037CA4` zeruje:
- +0x129
- +0x12A

`FUN_08037E9C` ustawia:
- +0x128 = 1
- +0x12B = 0
- +0x12C = 1

To nadal wspiera model pojedynczego aktywnego obiektu, którego typ/instancja jest przełączana.

## Konsekwencja dla poszukiwania źródła CO2/CO3/CO4

Nie szukamy już wyłącznie:
`C064 -> +0x12C`.

Musimy znaleźć:
```
param_2
  -> DAT_0803C218[param_2]
  -> class/type 1..4
  -> +0x12B
  -> FUN_08037D00
  -> +0x12C
  -> FUN_08036FF2 / 370C0 / 37212
  -> base + instance - 1
  -> rekord CO1..CO4
```

Najważniejszą luką pozostaje nadal **wartość param_2** oraz zawartość `DAT_0803C218`.

## Negatywny wynik, ale ważny
W całym zdekompilowanym blobie występuje literalnie tylko definicja `FUN_0803C064`; nie ma bezpośredniego wywołania. To potwierdza, że jej wejście pochodzi z mechanizmu pośredniego / function pointer / vtable albo z danych, których Ghidra nie wyemitowała jako kodowego call-site.

Nie będziemy udawać konkretnego caller-a bez odzyskania tej warstwy.

## Następny cel
1. odtworzyć function-pointer/vtable otoczenia klasy z zakresu 0x37C00..0x386xx;
2. powiązać C064 z właściwym slotem callbacku;
3. znaleźć, kto przekazuje `param_2`;
4. odzyskać `DAT_0803C218`;
5. dopiero wtedy mapować klasy 1..4 na konkretne parametry/moduły CO.

## Ważne
Nie wracamy do geometrii UI.
Nie przywracamy wycofanego tropu 0x08042146.
Nie traktujemy 0x2105 jako bezpośredniego settera +0x12C bez dowodu.


## Konsolidacja dalszego trace — 2026-11-19

Potwierdzono wspólną ścieżkę Heating dla klas +0x12B=1..4: FUN_0803E714 -> FUN_0803EFDA(param_1, DAT_0803EEC0+0x62, 0x0C) -> 12 kolejnych 16-bitowych ID -> FUN_08036FF2(context,id) -> widget. Przy +0x158 != 0 dochodzi 11 kolejnych ID z DAT_0803EEC0+0x6E. +0x158 jest osobnym gate'em wariantu/UI, nie numerem obwodu.

Znane rodziny count=4: 0x2032..0x2035 (CH comfort temperature), 0x2048..0x204B (CH eco temperature), 0x2064..0x2067 (CH program). Engine wykonuje base+instance-1, więc mechanizm CO1..CO4 jest rzeczywisty, ale nie dowodzi jeszcze źródła liczby aktywnych obwodów.

DAT_0804107C/08040FC2 sklasyfikowano jako Test I/O (pompy/mieszacze CO1..CO4), nie jako źródło C064. Aktualny brakujący łańcuch: unknown indirect caller/vtable -> C064(param_1,param_2) -> DAT_0803C218[param_2] -> class 1..4 -> +0x12B -> D00 -> +0x12C -> instance-aware engine.

Najcenniejszy brakujący artefakt: surowy eksport 0x0803EEC0..0x0803F008, 0x0803C218..0x0803C283 oraz vtable 0x08038694/98/9C.
