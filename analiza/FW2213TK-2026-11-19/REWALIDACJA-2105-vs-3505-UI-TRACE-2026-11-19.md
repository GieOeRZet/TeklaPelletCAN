# FW2213TK — rewalidacja 0x2105 vs 0x3505 po pełnym trace UI

Data: 2026-11-19

## Najważniejsza korekta

Po ponownym przejściu przez cały dostępny `decompiled.c` nie wolno traktować `0x3505 / panel 0x10E` jako liczby obwodów CO.

Mapa panelu:
- panel 0x10E -> CAN 0x3505
- panel 0x10F -> CAN 0x2105

W katalogu firmware:
- 0x3505 = Outside temperature sensor configuration, u8, 0..2
- 0x2105 = Heating configuration, u8, 0..4

## Twardy trace panel 0x10E / 0x3505

W `FUN_08031CCC` parametr 0x10E jest używany wyłącznie w logice UI:

```
iVar7 = FUN_08036FF2(context, 0x10e);
FUN_0802d3bc(ui, 0 < iVar7, value);

iVar7 = FUN_08036FF2(context, 0x10e);
FUN_0802d3ce(ui, 1 < iVar7, value);
```

Czyli wartość 0x10E jest używana jako progowanie dostępności dwóch elementów UI (>0 i >1).

Niezależnie katalog firmware mówi, że CAN 0x3505 to konfiguracja czujnika temperatury zewnętrznej, zakres 0..2.

Wniosek: 0x3505 nie jest licznikiem CO.

## Twardy trace panel 0x10F / 0x2105

W tej samej funkcji:

```
uVar8 = FUN_08036FF2(context, 0xdc);
uVar1 = FUN_08036FF2(context, 0x10f);
FUN_0802d3e0(ui, uVar1, uVar8);

uVar1 = FUN_08036FF2(context, 0x10f);
FUN_0802d91c(ui, uVar1);
```

0x10F steruje stanem/obrazem dwóch elementów UI:
- `FUN_0802d3e0` ustawia flagi widoczności/aktywności i odświeża widget,
- `FUN_0802d91c` wybiera dwa warianty grafiki/elementu zależnie od zera/niezera.

W całym dostępnym decompiled.c literalny indeks panelowy 0x10F występuje tylko w tych miejscach. Nie znaleziono bezpośredniego kodu typu:
`0x10F -> loop 1..N -> create CO objects`.

## Co nadal pozostaje mocne

0x2105 pozostaje najlepszym kandydatem na parametr funkcjonalny związany z konfiguracją liczby obwodów, ponieważ:
- ma zakres 0..4,
- nazywa się w firmware `Heating configuration`,
- dokumentacja instalatora opisuje osobną pozycję „Ilość obwodów grzewczych” jako określającą ilość obwodów CO,
- firmware ma mechanizm czterech instancji CO1..CO4.

Dokumentacja producenta dodatkowo pokazuje profile BIG:
- Profil 1 = CO + CWU + Bufor,
- Profil 2 = CO1 + CO2 + CWU,
- Profil 3 = CO1 + CO2 + CWU + Bufor.

To oznacza, że warstwa profilu sprzętowego i warstwa „ilość obwodów” nie powinny być automatycznie utożsamiane.

## Aktualny model

```
0x3505 / 0x10E
    -> konfiguracja czujnika zewnętrznego
    -> progowanie elementów UI

0x2105 / 0x10F
    -> Heating configuration
    -> bezpośrednio widoczny w UI
    -> brak znalezionego bezpośredniego fan-out do tworzenia obiektów

0x3500 / 0x3502 / 0x350B
    -> wybór wariantu sprzętowego
    -> zestaw struktur/pointerów

wariant / moduły
    -> obiekty modułów
    -> +0x12B = typ/klasyfikacja
    -> +0x12C = instancja 1..4
    -> base + instance - 1
    -> rekordy CO1..CO4
```

## Następny cel

Nie szukamy już „czy 0x3505 jest countem” — odpowiedź brzmi: nie.

Szukamy teraz kodowego fan-out:
`0x2105 -> warstwa konfiguracji -> aktywacja/dezaktywacja obiektów CO`

oraz równolegle źródła `param_2` dla `FUN_0803C064`.

Status:
- 0x3505 jako count CO: ODRZUCONE.
- 0x2105 jako konfiguracja ogrzewania: POTWIERDZONE jako parametr UI, ale nadal nieudowodnione jako bezpośredni konstruktor instancji.
- mechanizm CO1..CO4: POTWIERDZONY niezależnie.
