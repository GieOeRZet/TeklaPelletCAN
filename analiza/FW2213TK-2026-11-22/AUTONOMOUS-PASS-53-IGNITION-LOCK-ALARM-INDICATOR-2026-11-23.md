# PASS 53 — "zakaz rozpalenia" (kloda na kafelku palnika) i wskaznik alarmu na ekranie glownym

## Klodka na kafelku palnika (HARD: sledzenie zapisu widocznosci widgetu + kod)
- Bitmapa **72** (czerwona klodka 10x14) to obraz `0x2001B2FC` (kafelek palnika ekranu glownego). Widocznosc ustawia setter `0x0803D2E4` wolany z presentera `0x08041D3C`:
  `widoczna = (0x080472C8() == 0)`, gdzie `0x080472C8` czyta rekord **PID 0x2006 "Burner external permission"** (u8 0..1, klasa 0 "live", domyslnie 0, storage `0x20020F80`).
  => **0x2006 = 0: klodka WIDOCZNA (brak zezwolenia zewnetrznego = zakaz rozpalenia); 0x2006 = 1: klodka ukryta.** To jest wejscie zezwolenia z modulu CAN BIG (zworka/przekaznik) raportowane przez sterownik.
- Panel nie interpretuje tego dalej: PID 0x2006 ma jedyny odczyt w kodzie (`0x080472CC`), skutek po stronie panelu = tylko ikona. Blokade rozpalania wykonuje sterownik kotla.
- W emulatorze bez sterownika klodka widoczna do ok. tiku 3400 (potem zniknela — do wyjasnienia, co zapisalo 0x2006=1 po starcie polleru).
- **Emulacja stanu w naszym projekcie (pozniej):** wystarczy wyslac jako "sterownik" ramke CAN `0x584`: `42 06 20 01 <0|1> 00 00 00` (cmd 0x42, PID LE `06 20`, sub 1, wartosc). Na ekranie 1:1 zmieni to tylko ikone; realnej blokady kotla w ten sposob NIE uzyskamy (to logika sterownika).
## Wskaznik alarmu (kafelek ekranu glownego)
`0x080472B0`: zwraca 1 gdy w menedzerze alarmow jest dowolny wpis niepotwierdzony (`0x080250C8`, zlicza bit17) lub aktywny (`0x08025018`, zlicza bit16); wynik -> setter `0x0803D29C` (widocznosc znacznika alarmu). Czyli wskaznik "!" = istnieje alarm aktywny LUB niepotwierdzony.
