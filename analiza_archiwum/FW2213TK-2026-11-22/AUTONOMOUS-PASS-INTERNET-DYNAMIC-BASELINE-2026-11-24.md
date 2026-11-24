# AUTONOMOUS-PASS — INTERNET dynamic baseline — 2026-11-24

## FACT-DYNAMIC
Po rzeczywistym boot/configuration/access/navigation ekran INTERNET został osiągnięty przez trzy rzeczywiste gesty przewijania MENU.

Zaobserwowany układ:
- SSID:
- PASSWORD:
- SERIAL:
- PIN:
- WiFi — przełącznik.
- Zmiany zdalne — przełącznik.
- nagłówek INTERNET.

Dowód lokalny: /mnt/data/internetnav/internet.png

## FACT-DYNAMIC — navigation
Pozycja INTERNET jest osiągalna jako pozycja menu widoczna obok SIEĆ; w aktualnym skonfigurowanym menu jest to row 18.

## FACT-DYNAMIC — aktualny test PID
Próba wstrzyknięcia PID 0x373E=1 wprost przez CAN 0x584/0x42 nie spowodowała różnicy obrazu po 50 tickach. Nie jest to dowód braku obsługi; test wymaga powtórzenia z pełnym oknem odpowiedzi i dłuższym settle.

## OPEN
- pełna korelacja PID → widget dla WiFi i Zmiany zdalne.
- status 0x373D.
- SSID editor.
- PASSWORD editor.
- SERIAL/PIN formatting.
- save/cancel/keyboard.
- 0x5B correlation.