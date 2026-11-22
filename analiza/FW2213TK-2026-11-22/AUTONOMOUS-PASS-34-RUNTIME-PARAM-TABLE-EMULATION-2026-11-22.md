# AUTONOMOUS PASS 34 — RUNTIME PARAMETER TABLE (655 REKORDÓW) Z EMULACJI STARTUPU — 2026-11-22

Firmware: FW2213TK_kopia.bin, SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071` (zweryfikowany przez narzędzie).
Adresy: RAW → PROJECT `+0x08000000` → RUNTIME `+0x10000`. Poniżej podaję PROJECT, a w nawiasie RUNTIME tam, gdzie to istotne dla emulatora.

## 0. Cel i metoda
Zamknąć zadania 1–4, 6 z promptu (struktura `0x200208EC`, tabela `runtime key → storage → type → metadata`, wywołania `0x0801143C`/`0x080115F6`, powiązanie key 3 z katalogiem).
Zamiast odtwarzać rejestracje statycznie (448 miejsc wywołania), **uruchomiono prawdziwy startup firmware w emulatorze** (Unicorn, Thumb/M-class)
i odczytano tabelę manager’a `0x20008D84` z RAM po inicjalizacji. Narzędzia: `tools/emu_startup.py`, `tools/runtime_param_table.py`,
`tools/resolver_tables.py`, `tools/bl_xref.py`, `tools/disasm_thumb.py` (patrz `NewEstyma/03_TOOLING.md`).

Co emulator robi (i czego NIE robi): wykonuje startup od reset vectora, stubuje `RCC_GetFlagStatus` (RUNTIME `0x08028AE4` → 1), NOP-uje trzy pętle RCC,
a `svc #0` (`vPortStartFirstTask`, RUNTIME `0x08068198`) odtwarza ręcznie (wczytanie kontekstu z `pxCurrentTCB`), po czym wykonuje kod
pierwszego zadania FreeRTOS (`0x08072C95`). Przerwania, kolejne zadania i peryferia NIE są modelowane. Inicjalizacja parametrów wykonuje się
w tej ścieżce w całości: **655 wywołań `0x0801143C` (PROJECT; RUNTIME `0x0802143C`)** — tyle, ile rekordów tabeli.
BIN ma **448** miejsc wywołania (`tools/bl_xref.py`); 655 > 448, bo część miejsc wykonuje się wielokrotnie (przyczyna — pętle/instancje — NIE zweryfikowana; OPEN).

## 1. HARD — układ rekordu tabeli runtime (manager `0x20008D84`)
Tabela: `manager + 0x08`, stride `0x2C`, 660 pozycji; po starcie zajętych jest **655** (klucze unikalne, brak duplikatów).
Pola u32 LE (adresy względem początku rekordu):

| off | pole |
|---|---|
| +0x00 | klucz wyszukiwania (używany przez `0x080115F6`) |
| +0x04 | wskaźnik storage (SRAM) |
| +0x08 | kod typu: 1=u8, 2=u16, 4=s16, 3/5=u32 |
| +0x0C | min |
| +0x10 | kod typu pola min |
| +0x14 | max |
| +0x18 | kod typu pola max |
| +0x1C | default |
| +0x20 | kod typu pola default |
| +0x24 | klasa sidecar (0/1/2/3; rozkład: 0=208, 1=49, 2=44, 3=354) |
| +0x28 | wskaźnik RUNTIME na nazwę ASCII (635/655 rekordów ma nazwę) |

**Kluczowa uwaga o wartościach:** pola min/max/default są zapisane jako u32, ale znaczące tylko tyle bajtów, ile mówi **ich własny** kod typu;
pozostałe bity to śmieci ze stosu (np. `0x2010` min = `0x20020014` → u16 → 20; `0x200D` max = `0x5FF` typ 1 → 255; `0x2016` min `0xFF9C` typ 4 → −100).
Po zamaskowaniu: z 448 pozycji katalogu panelu **min+max zgadza się w 427**, typ w 447, nazwa w 448/448.
Rozbieżne (21) to wartości zmieniane po rejestracji albo inna interpretacja — OPEN.
Default `5678` (`0x162E`) = sentinel „brak default” (np. `0x2101 Solar power`). Default w katalogu `rejestry/` (304/448 zgodnych) pochodzi z innego źródła (wartości inicjalne), nie mylić z deskryptorem.

Pełny zrzut: `analiza/FW2213TK-2026-11-22/data/runtime_param_table_655.csv`.

