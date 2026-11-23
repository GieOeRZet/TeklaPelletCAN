# PASS 89 — reguły widoczności

FACT: 0x350D = Pressure sensor, 0x350A = Return to boiler temperature sensor, 0x2277 = Boiler pump state, 0x370A = Boiler image selector.
FACT: helper PROJECT 0x08054848 wylicza A95=(0x22A1!=4) i A69=(0x22A1==4 && 0x2301==1).
STRONG: istniejące oczekiwania UI wskazują odpowiednio etykiety Ciśnienie=, T. powrotu=, bitmapę 138 i obraz kotła.
OPEN: dokładne identyfikatory widgetów (+0x25/+0x24) dla wszystkich czterech ekranów wymagają domknięcia CFG/pid-diff; nie utożsamiono automatycznie A69/A95 z TypedText 87.
