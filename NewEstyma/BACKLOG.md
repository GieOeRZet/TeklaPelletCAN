# BACKLOG (nowe znaleziska po ustaleniu planu zamknięcia; NIE wchodzą do bieżącej pracy do czasu FREEZE)

Zasada (PLAN_ZAMKNIECIA_I_PORZADKU.md): po osiągnięciu bramki toru nowe tematy trafiają tutaj. Wpis: data, temat, kto znalazł, dlaczego ważne, szacowany koszt.

| Data | Temat | Kto | Uwagi |
|---|---|---|---|
| 2026-11-24 | Krok/zakres dialogu liczbowego mierzony tylko próbką (co 4. wiersz + wiersze dziesiętne) | agent UI | pełny przebieg zajmie ~1 h na 4 procesach; zrobić po FREEZE jeśli potrzebne |
| 2026-11-24 | Etykiety wyliczeń (enum) tylko dla IN17/Energy meter type (częściowo) | agent UI | metoda: list_enum_dialog.py, wymaga filtra szumu |
| 2026-11-24 | Stany alarm/moduł offline/dialog w macierzy pokrycia (ChatGPT etap 3 A: 1120 komórek, mierzone 133 domyślnych) | ChatGPT | dociągnąć zrzuty po zamknięciu rendererów list |
| 2026-11-24 | Timeout offline SIEĆ > 10000 tików | ChatGPT | OPEN; test z 100000 tików |
| 2026-11-24 | Źródło wypełnienia wildcardów INFO (0x3665, 0x2170) | ChatGPT | OPEN |
| 2026-11-24 | Krok dialogu liczbowego listy (list_dialog_step.py): wyniki WIARYGODNE tylko dla Kocioła, wiersze 0,1,2,4 (krok 1/1); reszta zera = błąd metody | agent UI | Pułapki: punkt kontrolny węzła `N_settings` NIE jest na górze listy (np. Palnik startuje przewinięty do "Korekta powietrza"); kolejność wierszy listy zależy od poziomu/grup (separatory z kluczem), a wiersz z lists.json może nie być osiągalny przesuwem w tym samym układzie; szybki swipe otwiera dialog zamiast przewijać (użyć swipe z pause_end=160). Naprawa: najpierw przewinąć do góry (go_top), potem znajdować wiersz po napisie etykiety (tekst na ekranie), nie po adresie widgetu. |