## 2. HARD — klucz 3 = „Language” (zamyka OPEN z PASS 33)
Rekord slot 3: `key 0x0003, storage 0x20021FAA (= 0x200208EC + 0x16BE), typ u8, min 0, max 30, default 0, nazwa (z BIN, 0x08034C00) = "Language"`.
Klucz 4: `Parameters set Number`, storage `0x20021FBA` (+0x16CE), u16, 0..65535, default 10.
Wniosek: **klucz runtime = PID z katalogu panelu** (wszystkie 448 PID z `rejestry/panel-fw-parametry-FW2213TK.csv` są w tabeli runtime, nazwy 448/448 identyczne).
„Runtime key 3” jest więc PID `0x0003` „Language” — to mocny dowód z nazwy w firmware, adresu storage i zakresu (0..30), nie nazwa przejęta ze starego projektu.

## 3. STRONG — class 12 = przełączanie języka
Klasa 12 (`0x3C12A`): GET key 3, +1, SET, modulo 8, SET → wynik 0..7. Firmware ma **8 tabel TypedText** (ES, EST, EN, LT, PL, RO, SK, CZ).
Zakres parametru (0..30) jest szerszy niż 0..7, więc operacja modulo 8 ogranicza cykl do 8 języków. STRONG (nie HARD): brakuje bezpośredniego dowodu,
który widget wywołuje class 12 i że wartość 0..7 trafia do wyboru tabeli TypedText. `MENUTREE-ATTACK-01` wiązało selector 90 z Language.

## 4. HARD — obiekt `0x200208EC` i storage
- **603 z 655** storage’ów leży w `0x200208EC + [0x08 .. 0x3DD9]`: to jeden blok ustawień/konfiguracji, a nie osobne zmienne.
- Region „konfiguracji instalacji” `+0x16A0..+0x16F0` (bajt po bajcie, adresy storage = `0x200208EC + off`):
  `+0x16BA Boiler image selector (0x370A)`, `+0x16BB Default settings request (0x0005)`, `+0x16BC Is reset required (0x3728)`, `+0x16BD Autoconfig activation (0x3501)`,
  **`+0x16BE Language (0x0003)`**, `+0x16BF Main module type (0x3500)`, `+0x16C0 CH expansion module type (0x3502)`, `+0x16C1 Outside temp sensor config (0x3505)`,
  `+0x16C2 Outside temp averaging [h] (0x3720)`, **`+0x16C3 Heating configuration (0x2105)`, `+0x16C4 Hot water configuration (0x2106)`, `+0x16C5 Buffer configuration (0x2107)`, `+0x16C6 Solar configuration (0x2108)`**,
  `+0x16C7 Lambda module presence (0x2123)`, `+0x16C8 Sound alarm activation (0x3506)`, `+0x16C9 Return to boiler temp sensor (0x350A)`, `+0x16CA/+0x16CB Silence hours from/to (0x3508/0x3509)`,
  `+0x16CC Profile number (0x350B)`, `+0x16CD Start burning wood (0x3001)`, `+0x16CE Parameters set Number (0x0004, u16)`, `+0x16D2 Additional fuel storage (0x3525)`, … 
  To są dokładnie pola, które sterują widocznością menu (`0x2105..0x2108` → CO/CWU/Buffer/Solar), więc **UI czyta konfigurację bezpośrednio z tego bloku** (pełna lista w CSV: kolumna `cfg_off`).
- **15 parametrów statystyk** (`0x3608..0x3619`, `0x3628`, `0x362A`, `0x362C`: liczniki zapłonów, czasy podajników, tlen, czyszczenia, energia) ma storage w `0x40024000..` — **backup SRAM (BKPSRAM)**, czyli przeżywają zanik zasilania. To jedyna widoczna tu persystencja lokalna; reszta ustawień jest w zwykłym SRAM (synchronizacja z centralą przez CAN — wcześniejsze passy).
- Jedna para dzieli storage: `0x2119` i `0x4009` (oba „Exhaust gas temperature (2)”, `0x20014490`) — alias/lustro.

## 5. HARD — rezolwer `FUN_08036FF2` (RUNTIME `0x08046FF2`): dwie tabele i reguła instancji
Wynika z dezasemblacji (adresy tabel liczone z `addw r1,pc,#imm`, nie z zapamiętanych wartości):
- **Tabela 1** @ RAW `0x37B48`, **49 rekordów** po 4 B `(s16 klucz UI, u16 baza PID)`. To 49 parametrów obwodu grzewczego (CH): `0xA9→0x2032 CH comf temp`, `0xAA→0x2048`, `0xAC→0x2064 CH program`,
  `0xBF..0xC5→0x2126..0x213E` (harmonogramy), `0xD4..0xD6→0x2321..0x2329` (nazwa obwodu) itd. **Reguła: `PID = baza + instancja − 1`**, gdzie `instancja = [page_ctx+0x12C]`
  (`ldrb [r0,#0x12C]; r0 = r1 + r0; r1 = r0 − 1`). Klucz `0xA8` jest rekordem 0. Dla wszystkich 49 baz instancje 1..4 **istnieją** w tabeli runtime (196/196).
