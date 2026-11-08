# Wgranie zdalne (bez dostępu do urządzenia) – krok po kroku

Założenie: na ESP działa teraz firmware ESPHome PelletCAN, urządzenie jest **podpięte do CAN** i nie możesz go zdjąć.
Nowy firmware wgrywasz przez OTA ESPHome. Dane Twojej sieci **nie przechodzą** ze starego firmware na nowy
(ESPHome trzyma je w pamięci RAM sterownika Wi-Fi), dlatego wpisujesz je **do pliku** przed wgraniem – lokalnie,
bez wysyłania gdziekolwiek.

## 1. Pobierz plik
GitHub → **Actions** → ostatni przebieg „CI” na gałęzi → artefakt **teklapelletcan-firmware**:
`teklapelletcan.bin` (aplikacja) i `teklapelletcan.bin.sig` (podpis do późniejszych aktualizacji z przeglądarki).

## 2. Wpisz w plik swoją sieć (lokalnie)
Wymaga Pythona 3 (bez żadnych bibliotek), plik `tools/patch_firstboot.py` z repozytorium:
```bash
python3 patch_firstboot.py teklapelletcan.bin teklapelletcan-moj.bin \
    --ssid "NAZWA_SIECI" --password "HASLO_WIFI" \
    --ip 192.168.10.250 --mask 255.255.254.0 --gateway 192.168.10.1 --dns 192.168.10.1 \
    --device-password "HASLO_URZADZENIA"
python -m esptool image-info teklapelletcan-moj.bin     # opcjonalnie: powinno pokazać "(valid)" przy sumie i skrócie
python3 patch_firstboot.py --show teklapelletcan-moj.bin  # podgląd (hasła zamaskowane)
```
- Stały IP: te same wartości co w dotychczasowym ESPHome (`device_ip`, `device_gateway`, `device_subnet`). DHCP: pomiń `--ip`.
- Sieć **2,4 GHz** (ESP32-C6 nie widzi 5 GHz).
- `--device-password` (min. 4 znaki): hasło do sterowania kotłem; bez niego ustawisz je przy pierwszym wejściu na stronę (ryzyko: zrobi to pierwszy, kto wejdzie).

## 3. Wgraj przez OTA ESPHome
```bash
esphome upload TWOJ.yaml --device 192.168.10.250 --file teklapelletcan-moj.bin
```
(`TWOJ.yaml` to dotychczasowy plik urządzenia, używany do hasła OTA; nowsze ESPHome pozwala też `esphome upload --file … --device … --ota-password …` bez YAML.)
Plik ma ok. 1,0 MB i mieści się w partycji ESPHome (1,75 MB). Poprzedni firmware zostaje w drugiej partycji.

## 4. Co zobaczysz
Po ok. 30–60 s:
- strona urządzenia: **http://192.168.10.250/** (karta kotła), ustawienia: **/settings.html**,
- adres mDNS: `teklapelletcan-xxxxxx.local`; Home Assistant zgłosi nowe urządzenie „TeklaPelletCAN” (Integracje → Wykryte),
- **tryb: tylko odczyt** (domyślnie) – urządzenie nic nie zapisuje do kotła. Porównaj odczyty z panelem kotła, dopiero potem w Ustawieniach odznacz „Tylko odczyt”.

## 5. Gdy coś nie wyjdzie
| Objaw | Co zrobić |
|---|---|
| Brak strony pod adresem | Poczekaj 60 s. Jeśli sieć nie zadziała (zła nazwa/hasło), po ~30 s urządzenie włączy własną sieć **`TeklaPelletCAN-XXXX`** (hasło `qwerty123`) z portalem na 192.168.4.1 – potrzebujesz być w zasięgu. Wpiszesz wtedy sieć ponownie. |
| Karta „-” przy temperaturach | Ustawienia → **Dziennik**: szukaj `MCP2515` i `CAN: kociol odpowiada`. Pobierz raport (**Pobierz raport**) i wklej mi. |
| Chcesz wrócić do ESPHome | Ustawienia → Aktualizacja → **Wróć do poprzedniego firmware** (działa do czasu pierwszej własnej aktualizacji OTA, która nadpisuje drugą partycję). |
| Nowa wersja się zawiesza | Własne OTA uruchamia nową wersję „na próbę” i bez potwierdzenia po 25 s wraca do poprzedniej (przy bootloaderze z włączonym rollbackiem – patrz niżej). |

## 6. Aktualizacje później (jedno kliknięcie w przeglądarce)
Ustawienia → **Aktualizacja oprogramowania**: wybierz `teklapelletcan.bin` i plik `.sig` z artefaktu CI → *Wgraj*.
Urządzenie sprawdza **podpis ECDSA** – obcego pliku nie przyjmie. Uwaga: obecnie podpis wykonuje klucz **testowy** z repozytorium
(etap rozwojowy); przed wydaniem produkcyjnym trzeba wygenerować własny klucz (`tools/ota_sign.py init`) i dodać go jako sekret `OTA_SIGNING_KEY`.

## 7. Dziennik i raport do wysłania
Ustawienia → **Dziennik i diagnostyka**: podgląd, *Kopiuj*, *Pobierz dziennik*, *Pobierz raport* (diagnostyka CAN/SDO/Wi-Fi/pamięć + dziennik, bez haseł).
Dziennik jest w pamięci RTC, więc **przeżywa restart, panikę i rollback** – po awarii na górze zobaczysz wpisy sprzed restartu.

## Ograniczenia, o których warto wiedzieć
- To jest pierwsza wersja warstwy sieciowej: **nie była uruchamiana na prawdziwym ESP** (Wi-Fi, serwer HTTP, mDNS, OTA są sprawdzone kompilacją i w części testami na hoście). Dlatego domyślny tryb to „tylko odczyt” i jest ścieżka powrotu do ESPHome.
- Rollback automatyczny po nieudanej aktualizacji wymaga bootloadera z włączonym rollbackiem; bootloader ESPHome może go nie mieć. Wtedy ratunkiem jest ręczny „Wróć do poprzedniego firmware” albo kabel USB.
