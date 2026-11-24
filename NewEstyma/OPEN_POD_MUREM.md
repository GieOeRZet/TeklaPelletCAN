# Lista "pod murem" (agent UI): rzeczy, których nie udało się rozgryźć, do narady na końcu
Zasada właściciela: cel to soft 1:1; wszystko ma być wyjaśnione. Tu trafiają tylko tematy, przy których zabrakło narzędzi/danych. Nic tu nie jest odpuszczone.

1. **Krzywa przepływomierzy 0x371A/0x371E**: liniowo 5,74 x surowy do 200, powyżej nieregularnie (300→252, 500→1401, 800→183, 1000→1332). Powód nieznany (filtr/odrzucanie próbek lub inna formuła). Następny krok: statyczna analiza funkcji ~0x8006970 (zapis flow) + test z jedną wartością długo (>=40 rund).
2. **Alarmy, układ L0 (przesunięcie o 80 px)**: deterministyczne, ale mechanizm poziomu nie znaleziony w kodzie widoku (czyta go wspólny nagłówek 0x0804A20C/0x0804A566 i bramka 0x0807FCAA).
3. **Tekstura strzałek alarmów (168/169)**: w binarce stała; czy przełącza się dynamicznie - brak dowodu.
4. **Zapis 0x2170 (videRoom PIN)**: emulator odrzuca (stored=0) - temat PIN-ów należy do właściciela.
5. **Ramka 0x20 04 30 01 do slave**: znaczenie bajtu 0x20 (download initiate bez rozmiaru?) i skutek po stronie slave - nie do sprawdzenia bez drugiej strony.
