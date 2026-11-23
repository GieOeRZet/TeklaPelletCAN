# PASS 88 — callbacki widoków

FACT: wspólny handler rejestru wierszy FUN_0807EB00 porównuje sender z this[+0x3B4] + i*0x274 i dispatchuje FUN_0803C064(this[+0x3C],i).
FACT: siostrzany FUN_0807EB36 wykonuje analogiczny dispatch do FUN_0804EC18.
OPEN: komplet par offset widżetu -> handler dla każdej klasy setupScreen nie jest zamknięty statycznie; rejestr wierszy nie jest dowodem, że wszystkie kontrolki ekranów używają tego samego handlera.
