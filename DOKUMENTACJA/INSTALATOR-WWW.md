# Instalator WWW (ESP Web Tools) — wgranie firmware bez ESPHome

Dodane w listopadzie 2026, w odpowiedzi na pytanie "czy musimy zależeć od ESPHome do pierwszego wgrania". Firmware
samo w sobie **nigdy** nie było zależne od ESPHome (czysty ESP-IDF — patrz [`FIRMWARE.md`](FIRMWARE.md), sekcja
OTA) — jedyna realna zależność była narzędziowa: pierwsze wgranie nowego/czystego modułu wymagało ESPHome
dashboardu albo ręcznego `esptool`. Instalator WWW usuwa i tę zależność.

## Co to jest i jak działa

Strona `docs/install/index.html` używa biblioteki **[ESP Web Tools](https://esphome.github.io/esp-web-tools/)**
(ta sama, z której korzystają WLED i sam ESPHome na swoich stronach instalatorów) — element
`<esp-web-install-button>`, oparty na **Web Serial API** przeglądarki (działa tylko w Chrome/Edge/Opera na
komputerze; telefony, Firefox, Safari — nie wspierają Web Serial, dla nich zostaje ręczne `esptool`, opisane na
tej samej stronie).

Instalator wgrywa **jeden plik**: `teklapelletcan-factory.bin` (pełny obraz — bootloader + partycje + aplikacja,
od adresu 0x0 — ten sam plik, który CI już generuje przy każdym wydaniu: `esptool merge_bin -o
teklapelletcan-factory.bin @flash_args`, patrz `.github/workflows/ci.yml`). Manifest (`docs/install/manifest.json`)
opisuje to jako jedną "część" (`parts`) przy offsecie `0`, dla `chipFamily: "ESP32-C6"`.

## Jak strona zawsze ma aktualną wersję (bez ręcznej pracy)

`.github/workflows/pages.yml` — osobny, niezależny workflow (NIE modyfikuje `ci.yml`):
- Uruchamia się automatycznie na `release: published` (czyli po każdym `gh release create` w `ci.yml`) oraz ręcznie
  (`workflow_dispatch`).
- Pobiera `teklapelletcan-factory.bin` z **najnowszego** wydania repo (`gh release download` bez podawania tagu —
  domyślnie najnowsze) do `docs/install/`, i wpisuje numer tej wersji do `manifest.json`.
- Publikuje `docs/install/` jako GitHub Pages (`actions/configure-pages` + `upload-pages-artifact` +
  `deploy-pages`).

Adres: **https://gieoerzet.github.io/TeklaPelletCAN/** (domena `<login-właściciela-małymi-literami>.github.io`,
automatyczna dla GitHub Pages).

## Dlaczego strona jest w `docs/install/`, a nie w `web/`

`web/` to katalog, który `firmware/main/CMakeLists.txt` (`pack_web.py`) **zagarnia w całości** (`*.html`, `*.js`,
`*.css`, `img/*`) i osadza w obrazie firmware — umieszczenie tam strony instalatora bezsensownie powiększyłoby
firmware (urządzenie nie może przecież wgrać samo siebie przez Web Serial). `docs/install/` jest poza tym
zasięgiem, więc nie wpływa na rozmiar firmware ani na żadną z synchronizacji do innych repozytoriów
(`publish-card-classic`/`-modern`/`-integration`/`-apk` w `ci.yml` nie dotykają `docs/`).

`docs/install/teklapelletcan-factory.bin` jest w `.gitignore` — nie jest commitowany, pobiera się świeżo przy
każdym uruchomieniu `pages.yml`.

## Pułapka napotkana przy wdrażaniu (ważne, jeśli workflow kiedyś przestanie działać)

`actions/configure-pages` (nawet z `enablement: true`) **nie ma uprawnień, by stworzyć stronę Pages od zera**
samym domyślnym tokenem workflow (`GITHUB_TOKEN`), choćby workflow miał `permissions: pages: write` — kończy się
błędem `Resource not accessible by integration` przy próbie "Create Pages site". To jest ograniczenie API GitHub,
nie błąd w naszym workflow. **Jednorazowe, ręczne rozwiązanie** (zrobione już w listopadzie 2026, nie trzeba
powtarzać): Settings repozytorium → Pages → *Build and deployment* → Source: **GitHub Actions** (nie "Deploy from
a branch"). Po tym jednym kliknięciu workflow działa sam przy każdym kolejnym wydaniu.

## Sterowniki USB (pytanie użytkowników)

Zależy od konkretnej płytki/chipu USB-UART, nie od naszego firmware:
- Natywne USB Serial/JTAG wbudowane w ESP32-C6 (jeśli płytka ma taki port) — żaden sterownik nie jest potrzebny
  na Windows 10/11, macOS, Linux.
- Zewnętrzny mostek USB-UART (najczęściej CP2102/CP210x albo CH340) — na Windows zwykle trzeba doinstalować
  sterownik (Silicon Labs CP210x VCP / sterownik CH340); macOS i Linux mają je zwykle wbudowane.
- Web Serial korzysta z tego samego sterownika systemowego co `esptool` — nie omija braku sterownika.

## Pliki

- `docs/install/index.html` — strona (ESP Web Tools z jsdelivr CDN + alternatywa `esptool` dla przeglądarek bez
  Web Serial).
- `docs/install/manifest.json` — manifest ESP Web Tools (nazwa, wersja, `chipFamily`, `parts`); wersja i binarka
  nadpisywane przy każdym uruchomieniu `pages.yml`.
- `.github/workflows/pages.yml` — publikacja na GitHub Pages.
