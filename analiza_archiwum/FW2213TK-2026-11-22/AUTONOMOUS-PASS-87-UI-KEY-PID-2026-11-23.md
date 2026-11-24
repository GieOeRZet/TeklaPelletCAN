# PASS 87 — UI key → PID closure

## Ustalenia
- FACT: klucz 0x000E → PID 0x2004, resolver_t2.
- FACT: klucz 0x0029 → PID 0x216F, resolver_t2.
- FACT: klucz 0x002A → PID 0x4000, resolver_t2.
- FACT: klucz 0x0121 → PID 0x370A, resolver_t2.
- STRONG: wszystkie cztery są mapowaniami typu PID=value; nie ma potrzeby modelowego wzoru dla tych przypadków.
- OPEN: pozostałe klucze, które w przyszłych przebiegach nie pojawią się w resolverach, wymagają osobnego śledzenia w kodzie modelu.
