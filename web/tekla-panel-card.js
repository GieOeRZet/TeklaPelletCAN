/* tekla-panel-card v6.9 (Test wyjsc tylko po odblokowaniu POZIOMU MENU, bez osobnego PIN-u; ikona zakazu rozpalenia na palniku, encja ban) – v6.8 (menu Palnik - ustawienia 1:1 z panelu: Korekta powietrza, Moc min, Moc max, Wartosc opalowa, Ilosc paliwa test; encje power_min/power_max/fuel_heat) – v6.7 (POZIOM MENU: PIN 0999 odblokowuje sekcje serwisowa, 0000 blokuje, 5 min bez aktywnosci = blokada; ekran Moc dmuchawy modulacja) – v6.6 (brak danych lub encji = '-', takze tlen; zamiast '--' i 0.0) – v6.3 (tryb mirror: encja 'mirror' = tylko podglad, zapis tylko wlacz/wylacz kociol i potwierdz alarm) – v6.1 – replika panelu Estyma Igneo Touch (zapis z karty: tryb kotła, CO/CWU, PROGRAM, Statystyki; historia zmian: v5.x w kopii lokalnej) */
/* Brak domyślnych encji – użytkownik wskazuje własne w edytorze karty (lub w YAML: entities:). */
const BTN = ['button', 'input_button'];
const S = ['sensor', 'input_number', 'number'], B = ['binary_sensor', 'switch', 'input_boolean'];
const ENT_GROUPS = [
  ['Kocioł', [
    ['boiler_temp', 'Temperatura kotła', S], ['boiler_set', 'Temp. zadana kotła (wynikowa)', S], ['boiler_manual', 'Temp. zadana kotła (ręczna)', S],
    ['mode', 'Tryb pracy kotła', S], ['sch_boil', 'Harmonogram kotła (rejestry, tekst)', S], ['on', 'Kocioł włączony', B], ['power_switch', 'Włącznik kotła', ['switch', 'input_boolean']], ['outside', 'Temperatura zewnętrzna', S]]],
  ['Palnik', [
    ['burner', 'Stan palnika (tekst)', S], ['burner_code', 'Kod stanu palnika', S], ['power', 'Moc palnika [%]', S],
    ['burn_kw', 'Moc palnika [kW]', S], ['burn_kgh', 'Spalanie [kg/h]', S], ['burn_bright', 'Jasność płomienia', S], ['burn_temp', 'Temperatura palnika', S], ['air_corr', 'Korekta powietrza [%]', S], ['power_min', 'Moc min [%]', S], ['power_max', 'Moc max [%]', S], ['fuel_heat', 'Wartość opałowa [kWh/kg]', S], ['fuel_test', 'Ilość paliwa test [kg/h]', S], ['ban', 'Zakaz rozpalenia (wejście)', B],
    ['fan_pct', 'Dmuchawa [%]', S], ['blower_run', 'Dmuchawa pracuje', B], ['feeder_run', 'Podajnik pracuje', B], ['feeder', 'Podajnik', S], ['burn_time', 'Czas pracy palnika', S], ['fuel', 'Paliwo w zbiorniku [kg]', S], ['fuel_cap', 'Pojemność zbiornika [kg]', S], ['fuel_pct', 'Zapełnienie zbiornika [%]', S], ['feed_time', 'Czas podawania ręcznego [s]', S]]],
  ['Ogrzewanie (CO)', [
    ['co_temp', 'Temperatura CO', S], ['co_set', 'Temp. zadana CO (wynikowa)', S], ['co_manual', 'Temp. zadana CO (ręczna)', S],
    ['co_pump', 'Pompa CO', B], ['co_aux', 'CO – pomocnicza', S], ['co_comfort', 'CO – komfort (zadana)', S], ['co_eco', 'CO – ekonomiczna (zadana)', S], ['sch_co', 'Harmonogram CO (rejestry, tekst)', S], ['co_mode', 'Tryb CO (Off/Eko/Harmonogram/Komfort)', S], ['co_mode_sel', 'Tryb CO – ustawianie (select)', ['select', 'input_select']]]],
  ['Woda użytkowa (CWU)', [
    ['cwu_temp', 'Temperatura CWU', S], ['cwu_set', 'Temp. zadana CWU (wynikowa)', S], ['cwu_comfort', 'CWU – komfort', S],
    ['cwu_eco', 'CWU – ekonomiczna', S], ['sch_cwu', 'Harmonogram CWU (rejestry, tekst)', S], ['cwu_mode', 'Tryb CWU (Off/Eko/Harmonogram/Komfort)', S], ['cwu_mode_sel', 'Tryb CWU – ustawianie (select)', ['select', 'input_select']], ['cwu_pump', 'Pompa CWU', B]]],
  ['Statystyki kotła', [
    ['stats', 'Statystyki kotła (jeden sensor tekstowy: 8 liczb)', S]]],
  ['Test wyjść', [
    ['blower_mode', 'Dmuchawa – tryb (tekst)', S], ['blower_auto', 'Dmuchawa: Automat', BTN], ['blower_off', 'Dmuchawa: Wyłącz', BTN], ['blower_on', 'Dmuchawa: Włącz (czasowo)', BTN],
    ['feeder_mode', 'Podajnik – tryb (tekst)', S], ['feeder_auto', 'Podajnik: Automat', BTN], ['feeder_off', 'Podajnik: Wyłącz', BTN], ['feeder_on', 'Podajnik: Podaj paliwo', BTN]]],
  ['Moc dmuchawy modulacja [%] (progi mocy 20/40/60/80/100 %)', [
    ['fan_mod_1', 'Dmuchawa przy mocy 20 %', S], ['fan_mod_2', 'Dmuchawa przy mocy 40 %', S], ['fan_mod_3', 'Dmuchawa przy mocy 60 %', S], ['fan_mod_4', 'Dmuchawa przy mocy 80 %', S], ['fan_mod_5', 'Dmuchawa przy mocy 100 %', S]]],
  ['Alarmy i system', [
    ['alarm', 'Alarm aktywny', B], ['last_alarm', 'Ostatni alarm', S], ['alarm_start', 'Alarm – początek', S], ['alarm_end', 'Alarm – koniec', S], ['can_ok', 'Łączność CAN OK', B], ['mirror', 'Tryb mirror (ESP: tylko podgląd)', B], ['confirm', 'Przycisk „Potwierdź alarm"', ['button', 'input_button']]]],
];
const TEKLA_DEF = {};
ENT_GROUPS.forEach(g => g[1].forEach(f => { TEKLA_DEF[f[0]] = ''; }));
// końcówki entity_id (nazwy z ESPHome tekla_estyma) używane przez „uzupełnij z prefiksu"
const ROLE_KEY = {
  boiler_temp: 'kociol_temperatura', boiler_set: 'kociol_zadana_wynikowa', boiler_manual: 'kociol_zadana_reczna', mode: 'kociol_tryb_pracy',
  on: 'kociol_wlaczony', power_switch: 'kociol_wlacz_wylacz', outside: 'temperatura_zewnetrzna',
  fuel: 'zbiornik_paliwo', fuel_cap: 'zbiornik_pojemnosc', fuel_pct: 'zbiornik_zapelnienie', fan_pct: 'dmuchawa_obroty', blower_run: 'dmuchawa_pracuje', feeder_run: 'podajnik_pracuje',
  burner: 'palnik_stan', burn_temp: 'temperatura_palnika', air_corr: 'korekta_powietrza', power_min: 'moc_min', power_max: 'moc_max', fuel_heat: 'wartosc_opalowa', fuel_test: 'ilosc_paliwa_test', ban: 'zakaz_rozpalenia', co_mode: 'co_tryb', cwu_mode: 'cwu_tryb', co_mode_sel: 'co_tryb_ustaw', cwu_mode_sel: 'cwu_tryb_ustaw', burner_code: 'palnik_kod_stanu', power: 'moc_palnika',
  co_temp: 'co_temperatura', co_set: 'co_zadana_wynikowa', co_manual: 'co_zadana_reczna', co_pump: 'co_pompa',
  cwu_temp: 'cwu_temperatura', cwu_set: 'cwu_zadana_wynikowa', cwu_comfort: 'cwu_zadana_komfort', cwu_eco: 'cwu_zadana_ekonomiczna', cwu_pump: 'cwu_pompa',
  blower_mode: 'dmuchawa_tryb', blower_auto: 'dmuchawa_automat', blower_off: 'dmuchawa_wylacz', blower_on: 'dmuchawa_wlacz_czasowo',
  feeder_mode: 'podajnik_tryb', feeder_auto: 'podajnik_automat', feeder_off: 'podajnik_wylacz', feeder_on: 'podajnik_podaj_paliwo_30_s',
  sch_boil: 'kociol_harmonogram_rejestry', sch_co: 'co_harmonogram_rejestry', sch_cwu: 'cwu_harmonogram_rejestry', co_comfort: 'co_zadana_komfort', co_eco: 'co_zadana_ekonomiczna',
  fan_mod_1: 'dmuchawa_modulacja_20', fan_mod_2: 'dmuchawa_modulacja_40', fan_mod_3: 'dmuchawa_modulacja_60', fan_mod_4: 'dmuchawa_modulacja_80', fan_mod_5: 'dmuchawa_modulacja_100',
  stats: 'statystyki_kotla', mirror: 'tryb_mirror',
  alarm: 'alarm_aktywny', last_alarm: 'ostatni_alarm', alarm_start: 'alarm_poczatek', alarm_end: 'alarm_koniec', can_ok: 'can_ok', confirm: 'potwierdz_alarm',
};
const SCREEN_OPTS = [
  ['main', 'Ekran główny'], ['heat', 'Ogrzewanie'], ['water', 'Woda użytkowa'], ['burn', 'Palnik'], ['quick', 'Szybkie ustawienia (okno)'], ['fuel', 'Paliwo (okno)'],
  ['menu', 'Menu'], ['prog', 'Program (harmonogram)'], ['stats', 'Statystyki'], ['boiler', 'Kocioł – ustawienia'], ['burner_s', 'Palnik – ustawienia'], ['co_s', 'Ogrzewanie – ustawienia'], ['cwu_s', 'Woda – ustawienia'],
  ['test', 'Test wyjść'], ['alarm', 'Alarmy'], ['net', 'Sieć'], ['info', 'Info'], ['level', 'Poziom menu (PIN)'],
];
// harmonogramy (godziny komfortu) – na razie przepisane z panelu, do czasu odczytu z rejestrów
const SCHED_DEF = { cwu: [[0, 24]], co: [[2.5, 10], [16.5, 21]] };
const ICO = {"hopper":{"vb":"0 0 39.6 32.8","d":"M39.0 0.1L37.5 0.4L36.8 1.6L36.9 16.2L36.5 18.8L35.8 20.5L35.0 21.1L28.2 30.1L28.1 30.9L28.9 32.0L29.6 32.0L30.9 31.0L32.9 28.1L37.6 22.5L39.2 19.9L39.5 18.6L39.6 1.4ZM1.5 0.0L0.4 0.8L0.0 1.9L0.2 17.4L0.8 20.1L1.9 22.1L2.8 22.9L3.1 23.8L9.1 31.1L10.8 32.1L11.5 31.0L11.4 29.9L7.8 24.9L5.0 21.9L3.2 19.0L3.0 17.9L3.1 2.0L2.8 0.4Z"},"flame":{"vb":"0 0 29.0 38.9","d":"M17.2 0.1L14.8 0.0L12.8 0.6L11.0 1.5L9.1 3.2L8.5 4.4L8.2 6.0L8.6 12.4L7.9 13.2L3.4 13.2L2.0 13.9L1.6 14.4L1.8 15.5L4.1 16.5L4.8 17.1L5.2 18.5L5.2 19.5L4.6 21.2L1.6 24.2L0.0 27.9L0.1 30.4L0.6 32.6L1.9 35.5L3.6 37.9L5.2 38.9L6.1 38.6L6.1 37.4L5.4 34.4L5.4 32.8L6.2 29.2L8.4 26.6L10.1 25.8L12.5 23.5L13.1 19.9L13.9 18.9L14.8 19.0L16.1 19.9L18.6 23.5L19.0 25.5L18.8 29.4L19.4 29.6L20.8 28.6L21.9 28.6L23.5 30.2L24.0 32.1L24.0 34.2L23.6 35.9L22.2 37.9L22.4 38.4L23.1 38.4L24.2 37.1L26.0 35.9L28.2 32.5L29.0 28.6L29.0 25.9L28.4 22.5L27.1 19.5L26.2 15.6L26.2 14.2L26.9 12.5L26.9 11.5L26.4 11.1L25.1 11.5L23.9 13.0L22.8 13.5L21.0 12.9L18.6 10.5L17.4 7.6L16.8 5.2L17.2 3.1L18.1 1.6L17.9 0.6Z"},"radi":{"vb":"0 0 29.8 36.5","d":"M4.0 0.2L3.4 1.2L2.8 3.6L0.0 6.2L0.4 7.2L2.9 9.5L3.2 10.2L3.5 19.8L3.4 26.8L2.9 27.6L0.9 29.4L0.2 30.8L2.9 32.4L3.5 33.5L3.8 35.5L4.6 36.4L5.5 36.4L6.0 35.9L6.2 32.1L7.1 31.1L8.0 30.9L9.6 31.0L10.5 31.6L10.9 32.5L11.0 35.6L11.9 36.5L12.9 36.4L13.4 35.8L13.6 32.1L14.6 31.2L15.8 30.9L16.8 30.9L18.0 31.9L18.4 32.8L18.5 35.8L19.2 36.4L20.1 36.2L20.6 35.6L21.0 32.2L21.9 31.4L22.8 31.0L24.0 31.0L25.2 31.6L25.9 32.5L26.1 35.8L26.8 36.4L28.0 36.1L28.4 35.8L28.8 32.8L29.5 30.6L28.6 26.0L28.8 11.5L29.8 6.1L28.5 0.6L28.0 0.2L26.6 0.1L25.8 1.1L25.0 4.9L24.1 5.6L23.1 5.8L21.6 4.6L20.9 0.9L20.1 0.1L19.0 0.1L18.0 1.4L17.8 4.8L17.2 5.5L16.1 5.9L14.4 5.1L13.9 3.9L13.8 1.1L13.0 0.1L11.9 0.0L10.6 1.2L10.6 3.4L10.2 5.0L9.5 5.6L7.6 5.8L6.8 5.1L6.5 4.5L6.2 0.8L5.2 0.0ZM23.1 7.4L24.4 7.6L25.0 8.2L25.6 9.9L25.9 27.1L25.4 28.6L23.8 30.1L23.0 30.1L21.4 28.5L21.0 27.6L21.2 9.6L21.8 8.2ZM7.6 7.4L9.8 7.6L10.4 8.2L10.6 9.2L10.9 26.9L10.4 28.9L9.1 30.1L7.6 30.1L7.0 29.5L6.2 27.9L6.4 9.4L6.8 8.0ZM16.2 7.2L16.9 7.4L17.6 8.1L18.0 9.6L18.2 24.2L18.1 27.9L17.2 29.8L16.6 30.2L15.1 29.9L13.9 28.5L13.5 27.4L13.8 9.5L14.5 7.9Z"},"faucet":{"vb":"0 0 40.6 43.5","d":"M37.0 35.5L36.4 36.0L35.8 38.1L34.8 39.5L34.6 41.1L36.5 43.4L38.1 43.5L39.0 43.1L40.4 41.8L40.6 40.0L40.4 39.0L38.6 35.9ZM1.6 9.2L0.5 10.0L0.0 11.1L0.0 22.1L0.2 23.0L1.2 24.2L2.6 24.4L3.5 23.8L3.9 22.6L4.0 11.6L3.8 10.0L3.2 9.5ZM6.6 1.1L5.9 2.9L5.8 4.6L6.1 6.2L6.9 7.2L8.6 8.1L9.8 8.1L14.0 7.0L15.5 7.4L16.2 8.5L16.1 10.1L15.6 10.8L13.1 11.5L11.0 13.2L8.1 13.6L7.6 14.8L7.5 16.4L7.9 18.2L9.0 19.0L25.2 18.9L28.4 19.5L30.1 20.8L31.6 21.4L32.6 22.6L34.2 25.8L34.4 28.6L34.9 29.8L37.6 30.1L39.4 29.5L39.5 27.2L38.6 22.6L37.5 20.2L33.6 16.6L30.6 14.9L27.0 13.9L25.5 12.6L24.8 11.5L22.5 11.1L21.8 10.6L21.5 10.0L21.6 7.9L22.5 7.1L24.5 7.2L27.2 8.1L28.4 8.1L30.4 7.2L31.4 6.4L31.9 5.0L31.9 3.1L31.6 2.2L30.5 0.9L27.5 0.0L22.6 1.2L19.5 0.1L18.2 0.0L15.8 1.0L14.1 1.1L12.2 0.5L8.9 0.0L7.4 0.5Z"},"power":{"vb":"0 0 45.1 44.0","d":"M42.5 39.2L42.0 39.6L41.4 41.2L41.6 43.1L42.5 44.0L44.1 43.9L44.9 43.4L45.1 42.8L45.1 40.6L44.4 39.5ZM35.4 39.1L34.6 39.6L33.8 40.9L33.6 42.1L34.8 43.8L36.2 44.0L37.8 43.2L38.2 41.4L37.4 39.8ZM28.4 39.1L27.4 39.6L26.1 40.9L26.0 42.0L26.9 43.5L28.1 44.0L29.0 44.0L30.5 43.0L30.9 41.1L29.5 39.5ZM26.1 2.8L25.1 3.6L25.0 4.9L28.0 7.0L30.2 8.0L34.4 11.9L36.2 14.9L37.6 18.6L38.0 20.2L38.0 24.9L37.6 27.0L35.9 31.0L34.6 32.5L34.9 34.5L35.9 34.9L37.1 34.2L37.9 33.4L39.5 30.1L41.2 23.8L41.2 20.5L39.5 14.9L38.0 11.9L36.4 9.6L32.2 5.8L30.9 5.2L27.1 2.8ZM14.5 2.5L12.1 3.8L10.4 5.1L8.9 5.6L6.6 7.5L3.6 10.8L2.6 13.1L1.6 14.6L0.0 19.8L0.1 25.4L1.6 30.2L3.0 32.6L3.6 34.4L6.9 37.6L10.8 40.5L15.0 42.1L19.6 42.9L20.2 42.6L21.0 41.6L20.4 40.5L12.6 38.4L7.9 34.8L5.2 31.4L3.2 27.1L3.1 19.8L3.6 16.8L5.5 13.2L9.0 9.2L13.8 6.2L15.4 5.6L16.0 5.0L16.2 4.4L16.0 3.6L15.2 2.8ZM19.8 0.0L19.1 0.6L18.9 1.5L19.1 4.2L19.0 20.5L19.5 21.5L21.2 21.8L22.2 20.6L22.2 1.0L21.2 0.0Z"}};
const HOP_ROWS = [[8.0, [5.5, 11.2, 17.2, 22.9, 28.8, 34.6]], [14.0, [8.3, 14.2, 19.9, 25.8, 31.4]], [19.7, [11.2, 17.1, 22.6, 28.4]], [25.4, [14.2, 20.1, 25.8]], [31.2, [16.9, 22.6]]]; // zasobnik: rzedy kropek (od gory), uklad ze zdjecia panelu
const BURNER = { 0: 'Wyłączony', 1: 'Rozpalanie', 2: 'Rozżarzanie', 5: 'Modulacja', 6: 'Wygaszanie', 7: 'Czyszczenie', 8: 'Pauza', 9: 'Stop', 10: 'Alarm' };
const MENU = [
  ['boiler', 'Kocioł'], ['burner_s', 'Palnik'], ['co_s', 'Ogrzewanie'], ['cwu_s', 'Ciepła woda użytkowa'],
  ['stats', 'Statystyki'], ['test', 'Test wyjść'], ['alarm', 'Alarmy'], ['net', 'Sieć'], ['info', 'Info'], ['level', 'POZIOM MENU'],
];
const TITLES = {
  menu: 'MENU', boiler: 'KOCIOŁ', burner_s: 'PALNIK – USTAWIENIA', co_s: 'OGRZEWANIE 1 – USTAWIENIA', cwu_s: 'WODA – USTAWIENIA',
  stats: 'STATYSTYKI', test: 'TEST WYJŚĆ', level: 'POZIOM MENU', fanmod: 'MOC DMUCHAWY', alarm: 'ALARMY', net: 'SIEĆ', info: 'INFO',
};
const MODES = [
  { n: 'Off', ic: 'mdi:power', sup: 'off', pos: 0.052 }, { n: 'Eko', ic: 'mdi:moon-waning-crescent', sup: 'eco', pos: 0.37 },
  { n: 'Harmonogram', ic: 'mdi:clock-outline', sup: '', pos: 0.664 }, { n: 'Komfort', ic: 'mdi:white-balance-sunny', sup: 'comf', pos: 1 }];
