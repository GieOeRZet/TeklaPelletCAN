# PelletCAN – TODO (pełna lista, stan 2026-11-08 17:30)

Gdy Roman pyta „co do zrobienia?” – pokazać CAŁĄ tę listę (wszystkie sekcje), po aktualizacji o to, co zrobione.
Repo: GieOeRZet/PelletCAN (fw 1.4.23, karta 1.40; wersja lite w osobnym repo PelletCAN_lite). Zasady: krótko po polsku, „-” dla braków, bez template sensorów w HA, każda zmiana = bump wersji + changelogi, pełna karta (lite w osobnym repo, nie ruszamy).

## A. Po stronie Romana
- [x] Release HACS karty 1.40 / firmware 1.4.23 wydany (workflow release.yml).
- [x] W swoim yaml: `sniff: "false"` i `diag_log: "false"` (domyślne wartości).
- [ ] Rotacja sekretów: stare hasła Wi-Fi / API / OTA, wcześniej wklejony PAT; wymienić też token webhooka MCP wklejony w czacie 6.11. W repo jawne `ap_pass: "11223344"` (świadoma decyzja – tylko opisane w README).
- [ ] Repo przeniesione: używać https://github.com/GieOeRZet/PelletCAN.git (git remote set-url).
- [x] Wybieg pompy = 0, Rezerwa paliwa stop = 0 przywrócone (potwierdzone w HA 6.11).

## B. Rejestry – do znalezienia (metoda: snap → zmiana na panelu → skan różnicowy)
- [x] Snap 197 rejestrów znanych panelowi, a niewykorzystanych: `rejestry/snap-197-baseline-2026-11-06.csv` (skan: `esphome.tekla_estyma_sdo_scan`, **sub=1**, indeksy dziesiętnie; nieistniejące rejestry nie dają wpisu).
- [x] Temp. maksymalna CWU = 0x201C (u8 40–80, raw 316=60) – do podpięcia w firmware/karcie.
- [x] Antylegionella: panel ma tylko flagę 0x2297 (brak dnia/godziny w parametrach) – do podpięcia.
- [x] Krzywa wentylatora spalin = 0x2268/226E/226F/2275/227A (potwierdzone nazwą „exh. fan char. 1–5”) – do podpięcia.
- [x] Alarm dźwiękowy = 0x3506 (+ godziny ciszy 0x3508/0x3509) – do podpięcia.
- [~] Wymiennik w teście wyjść: w fw 1.4.22 = 0x2285 (węzeł 4); do sprawdzenia na kotle.
- [~] PDO 0x356 b2.0 = podajnik palnika pracuje (do potwierdzenia).
- [ ] Mieszacze CO2–CO4: kocioł odrzuca zapis z ESP (u Romana jest 1 obieg CO + CWU – niski priorytet).
- [x] Nazwy 197 nieznanych: `snap-197-nazwy-FW2213TK.csv` (z kodu panela). Do zrobienia: podpiąć użyteczne (statystyki 0x3610/0x3613–16/0x3628, serwis 0x3718, cyrkulacja CWU 0x374B/C, wentylator, ciche godziny). Było: (z tabeli panela: grupy 0x3500–0x352B, 0x3116–0x3174, 0x3630–0x366x itd.).
- 91 indeksów z tablicy panela NIE odpowiada na kotle Romana (m.in. 0x372F–0x374C, 0x228D–0x228F, 0x218A–0x218C) – inne konfiguracje.

## C. Firmware panela IgneoTouch (FW2213TK.bin) – inżynieria wsteczna
- [x] Tablica par (indeks CANopen, ID panela): 420 par @0x37576 → `rejestry/panel-fw-mapa-indeks-id.csv`.
- [x] Min / max / typ / dostęp dla 448 parametrów znalezione (`panel-fw-parametry-FW2213TK.csv`), scalone z katalogiem (`tools/scal_nazwy_panela.py`).
- [ ] Tablica ID → tekst menu (potrzebny dezasembler Thumb2 kodu menu).
- [ ] Teksty menu (UTF-16, PL/EN/CZ/RO/LT/EE/ES) zmapować na ID → nazwy dla 197 rejestrów.
- [x] Bitmapy zdekodowane (RGB565+A8, baza 0x08010000) – własność Estymy; w repo jako opcja `grafiki: pelne`, do usunięcia na prośbę właściciela praw.
- [x] Sieć na panelu: ESP jako węzeł 90 z nazwą „PelletCAN” i wersją softu (fw 1.4.0–1.4.2).

