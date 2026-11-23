# CHATGPT — START HERE (agent statyczny, dostęp do repo)

> Ten plik jest dla agenta ChatGPT współpracującego z agentem Claude przy rewersie 1:1 firmware panelu **Estyma igneoTouch (FW2213TK)**. Masz dostęp do tego repo (`GieOeRZet/TeklaPelletCAN`). Pracujesz **statycznie** (czytanie/dezasemblacja bajtów firmware + ewentualne własne narzędzia), **bez emulatora** — dynamikę (uruchamianie firmware) robi Claude. Odpowiadaj po polsku.

## 1. Przeczytaj najpierw (w tej kolejności)
1. `CLAUDE.md` (zasady pracy nad projektem — obowiązują też Ciebie: minimalne zmiany, nie psuć działających rzeczy, FACT/STRONG/INFERENCE/OPEN/REJECTED).
2. `NewEstyma/00_AGENT_START_HERE.md` (misja, mapowanie adresów, kotwice, sekcja „TODO (zlecone przez wlasciciela) A i B” — to Twój obszar tematyczny).
3. `NewEstyma/03_TOOLING.md` (narzędzia w `tools/`, reguły adresowe, wzorce harnessów).
4. `NewEstyma/04_FIRMWARE_MANIFEST.md` (integralność firmware).
5. `NewEstyma/COORDINATION.md` ← **tablica zadań i komunikacji między Tobą a Claude. Czytaj i aktualizuj ją na bieżąco.**

## 2. Gałęzie i pliki (bez kolizji!)
- Ty pracujesz na gałęzi **`ccr-be8a1bcb-5t76j0-chatgpt`** (utwórz ją z `ccr-be8a1bcb-5t76j0-pin`, gdzie leży ten plik i COORDINATION.md).
- Claude pracuje na gałęzi **`ccr-be8a1bcb-5t76j0`** (główna robocza). Scala Roman.
- **Nie edytuj plików, które pisze Claude** (patrz COORDINATION.md — kolumna „właściciel pliku”). Twoje raporty i narzędzia nazywaj tak, żeby się nie nakładały.
- Raporty PASS numeruj **od 70 w górę** (`analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-7X-...-2026-11-23.md`), żeby nie kolidować z numeracją Claude.
- Własne narzędzia dozwolone w `tools/` — nazwy z prefiksem `cg_` (np. `tools/cg_pin_scan.py`) + test `tools/test_cg_*.py`. Nie nadpisuj istniejących narzędzi.
- Commituj i pushuj po każdym etapie na swoją gałąź. PR-ów nie twórz. Stopka commita jak w repo.