// nazwy alarmów (kod z ESP -> opis jak na panelu)
const ALARM_PL = {
  1: 'Czujnik kotła', 2: 'Przegrzanie kotła', 3: 'Czujnik powrotu', 4: 'Czujnik temp. podajnika', 5: 'STB', 6: 'Przegrzanie podajnika', 7: 'Łańcuch bezpieczeństwa', 8: 'Czujnik spalin',
  20: 'Czujnik pokojowy CO1', 21: 'Czujnik pokojowy CO2', 24: 'Czujnik CO1', 25: 'Czujnik CO2', 30: 'Czujnik CWU', 31: 'Czujnik bufora góra', 32: 'Czujnik bufora dół',
  50: 'Rezerwa paliwa', 51: 'Brak paliwa w zasobniku', 110: 'Brak komunikacji z modułem BIG', 115: 'Brak komunikacji z modułem lambda', 130: 'Faza czyszczenia', 131: 'Błąd wygaszania',
  140: 'Brak ognia/opału', 150: 'Dodatkowy magazyn: brak paliwa/max', 151: 'Dodatkowy magazyn: rezerwa', 160: 'Wymiennik do czyszczenia', 161: 'Palnik do czyszczenia',
  200: 'Ruszt', 201: 'Awaria dmuchawy', 202: 'Drzwi kotła otwarte', 203: 'Bardzo niski poziom tlenu' };
const DAYS = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd'], DAYS_FULL = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'];
const PROG_LBL = ['WODA', 'OGRZEWANIE', 'KOCIOŁ']; // kind: 0 = CWU, 1 = CO, 2 = kocioł
// okna ustawień CO / CWU (zakresy wg panelu)
const CDLG = {
  co: { lo1: 15, hi1: 30, lo2: 10, hi2: 30, step: 0.5, dec: 1, w1: 2, w2: 3, ck: 'co_comfort', ek: 'co_eco', mk: 'co_mode' },
  cwu: { lo1: 20, hi1: 70, lo2: 20, hi2: 70, step: 1, dec: 0, w1: 0, w2: 1, ck: 'cwu_comfort', ek: 'cwu_eco', mk: 'cwu_mode' } };
const MX = [28, 42.5, 57, 71.5]; // środki ikon trybów w oknach (cqw); suwak trybu: left 24, width 52
// poziom menu (serwis): odblokowanie PIN-em, wazne 5 min od ostatniej aktywnosci w karcie (pamiec modulu + sessionStorage)
const LVL = window.__teklaLvl = window.__teklaLvl || { t: 0 };
try { LVL.t = Math.max(LVL.t, +sessionStorage.getItem('tekla_lvl') || 0); } catch (e) {}
const LVL_MS = 300000, SERVICE = ['fanmod', 'test'];
const LIVE = ['main', 'water', 'heat', 'burn'];
const IMG = () => window.TEKLA_IMG || {}; // grafiki: tekla-panel-burner.js (kocioł + palnik, WebP)

class TeklaPanelCard extends HTMLElement {
  setConfig(c) {
    this._cfg = c || {};
    this.E = Object.assign({}, TEKLA_DEF, this._cfg.entities || {});
    this.SCH = Object.assign({}, SCHED_DEF, this._cfg.schedules || {});
    this._scr = this._cfg.screen || 'main'; this._backTo = 'main';
    this._modal = false; this._scroll = {}; this._sig = '';
    if (!document.getElementById('tekla-font')) {
      const l = document.createElement('link'); l.id = 'tekla-font'; l.rel = 'stylesheet';
      l.href = 'https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;700&display=swap';
      document.head.appendChild(l);
    }
    if (c && c.screen === 'quick') { this._scr = 'main'; this._modal = true; }
    if (c && c.screen === 'fuel') { this._scr = 'main'; this._modal = 'fuel'; }
    this._lvlTimer();
    if (!this._imgL) { this._imgL = () => this._built && this._render(true); window.addEventListener('tekla-img', this._imgL); }
    if (!this.shadowRoot) this._build();
    else this._render(true);
  }
  getCardSize() { return 6; }
  static getStubConfig() { return { screen: 'main', entities: {} }; }
  static getConfigElement() { return document.createElement('tekla-panel-card-editor'); }

  set hass(h) {
    this._hass = h;
    if (!this._rf0) { this._rf0 = 1; this._refresh(true); }
    this._trackFeed();
    if (!this._built) return;
    this._render(false);
  }

