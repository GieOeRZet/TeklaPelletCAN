#!/usr/bin/env python3
"""PASS 68: dane alarmow (ui_model/alarms.json): kody, teksty w 8 jezykach (TypedText), miejsca ustawiania/kasowania (ChatGPT PASS 100/110), model rejestrow historii (zmierzony), zachowanie ekranu."""
import csv, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data")
TT = {int(r["id_relative"]): r for r in csv.DictReader(open(os.path.join(D, "texts_all_languages.csv"), encoding="utf-8"))}
codes = {}
for r in csv.DictReader(open(os.path.join(D, "alarm_codes_texts.csv"), encoding="utf-8")):
    t = TT.get(int(r["typedtext_id"]), {}); codes[int(r["alarm_code"])] = dict(code=int(r["alarm_code"]), typedtext_id=int(r["typedtext_id"]), text={k: t.get(k) for k in ("PL", "EN", "LT", "SK", "CZ", "ES", "RO", "EST")})
cg = os.path.join("/tmp/w/cg", "cg_alarm_catalog_sites.csv")
if os.path.exists(cg):
    for r in csv.DictReader(open(cg, encoding="utf-8")):
        c = codes.setdefault(int(r["code"]), dict(code=int(r["code"]), text=dict(PL=r["text_pl"])))
        c["raise_sites"] = r["raise_sites"].split(";") if r["raise_sites"] else []; c["clear_sites"] = r["clear_sites"].split(";") if r["clear_sites"] else []; c["condition"] = "OPEN: " + r["condition_status"]
