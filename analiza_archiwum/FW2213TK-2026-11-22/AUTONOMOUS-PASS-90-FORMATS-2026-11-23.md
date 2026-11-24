# PASS 90 — formatowanie pól

FACT: PID 0x2001 jest prezentowany jako %d.%d, skala 0.1.
FACT: PID 0x22F5 jest prezentowany jako %d; wartość 5678 oznacza brak danych.
STRONG: istniejący presenter_map.csv ma formaty %d.%d, -%d.%d i %d oraz flagę div10.
OPEN: kompletna mapa 655 PID -> formatter wymaga śledzenia wszystkich call-site formatterów.
