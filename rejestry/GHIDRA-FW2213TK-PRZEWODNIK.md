# Dekompilacja panela Igneo Touch (FW2213TK) — co to jest i jak z tego korzystać

> Temat poboczny względem głównego rozwoju (firmware ESP32/karty/appka/integracja) — to notatka z sesji
> poświęconej wyłącznie researchowi rejestrów drugiego obiegu CO (CO2), zapisana, żeby nie trzeba było
> odkrywać tych samych rzeczy drugi raz. Nie wymaga żadnej akcji w kodzie projektu.

## Pliki i ich pochodzenie

| Plik | Co to jest | Kompletność |
|---|---|---|
| `firmware/FW2213TK-ghidra/decompiled.c` | Dekompilacja **wszystkich** 1157 wykrytych funkcji binarki panela (Ghidra 12.2, `analyzeHeadless`, domyślne analizatory) | Surowa, kompletna wg własnego `README.md` tego folderu |
| `firmware/FW2213TK-ghidra/strings.txt` | **Wszystkie** zdefiniowane stringi binarki z adresami | Surowa, kompletna |
| `firmware/FW2213TK-ghidra/functions.txt` | Adresy + nazwy (`FUN_*`, brak symboli) + rozmiary wszystkich funkcji | Surowa, kompletna |
| `rejestry/panel-fw-parametry-FW2213TK.csv` | **448** wyciągniętych parametrów: id (dziesiętnie), adres CANopen (hex), nazwa angielska, typ, zakres, wartość domyślna, adresy RAM/kodu | **Wyciąg zrobiony w innej, nieudokumentowanej sesji — w repo NIE MA skryptu, który to wygenerował.** Nie można zweryfikować, czy to ekstrakcja wyczerpująca, czy tylko "to, co dało się łatwo powiązać z nazwą". |
| `rejestry/panel-fw-mapa-indeks-id.csv` | Mapa indeks CANopen ↔ ID panela (420 par) | Jw. — bez znanego skryptu źródłowego |

**Ważne dla kogoś, kto to kontynuuje:** `decompiled.c`/`strings.txt`/`functions.txt` to twarde, surowe dane (można im ufać, że są kompletne — to bezpośredni output Ghidry). Natomiast `panel-fw-parametry-FW2213TK.csv` to **interpretacja** tych danych zrobiona wcześniej — może nie być wyczerpująca. Jeśli czegoś brakuje w tej tabeli, **nie znaczy to, że tego nie ma w binarce** — trzeba sprawdzić bezpośrednio w `decompiled.c`/`strings.txt`.

## Kluczowe ustalenia z researchu (listopad 2026) — jak czytać tę tabelę

1. **Kolumna `id` to dziesiętny zapis adresu CANopen**, identyczny jak `id_hex` (np. `8514` = `0x2142`). To nie jest sekwencyjny numer porządkowy ani indeks tablicy w pamięci panela.
2. **Duże "dziury" w numeracji `id` są normalne** — to zwykłe przeskoki między zakresami obiektów CANopen (systemowe `0x0000` → producenckie `0x2000` → `0x3000` → `0x4000`). Nie traktować jako dowodu brakującej ekstrakcji.
3. **Małe dziury WEWNĄTRZ gęsto upakowanego zakresu** (np. `0x22A5`→`0x22AD`, brakuje `0x22A6`-`0x22AC`) **są podejrzane i warte sprawdzenia** — szczególnie w rejonie `0x2140`-`0x2300`, gdzie nastawy serwisowe CO1 leżą co 4 bajty. Sprawdzać przez grep po dokładnym adresie we wszystkich trzech plikach katalogu (`panel-fw-parametry-FW2213TK.csv`, `katalog-rejestrow.csv`, `archiwum/igneo-katalog-calosc.csv`) — jeśli adresu nie ma **nigdzie**, nawet jako niepotwierdzony "sąsiad" ze skanu różnicowego, to prawdziwa, nieobjaśniona luka.
4. **Sąsiad pod adresem ±1 z IDENTYCZNYM zakresem min/max co sprawdzany rejestr to niemal zawsze artefakt skanu różnicowego** (echo tej samej wartości 16-bitowej czytane jako dwa osobne bajty), **nie prawdziwy, osobny rejestr**. Odróżnić od prawdziwej pary: prawdziwy, potwierdzony odpowiednik ma **inną wartość**, własną nazwę z firmware (`fw: xxx` w notatkach) i reaguje na realną akcję/zmianę na panelu.

## Temat, który był badany: rejestry obwodu CO2

**Pytanie wyjściowe:** czy drugi obieg CO (CO2) ma własny, pełny zestaw parametrów (histereza, krzywa pogodowa, kalibracja, korekcje, limity), tak jak CO1.

