# KOTŁY — PRAWDZIWE BITMAPY VS RENDER MOCKUPU — 2026-11-19

## Korekta po renderze

Poprzedni render wygenerowany przez model graficzny **NIE był zbudowany z bitmap 011/012/013/014 ani z żadnego wyciętego assetu FW**. Był interpretacją na podstawie opisu. Nie wolno używać jego wyglądu jako dowodu zawartości FW2213TK.

To jest ważna korekta metodologiczna.

## Twardy dowód: prawdziwe grafiki kotłów są już w wyciągniętym pakiecie

Repo ma:
- 011.png — 105x126
- 012.png — 108x141
- 013.png — 82x145
- 014.png — 54x100

Dokumentacja bitmap mówi, że pliki `web/img/panel/NNN.png` są dekodowane z tablicy bitmap firmware pod `0x54450`. Zatem 011–014 **nie są dodatkowymi grafikami znalezionymi poza 188 rekordami**. Są częścią wyciągniętego pakietu oryginalnych bitmap.

W repo kod karty ładuje je jako oryginalne grafiki panela.

## Bardzo ważna rozbieżność: numeracja FW vs numeracja karty

Firmware ma parametr:
- `0x370A = Boiler image selector`
- typ `u8`
- min `1`
- max `3`
- default `1`
- RAM `0x20021FA6`
- rejestracja pod `0x0801AB7E`.

Natomiast obecna karta webowa ma własny wybór:
- `boiler_image = 11 / 12 / 13 / 14`
- domyślnie 13,
- i bezpośrednio ładuje `011.png / 012.png / 013.png / 014.png`.

**Nie wolno jeszcze utożsamiać tych numeracji.**

Najbardziej interesująca hipoteza do sprawdzenia:
```
FW 0x370A: 1..3
        ↓
  firmware selector / wariant
        ↓
mapowanie na bitmapę 011..014
```

Możliwe jest też, że:
- 0x370A wybiera tylko 3 klasy grafiki,
- jedna z nich jest bazowa,
- 11..14 są indeksami bitmap wewnątrz kilku klas/komponentów,
- albo webowa numeracja 11..14 jest niezależnym mapowaniem ręcznym.

Na obecnym etapie żadnej z tych wersji nie uznajemy za fakt.

## Co z grafiką z ostatniego renderu?

Grafika z renderu:
- została wygenerowana od zera,
- nie została przekazana modelowi jako referencja bitmapy,
- nie pochodzi z `011.png`, `012.png`, `013.png` ani `014.png`,
- dlatego jej podobieństwo do rzeczywistej grafiki kotła **nie jest dowodem** na obecność dodatkowego assetu w FW.

Jeżeli wizualnie przypomina jedną z prawdziwych grafik, jest to przypadkowa zbieżność/interpretacja modelu.

## Nowy bardzo mocny trop

W `web/teklapelletclassic-engine.js` istnieje jawny mechanizm:
- pakiet `img/panel/NNN.png` opisany jako „numery jak w tablicy bitmap FW panela”,
- `T.boiler = U([11, 12, 13, 14].includes(...)`,
- `T.burner = U(17)`,
- `boiler_image` steruje wyborem konkretnej bitmapy.

To daje nam możliwość odtworzenia **prawdziwego** wyglądu kotła bez generowania grafiki.

## Priorytet dalszej analizy

1. Znaleźć w firmware wszystkie odwołania do bitmap 11/12/13/14.
2. Znaleźć miejsce, gdzie `0x370A` wpływa na wybór grafiki.
3. Ustalić mapowanie `370A=1/2/3` -> konkretna bitmap ID.
4. Ustalić, czy 011–014 są czterema modelami kotła, czy częścią innego mechanizmu wariantowania.
5. Odtworzyć ekran Home z **oryginalnych bitmap**, TypedText i realnej geometrii; żadnych wygenerowanych ilustracji.

## Wniosek

Na razie **nie mamy dowodu na „grafiki poza 188”**.

Mamy natomiast coś znacznie lepszego: twardy dowód, że wśród wyciągniętych bitmap istnieją cztery konkretne grafiki kotła (011–014), a firmware posiada osobny parametr `Boiler image selector`. Teraz trzeba połączyć te dwa końce kodem firmware.
