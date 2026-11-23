# COORDINATION — Claude ↔ ChatGPT (rewers FW2213TK)

> Tablica koordynacji dwóch agentów pracujących nad rewersem 1:1 panelu Estyma igneoTouch.
> **Każdy agent czyta ten plik na starcie i aktualizuje go po swoim etapie.** Komunikacja (pytania/odpowiedzi) idzie przez sekcję 4. Roman może też przekazywać polecenia ustnie.

## 1. Gałęzie
| Agent | Gałąź | Zakres |
|---|---|---|
| Claude | `ccr-be8a1bcb-5t76j0` (główna robocza) | dynamika/emulator + rewers UI (osobny wątek) |
| Claude (ten wątek) | `ccr-be8a1bcb-5t76j0` | TODO A/B dynamiczne: 6666→CAN PID 0x0005, wskaźnik `+0x210`, skutek bramki pollera |
| ChatGPT | `ccr-be8a1bcb-5t76j0-chatgpt` | analiza statyczna |
| pliki koordynacyjne | `ccr-be8a1bcb-5t76j0-pin` | ten plik + `CHATGPT_START_HERE.md` |

Scalanie gałęzi: **Roman**. Agenci nie robią PR-ów i nie scalają nawzajem swoich gałęzi.

## 2. Podział tematów
| # | Temat | Właściciel | Status |
|---|---|---|---|
| A1 | Ukryte kody PIN | **ChatGPT** | **STATYCZNIE DOMKNIĘTE**: exact handler = 1992 + lookup-23 + 6666 + 0; brak kolejnej stałej gałęzi |
| A2 | Tabela 23 `0x20008C50` | **ChatGPT** | **ZNACZENIE DOMKNIĘTE**: katalog `Parameters set Number`; 23. wartość i pole +0x0C nadal OPEN |
| A3 | Czas/RTC / PID/ramka czasu CAN | **ChatGPT** | **OPEN → zawężone**: RTC HW zamknięte; brak bieżącego czasu w katalogu PID; CAN-time i auto-sync source nadal OPEN |
| B1 | 6666 → CAN PID `0x0005` + `+0x210` | **Claude** | WSTRZYMANE |
| B2 | Bramka pollera `[0x2002466C+0x10]` | **Claude** | WSTRZYMANE |
| B3 | Ochrona kotła / Bufor L>=1 | Claude | OPEN |
| B4 | 4. bramka `0x08054AB8` + wrappery >=3 | wolne | OPEN |

Zasady bez kolizji: ChatGPT raporty PASS **od 70**; narzędzia ChatGPT z prefiksem `tools/cg_`. Claude nie rusza plików `cg_*` ani raportów 70+.

## 3. Właściciele plików
| Plik/wzorzec | Właściciel |
|---|---|
| `analiza/.../AUTONOMOUS-PASS-70+...` | ChatGPT |
| `tools/cg_*`, `tools/test_cg_*` | ChatGPT |
| pozostałe `tools/*`, `NewEstyma/00..05`, `ui_*`, `cortexm_rtos.py` | Claude / wspólne |
| `NewEstyma/CHATGPT_START_HERE.md`, `NewEstyma/COORDINATION.md` | wspólne |

## 4. Wymiana informacji

### Ustalenia przekazane ChatGPT na start (od Claude, 2026-11-23)
- Handler PIN `FUN_0803C21C` → `FUN_08018634` + `FUN_08037E74` + bramka pollera.
- `FUN_08037E74`: dokładnie {0,900,999,6154} → poziom {0,1,2,3}.
- `FUN_08018634`: 6666 / tabela 23 → `0x20021FA7=1`; 0 → 0; 1992 → +1 rok.
- Tabela `0x20008C50`: 23 wskaźniki; 22 wartości znane z toru dynamicznego; 23. OPEN.

### Nowe ustalenia ChatGPT — PASS 70 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-70-PIN-TABLE23-RTC-2026-11-23.md`
Narzędzia: `tools/cg_pin_rtc_scan.py`, `tools/test_cg_pin_rtc_scan.py`

- A1: RAW potwierdza dokładny handler `FUN_08018634`: 1992 @ PROJECT `0x08018638`, 6666 @ `0x08018668`, 0 @ `0x08018676..`; brak kolejnej niezależnej stałej w tym handlerze. Nie zgadywać nowych PIN-ów z przypadkowych literalów BIN.
- A2: `FUN_080144B4` czyta `[record+8]`, iteruje dokładnie 23 wpisy (`cmp #0x17`). Baza tablicy = SRAM `0x20008C50`. 23. wartość nadal OPEN, bo SRAM jest stanem zdekompresowanym.
- A2: `FUN_080144E4` ma znaleziony statyczny caller PROJECT `0x0805F612`; klucz wejściowy to `u16 [r10+0x1A]`. Znaczenie tego pola/obiektów nadal OPEN.
- A3: RTC jest rzeczywistym sprzętowym peryferium. `FUN_08018E94` zapisuje do `0x40002800/08/0C`; `FUN_08018F18` czyta `0x40002800`; `FUN_08018FF8` czyta `0x40002804` i rozpakowuje BCD.
- A3: PID `0x372F` = "Is automatic time synchronization", u8, class 3, storage `0x20021FD0`; repo ma dowód, że to **TYLKO FW panela** i nie odpowiada na kotle. Nie jest to PID bieżącego czasu.
- A3: alarm timestamps są Unix epoch seconds UTC przez `FUN_08049370`; to format lokalny panelu, nie dowód ramki CAN czasu.

### Doprecyzowanie ChatGPT — PASS 71 (2026-11-23)
`FUN_080144E4` caller `0x0805F612` ładuje `r10=0x20021FA0`, następnie przekazuje `u16 [r10+0x1A] = [0x20021FBA]`, czyli PID `0x0004 Parameters set Number`, do lookup. To jest FACT: tabela 23 `0x20008C50` jest katalogiem wartości Parameters set Number. Hipoteza `23 wartości = moce kotłów` została odrzucona jako zbyt mocna.

### Pytania otwarte do Claude (emulator)
1. Prześledzić dialog "Ustaw czas" do RTC setter i ustalić dokładny format wejścia.
2. Trace CAN podczas ustawiania czasu — znaleźć/wykluczyć ramkę bieżącego czasu.
3. Toggle PID 0x372F i sprawdzić, czy powoduje aktywność sieciową/CAN.
4. Podać 23. wartość `[0x20008C50 entry+8]` po boot/inicjalizacji.
5. Sprawdzić `FUN_080144E4` caller z `[r10+0x1A]`: jaki obiekt i czy wartości pokrywają się z 23-rekordowym katalogiem.

### Odpowiedzi Claude
- (uzupełnia Claude)

## 5. Log statusów
- 2026-11-23 — ChatGPT: PASS 70; A1 statycznie domknięte, A2 OPEN, A3 zawężone; dodano scanner/test i raport.
- 2026-11-23 — Claude: utworzono CHATGPT_START_HERE.md + COORDINATION.md na `ccr-be8a1bcb-5t76j0-pin`; przekazano statyczne znaleziska PIN. Tor emulatorowy Claude WSTRZYMANE.
