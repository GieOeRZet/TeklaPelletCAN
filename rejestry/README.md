# Rejestry kotła Estyma / Tekla Igneo Touch (CANopen) i skaner rejestrów

Ten folder zawiera **wszystko, co wiemy o rejestrach kotła**, oraz instrukcję, jak szukać nowych za pomocą firmware PelletCAN i Home Assistanta.

| Plik | Zawartość |
|---|---|
| [`REJESTRY.md`](REJESTRY.md) | **Pełna dokumentacja rejestrów** (generowana): liczby, kodowanie, rejestry wykorzystywane z opisem i miejscem użycia, wszystkie 448 parametrów z binarki panela, reszta rejestrów kotła, węzeł 86, instrukcja kontynuacji pracy. Zacznij tutaj. |
| [`katalog-rejestrow.csv`](katalog-rejestrow.csv) | **Pełny katalog** (węzeł 4 – kocioł, węzeł 86 – CAN IO BIG; 693 wiersze). Nazwa, status, opis, typ, zakres min/max, kodowanie wartości, dostęp (R / R/W), poziom menu (PIN), przykładowa wartość, jak potwierdzono, **czy rejestr jest już wykorzystany w firmware/karcie i gdzie**. Otwiera się w Excelu/LibreOffice (UTF-8). |
| [`alarmy-kody.csv`](alarmy-kody.csv) | Kody alarmów (opis z firmware i z karty). |
| [`archiwum/`](archiwum) | Stary surowy katalog ze skanów (wartości ze skanu i migawki z 19–21.10) – dla historii. |
| [`../tools/oznacz_uzycie.py`](../tools/oznacz_uzycie.py) | Skrypt przeliczający kolumny „wykorzystany” i „gdzie w firmware” na podstawie aktualnego kodu. |

## 1. Jak czytać katalog

### Kolumny
`wezel`, `index` (hex), `sub` (1 = wartość), `nazwa`, `status`, `opis / za co odpowiada`, `typ` (sub 2), `zakres min` / `zakres max` (sub 3 / 4, **surowe wartości**), `skala / kodowanie / jednostka`, `dostep`, `wartosc przykladowa (raw)`, `poziom menu (PIN)`, `w SCADA.pdf`, `grupa adresowa`, `uzycie w firmware / karcie`, `jak potwierdzone / uwagi`, `rozmiar zapisu SDO`, **`wykorzystany`** (TAK / NIE), **`gdzie w firmware`**.

### Statusy
| Status | Znaczenie |
|---|---|
| `POTWIERDZONY` | Wiemy, co to jest: zmiana na panelu zmieniła rejestr i/lub zapis z ESP zmienił panel. |
| `PRZYPISANY` | Przypisany na podstawie zgodności wartości z panelem (odczyt), bez testu zapisu. |
| `ODNALEZIONY – NIEPOTWIERDZONY` / `KANDYDAT` | Prawdopodobne znaczenie, brak dowodu. |
| `NIEZNANY` | Rejestr istnieje (odpowiada na SDO), nie wiemy do czego służy. Opis zaczyna się od „(auto)” – to opis wygenerowany z wartości i sąsiadów. |
| `NIEZNANY (otwarte)` | Pozycja menu panelu, której rejestru jeszcze nie znaleziono (wiersze bez indeksu na końcu węzła 4). |

### Kolumna „wykorzystany”
`TAK` = rejestr jest w firmware (`odczyt` – obsługa w parserze / liście odpytywania; `zapis: set_param N` – zapis z karty; `zapis: Test wyjsc …`, `set_schedule …` itd.). `NIE` = rejestr znany, ale jeszcze nieużyty. Odświeżenie po zmianie firmware: `python3 tools/oznacz_uzycie.py`.

### Kodowanie wartości (rejestry U16, sub 1, zapis `cs 0x2B` = 2 bajty)
| Rodzaj | Odczyt `raw` | Przykład |
|---|---|---|
| **flaga + bajt** (większość nastaw menu) | `raw = 256 + wartość` (młodszy bajt = wartość, bit 8 = flaga) | Wybieg pompy 13 min → `269` |
| **liczba** (bez flagi) | `raw = wartość` | Rezerwa paliwa 17 kg → `17`; Min. temp. powrotu 45 °C → `45` |
| **ułamek** | `raw = wartość × 10` | Wartość opałowa 4,6 → `46` (w flaga+bajt `302`) |
| **przełącznik** | `256` = wył., `257` = wł. | Stała pompa |
| **wybór z listy** | `256 + indeks` | Czujnik pokojowy: 0 brak … 5 CAN |
| **maska 24 bit** | bit i = godzina i | Harmonogramy (`0x2126…`, `0x2154…`, `0x2209…`) |
| **znacznik czasu** | sekundy Unix | Alarmy `0x4024…` |

