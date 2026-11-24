# AUTONOMOUS-PASS-109-RESOLVER-T1-T2-RECONCILIATION-2026-11-23

## HARD
Źródła: dokładne `resolver_t1.csv` i `resolver_t2.csv` z gałęzi ChatGPT.
- T1: 49 rekordów.
- T2: 372 rekordy.
- Porównanie kluczy `ui_key`: **0 wspólnych kluczy**.
- T1 ma regułę `PID=value+inst-1`; T2 ma `PID=value`.

Wniosek: na poziomie tabel resolverów nie ma konfliktu klucza UI wymagającego arbitrażu T1/T2. Wcześniejsza zasada „T1 baza+instancja, T2 bez instancji” jest zgodna z polami `rule` źródłowych tabel.

## Granica
Brak kolizji kluczy nie dowodzi, że każdy presenter używa tylko jednej tabeli; nie zastępuje analizy callsite resolvera.
