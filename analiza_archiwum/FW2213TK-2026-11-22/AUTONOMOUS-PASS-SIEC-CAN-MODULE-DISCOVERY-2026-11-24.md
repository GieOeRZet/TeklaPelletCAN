# PASS — KOREKTA SIEĆ / CAN MODULE DISCOVERY — 2026-11-24

## Decyzja

Ekran `SIEĆ` `0x808f770` traktujemy jako **dynamiczną listę podłączonych modułów CAN**, a nie jako ekran wartości PID.

To jest zgodne zarówno z firmware, jak i z dokumentacją producenta: instrukcja instalatora igneoTouch opisuje punkt 4.14 jako ekran, który „wyświetla stan podłączonych modułów sieci CAN”. Nie należy więc próbować mapować czterech kolumn wiersza na zwykłe PID-y kotła.

## Twarde fakty z firmware

### Tablica nazw węzłów

Firmware posiada tablicę nazw zależną od Node-ID:

- 0x05 = SLAVE 1
- 0x06 = SLAVE 2
- 0x07 = SLAVE 3
- 0x08 = RADIO GATEWAY
- 0x40..0x47 = CAN IO 0..7
- 0x50 = MODUL LAMBDA
- 0x51 = IO BOARD PRO
- 0x54/0x55 = FLOWMETER 1/2
- 0x56 = CAN IO BIG
- **0x57 = CAN IO BIG**
- 0x5A = VIDE GSM
- 0x5B = VIDE NET WIFI
- 0x5C = VIDE NET
- 0x64..0x67 = VIDE ROOM 1..4
- 0x6E..0x75 = CAN GATEWAY 0..7
- 0x78..0x7F = CAN IO MINI 0..7
- pozostałe = UNKNOWN

Istotna korekta: wcześniejszy katalog `can_node_names.csv` nie zawierał 0x57. Kod/obiekty runtime już wcześniej wykazały, że **0x56 i 0x57 są obsługiwane jako CAN IO BIG**. Katalog został poprawiony.

Commit korekty:
`8ee8df8d60268e8ececb8ef5e6f660dc0e9d8572`

### Dlaczego BIG może dawać dwa wpisy

PASS 64 wykazał dwa identyfikatory obsługiwane przez obiekty CAN IO BIG: `0x56` oraz `0x57`.

To dokładnie pasuje do obserwacji właściciela, że przy samym CAN IO BIG na ekranie SIEĆ pojawiają się dwa wpisy.

**Wniosek FACT/STRONG:** nie są to dwa różne typy urządzeń. Firmware traktuje oba Node-ID jako CAN IO BIG.

### Jak wykrywane są urządzenia

PASS 43 wykazał:

- heartbeat: `0x701..0x77F`
- odpowiedzi SDO: `0x581..0x5FF`
- skan identyfikacji: `0x600 + node`
- zapytanie:
  `40 18 10 02`
  czyli CANopen SDO odczyt `0x1018:02`.

To oznacza, że panel ma mechanizm wykrywania obecności i identyfikacji urządzeń CANopen.

## ESP32 / UNKNOWN

Nie będziemy zakładać, że ESP jest „VIDE GSM” tylko dlatego, że aktualny projekt używa Node-ID 0x5A.

Jeżeli ESP32 pojawi się na magistrali jako Node-ID, dla którego firmware nie ma wpisu w tablicy nazw, ekran SIEĆ ma naturalny stan **UNKNOWN**.

Jeżeli ESP32 zostanie ustawiony na Node-ID istniejącego typu, np. `0x5A`, panel może zaklasyfikować go jako **VIDE GSM**, ale to nadal nie dowodzi, że zachowanie urządzenia jest 1:1 — trzeba sprawdzić również heartbeat, IDENT/0x1018 oraz dalszy ruch CAN.

Jeżeli chcemy zrobić prawdziwą replikę VIDE NET WIFI, właściwym kierunkiem jest:
- Node-ID `0x5B`
- heartbeat jak oryginalny moduł
- odpowiedź na wymagane zapytania CANopen/IDENT
- właściwe Object Dictionary / PDO
- dopiero potem ekran INTERNET i jego konfiguracja.

## Cztery kolumny SIEĆ

Obecny inwentarz UI pokazuje cztery pola w każdym wierszu:

1. x=15, szer. 135
2. x=150, szer. 110
3. x=260, szer. 80
4. x=340, szer. 90

oraz 8 wierszy.

**Nie zamykamy jeszcze semantyki tych czterech pól.**

Do rozwiązania 1:1 należy odtworzyć jeden konkretny moduł przez emulację jego ruchu CAN i obserwować:
- który wiersz się pojawia,
- jakie cztery teksty się pojawiają,
- które ramki powodują ich zmianę,
- co dzieje się po timeout/offline,
- co dzieje się po odpowiedzi na IDENT,
- jak wersja urządzenia jest pobierana.

## Nowy test akceptacyjny SIEĆ

Przygotować automatyczny scenariusz:

### T0
Pusta magistrala.
Oczekiwane:
- brak wpisów,
- brak zmian w 8 wierszach.

### T1
Jeden węzeł:
- Node-ID 0x56
- heartbeat
- IDENT
- minimalne odpowiedzi wymagane przez panel.

Oczekiwane:
- dokładnie jeden wpis 0x56.

### T2
Dodać Node-ID 0x57.

Oczekiwane:
- drugi wpis **CAN IO BIG**.

To jest kluczowy test potwierdzający obserwację właściciela.

### T3
Dodać 0x40, 0x45, 0x5A, 0x5B, 0x64.

Oczekiwane:
- każdy nowy moduł tworzy kolejny wpis,
- nazwa odpowiada tablicy Node-ID,
- kolejność/pozycja zostaje zmierzona.

### T4
Node-ID spoza tablicy.

Oczekiwane:
- **UNKNOWN**, jeśli firmware rzeczywiście używa fallbacku tablicy nazw.

### T5
Ten sam Node-ID bez heartbeat / z timeoutem.

Oczekiwane:
- dokładny sposób usuwania/oznaczania wpisu.

## INTERNET — konsekwencja

SIEĆ i INTERNET należy badać razem.

`0x5B = VIDE NET WIFI` jest jednym z oficjalnych typów modułu. Ekran INTERNET nie implementuje lokalnego Wi-Fi panela; panel komunikuje się z modułem CAN.

Dlatego test klawiatury SSID/PASSWORD musi być wykonany nie tylko jako zmiana PID, ale również z obserwacją zachowania wirtualnego modułu 0x5B:
- jakie zapytania panel wysyła,
- czy zapis idzie przez 0x584,
- czy moduł odpowiada ACK/SDO/PDO,
- kiedy status WiFi zmienia się na ekranie.

## Źródło producenta

Oficjalna instrukcja instalatora igneoTouch:
`InstrukcjaTeklaPelletInstalator_PL.pdf`, rozdział 4.14.

Producent definiuje tam SIEĆ jako ekran stanu podłączonych modułów sieci CAN.

## Status

SIEĆ:
- geometria: FACT
- lista typów Node-ID: FACT
- 0x56 + 0x57 jako CAN IO BIG: FACT/STRONG z kodu runtime
- UNKNOWN fallback: FACT-STATIC z tablicy, dynamiczne zachowanie jeszcze do testu
- kolejność wpisów: OPEN
- cztery pola wiersza: OPEN
- timeout/usuwanie wpisu: OPEN

Następny krok nie jest „zgadywaniem PID-ów”, tylko **emulacja modułów CAN i odtworzenie listy SIEĆ 1:1**.