  /* ---------- helpers ---------- */
  _unl() { return Date.now() - LVL.t < LVL_MS; }
  _lvlSet(on) { LVL.t = on ? Date.now() : 0; try { sessionStorage.setItem('tekla_lvl', String(LVL.t)); } catch (e) {} this._lvlTimer(); }
  _touch() { if (this._unl()) this._lvlSet(true); }
  _lvlTimer() { clearTimeout(this._lt); if (this._unl()) this._lt = setTimeout(() => this._built && this._render(true), LVL_MS + 500); }
  // ---- zapis do ESP (usługi esphome.<węzeł>_...) i odczyt harmonogramów ----
  // tryb mirror: opcja karty 'mirror: true/false' ma pierwszenstwo, inaczej encja z ESP; w mirrorze blokujemy wszelka edycje
  _mirror() { if (typeof this._cfg.mirror === 'boolean') return this._cfg.mirror; return this._on('mirror'); }
  _node() { return this._cfg.esphome_node || 'tekla_estyma'; }
  _svc(name, data) { if (this._hass) this._hass.callService((this._cfg && this._cfg.service_domain) || 'teklapelletcan', this._node() + '_' + name, data || {}); }
  _refresh(force) { const n = Date.now(); if (!force && n - (this._rfAt || 0) < 30000) return; this._rfAt = n; this._svc('schedule_refresh'); }
  // harmonogram: kind 0 = CWU, 1 = CO, 2 = kocioł; zwraca 7 liczb (24 bity) albo null
  _bits(kind) {
    const s = this._s(['sch_cwu', 'sch_co', 'sch_boil'][kind]), arr = new Array(7).fill(null);
    if (s && !['unknown', 'unavailable'].includes(s.state)) s.state.trim().split(/\s+/).forEach((h, i) => { if (i < 7 && /^[0-9A-Fa-f]{6}$/.test(h)) arr[i] = parseInt(h, 16); });
    const sp = this._sp || (this._sp = {});
    for (let d = 0; d < 7; d++) { const q = sp[kind + ':' + d]; if (q) { if (arr[d] === q.bits || Date.now() - q.t > 20000) delete sp[kind + ':' + d]; else arr[d] = q.bits; } }
    return arr;
  }
  _bands(bits) {
    if (bits == null) return null;
    const o = []; let st = null;
    for (let i = 0; i <= 24; i++) { const b = i < 24 && ((bits >> i) & 1); if (b && st === null) st = i; if (!b && st !== null) { o.push([st, i]); st = null; } }
    return o;
  }
  _today() { return (new Date().getDay() + 6) % 7; }
  _todayBands(kind, fb) { return this._bands(this._bits(kind)[this._today()]) || fb; }
  // tryb zadawania kotła z 0x2002: 0 czasowy auto, 1 czasowy ręczny, 2 auto, 3 ręczny
  _bMode() {
    const t = this._t('mode', '').toLowerCase(), man = /ręcz|recz/.test(t);
    return t.includes('czas') ? (man ? 1 : 0) : (man ? 3 : 2);
  }
  _chipHtml(bm) {
    return bm < 2 ? `<span class="ck"><ha-icon icon="mdi:clock-outline"></ha-icon><sup>${bm ? 'M' : 'A'}</sup></span>` : `<u>${bm === 2 ? 'AUTO' : 'MAN'}</u>`;
  }
  // suwak jak w oknach panelu (kolorowy do wskaźnika, reszta szara)
  _sl(attrs, x, y, w, p) {
    p = Math.max(0, Math.min(1, p)); const f = Math.max(p, 0.001);
    return `<div class="sl" ${attrs} style="left:${x}cqw;top:${y}cqw;width:${w}cqw"><b style="width:${(p * 100).toFixed(1)}%;background-size:${(100 / f).toFixed(1)}% 100%"></b><i style="left:${(p * 100).toFixed(1)}%"></i></div>`;
  }
  _mdiIcon(attrs, x, y, inner, on) { return `<span class="mdi ${on ? 'on' : ''}" ${attrs} style="left:${x}cqw;top:${y}cqw">${inner}</span>`; }
  // okno trybu kotła
  _bOpen() {
    const bm = this._bMode(), v = Math.round(this._v('boiler_manual'));
    const val = isNaN(v) ? 65 : Math.max(60, Math.min(80, v));
    this._bd = { mode: bm, m0: bm, val, v0: val };
    this._modal = 'boiler'; this._refresh(); this._render(true);
  }
  _bDlg() {
    const d = this._bd || (this._bOpen(), this._bd), man = d.mode === 1 || d.mode === 3;
    const top = man ? `<div class="bval">${d.val}</div><span class="blb" style="left:17cqw">60</span><span class="blb" style="left:79cqw">80</span>
      ${this._sl('data-act="bslide"', 17, 27, 66, (d.val - 60) / 20)}
      <div class="bpm" data-act="bval" data-d="-1" style="left:17cqw"><i></i></div><div class="bpm pl" data-act="bval" data-d="1" style="left:50.5cqw"><i></i><i></i></div>`
      : '<div class="btxt">W tym trybie temperatura<br>zadawana jest automatycznie.</div>';
    const ic = [
      `<ha-icon icon="mdi:clock-outline"></ha-icon><sup>A</sup>`, `<ha-icon icon="mdi:clock-outline"></ha-icon><sup>M</sup>`, '<u class="plq">AUTO</u>', '<u class="plq">MAN</u>'];
    return `<div class="qd"><div class="qx" data-act="cancel"></div><div class="qbg"></div>${top}
      ${ic.map((h, i) => this._mdiIcon(`data-act="bm" data-i="${i}"`, MX[i], 45, h, d.mode === i)).join('')}
      ${this._sl('data-act="bmslide"', 24, 49.6, 52, (MX[d.mode] - 24) / 52)}
      <div class="qok" data-act="ok">OK</div></div>`;
  }
  // okno ustawień obiegu (CO / CWU): komfort, eco, tryb
  _cOpen(k) {
    const c = CDLG[k], cf = this._v(c.ck), ec = this._v(c.ek), mm = this._mode(c.mk);
    const mi = mm ? MODES.indexOf(mm) : 3;
    const cfv = isNaN(cf) ? c.hi1 : cf, ecv = isNaN(ec) ? c.lo2 : ec;
    this._cd = { k, comf: cfv, eco: ecv, mode: mi, c0: cfv, e0: ecv, m0: mi };
    this._modal = k; this._refresh(); this._render(true);
  }
  _cDlg(k) {
    if (!this._cd || this._cd.k !== k) return '';
    const c = CDLG[k], d = this._cd, f = v => v.toFixed(c.dec);
    const blk = (w, y, lo, hi, val, icon, sup) => `
      ${this._mdiIcon('', 40, y + 3.2, `<ha-icon icon="${icon}"></ha-icon><sup>${sup}</sup>`, true)}<div class="cval" style="top:${y - 1.3}cqw">${f(val)}</div>
      <span class="blb" style="left:21cqw;top:${y + 4}cqw">${lo}</span><span class="blb" style="left:79cqw;top:${y + 4}cqw">${hi}</span>
      ${this._sl(`data-act="cslide" data-w="${w}"`, 21, y + 12.5, 58, (val - lo) / (hi - lo))}
      <div class="bpm sm" data-act="cval" data-w="${w}" data-d="-1" style="left:6.5cqw;top:${y + 8.3}cqw"><i></i></div><div class="bpm sm pl" data-act="cval" data-w="${w}" data-d="1" style="left:81.5cqw;top:${y + 8.3}cqw"><i></i><i></i></div>`;
    return `<div class="qd"><div class="qx" data-act="cancel"></div><div class="qbg"></div>
      ${blk('comf', 8.4, c.lo1, c.hi1, d.comf, 'mdi:white-balance-sunny', 'comf')}${blk('eco', 24, c.lo2, c.hi2, d.eco, 'mdi:moon-waning-crescent', 'eco')}
      ${MODES.map((m, i) => this._mdiIcon(`data-act="cm" data-i="${i}"`, MX[i], 45, `<ha-icon icon="${m.ic}"></ha-icon>${m.sup ? `<sup>${m.sup}</sup>` : ''}`, d.mode === i)).join('')}
      ${this._sl('data-act="cmslide"', 24, 49.6, 52, (MX[d.mode] - 24) / 52)}
      <div class="qok" data-act="ok">OK</div></div>`;
  }
  _commit() {
    const m = this._modal;
    if (m === 'boiler' && this._bd) {
      const d = this._bd;
      if (d.mode !== d.m0) this._svc('set_boiler_mode', { mode: d.mode });
      if ((d.mode === 1 || d.mode === 3) && d.val !== d.v0) this._svc('set_setpoint', { which: 4, value: d.val });
    } else if ((m === 'co' || m === 'cwu') && this._cd) {
      const d = this._cd, c = CDLG[m];
      if (d.comf !== d.c0) this._svc('set_setpoint', { which: c.w1, value: d.comf });
      if (d.eco !== d.e0) this._svc('set_setpoint', { which: c.w2, value: d.eco });
      if (d.mode !== d.m0) this._setMode(c.mk, d.mode);
    }
    this._modal = false; this._render(true);
  }
  _slFrac(a, e) { const r = a.getBoundingClientRect(); return Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)); }
  // ekran PROGRAM: 7 dni z paskami 0–24 i edycja godzin
  _dayBar(bits) {
    if (bits == null) return '<svg viewBox="0 0 240 24" preserveAspectRatio="none" class="dbar"><text x="120" y="17" text-anchor="middle" font-size="14" fill="#9fb0d8">--</text></svg>';
    let r = '', t = '';
    (this._bands(bits) || []).forEach(([a, b]) => { r += `<rect x="${a * 10}" y="3" width="${(b - a) * 10}" height="14" fill="#ff2a22"/>`; });
    for (let h = 0; h <= 24; h++) t += `<line x1="${h * 10}" y1="${h % 6 === 0 ? 18 : 20}" x2="${h * 10}" y2="24" stroke="#c5d0ea" stroke-width="${h % 6 === 0 ? 2 : 1}"/>`;
    return `<svg viewBox="0 0 240 24" preserveAspectRatio="none" class="dbar"><rect x="0" y="15" width="240" height="2.4" fill="#ff2a22"/>${r}${t}</svg>`;
  }
  _progHdr(title, edit) {
    return `<div class="h2"><span class="bk" ${edit ? 'data-act="pcancel"' : `data-go="${this._backTo || 'main'}"`}>&lsaquo; ${edit ? 'PROGRAM' : PROG_LBL[(this._prog || {}).kind ?? 2]}</span><span class="tt">${title}</span>
      <span class="hi"><span data-go="main"><ha-icon class="cy" icon="mdi:home"></ha-icon></span></span></div>`;
  }
  _progPg() {
    const kind = (this._prog || {}).kind ?? 2, pe = this._pe;
    if (pe) {
      let cells = '';
      for (let h = 0; h < 24; h++) {
        const on = (pe.bits >> h) & 1;
        cells += `<div class="hc ${on ? 'on' : ''}" data-act="phr" data-h="${h}" style="left:${(3.6 + (h % 12) * 7.6).toFixed(1)}cqw;top:${(h < 12 ? 14 : 28.6)}cqw"><b>${h}</b></div>`;
      }
      return `${this._progHdr(DAYS_FULL[pe.day].toUpperCase(), true)}${cells}
        <div class="pb" data-act="pall" data-v="1" style="left:3.6cqw;width:27cqw">KOMFORT 24 h</div><div class="pb" data-act="pall" data-v="0" style="left:33cqw;width:20cqw">ECO 24 h</div>
        <div class="pb" data-act="pcancel" style="left:62cqw;width:15cqw">ANULUJ</div><div class="pb" data-act="pok" style="left:79.5cqw;width:15cqw">OK</div>`;
    }
    const bits = this._bits(kind), td = this._today();
    const rows = DAYS.map((n, d) => `<div class="prow ${d === td ? 'td' : ''}" data-act="pday" data-d="${d}"><span class="pn">${n}</span><div class="pbar">${this._dayBar(bits[d])}<span class="pbl">0</span><span class="pbl" style="left:25%">6</span><span class="pbl" style="left:50%">12</span><span class="pbl" style="left:75%">18</span><span class="pbl" style="left:100%">24</span></div></div>`).join('');
    return `${this._progHdr('PROGRAM')}<div class="plist">${rows}</div>`;
  }
  // licznik ręcznego podawania (0x2267): odlicza => wartość maleje; animujemy tylko przez 15 s od ostatniego spadku
  _trackFeed() {
    const v = this._v('feed_time'), f = this._ft || (this._ft = { v: NaN, dec: 0 });
    if (!isNaN(v) && !isNaN(f.v) && v < f.v) {
      f.dec = Date.now();
      clearTimeout(this._ftTimer);
      this._ftTimer = setTimeout(() => this._built && this._render(true), 15500);
    }
    f.v = v;
  }
  // ilość paliwa [kg]: po kliknięciu + / − pokazujemy wartość zadaną do czasu potwierdzenia z kotła (maks. 8 s)
  _fuelKg() {
    const p = this._fp;
    if (p && Date.now() - p.t < 8000 && this._v('fuel') !== p.kg) return p.kg;
    if (p) this._fp = null;
    return this._v('fuel');
  }
  _fuelStep(d) {
    const cap = this._v('fuel_cap'), cur = this._fuelKg();
    if (isNaN(cur)) return;
    const kg = Math.max(0, Math.min(isNaN(cap) ? 9999 : cap, Math.round(cur) + d));
    this._fp = { kg, t: Date.now() };
    clearTimeout(this._fpT); this._fpT = setTimeout(() => this._svc('set_param', { key: 47, value: kg }), 600);
    clearTimeout(this._fpR); this._fpR = setTimeout(() => this._built && this._render(true), 8200);
    this._render(true);
  }
  // zapełnienie zbiornika 0..1: z kg / pojemność (spójnie z ESP: 0x3601 / 0x3600), a gdy brak kg – z encji w % (fuel_pct)
  _fuelPct() {
    const kg = this._fuelKg(), cap = this._v('fuel_cap');
    if (this._fp && !isNaN(kg) && !isNaN(cap) && cap > 0) return Math.max(0, Math.min(1, kg / cap));
    const p = this._v('fuel_pct');
    if (!isNaN(p)) return Math.max(0, Math.min(1, p / 100));
    return isNaN(kg) || isNaN(cap) || cap <= 0 ? 0 : Math.max(0, Math.min(1, kg / cap));
  }
  // licznik przy przycisku podajnika: stan spoczynku 30 s (kocioł wyłączony: 600 s); po starcie odlicza co 1 s, po zatrzymaniu/końcu wraca
  _fcLeft() {
    const c = this._fc; if (!c) return null;
    const l = Math.ceil(c.d - (Date.now() - c.t) / 1000);
    if (l <= 0) { this._fc = null; return null; }
    return l;
  }
  _fcShow() { const l = this._fcLeft(); return l !== null ? l : (this._on('power_switch') || !this.E.power_switch ? 30 : 600); }
  _fcGo() {
    if (this._fcLeft() !== null) { this._fc = null; clearInterval(this._fcT); const a = this.E.feeder_auto; if (a && this._hass) this._hass.callService('button', 'press', { entity_id: a }); this._render(true); return; }
    const e = this.E.feeder_on; if (e && this._hass) this._hass.callService('button', 'press', { entity_id: e });
    this._fc = { t: Date.now(), d: this._on('power_switch') || !this.E.power_switch ? 30 : 600 };
    clearInterval(this._fcT);
    this._fcT = setInterval(() => { if (!this._built || this._modal !== 'fuel' || this._fcLeft() === null) { clearInterval(this._fcT); this._fc = null; } if (this._built) this._render(true); }, 1000);
    this._render(true);
  }
  _feeding() { return !!this._ft && Date.now() - this._ft.dec < 15000; }
  _s(k) { return this._hass && this.E[k] && this._hass.states[this.E[k]]; }
  _v(k) { const s = this._s(k); if (!s) return NaN; const n = parseFloat(s.state); return isNaN(n) ? NaN : n; }
  _on(k) { const s = this._s(k); return !!s && s.state === 'on'; }
  // tryb pracy obiegu: Off / Eko / Harmonogram / Komfort (tekst z ESP) -> ikona, podpis, pozycja suwaka
  _mode(k) {
    const t = (this._s(k) && !['unknown', 'unavailable'].includes(this._s(k).state) ? this._s(k).state : '').toLowerCase();
    let i = -1;
    if (t.startsWith('off')) i = 0; else if (t.startsWith('eko') || t.startsWith('eco')) i = 1;
    else if (t.startsWith('har') || t.startsWith('cza')) i = 2; else if (t.startsWith('kom') || t.startsWith('com')) i = 3;
    const p = this._mp && this._mp[k];
    if (p) { if (i === p.i || Date.now() - p.t > 20000) delete this._mp[k]; else i = p.i; }
    return i < 0 ? null : MODES[i];
  }
  // zmiana trybu: select z ESP (opcja Off/Eko/Harmonogram/Komfort); do potwierdzenia z kotła pokazujemy wybór od razu
  _setMode(k, i) {
    const sel = this.E[k + '_sel'];
    if (!sel || !this._hass || !MODES[i]) return;
    (this._mp = this._mp || {})[k] = { i, t: Date.now() };
    this._hass.callService('select', 'select_option', { entity_id: sel, option: MODES[i].n });
    clearTimeout(this._mpT); this._mpT = setTimeout(() => this._built && this._render(true), 20500);
    this._render(true);
  }
  // Test wyjść: tryb dmuchawy / podajnika z tekstu z ESP -> 'auto' | 'off' | 'on'
  _outMode(o) {
    const t = this._t(o + '_mode', '').toLowerCase();
    let m = t.startsWith('auto') ? 'auto' : t.startsWith('wyl') ? 'off' : t.startsWith('wl') ? 'on' : '';
    const p = this._op && this._op[o];
    if (p) { if (m === p.m || Date.now() - p.t > 20000) delete this._op[o]; else m = p.m; }
    return m;
  }
  _outSet(o, m) {
    const e = this.E[o + '_' + m];
    if (!e || !this._unl() || !this._hass) return;
    (this._op = this._op || {})[o] = { m, t: Date.now() };
    this._hass.callService('button', 'press', { entity_id: e });
    clearTimeout(this._opT); this._opT = setTimeout(() => this._built && this._render(true), 20500);
    this._render(true);
  }
  _pinStep(i, st) {
    const d = this._pd || (this._pd = [0, 0, 0, 0]);
    d[i] = (d[i] + st + 10) % 10;
    this._render(true);
  }
  _pinOk() {
    const PIN = String(this._cfg.test_pin || '0999'), d = this._pd || [0, 0, 0, 0];
    if (this._scr === 'level') {
      const c = d.join('');
      if (c === String(this._cfg.service_pin || '0999')) this._lvlSet(true);
      else if (c === '0000') this._lvlSet(false);
      else { this._pd = [0, 0, 0, 0]; this._render(true); return; }
      this._pd = [0, 0, 0, 0]; this._go('menu'); return;
    }
    if (d.join('') === PIN) this._testOk = true;
    this._pd = [0, 0, 0, 0];
    this._render(true);
  }
  _pinPg(back, title, msg) {
    const d = this._pd || (this._pd = [0, 0, 0, 0]), X = i => (9.23 + i * 16.75).toFixed(2);
    let h = `<div class="pdt">${msg || 'Wpisz PIN'}</div>`;
    for (let i = 0; i < 4; i++) {
      h += `<div class="pbt pl" data-act="pinp" data-i="${i}" data-s="1" style="left:${X(i)}cqw;top:11.9cqw"><i></i><i></i></div>`
        + `<div class="pdg" style="left:${X(i)}cqw">${d[i]}</div>`
        + `<div class="pbt" data-act="pinp" data-i="${i}" data-s="-1" style="left:${X(i)}cqw;top:39.2cqw"><i></i></div>`;
    }
    h += '<div class="pbt pok" data-act="pinok" style="left:76.9cqw;top:39.2cqw;width:11.15cqw">OK</div>';
    return `${this._hdr(title || TITLES.test, back)}<div class="pvl"></div><div class="pdlg">${h}</div>`;
  }
  _t(k, d = '-') { const s = this._s(k); return !s || ['unknown', 'unavailable'].includes(s.state) ? d : s.state; }
  _p(v, n = 1) { return isNaN(v) ? '-' : v.toFixed(n); }
  _opt(k, n = 0, d = '-') { const v = this._v(k); return isNaN(v) ? d : v.toFixed(n); }

  /* ---------- skeleton ---------- */
  _build() {
    this._built = true;
    const root = this.attachShadow({ mode: 'open' });
    root.innerHTML = `<style>${this._css()}</style>
      <div class="bezel"><div class="strip" id="strip"></div><div class="screen" id="scr"></div></div>`;
    root.addEventListener('click', e => {
      this._touch();
      const a = e.target.closest('[data-go],[data-act]'); if (!a || !this._hass) return;
      if (a.dataset.go) { this._go(a.dataset.go, a.dataset.back); return; }
      const act = a.dataset.act;
      if (this._mirror() && ['bdlg', 'cdlg', 'bm', 'bmslide', 'bval', 'bslide', 'cm', 'cmslide', 'cval', 'cslide', 'pday', 'phr', 'pall', 'pok', 'setmode', 'slider', 'out', 'feedgo', 'fuelpm'].includes(act)) return;
      if (act === 'quick') { this._modal = true; this._render(true); }
      else if (act === 'fuelpm') { if (this._fhold) { this._fhold = false; return; } this._fuelStep(+a.dataset.d); }
      else if (act === 'feedgo') this._fcGo();
      else if (act === 'fuel') { this._modal = 'fuel'; this._render(true); }
      else if (act === 'ok') { if (['boiler', 'co', 'cwu'].includes(this._modal)) this._commit(); else { this._modal = false; this._render(true); } }
      else if (act === 'cancel') { this._modal = false; this._render(true); }
      else if (act === 'bdlg') this._bOpen();
      else if (act === 'cdlg') this._cOpen(a.dataset.k);
      else if (act === 'bm') { this._bd.mode = +a.dataset.i; this._render(true); }
      else if (act === 'bmslide') { const x = 24 + this._slFrac(a, e) * 52; this._bd.mode = MX.reduce((b, v, i) => Math.abs(v - x) < Math.abs(MX[b] - x) ? i : b, 0); this._render(true); }
      else if (act === 'bval') { this._bd.val = Math.max(60, Math.min(80, this._bd.val + +a.dataset.d)); this._render(true); }
      else if (act === 'bslide') { this._bd.val = Math.round(60 + this._slFrac(a, e) * 20); this._render(true); }
      else if (act === 'cm') { this._cd.mode = +a.dataset.i; this._render(true); }
      else if (act === 'cmslide') { const x = 24 + this._slFrac(a, e) * 52; this._cd.mode = MX.reduce((b, v, i) => Math.abs(v - x) < Math.abs(MX[b] - x) ? i : b, 0); this._render(true); }
      else if (act === 'cval' || act === 'cslide') {
        const c = CDLG[this._cd.k], w = a.dataset.w, lo = w === 'comf' ? c.lo1 : c.lo2, hi = w === 'comf' ? c.hi1 : c.hi2, cur = this._cd[w];
        let v = act === 'cval' ? cur + +a.dataset.d * c.step : lo + this._slFrac(a, e) * (hi - lo);
        v = Math.round(v / c.step) * c.step; this._cd[w] = Math.max(lo, Math.min(hi, v)); this._render(true);
      }
      else if (act === 'prog') { this._prog = { kind: +a.dataset.kind }; this._pe = null; this._go('prog', a.dataset.back || 'main'); this._refresh(true); }
      else if (act === 'pday') { const k = this._prog.kind, d = +a.dataset.d, b = this._bits(k)[d]; if (b != null) { this._pe = { kind: k, day: d, bits: b, b0: b }; this._render(true); } }
      else if (act === 'phr') { this._pe.bits ^= (1 << +a.dataset.h); this._render(true); }
      else if (act === 'pall') { this._pe.bits = +a.dataset.v ? 0xFFFFFF : 0; this._render(true); }
      else if (act === 'pcancel') { this._pe = null; this._render(true); }
      else if (act === 'pok') {
        const pe = this._pe;
        if (pe.bits !== pe.b0) { (this._sp = this._sp || {})[pe.kind + ':' + pe.day] = { bits: pe.bits, t: Date.now() }; this._svc('set_schedule', { kind: pe.kind, day: pe.day, bits: pe.bits }); }
        this._pe = null; this._render(true);
      }
      else if (act === 'setmode') this._setMode(a.dataset.k, +a.dataset.i);
      else if (act === 'slider') { const r = a.getBoundingClientRect(); this._setMode(a.dataset.k, Math.round(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * 3)); }
      else if (act === 'fmsel') { if (this._fm) { this._fm.sel = +a.dataset.i; this._render(true); } }
      else if (act === 'fmstep') { const f = this._fm; if (f && f.sel >= 0) { const v = f.v[f.sel]; f.v[f.sel] = Math.max(0, Math.min(100, (isNaN(v) ? 50 : v) + +a.dataset.d)); this._render(true); } }
      else if (act === 'pinp') this._pinStep(+a.dataset.i, +a.dataset.s);
      else if (act === 'pinok') this._pinOk();
      else if (act === 'out') this._outSet(a.dataset.o, a.dataset.m);
      else if (act === 'toggle') {
        this._hass.callService('switch', this._on('power_switch') ? 'turn_off' : 'turn_on', { entity_id: this.E.power_switch });
      } else if (act === 'confirm') this._hass.callService('button', 'press', { entity_id: this.E.confirm });
      else if (act === 'more') {
        const ev = new Event('hass-more-info', { bubbles: true, composed: true });
        ev.detail = { entityId: this.E[a.dataset.e] }; this.dispatchEvent(ev);
      }
    });
    // przytrzymanie + / −: po 0,45 s powtarza co 0,12 s
    const fstop = () => { clearTimeout(this._fh0); clearInterval(this._fh1); };
    root.addEventListener('pointerdown', e => {
      const a = e.target.closest('[data-act=fuelpm]'); if (!a || this._mirror() || !this._hass) return;
      fstop(); this._fhold = false;
      this._fh0 = setTimeout(() => { this._fhold = true; this._fuelStep(+a.dataset.d); this._fh1 = setInterval(() => this._fuelStep(+a.dataset.d), 120); }, 450);
    });
    ['pointerup', 'pointerleave', 'pointercancel'].forEach(t => root.addEventListener(t, fstop));
    root.addEventListener('scroll', e => {
      const t = e.target; if (t && t.classList && t.classList.contains('list')) this._scroll[this._scr] = t.scrollTop;
    }, true);
    this._render(true);
  }
  _go(s, back) {
    this._backTo = back || (LIVE.includes(this._scr) ? this._scr : 'main');
    if (s === 'main') this._backTo = 'main';
    if (s === 'burner_s' && this._scr === 'fanmod') this._backTo = 'burn';
    if (s !== 'test' && s !== 'level') { this._testOk = false; this._pd = [0, 0, 0, 0]; }
    if (s === 'level') this._pd = [0, 0, 0, 0];
    if (s === 'fanmod') this._fm = null;
    this._scr = s; this._modal = false; this._pe = null;
    if (['main', 'heat', 'water', 'stats', 'prog'].includes(s)) this._refresh();
    this._render(true);
  }

  /* ---------- parts ---------- */
  _hdrLive(title) {
    return `<div class="h2"><span class="bk" data-go="main">EKRAN GŁ.</span><span class="tt">${title}</span>
      <span class="hi"><ha-icon icon="mdi:account"></ha-icon><span data-go="main"><ha-icon class="cy" icon="mdi:home"></ha-icon></span></span></div>`;
  }
  _fan(spin) {
    return `<svg viewBox="0 0 24 24" class="fan4 ${spin ? 'spin' : ''}"><g fill="#fff"><path d="M12 11C9.6 8.8 9.4 3.4 12 1.6C14.6 3.4 14.4 8.8 12 11Z"/><path d="M13 12C15.2 9.6 20.6 9.4 22.4 12C20.6 14.6 15.2 14.4 13 12Z"/><path d="M12 13C14.4 15.2 14.6 20.6 12 22.4C9.4 20.6 9.6 15.2 12 13Z"/><path d="M11 12C8.8 14.4 3.4 14.6 1.6 12C3.4 9.4 8.8 9.6 11 12Z"/></g><circle cx="12" cy="12" r="1.6" fill="#51618f"/></svg>`;
  }
  _augSvg(anim = true) {
    return `<svg viewBox="-2 -2 104 48" class="aug"><defs><clipPath id="augc"><rect x="-2" y="-2" width="104" height="17.6"/><rect x="-2" y="31.4" width="104" height="17.6"/></clipPath></defs><rect x="0" y="15.6" width="100" height="15.8" rx="2" fill="#566690" stroke="#fff" stroke-width="3.4"/><g clip-path="url(#augc)"><g><polyline points="-33.2,0 -18.5,44 -3.8,0 10.9,44 25.6,0 40.3,44 55.0,0 69.7,44 84.4,0 99.1,44 113.8,0 128.5,44 143.2,0 157.9,44 172.6,0 187.3,44" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="miter"/>${anim ? '<animateTransform attributeName="transform" type="translate" from="0 0" to="29.4 0" dur=".6s" repeatCount="indefinite"/>' : ''}</g></g></svg>`;
  }
  _auger(n, run) {
    if (!run) return '';
    return `<span class="augw">${this._augSvg()}<sup>${n}</sup></span>`;
  }
  _fuelDlg() {
    // wymiary 1:1 ze zdjęcia panelu (dialog 1555 px = 94,2 cqw => 0,0606 cqw/px)
    const kg = this._fuelKg(), cap = this._v('fuel_cap'), ft = this._v('feed_time');
    const pct = this._fuelPct();
    const barTop = 9.58, barH = 32.7, y = barTop + barH * (1 - pct);
    const chev = (d, top) => `<svg viewBox="0 0 24 13" class="fch" style="top:${top.toFixed(2)}cqw"><path d="${d}" fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/></svg>`;
    return `<div class="qd"><div class="qbg" style="top:4.7cqw;height:51.2cqw"></div>
      <div class="ftk"><div class="fth"></div>
        <svg viewBox="0 0 42 20" class="fhd"><path d="M3 20V9Q3 2.2 9.5 2.2H32.5Q39 2.2 39 9V20" fill="none" stroke="#f9d3cf" stroke-width="4.4"/></svg>
        <div class="fbar"><i style="height:${(pct * 100).toFixed(1)}%"></i></div>
        <div class="fhn" style="top:${y.toFixed(2)}cqw"></div>
        ${chev('M2 11L12 2.5L22 11', y - 3.03 - 1.25)}${chev('M2 2L12 10.5L22 2', y + 2.73 - 1.25)}
        <span class="fe">E</span></div>
      <span class="ftt">Paliwo</span>
      <span class="fbt" data-act="fuelpm" data-d="1" style="left:47.2cqw;top:15.7cqw;height:7.4cqw;width:11cqw">+</span>
      <span class="fkg">${isNaN(kg) ? '-' : Math.round(kg)}kg</span>
      <span class="fbt" data-act="fuelpm" data-d="-1" style="left:47.2cqw;top:32.8cqw;height:7.4cqw;width:11cqw">&minus;</span>
      <span class="fbt fau" data-act="feedgo">${this._augSvg(this._feeding() || this._fcLeft() !== null)}</span><span class="fts">${this._fcShow()}s</span>
      <div class="qok" data-act="ok" style="left:82.4cqw;top:45.8cqw;width:10.1cqw;height:6.67cqw;background:linear-gradient(#5b6a8a,#3e4a68);border-color:#2c3550">OK</div></div>`;
  }
  _hopper() {
    // zasobnik wypelniany "kropkami" proporcjonalnie do paliwa: 0 / 20 / 40 / 60 / 80 / 100 % (rzedy od dolu)
    const lv = Math.ceil(this._fuelPct() * HOP_ROWS.length - 1e-9);
    let dots = '';
    for (let i = 0; i < lv; i++) { const [y, xs] = HOP_ROWS[HOP_ROWS.length - 1 - i]; dots += xs.map(x => `<circle cx="${x}" cy="${y}" r="1.5"/>`).join(''); }
    return `<svg viewBox="${ICO.hopper.vb}" class="ic2" fill="#d6e4ff"><path d="${ICO.hopper.d}"/>${dots}</svg>`;
  }
  _brow(first, gear, second) {
    return `<div class="brow"><div class="c1">${first}</div><div class="c">${second || ''}</div><div class="c"></div><div class="c"></div><div class="c"></div><div class="c"></div>
      <div class="cg" ${gear ? `data-go="${gear}" data-back="${this._scr}"` : ''}><ha-icon icon="mdi:cogs"></ha-icon></div></div>`;
  }
  _sched(bands) {
    const X = h => 29 + h * 6.35;
    let t = '';
    for (let h = 0; h <= 24; h++) t += `<line x1="${X(h).toFixed(1)}" y1="${h % 6 === 0 ? 25 : 27}" x2="${X(h).toFixed(1)}" y2="32" stroke="#c5d0ea" stroke-width="${h % 6 === 0 ? 2 : 1.2}"/>`;
    const lab = [0, 6, 12, 18, 24].map(h => `<text x="${X(h).toFixed(1)}" y="49" text-anchor="${h === 0 ? 'start' : h === 24 ? 'end' : 'middle'}" font-size="17" fill="#dfe7fa">${h}</text>`).join('');
    const bs = (bands || []).map(([a, b]) => `<rect x="${X(a).toFixed(1)}" y="9" width="${((b - a) * 6.35).toFixed(1)}" height="14" fill="#ff2a22"/>`).join('');
    return `<svg viewBox="0 0 205 56" preserveAspectRatio="none" class="sched"><rect x="27" y="20" width="155" height="3" fill="#ff2a22"/>${bs}${t}${lab}</svg>`;
  }
  _tank() {
    return `<svg viewBox="0 0 70 124" preserveAspectRatio="none" class="tank"><defs><linearGradient id="tk" x1="0" x2="1"><stop offset="0" stop-color="#c9d3ea"/><stop offset=".45" stop-color="#ffffff"/><stop offset="1" stop-color="#aab7d6"/></linearGradient>
      <linearGradient id="cl" x1="0" x2="1"><stop offset="0" stop-color="#5f8cd8"/><stop offset="1" stop-color="#9dbcf0"/></linearGradient></defs>
      <rect x="8" y="6" width="54" height="110" rx="14" fill="url(#tk)"/><ellipse cx="35" cy="8" rx="26" ry="4" fill="#eef2fb"/>
      <g transform="translate(7.5 9.5) scale(.91 .7)"><path d="M14 32h12v-5h8v5h2c8 0 12 4 12 14" fill="none" stroke="#e5352b" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><rect x="22" y="20" width="14" height="5" rx="2" fill="#e5352b"/>
      <path d="M45 52q0 6-3 9 3 0 6 0" fill="none" stroke="#e5352b" stroke-width="0"/><circle cx="48" cy="58" r="3.4" fill="#e5352b"/></g>
      <path d="M18 70h34l-4 6 4 6-4 6 4 6-4 6H18l4-6-4-6 4-6-4-6z" fill="url(#cl)" opacity=".9"/>
      <g stroke="#fff" stroke-width="1.2" opacity=".9"><path d="M20 74h30M20 80h30M20 86h30M20 92h30M20 98h30M20 104h30"/></g></svg>`;
  }
  _rad(on) {
    let c = '';
    for (let i = 0; i < 9; i++) {
      const x = 37 + i * 21.9;
      c += `<rect x="${x}" y="8" width="14" height="126" rx="6" fill="url(#rd)"/><ellipse cx="${x + 7}" cy="9" rx="9" ry="6" fill="#f2f6ff"/><ellipse cx="${x + 7}" cy="133" rx="9" ry="6" fill="#dfe8fb"/>`;
    }
    return `<svg viewBox="0 0 232 143" preserveAspectRatio="none" class="rad"><defs><linearGradient id="rd" x1="0" x2="1"><stop offset="0" stop-color="#8fa8dc"/><stop offset=".45" stop-color="#ffffff"/><stop offset="1" stop-color="#8ea7da"/></linearGradient></defs>
      ${c}<rect x="34" y="22" width="196" height="5" rx="2" fill="#cfdaf3"/><rect x="34" y="112" width="196" height="5" rx="2" fill="#cfdaf3"/>
      <circle cx="26" cy="15" r="6" fill="none" stroke="#fff" stroke-width="2.6"/><path d="M0 15h18M32 15h6" stroke="#fff" stroke-width="3"/><path d="M0 124h38" stroke="#fff" stroke-width="3.2"/></svg>`;
  }
  _switch(closed) {
    return `<svg viewBox="0 0 110 36" class="sw"><g stroke="#fff" stroke-width="7.4" stroke-linecap="round" fill="none"><path d="M3.7 30H28.8M75.3 30H106.3"/><path d="${closed ? 'M28.8 30L78.4 30' : 'M28.8 30L71.3 4.4'}"/></g><circle cx="28.8" cy="30" r="6.4" fill="#fff"/><circle cx="77" cy="30" r="6.4" fill="#fff"/></svg>`;
  }
  _burner() {
    return `<img class="burn" alt="Palnik" src="${IMG().burner || ''}" draggable="false">`;
  }
  _boilerMain(burning) {
    return `<img class="boil" alt="Tekla" src="${IMG().boiler || ''}" draggable="false">`;
  }
  _pump(spin) {
    return `<svg viewBox="0 0 24 24" class="pmp ${spin ? 'spin' : ''}"><circle cx="12" cy="12" r="10" fill="none" stroke="#e9f0ff" stroke-width="2"/><circle cx="12" cy="12" r="7.6" fill="#e9f0ff" opacity=".35"/><path d="M12 5.6L18 16.6H6Z" fill="#fff"/></svg>`;
  }
  _lamp(on) { return `<span class="lamp ${on ? 'on' : ''}"></span>`; }

  /* ---------- live screens ---------- */
  _main(ctx) {
    const { burning, alarm, bname, out, sw } = ctx;
    const d = new Date();
    let day = d.toLocaleDateString('pl-PL', { weekday: 'long' }); day = day.charAt(0).toUpperCase() + day.slice(1);
    const time = d.toLocaleTimeString('pl-PL', { hour: 'numeric', minute: '2-digit' });
    const bar = (cls) => `<i class="ind ${cls}"></i>`;
    const fuel = this._s('fuel') && !isNaN(this._fuelKg()) ? Math.round(this._fuelKg()) : '-';
    return `
      <div class="top"><span class="tm">${time}</span><span class="dy">${day}</span>
        <span class="ot"><svg viewBox="0 0 108 68" class="wx" fill="#dbe7ff"><g stroke="#dbe7ff" stroke-width="5" stroke-linecap="round" fill="none"><circle cx="79" cy="32" r="14"/><path d="M79 5V9M79 55V59M52 32H56M102 32H106M60 13L63 16M98 13L95 16M98 51L95 48"/></g><path d="M12 68A12 12 0 0 1 13 44A18 18 0 0 1 46 36A15 15 0 0 1 74 50A9 9 0 0 1 72 68Z" stroke="#4a5a8c" stroke-width="3"/></svg>${this._p(out)}</span></div>
      ${this._boilerMain(burning)}
      <div class="big" data-act="more" data-e="boiler_temp">${this._p(this._v('boiler_temp'))}</div>
      <div class="st ${alarm ? 'al' : ''}">${bname}</div>
      <div class="tag" data-act="bdlg"><b>${isNaN(this._v('boiler_set')) ? '-' : Math.round(this._v('boiler_set'))}</b>${this._chipHtml(ctx.bm)}</div>
      ${ctx.bm < 2 ? `<div class="tbar" data-act="prog" data-kind="2" data-back="main">${this._sched(this._todayBands(2, []))}</div>` : ''}
      <div class="bbar">
        <div class="cell"><svg viewBox="0 0 35 30.2" class="ic mic"><path d="M0 1.3H35M0 8.5H35M0 15.8H35" stroke="#d6e4ff" stroke-width="2.6" fill="none"/><text x="0" y="29.7" textLength="35" lengthAdjust="spacingAndGlyphs" font-size="11" font-weight="700" fill="#d6e4ff" font-family="Roboto Condensed,Roboto,Arial,sans-serif">MENU</text></svg><small class="mn" data-go="menu"></small></div>
        <div class="cell" data-act="fuel"><small class="fl">${fuel === '-' ? '-' : fuel + 'kg'}</small>${this._hopper()}</div>
        <div class="cell" data-go="burn">${bar(this._v('burner_code') % 256 === 5 ? 'g' : [1, 2].includes(this._v('burner_code') % 256) ? 'g gb' : '')}${this._on('ban') ? '<i class="ban"></i>' : ''}<svg viewBox="${ICO.flame.vb}" class="ic2" fill="#d6e4ff" fill-rule="evenodd"><path d="${ICO.flame.d}"/></svg></div>
        <div class="cell" data-go="heat">${bar(this._on('co_pump') ? 'g' : '')}<span class="radi"><svg viewBox="${ICO.radi.vb}" class="ic2" fill="#d6e4ff" fill-rule="evenodd"><path d="${ICO.radi.d}"/></svg><sup>1</sup></span></div>
        <div class="cell"></div>
        <div class="cell" data-go="water">${bar(this._on('cwu_pump') ? 'g' : '')}<svg viewBox="${ICO.faucet.vb}" class="ic2" fill="#d6e4ff" fill-rule="evenodd"><path d="${ICO.faucet.d}"/></svg></div>
        <div class="cell" data-act="quick">${bar(sw ? 'g' : 'r')}<svg viewBox="${ICO.power.vb}" class="ic2" fill="#d6e4ff" fill-rule="evenodd"><path d="${ICO.power.d}"/></svg></div>
      </div>
      <div class="mnb" data-go="menu"></div>${alarm ? '<div class="alic" data-go="alarm" data-back="main">!</div>' : ''}`;
  }
  _water(ctx) {
    const set = this._v('cwu_set'), cf = this._v('cwu_comfort'), eco = this._v('cwu_eco');
    const wm = this._mode('cwu_mode');
    const m = wm ? [wm.ic, wm.sup] : !isNaN(set) && !isNaN(eco) && set === eco && set !== cf ? ['mdi:weather-night', 'eco'] : ['mdi:white-balance-sunny', 'comf'];
    return `${this._hdrLive('WODA')}
      ${this._tank().replace('class="tank"', 'class="tank pos-tank"')}
      <div class="bigv" data-act="more" data-e="cwu_temp">${this._p(this._v('cwu_temp'))}</div>
      <div class="box b1" data-act="cdlg" data-k="cwu"><b>${isNaN(set) ? '-' : Math.round(set)}</b><span class="mi"><ha-icon icon="${m[0]}"></ha-icon><sup>${m[1]}</sup></span></div>
      <div class="box b2" data-act="prog" data-kind="0" data-back="water">${this._sched(this._todayBands(0, this.SCH.cwu))}</div>
      ${this._brow(`${this._pump(this._on('cwu_pump'))}`, 'cwu_s')}${this._modal === 'cwu' ? this._cDlg('cwu') : ''}`;
  }
  _heat(ctx) {
    const sv = this._v('co_set'), aux = isNaN(sv) ? '' : Math.round(sv);
    return `${this._hdrLive('OGRZEWANIE 1')}
      <div class="cot" data-act="more" data-e="co_temp">${this._p(this._v('co_temp'))}${aux !== '' ? `<sup>${aux}</sup>` : ''}</div>
      ${this._rad()}
      ${this._switch(this._on('co_pump'))}
      <div class="box b1 mono" data-act="cdlg" data-k="co"><span class="mi lone"><ha-icon icon="${(this._mode('co_mode') || { ic: 'mdi:white-balance-sunny' }).ic}"></ha-icon><sup>${this._mode('co_mode') ? this._mode('co_mode').sup : 'comf'}</sup></span></div>
      <div class="box b2" data-act="prog" data-kind="1" data-back="heat">${this._sched(this._todayBands(1, this.SCH.co))}</div>
      ${this._brow(`${this._pump(this._on('co_pump'))}`, 'co_s')}${this._modal === 'co' ? this._cDlg('co') : ''}`;
  }
  _burn(ctx) {
    const kgh = this._opt('burn_kgh', 1), kw = this._opt('burn_kw', 1), br = this._opt('burn_bright', 0), bt = this._opt('burn_temp', 0);
    const pw = this._p(this._v('power'), 0);
    const fanOff = this._v('fan_pct') === 0; // wentylator stoi: bez liczby i bez ikony
    const fan = fanOff ? '' : this._opt('fan_pct', 0, ''), fd = this._s('feeder') ? this._t('feeder', '') : '', tm = this._s('burn_time') ? this._t('burn_time', '') : '';
    return `${this._hdrLive('PALNIK')}
      <div class="bname">${ctx.bname}</div>${this._burner()}
      <div class="stats"><div>spalanie[kg/h]=${kgh}</div><div>moc[kW]=${kw}</div><div>moc[%]=${pw}</div><div>jasność=${br}</div><div>&nbsp;</div><div>T. palnika=${bt}</div></div>
      <div class="mini"><span>${fan}</span><span>${fd}</span><span class="tmn">${tm}</span></div>
      ${this._brow(fanOff ? '' : this._fan(isNaN(this._v('fan_pct')) ? (this._s('blower_run') ? this._on('blower_run') : ctx.burning) : this._v('fan_pct') > 0), 'burner_s', this._auger(1, this._on('feeder_run')))}`;
  }
  _quick(sw) {
    const set = this._v('cwu_set'), cf = this._v('cwu_comfort'), eco = this._v('cwu_eco');
    const wm = this._mode('cwu_mode');
    const wpos = wm ? wm.pos : !isNaN(set) && !isNaN(eco) && set === eco && set !== cf ? 0.32 : 0.95;
    const cm = (this._s('co_mode') ? this._t('co_mode', 'comf') : 'comf').toLowerCase();
    const cmm = this._mode('co_mode');
    const cpos = cmm ? cmm.pos : cm.startsWith('eco') ? 0.32 : cm.startsWith('off') ? 0.05 : 0.95;
    const mi = (k, n, x, y, ic, sup) => `<span class="mdi" data-act="setmode" data-k="${k}" data-i="${n}" style="left:${x}cqw;top:${y}cqw"><ha-icon icon="${ic}"></ha-icon>${sup ? `<sup>${sup}</sup>` : ''}</span>`;
    const modes = (k, y, xs) => MODES.map((m, n) => mi(k, n, xs[n], y, m.ic, m.sup)).join('');
    const slider = (k, x, y, w, p) => { const f = Math.max(p, 0.001); return `<div class="sl" data-act="slider" data-k="${k}" style="left:${x}cqw;top:${y}cqw;width:${w}cqw"><b style="width:${(p * 100).toFixed(1)}%;background-size:${(100 / f).toFixed(1)}% 100%"></b><i style="left:${(p * 100).toFixed(1)}%"></i></div>`; };
    return `<div class="qd"><div class="qbg"></div>
      <span class="qa" style="left:8.1cqw;top:11.7cqw">Kocioł</span><span class="tgq ${sw ? 'on' : ''}" data-act="toggle"><i></i></span>
      <span class="qa" style="left:7.8cqw;top:25.2cqw">Ogrzewanie 1</span>${modes('co_mode', 24.7, [39.5, 51.7, 63, 75.8])}${slider('co_mode', 37.5, 28.9, 38.4, cpos)}
      <span class="qa" style="left:7.6cqw;top:45.5cqw">Woda użytkowa</span>${modes('cwu_mode', 45.3, [38.5, 51, 61.8, 74.9])}${slider('cwu_mode', 37.1, 49.1, 38.4, wpos)}
      <div class="qok" data-act="ok">OK</div></div>`;
  }

  /* ---------- list pages (menu / ustawienia) ---------- */
  _hdr(title, back, sup = '1') {
    const lab = back === 'menu' ? 'MENU' : back === 'main' ? 'EKRAN GŁ.' : 'WSTECZ';
    return `<div class="h2"><span class="bk" data-go="${back}">&lsaquo; ${lab}</span><span class="tt">${title}</span>
      <span class="hi"><span class="wr"><ha-icon icon="mdi:wrench"></ha-icon><sup>${sup}</sup></span><span data-go="main"><ha-icon class="cy" icon="mdi:home"></ha-icon></span></span></div>`;
  }
  _row(label, val) { return `<div class="row"><span class="l">${label}</span><span class="v">${val}</span></div>`; }
  _tog(label, on, red) { return `<div class="row ${red ? 'red' : ''}"><span class="l">${label}</span><span class="tg ${on ? 'on' : ''}"><i></i></span></div>`; }
  _page(title, back, body) { return `${this._hdr(title, back)}<div class="list">${body}</div>`; }
  // Moc dmuchawy modulacja [%]: 5 progow mocy kotla (20..100 %) -> obroty dmuchawy.
  // Wymiary zmierzone na zdjeciu panelu. Klik w wartosc = wybor, strzalki gora/dol = korekta co 1 (szkic lokalny, bez zapisu do kotla)
  _fanMod() {
    const fm = this._fm || (this._fm = { v: [1, 2, 3, 4, 5].map(i => this._v('fan_mod_' + i)), sel: -1 });
    const PX = 9.98, PY = 13.6, PW = 71.7, PH = 36.3, X = i => 14.9 + i * 16.03, Y = v => isNaN(v) ? 32.1 : 32.1 - (v - 56) * 0.05;
    const pts = fm.v.map((v, i) => `<span class="fmv ${fm.sel === i ? 'sel' : ''}" data-act="fmsel" data-i="${i}" style="left:${X(i).toFixed(2)}cqw;top:${(Y(v) - 6.2).toFixed(2)}cqw">${isNaN(v) ? '-' : Math.round(v)}</span><i class="fmp ${fm.sel === i ? 'sel' : ''}" data-act="fmsel" data-i="${i}" style="left:${X(i).toFixed(2)}cqw;top:${Y(v).toFixed(2)}cqw"></i>`).join('');
    const lab = [20, 40, 60, 80, 100].map((m, i) => `<span class="fml" data-act="fmsel" data-i="${i}" style="left:${(X(i) - 1.1).toFixed(2)}cqw">${m}</span>`).join('');
    const poly = fm.v.map((v, i) => `${((X(i) - PX) / PW * 100).toFixed(2)},${((Y(v) - PY) / PH * 100).toFixed(2)}`).join(' ');
    const ch = d => `<svg viewBox="0 0 24 14" class="fmc"><path d="${d}" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    return `<div class="qd" style="background:rgba(30,40,78,.3)"><div class="qbg"></div>
      <span class="fmt">Moc dmuchawy modulacja [%]</span>
      <div class="fmb"><svg viewBox="0 0 100 100" preserveAspectRatio="none"><polyline points="${poly}" fill="none" stroke="#19d3f7" stroke-width="3" vector-effect="non-scaling-stroke"/></svg></div>
      ${pts}${lab}
      <span class="fbt fma ${fm.sel < 0 ? 'dis' : ''}" data-act="fmstep" data-d="1" style="left:84.8cqw;top:19.4cqw;width:11cqw;height:7.4cqw">${ch('M3 11L12 3L21 11')}</span>
      <span class="fbt fma ${fm.sel < 0 ? 'dis' : ''}" data-act="fmstep" data-d="-1" style="left:84.8cqw;top:28.5cqw;width:11cqw;height:7.4cqw">${ch('M3 3L12 11L21 3')}</span>
      <div class="qok" data-go="burner_s" data-back="burn" style="left:84.8cqw;top:45.8cqw;width:11cqw;height:7.4cqw;background:linear-gradient(#5b6a8a,#3e4a68);border-color:#2c3550">OK</div></div>`;
  }
  _alarmPg(back) {
    const txt = this._t('last_alarm', ''), m = /kod\s+(\d+)/.exec(txt), code = m ? +m[1] : 0, act = this._on('alarm') || (this._v('burner_code') & 255) === 10;
    const raw = ALARM_PL[code] || ((/\(([^)]*)\)/.exec(txt) || [])[1] || '');
    const nm = raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : '';
    const t0 = parseInt(this._t('alarm_start', '0'), 10), d = t0 > 1e9 ? new Date(t0 * 1000) : null;
    const dd = d ? d.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC' }) : '-';
    const tt = d ? d.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) : '-';
    const body = code ? `<span class="al1" style="left:9.8cqw;top:17.4cqw">NR: 1</span><span class="al1" style="left:30cqw;top:17.7cqw">KOD: ${code}</span>
        <span class="al1" style="left:9.8cqw;top:24cqw">${nm}</span>
        <span class="al1" style="left:9.8cqw;top:30cqw">Powstanie:</span><span class="al1" style="left:46cqw;top:30.2cqw">${dd}</span><span class="al1" style="left:71cqw;top:30.4cqw">${tt}</span>
        ${act ? `<div class="alb" data-act="confirm">POTWIERDŹ</div><span class="ala">AKTYWNY</span>` : ''}
        <div class="alar" style="top:22cqw">&#8963;</div><div class="alar" style="top:35.5cqw">&#8964;</div>`
      : '<span class="al1" style="left:0;right:0;text-align:center;top:26cqw">Brak alarmów</span>';
    return `${this._hdr('HISTORIA ALARMÓW', back, '2')}<div class="alln" style="top:14.2cqw"></div>${body}<div class="alln" style="top:49.6cqw"></div>`;
  }
  _menu() {
    return this._page('MENU', 'main', MENU.filter(([k]) => !SERVICE.includes(k) || this._unl()).map(([k, n]) => `<div class="row go" data-go="${k}" data-back="menu"><span class="l">${n}</span><span class="v ch">&rsaquo;</span></div>`).join(''));
  }
  _body(s) {
    const burning = [1, 2, 5].includes(this._v('burner_code') & 255);
    const e = (l, v) => this._row(l, v);
    const back = ['boiler', 'stats', 'test', 'net', 'info', 'level'].includes(s) ? 'menu' : this._backTo;
    const P = (t, b) => this._page(t, back, b.join(''));
    if (s === 'alarm') return this._alarmPg(this._backTo === 'main' ? 'main' : 'menu');
    switch (s) {
      case 'boiler': return P(TITLES.boiler, [
        this._tog('Kocioł włączony', this._on('on')),
        e('Temperatura kotła [°C]', this._p(this._v('boiler_temp'))), e('Zadana wynikowa [°C]', this._p(this._v('boiler_set'), 0)),
        e('Zadana ręczna [°C]', this._p(this._v('boiler_manual'), 0)), e('Tryb pracy', this._t('mode')),
        e('Temperatura zewnętrzna [°C]', this._p(this._v('outside')))]);
      case 'burner_s': return P(TITLES.burner_s, [
        e('Korekta powietrza [%]', this._p(this._v('air_corr'), 0)), e('Moc min [%]', this._p(this._v('power_min'), 0)),
        e('Moc max [%]', this._p(this._v('power_max'), 0)), e('Wartość opałowa [kWh/kg]', this._p(this._v('fuel_heat'), 1)),
        e('Ilość paliwa test [kg/h]', this._p(this._v('fuel_test'), 1)),
        ...(this._unl() ? ['<div class="svsep">SERWIS</div>',
          '<div class="row go" data-go="fanmod" data-back="burner_s"><span class="l">Moc dmuchawy modulacja [%]</span><span class="v ch">&rsaquo;</span></div>'] : [])]);
      case 'level': return this._pinPg(back, TITLES.level, this._unl() ? 'Serwis aktywny. PIN 0000 blokuje' : 'Wpisz PIN');
      case 'fanmod': return this._fanMod();
      case 'co_s': return P(TITLES.co_s, [
        e('Temperatura CO [°C]', this._p(this._v('co_temp'))), e('Zadana wynikowa [°C]', this._p(this._v('co_set'), 0)),
        e('Zadana ręczna [°C]', this._p(this._v('co_manual'), 0)), this._tog('Pompa CO', this._on('co_pump')),
        e('Temperatura zewnętrzna [°C]', this._p(this._v('outside')))]);
      case 'cwu_s': return P(TITLES.cwu_s, [
        e('Temperatura CWU [°C]', this._p(this._v('cwu_temp'))), e('Zadana wynikowa [°C]', this._p(this._v('cwu_set'), 0)),
        e('Zadana komfort [°C]', this._p(this._v('cwu_comfort'), 0)), e('Zadana ekonomiczna [°C]', this._p(this._v('cwu_eco'), 0)),
        this._tog('Pompa CWU', this._on('cwu_pump'))]);
      case 'stats': {
        const sv = this._t('stats', '').trim().split(/\s+/), n = i => (/^\d+$/.test(sv[i] || '') ? sv[i] : '-');
        return `${this._hdr(TITLES.stats, back, '2')}<div class="list">${[
          ['Licznik rozpaleń', n(0)], ['Średni czas rozpalania [s]', n(1)], ['Średnia moc palnika z 50 godzin [%]', '-'],
          ['Czas pracy podajnika 1 [h]', n(2)], ['Czas pracy podajnika 2 [h]', n(3)], ['Całkowite zużycie paliwa [kg]', n(4)],
          ['Średni tlen dla mocy 30% [%]', '-'], ['Średni tlen dla mocy 50% [%]', '-'], ['Średni tlen dla mocy 70% [%]', '-'], ['Średni tlen dla mocy 90% [%]', '-'],
          ['Liczba czyszczeń wymiennika', n(5)], ['Liczba przegrzań kotła', n(6)], ['Liczba zaników zasilania', n(7)]].map(([l, v]) => this._row(l, v)).join('')}</div>`;
      }
      case 'test': {
        const ctl = (o, name, run) => {
          const cur = this._outMode(o), has = m => !!this.E[o + '_' + m];
          const b = (m, l) => `<em ${has(m) ? `data-act="out" data-o="${o}" data-m="${m}"` : ''} class="${has(m) ? 'cl' : 'dis'}"><small>${l}</small><b class="${cur === m ? 'ck' : ''}">${cur === m ? '&#10003;' : ''}</b></em>`;
          return `<div class="row tst"><span class="l">${this._lamp(run)}${name}</span><span class="abo">${b('auto', 'A')}${b('off', 'OFF')}${b('on', 'ON')}</span></div>`;
        };
        const ro = (n, on) => `<div class="row tst ro"><span class="l">${this._lamp(on)}${n}</span><span class="abo"><em><small>A</small><b></b></em><em><small>OFF</small><b></b></em><em><small>ON</small><b></b></em></span></div>`;
        return P(TITLES.test, [ctl('blower', 'Dmuchawa', this._on('blower_run')), ctl('feeder', 'Podajnik', this._on('feeder_run')),
          ro('Pompa CWU', this._on('cwu_pump')), ro('Pompa CO', this._on('co_pump')), ro('Palnik', burning),
          '<div class="dim" style="padding:1.6cqw 1.2cqw">Pompy i palnik: tylko podgląd (kocioł nie udostępnia sterowania).</div>']);
      }
      case 'net': {
        const ok = this._on('can_ok');
        return P(TITLES.net, [`<div class="net"><div><span>IGNEO TOUCH</span><span>Node ID=4</span></div><div><span>CAN IO BIG</span><span>Node ID=86</span></div><div><span>CAN (ESPHome)</span><span class="${ok ? 'gn' : 'rd'}">${ok ? 'OK' : 'BRAK'}</span></div></div>`]);
      }
      case 'info': return P(TITLES.info, [`<div class="inf"><div class="dim">igneo Touch wersja</div><div class="dim rd">Nazwa kotła</div><div>Tekla / Estyma</div><div class="big2">Controller by Estyma (www.estyma.pl)</div></div>`]);
      default: return this._menu();
    }
  }

  _render(force) {
    if (!this._built || !this._hass) return;
    const keys = Object.keys(this.E).map(k => (this._hass.states[this.E[k]] || {}).state);
    const sig = this._scr + '|' + this._modal + '|' + keys.join(',') + '|' + new Date().getMinutes();
    if (!force && sig === this._sig) return;
    this._sig = sig;
    const R = this.shadowRoot, scr = R.getElementById('scr');
    const code = this._v('burner_code') & 255;
    const burning = [1, 2, 5].includes(code);
    const alarm = this._on('alarm') || code === 10;
    const sw = this._on('power_switch') || this._on('on');
    const bname = isNaN(code) ? this._t('burner') : (BURNER[code] || this._t('burner'));
    const mode = this._t('mode', '').toLowerCase();
    const chip = mode.includes('ręcz') || mode.includes('recz') ? 'MAN' : mode.includes('czas') ? 'TIME' : 'AUTO';
    const ctx = { burning, alarm, bname, chip, bm: this._bMode(), out: this._v('outside'), sw };
    // diody na obudowie (płomień: rozpalanie = płynne pulsowanie, modulacja = świeci)
    const fl = code === 5 ? 'on' : (code === 1 || code === 2) ? 'bl' : '';
    const strip = R.getElementById('strip');
    if (strip.dataset.fl !== fl || strip.dataset.sw !== String(sw) || strip.dataset.al !== String(alarm)) {
      strip.dataset.fl = fl; strip.dataset.sw = String(sw); strip.dataset.al = String(alarm);
      strip.innerHTML = `
      <div class="sr"><ha-icon icon="mdi:power"></ha-icon><i class="led g ${sw ? 'on' : ''}"></i></div>
      <div class="sr"><ha-icon icon="mdi:fire"></ha-icon><i class="led o ${fl}"></i></div>
      <div class="sr"><ha-icon icon="mdi:alert-outline"></ha-icon><i class="led r ${alarm ? 'on' : ''}"></i></div>`;
    }
    if (SERVICE.includes(this._scr) && !this._unl()) { this._scr = 'menu'; this._backTo = 'main'; }
    const live = LIVE.includes(this._scr);
    scr.className = 'screen ' + (live ? 's-' + this._scr : 'is-sub') + (this._scr === 'alarm' ? ' s-alarm' : '');
    let html;
    if (this._scr === 'main') html = this._main(ctx) + (this._modal === 'fuel' ? this._fuelDlg() : this._modal === 'boiler' ? this._bDlg() : this._modal ? this._quick(sw) : '');
    else if (this._scr === 'water') html = this._water(ctx);
    else if (this._scr === 'heat') html = this._heat(ctx);
    else if (this._scr === 'burn') html = this._burn(ctx);
    else if (this._scr === 'menu') html = this._menu();
    else if (this._scr === 'prog') html = this._progPg();
    else html = this._body(this._scr);
    scr.innerHTML = html;
    const l = scr.querySelector('.list');
    if (l && this._scroll[this._scr]) l.scrollTop = this._scroll[this._scr];
  }

  _css() {
    return `
    :host{display:block}
    *{box-sizing:border-box}
    .bezel{container-type:inline-size;display:grid;grid-template-columns:14% 1fr;align-items:center;background:linear-gradient(160deg,#17181b,#050506);border-radius:16px;padding:2.6% 2.6% 2.6% 0;box-shadow:0 6px 24px #0008,inset 0 0 0 1px #2c2c2e;font-family:'Roboto Condensed','Arial Narrow',Roboto,sans-serif}
    .strip{display:flex;flex-direction:column;justify-content:space-around;align-items:center;height:100%;padding:0 0 0 8%;gap:6cqw}
    .sr{display:flex;align-items:center;gap:2.6cqw;color:#c9ccd3}
    .sr ha-icon{--mdc-icon-size:5.2cqw}
    .led{width:3.4cqw;height:1.7cqw;border-radius:.5cqw;background:#25282c;display:block}
    .led.g.on{background:#8bf01f;box-shadow:0 0 1.6cqw #8bf01f}.led.o.on{background:#ffb21a;box-shadow:0 0 1.6cqw #ffb21a}.led.r.on{background:#ff2a22;box-shadow:0 0 1.6cqw #ff2a22}
    .led.o.bl{animation:blk 3s ease-in-out infinite}
    @keyframes blk{0%,100%{background:#25282c;box-shadow:0 0 0 #ffb21a00}50%{background:#ffb21a;box-shadow:0 0 1.6cqw #ffb21a}}
    .screen{container-type:inline-size;position:relative;aspect-ratio:768/437;width:100%;overflow:hidden;border-radius:4px;color:#fff;user-select:none;-webkit-tap-highlight-color:transparent;background:linear-gradient(#566187,#2c355a 55%,#1b2240)}
    ha-icon{--mdc-icon-size:6.6cqw;display:inline-flex}
    .cy{color:#19d3f7}
    .spin{animation:spin 2.4s linear infinite}
    /* main */
    .s-main{background:linear-gradient(180deg,#5c6890,#3e4a74 70%)}
    .top{position:absolute;left:0;right:0;top:0;height:9cqw;font-size:4.6cqw;line-height:9cqw}
    .tm{position:absolute;left:4.2cqw}.dy{position:absolute;left:0;right:.8cqw;text-align:center;font-size:4.6cqw;letter-spacing:-.25cqw}
    .ot{position:absolute;right:11.2cqw;display:flex;align-items:center;gap:1.9cqw}.ot .wx{width:7cqw;height:4.4cqw}
    .boil{position:absolute;left:7cqw;top:7.2cqw;width:16cqw;height:auto;display:block;pointer-events:none}
    .big{position:absolute;left:30.4cqw;width:46cqw;top:11.9cqw;text-align:center;font-size:18.3cqw;line-height:1;color:#eaf0ff;cursor:pointer}
    .st{position:absolute;left:30.5cqw;width:46cqw;top:29cqw;text-align:center;font-size:7.4cqw;line-height:1;color:#eef3ff}.st.al{color:#ff5a52}
    .tag{position:absolute;right:.3cqw;top:12.8cqw;width:27.3cqw;height:7.1cqw;background:linear-gradient(#4d78cc,#3b5fa8);border:.3cqw solid #6a93e0;display:flex;align-items:center;gap:2cqw;padding-left:1.9cqw;cursor:pointer;border-radius:.4cqw;box-sizing:border-box}
    .tag b{font-size:7.5cqw;font-weight:400;color:#e8f0ff;line-height:1}
    .tag u{text-decoration:none;font-size:1.9cqw;border:.2cqw solid #dfe8ff;color:#dfe8ff;padding:.1cqw .5cqw;border-radius:.4cqw;font-weight:700;align-self:flex-start;margin-top:1.2cqw}
    .bbar{position:absolute;left:0;right:0;bottom:0;height:15.5cqw;display:flex;background:#3d63b5}
    .cell{position:relative;flex:1;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:.2cqw;background:linear-gradient(#5d8ae0,#4268bd);border-left:.5cqw solid #263872;padding-top:1.7cqw;cursor:pointer}
    .cell:first-child{border-left:0}.cell:nth-child(5){background:linear-gradient(#4f78c8,#3d62b4);cursor:default}
    .cell .ic{width:7.4cqw;height:7.4cqw}.cell:first-child .ic{margin-top:-3.4cqw}.cell ha-icon{--mdc-icon-size:7cqw;color:#d6e4ff}
    .cell small.fl{position:absolute;top:.9cqw;font-size:3.3cqw;font-weight:700;color:#e3ecff}
    .cell em{font-style:normal;font-size:3.6cqw;line-height:.4;color:#d6e4ff}
    .mnb{position:absolute;left:0;bottom:0;width:14.28%;height:15.5cqw}
    .radi{position:relative;display:flex}.radi sup{position:absolute;right:-2cqw;top:-.8cqw;font-size:3cqw;color:#d6e4ff}
    /* dolny pasek 1:1 z panelu (wymiary ze zdjecia, 1 px zdjecia = .1683cqw) */
    .cell{padding-top:0}
    .cell>svg,.cell>.radi{position:absolute!important;left:50%;margin:0!important;transform:translateX(-50%)}
    .cell small.fl{top:1.07cqw;font-size:3.4cqw;line-height:1;font-weight:500;letter-spacing:-.02em;transform:scaleX(.85)}
    /* ikony dolnego paska: ksztalty sledzone ze zdjecia panelu */
    .cell>.mic{width:5.9cqw!important;height:5.08cqw!important;top:6.0cqw}
    .cell[data-act=fuel]>svg{width:6.66cqw!important;height:5.52cqw!important;top:6.75cqw;left:calc(50% + 0.04cqw)}
    .cell[data-go=burn]>svg.ic2{width:4.88cqw!important;height:6.55cqw!important;top:5.13cqw;left:calc(50% + 0.2cqw)}
    .cell[data-go=heat]>.radi{top:5.47cqw;left:calc(50% + -0.56cqw);display:block}.cell[data-go=heat] .radi svg{width:5.02cqw!important;height:6.14cqw!important;display:block}
    .cell[data-go=heat] .radi sup{right:auto;left:calc(100% + .9cqw);top:-.1cqw;font-size:2.7cqw;line-height:1}
    .cell[data-go=water]>svg.ic2{width:6.83cqw!important;height:7.32cqw!important;top:4.88cqw;left:calc(50% + 0.16cqw)}
    .cell[data-act=quick]>svg.ic2{width:7.59cqw!important;height:7.41cqw!important;top:4.88cqw;left:calc(50% + 0.24cqw)}
    .ind{top:1.4cqw;height:1.3cqw;width:9.6cqw;margin-left:-4.8cqw;border-radius:.5cqw}
    .ind.g,.ind.gb{background:#3ee34a;box-shadow:0 0 1.4cqw #3ee34a}
    .ind.gb{animation:ignb 3s ease-in-out infinite}
    @keyframes ignb{0%,100%{background:#31477f;box-shadow:0 0 0 #3ee34a00}50%{background:#3ee34a;box-shadow:0 0 1.4cqw #3ee34a}}
    .ind{position:absolute;top:1.9cqw;left:50%;width:9.8cqw;height:1cqw;margin-left:-4.9cqw;background:#31477f;border-radius:.6cqw}
    .ind.y{background:#ece23a;box-shadow:0 0 1.4cqw #ece23a}.ind.w{background:#cfe0ff;box-shadow:0 0 1.2cqw #9fc0ff}.ind.g{background:#86e61f;box-shadow:0 0 1.4cqw #86e61f}.ind.r{background:#2c3e70}
    .ban{position:absolute;right:30%;bottom:17%;width:3.4cqw;height:3.4cqw;border-radius:50%;background:#f0301f;box-shadow:0 0 0 .35cqw #fff3,0 0 1.2cqw #f0301f}.ban::after{content:'';position:absolute;left:18%;right:18%;top:42%;height:16%;background:#fff;border-radius:.3cqw}
    .alic{position:absolute;left:87cqw;top:31cqw;width:6.4cqw;height:6.4cqw;border-radius:50%;background:#f4c20d;color:#2b2b2b;font-size:5.2cqw;font-weight:700;display:flex;align-items:center;justify-content:center;cursor:pointer;animation:alb 1.1s steps(1) infinite}
    @keyframes alb{50%{opacity:.12}}
    .s-alarm{background:linear-gradient(#5b88cc,#4975b9)}
    .al1{position:absolute;font-size:4.6cqw;line-height:1;color:#fff;white-space:nowrap}
    .alln{position:absolute;left:11.7cqw;right:13.5cqw;height:.4cqw;background:#19b4e8}
    .alb{position:absolute;left:32.7cqw;top:36.4cqw;width:26.7cqw;height:7.4cqw;display:flex;align-items:center;justify-content:center;font-size:4.2cqw;background:linear-gradient(#6a93d8,#5079c0);border:.3cqw solid #86a9e4;border-radius:.5cqw;cursor:pointer}
    .ala{position:absolute;left:32.7cqw;width:26.7cqw;text-align:center;top:45.3cqw;font-size:4.2cqw;line-height:1;color:#ff4a3d}
    .alar{position:absolute;left:86cqw;width:9.6cqw;height:6.2cqw;display:flex;align-items:center;justify-content:center;font-size:6cqw;line-height:1;background:linear-gradient(#6a93d8,#5079c0);border:.3cqw solid #86a9e4;border-radius:.5cqw;opacity:.8}
    /* quick dialog */
    .qd{position:absolute;inset:0;background:rgba(30,40,78,.72)}
    .qbg{position:absolute;left:4.95cqw;top:6.5cqw;width:94.3cqw;height:49.2cqw;background:linear-gradient(#5a88cd,#4a76bb);border:.3cqw solid #7fa6e4;border-radius:.5cqw;box-sizing:border-box;box-shadow:0 0 3cqw #0008}
    .qa{position:absolute;color:#fff;font-size:4.1cqw;font-weight:700;line-height:1;white-space:nowrap}
    .tgq{position:absolute;left:38.2cqw;top:11.85cqw;width:10cqw;height:3.8cqw;border-radius:1.9cqw;background:#68789b;box-shadow:inset 0 0 .8cqw #0006;cursor:pointer}
    .tgq i{position:absolute;top:.3cqw;width:3.2cqw;height:3.2cqw;border-radius:50%;background:radial-gradient(#fff,#b9c6e3)}
    .tgq.on{background:linear-gradient(#58b52b,#3e951a)}.tgq.on i{right:.3cqw}.tgq:not(.on) i{left:.3cqw}
    .tgq.on::before{content:'I';position:absolute;left:1.6cqw;top:.3cqw;font-size:3cqw;line-height:3.2cqw;color:#e8ffd8}
    .mdi{cursor:pointer;position:absolute;color:#e3ecff;display:flex;align-items:center;justify-content:center;width:6cqw;height:6cqw;margin:-3cqw 0 0 -3cqw}.mdi ha-icon{--mdc-icon-size:5.6cqw}.mdi sup{position:absolute;left:3.6cqw;top:-.6cqw;font-size:2.1cqw}
    .sl{position:absolute;height:2.2cqw;border-radius:1.1cqw;background:#68789b;box-shadow:inset 0 0 .6cqw #0006;cursor:pointer}.sl::before{content:'';position:absolute;inset:-2.4cqw 0}
    .sl b{position:absolute;left:0;top:0;bottom:0;border-radius:1.1cqw;background-image:linear-gradient(90deg,#3fd0ff,#e9e14a 40%,#ff7a22 70%,#ff2a22);background-repeat:no-repeat}
    .sl i{position:absolute;top:-1.05cqw;width:3.9cqw;height:3.9cqw;margin-left:-1.95cqw;border-radius:50%;background:radial-gradient(#fff,#aebddb);box-shadow:0 0 .8cqw #0008}
    .qok{position:absolute;left:82.7cqw;top:44.9cqw;width:10.4cqw;height:6.9cqw;display:flex;align-items:center;justify-content:center;font-size:4.6cqw;background:linear-gradient(#5e86c9,#4a6fb0);border:.3cqw solid #86a9e4;border-radius:.5cqw;cursor:pointer;box-sizing:border-box}
    .tag .ck{position:relative;display:inline-flex;color:#e8f0ff;margin-left:2cqw;align-self:center}.tag .ck ha-icon{--mdc-icon-size:5.6cqw}.tag .ck sup{position:absolute;right:-1.7cqw;bottom:-.6cqw;font-size:2.4cqw;font-weight:700}
    .tbar{position:absolute;right:.3cqw;top:21.4cqw;width:27.3cqw;height:8.6cqw;cursor:pointer}
    .qx{position:absolute;inset:0}
    .bval{position:absolute;left:0;right:0;top:7.4cqw;text-align:center;font-size:15cqw;line-height:1;color:#fff}
    .blb{position:absolute;top:19.2cqw;font-size:4.6cqw;line-height:1;color:#fff;transform:translateX(-50%)}
    .btxt{position:absolute;left:8cqw;right:8cqw;top:13cqw;text-align:center;font-size:5.6cqw;line-height:1.3;color:#fff}
    .bpm{position:absolute;top:32cqw;width:32.5cqw;height:8.6cqw;background:linear-gradient(#6a93d8,#5079c0);border:.3cqw solid #86a9e4;border-radius:.5cqw;cursor:pointer;box-sizing:border-box}
    .bpm i{position:absolute;left:50%;top:50%;width:5cqw;height:.8cqw;margin:-.4cqw 0 0 -2.5cqw;background:#e8f0ff}.bpm.pl i+i{width:.8cqw;height:5cqw;margin:-2.5cqw 0 0 -.4cqw}
    .bpm.sm{width:12cqw;height:8.2cqw}
    .cval{position:absolute;left:46cqw;font-size:9cqw;line-height:1;color:#fff}
    .mdi.on{color:#fff}.mdi.on ha-icon{filter:drop-shadow(0 0 .5cqw #fff)}.mdi .plq{text-decoration:none;font-size:2.8cqw;font-weight:700;background:#e3ecff;color:#3a5ba0;padding:.3cqw 1cqw;border-radius:.4cqw;line-height:1}
    .mdi sup{left:3.8cqw}
    /* PROGRAM */
    .plist{position:absolute;left:0;right:0;top:10.4cqw;bottom:0;padding:.4cqw 3cqw 0 3.4cqw}
    .prow{display:flex;align-items:center;height:6.4cqw;cursor:pointer;border-bottom:.25cqw solid #ffffff1c}.prow.td .pn{color:#19d3f7}
    .pn{width:8cqw;font-size:4.2cqw}.pbar{position:relative;flex:1;height:5.2cqw}.dbar{width:100%;height:100%;display:block}
    .pbl{position:absolute;bottom:-1.1cqw;font-size:1.7cqw;color:#c5d0ea;transform:translateX(-50%);display:none}
    .hc{position:absolute;width:7.2cqw;height:10.6cqw;box-sizing:border-box;border:.3cqw solid #6980b8;border-radius:.6cqw;background:#3d4e83;display:flex;align-items:flex-end;justify-content:center;cursor:pointer;padding-bottom:1cqw}
    .hc b{font-weight:400;font-size:3.6cqw;color:#dfe7fa}.hc.on{background:linear-gradient(#ff5a3c,#e0301f);border-color:#ff8a6e}.hc.on b{color:#fff}
    .pb{position:absolute;top:44.6cqw;height:8cqw;display:flex;align-items:center;justify-content:center;font-size:3.6cqw;white-space:nowrap;background:linear-gradient(#6a93d8,#5079c0);border:.3cqw solid #86a9e4;border-radius:.5cqw;cursor:pointer;box-sizing:border-box}
    /* live sub screens */
    .h2{position:absolute;left:0;right:0;top:0;height:9.8cqw;background:linear-gradient(#6e778f,#59627c);border-bottom:.3cqw solid #343c55;display:flex;align-items:center;justify-content:space-between;padding:0 3.2cqw 0 3.9cqw;font-size:4.4cqw}
    .h2 .bk{color:#19d3f7;cursor:pointer;min-width:20cqw}.h2 .tt{position:absolute;left:24cqw;right:24cqw;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .hi{display:flex;align-items:center;gap:2.4cqw;color:#e3e9f7}.hi ha-icon{--mdc-icon-size:5.4cqw}.hi span{cursor:pointer}.wr{display:flex;align-items:flex-start;color:#e3e9f7}.wr sup{font-size:2.2cqw}
    .s-water,.s-heat,.s-burn{background:linear-gradient(180deg,#5c6890,#3e4a74 70%)}
    .pos-tank{position:absolute;left:18.7cqw;top:12cqw;width:18.9cqw;height:35.4cqw}
    .bigv{position:absolute;left:36.3cqw;top:12.4cqw;width:36cqw;text-align:center;font-size:20.8cqw;color:#fff;line-height:1;cursor:pointer}
    .box{position:absolute;right:.2cqw;width:26.4cqw;box-sizing:border-box;background:linear-gradient(#4b5f95,#3d4e83);border:.3cqw solid #6980b8;border-radius:.6cqw;display:flex;align-items:center;justify-content:space-between;padding:0 3cqw 0 3.4cqw;cursor:pointer}
    .box.b1{top:14.6cqw;height:7.3cqw;padding-left:3.4cqw}.box.b1 b{font-size:7.9cqw;font-weight:400;color:#e8f0ff;line-height:1}.box.b2{top:23.9cqw;height:7.3cqw;padding:0}
    .mi{position:relative;display:inline-flex;color:#e8f0ff;margin-right:3.4cqw}.mi ha-icon{--mdc-icon-size:5cqw}.mi sup{position:absolute;right:-4.6cqw;top:-.4cqw;font-size:2.2cqw}.mi.lone{margin-left:auto;margin-right:3.4cqw}
    .sched{width:100%;height:100%;display:block}
    .brow{position:absolute;left:0;right:0;bottom:0;height:9.4cqw;display:grid;grid-template-columns:7.8% 8.3% 8.3% 8.3% 8.3% 8.6% 1fr;background:#51618f}
    .brow>div{border-left:.3cqw solid #7b8fc2;background:linear-gradient(#6676a3,#4a5a88);display:flex;align-items:center;justify-content:center;color:#e3ecff}
    .brow .c1{border-left:0}.brow .pmp{width:5.6cqw;height:5.6cqw}.brow ha-icon{--mdc-icon-size:5.8cqw}
    .brow .fanb{--mdc-icon-size:7cqw}.brow .cg{background:linear-gradient(#8aa0cf,#6e86b8);cursor:pointer}.brow .cg ha-icon{--mdc-icon-size:7.4cqw}
    .cot{position:absolute;left:4.6cqw;top:18.65cqw;font-size:8.05cqw;line-height:1;color:#fff;cursor:pointer;white-space:nowrap}.cot sup{font-size:5.9cqw;vertical-align:top;margin-left:.5cqw;position:relative;top:-.45cqw;line-height:1}
    .rad{position:absolute;left:16.7cqw;top:24.1cqw;width:30.2cqw;height:18.6cqw}
    .sw{position:absolute;left:53.8cqw;top:15.36cqw;width:12.6cqw}
    .box.mono{justify-content:flex-end}
    .bname{position:absolute;left:3.3cqw;top:11.4cqw;font-size:7.4cqw;line-height:1;color:#fff;width:48cqw;text-align:center}
    .burn{position:absolute;left:13.1cqw;top:18.9cqw;width:21.5cqw;height:auto;pointer-events:none}
    .stats{position:absolute;right:.5cqw;top:11.85cqw;font-size:4.3cqw;line-height:5.13cqw;text-align:center;color:#fff;width:46cqw}
    .mini span{position:absolute;top:42cqw;font-size:3.8cqw;line-height:1;color:#fff;transform:translateX(-50%);white-space:nowrap}.mini span:nth-child(1){left:3.9cqw}.mini span:nth-child(2){left:11.95cqw}.mini span:nth-child(3){left:36.85cqw}
    /* list pages */
    .is-sub{background:linear-gradient(180deg,#5c6890,#3b4670 70%)}
    .list{position:absolute;left:0;right:0;top:10cqw;bottom:0;overflow-y:auto;scrollbar-width:none;padding:0 2.8cqw 2cqw 2.4cqw}.list::-webkit-scrollbar{display:none}
    .row{display:flex;align-items:center;justify-content:space-between;min-height:11cqw;border-bottom:.3cqw solid #ffffff22;font-size:4.4cqw;padding:0 1.2cqw}
    .row .l{display:flex;align-items:center;gap:1.6cqw}.row .v{color:#fff;font-weight:300;white-space:nowrap}.row.go{cursor:pointer}.ch{color:#19d3f7;font-size:6cqw}.row .l.cy{color:#19d3f7}
    .row.red .l{color:#ff6b62}
    .tg{width:7.4cqw;height:3.8cqw;border-radius:1.9cqw;background:#3b4670;position:relative;box-shadow:inset 0 0 .6cqw #000}
    .tg i{position:absolute;left:.4cqw;top:.4cqw;width:3cqw;height:3cqw;border-radius:50%;background:radial-gradient(#fff,#a9b4d0)}
    .tg.on{background:#58b52b}.tg.on i{left:4cqw}
    .lamp{width:2.6cqw;height:2.6cqw;border-radius:50%;background:#2a3358;display:inline-block}.lamp.on{background:#86e61f;box-shadow:0 0 1cqw #86e61f}
    .abo em.cl{cursor:pointer}.abo em.dis{opacity:.4}.row.ro{opacity:.55}
    .pvl{position:absolute;inset:0;background:rgba(6,6,6,.92);pointer-events:none}
    .pdlg{position:absolute;left:4.23cqw;top:5.38cqw;width:91.35cqw;height:50.2cqw;box-sizing:border-box;border-radius:.8cqw;background:linear-gradient(#666,#404040);border:.26cqw solid #5e5e5e;box-shadow:0 .4cqw 1.2cqw #000a;color:#fff}
    .pdt{position:absolute;left:0;right:0;top:2.3cqw;text-align:center;font-size:5.4cqw;line-height:6cqw}
    .pbt{position:absolute;width:10.77cqw;height:7.5cqw;box-sizing:border-box;border:.26cqw solid #2c2c2c;border-radius:.8cqw;background:linear-gradient(#686868,#454545);box-shadow:inset 0 .26cqw 0 rgba(255,255,255,.22);cursor:pointer;display:flex;align-items:center;justify-content:center}
    .pbt i{position:absolute;left:50%;top:50%;width:5.1cqw;height:.8cqw;margin:-.4cqw 0 0 -2.55cqw;background:#d4d4d4}
    .pbt.pl i+i{width:.8cqw;height:5.1cqw;margin:-2.55cqw 0 0 -.4cqw}
    .pbt.pok{font-size:4.3cqw;color:#f2f2f2}
    .pdg{position:absolute;width:10.77cqw;top:19.6cqw;height:20cqw;line-height:20cqw;text-align:center;font-size:20cqw;font-weight:400;-webkit-text-stroke:.3cqw #fff;transform:scaleX(.74)}
    .abo{display:flex;gap:1.6cqw}.abo em{font-style:normal;display:flex;flex-direction:column;align-items:center}.abo small{font-size:2cqw;color:#e0e7f8}
    .abo b{width:6cqw;height:5.6cqw;border-radius:.8cqw;background:#3b4670;box-shadow:inset 0 0 .6cqw #000;display:flex;align-items:center;justify-content:center;color:#b5e61d;font-size:5.4cqw;font-weight:400}
    .net,.inf{padding:2cqw;font-size:3.8cqw}.net div{display:flex;justify-content:space-between;padding:2cqw 0;border-bottom:.3cqw solid #ffffff22}
    .gn{color:#86e61f}.rd{color:#ff6b62}.dim{color:#aab4d4;font-size:3.4cqw;padding:1.4cqw 0}.inf .rd{color:#ff6b62}.inf div{padding:1.2cqw 0}.big2{font-size:4.4cqw}
    @keyframes spin{to{transform:rotate(360deg)}}
    .brow .fan4{width:6.1cqw;height:6.1cqw}.fan4.spin{animation:spin .7s linear infinite}
    .ftk{position:absolute;left:12.4cqw;top:8.34cqw;width:25.6cqw;height:44.5cqw;background:linear-gradient(#f4b5b8,#f09aa2);border:.25cqw solid #e0453b;box-sizing:border-box;overflow:hidden}
    .fth{position:absolute;left:0;right:0;top:0;height:6.97cqw;background:linear-gradient(#f6604f,#e5352b);border-bottom:.3cqw solid #b8352c}.fhd{position:absolute;left:9.47cqw;top:2.7cqw;width:6.4cqw;height:3cqw}
    .fbar{position:absolute;left:9.7cqw;top:9.58cqw;width:6.06cqw;height:32.7cqw;background:#6c7898;border:.25cqw solid #e9edf8;box-sizing:border-box;display:flex;align-items:flex-end}
    .fbar i{display:block;width:100%;background:repeating-linear-gradient(45deg,#f3e24f 0 .5cqw,#e1c92f .5cqw 1cqw)}
    .fhn{position:absolute;left:12.67cqw;width:11.4cqw;height:.45cqw;background:#fff;margin-top:-.22cqw}.fhn::before{content:'';position:absolute;left:-.95cqw;top:-.72cqw;width:1.9cqw;height:1.9cqw;border-radius:50%;background:#fff}
    .fch{position:absolute;left:18.13cqw;width:4.55cqw;height:2.5cqw}.fe{position:absolute;left:6.4cqw;bottom:3.3cqw;font-size:4.2cqw;line-height:1;color:#f5a21a;font-weight:700}
    .ftt{position:absolute;left:45.55cqw;top:6.9cqw;font-size:5.4cqw;line-height:1;color:#fff}
    .fbt{position:absolute;display:flex;align-items:center;justify-content:center;color:#fff;font-size:7.5cqw;line-height:1;background:linear-gradient(#5b6a8a,#3e4a68);border:.3cqw solid #2c3550;border-radius:.8cqw;box-sizing:border-box}
    .fkg{position:absolute;left:47cqw;width:13.4cqw;text-align:center;top:25.6cqw;font-size:5.4cqw;line-height:1;color:#fff}
    .fau{left:47.2cqw;top:45.1cqw;width:11cqw;height:7.4cqw}.fau .aug{width:6.1cqw;height:2.9cqw}.fts{position:absolute;left:59.2cqw;top:46.2cqw;font-size:5.4cqw;line-height:1;color:#fff}
    .svsep{display:flex;align-items:center;gap:2cqw;color:#19d3f7;font-size:4cqw;line-height:1;padding:2.6cqw 0 1.4cqw;letter-spacing:.3cqw}.svsep::before,.svsep::after{content:'';flex:1;height:.3cqw;background:#19d3f7}
    .fmt{position:absolute;left:0;right:0;top:8.2cqw;text-align:center;font-size:5.2cqw;line-height:1;color:#fff}
    .fmb{position:absolute;left:9.98cqw;top:13.6cqw;width:71.7cqw;height:36.3cqw;background:#050505;box-sizing:border-box}.fmb svg{width:100%;height:100%;display:block}
    .fmp{position:absolute;width:3.6cqw;height:3.6cqw;margin:-1.8cqw 0 0 -1.8cqw;border-radius:50%;background:#050505;border:.45cqw solid #aebddb;cursor:pointer}
    .fmp.sel{background:radial-gradient(#8bf01f,#58b52b 70%);border-color:#e8ffd8;box-shadow:0 0 1.4cqw #8bf01f}
    .fmv{position:absolute;width:10cqw;margin-left:-5cqw;text-align:center;font-size:4.4cqw;line-height:1;color:#fff;cursor:pointer}.fmv.sel{color:#19d3f7}
    .fml{position:absolute;top:49.8cqw;width:10cqw;margin-left:-5cqw;text-align:center;font-size:4.2cqw;line-height:1;color:#fff;cursor:pointer}
    .fma{cursor:pointer}.fma.dis{opacity:.5}.fmc{width:5.4cqw;height:3.2cqw}
    .augw{position:relative;display:inline-block;line-height:0}.aug{width:6.2cqw;height:2.9cqw;overflow:visible}.augw sup{position:absolute;right:-.7cqw;top:-1.2cqw;font-size:2.1cqw;color:#fff;line-height:1}
    `;
  }
}
customElements.define('tekla-panel-card', TeklaPanelCard);   // silnik renderowania, nie pokazujemy w selektorze kart (zob. teklapelletcan-card.js)