Zakres z sub 3/4 jest podawany w tej samej postaci co odczyt (np. flaga+bajt 0–120 → `256…376`). Pusty zakres = rejestr bez ograniczeń albo tylko do odczytu.

### Mapa adresowa (węzeł 4)
`0x0000–0x0FFF` nieznane liczby i harmonogramy CO2 · `0x2001–0x2067` ustawienia podstawowe, tryby, zadane · `0x2101–0x2160` harmonogramy CO/CWU, CO1 tryb/zadana, parametry palnika · `0x2161–0x216F` nastawy kotła (min. powrotu, mieszacz, antylegionella) · `0x2207–0x2314` kocioł, palnik, dmuchawa, pompy, CO1 (nastawy, krzywa pogodowa), test wyjść · `0x2999–0x299F`, `0x3000–0x3174`, `0x3500–0x352B` serwis, zbiornik, liczniki · `0x3600–0x3665` zbiornik/statystyki · `0x3700–0x3728` palnik (podajnik, pauza, żarzenie), wybieg pompy `0x3708` · `0x4000–0x404D` pomiary i historia alarmów. Węzeł 86 (CAN IO BIG): wejścia/wyjścia CiA 401 (`0x6000`, `0x6200`, `0x6401`, `0x6411`).

Węzeł 4 jest przeskanowany w całości (0x0000–0xFFFF, sub 1; istnieje 593 rejestrów), więc **każda pozycja menu panelu jest w katalogu – trzeba ją tylko przypisać**.

## 2. Skaner rejestrów – instrukcja

### Do czego służy
Firmware PelletCAN udostępnia w Home Assistancie akcje (usługi) ESPHome, którymi czytasz i zapisujesz dowolny rejestr kotła. W wersji ≥ 1.4.14 **nie ma już migawek ani encji diagnostycznych** – log jest czysty, zostaje samo narzędzie skanowania.

Akcje mają postać `esphome.<nazwa_urządzenia>_<akcja>` (u autora `esphome.tekla_estyma_…`; sprawdzisz w HA: Narzędzia deweloperskie → Akcje, wpisz „sdo”).

| Akcja | Parametry | Działanie |
|---|---|---|
| `sdo_scan` | `from_index`, `to_index` (**dziesiętnie!**), `sub` (1), `node` (4) | Czyta kolejne rejestry i zapisuje wyniki w `sensor.<urządzenie>_sdo_ostatni_odczyt` (kolejne stany = log, historia encji). |
| `sdo_scan_stop` | – | Przerywa skan. |
| `sdo_read` | `index`, `sub` | Odczyt jednego rejestru (wynik jak wyżej). |
| `sdo_write` | `index`, `sub`, `value`, `size` (1/2/4) | Zapis surowej wartości. Wymaga `write_enabled: "true"` i nie działa w trybie `mirror`. Dla nastaw menu użyj `size: 2` i wartości **po zakodowaniu** (np. 256 + 13). |
| `sdo_poll_add`, `sdo_poll_clear` | `index` | Dodaje / czyści dodatkowy rejestr w cyklicznym odczycie (do restartu). |

Format wyniku: `0x3708.1 = 269 (signed 269, 4 B)`. Skan pokazuje **także rejestry, które firmware już zna** (od 1.4.14).

Przeliczanie hex → dziesiętnie: `0x0800 = 2048`, `0x2100 = 8448`, `0x2200 = 8704`, `0x2300 = 8960`, `0x3000 = 12288`, `0x3500 = 13568`, `0x3600 = 13824`, `0x3700 = 14080`, `0x4000 = 16384`.

### Ograniczenia (ważne)
- ESP wykonuje **jeden skan naraz**; kolejne wywołanie w trakcie skanu jest ignorowane. Poczekaj na koniec (ok. 10–12 rejestrów/s; blok 128 rejestrów ≈ 12–15 s).
- Część odpowiedzi ginie na magistrali (kocioł ma ruch własny i panelu). Brak odpowiedzi ≠ brak rejestru – powtórz skan bloku 2–3 razy i zsumuj wyniki.
- Rejestry, które nie istnieją, nie dają żadnego wpisu.
- Skanuj, gdy **nic nie zmieniasz na panelu** (zmiany w trakcie skanu mylą wyniki).
- Zapis rejestrów mieszaczy CO2–CO4 z ESP bywa odrzucany przez kocioł (zmienia je tylko panel).

