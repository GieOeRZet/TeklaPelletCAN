# Budowanie firmware

## Wymagania
ESP-IDF **5.4.x**, cel `esp32c6`.

## Kompilacja
```bash
cd firmware
idf.py set-target esp32c6
idf.py build            # wynik: build/teklapelletcan.bin
idf.py -p /dev/ttyACM0 flash monitor
```
Pierwsze wgranie po USB wgrywa bootloader, tablicę partycji i aplikację (wszystko z `build/flash_args`).

## Testy logiki na hoście (bez ESP-IDF)
```bash
python3 tools/gen_points.py --check
cmake -S firmware/test -B build-host && cmake --build build-host && ctest --test-dir build-host --output-on-failure
```

## Stan weryfikacji
- Testy hosta: przechodzą (SDO, MCP2515, kodowanie, kolejka, dostęp, automat sieci, wersje).
- Kompilacja ESP-IDF 5.4.1 dla ESP32-C6: przechodzi (CI: `idf-build`), obraz ok. 166 KB.
- **Nie sprawdzono jeszcze na sprzęcie** (ESP + MCP2515 + kocioł).

## Wgranie przez OTA z ESPHome (migracja z PelletCAN)
```bash
esphome upload --file build/teklapelletcan.bin --device <IP> --ota-password <ota_pass>
```
Zadziała, jeśli obraz mieści się w partycji aplikacji ESPHome (ok. 1,7 MB na 4 MB flash). Układ partycji ESPHome pozostaje (chyba że wgrasz też tablicę partycji nowszym ESPHome). Na wszelki wypadek miej kabel USB i kopię starego firmware.

## Test karty w przeglądarce (bez sprzętu)
Karta z `web/` (oryginalna karta PelletCAN + `shim.js`) jest sprawdzana w prawdziwej przeglądarce na danych z silnika:
```bash
cmake -S firmware/test -B build-host && cmake --build build-host
build-host/sim_dump web/test/states.json            # silnik + atrapa kotła -> stany encji
python3 web/test/mock_server.py 8099 &              # atrapa urządzenia (API + pliki web/)
node web/test/e2e_card.js http://127.0.0.1:8099/index.html /tmp/karta.png
node web/test/e2e_screens.js                        # ekrany: palnik, CO, CWU, menu, alarmy, info
```
(wymaga Node z pakietem `playwright`).
