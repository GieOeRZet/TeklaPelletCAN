# BATCH — korekta kierunku: warunkowe widgety UI CO — 2026-11-19

## Korekta względem poprzedniego raportu
Geometria X/Y/W/H nie jest nowym odkryciem. Została rozpracowana wcześniej i dokumentacja projektu już traktuje ją jako ustaloną warstwę. Również nakładanie się elementów o tych samych/zbliżonych współrzędnych było wcześniejszym punktem startowym analizy: różne obiekty zajmują ten sam obszar i firmware wybiera, który z nich jest aktywny zależnie od konfiguracji/stanu.
Od tej chwili geometria jest narzędziem identyfikacyjnym, a nie głównym celem reverse engineeringu.

## 1. Najważniejsza rzecz dla panela 1:1
Właściwy problem brzmi: który obiekt/widget jest aktywowany dla danej konfiguracji i z jakiego parametru wynika ta decyzja?
Dla każdej nakładającej się grupy musimy znaleźć: widget A/B/C -> warunek -> źródło wartości -> parametr CAN/panel index -> aktywny obiekt.

## 2. Twardy trace 0x10E
W FUN_08031CCC: FUN_08036FF2(context, 0x10E) -> FUN_0802D3BC(ui, 0 < value, ...), a następnie ponownie FUN_08036FF2(context, 0x10E) -> FUN_0802D3CE(ui, 1 < value, ...).
To jest [FW]: w tym konkretnym fragmencie 0x10E jest używane jako wartość progowa dla dwóch elementów UI: value > 0 aktywuje pierwszy, value > 1 drugi.
Ten fragment nie dowodzi, że 0x10E jest liczbą CO1..CO4.

## 3. Twardy trace 0x10F / 0x2105
W tej samej funkcji FUN_08036FF2(context, 0x10F) -> FUN_0802D3E0(ui, value, auxiliary_value) oraz FUN_08036FF2(context, 0x10F) -> FUN_0802D91C(ui, value).
To jest [FW]: 0x2105/0x10F trafia bezpośrednio do warstwy stanu/grafiki UI.
W tym miejscu nie ma dowodu 0x10F -> C064 ani 0x10F -> ustawienie +0x12C.

## 4. Korekta starego tropu
Nie wolno używać starego śladu 0x08042146 -> 0x38130 jako dowodu źródła instancji. Ten trop został formalnie wycofany.
Aktualnie obowiązuje: C064 -> C218 -> +0x12B/+0x12C jako potwierdzony dispatcher/klasyfikator; inne zapisy +0x12C analizujemy osobno; źródło param_2 dla C064 nadal nie jest odzyskane.

## 5. 0x2105 jest elementem większego zestawu konfiguracji UI
FUN_08031CCC używa 0x2105 razem z innymi indeksami, m.in. 0xDC, oraz innymi parametrami tego fragmentu.
Dla repliki nie wystarczy więc implementacja if (2105 != 0) show CO. Trzeba odtworzyć cały warunek ekranowy.

## 6. Aktualny model aktywacji UI
parametr CAN -> panel index -> FUN_08036FF2 -> wartość konfiguracji -> funkcja sterująca widgetem -> widoczność / bitmapa / stan / tekst.
Równolegle: konfiguracja sprzętowa 3500/3502/350B + 16C1/16D5 -> wariant sprzętowy -> zestaw obiektów/modułów.
Niżej: typ obiektu + instancja -> dynamiczny lookup parametrów -> CAN.

## 7. Najcenniejszy następny trace
1. Wszystkie caller-y FUN_0802D3BC, FUN_0802D3CE, FUN_0802D3E0, FUN_0802D91C.
2. Rodzic/obiekt przekazywany jako ui.
3. Pola tego obiektu używane później jako bitmapa/tekst/visibility.
4. Wszystkie inne parametry używane w tym samym fragmencie FUN_08031CCC.
5. Analogiczne warunki dla CO2/CO3/CO4.
To powinno ujawnić, dlaczego elementy o tych samych współrzędnych nie są widoczne równocześnie.

## 8. Stan pewności
[FW] 0x10E -> dwa progi UI w FUN_08031CCC.
[FW] 0x10F/0x2105 -> FUN_0802D3E0 + FUN_0802D91C.
[FW] geometria jest wcześniejszym, ustalonym obszarem analizy.
[HIPOTEZA] 0x2105 jest funkcjonalnie związane z liczbą/konfiguracją obwodów CO.
[HIPOTEZA] 0x10E ma związek z dostępnością części UI zależnej od konfiguracji.

## Następny batch
Nie wracać do geometrii jako celu. Skupić analizę na FUN_08031CCC -> 0x10E/0x10F/0xDC -> konkretne obiekty UI -> visibility/bitmap/text -> warunek konfiguracji.
Równolegle kontynuować C064 -> pośrednie wywołanie -> DAT_0803C218 -> typ/instancja.
Cel końcowy: odtworzenie zachowania panela TOUCH 1:1, a nie tylko odtworzenie wyglądu.