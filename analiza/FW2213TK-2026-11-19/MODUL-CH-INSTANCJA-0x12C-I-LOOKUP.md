# FW2213TK — moduły CH i indeksowanie instancji, 2026-11-19

## Nowe ustalenia z firmware

### 1. Obiekt modułu ma własne pole instancji
W konstruktorze runtime/raw 0x08047CA4 / raw 0x37CA4:
- `module+0x108` jest zerowane,
- `module+0x128`: bajty początkowo `1,0,0`,
- `module+0x158` = 0,
- później kod modułu ustawia `module+0x12C`.

### 2. +0x12C jest ustawiane jawnie na 1..4
Runtime/raw 0x08048130 / raw 0x38130:
- wejściowe `r1` jest normalizowane do 1..4,
- `module+0x11F` dostaje typ zależny od tej wartości,
- `module+0x12C = r1`, a wartości >=5 są zamieniane na 4.

To jest bezpośredni dowód firmware, że `+0x12C` przechowuje numer instancji modułu 1..4.

### 3. Dynamiczny lookup parametru używa tego numeru
Runtime/raw 0x080470C0 / raw 0x370C0:
- globalny stan pod `0x200248D4` przechowuje flagę inicjalizacji i bajt instancji,
- przy pierwszym użyciu pobierane jest `module+0x12C`,
- lookup wykonuje dokładnie:
  `lookup_index = base_CAN_index + instance - 1`.

Przykład:
- baza `0x2032`, instancja 1 -> `0x2032`
- instancja 2 -> `0x2033`
- instancja 3 -> `0x2034`
- instancja 4 -> `0x2035`.

### 4. Tabela mapowania parametrów zawiera bazę + ID panelu
W okolicy raw 0x37B48:
- (168, 0x22FD)
- (169, 0x2032)
- (170, 0x2048)
- (171, 0x2166)
- (172, 0x2064)
- itd.

Pierwsze pole jest używane jako ID wejściowe lookupu, drugie jako bazowy indeks CAN. Dla CO temperatura komfortowa: ID 170 -> baza 0x2032.

### 5. Rejestracja pojedynczego rekordu nadal ma 0x2C
Runtime/raw 0x0802143C / raw 0x1143C:
- tabela rekordów: baza przekazana przez caller,
- rekord = 0x2C bajtów,
- `record+0x08` = CAN/index,
- `record+0x0C` = źródło/pointer przekazane w r2,
- `record+0x14`, `+0x1C`, `+0x24` = 5-bajtowe deskryptory kopiowane przez helper 0x14728.

## Ważna granica dowodu

Nadal NIE ma dowodu, że RAM dla CO2 jest stałym przesunięciem względem CO1.

Nie znaleziono statycznej rejestracji literalnych `0x2033`, `0x2034`, `0x2035` przez bezpośrednie wywołania 0x1143C. Dlatego nie wpisujemy jeszcze żadnego adresu RAM CO2 jako pewnika.

## Następny cel

Trace inicjalizacji modułu rozszerzeń CH:
- runtime/raw 0x08047Cxx–0x080483xx,
- runtime/raw 0x080493xx–0x08049xxx,
- pola `module+0x128/+0x12A/+0x12C/+0x158`,
- miejsce, w którym dla instancji 2/3/4 pojawia się rzeczywisty rekord/source pointer dla indeksów `0x2033...`.

