# Pierwsze uruchomienie na sprzęcie (bring-up)

Cel: sprawdzić **MCP2515 + CAN + kocioł** i cały silnik na prawdziwych danych. Firmware w tym etapie **tylko czyta** z kotła (tryb mirror włączony), niczego nie zapisuje i nie ma jeszcze Wi-Fi – wyniki idą na port szeregowy.

## 1. Skąd wziąć plik
GitHub → zakładka **Actions** → ostatni przebieg „CI” na gałęzi → artefakt **teklapelletcan-firmware**:
- `teklapelletcan-factory.bin` – pełny obraz (bootloader + partycje + aplikacja) do wgrania po USB od adresu `0x0`,
- `teklapelletcan.bin` – sama aplikacja (do wgrania przez OTA z ESPHome, patrz niżej).

## 2. Wgranie po USB (zalecane)
```bash
pip install esptool
python -m esptool --chip esp32c6 -b 460800 write-flash 0x0 teklapelletcan-factory.bin
```
Jeśli port się nie pojawia, przytrzymaj BOOT podczas podłączania USB. Można też użyć strony https://espressif.github.io/esptool-js/ (adres `0x0`).

## 3. Podgląd logów
```bash
python -m esptool --chip esp32c6 --no-stub chip-id   # sprawdza łączność
pip install pyserial && python -m serial.tools.miniterm /dev/ttyACM0 115200
```
(na Windows port `COMx`).

## 4. Co powinieneś zobaczyć
```
tpc: MCP2515 OK, CAN 125 kbit/s
tpc: id urzadzenia XXXXXXXXXXXX, tryb: tylko odczyt
tpc: t=5s can_ok=1 ramek=NNN (PDO N) bledy_mcp=0x00
tpc: odczyty (surowe): boiler_temp=0x… burner_state=0x2 …
```
Co sprawdzamy:
- `MCP2515 nie odpowiada` → okablowanie SPI (SCK=GPIO19, MISO=GPIO20, MOSI=GPIO18, CS=GPIO17), zasilanie 5 V modułu,
- `can_ok=0` i `ramek=0` → CAN-H/CAN-L zamienione, brak masy, zły bitrate (125 kbit/s) lub kwarc modułu ≠ 16 MHz,
- `bledy_mcp` ≠ 0x00 → problemy z magistralą (terminator, długość przewodów),
- odczyty `-` mimo `can_ok=1` → kocioł nie odpowiada na dany rejestr (to normalne dla części).

Wklej mi ok. 20–30 linii logu – na tej podstawie poprawię firmware.

## 5. Zamiast kabla: OTA z ESPHome
Jeśli na ESP jest teraz firmware ESPHome PelletCAN:
```bash
esphome upload --file teklapelletcan.bin --device <IP> --ota-password <ota_pass>
```
Miej pod ręką kabel USB i kopię poprzedniego firmware – po wgraniu tego firmware nie ma jeszcze własnej aktualizacji OTA ani Wi-Fi.
