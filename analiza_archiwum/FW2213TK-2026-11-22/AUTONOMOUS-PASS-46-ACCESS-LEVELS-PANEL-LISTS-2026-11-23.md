# AUTONOMOUS PASS 46 — POZIOMY DOSTĘPU: LISTY PARAMETRÓW EKRANÓW USTAWIEŃ (WYKONANE W FIRMWARE) — 2026-11-23

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzia: `tools/panel_lists.py`, `tools/ui_explore.py` (v3, punkty kontrolne), `tools/ui_session.py` (`ListNav`, `set_access`, `checkpoint`), `Board.save_state/load_state`.
Dane: `data/panel_lists_by_level.csv` (+ `.md` czytelna tabela). Adresy RUNTIME (PROJECT = −0x10000).

## HARD — mechanizm poziomów dostępu
- `FUN_08037E74` (RUNTIME `0x08047E74`): `PIN 900 → 1`, `999 → 2`, `6154 → 3`, `0 → 0`, inne bez zmian; zapis do `[this+0x158]`, `this = 0x20020784` (singleton modelu z `FUN_080414BA`). Zweryfikowane wykonaniem (PIN `0999` → `this+0x158 == 2`).
- Poziom ≥ 1 dodaje do menu głównego wiersze 15..20: **Język (Language)**, **Alarm dźwiękowy** (przełącznik), **Test wyjść**, **Statystyki**, **Sieć**, **Internet** (zgodnie z tablicą klas 12, 14, 18, 16, 19, 20); nagłówek pokazuje ikonę klucza z cyfrą poziomu i wskaźnik procentowy przy ikonie domu (zmienny — przy porównywaniu obrazów maskować nagłówek).
- Kafelek palnika na ekranie głównym traci czerwoną kłódkę po wpisaniu PIN-u.
- Ekrany USTAWIEŃ („NASTAWY”) dzielą listę separatorami z ikoną klucza i cyfrą (`🔧1`, `🔧2`): pozycje poniżej separatora wymagają tego poziomu.

## HARD — listy parametrów wg klasy strony i poziomu (`FUN_0803E714` wykonana dla klas 0..0x11 × poziomy 0..3)
Funkcja czyta klasę z `model+0x12B`, poziom z `model+0x158` i zapisuje klucze paneli do obiektu strony (`+0x20`, licznik `+0xE8`). Wyniki (liczba pozycji; poziom 3 = poziom 2 w tym konstruktorze):
| klasa | ekran | poziom 0 | poziom 1 | poziom ≥2 |
|---|---|---|---|---|
| `0x00` | Kocioł | 3 | 13 | 13 |
| `0x01..0x04` | Ogrzewanie obwód 1..4 | 12 | 23 | 23 |
| `0x05` | Ciepła woda użytkowa | 8 | 12 | 12 |
| `0x06` | Solary | 3 | 7 | 7 |
| `0x07` | Bufor | 2 | 7 | 7 |
| `0x08` | Kaskada | 9 | 9 | 9 |
| `0x09` | Dodatkowy magazyn paliwa | 4 | 7 | 7 |
| `0x0A` | Palnik | 5 | 24 | 28 |
| `0x10` | **Konfiguracja** | 5 | 24 | 26 |
| `0x11` | **Statystyki** | 13 | 13 | 13 |
Pełna lista z PID-ami i nazwami: `data/panel_lists_by_level.md`. Najważniejsze:
- **Kocioł** (poz. 0): `0x2003` Boiler set manual temp (Temperatura zadana), `0x2208`/`0x2291` histerezy załączenia/wyłączenia. Poz. 1 dodaje: **klucz `0x48` (wykres „Wentylator wspomagający [%]”)**, `0x2207` minimalna temp. pomp, `0x3708` wybieg pompy, `0x3508/0x3509` cisza nocna od/do, `0x216C` min. temp. powrotu, `0x216E` czas otwarcia mieszacza, `0x3604` rezerwa paliwa, `0x3129/0x312A` ciśnienie hydrauliczne min/max.
  → zamyka P0 z 20.11: klucz `0x48` pochodzi z listy **Kotła** (klasa 0) od poziomu 1, a nie z klasy 10.
- **Palnik**: poz. 0 — korekta dmuchawy `0x2273`, moc min/max `0x2270/0x2271`, wartość opałowa `0x2292`, podawanie `0x2272`; poz. 1 (+19) — **klucz `0x47` (wykres „Moc dmuchawy modulacja [%]”)**, podawanie max `0x2257`, wstępna dawka `0x2256`, próg jasności `0x226A`, moc dmuchawy przy rozpalaniu/rozżarzaniu/wygaszaniu, czasy, **lambda `0x3605` i tlen `0x214E/0x2152`**, czyszczenie rusztu `0x2258`, pauza palnika `0x3715..0x3717`; poz. 2 (+4) — bezwładność palnika `0x2153`, ruch rusztu `0x3003`, podajnik magazynowy `0x370B/0x3700`.
- **Konfiguracja**: poz. 0 — uśrednianie temp. zewn. `0x3720`, próg lata `0x372A`, kalibracja czujnika `0x3747`, rezerwa paliwa, auto-synchronizacja zegara `0x372F`; poz. 1 (+19) — **Autoconfig activation, Main module type `0x3500`, CH expansion module type `0x3502`, Heating configuration `0x2105`, Outside temp. sensor config, Hot water configuration `0x2106`, Solar configuration `0x2108`, Buffer configuration `0x2107`, Lambda module presence** i dalsze; poz. 2 (+2) — **HALL Activated**, **Request reset alarm memory**.
  → konfigurację określającą widoczność menu (`0x2105..0x2108`) użytkownik zmienia w **Konfiguracji od poziomu 1**.
- Klucze nierozwiązane tabelami rezolwera: tylko rejestr wykresów `0x48` (`0x47` w klasie Palnik).

## Potwierdzenie obrazem (poziom 3)
Ekrany NASTAWY Kotła i Palnika pokazują pozycje z listy poziomu 0 u góry, a po separatorze `🔧1` pozycje poziomu 1 z ikonami wykresów przy „Wentylator wspomagający [%]” i „Moc dmuchawy modulacja [%]”.
Automat `ui_explore` zebrał 16/16 ekranów poziomu 3 (menu, urządzenia, ich strony ustawień, Konfiguracja, Test wyjść, Statystyki, Sieć, Internet); poziomy 0–2 w toku (porównanie zrzutów dopisane w kolejnym passie).

## OPEN
1. Poziom 3: konstruktor list go nie rozróżnia od 2; 17 bramek poziomu 3 (PASS 12–14 z 20.11) odpowiada za dodatkowe dzieci w drzewie widżetów — zmapować na ekrany (porównanie zrzutów L2 vs L3).
2. Klasa 8 (Kaskada) i 9 (Dodatkowy magazyn paliwa): ukryte w menu w domyślnej konfiguracji (parametry `0x11C`, `0x122`, `0x3525`); nie wyrenderowane.
3. Zmiana wartości parametrów w ekranach USTAWIEŃ (dialogi edycji, zapis przez `0x08011812`, skutki dla ramek `0x584`).
4. Nazwy pozycji po polsku (z TypedText) — powiązać z PID dla wszystkich list.
