# FW2213TK – dokładny trace wyboru wariantu 0x3500/0x3502/0x350B

Data: 2026-11-19

## Nowy twardy dowód

W funkcji inicjalizacyjnej zaczynającej się w okolicy 0x08000E?? firmware najpierw wywołuje `FUN_08001AE4()`, a następnie pobiera:

- `object + 0x16BF` jako `cVar1` = Main module type,
- `object + 0x16CC` jako `pcVar21` = Profile number,
- `object + 0x16C0` = CH expansion module type.

Kod nie tylko odczytuje te pola. Używa ich do indeksowania zestawów 8-elementowych struktur.

### Main module type

Dla `main_module_type == 1 || 2` kod wchodzi do gałęzi, gdzie:

- przy expansion != 0 dla typu 1 wybierany jest wariant `iVar14 = 1`;
- dla typu 2 również ustawiany jest wariant `iVar14 = 1`;
- dla typu 0 wybór zależy od expansion + profile.

### Main module type == 0

Dla expansion == 0:

```
profile == 1 -> iVar14 = 2
profile == 2 -> iVar14 = 3
profile == 3 -> iVar14 = 4
```

Dla expansion == 1:

```
profile == 1 -> iVar14 = 5
profile == 2 -> iVar14 = 6
profile == 3 -> iVar14 = 7
```

Następnie `iVar14` jest używany do pobierania wielu elementów z tablic:

```
local_48[iVar14]
local_68[iVar14]
local_88[iVar14]
local_a8[iVar14]
local_c8[iVar14]
local_e8[iVar14]
local_108[iVar14]
local_128[iVar14]
local_148[iVar14]
local_168[iVar14]
local_188[iVar14]
local_1a8[iVar14]
local_1c8[iVar14]
local_1e8[iVar14]
local_208[iVar14]
local_228[iVar14]
local_248[iVar14]
local_268[iVar14]
local_288[iVar14]
local_2a8[iVar14]
local_2c8[iVar14]
local_2e8[iVar14]
local_308[iVar14]
local_328[iVar14]
```

To jest bardzo mocny dowód, że wybór Main I/O + expansion + profile wybiera **cały pakiet konfiguracji**, a nie pojedynczy parametr.

## Ważna obserwacja

`0x3501 Autoconfig activation` nie występuje literalnie w obecnym `decompiled.c`. Z kolei 0x3500/0x3502/0x350B są rejestrowane bezpośrednio przez:

```
FUN_0801143c(..., 0x3500, object+0x16BF, ...)
FUN_0801143c(..., 0x3502, object+0x16C0, ...)
FUN_0801143c(..., 0x350B, object+0x16CC, ...)
```

Dlatego nie wolno jeszcze twierdzić, że 0x3501 steruje właśnie tą funkcją.

## Konsekwencja dla hipotezy BIG I/O

Hipoteza o BIG I/O jako głównym module robi się bardzo mocna strukturalnie:

```
Main module type
      +
CH expansion module type
      +
Profile number
      |
      v
wybór jednego z 8 profili struktur
      |
      v
konkretne zestawy wskaźników / obiektów
      |
      v
dalsza inicjalizacja funkcji panelu
```

Nie znamy jeszcze mapowania:

```
iVar14 0..7 -> fizyczna konfiguracja Tekli
```

i nie należy go zgadywać.

## Co nadal trzeba znaleźć

1. Skąd ładowane są wartości `+0x16BF/+0x16C0/+0x16CC`.
2. Gdzie dokładnie działa `0x3501 Autoconfig activation`.
3. Czy `0x2105 Heating configuration` jest używany przed wyborem wariantu, po nim, czy w zupełnie innej warstwie.
4. Który z 24 zestawów danych odpowiada za obiekty CO1..CO4.
5. Czy wybór profilu wpływa na utworzenie modułów z `+0x12C = 1..4`.

## Status

**PEWNE:** 0x3500/0x3502/0x350B są aktywnymi wejściami do wyboru całego wariantu konfiguracji.

**PEWNE:** expansion module zmienia wybór profilu dla Main module type 0.

**PEWNE:** wybrany indeks wpływa na dziesiątki pól/struktur obiektu.

**NIEPEWNE:** znaczenie konkretnych profili 1..7 w dokumentacji Tekli.

**NIEPEWNE:** bezpośrednie połączenie 0x2105 z tym mechanizmem.
