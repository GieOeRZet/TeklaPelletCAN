# BATCH-TRACE-CO-AKTYWACJA-GRANICA-2026-11-19

## Cel
Dalsza rekonstrukcja 1:1 mechanizmu CO1..CO4. Nie wracamy do geometrii. Szukamy rozdzielenia:
- pojemność danych CO = 4,
- liczba aktywnych obwodów,
- konkretny numer instancji +0x12C,
- warunek sprzętowy expansion,
- warunkowe widgety UI.

## 1. Najważniejsza granica: count=4 != aktywacja 4 obwodów
Potwierdzone rodziny:
- 0x2032..0x2035
- 0x2048..0x204B
- 0x2064..0x2067
oraz kolejne grupy count=4 (m.in. 0x2142, 0x2321/2325/2329, 0x4001).

Wniosek implementacyjny:
`count=4` opisuje pojemność/rodzinę czterech rekordów. `+0x12C` wybiera konkretną instancję 1..4. Nie jest to licznik aktywnych obwodów.

## 2. UI ma osobny model dla CO1..CO4
Twardo potwierdzone TypedText:
- 119 = Ogrzewanie obwód 1
- 120 = Ogrzewanie obwód 2
- 121 = Ogrzewanie obwód 3
- 122 = Ogrzewanie obwód 4

To jest dowód pełnego modelu UI, ale nie dowód równoczesnej aktywności.

## 3. 0x10E/0x3505 jest jedynym znalezionym twardym progiem aktywacji UI w FUN_08031CCC
`FUN_08036FF2(context, 0x10E)` jest używane jako:
- >0 -> pierwszy element UI,
- >1 -> drugi element UI.

To nadal NIE dowodzi zapisu +0x12C.

Istotne: ten próg pokazuje architekturę typu:
`parametr konfiguracji -> warunek -> konkretny widget`,
czyli dokładnie warstwę, której szukamy dla CO2..CO4.

## 4. 0x10F/0x2105 ma inną rolę w tym samym callerze
`0x10F -> 0x2105 Heating configuration` trafia do:
- `FUN_0802D3E0(ui, value_10F, value_DC)`
- `FUN_0802D91C(ui, value_10F)`

Nie ma w tym miejscu przejścia do C064 ani zapisu +0x12C.

Dlatego aktualny model:
`2105 -> UI state/configuration`
jest twardy, natomiast:
`2105 -> instance selector`
pozostaje nieudowodnione.

## 5. Najmocniejszy sprzętowy warunek dodatkowych CO
`0x3502 = CH expansion module type` jest polem konfiguracji głównego obiektu.

W `FUN_08000e34` obecność expansion zmienia wybór wariantu:
Main=0, expansion=0:
- profile 1 -> variant 2
- profile 2 -> variant 3
- profile 3 -> variant 4

Main=0, expansion=1:
- profile 1 -> variant 5
- profile 2 -> variant 6
- profile 3 -> variant 7

To jest twardy dowód, że expansion nie jest zwykłą flagą UI: zmienia cały zestaw struktur/wskaźników używany przez firmware.

Dokumentacja systemu dodatkowo opisuje CO1 jako podstawowy obwód oraz CO2..CO4 jako obwody związane z modułem rozszerzeniowym. To jest zgodność architektoniczna, nie zastępuje dowodu z kodu.

## 6. Dodatkowe pola wariantu
- +0x16C1 realnie zmienia wybór struktur:
  - Main=0: 16C1==2 -> +0x199C, inaczej obszar +0x77A0
  - Main=1/2: 16C1==2 -> +0x199C, inaczej obszar +0x7DCC
- +0x16D5 jest osobnym warunkiem:
  - Main=0: ==1
  - Main=1: !=1

Nie wolno utożsamiać 16C1 z 16D5 ani zakładać ich semantyki bez znalezienia źródła.

## 7. C064 nadal pozostaje dispatcherem/klasyfikatorem, nie aktywatorem liczby obwodów
Twardy przepływ:
`param_2 -> DAT_0803C218[param_2] -> class 1..4 -> object+0x12B/+0x12C`.

Dla klas 1..4 +0x12C dostaje 1..4. Potem parametr engine używa:
`base + instance - 1`.

Ale brak bezpośredniego caller-a C064 w aktualnym decompiled.c nadal blokuje przypisanie konkretnego parametru konfiguracyjnego do konkretnej instancji.

## 8. Nowa hipoteza robocza — rozdzielenie odpowiedzialności
Najbardziej spójny obecnie model:
```
hardware/profile:
  3500 + 3502 + 350B + 16C1/16D5
      -> wariant i dostępny zestaw struktur

functional config:
  2105..2108
      -> stan/konfiguracja funkcji systemu

activation/UI:
  parametr -> warunek -> widget CO1..CO4

instance:
  C064/C218 -> +0x12B/+0x12C
      -> base + instance - 1
      -> statyczny rekord CO1..CO4
```

Nie zakładamy jeszcze jednego wspólnego miejsca łączącego te cztery warstwy.

## 9. Najbliższy cel kodowy
Priorytet:
1. odzyskać `DAT_0803C218` i znaleźć wpisy mapujące konkretne `param_2` na klasy 1..4;
2. odzyskać `DAT_0804107C`, ale nadal traktować ją jako Test I/O;
3. znaleźć wszystkie caller-y/pośrednie wskaźniki do C064;
4. znaleźć kodowe użycia 0x110/0x111/0x114, jeśli występują przez tabelaryczny/generic engine;
5. znaleźć źródła +0x16C1/+0x16D5;
6. dopiero po tym zamknąć most `2105 -> liczba aktywnych CO`.

## 10. Kryterium dowodu
Nie uznajemy za zamknięte:
- 2105 = liczba CO,
- 3505 = liczba CO,
- 3502 = liczba CO,
- C064 = aktywator CO,
dopóki nie znajdziemy konkretnego przepływu danych/instrukcji.

Za zamknięte uznajemy już:
- maksymalnie 4 rekordy/instancje w rodzinach CO,
- +0x12C = numer konkretnej instancji,
- osobny model UI CO1..CO4,
- 0x10E jako realny próg aktywacji elementów UI,
- 0x2105 jako wejście do stanu/grafiki UI,
- 3502 jako element wyboru wariantu sprzętowego.
