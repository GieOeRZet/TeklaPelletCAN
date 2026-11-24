# AUTONOMOUS-PASS-108-VIEW-CALLBACK-DUAL-CLOSURE-2026-11-23

## HARD
Dokładny raw snippet `analiza/FW2213TK-2026-11-20/raw-snippets/0807eb36-decompiled.c.txt` pokazuje pełne ciało `FUN_0807EB36`:
- iteruje `uVar1 < *(byte *)(this+0x3B8)`;
- dopasowuje `sender == *(int *)(this+0x3B4) + uVar1*0x274`;
- wywołuje `FUN_0803EC18(*(undefined4 *)(this+0x3C), uVar1 & 0xffff)`.

W połączeniu z wcześniej źródłowo zamkniętym `FUN_0807EB00` daje to dwa różne callbacki korzystające z tego samego rejestru wierszy:
- `0x0807EB00 -> 0x0803C064` (dispatcher menu/class),
- `0x0807EB36 -> 0x0803EC18` (registry/model refresh dispatcher).

## Granica
To **nie** dowodzi, że `0x0803EC18` jest końcowym konstruktorem ekranu ani że każdy widget ma osobny callback. Nie przypisuję tu semantyki przycisku poza tym, co wynika z kodu.

## Weryfikacja
CSV zachowuje offset bazowy, stride, count i target obu handlerów. Test sprawdza obie ścieżki.
