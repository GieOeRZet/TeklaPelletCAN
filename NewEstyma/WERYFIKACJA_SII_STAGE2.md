# Weryfikacja wyników ChatGPT SII stage 2 (gałąź ccr-be8a1bcb-5t76j0-chatgpt-sii, f17dc77) - agent UI, 2026-11-24

ChatGPT oznaczył wyniki jako STRONG (lokalnie "reconstructed runtime core", nie repo-harness). Wybrane twierdzenia powtórzyłem na prawdziwym emulatorze z repo (punkty kontrolne, firmware SHA 1d679d68...). Dowody: `data/ui_model/sii_acceptance/verification_stage2/`.

| twierdzenie ChatGPT | mój wynik | status |
|---|---|---|
| INFO: 0x3664=2213 ustawione PRZED wejściem → "v2.213 TE" | zgodne (stored 2213, tekst `igneoTouch v2.213 TE`) | FACT-DYNAMIC (potwierdzone) |
| SSID: A → `42 30 37 01 00 00 00 41`, AB → `...00 00 42 41` | zgodne | FACT-DYNAMIC |
| `<` po ABC/AB zapisuje poprzedni stan | zgodne (po B i `<` ramka dla 'A') | FACT-DYNAMIC |
| SIEĆ 9 modułów → 8 wierszy, lista posortowana po Node-ID | 0x78 (najwyższy) obcięty; kolejność rosnąca po Node-ID: 0x40,0x45,0x46,0x50,0x54,0x56,0x57,0x5B | FACT-DYNAMIC (inna kolejność odcięcia niż u ChatGPT "pominięty 0x50": u mnie pominięty 0x78; zgodne z "posortowana, limit 8") |
| 0x50/0x54: bez czwartej kolumny; nazwy | `MODUL LAMBDA Node ID=80`, `FLOWMETER 1 Node ID=84`, bez T= | FACT-DYNAMIC |
| 0x57 bez "SW" | zgodne | FACT-DYNAMIC |
| SW z PDO1 bajty 6/7: 34 12 → "v52.1c" | u mnie `SW v52.18` (b6=0x34=52, b7=0x12=18, dziesiętnie) po 10 rundach; "1c" ChatGPT = wartość z niedokończonego uśredniania (8 próbek) | ROZBIEŻNOŚĆ: format = v<b6>.<b7> dziesiętnie po ustabilizowaniu; do potwierdzenia w jeszcze jednym przebiegu |
| czwarta kolumna 0x45/0x40/0x46: "T=150" | u mnie `T=5678` (brak danych) w stanie bazowym; T=150 pojawia się po podaniu temperatury kanału | ROZBIEŻNOŚĆ stanów, nie wyników: oba zgodne z PASS 67 (5678 = brak danych) |

Niepotwierdzone przeze mnie (zostają STRONG u ChatGPT): pełne zestawy znaków (liczność), 24 znaki limit/25-26 bez zapisu, PASSWORD 0x3736, przełączniki WiFi/Zmiany zdalne (zapis 1/0 po stronie on/off), persystencja SSID, INFO L0/L1 (ikona), INFO bez odczytów PID podczas rysowania.
Zamknięcie po weryfikacji: SIEĆ ok. 85%, INFO ok. 70%, INTERNET ok. 75%. Otwarte: źródło 0x3665 i 0x2170 (INFO), SERIAL/PIN, korelacja 0x5B, dokładny timeout offline, mechanizm braku SW dla 0x57.