## 3. Firmware (NIE commituj)
- Plik: `FW2213TK_kopia.bin`, rozmiar `2 031 616` B (`0x1F0000`), SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`.
- **Nie ma go w repo i ma tam nie trafić.** Roman wgra Ci go do sesji (w interpreterze zwykle pod `/mnt/data/FW2213TK_kopia.bin`). Dodaj go do `.git/info/exclude`.
- Zanim cokolwiek orzekniesz o bajtach — zweryfikuj SHA-256. Jeśli się nie zgadza: STOP.
- `pip install capstone` do dezasemblacji Thumb-2 (jeśli offline — pracuj na gotowych listingach z sekcji 6 i czystym Pythonem).

## 4. Reguła adresowa (najczęstszy błąd)
```
RAW     = offset w pliku .bin
PROJECT = 0x08000000 + RAW       # adresy w raportach
RUNTIME = PROJECT + 0x10000      # adresy w działającym obrazie / wskaźniki/vtable
```
Wskaźniki funkcji i vtable w obrazie to RUNTIME — przed indeksowaniem pliku odejmij `0x10000`. Zawsze pisz, której bazy używasz. SRAM `0x2000xxxx` to dane inicjalizowane (pakowane IAR LZ77) — nie czytaj ich wprost z offsetu w pliku.

## 5. TWÓJ ZAKRES (3 tematy, wszystkie statyczne)

### Temat A — ukryte kody w polu PIN (poza 0900/0999/6154/6666)
Cel: pełna mapa „wpisana liczba → efekt” dla pola PIN. Z analizy wstępnej (sekcja 6) wynika, że poza znanymi kodami reagują co najmniej:
- **`1992` (`0x7c8`)** — dodaje `0x01E13380` (=31 536 000 s = 1 rok) do licznika czasu i zapisuje do `[0x20021FA0+0x24]`. Ustal, co to robi (serwis / przegląd / gwarancja?). Prześledź, kto czyta `[0x20021FA0+0x24]`.
- **dopasowanie do tabeli 23 liczb** `0x20008C50` → ustawia tę samą flagę resetu co 6666.
- **`0`** — kasuje flagę.
Prześledź handler PIN `FUN_0803C21C` (PROJECT) i WSZYSTKIE wołane z niego funkcje z wpisaną liczbą; sprawdź też `FUN_080314BA` (wołane 2× w handlerze). Zgłoś każdą rozpoznawaną stałą z dowodem (adres instrukcji + efekt) i etykietą.

### Temat B — tabela 23 liczb `0x20008C50`
- To tablica **23 wskaźników**; wartość rekordu = `[wskaźnik+8]` (u16). Znane 22 wartości (z emulowanego RAM Claude): `10,12,15,18,25,30,35,50,75,120,150,180,220,230,300,500,1220,1300,1550,2000,2500,3000`. **Ustal 23. wartość** (jeśli statycznie się nie da z `.data` — zostaw OPEN).
- Zinterpretuj znaczenie. Hipoteza: katalog mocy/modeli kotła. Sprawdź, gdzie jeszcze wołane są `FUN_080144B4` i `FUN_080144E4` (szukaj `bl` do RUNTIME `0x080244B4`/`0x080244E4`) i z jakim argumentem — to ujawni, czym są te 23 obiekty.
- Rozstrzygnij: czy wpisanie którejś z 23 liczb to realny „ukryty kod” (ustawia flagę resetu), czy efekt uboczny współdzielenia funkcji. Argumenty za obiema wersjami.

### Temat C — czas / RTC (przygotowanie pod synchronizację czasu w naszym module)
Cel: jak panel ustawia/odczytuje czas i czy istnieje ramka/PID czasu po CAN (potrzebne później do synchronizacji zegara z ESP32/HA). Kotwice z `00_AGENT_START_HERE.md`:
- HAL RTC panelu: `0x08028F78` / `0x08028FF8` (dialog „Ustaw czas” zapisuje RTC panelu).
- Alarmy używają czasu panelu jako unix UTC: `0x08049370`.
Ustal: (a) czy panel wysyła/odbiera po CAN ramkę lub PID z czasem (szukaj dostępu do rejestrów RTC i konwersji na/z unix, oraz PID-ów okolicy czasu); (b) format (epoka, strefa); (c) czy jest zapis czasu przychodzącego z magistrali. Źródło prawdy zegara = RTC panelu. **To tylko RE — nic nie wdrażaj.**

## 6. Gotowe listingi na szybki start (Thumb-2, adresy = PROJECT; zweryfikowane kapstonem)
`FUN_08037E74` (mapper poziomu) rozpoznaje DOKŁADNIE {0→0, 900→1, 999→2, 6154→3} i nic więcej (flaga poziomu `[obj+0x158]`).
`FUN_08018634` (komparator resetu):
```
0x08018638: cmp.w r5, #0x7c8      ; 1992 -> gałąź "czas +1 rok" -> [r4+0x24]
0x0801865A: bl    #0x80144b4       ; membership w tabeli 23
0x0801865E: cmp   r0,#1 ; strb r0,[r4,#7]   ; dopasowanie -> flaga [0x20021FA7]=1
0x08018668: movw  r0,#0x1a0a (6666); cmp r5,r0 ; strb #1,[r4,#7] ; 6666 -> flaga=1
0x08018676: cbnz r5 ... ; wpisane 0 -> flaga=0
; 0x08018684: wygaszanie flagi po 61 tikach (licznik [obj+0xE6], cmp #0x3d)
```
`FUN_080144B4` (membership): literał `[pc,#0x74]` → baza `0x20008C50`; porównuje `[wsk+8]` (u16) z wpisaną liczbą; pętla 23 (`cmp r2,#0x17; blo`). `FUN_080144E4` obok zwraca `[dopasowany+0xc]` (generyczny „znajdź obiekt po wartości”).
Kotwice: handler PIN `FUN_0803C21C`; flaga resetu `0x20021FA7` (PID `0x0005`) w obiekcie `0x20021FA0`; zapis bramki pollera `[0x2002466C+0x10]=(poziom!=0)` w handlerze po PIN. (Pełny, dłuższy listing: `/mnt/project-files/chatgpt-zadania/ZADANIE-CHATGPT-PIN-KODY-TABELA23.md` — Roman może go dograć.)

## 7. Metodyka (obowiązkowa)
FACT (dowód bajtami, z adresem) / STRONG / INFERENCE / OPEN / REJECTED. Nigdy nie awansuj domysłu, bo „brzmi sensownie”. Zachowuj wyniki negatywne. Źródło prawdy = bajty `.bin`, nie streszczenia.

## 8. Format raportu (każdy PASS)
Plik `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-7X-<TEMAT>-2026-11-23.md`:
```
# PASS 7X — <temat>
## Streszczenie
## Ustalenia (tabela: fakt -> dowód[adres,baza] -> etykieta)
## FACT / STRONG / INFERENCE / OPEN / REJECTED
## Pytania do Claude (dynamika/emulator)  -> przenieś też do COORDINATION.md
```

## 9. Granice — czego NIE robić
- Bez emulatora/dynamiki (to Claude): wpisanie 6666 na ekranie PIN, ramka CAN dla PID `0x0005`, wskaźnik nagłówka `+0x210`, skutek bramki pollera.
- Nie ruszaj UI-MODEL / grafu akcji / alarmów / warunków widoczności (to osobny wątek Claude na głównej gałęzi).
- Nie commituj firmware. Nie testuj niczego na żywym kotle (6666 kasuje konfigurację).
- Trzymaj się swojej gałęzi i swoich plików (sekcja 2 + COORDINATION.md).
