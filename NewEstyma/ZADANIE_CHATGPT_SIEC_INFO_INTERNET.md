# Zadanie dla ChatGPT: domknięcie SIEĆ / INFO / INTERNET (dynamicznie, w emulatorze)

Właściciel tematu: ChatGPT. Agent UI (Claude) nie rusza tych ekranów, dopóki nie oddasz tematu wpisem w COORDINATION.md.
Zanim zaczniesz: przeczytaj `NewEstyma/METODYKA_EMULATOR.md` (obowiązuje w całości), `NewEstyma/AUDIT_SIEC_INFO_INTERNET_2026-11-24.md` i dane `ui_model/sii_acceptance/`, `ui_model/internet_editor.json`. Gotowe narzędzia: `tools/sii_acceptance.py`, `tools/sii_editor_probe.py`, `tools/audit_siec.py`. Punkty kontrolne zrób przez `ui_prepare_cfg.py` (poziom 1), węzły `17_screen` SIEĆ, `18_screen` INTERNET, `10_screen` INFO (poziom 0 lub 1, podawaj poziom).

## A. INTERNET (priorytet)
Edytor to klawiatura rolkowa: `^`/`v` zmiana znaku, `ABC`/`abc`/`123.0`/`?!&` zestawy, `OK` dopisuje znak i zapisuje PID (zmierzone: `!` → 0x3730 = 0x21000000).
1. Kasowanie `<` i kursor: co robi, jaka ramka 0x584.
2. Wiele znaków: kolejne `OK` → który bajt/chunk (0x3730..0x3735), kolejność, limit 24/25 znaków, zachowanie po przekroczeniu.
3. Pełne listy znaków dla każdego zestawu (przejdź `^` aż do zapętlenia, zrzut + znak).
4. Anulowanie (poza OK: tap poza klawiaturą, `<` na pustym, ekran wstecz) - czy zapisuje coś.
5. Pola PASSWORD, SERIAL, PIN: czy edytowalne tapem, jaki PID, ta sama klawiatura? (PIN: tylko opis ekranu/ramki, bez zmian zapisu 0x2170 - temat właściciela).
6. Przełączniki WiFi i Zmiany zdalne: TAP w przełącznik → ramka 0x584, PID, zmiana tekstury (wstrzyknięcie PID ich nie zmienia - to już zmierzone, szukaj akcji UI).
7. Trwałość: wyjście z ekranu i powrót (SSID zostaje? skąd odczyt).
8. Korelacja z 0x5B (moduł VIDE NET WIFI w SIEĆ): czy obecność węzła 0x5B zmienia INTERNET (status 0x373D, ikona).

## B. SIEĆ
1. Wersja SW (`SW v0.0`): źródło - PDO1 bajty 6/7 (PASS 67) lub SDO; test z niezerową wersją dla 0x56, 0x57, 0x45, 0x5B.
2. Brak "SW" dla 0x57 (zmierzone): od czego zależy.
3. Czwarta kolumna (0x45 → `T=5678`): dla 0x40, 0x46, 0x78, 0x50, 0x54/0x55, 0x7A–0x7D - co pokazują.
4. 3+ moduły: kolejność (zmierzone: 0x56 przed 0x57 niezależnie od przybycia), limit 8 wierszy, co przy 9 modułach.
5. Timeout długoterminowy (>1500 tików, np. 10000): wiersz znika/oznaczony? Reappearance.
6. Identity: różne wartości vendor/product (0x1018:01/02) i brak odpowiedzi SDO - czy nazwa zależy od Node-ID czy identity.

## C. INFO
1. Skąd bierze się każdy tekst (wersja "v2.213 TE", nazwa kotła, "videRoom PIN 0", 4. linia): PID / stała / konfiguracja (wstrzyknięcie 0x3664/0x3665/0x2170 nie zmienia - ustal prawdziwe źródła: pid_diff na całym zakresie PID-ów, kandydaci z `enable_trace`).
2. Wariant nagłówka/poziomów dostępu (L0 vs L1: ikona człowieka vs klucz) i powtórne wejście/wyjście.
3. Które elementy ekranu są dynamiczne, a które stałe.

## Format wyniku
Dane w `analiza/FW2213TK-2026-11-22/data/ui_model/<siec|info|internet>/` (json + małe PNG + RUN_SUMMARY), plik opisowy krótki. Każdy test według pkt 4 metodyki. Po każdym etapie commit + push na swojej gałęzi i krótki raport. Gdy skończysz lub utkniesz: wpis w COORDINATION (co zmierzone, OPEN z warunkami, polecenia odtworzenia) - agent UI dopiero wtedy przejmuje i domyka.
