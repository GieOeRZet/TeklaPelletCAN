# Bitmapy panelu (`web/img/panel/`)

189 plików PNG (`000.png`–`187.png` + `76b.png`) wyodrębnionych z firmware oryginalnego panelu dotykowego
Igneo Touch (tablica bitmap RGB565+A8 pod adresem `0x54450` w obrazie `FW2213TK.bin` — patrz
[`rejestry/PANEL-FW.md`](../rejestry/PANEL-FW.md)). Używane przez `web/teklapelletclassic-engine.js` do
odwzorowania wyglądu oryginalnego panelu 1:1 w karcie/aplikacji/portalu urządzenia.

**Własność:** grafiki są własnością Estymy (wszelkie prawa zastrzeżone) — zostaną usunięte na wyraźną prośbę
właściciela praw (patrz `rejestry/PANEL-FW.md`).

## Jak sprawdzać bitmapę (metodologia — WAŻNE)

Podczas pracy nad kartą w listopadzie 2026 wielokrotnie okazywało się, że renderowanie wielu bitmap naraz w jedną
"siatkę kontaktową" (compositing wielu obrazków w jeden duży plik przez PIL) **wprowadzało błędy przesunięcia
etykiet** — podpis pod obrazkiem nie zawsze odpowiadał faktycznie wklejonemu obrazkowi (błąd w skrypcie
wklejającym, nie w samych plikach). Doprowadziło to kilkukrotnie do pomylenia numerów bitmap i wdrożenia złej
grafiki w kodzie.

**Zasada na przyszłość: zawsze weryfikuj POJEDYNCZYM, niezależnym odczytem pliku** (`Read` na konkretnej ścieżce
`web/img/panel/NNN.png`), nigdy tylko przez złożony podgląd wielu obrazków naraz. Siatka kontaktowa (ten dokument
zawiera link do wygenerowanego `tools/bitmap_contact_sheet.py`, patrz niżej) jest dobra do **pierwszego
rozeznania** "gdzie mniej więcej szukać", ale ostateczne potwierdzenie numeru zawsze przez pojedynczy odczyt.

Przydatna technika dodatkowa: porównanie pikseli przez PIL (`Image.open(f).getpixel((x,y))`) gdy różnica między
dwoma podobnymi bitmapami (np. stan normalny/aktywny przycisku) jest zbyt subtelna, żeby ocenić ją wzrokiem na
małej miniaturze.

## Tabela: selektor CSS → numer bitmapy (wyciągnięte z kodu, `web/teklapelletclassic-engine.js`)

Źródło prawdy — wygenerowane automatycznie z `U(NNN)` w pliku silnika (funkcja `U` buduje URL do
`img/panel/NNN.png`). Jeśli kod się zmieni, ta tabela się zdezaktualizuje — **nie kopiuj jej ślepo, sprawdź
źródło przy wątpliwościach**.

