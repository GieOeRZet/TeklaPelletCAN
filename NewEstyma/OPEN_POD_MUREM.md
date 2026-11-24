# Lista "pod murem" (agent UI): rzeczy, których nie udało się rozgryźć, do narady na końcu
Zasada właściciela: cel to soft 1:1; wszystko ma być wyjaśnione. Tu trafiają tylko tematy, przy których zabrakło narzędzi/danych. Nic tu nie jest odpuszczone.

1. ~~Krzywa przepływomierzy~~ ROZWIĄZANE (PASS 70): liniowa, bajt 6 = część całkowita, bajt 7 = ułamek (8.8), PID = X*1469/65536.
2. ~~Alarmy, układ L0 (przesunięcie o 80 px)~~ **ROZWIĄZANE 2026-11-24** (zdjęcie właściciela `ui_model/real_panel/alarmy_L0_foto_wlasciciela_2026-11-24.jpg`): prawdziwy panel na L0 ma NORMALNY układ (ikony użytkownik+dom po prawej, przyciski góra/dół po prawej, wpis: NR, KOD, treść, Powstanie, Potwierdz., status NIEAKTYWNY zielony / AKTYWNY czerwony). Przesunięcie ~100 px z zawinięciem to artefakt emulatora na L0 - pomijać w ocenie renderera.
3. **Tekstura strzałek alarmów (168/169)**: w binarce stała; czy przełącza się dynamicznie - brak dowodu.
4. **Zapis 0x2170 (videRoom PIN)**: emulator odrzuca (stored=0) - temat PIN-ów należy do właściciela.
5. **Ramka 0x20 04 30 01 do slave**: znaczenie bajtu 0x20 (download initiate bez rozmiaru?) i skutek po stronie slave - nie do sprawdzenia bez drugiej strony.
