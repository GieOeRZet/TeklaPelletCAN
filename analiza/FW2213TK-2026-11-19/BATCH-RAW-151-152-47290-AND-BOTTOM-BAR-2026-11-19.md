# BATCH — RAW BIN 151/152 + 47290 RESOURCE CHAIN — 2026-11-19

## Cel
Niezależny raw-binary pass na FW2213TK_kopia.bin, po wcześniejszym pokazaniu 151/152, oraz rozdzielenie ich od 056/057 z ekranu "Moc dmuchawy modulacja".

## PASS 1 — tabela bitmap w BIN

Zweryfikowany BIN:
- FW2213TK_kopia.bin
- 2,031,616 B = 0x1F0000
- obraz ładowany od 0x08000000 dla raw disassembly
- bitmap descriptor table: file offset 0x54450 / runtime 0x08054450

Z tabeli wynika rekord 20 B na bitmapę. Dla numerów 151 i 152:

151:
- descriptor file offset: 0x5501C
- RGB/data pointer: 0x081C5638
- secondary/alpha pointer: 0x081E4C7C
- W=30, H=31
- trailing fields = 0,0

152:
- descriptor file offset: 0x55030
- RGB/data pointer: 0x081C5D7C
- secondary/alpha pointer: 0x081E5020
- W=30, H=31
- trailing fields = 0x00090009 / 0x000C000C

Różnica pointerów RGB 151→152 = 0x744 = 30*31*2. To jest twardy dowód, że oba zasoby mają kolejne 16-bitowe płaszczyzny RGB565 o dokładnym rozmiarze 30x31.

Uwaga: naive raw RGB565 decode z samego pointera nie odtwarza poprawnie PNG. Oznacza to, że między descriptor table a gotowym PNG istnieje jeszcze firmware/TouchGFX-specific interpretation/packing warstwa. Nie wolno udawać, że prosty dump 16-bitów jest gotowym obrazem. Repozytoryjny PNG atlas pozostaje poprawnym wynikiem wcześniejszej ekstrakcji.

## PASS 2 — 47290: 151/152 są potwierdzone bezpośrednio z BIN

Raw disassembly:

FUN_08047290:
- tworzy 6 rekordów, stride 0x40
- rejestruje obiekt przez FUN_080318B4
- wywołuje FUN_08047334 w runtime refresh path

W FUN_08047334 dla każdego slotu:
- X = 100
- Y = 50 + 34*slot
- tworzony jest child przez FUN_0804C392
- później FUN_0804C320 dostaje cztery resource IDs:
  - +0x2E = 151
  - +0x30 = 151
  - +0x32 = 152
  - +0x34 = 152

Konkretny raw fragment:
- 0x474DA: movs r0,#0x98
- 0x474E8: movs r0,#0x97
- 0x474F... przygotowanie czterech halfwordów
- 0x47500: BL FUN_0804C320

To zamyka: 151/152 są parą bitmap stanów używaną przez 47290. Nie jest to hipoteza z samego atlasu.

## PASS 3 — ważne rozdzielenie od screenshotu "Moc dmuchawy modulacja"

Screenshot użytkownika z wykresem używa wizualnych punktów odpowiadających innej parze:
- 056.png = 20x20
- 057.png = 20x20
- web engine ma twarde:
  .fmp -> U(56)
  .fmp.sel -> U(57)

Czyli:
- 056/057 = punkty wykresu "Moc dmuchawy modulacja"
- 151/152 = osobny element stanu w 47290

Nie wolno już łączyć 151/152 z punktami wykresu tylko dlatego, że wizualnie oba są okrągłymi znacznikami.

## PASS 4 — caller chain 47290

Raw scan:
- jedyny bezpośredni BL do FUN_08047334: 0x080484D4, wewnątrz FUN_080484B0
- jedyny znaleziony bezpośredni BL do FUN_080484B0: 0x0803EE30, wewnątrz FUN_0803EC18

W 0x0803EE30:
- r0 = component pointer
- r1 = signed halfword record+0x02
- r2 = runtime result
- r3 = runtime result
- stack arg0 = record+0x0C - 1
- stack arg1 = byte record+0x07
- stack arg2 = pointer *(record+0x08)

FUN_080484B0 kopiuje stack arg2 do argumentu 7 FUN_08047334, więc:
param_7 = *(record + 0x08)
TypedTextID dla slotu = param_7[slot]

To jest twardy most:
record -> pointer do listy TypedText IDs -> 47334 -> konkretny slot.

## PASS 5 — korekta architektoniczna

Nie używać 47290 jako centralnego boiler graphic ani jako wykresu.

Najbezpieczniejszy model:
Home root 0803E5AC
 -> +0x92DC 47290
 -> 6-slot vertical component
 -> 151/152 state bitmap pair
 -> per-slot TypedText supplied dynamically

Natomiast screenshot burner screen i jego dolny pasek należy śledzić osobnym łańcuchem. W rodzinie 0804C410..0804D948 znaleziono już osobne użycie bitmap 160/161 (241x49), co jest znacznie bliższe dużemu przyciskowi/obszarowi konfiguracji widocznemu na screenshotach. Nie utożsamiamy tego jeszcze bez parent/vtable proof.

## Next attack

1. odzyskać dokładną semantykę 20-byte BitmapData descriptor:
   pointer RGB + pointer A8 + W/H + trailing fields;
2. znaleźć firmware/TouchGFX decode/packing path, który zamienia raw payload na PNG;
3. rozwinąć FUN_0804C320/FUN_0804C392/FUN_0804C410 w stronę parent/child;
4. osobno zamknąć realny bottom bar screenshotu przez resource 159/160/161/170/171 i geometry;
5. dopiero potem wrócić do Home root -> variant -> CO1/CO2 -> boiler image.

## Evidence status

[HARD RAW]
- table 0x08054450
- 20 B bitmap descriptors
- 151/152 dimensions and pointers
- 47290 direct resource IDs 151/152
- 47334 caller chain 484B0 <- 3E...30
- param_7 provenance

[OPEN]
- exact bitmap payload decoder
- exact semantic class of 47290
- exact parent path of 160/161 bottom-bar/config button
- Home variant -> concrete CO1/CO2 instantiation