| Bitmapa(y) | Selektor / element | Opis (potwierdzony wizualnie w listopadzie 2026) |
|---|---|---|
| `070` | `.sl i` | Gałka (uchwyt) suwaka — wspólna dla wszystkich typów suwaków. |
| `023` | `.cell+.cell::before` | Szczelina/rowek między kafelkami paska dolnego (pulpit) — ciemny pasek z czarną linią na środku, w pseudo-elemencie wypełniającym realny `gap` flex. |
| `006` / `007` | `.box` / `.box:active` | Pusty przycisk prostokątny (tło), stan normalny/aktywny. |
| `006` / `007` | `.opt` / `.opt.on` | Przycisk wyboru opcji (lista wyboru w dialogu), stan normalny/zaznaczony — **ten sam plik co `.box`**, tylko inna klasa docelowa. |
| `006` / `007` | `.tag` / `.tag:active` | Przycisk-plakietka (etykieta klikalna), normalny/aktywny. |
| `019` / `020` | `.tr .tb` / `.tr .tb.ck` | Przełącznik (checkbox-like) w wierszu ustawień — niezaznaczony/zaznaczony. |
| `054` | `.ftk.pk` | Tło/ramka dialogu wyboru paliwa (`pk` = paliwo). |
| `056` / `057` | `.fmp` / `.fmp.sel` | Mapa/siatka wyboru (prawdopodobnie wybór dnia w harmonogramie) — normalny/zaznaczony. |
| `102` / `103` | `.bpm:not(.sm)` / `:active` | **Duży przycisk „−”** (edytory wartości: kocioł, nastawy generyczne `_prDlg`/`_q2Dlg`/`_spDlg`) — normalny/wciśnięty. Rozmiar 155×38, dopasowany do proporcji dużego `.bpm` (nie do `.sm`). |
| `117` / `118` | `.bpm.pl:not(.sm)` / `:active` | **Duży przycisk „+”** — analogicznie do 102/103. |
| `104` + `168`/`169` | `.bpm` (wariant mały `.sm`, kompozyt) | Mały przycisk „−” (dialog CO/CWU, `_cDlg`): tło `168`/`169` (normalne/aktywne, 52×36 — dopasowane do `.sm`) + nałożona kreska `104` (sama myślnik, bez tła). |
| `119` + `168`/`169` | `.bpm.pl` (wariant mały `.sm`) | Mały przycisk „+” — analogicznie, nakładka `119` (sam plus). |
| `110` / `111` | `.qok` | Duży przycisk „OK” w dialogach (potwierdzenie suwaka/edycji). |
| `112` / `113` | `.qbg::before` / `::after` | Lewa/prawa krawędź tła dialogu suwaka (`.qbg`) — wąskie pionowe paski 10×242 z zanikaniem alpha. |
| `114` | `.qbg` | Środkowa, powtarzana (tile) część tła dialogu — pasek 10×242, `repeat-x`. |
| `160` / `161` | `.brow .cg` / `:active` | Przycisk "ustawienia/konfiguracja" w dolnym pasku ekranów — normalny/aktywny. |
| `163` | `.sl` (tor/tło suwaka) | Szary, neutralny tor pod suwakiem — wspólny dla wszystkich typów. |
| `165` | `.sl[data-act="slider"\|"bmslide"\|"cmslide"] b` | **Wypełnienie suwaka TRYBU** (off/eco/auto/komfort) — jednolity niebieski pasek. |
| `167` | `.sl[data-act="bslide"\|"cslide"\|"prslide"\|"spslide"\|"q2slide"] b` | **Wypełnienie suwaka WARTOŚCI** (temperatury, nastawy liczbowe) — tęczowy gradient niebieski→żółty→pomarańcz→czerwony. |
| `168` / `169` | `.alar.bk` / `:active`, `.fbt` / `:active` | Tło przycisku alarmu/paliwa (mały wariant, 52×36) — normalne/aktywne. |
| `184` / `185` | `.tgq` / `.tgq.on`, `.row .tgq.on` | Duży przełącznik (toggle) w wierszach ustawień — wyłączony/włączony. |

### Pozostałe bitmapy — NIEOPISANE, wymagają weryfikacji przed użyciem

Pliki spoza powyższej tabeli (większość ikon SVG-podobnych: płomień, grzejnik, kran, WiFi, ikony menu, cyfry,
strzałki, grafiki kotła 11-14 itd.) nie zostały opisane jeden po drugim — część to oczywiste ikonki rozpoznawalne
na pierwszy rzut oka (patrz rozmiary w `tools/bitmap_sizes.tsv`, wygenerowane `PIL`), ale żeby **nie powtórzyć
błędu z tej sesji** (zgadywanie numeru z pamięci / z błędnie poskładanej siatki), każdy kolejny numer trzeba
potwierdzić pojedynczym odczytem przed użyciem w kodzie — nie kopiować z tej tabeli "na pamięć", jeśli go tu nie
ma.

Pełna lista plików + wymiary (dane obiektywne, bez opisu): [`bitmap_sizes.tsv`](bitmap_sizes.tsv).

### Ważna lekcja z tej sesji: `76b.png` to NIE oryginalna bitmapa

`76b.png` (bez prefiksu zera, więc w sortowaniu alfabetycznym ląduje na końcu listy) jest plikiem
**wygenerowanym w ramach wcześniejszych prac nad kartą** — miał być korektą tonalną `076.png` ("kafelek pusty bez
czarnej dziury, skorygowany tonem do 075"). Okazało się, że miał wbudowaną niezamierzoną winietę, która przy
rozciągnięciu na duży kafelek dawała efekt widocznej "ramki". **Obecnie `.cell` nie używa już żadnej bitmapy do
tła** — zastąpiono płaskim, pionowym gradientem CSS (`linear-gradient(#6a696a,#5a585a)`), zgodnym z oryginalnym
wyglądem (patrz [`ARCHITEKTURA-KARTY-CLASSIC.md`](ARCHITEKTURA-KARTY-CLASSIC.md)). Plik `76b.png` zostaje w
repozytorium jako ślad historyczny, ale **nie jest już nigdzie referencjonowany w kodzie**.
