# Raport środowiska emulatora — 2026-11-23

## WYNIK
Emulator **nie może zostać uruchomiony w tym środowisku**. Test został wykonany zgodnie z instrukcją; nie obchodzę błędu. Zgodnie z PROMPT_CHATGPT_UI.md pomiary dynamiczne/T1 wracają do Claude, a ja wykonuję wyłącznie statykę C1–C10.

## System i zasoby
- uname -a: `Linux b293dc500931 6.18.57 #1 SMP Tue Oct 20 21:56:04 UTC 2026 x86_64 GNU/Linux`
- Python: `Python 3.13.5`
- nproc: `5`
- RAM: 5947 MB total, 1126 MB used, 4821 MB available, swap 0
- df -h: filesystem 32G, used 7.2M, available 30G
- test timeout: `timeout 5 sh -c 'sleep 10'` -> exit 124, więc mechanizm timeout działa
- procesy w tle: **działają między poleceniami** (test sleep 2 zakończony plikiem /tmp/bg_survive)
- zapis plików lokalnych: TAK
- lokalne git commit/push: nie można potwierdzić; repo nie jest dostępne lokalnie

## Sieć / Git / PyPI
- `git clone https://github.com/GieOeRZet/TeklaPelletCAN.git`: **BŁĄD** `fatal: unable to access 'https://github.com/GieOeRZet/TeklaPelletCAN.git/': Could not resolve host: github.com`
- `git fetch origin ccr-be8a1bcb-5t76j0`: nie wykonano w repo, ponieważ nie dało się uzyskać repo przez sieć; ten sam brak DNS uniemożliwia fetch.
- `pip install -q unicorn capstone pillow numpy`: **BŁĄD**: 5 prób połączenia z PyPI zakończonych `Temporary failure in name resolution`; końcowo `ERROR: Could not find a version that satisfies the requirement unicorn`.
- GitHub connector pozostaje dostępny do odczytu/zapisu plików repo, ale nie zastępuje lokalnego `git fetch/pull` ani instalacji PyPI.

## Biblioteki
- unicorn: **BRAK**, ModuleNotFoundError
- capstone: **BRAK**, ModuleNotFoundError
- PIL: OK, 12.3.0
- numpy: OK, 2.3.5

## Firmware
- /mnt/data/FW2213TK_kopia.bin: **TAK**, 2,031,616 B
- SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071` — zgodny z kanonicznym FW
- .git/info/exclude: **NIE MOGĘ SPRAWDZIĆ**, brak lokalnego checkoutu repo; firmware nie został commitowany.

## Test renderera / ui_explore / pid_diff
Nie uruchomione, ponieważ wymagają modułu Unicorn, którego nie można zainstalować z powodu braku DNS/PyPI. Nie obchodzę tego przez alternatywny emulator ani ręczne podmienianie bibliotek.

## Konkluzja
**Emulator: NIE.** T1 nie przejmuję. Dalsza praca: wyłącznie statyczne C1→C10, bez własnych targetów poza kolejnością z TODO/PROMPT.