### Odczyt wyników z HA
- Najprościej: historia encji `sdo_ostatni_odczyt` w HA (Historia → encja) – każdy rejestr to osobny wpis z godziną.
- Przez API / MCP: pobierz historię encji z **czasem w formacie ISO UTC**, np. `start_time: 2026-10-22T21:42:30Z` (nie w przyszłości). **Uwaga:** skrót `1m` oznacza *1 miesiąc*, nie minutę – używaj ISO albo `5h`.
- Odpowiedź ma limit rozmiaru – przy dużych skanach zapisz wynik do pliku i przetwarzaj skryptem (regex `0x([0-9A-F]+)\.1 = (-?\d+)`).

## 3. Jak znaleźć rejestr brakującej pozycji menu (metoda różnicowa)

1. **Wybierz jedną pozycję** menu, której nie ma w katalogu / firmware (lista w sekcji 5). Odblokuj poziom na panelu (klucz 1 / klucz 2 – PIN-y instalatora).
2. **Zanotuj wartość początkową** i zakres pozycji (z ekranu edycji, np. „0–120”).
3. **Zmień wartość na panelu na niecodzienną** (np. 13, 17, 23 – liczba, której nie ma nigdzie indziej) i zatwierdź. Nie zmieniaj niczego innego.
4. **Przeskanuj podejrzane strefy** (poniżej) i szukaj wartości: dla nastaw typu *flaga+bajt* `256 + wartość` (np. 269), dla *liczby* – samej wartości (17). Zakres sub 3/4 rejestru musi pasować do zakresu z panelu (np. 0–120 → max `376`).
5. **Strefy w kolejności prawdopodobieństwa:** blok sąsiadujący ze znanymi pozycjami tego samego menu (np. nastawy kotła: `0x2207`, `0x216C`, `0x216E`), potem `0x2100–0x22FF`, `0x3000–0x3130`, `0x3500–0x3530`, `0x3600–0x3670`, `0x3700–0x3730`, `0x0000–0x0FFF` (małe bloki), `0x4000–0x400A`. Pozycje jednego menu często leżą w zupełnie różnych blokach (Wybieg pompy = `0x3708`, Rezerwa paliwa = `0x3604`).
6. **Kilku kandydatów z tą samą wartością?** Zmień wartość na panelu na inną i odczytaj tylko kandydatów (`sdo_read`). Rejestr, który „poszedł za” wartością z panelu, jest właściwy.
7. **Pozycje bez liczby** (przełączniki, listy): zmień opcję i porównaj skany przed i po (kandydaci to rejestry `256`/`257`/`256+n`, które się zmieniły).
8. **Przywróć wartość na panelu** (albo zrób to z karty po dodaniu zapisu).

### Potwierdzenie zapisu z ESP
Po wskazaniu rejestru: `sdo_write` z wartością inną niż obecna (w kodowaniu rejestru), sprawdź, że **panel pokazuje nową wartość**, i wpisz oryginał z powrotem. Dopiero wtedy status = `POTWIERDZONY`, dostęp = `R/W`. Zakres sprawdź też zapisem wartości skrajnych (kocioł odrzuca wartości spoza zakresu).

## 4. Co zrobić, gdy znajdziesz rejestr

1. **Katalog**: dopisz/zmień wiersz w `katalog-rejestrow.csv` (nazwa, status `POTWIERDZONY`, zakresy surowe, kodowanie, poziom menu, jak potwierdzone, rozmiar zapisu) i uruchom `python3 tools/oznacz_uzycie.py`.
2. **Firmware** (`esphome/PelletCAN_packages.yaml`), na przykładzie nastaw kotła (klucze 64–65):
   - `set_param`: dopisz rejestr na końcu tablic `ix[]` (adres), `lo[]` i `hi[]` (zakres w jednostkach panelu), `lv[]` (poziom: 0 użytkownik, 1 klucz 1, 2 klucz 2); zwiększ limit `key > N`; ustal kodowanie w łańcuchu `raw = …` (flaga+bajt: `0x0100 | wartość`, liczba: bez flagi).
   - Odczyt: `case 0xXXXX:` w parserze (`low` = młodszy bajt dla flaga+bajt, `raw & 0xFFFF` dla liczby) → `publish_state` encji.
   - Nowa encja `sensor: platform: template` (`update_interval: never`), rejestr w listach odczytu `l1[]` (dwa miejsca) i `mine[]`.
3. **Karta** (`dist/pelletcan-card.js`): wpis w tablicy `PR[]`, wiersz w ekranie (`P('Nazwa', this._po(k), k)`), nazwa encji w mapie ról, wpis w liście edytora, `CARD_VER`.
4. **Wersje i dokumentacja**: podbij wersję firmware i karty; `CHANGELOG.md`, `CHANGELOG-firmware.md`, `version.json`; commit i push.

