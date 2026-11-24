# BATCH-TYPE-INSTANCE-0x12B-0x12C-2026-11-19

## Nowy twardy wynik z binarki FW2213TK

W bezpośrednim kodzie `FUN_08037D00` i `FUN_0803C064` pola są używane konsekwentnie jako:

- offset 299 decimal = `0x12B` = **typ/rodzaj obiektu**
- offset 300 decimal = `0x12C` = **instancja**

### D00
`FUN_08037D00(param_1)`:
- czyta `param_1+0x12A` jako tryb wariantu,
- następnie switchuje po `param_1+299`,
- dla typów 1,2,3,4 ustawia lokalne `uVar1=1..4`,
- zapisuje `param_1+300 = uVar1`,
- dobiera descriptor przez `FUN_08039494`.

Czyli D00 nie tworzy numeru CO z 2105; wykonuje normalizację już istniejącego typu obiektu.

### C064
`FUN_0803C064(param_1,param_2)`:
`class = DAT_0803C218[param_2]`

Dla class 1..4:
- pobiera singleton przez `FUN_080314BA()`,
- ustawia `object+299 = class`,
- ustawia `object+300 = class`,
- dobiera descriptor.

To jest jeszcze mocniejszy dowód, że C064 jest klasyfikatorem/dispatcherem, który może ustawić typ i instancję równocześnie.

### Co ważne
C064 nie jest jedynym miejscem ustawiającym te pola. W kodzie występują także jawne wyspecjalizowane ścieżki ustawiające +0x12B na:
0, 5, 6, 7, 8, 9, 10, 0x10, 0x11, 0x13 oraz ścieżki 1..4.

To definitywnie odsuwa interpretację `+0x12B = numer CO`.
To jest enum typu obiektu/modułu, którego wartości 1..4 mają dodatkowo znaczenie instancyjne w mechanizmie parametrów.

## Nowa architektura
```
param_2
  -> DAT_0803C218[param_2]
  -> class/type
  -> object+0x12B = type
  -> object+0x12C = instance
  -> descriptor
  -> FUN_08036FF2 / 370C0 / 37212
  -> base + instance - 1
```

## Vtable
`FUN_08037CA4` ustawia pierwszy word obiektu na `DAT_08038694`, a następnie ponownie na `DAT_0803869C`. To potwierdza realną warstwę polimorficznego obiektu/vtable w tym module.

`FUN_08037C1E` i `FUN_08037C70` wykonują jawne wywołania przez vtable, np. sloty +0x04, +0x08, +0x0C, +0x10, +0x14 i +0x28.

Brakujące dane binarne `DAT_08038694/98/9C` i `DAT_0803C218` nadal nie są zawarte w tekstowym decompiled.c. Ich odzyskanie wymaga pamięci/bin eksportu z Ghidra albo surowego BIN.

## Wniosek dla dalszego trace
Nie szukamy już pytania „czy +0x12C jest instancją?”. Jest to potwierdzone.

Teraz trzeba znaleźć:
1. kto wywołuje metodę/dispatcher ustawiający +0x12B,
2. jaki parametr daje `param_2`,
3. jakie wartości ma DAT_0803C218,
4. które wpisy prowadzą do class 1..4,
5. następnie połączyć te wpisy z aktywacją CO1..CO4.

Nie wolno przypisywać 2105 do tego łańcucha bez konkretnego call-site'u w binarce.
