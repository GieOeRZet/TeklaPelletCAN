# UI rekorder — emulator panelu z logowaniem klikania (dla Romana)

Narzędzie `tools/ui_recorder.py` uruchamia emulator panelu Estyma igneoTouch z interfejsem w przeglądarce. Klikasz po ekranie jak na prawdziwym panelu, a program zapisuje do pliku **każde stuknięcie**: z jakiego ekranu na jaki przeszedłeś, który widżet kliknąłeś (adres, pozycja, tekst/bitmapa), jakie PID-y się zmieniły, jakie ramki CAN poszły, plus zrzut ekranu.

## Windows (i Linux/macOS)
1. Zainstaluj Pythona 3.10+ (python.org, zaznacz „Add to PATH”).
2. W terminalu: `pip install unicorn capstone pillow numpy`
3. Pobierz repo (gałąź `ccr-be8a1bcb-5t76j0`) i wrzuć `FW2213TK_kopia.bin` obok (firmware **nie** jest w repo).
4. Uruchom z katalogu repo: `python tools\ui_recorder.py --fw FW2213TK_kopia.bin`
   (opcje: `--level 0..3` poziom dostępu, `--config 0x350C=1 0x3525=1` konfiguracja, np. dla Kaskady i Magazynu, `--port 8765`).
5. Poczekaj ok. 20 s na „gotowe”, otwórz **http://localhost:8765**. Klikaj w obraz. Pod obrazem: wybór poziomu dostępu, pole konfiguracji (`0x2105=2 ...`), pole **notatki** (np. „tu wchodzę w ustawienia czasu”).
6. Wynik: `sesja_RRRRMMDD_GGMMSS.jsonl` (jedna linia = jedno stuknięcie lub notatka) i katalog `sesja_.../` ze zrzutami. Wyślij mi ten plik i katalog (lub wrzuć do repo).

## Android / telefon
Emulator (Python + unicorn) nie działa natywnie jako aplikacja Androida. Najprościej: uruchom go na PC i otwórz **http://IP_PC:8765** w przeglądarce telefonu w tej samej sieci Wi-Fi (kliknięcia palcem działają). Natywna aplikacja Androida wymagałaby przepisania silnika (osobny, duży projekt).

## Co jest w logu (pola JSONL)
`before`/`after` (nazwa ekranu), `vtable_*` (tożsamość ekranu), `tap` (x,y), `widget` (adres `this`, prostokąt, rola, id tekstu/bitmapy, etykieta), `pid` (zmiany względem tła; liczniki tła wyłączone), `can` (ramki TX spoza tła), `shot` (plik zrzutu). Rekorder pokazuje na żywo „ekran X -> Y” przy każdym kliknięciu.

## Ograniczenia
- Emulator działa wolniej niż prawdziwy panel (ok. 1/3 czasu rzeczywistego) — po kliknięciu poczekaj ok. 1 s.
- Wartości live (temperatury kotła, CWU, bufora, solarów) są SYMULOWANE (moduły CAN IO 0x56 i 0x45 karmione typowymi temperaturami); pozostałe wartości live (ciśnienie, temp. powrotu, lambda, kaskada) są zerami.
- Zapis do prawdziwego kotła: **brak** (emulator nie jest podłączony do magistrali).
