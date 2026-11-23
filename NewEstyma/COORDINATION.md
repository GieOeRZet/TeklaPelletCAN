# COORDINATION — Claude ↔ ChatGPT (rewers FW2213TK)

> Tablica koordynacji dwóch agentów pracujących nad rewersem 1:1 panelu Estyma igneoTouch.
> **Każdy agent czyta ten plik na starcie i aktualizuje go po swoim etapie.** Komunikacja (pytania/odpowiedzi) idzie przez sekcję 4. Roman może też przekazywać polecenia ustnie.

## 1. Gałęzie
| Agent | Gałąź | Zakres |
|---|---|---|
| Claude | `ccr-be8a1bcb-5t76j0` (główna robocza) | dynamika/emulator + rewers UI (osobny wątek) |
| Claude (ten wątek) | `ccr-be8a1bcb-5t76j0` | TODO A/B dynamiczne: 6666→CAN PID 0x0005, wskaźnik `+0x210`, skutek bramki pollera |
| ChatGPT | `ccr-be8a1bcb-5t76j0-chatgpt` (utwórz z `-pin`) | analiza statyczna (patrz niżej) |
| pliki koordynacyjne | `ccr-be8a1bcb-5t76j0-pin` | ten plik + `CHATGPT_START_HERE.md` |

Scalanie gałęzi: **Roman**. Agenci nie robią PR-ów i nie scalają nawzajem swoich gałęzi.

## 2. Podział tematów (TODO A/B z `00_AGENT_START_HERE.md`)
| # | Temat | Właściciel | Status |
|---|---|---|---|
| A1 | Ukryte kody w polu PIN (poza 0900/0999/6154/6666) | **ChatGPT** (statyka) | OPEN |
| A2 | Tabela 23 liczb `0x20008C50` — wartości + znaczenie | **ChatGPT** (statyka) | OPEN |
| A3 | Czas/RTC: jak panel ustawia/czyta czas, czy jest PID/ramka czasu po CAN | **ChatGPT** (statyka) | OPEN |
| B1 | 6666 w emulatorze → ramka CAN dla PID `0x0005` + reakcja wskaźnika `+0x210` | **Claude** (emulator) | WSTRZYMANE (czeka na zgodę Romana) |
| B2 | Bramka pollera `[0x2002466C+0x10]=(poziom!=0)` — weryfikacja skutku | **Claude** (emulator) | WSTRZYMANE |
| B3 | „Ochrona kotla” (TypedText 87) warunek wyświetlenia; Bufor L≥1 „0%”/„7°C” | Claude (statyka+emulator) | OPEN |
| B4 | 4. bramka `0x08054AB8` + 6 nietrafionych wrapperów ≥3 | wolne (statyka) — do ustalenia | OPEN |

Zasady bez kolizji: ChatGPT raporty PASS **od 70**; narzędzia ChatGPT z prefiksem `tools/cg_`. Claude nie rusza plików `cg_*` ani raportów 70+; ChatGPT nie rusza plików Claude.

## 3. Właściciele plików (nie edytować cudzych)
| Plik/wzorzec | Właściciel |
|---|---|
| `analiza/.../AUTONOMOUS-PASS-70+...` | ChatGPT |
| `analiza/.../AUTONOMOUS-PASS-61..69...` | Claude (rezerwa) |
| `tools/cg_*`, `tools/test_cg_*` | ChatGPT |
| pozostałe `tools/*`, `NewEstyma/00..05`, `ui_*`, `cortexm_rtos.py` | Claude / wspólne (nie modyfikować bez wpisu tutaj) |
| `NewEstyma/CHATGPT_START_HERE.md`, `NewEstyma/COORDINATION.md` | wspólne (dopisywać, nie usuwać cudzych wpisów) |

## 4. Wymiana informacji (dopisuj na dole, z datą i podpisem agenta)

### Ustalenia przekazane ChatGPT na start (od Claude, 2026-11-23)
Statyczne znaleziska do domknięcia (adresy = PROJECT, RUNTIME = PROJECT+0x10000):
- Handler PIN `FUN_0803C21C` → woła `FUN_08018634` (6666+tabela), potem `FUN_08037E74` (poziom), potem zapis bramki pollera `[0x2002466C+0x10]=(poziom!=0)`.
- `FUN_08037E74` rozpoznaje DOKŁADNIE {0,900,999,6154} → poziom {0,1,2,3}. Brak innych kodów poziomu. (STRONG)
- `FUN_08018634`: 6666 ORAZ dopasowanie do tabeli 23 (`FUN_080144B4`) → flaga `[0x20021FA7]`=1 (PID 0x0005, obiekt `0x20021FA0`, `[obj+7]`); 0 kasuje; **1992 (0x7c8)** → `[obj+0x24]=czas+0x01E13380` (1 rok w s). (FACT z listingu)
- Tabela `0x20008C50`: 23 wskaźniki, wartość=`[wsk+8]`; 22 znane wartości (patrz CHATGPT_START_HERE §5B); 23. — OPEN.

### Pytania otwarte do Claude (emulator) — uzupełnia ChatGPT
- (tu ChatGPT wpisuje pytania wymagające uruchomienia firmware)

### Odpowiedzi Claude — uzupełnia Claude
- (tu Claude odpowiada po przebiegach emulatora)

## 5. Log statusów (ostatni na górze)
- 2026-11-23 — Claude: utworzono CHATGPT_START_HERE.md + COORDINATION.md na `ccr-be8a1bcb-5t76j0-pin`; przekazano statyczne znaleziska PIN. Tor emulatorowy Claude WSTRZYMANY do decyzji Romana.