## D. Karta i firmware – funkcje
- [x] Tłumaczenia karty (11 języków, `pelletcan-lang.js`).
- [x] Wskaźnik aktualizacji (zielona dioda, INFO: autor + wersja + changelog, „odrzuć aktualizację”).
- [x] Wersja lite (publiczna, tylko podgląd) – osobne repo PelletCAN_lite. Wariant „pro” – niezdecydowane.
- [ ] Alarm start/koniec jako timestamp (device_class) w firmware.
- [ ] Źródła Statystyk, poziom CO1 i histerez kotła (potwierdzić zdjęciami panela).
- [~] Test wyjść: Pompa CWU, Podajnik palnika i Wymiennik podpięte (rejestry węzła 4); do potwierdzenia na kotle.
- [ ] Końcowe testy zapisów z karty (set_boiler_mode, set_setpoint, harmonogramy, set_param).
- [ ] Przycisk „Restart ESP” już jest (`switch.tekla_restart`) – nic do dodania.
- [ ] Epizod encji „unavailable” ok. 25 min (15:08–15:34, 20.10) – znaleźć przyczynę.

## E. Duże pomysły (niezdecydowane)
- Strona standalone na ESP (karta bez Lovelace, poziom 0), Shelly-style konfiguracja Wi-Fi przy pierwszym starcie (AP + strona).
- Aplikacja Android wyglądająca jak karta, łącząca się bezpośrednio z ESP (bez HA).
- Własna integracja HA (lista ESPHome, wspólny klucz API, klucz=wartość zamiast encji), karta instalowana z integracją.
- Bramka CAN→TCP i odcięcie od ESPHome.
- Wariant płytki PCB z jednym ESP zamiast składaka.

## F. Co może być „zajebiste” (propozycje Claude)
1. **Wbudowany skan różnicowy w ESP**: przycisk „Snap A”, „Snap B” → ESP sam publikuje listę zmienionych rejestrów (bez zasypywania historii HA, działa też bez Claude).
2. **Strona katalogu rejestrów** (GitHub Pages) generowana z CSV: nazwa, zakres, kodowanie, gdzie użyte, status.
3. **Prognoza paliwa**: kg w zasobniku, dni do końca przy aktualnym spalaniu, powiadomienie przy rezerwie paliwa (blueprint HA).
4. **Statystyki i wykresy** na karcie: spalanie/dzień, godziny pracy podajnika, liczba rozpaleń, koszt sezonu.
5. **Tryb demo karty** (dane przykładowe bez ESP) do zrzutów w README i do testów wyglądu.
6. **CI na GitHubie**: kompilacja ESPHome + lint karty przy każdym pushu, automatyczna kontrola wersji / changelogów / version.json.
7. **Bezpieczny update**: ESP sprawdza release na GitHubie i pokazuje „dostępna aktualizacja” (zawsze ręczne OTA).
8. **Zestaw diagnostyczny**: jednym przyciskiem raport (wersja, jakość magistrali, liczba ramek SDO, ostatnie aborty) do wklejenia w Issue.
9. **Alarmy po ludzku**: pełna lista kodów (rejestry/alarmy-kody.csv) z opisem przyczyny i co zrobić, w karcie i w powiadomieniu.
10. **Dokumentacja krok po kroku** (instalacja, CAN/okablowanie, zdjęcia, FAQ) – README + docs.

## G. Zrobione (skrót)
6.11: fw 1.4.15 + karta 1.18 – Raport diagnostyczny (przycisk), Snap A/B w ESP, prognoza paliwa (zużycie 24 h, dni, rezerwa) + wiersze w Statystykach, tryb demo karty (docs/demo.html, zrzuty), CI (ci.yml: wersje/changelogi, JS, kompilacja ESPHome), strona katalogu rejestrów (pages.yml + tools/gen_katalog_html.py), szablon Issue. DO SPRAWDZENIA po pushu: wynik kompilacji w Actions; włączyć Settings → Pages → GitHub Actions; wgrać fw 1.4.15 i sprawdzić Snap/raport/prognozę na żywo. Dalej: wersja LITE publiczna vs pełna dla wspierających (buycoffee).
Wybieg pompy 0x3708 i Rezerwa paliwa stop 0x3604 (fw 1.4.15, karta 1.18); czysty log (diag_log/sniff false); folder rejestry/ z katalogiem (617 wierszy), skanerem i instrukcją; tools/oznacz_uzycie.py; analiza FW panela (mapa indeks↔ID); skan 6.11: 446 odpowiedzi, 0 nowych poza katalogiem.

8.11: README pełnej wersji (jak działa, pełna vs lite, szybki start, encje, akcje, diagnostyka, ustalenia z binarki, przykłady); katalog rejestrów scalony z nazwami z FW panela (693 wiersze: 225 nazw dopisanych, 76 nowych parametrów); przegląd porządku w repo.
