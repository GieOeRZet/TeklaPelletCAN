# BATCH — HOME / HEADER 4A114 + REAL FIRMWARE BITMAP 014 — 2026-11-19

## 1. 4A114 — twardo rozpoznany jako złożony komponent status/header, nie cały Home

FUN_0804A0E4 ustawia vptr DAT_0804A0F4.
FUN_0804A114 jest metodą tego obiektu i tworzy/konfiguruje wiele childów. FUN_0804A510 dodaje do parenta:
+0x78, +0x11C, +0xD8, +0x17C, +0x1B0, +0xA4, +0x1E4, +0x23C (warunkowo), +0x210.

To daje co najmniej 8/9 childów. Komponent dobrze pasuje do bogatego status/header, ale nie wolno utożsamiać go z całym Home.

### Twarde zasoby/geometry w 4A114
- +0x48: X=0, Y=0, W=480, H=272
- +0x78: Bitmap ID 0x4F = asset 079.png, rozmiar 480x45
- +0x1E4: Bitmap ID 0x5B = asset 091.png, rozmiar 39x23; pozycja X=390, Y=9
- +0x210: Bitmap ID 0xA2 = asset 162.png, rozmiar 23x21; pozycja X=350, Y=10
- +0x23C: TypedText 0x1C6 = ID 454; geometria X=439, Y=0, W=40, H=30
- +0xD8: resource/bitmap-like ID 0x26, geometria dynamiczne X, Y=10, W=130, H=20; później wybór ID 0x26..0x31 zależny od FUN_08037DEC() i module+299.

079.png jest dodatkowo potwierdzone w implementacji webowej jako .h2 — tło górnego nagłówka o wysokości 45 px. To jest niezależna zgodność z layoutem.

## 2. Ważna korekta: 4A114 nie jest grafiką kotła

+0x23C używa TypedText 454 = „Próg zmniejszania stopnia mocy [%]” według istniejącej dokumentacji tekstów. To dowodzi, że 4A114 jest komponentem używanym w kontekście bardziej ogólnego statusu/struktury UI, a nie wyłącznie ekranem Home.

Wiele kolejnych funkcji 4E7A4, 4FF64, 50220, 504DC, 50798, 50AAC, 50D68, 51024, 512E0 powtarza praktycznie ten sam layout i różni się dalszym helperem. Wygląda to na rodzinę wariantów tego samego komponentu.

Nie używamy 4A114 jako dowodu lokalizacji grafiki kotła.

## 3. Realny ślad bitmapy kotła — FUN_080469E8

Znaleziono osobny widget FUN_080469E8.
- tworzy child bitmap pod +0x4F
- FUN_080307BC(..., 0x0E) ustawia bitmap ID 14
- asset 014.png ma rozmiar 54x100
- bitmapa jest ustawiona na Y=20
- obiekt nadrzędny ma rozmiar około 70x150
- pod bitmapą znajdują się kolejne TypedText/elementy.

To jest pierwszy twardy dowód, że bitmapa 014.png jest faktycznie osadzana przez oryginalny firmware w widgetcie UI, a nie jest tylko artefaktem webowej rekonstrukcji.

FUN_0803E34C tworzy cztery instancje FUN_080469E8 pod kolejnymi rekordami. To bardzo silnie sugeruje komponent wieloelementowy, ale bez dodatkowego dowodu nie przypisujemy go jeszcze do głównego ekranu.

## 4. Znaczenie dla 370A

Mamy dwa niezależne fakty.

A. 0x370A:
- Boiler image selector
- u8, zakres 1..3
- RAM 0x20021FA6
- callback/rejestracja 0x0801AB7E

B. Oryginalny FW faktycznie używa assetu 014.png:
- FUN_080469E8
- FUN_080307BC(..., 0x0E).

Ale nadal nie mamy bezpośredniego połączenia 370A -> 11/12/13/14. Tego nie dopisujemy jako faktu.

## 5. Następny właściwy tor

1. prześledzić wszystkie instancje FUN_080469E8 i funkcje aktualizujące ich bitmapę/visibility,
2. znaleźć miejsca, gdzie bitmap ID 11/12/13/14 pochodzi z tabeli albo wartości parametru,
3. prześledzić 0x0801AB7E / RAM 0x20021FA6 do UI,
4. równolegle rozebrać prawdziwy root FUN_0803E5AC po childach, ale tylko przez twarde bitmap/TypedText/geometry/callback evidence,
5. dopiero wtedy przypisać konkretny widget do grafiki kotła na screenshotcie.

## 6. Zasada dowodowa

Nie utożsamiamy bitmapy 014 z głównym ekranem tylko dlatego, że wygląda jak kocioł; 4A114 z Home tylko dlatego, że ma 480x272; ani sześciu elementów 47290 z dolnym paskiem tylko dlatego, że liczba się zgadza.

Wymagane jest połączenie: root -> child -> resource -> geometry -> state/parameter/callback.