/* ---------- edytor karty (wizualny konfigurator) ---------- */
class TeklaPanelCardEditor extends HTMLElement {
  setConfig(c) { this._cfg = c || {}; this._draw(); }
  set hass(h) { this._hass = h; if (this._form) this._form.hass = h; }
  _flat() {
    const d = { screen: this._cfg.screen || 'main' };
    const e = this._cfg.entities || {};
    for (const k of Object.keys(TEKLA_DEF)) d['e_' + k] = e[k] || '';
    return d;
  }
  _draw() {
    if (!this._form) {
      this._form = document.createElement('ha-form');
      this._form.computeLabel = s => s.label || s.name;
      this._form.addEventListener('value-changed', ev => this._changed(ev.detail.value));
      this.appendChild(this._form);
      const n = document.createElement('div');
      n.style.cssText = 'font-size:12px;opacity:.7;margin-top:8px';
      n.textContent = 'Pola możesz zostawić puste – wtedy dany element panelu pokaże „-".';
      this.appendChild(n);
      const box = document.createElement('div');
      box.style.cssText = 'display:flex;gap:8px;align-items:center;margin:12px 0 4px;flex-wrap:wrap';
      box.innerHTML = `<input id="pfx" placeholder="prefiks encji, np. tekla_" style="flex:1;min-width:140px;padding:8px;border-radius:6px;border:1px solid var(--divider-color,#888);background:var(--card-background-color,#fff);color:var(--primary-text-color,#000)">
        <button id="auto" style="padding:8px 14px;border-radius:6px;border:0;background:var(--primary-color,#03a9f4);color:var(--text-primary-color,#fff);cursor:pointer">Uzupełnij z prefiksu</button>
        <div id="autost" style="flex-basis:100%;font-size:12px;opacity:.8"></div>`;
      this.insertBefore(box, this._form);
      box.querySelector('#auto').addEventListener('click', () => this._auto(box.querySelector('#pfx').value.trim(), box.querySelector('#autost')));
    }
    if (!this._form.schema || !this._form.schema.length) {
      const schema = [{ name: 'screen', label: 'Ekran startowy', selector: { select: { mode: 'dropdown', options: SCREEN_OPTS.map(o => ({ value: o[0], label: o[1] })) } } }];
      for (const [title, fields] of ENT_GROUPS) {
        schema.push({
          type: 'expandable', title, flatten: true,
          schema: fields.map(f => ({ name: 'e_' + f[0], label: f[1], selector: { entity: { domain: f[2] } } })),
        });
      }
      this._form.schema = schema;
    }
    this._form.data = this._flat();
    if (this._hass) this._form.hass = this._hass;
  }
  _auto(prefix, out) {
    if (!this._hass) { out.textContent = 'Brak połączenia z HA.'; return; }
    const ids = Object.keys(this._hass.states), pf = prefix.toLowerCase();
    const cur = Object.assign({}, this._cfg.entities || {});
    let n = 0, miss = [];
    for (const [title, fields] of ENT_GROUPS) for (const f of fields) {
      const [k, label, doms] = f, key = ROLE_KEY[k];
      if (cur[k] || !key) continue;
      const re = new RegExp('(^|_)' + key + '(_\\d+)?$');
      const c = ids.filter(id => {
        const [d, o] = id.split('.');
        return doms.includes(d) && o.includes(pf) && re.test(o);
      }).sort((a, b) => a.length - b.length);
      if (c.length) { cur[k] = c[0]; n++; } else miss.push(label);
    }
    this._cfg = Object.assign({}, this._cfg, { entities: cur });
    this._form.data = this._flat();
    this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: this._cfg }, bubbles: true, composed: true }));
    out.textContent = `Dobrano ${n} encji (puste pola uzupełnione, wybrane wcześniej bez zmian).` + (miss.length ? ' Nie znaleziono: ' + miss.join(', ') + '.' : '');
  }
  _changed(v) {
    const entities = {};
    for (const k of Object.keys(TEKLA_DEF)) if (v['e_' + k]) entities[k] = v['e_' + k];
    const cfg = Object.assign({}, this._cfg, { screen: v.screen || 'main', entities });
    this._cfg = cfg;
    this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: cfg }, bubbles: true, composed: true }));
  }
}
customElements.define('tekla-panel-card-editor', TeklaPanelCardEditor);
