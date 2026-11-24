# PASS 66 — czerwone tla ekranow: przyczyna = brak resetu DMA2D przez RCC w emulatorze (Claude, 2026-11-23)

## FACT
- Tlo wielu ekranow (Kociol, Palnik, Ogrzewanie, Woda, PROGRAM, listy NASTAWY) w emulatorze wychodzilo czerwone `(255,40,41)`, a prawidlowy kolor to ciemnoszary `(41,40,41)` = RGB565 `0x2945` (tlo Box w widoku). HOME, MENU, Test wyjsc, Alarmy, Kaskada, Internet byly poprawne.
- Firmware wypelnia tlo operacja DMA2D R2M z `OCOLR`. W logu operacji DMA2D: 835 wypelnien `OCOLR=0xF945` i 197 `0x2945` na jednym ekranie. `0xF945 = 0x2945 | 0xF800` (dolozona czerwien 31).
- Zapis `OCOLR` pochodzi z jednej procedury (RUNTIME 0x08070E62, PROJECT 0x08060E62; SPL `DMA2D_Init`): sklada kolor przez `OCOLR |= (R<<11 | G<<5 | B)` BEZ czyszczenia. Poprzedza ja `DMA2D_DeInit` (RUNTIME 0x08070DDC): `RCC_AHB1PeriphResetCmd(RCC_AHB1Periph_DMA2D=0x00800000, ENABLE)` potem `DISABLE` — czyli reset peryferium przez `RCC_AHB1RSTR` (0x40023810) bit 23, ktory zeruje rejestry DMA2D (w tym `OCOLR`).
- Emulator (`tools/stm32_dma2d.py`) nie modelowal tego resetu, wiec bity koloru kumulowaly sie miedzy operacjami (kazde wypelnienie czerwonym elementem dokladalo `0xF800` do wszystkich kolejnych).

## POPRAWKA
`tools/stm32_dma2d.py`: hak zapisu na `RCC_AHB1RSTR` (0x40023810); zapis bitu 23 zeruje rejestry DMA2D 0x00..0x4C. Hak dodawany przy inicjalizacji modelu peryferium (nie w callbacku emulacji kodu).
Po poprawce: wypelnienia R2M na ekranie Kociol: `0x2945` x986 + `0xF800` x46 (tylko prawdziwie czerwone elementy: ikony, segmenty harmonogramu). Tlo `(41,40,41)`. `tools/test_render_screen.py`: OK (935 kolorow).

## SKUTKI
- Wszystkie zrzuty sprzed poprawki sa nieaktualne kolorystycznie (ukladem/widzetami nie): punkty kontrolne i atlas odtworzone (`data/ui_model/atlas/`, 44 PNG).
- Na PROGRAM segmenty komfortu byly niewidoczne (czerwone na czerwonym); po poprawce widac je: Kociol Pn godz. 0-6 i 14-19, Sr 0-17 (zgodnie z dekodowaniem bit=1 -> komfort).
- Wzorzec dla renderera i testu 1:1: `data/ui_model/atlas/*.png` (np. `L0_0_screen.png`, `L0_0_settings.png`, `prog_kociol.png`, `paliwo.png`).
- OPEN: czy istnieja inne rejestry peryferiow resetowane przez RCC (LTDC, I2C, CAN), ktorych reset firmware wykonuje, a emulator nie modeluje; do sprawdzenia przy kolejnej rozbieznosci wygladu.
