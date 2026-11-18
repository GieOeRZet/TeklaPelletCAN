# FW2213TK – analiza Ghidra

Wynik automatycznej analizy `FW2213TK.bin` (sha256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`, 2 031 616 B).

- Procesor: ARM:LE:32:Cortex (Cortex-M, prawdopodobnie STM32). Dla kodu i klasycznych danych adres funkcji odpowiada `0x08000000 + raw_offset`. Uwaga: wskaźniki do części tekstów/assetów używają osobnej przestrzeni przesuniętej o `0x10000`; nie wolno stosować tego przesunięcia do adresów funkcji.
- Ghidra 12.2 (build ze źródeł), JDK 25, `analyzeHeadless`, domyślne analizatory
- `functions.txt` – adres, nazwa (`FUN_*`, brak symboli), rozmiar w bajtach
- `strings.txt` – zdefiniowane stringi z adresami
- `decompiled.c` – dekompilacja wszystkich wykrytych funkcji (1157)

Uwaga: analiza surowa, bez map peryferiów. `FUN_08001ce8` (24 kB) to najpewniej tablica danych rozpoznana jako kod.