- **Tabela 2** @ RAW `0x37578`, **372 rekordy** po 4 B `(s16 klucz UI, u16 PID)`, wynik wprost bez instancji; 362/372 PID jest w tabeli runtime.
- Po rezolucji: lookup po PID w tabeli runtime (`0x080115F6`). Specjalny klucz `0xA8` (CH status).
- Wyjaśnia to część „dodatkowych” kluczy runtime: z 207 kluczy spoza katalogu 448, **147** to CO2..CO4 z reguły powyżej; reszta to m.in. `0x2306..0x2308` i rejestry alarmów `0x4011..`.

## 6. KOREKTA — PASS 26 (negative closure klucza 0x0117) jest ODRZUCONY
PASS 26 twierdził, że `0x0117` nie występuje w tabelach rezolwera, a „klucz `0x2123` → wartość `0x0117`” jest pod RAW `0x3797A`.
To błąd fazy odczytu: rekordy są 4-bajtowe i wyrównane od `0x37578`; poprawny rekord to **`(0x0117 → 0x3506)` @ RAW `0x3797C`**, a `0x3797A` jest drugą połówką rekordu `(0x0115 → 0x2123)`.
Konsekwencja: ścieżka menu `0x0E → row+0xF8 → 0x0807C540[+0x2C]=0x15 → 0x0803C270 → klucz 0x0117 → 0x08037212` **dochodzi do PID `0x3506` „Sound alarm activation”**
(storage `0x20021FB4`, u8) i dalej do `0x08011812`. Pozycja o stanie `0x0E` w menu to więc przełącznik „Sound alarm”, spójne z listą wierszy 15..20 z MENUTREE-ATTACK-01.
Status: HARD dla mapowania `0x0117→0x3506` (bajty BIN + rezolwer); STRONG dla przypisania tego do wiersza menu (zależy od pośredniego `+0x2C = 0x15` z PASS 27).
Ten sam błąd fazy mógł wpłynąć na inne odczyty tabel — **sprawdzić** PASS 19/26 pod kątem wszystkich odczytów z `0x37578` i `0x37794`.

## 7. Potwierdzenie z PASS 19: `0x68 → 0x300B`
Tabela 2, rekord `(0x0068 → 0x300B)`; nazwa w firmware `Stop burning wood` (BIN `0x2595C`), sąsiednie parametry „Start burning wood” `0x3001` (storage `+0x16CD`) i „Burning type”.
Czy wartość 0/1 oznacza wentylator/podajnik — nadal wniosek z kontekstu (hybryda pellet+drewno), nie dowód.

## 8. Rzeczy ODRZUCONE / skorygowane
- REJECTED: PASS 26 (patrz §6).
- CORRECTED: „logical key 3” → klucz runtime = PID `0x0003` Language (HARD).
- CORRECTED: katalog „260 slotów” ≠ tabela rezolwera; rezolwer ma 49 + 372 rekordów, runtime 655, panelowy katalog 448 (PID).
- NOTE: "260 slotów" z wcześniejszych passów nie jest tabelą rezolwera ani katalogiem panelu; relacji 260 ↔ 448 ↔ 655 nie rozstrzygnięto (OPEN).

## 9. OPEN
1. Skąd bierze się instancja `[page_ctx+0x12C]` w każdej ścieżce (producent).
2. 21 rozbieżnych par min/max i 144 default względem katalogu `rejestry/` — czy wartości zmieniane po rejestracji (zakresy dynamiczne)?
3. 10 kluczy tabeli 2 poza runtime po starcie (`0x211A, 0x3002, 0x2269, 0x228D..0x228F, 0x218B, 0x218C, 0x3668, 0x3669`).
4. 20 rekordów runtime bez nazwy ASCII (`0x3123..0x3126`, `0x3713`, `0x3714`, …).
5. Znaczenie klasy sidecar +0x24 (0/1/2/3) w czasie wykonania.
6. Dowód, który widget wywołuje class 12 i że wynik 0..7 wybiera tabelę TypedText.
7. Emulator kończy w pierwszym zadaniu FreeRTOS; pozostałe zadania (CAN RX/TX, UI) wymagają modelu schedulera/PendSV.

## 10. Następny atak
(a) rozszerzyć emulator o kolejne zadania FreeRTOS (PendSV/kolejki), żeby zobaczyć zawartość storage po pełnej inicjalizacji i przepływ CAN; (b) wykorzystać tabelę 655 do automatycznego
zbudowania macierzy `PID → storage → CAN` oraz weryfikacji `0x08011812`; (c) sprawdzić wszystkie wcześniejsze odczyty tabel rezolwera (korekta §6).
