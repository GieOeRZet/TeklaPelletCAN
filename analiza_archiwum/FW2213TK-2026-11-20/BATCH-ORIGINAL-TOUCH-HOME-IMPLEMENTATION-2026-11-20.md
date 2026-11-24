# TeklaPelletCAN — ORIGINAL TOUCH HOME SCREEN IMPLEMENTATION
Data: 2026-11-20

## Cel
Zamiast budować osobny "ładny" mockup, produkcyjna karta Classic ma dostać ekran Pulpit/Home możliwie bliski fizycznemu Igneo Touch, ale bez utraty istniejącej logiki HA.

## Przebieg wielotorowy

### PASS 1 — źródło UI
Zweryfikowano `web/tekla-panel-card.js`:
- `_main(ctx)` jest jedynym rendererem ekranu głównego.
- Semantyczne eventy pozostają w HTML: `data-go`, `data-act`, `data-kind`, `data-back`.
- `_render()` nadal steruje stanem, alarmem, trybem kotła, temperaturą, paliwem i pompami.
- Dotyk jest obsługiwany przez istniejące handlery bazowego silnika.

### PASS 2 — bitmapy FW
Użyte zasoby są bezpośrednio z tablicy BitmapData firmware:
- 051 = niski zasobnik
- 052 = normalny/pełny zasobnik
- 053 = rezerwa/E
- 077 = MENU
- 115 = szybkie ustawienia / zasilanie
- 144 = CO1
- 174 = CWU

Wspólna reguła payloadu:
`file_offset = runtime_pointer - 0x08010000`

RGB565 i A8 zostały wcześniej zweryfikowane na całym atlasie.

### PASS 3 — hopper
Nie kopiujemy błędnej starej logiki wizualnej bezpośrednio.
Produkcja korzysta z:
- `pct <= 0 -> 053`
- `0 < pct < 0.15 -> 051`
- `pct >= 0.15 -> 052`

To jest warstwa wizualna; źródłowy BIN nadal ma dynamiczne 051/053 na obiekcie +0x5A8 i stałą warstwę 052 na +0x5D4.

### PASS 4 — interakcja
Nowa warstwa **nie tworzy własnego systemu kliknięć**.
Najpierw wykonywany jest oryginalny:
`baseMain.call(this, ctx)`

Dzięki temu:
- klik MENU nadal prowadzi do MENU,
- klik paliwa nadal otwiera ekran/okno paliwa,
- klik palnika nadal prowadzi do PALNIK,
- klik CO nadal prowadzi do OGRZEWANIE,
- klik CWU nadal prowadzi do WODA,
- klik zasilania nadal otwiera szybkie ustawienia,
- alarm pozostaje aktywny,
- istniejące usługi HA pozostają niezmienione.

Patch podmienia tylko mark-up SVG → IMG.

### PASS 5 — brak pakietu bitmap
Jeżeli któregokolwiek z siedmiu wymaganych plików nie można załadować, moduł wycofuje się i pozostawia bazowy renderer.
Nie ma sytuacji, w której brak grafiki psuje całą kartę.

### PASS 6 — cache / HACS
Bitmapy są ładowane względnie względem `import.meta.url`, więc działają z katalogu karty.
Do URL dodawany jest timestamp cache-bust.

### PASS 7 — responsywność
Istniejące pozycjonowanie bazuje na `cqw`; patch zachowuje ten model.
Nie wprowadza stałego 480×272 w CSS karty HA.
Grafiki dostają wymiary zgodne z geometrią bazowego ekranu.

### PASS 8 — separacja
Nowy plik:
`web/teklapelletclassic-touch-main.js`

Karta ładuje go po pełnym załadowaniu silnika:
`web/teklapelletclassic-card.js`

Nie modyfikujemy bezpośrednio logiki CAN, usług, encji ani zapisu parametrów.

## Zmienione pliki

1. `web/teklapelletclassic-touch-main.js`
   Produkcyjna bitmapowa warstwa Home.

2. `web/teklapelletclassic-card.js`
   Ładuje warstwę Touch Home po silniku.

## Ważne
To jest **prawdziwy ekran działającej karty**, a nie statyczny obraz.
Cała istniejąca ścieżka:
`HA state -> _render -> _main -> data-act/data-go -> handler -> service`
pozostaje aktywna.

## Następny krok
Po Home należy tym samym sposobem przejść przez:
1. okno szybkich ustawień,
2. Ogrzewanie,
3. CWU,
4. Palnik,
5. Menu,
6. Program,
7. wszystkie strony ustawień.

Zasada: najpierw zachować działanie, potem wymieniać warstwę graficzną na zweryfikowane bitmapy/animacje FW.
