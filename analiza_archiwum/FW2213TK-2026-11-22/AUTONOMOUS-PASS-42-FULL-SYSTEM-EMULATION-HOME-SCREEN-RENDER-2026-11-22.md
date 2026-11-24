# AUTONOMOUS PASS 42 — EMULACJA SYSTEMOWA (FreeRTOS + LTDC + DMA2D) I RENDER EKRANU GŁÓWNEGO Z FIRMWARE — 2026-11-22

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`.
Obraz: `data/screen_home_emulated.png` (480×272). Narzędzia: `tools/cortexm_rtos.py`, `tools/stm32_dma2d.py`, `tools/render_screen.py`, `tools/test_render_screen.py`.

## Dlaczego to powstało
Dotychczasowy emulator (`emu_startup.py`) wykonywał tylko kod startowy i pojedyncze funkcje. Do UI (ekrany, widżety, nawigacja po dotyku, wartości z CAN) potrzebny jest działający system: scheduler, przerwania i peryferia graficzne.
Zbudowano więc emulator systemowy, który uruchamia **prawdziwe zadania firmware** i pozwala obserwować wynik jako obraz.

## HARD — zadania FreeRTOS firmware (nazwy z TCB `+0x34`)
`EstymaTask` (pierwsze, start przez `svc`), `GUITask` (TouchGFX `taskEntry`), `CanRxTask`, `CanTxTask`, `IDLE` — priorytet 2 dla czterech pierwszych, IDLE 0. Ready lists: `0x200240C4` (prio 0), `0x200240D8` (1), `0x200240EC` (2).
Handlery wyjątków z tablicy wektorów (RAW 0): SVC `0x08068175`, PendSV `0x08068119`, SysTick `0x08067FF3` (RUNTIME); `vPortStartFirstTask` `svc #0` @`0x08068198`. `pxCurrentTCB` = zmienna z literału `0x08068174+0x34`.

## HARD — TouchGFX / sprzęt wyświetlacza
- **LTDC** (IRQ 88, wektor 104 → `0x0807499B`): ISR `0x0807499A` czyta `LTDC_ISR` (`0x40016838`) bit0 (line interrupt), czyści go (`ICR`), przełącza `LIPCR` między dwiema wartościami z RAM `0x20024884` i przy jednej z faz wywołuje `signalVSync()` (`0x08066A68`: `xQueueGenericSendFromISR` do kolejki vsync `[0x20005F24]` + `PENDSVSET`); przy drugiej woła metodę vtable `+0x18` obiektu `[[lit]]`.
- Konfiguracja LTDC zapisana przez firmware: warstwa 1 włączona, **RGB565 (PFCR=2), 480×272** (AWCR/BPCR), bufor ramki **`0xC0000000`** (SDRAM), pitch 960 B; **podwójne buforowanie** — po renderze CFBAR wskazuje drugi bufor `0xC003FC00` (przesunięcie `0x3FC00` = 480·272·2).
- **DMA2D** (IRQ 90, wektor 106 → `0x080749EB`): ISR czyta `DMA2D_ISR` (`0x4002B004`) bit1 (TCIF), czyści go i woła metodę vtable `+0x14` obiektu `[[lit]+4]`, która ostatecznie oddaje semafor bufora ramki. GUITask czeka na ten semafor (`takeFrameBufferSemaphore` `0x08066A2E`, uchwyt `[0x20005F20]`) — bez zasymulowanego DMA2D GUI stoi.
- Funkcje `OSWrappers` TouchGFX: `0x08066A04` inicjalizacja (semafor + kolejka vsync), `0x08066A2E/A3A/A48/A56` take/give/tryTake/giveFromISR semafora bufora, `0x08066A68` `signalVSync`, `0x08066A8E` `waitForVSync`; `0x080661D4` to pętla `taskEntry` (`czekaj vsync → vtable+0x54`). 

