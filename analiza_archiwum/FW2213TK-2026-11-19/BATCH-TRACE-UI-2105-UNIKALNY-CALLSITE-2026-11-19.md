# BATCH-TRACE-UI-2105-UNIKALNY-CALLSITE-2026-11-19

## Cel
Skonsolidowanie kolejnego kroku śledzenia warunkowych widgetów CO bez wracania do geometrii.

## Nowe twarde ustalenia

### 1. 0x10F ma jeden znaleziony kodowy fan-out UI
W aktualnym materiale wyszukiwanie literalnego panel index `0x10F` prowadzi do `FUN_08031CCC`.

Ścieżka:
```
FUN_08031CCC
  -> FUN_08036FF2(context, 0x10F)
  -> FUN_0802D3E0(ui, value_10F, value_DC)
  -> FUN_08036FF2(context, 0x10F)
  -> FUN_0802D91C(ui, value_10F)
```

To wzmacnia wniosek, że `0x2105` nie jest w tej funkcji używany do tworzenia obiektów CO. Jest używany jako wejście do warstwy stanu/grafiki konkretnego UI.

### 2. 0x10E jest inną logiką niż 0x10F
`0x10E -> CAN 0x3505` jest pobierany dwa razy i progowany:
- `> 0` -> pierwszy element UI,
- `> 1` -> drugi element UI.

Nie znaleziono analogicznego użycia 0x10E jako źródła instancji `+0x12C`.

Wniosek: `0x3505` jest obecnie znacznie mocniej potwierdzone jako parametr aktywacji/ilości elementów w tym fragmencie UI niż jako bezpośredni setter obiektu CO.

### 3. 2106/2107/2108 są sąsiednimi parametrami funkcjonalnymi
Mapa panelowa potwierdzona w notatkach:
- panel 271 / `0x10F` -> CAN `0x2105`
- panel 272 / `0x110` -> CAN `0x2107`
- panel 273 / `0x111` -> CAN `0x2106`
- panel 276 / `0x114` -> CAN `0x2108`
- panel 277 / `0x115` -> CAN `0x3501`

To daje lokalny blok parametrów konfiguracyjnych, ale tylko 0x10F ma obecnie udowodniony bezpośredni fan-out do `D3E0/D91C`.

### 4. Ważna konsekwencja dla CO3/CO4
Skoro `FUN_08031CCC` pokazuje tylko dwa progi dla `0x10E`, a `0x10F` steruje osobnym stanem/grafiką, to nie należy zakładać, że cały mechanizm CO1..CO4 znajduje się w jednym miejscu.

Następny cel UI:
- znaleźć pozostałe funkcje/fragmenty, które wybierają widgety CO3/CO4,
- szukać przede wszystkim parametrów `0x110`, `0x111`, `0x114` oraz ich wartości po `FUN_08036FF2`,
- porównać ich odbiorców z `D3BC/D3CE/D3E0/D91C`,
- ustalić, czy te parametry zmieniają aktywność widgetu, tekst, grafikę czy tylko tryb.

## Czego NIE wnioskujemy
- `0x2105` nadal nie jest dowiedzione jako bezpośredni licznik CO.
- `0x3505` nie jest dowiedzione jako źródło `+0x12C`.
- geometria X/Y/W/H nie jest nowym odkryciem i nie jest celem analizy.

## Priorytet dalszego śledzenia
1. `0x110/0x111/0x114` -> wszystkie wywołania UI.
2. źródło `param_2` dla C064.
3. zawartość `DAT_0803C218`.
4. źródła `+0x16C1/+0x16D5`.
5. dopiero potem most `2105 -> aktywacja/instancje CO`.