out = dict(
    evidence="MEASURED (rejestry i ekran: PASS 68, emulator) + STRONG (ChatGPT PASS 97/100/110: automat alarmowy, miejsca raise/clear) + opis zachowania ekranu od wlasciciela (firmware)",
    history_ring=dict(size=20, registers=dict(alarm_register="0x4010+i (u32): niskie 16 bitow = kod; bit16 = AKTYWNY; bit17 = NIEPOTWIERDZONY", date_timestamp="0x4024+i (u32, unix)", confirm_timestamp="0x4038+i (u32, unix; 0 = niepotwierdzony)", next_index="0x404C (u8)", count="0x404D (u8)"),
        measured="przy braku modulow silnik sam dopisuje alarmy 100, 105, 110 (komunikacja z modulami) z flagami 0x30000 (aktywny + niepotwierdzony); znacznik czasu = RTC panelu (bez RTC = 2000-12-01 => 975542400)"),
    screen=dict(node="ALARMY", vtable="0x808ec10", title="HISTORIA ALARMOW",
        layout="okno szczegolow jednego wpisu: NR, KOD, tekst alarmu (TypedText wg jezyka), 'Powstanie: DD.MM.RRRR G:MM', przycisk POTWIERDZ, status (AKTYWNY na czerwono); po potwierdzeniu dochodzi linia 'Potwierdz.: DD.MM.RRRR G:MM', a przycisk znika",
        real_device_behavior=dict(source="WLASCICIEL (obserwacja prawdziwego panelu, 2026-11-24) - obowiazujace zachowanie UI do odtworzenia",
            rules=["pierwsze okno pokazuje najnowszy alarm, ktory trzeba potwierdzic; dopoki nie jest potwierdzony, kociol nie wystartuje ponownie, a strzalek nie ma", "po potwierdzeniu najnowszego pojawia sie strzalka w gore (do starszych alarmow)", "na NR 2 sa dwie strzalki: w gore (starszy) i w dol (powrot do nowszego); tak do NR 3, 4 ... az do 20 (cala historia)", "na najstarszym wpisie zostaje tylko strzalka w dol (powrot)", "zachowanie historii alarmow bez widocznych roznic miedzy poziomami dostepu (wg obserwacji wlasciciela)"],
            level_0_hypothesis="na poziomie 0 strzalki moga byc poza ekranem celowo (widok przesuniety o 80 px), zeby nie dalo sie ogladac historii na poziomie uzytkownika; spojne z pomiarem emulatora",
            evidence="OWNER (nie zmierzone); wymaga potwierdzenia nagraniem z prawdziwego panelu (A3 w TODO)"),
        emulator_observation=dict(arrows="w emulatorze (FW2213TK_kopia.bin) OBIE strzalki sa rysowane zawsze (NR 1 niepotwierdzony, potwierdzony, srodek, kraniec); flagi vis/touch widzetow (420,100) i (420,170) stale 1; w kodzie: setupScreen (PROJECT 0x080405B6) tworzy dwa przyciski bezwarunkowo, petla odswiezania 0x080407DC (20 wpisow) formatuje tylko kod, daty i status (0x08040566) - nie znaleziono logiki widocznosci strzalek",
            ends="nawigacja zatrzymuje sie na ostatnim waznym wpisie (NR zatrzymany, np. 15 przy mieszanym pierscieniu)", level_layout="poziom 0: naglowek x=80 i strzalki (x=500) poza ekranem; poziom >=1: naglowek x=0, strzalki widoczne; w kodzie nie znaleziono odczytu poziomu w setupScreen (warunek poziomu moze byc w kontenerze/transition - OPEN)",
            evidence="MEASURED (PASS 68) + analiza listingu", hypotheses=["strzalki w prawdziwym panelu maja stan 'wylaczony' bez bitmapy (niewidoczny), ktorego emulator nie odtwarza", "inna wersja firmware w panelu wlasciciela niz FW2213TK_kopia.bin", "brak wejsc modulowych/RTC w emulatorze zmienia warunek (np. czas potwierdzenia > 0)"]),
        controls=dict(arrow_down=dict(tap=[445, 187], effect="NR + 1 (starszy wpis); bez PID i CAN"), arrow_up=dict(tap=[445, 118], effect="NR - 1 (nowszy wpis); bez PID i CAN"), ack_button=dict(tap=[232, 187], effect="zapis rejestru i czasu potwierdzenia + 2 ramki CAN; przycisk znika; dochodzi linia Potwierdz.")),
        behaviour=["NR 1 = najnowszy wpis wymagajacy uwagi (pierwsze okno); kolejne NR = starsze", "historia trzyma 20 wpisow (pierscien)", "POTWIERDZ zdejmuje bit17 (UNACK) rejestru i zapisuje czas potwierdzenia = czas panelu; bit16 (AKTYWNY) zostaje - status AKTYWNY zalezy od warunku, nie od potwierdzenia"],
        ack_measured=dict(example="NR 2, kod 105: PID 0x4012 0x00030069 -> 0x00010069; PID 0x403A 0 -> 0x3A259880 (975542400 = 30.11.2000 00:00 przy RTC panelu = 0)", can_frames=["0x584: 42 12 40 01 69 00 01 00", "0x584: 42 3a 40 01 80 98 25 3a"], rule="ramka 0x584: 42 <pid_lo> <pid_hi> 01 <u32 LE>; para: rejestr alarmu 0x4010+i oraz czas potwierdzenia 0x4038+i", evidence="MEASURED (PASS 51 i PASS 68)"),
        open=["mapowanie NR -> numer slotu pierscienia (zalezy od indeksu zapisu 0x404C); w tescie NR 2 = slot 2", "kiedy status zmienia sie na nieaktywny (kasowanie bitu 16 po ustapieniu warunku)", "format godziny: G:MM (np. 0:00)"]),
    alarm_automaton=dict(raise_fn="RUNTIME 0x08025198", active_bit="bit16 (0x0802516C)", unack_bit="bit17 (0x08025134)", clear_fn="0x08025104", ack="zapis rejestru 0x4010+i i znacznika 0x4038+i", memory_reset="lokalny reset pamieci alarmow: 0x404E", source="ChatGPT PASS 97"),
    codes=[codes[k] for k in sorted(codes)], codes_total=len(codes),
    open=["warunki wyzwolenia per alarm (clear-only: 7,43,53,115,250; raise-only: 131,139,140,150,160,161 - asymetria katalogu PASS 110)"])
json.dump(out, open(os.path.join(D, "ui_model", "alarms.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(len(codes), "kodow")