## 5. Stan na 08.11.2026 (fw 1.4.23)

### Źródła rejestrów
- **Skan kotła** (węzeł 4, sub 1): 593 rejestry odpowiadają.
- **Firmware panela FW2213TK** (analiza kodu): 448 parametrów z nazwą, typem, zakresem, wartością domyślną i dostępem – [`panel-fw-parametry-FW2213TK.csv`](panel-fw-parametry-FW2213TK.csv); mapa indeks ↔ ID panela (420 par) – [`panel-fw-mapa-indeks-id.csv`](panel-fw-mapa-indeks-id.csv).
- **Katalog** ([`katalog-rejestrow.csv`](katalog-rejestrow.csv), 693 wiersze) łączy oba źródła (`tools/scal_nazwy_panela.py`): nazwy z panela dopisane do 225 wcześniej bezimiennych rejestrów, a 76 parametrów znanych tylko z firmware panela dodane jako osobne wiersze (status „ODNALEZIONY – TYLKO W FW PANELA”). Kolumna „wykorzystany” jest przeliczana przez `tools/oznacz_uzycie.py`.

### Znalezione i wykorzystane w firmware
- **Kocioł → NASTAWY (klucz 1):** `0x2207` min. temp. pomp, `0x3708` wybieg pompy, `0x216C` min. temp. powrotu, `0x216E` czas mieszacza, `0x3604` rezerwa paliwa stop, `0x3709` moc nominalna, `0x370E` dawka wstępna, `0x3701`/`0x3703` min/max temp. spalin, `0x3122` interwał czyszczenia wymiennika.
- **Ogrzewanie 1 → NASTAWY (klucz 1):** `0x22B1`, `0x22D5`, `0x22D9`, `0x22DD`, `0x22E1`, `0x22E5`, `0x22E9`, `0x22B5`, `0x22F1`, `0x22F9`, `0x22D1`, `0x22A5`, `0x22A1` (wszystkie 13 pozycji).
- **Woda:** `0x201C` temperatura maksymalna CWU, `0x2297` antylegionella (tylko flaga wł./wył.).
- **Palnik:** krzywa wentylatora spalin `0x2268`, `0x226E`, `0x226F`, `0x2275`, `0x227A`; zapalarka `0x2253`; odczyty `0x3706` (moc), `0x3710` (zużycie), `0x3711` (czas do czyszczenia rusztu), `0x228C` (wentylator spalin).
- **Konfiguracja i alarm dźwiękowy:** 18 rejestrów konfiguracji (odczyt), `0x3506` alarm dźwiękowy, `0x3508`/`0x3509` godziny ciszy.
- **Statystyki:** `0x3610`, `0x3613`–`0x3616`, `0x3628`.
- **Test wyjść:** `0x2259` podajnik, `0x2283` dmuchawa, `0x2284` zapalarka, `0x2295` podajnik palnika, `0x2296` pompa CWU, `0x2285` wymiennik, mieszacze CO1–CO4 `0x214A`–`0x214D`.

### Wciąż otwarte
| Pozycja | Uwagi |
|---|---|
| Wymiennik (test wyjść) | Zapis `0x2285` jest w firmware 1.4.22, do sprawdzenia na kotle (czy faktycznie włącza wymiennik). |
| Mieszacze CO2–CO4 | Kocioł odrzuca zapis tych wyjść z ESP. |
| PDO | Bit „Podajnik palnika pracuje” (`PDO 0x356` bajt 2 bit 0) – prawdopodobne, do potwierdzenia testem. |
| 91 indeksów z panela, które nie odpowiadają na kotle | M.in. `0x372F`–`0x374C`, `0x228D`–`0x228F`, `0x218A`–`0x218C` – zapewne opcje innych konfiguracji. |
| Powiązanie wszystkich wierszy menu z ID z binarki | Tablica ID → tekst menu nie została jeszcze znaleziona w obrazie firmware. |

## 6. Tryb diagnostyczny (opcjonalnie)
Firmware ≥ 1.4.14 jest domyślnie „cichy”. Dodatkowe wpisy (NMT/heartbeat innych węzłów, zapytania o tożsamość `IDENT`, zmiany PDO, raport `SKAN SIECI`) włączysz w `PelletCAN.yaml`: `diag_log: "true"`. Podsłuch zapisów innych węzłów w logu ESPHome (np. zapisy panelu): `sniff: "true"`; wszystkie ramki: `can_debug: "true"`. Po zakończeniu przywróć `"false"`.
