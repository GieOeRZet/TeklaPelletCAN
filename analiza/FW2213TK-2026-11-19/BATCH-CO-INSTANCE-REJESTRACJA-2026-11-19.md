# BATCH-CO-INSTANCE-REJESTRACJA-2026-11-19

## Najważniejszy wynik

Instancje CO1..CO4 nie są tworzone dopiero przez runtime lookup.

Istnieje statyczna rejestracja rodzin:
- 0x2032..0x2035
- 0x2048..0x204B
- 0x2064..0x2067

W pętli r7=0..3 parametr bazowy jest rozszerzany o +r7. Przykład: 0x2032, 0x2033, 0x2034, 0x2035.

Analogicznie dla 0x2048 i 0x2064.

To jest twardy dowód czterech fizycznie zarejestrowanych rekordów parametrów CO. Runtime base + instance - 1 wybiera później właściwy rekord.

## Konsekwencja

Najbardziej prawdopodobny model:

konfiguracja instalacji
  -> aktywność/obsługa CO1..CO4
  -> wybór odpowiedniego obiektu UI
  -> runtime wybiera instancję
  -> +0x12C = 1..4
  -> base + instance - 1
  -> rekordy 2032..2035 / 2048..204B / 2064..2067

Czyli liczba obwodów nie musi powodować tworzenia rekordów. Rekordy mogą istnieć statycznie, a konfiguracja decyduje, które są aktywne/widoczne/obsługiwane.

## 0x2064..0x2067

0x2064 jest nazwane Tryb CO1, a firmware ma rodzinę czterech rekordów:
- 2064 = CO1
- 2065 = CO2
- 2066 = CO3
- 2067 = CO4

Nie oznacza to jeszcze, że wszystkie są aktywne w każdej konfiguracji.

## Nowy priorytet

1. Znaleźć miejsce decydujące, czy instancja 2/3/4 jest aktywna.
2. Połączyć to z 0x3505 / 0x10E, gdzie mamy już twarde progi aktywacji UI.
3. Znaleźć źródło param_2 dla C064 i sprawdzić, jak klasy 1..4 są wybierane.
4. Dopiero potem wrócić do 2105.

## Korekta modelu

Nie piszemy już: 2105 -> tworzy CO2/CO3/CO4.

Roboczo: konfiguracja -> aktywuje/wybiera instancję -> istniejący rekord COx -> UI + CAN.