## HARD — wynik: ekran główny wyrenderowany przez firmware
Po 3000 tikach (tick = 100 000 instrukcji; ok. 9 s) i wstrzykiwaniu LTDC co 10 tików firmware wykonał **1352 operacje DMA2D** (760× M2M RGB565 kopie, 592× R2M RGB565 wypełnienia; blend/PFC nie wystąpiły) i narysował ekran główny:
godzina `0:00`, dzień `Poniedziałek`, duża wartość `0.0`, stan `Wyłączony`, obraz kotła Tekla, okienko `0 AUTO`, dolny pasek 7 kafelków (MENU, zasobnik `180kg`, palnik z kłódką, obwód grzewczy `1`, dwa puste, przycisk zasilania z zieloną kreską).
Wszystko wynika z kodu i danych firmware (czcionki, bitmapy, TypedText PL — język domyślny 0); **nie zadano żadnych danych kotła** (brak ramek CAN), dlatego wartości są domyślne. To dowód, że emulacja wykonuje rzeczywiste UI, a nie jego odtworzenie.

## Poprawki modelu wyjątków (ważne dla kolejnych agentów)
1. SysTick tylko po starcie schedulera (po pierwszym `svc`) — wcześniej wywalało się na `pxCurrentTCB` = ?.
2. Zapis `ICSR.PENDSVSET` zatrzymuje emulację **po** instrukcji zapisu (jednorazowy hook na następnej instrukcji); zatrzymanie w hooku zapisu wykonywałoby instrukcję w kółko. PendSV ma być natychmiastowy (portYIELD).
3. **Wyrównanie ramki stosu (STKALIGN)**: bit 9 xPSR zapamiętuje dopełnienie o 4 B; bez tego SysTick w środku `memcpy` psuł SP i dawał skok pod `0x2C`/NULL.
4. Realistyczny tick: ~100 tys. instrukcji/ms; przy 2000 instr/tick EstymaTask (synchronizacja 660 rekordów) nigdy nie oddawała CPU, a GUITask głodował.
5. Lazy FPU stacking (`EXC_RETURN` bit 4) nie jest modelowany — rejestry `s0-s15/s16-s31` nie są zapisywane przy przełączeniu; zadania używające FPU mogą się wzajemnie zakłócać (do sprawdzenia, jeśli pojawią się dziwne wartości liczb zmiennoprzecinkowych).

## Ograniczenia (czego ten render NIE dowodzi)
- Wartości na ekranie są domyślne: brak CAN, brak RTC (godzina `0:00`), brak dotyku. Zawartość po otrzymaniu danych z kotła, inne ekrany i stany wymagają wstrzykiwania ramek CAN i zdarzeń dotyku (następny krok).
- Model DMA2D obejmuje M2M/PFC/blend/R2M dla RGB565/ARGB8888/RGB888/A8; L8/CLUT, AL44 itd. zgłaszają `unsupported` (w tym przebiegu 0).
- `Board` nie modeluje NVIC (priorytety), DMA, timerów, flasha/EEPROM, I2C/SPI; peryferia poza LTDC/DMA2D to zwykła pamięć.
- Kolejność/czas względem rzeczywistego sprzętu jest przybliżony (1 tick = 100 000 instrukcji).

## OPEN / następny atak
1. Wstrzyknięcie ramek CAN (`0x584/0x42`) do `CanRxTask` przez IRQ CAN2 RX0 (IRQ 64) → obserwacja zmiany ekranu (temperatury, stan kotła).
2. Zdarzenia dotyku (kontroler dotyku — sprawdzić, przez co czyta firmware: I2C/SPI/ADC) → przejścia między ekranami, test wszystkich wierszy menu (PASS 41) wprost jako obrazy.
3. Eksport wszystkich ekranów do PNG i powiązanie `ekran → widżet → zasób → PID` (obrazy + tablice z PASS 35/36/40).
4. Zapis/odczyt `currentLanguage` i render w innych językach (PASS 39) jako obrazy.