**Ustalenia (zweryfikowane w kodzie/rejestrach, nie na słowo):**
- CO2 ma potwierdzony odpowiednik **tylko** dla 7 prostych odczytów stanu, zawsze pod adresem **CO1_adres + 1**:
  `ch1_temp`(`0x4001`)→`ch2_temp`(`0x4002`), `ch1_set_manual`(`0x2146`)→`ch2_set_manual`(`0x2147`),
  `ch1_set_result`(`0x22AD`)→`ch2_set_result`(`0x22AE`), `ch1_pump`(`0x2299`)→`ch2_pump`(`0x229A`),
  `co_mode`(`0x2064`)→`co2_mode`(`0x2065`), `co1_pump_mode`(`0x229D`)→`co2_pump_mode`(`0x229E`),
  `co1_mixer_mode`(`0x214A`)→`co2_mixer_mode`(`0x214B`).
- **19 pozostałych parametrów CO1** (histereza, kalibracja, krzywa pogodowa ×3, źródło, czujniki, limity,
  korekcje, stała pompa, ochrona powrotu...) **nie ma potwierdzonego odpowiednika CO2 nigdzie** — ani w skanie
  CAN, ani w pełnej dekompilacji panela (histereza występuje w `panel-fw-parametry-FW2213TK.csv` **dokładnie
  raz**, pod `0x22BD`).
- Sprawdzony offset `+1` (ten, który działa dla odczytów stanu) **nie przenosi się** na te 19 parametrów —
  sąsiad pod `CO1_adres+1` ma za każdym razem **identyczny zakres** co CO1, czyli to artefakt skanu (patrz pkt
  4 wyżej), nie prawdziwy rejestr CO2.
- Cały blok adresowy `0x229D`-`0x22FD`, w którym leżą te parametry, jest już w pełni zajęty przez CO1 i
  przeplatające się testy wyjść CO1/CO3/CO4 (np. sąsiad `co1_hyst` pod `-1` to dosłownie "Mieszacz CO4 — tryb
  testowy") — nie ma tam fizycznie wolnego miejsca na drugi zestaw.
- Każdy znaleziony rejestr CO2 (odczyty stanu) ma w katalogu CAN notatkę: **"Brak drugiego obiegu | w firmware
  wyłączone (`dwa_obiegi_co: false`)"** — kocioł, na którym robiono skan, ma fizycznie wyłączony drugi obieg.

**Wniosek (nierozstrzygnięty do końca — wymaga innego kotła):** najbardziej prawdopodobna hipoteza to
**wspólny, jeden zestaw nastaw serwisowych dla obu obiegów** (gdy drugi obieg jest aktywny, używa tych samych
rejestrów CO1), a nie druga, brakująca kopia. Ale jest też (mała) szansa, że te rejestry po prostu **nie
pojawiają się w skanie, bo drugi obieg jest wyłączony** — sterownik mógłby ich nie transmitować/nie
aktualizować, dopóki `dwa_obiegi_co` nie jest `true`, niezależnie od tego, czy istnieją w pamięci. Jedyny
sposób na rozstrzygnięcie: różnicowy skan na kotle z fizycznie włączonym drugim obiegiem CO — bez takiego
kotła temat zostaje otwarty.

**Dodatkowo w tej sesji:** potwierdzono, że angielskie nazwy jak `co1_calib`, `ch1_pump` to **nasze własne**
identyfikatory (zdefiniowane w `firmware/components/core/reads_table.cpp`), nie dosłowne stringi z binarki —
prawdziwa nazwa z Toucha dla `co1_calib` to np. inna fraza w `strings.txt`, a nasz identyfikator jest tylko
wygodną nazwą roboczą powiązaną z adresem CANopen po jego potwierdzeniu.

## Jak szukać dalej (dla kolejnej sesji)

1. Dla pytania "czy adres X ma coś przypisanego": `grep -n ",0xXXXX," rejestry/panel-fw-parametry-FW2213TK.csv rejestry/katalog-rejestrow.csv rejestry/archiwum/igneo-katalog-calosc.csv`.
2. Dla pytania "jaka jest angielska nazwa z Toucha": szukać w `panel-fw-parametry-FW2213TK.csv` po adresie (kolumna `id_hex`) — to jest nazwa wyciągnięta ze `strings.txt`, nie nasz identyfikator.
3. Żeby sprawdzić, czy ekstrakcja `panel-fw-parametry-FW2213TK.csv` jest wyczerpująca w konkretnym miejscu — trzeba wrócić do `decompiled.c`/`strings.txt` bezpośrednio (surowe, kompletne dane) i poszukać tam ręcznie, zamiast ufać, że tabela 448 pozycji obejmuje wszystko.
4. To wciąż czysty research dokumentacyjny — żadna z tych ustaleń nie wymaga zmiany kodu firmware/API/encji. Jeśli kiedyś pojawi się kocioł z aktywnym drugim obiegiem CO, to jest gotowy punkt wyjścia do pełnego różnicowego skanu.
