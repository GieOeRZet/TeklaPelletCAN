# PASS 48 — co dodaje bramka „poziom >= 3" (dziecko +0x23C)

## Wynik
- Bramka (17 wrapperow, wzorzec `ldrb [model+0x158]; cmp #3; blt; addChild(+0x23C)`) dodaje do kontenera **pole tekstowe**
  (klasa 0x080447BC, vtable 0x0807E15C), **nie przycisk "+"**. Wczesniejszy wniosek (BATCH-6154-LEVEL3, "+0x23C = increment")
  mylil handler 0x0803FB04 (inna klasa: widok z +/- na +0x23C/+0x284).
- Konstruktor bazy wiersza 0x0805A594 (wywolywany z 0x08050B30, vptr pochodnej 0x0808F638) tworzy obiekt, ale ID tekstu nie ustawia w ctor:
  pole ID jest w danych obiektu: slowo +0x24 = 0x01C60100 => **TypedText 454 = "Próg zmniejszania stopnia mocy [%]"** (potwierdzone w pamieci, L2 i L3).
- Geometria 40x30 przy x=439 (prawa krawedz wiersza).
- Dowod dynamiczny (ekran Informacje, instancja 0x20016038, emulator): na L3 obiekt +0x23C jest **podpiety** do kontenera
  (wskazniki listy dzieci wypelnione), na L2 pola linkow = 0 (niepodpiety).
- **Wizualnie: brak roznicy** L2 vs L3 (info_0/info_1 piksel w piksel, poza naglowkiem). Pole jest podpiete, ale nic nie rysuje na tym ekranie
  (prawdopodobnie tekst/wildcard ustawiany tylko dla konkretnych wierszy z wartoscia).
## Nie zamkniete
- Tabela 17 wrapperow -> TypedText -> PID (wymaga instancji kazdej klasy; w Kociol/Palnik/CO/Konfiguracja na L3 instancji 0x0808F638 nie znaleziono).
- Czy gdziekolwiek pole bywa widoczne (wymaga wywolania konstruktora/wrappera wprost w emulatorze).
Narzedzie: scratchpad probe_txt.py (skan RAM po vptr; wlaczyc do tools/ w kolejnym kroku).
