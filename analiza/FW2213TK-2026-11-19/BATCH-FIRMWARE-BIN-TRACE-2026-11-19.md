# BATCH-FIRMWARE-BIN-TRACE-2026-11-19

## Zakres
Analiza dotyczy cały czas binarnego firmware panelu TOUCH FW2213TK, a nie implementacji odtwórczej. Canonical source: firmware/FW2213TK-ghidra/decompiled.c + functions.txt.

## Ważna korekta po weryfikacji
W trakcie ponownego sprawdzenia wyszukiwania repo nie potwierdziło twierdzenia, że istnieje bezpośredni przepływ:
`0x2105 -> FUN_08037D00`.

Nie traktujemy tego jako faktu. Potwierdzone pozostaje tylko:
- 0x2105 jest parametrem używanym przez UI w FUN_08031CCC,
- FUN_08037D00 operuje na module+0x12B i dla typów 1..4 materializuje +0x12C,
- brak bezpośredniego call-site FUN_08037D00 w obecnym decompiled.c.

To rozdziela dowody od wcześniejszych skrótów interpretacyjnych.

## Co jest obecnie twarde

### C064
`FUN_0803C064(param_1,param_2)`:
`class = DAT_0803C218[param_2]`

Dla klas 1..4:
- +0x12B = class
- +0x12C = class

Następnie wybierany jest descriptor przez FUN_08039494.

### D00
`FUN_08037D00` czyta +0x12B.
Dla wartości 1..4 ustawia +0x12C odpowiednio 1..4 i dobiera descriptor.
To potwierdza osobny etap normalizacji typu -> instancja.

### Engine
+0x12C jest używane przez:
- FUN_08036FF2
- FUN_080370C0
- FUN_08037212

jako indeks instancji `base + instance - 1`.

### CO1..CO4
Statyczne rekordy:
- 2032..2035
- 2048..204B
- 2064..2067

Nie szukamy już dynamicznego tworzenia CO2..CO4.

### UI
TypedText 119..122 odpowiada CO1..CO4.
0x10E ma potwierdzone progi >0 i >1 w FUN_08031CCC.
0x2105 jest wejściem do D3E0/D91C w tym callerze, ale nie mamy jeszcze dowodu, że wybiera instancję.

## Najważniejsza luka
Brakuje:
1. zawartości DAT_0803C218 (108 B),
2. rzeczywistego wejścia/callbacku do C064,
3. wartości param_2,
4. źródła +0x12B w runtime dla ścieżki CO,
5. mostu między konfiguracją funkcjonalną a wyborem instancji.

## Kierunek dalszej analizy
Skupiamy się na binarnym kodzie i strukturach:
- okolice 0x37C00..0x386xx,
- tabele wskaźników / vtable,
- konstruktor i inicjalizacja obiektu,
- wszystkie zapisy do +0x12B,
- wszystkie zapisy do +0x12C,
- DAT_0803C218,
- następnie mapowanie param_2 -> class 1..4.

Nie wracamy do geometrii UI i nie zakładamy 2105=C064 bez instrukcji/call-chain.
