# MULTIPASS — 47290 / 3EC18 SEMANTIC DISAMBIGUATION — 2026-11-20

## Cel
Rozstrzygnąć, czy 0x0803EC18 + 47290 oznacza stały ekran Home, ukryte warstwy ekranu, czy odrębny parametr/configuration view. Analiza wieloźródłowa: raw BIN, istniejące ślady Ghidra, mapa rejestrów i wcześniejsze XREF-y.

## PASS 1 — znaczenie ID 74..83
W 0x0803EC18 występują kolejne wywołania FUN_08036FF2 dla indeksów/panel IDs 0x4A..0x53 = 74..83.

Z istniejącej mapy panelowej:
- 74 -> 0x2252 = Burner burner feeder
- 75 -> 0x2261 = krzywa dmuchawy, 20%
- 76 -> 0x2262 = krzywa dmuchawy, 40%
- 77 -> 0x2263 = krzywa dmuchawy, 60%
- 78 -> 0x2264 = krzywa dmuchawy, 80%
- 79 -> 0x2265 = krzywa dmuchawy, 100%
- 80..83 pozostają do niezależnego zamknięcia.

To jest bardzo mocny wzorzec jednej rodziny UI/modelu: feeder + pięć punktów charakterystyki dmuchawy.

## PASS 2 — korekta interpretacji użytkownika
Hipoteza użytkownika, że 75..79 są modulacją dmuchawy dla konkretnych mocy palnika, jest POTWIERDZONA dla ID 0x2261..0x2265.
Nie są to jednak same 'poziomy mocy' jako parametry kotła. Są to wartości obrotów dmuchawy przypisane do punktów mocy kotła 20/40/60/80/100%.

74 / 0x2252 jest sąsiednim parametrem: prędkość podawania przez burner burner feeder.

Wniosek: sekwencja 74..79 wygląda jak fragment jednego ekranu/strony parametrów palnika, a nie jak sześć przypadkowych elementów Home.

## PASS 3 — ważne rozdzielenie 47290
Raw XREF:
- 47290 jest dzieckiem runtime objectu root+0x92DC w FUN_0803E5AC.
- 47290 jest sześciopozycyjnym selektorem/listą, Y=50,84,118,152,186,220.
- bitmap state pair = 151/152.
- etykiety są dynamiczne: param_7[slot], gdzie param_7 pochodzi z runtime record +0x08.
- 484B0 jest update bridge do 47334 i działa na root+0x92DC.

Istotna korekta: obecność 47290 w drzewie 0803E5AC NIE dowodzi, że 0803E5AC jest wyłącznie ekranem Home ani że wszystkie jego dzieci są jednocześnie widoczne. Wcześniejsza analiza wykazała, że drzewo zawiera silnie konfiguracyjne/parametryczne komponenty.

## PASS 4 — host/content switching
Wcześniejszy twardy wynik:
FUN_0802EADE(host, content) jest wywoływany przez:
- FUN_08048468
- FUN_080484B0
- FUN_080484F0
- FUN_08048520

Pierwsze trzy warianty przekazują host = param_1 + 0x84F4 i różne content objects; 48520 używa innego contentu.

To jest silny dowód architektury typu HOST + PODMIENIANY CONTENT, a nie modelu 'cały firmware ma jeden ekran i tylko bitmapy są niewidoczne'.

W szczególności 080484B0 jest jednocześnie mostem aktualizacji 47290 i częścią rodziny funkcji, która zmienia zawartość hosta.

## PASS 5 — Home vs page container
Najbardziej prawdopodobny model architektoniczny:
1. istnieje trwały root/container z obiektami i hostami,
2. część obiektów jest tworzona jako reusable components,
3. aktywna strona/content jest podmieniana lub odświeżana,
4. visibility/state może być sterowane runtime,
5. nie należy jednak zakładać, że cały kompletny UI wszystkich stron jest zawsze wizualnie obecny.

W przypadku 47290 mamy realny obiekt drzewa, ale jego sześć etykiet pochodzi z aktywnego modelu/configuration descriptor. To pasuje do reusable page/list component.

## PASS 6 — związek z ekranem 'Moc dmuchawy modulacja'
Istnieją dwa niezależnie zamknięte zestawy:
- bitmapy 56/57 = punkty wykresu modulacji dmuchawy,
- parametry 0x2261..0x2265 = wartości charakterystyki dmuchawy 20..100%.

Nie wolno utożsamiać bitmap 151/152 z punktami wykresu. 151/152 należą do 47290.

Zatem:
0x2261..0x2265 -> dane modelu wykresu/parametrów,
56/57 -> wizualne punkty wykresu,
47290/151/152 -> osobny sześciopozycyjny selector/list component.

To sugeruje, że 3EC18 może przygotowywać dane/stan dla strony lub modelu, podczas gdy osobny komponent renderuje konkretny fragment UI.

## PASS 7 — architektura TouchGFX
Wzorzec:
model/data -> parameter resolver -> reusable UI component -> host/content -> render/update
jest lepiej zgodny z dowodami niż model 'wszystkie ekrany są na raz i tylko visibility'.

Możliwe są ukryte/nieaktywne dzieci, ale nie wolno tego utożsamiać z całą stroną jako bitmapą. Host/content switching jest już udokumentowany.

## PASS 8 — co pozostaje do rozstrzygnięcia
Najważniejsze:
A. dokładnie ustalić, co robią indeksy 80..83 w 3EC18;
B. rozwinąć 48624 i 7EB36, które są bezpośrednimi callerami 3EC18;
C. ustalić, czy ich obiekty są hostem, contentem, page/controllerem czy modelem;
D. znaleźć writer dla record+0x08 i odzyskać sześć TypedText IDs 47290;
E. znaleźć hard edge między 0803E5AC tree a konkretną stroną/variantem.

## Stan hipotez
- '75..79 to modulacja dmuchawy 20..100%' — HARD / potwierdzone przez mapę 0x2261..0x2265.
- '74..79 są jednym fragmentem funkcjonalnym' — STRONG.
- '47290 sam jest ekranem modulacji' — NIEPOTWIERDZONE i obecnie mało prawdopodobne.
- '47290 jest reusable selector/list component zasilanym przez aktywny model' — STRONG.
- 'cały UI wszystkich ekranów jest stale zbudowany, a tylko visibility się zmienia' — NIEPOTWIERDZONE; host/content switching wskazuje na bardziej dynamiczną architekturę.
- 'na jednym ekranie mogą istnieć ukryte warstwy/dzieci' — MOŻLIWE i zgodne z architekturą, ale każdorazowo wymaga XREF/visibility proof.

## Następny atak
1. 48624 -> vtable/class/factory -> writer r4+0x08.
2. 7EB36 -> analogicznie.
3. 3EC18 -> 80..83.
4. 3E714 -> wszystkie źródła list TypedText.
5. FUN_0802EADE -> caller/content selection map.
6. Dopiero potem przypisanie 47290 do konkretnego ekranu.

