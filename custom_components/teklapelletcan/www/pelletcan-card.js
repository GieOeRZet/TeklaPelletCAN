/* PelletCAN-card - JEDEN plik wejsciowy karty Tekla/Estyma Igneo Touch (wersja karty: patrz CARD_VER nizej i version.json).
   Rejestruje karte custom:pelletcan-card (stary typ custom:tekla-panel-card dziala dalej; tryb lite: lite: true w konfiguracji karty; typ tekla-panel-card_lite = alias).
   Dziala tak: pobiera rdzen tekla-panel-card.js (z tego samego katalogu) (baza v6.9), naklada poprawki (lista EDITS) i dolacza moduly:
     poprawki ekranow (menu, PROGRAM, NASTAWY) | paski harmonogramu | poziomy dostepu z ESP + parametry palnika/CWU | Antylegionella | Ogrzewanie 1
     | czas podawania | historia alarmow z kotla | grafiki z folderu img/ | autor na ekranie INFO | v9.2: automatyczne wykrywanie encji, tryb lite (lite: true w YAML), nowy edytor.
   Zasob w HA: tylko ten plik. Po zmianie podbij ?v= w adresie zasobu i zrob Ctrl+F5. */
(async () => {
  if (window.__igneoCard) return;
  window.__igneoCard = true;
  try {
    if (customElements.get('tekla-panel-card')) {
      console.warn('tekla-panel-card v7.8: element juz zarejestrowany (stara wersja w pamieci strony) - zrob twarde odswiezenie (Ctrl+F5)');
      return;
    }
    const DIR = new URL('.', import.meta.url).pathname; // katalog tego pliku (HACS: /hacsfiles/PelletCAN/, recznie: /local/community/igneo-ha/)
    let code = await (await fetch(DIR + 'tekla-panel-card.js?v=62&_=' + Date.now())).text();
    const EDITS = [
{
"t": "x",
"old": "['feeder_run', 'Podajnik pracuje', B], ",
"new": "['feeder_run', 'Podajnik pracuje', B], ['feeder2_run', 'Podajnik palnika pracuje', B], "
},
{
"t": "x",
"old": "feeder_run: 'podajnik_pracuje',",
"new": "feeder_run: 'podajnik_pracuje', feeder2_run: 'podajnik_palnika_pracuje',"
},
{
"t": "x",
"old": "_brow(first, gear, second) {",
"new": "_brow(first, gear, second, third) {"
},
{
"t": "x",
"old": "<div class=\"c\">${second || ''}</div><div class=\"c\"></div><div class=\"c\"></div>",
"new": "<div class=\"c\">${second || ''}</div><div class=\"c\">${third || ''}</div><div class=\"c\"></div>"
},
{
"t": "x",
"old": "'burner_s', this._auger(1, this._on('feeder_run')))}",
"new": "'burner_s', this._auger(1, this._on('feeder_run')), this._auger(2, this._on('feeder2_run')))}"
},
{
"t": "x",
"old": "Y = v => isNaN(v) ? 32.1 : 32.1 - (v - 56) * 0.05;",
"new": "Y = v => isNaN(v) ? 46 : 46.02 - 0.2367 * v;"
},
{
"t": "x",
"old": "{ v: [1, 2, 3, 4, 5].map(i => this._v('fan_mod_' + i)), sel: -1 }",
"new": "{ v: [1, 2, 3, 4, 5].map(i => this._v('fan_mod_' + i)), v0: [1, 2, 3, 4, 5].map(i => this._v('fan_mod_' + i)), sel: -1 }"
},
{
"t": "x",
"old": "<div class=\"qok\" data-go=\"burner_s\" data-back=\"burn\" style=\"left:84.8cqw;top:45.8cqw",
"new": "<div class=\"qok\" data-act=\"fmok\" style=\"left:84.8cqw;top:45.8cqw"
},
{
"t": "x",
"old": "else if (act === 'pinp') this._pinStep",
"new": "else if (act === 'fmok') { const f = this._fm; if (f) f.v.forEach((v, i) => { if (!isNaN(v) && v !== f.v0[i]) this._svc('set_param', { key: 5 + i, value: v }); }); this._go('burner_s', 'burn'); }\n      else if (act === 'pedit' || act.startsWith('pr')) this._prAct(act, a, e);\n      else if (act === 'pinp') this._pinStep"
},
{
"t": "x",
"old": ".ban{position:absolute;right:30%;bottom:17%;width:3.4cqw;height:3.4cqw;border-radius:50%;background:#f0301f;box-shadow:0 0 0 .35cqw #fff3,0 0 1.2cqw #f0301f}.ban::after{content:'';position:absolute;left:18%;right:18%;top:42%;height:16%;background:#fff;border-radius:.3cqw}",
"new": ".ban{position:absolute;right:31%;bottom:21%;width:3.3cqw;height:2.6cqw;border-radius:.5cqw;background:linear-gradient(#ff5a4a,#d8281c);box-shadow:0 0 .8cqw rgba(240,48,31,.55)}.ban::before{content:'';position:absolute;left:20%;right:20%;top:-1.6cqw;height:1.9cqw;border:.5cqw solid #e5352b;border-bottom:0;border-radius:1.4cqw 1.4cqw 0 0;box-sizing:border-box}.ban::after{content:'';position:absolute;left:43%;width:14%;top:24%;height:38%;background:#7a1510;border-radius:.2cqw}"
},
{
"t": "x",
"old": "e('Korekta powietrza [%]', this._p(this._v('air_corr'), 0))",
"new": "this._prow('Korekta powietrza [%]', this._p(this._v('air_corr'), 0), 3)"
},
{
"t": "x",
"old": "e('Moc min [%]', this._p(this._v('power_min'), 0))",
"new": "this._prow('Moc min [%]', this._p(this._v('power_min'), 0), 0)"
},
{
"t": "x",
"old": "e('Moc max [%]', this._p(this._v('power_max'), 0))",
"new": "this._prow('Moc max [%]', this._p(this._v('power_max'), 0), 1)"
},
{
"t": "x",
"old": "e('Wartość opałowa [kWh/kg]', this._p(this._v('fuel_heat'), 1))",
"new": "this._prow('Wartość opałowa [kWh/kg]', this._p(this._v('fuel_heat'), 1), 2)"
},
{
"t": "x",
"old": "e('Ilość paliwa test [kg/h]', this._p(this._v('fuel_test'), 1))",
"new": "this._prow('Ilość paliwa test [kg/h]', this._p(this._v('fuel_test'), 1), 4)"
},
{
"t": "r",
"src": "\\] : \\[\\]\\)\\]\\);(\\s*)case 'level'",
"fl": "",
"new": "] : [])]) + (this._pr ? this._prDlg() : '');\n      case 'level'"
},
{
"t": "x",
"old": "this._scr = s; this._modal = false; this._pe = null;",
"new": "this._scr = s; this._modal = false; this._pe = null; this._pr = null;"
},
{
"t": "x",
"old": ".fma{cursor:pointer}",
"new": ".fma{cursor:pointer}.row[data-act]{cursor:pointer}"
},
{
"t": "r",
"src": "const MENU = \\[[\\s\\S]*?\\n\\];",
"fl": "",
"new": "const MENU = [\n  ['boiler', 'Kocioł', 'mdi:water-boiler'], ['burner_s', 'Palnik', 'mdi:fire'], ['co_s', 'Ogrzewanie obwód 1', 'mdi:radiator'], ['cwu_s', 'Ciepła woda użytkowa', 'mdi:faucet'],\n  ['alarm', 'Historia alarmów', 'mdi:clipboard-alert-outline'], ['info', 'Informacje o programie', 'mdi:information'],\n  ['stats', 'Statystyki', 'mdi:chart-box-outline'], ['test', 'Test wyjść', 'mdi:toggle-switch-outline'], ['net', 'Sieć', 'mdi:lan'], ['level', 'Poziom menu (PIN)', 'mdi:account-lock'],\n];"
},
{
"t": "x",
"old": "SERVICE = ['fanmod', 'test']",
"new": "SERVICE = ['fanmod', 'test', 'stats', 'net', 'conf']"
},
{
"t": "x",
"old": ".map(([k, n]) => `<div class=\"row go\" data-go=\"${k}\" data-back=\"menu\"><span class=\"l\">${n}</span><span class=\"v ch\">&rsaquo;</span></div>`)",
"new": ".map(([k, n, ic]) => `<div class=\"row go mi\" data-go=\"${k}\" data-back=\"menu\"><span class=\"l\"><ha-icon icon=\"${ic}\"></ha-icon>${n}</span>${k === 'level' ? '' : '<span class=\"v ch2\">&rsaquo;</span>'}</div>`)"
},
{
"t": "x",
"old": "burner_s: 'PALNIK – USTAWIENIA', co_s: 'OGRZEWANIE 1 – USTAWIENIA', cwu_s: 'WODA – USTAWIENIA',",
"new": "burner_s: 'NASTAWY', co_s: 'NASTAWY', cwu_s: 'NASTAWY',"
},
{
"t": "x",
"old": "const lab = back === 'menu' ? 'MENU' : back === 'main' ? 'EKRAN GŁ.' : 'WSTECZ';",
"new": "const PL = { boiler: 'KOCIOŁ', burner_s: 'PALNIK', co_s: 'OGRZEWANIE 1', cwu_s: 'WODA' }, lab = PL[this._scr] || (back === 'menu' ? 'MENU' : back === 'main' ? 'EKRAN GŁ.' : 'WSTECZ');"
},
{
"t": "x",
"old": "<span class=\"wr\"><ha-icon icon=\"mdi:wrench\"></ha-icon><sup>${sup}</sup></span>",
"new": "<span class=\"wr\">${this._unl() ? `<ha-icon icon=\"mdi:wrench\"></ha-icon><sup>${sup}</sup>` : '<ha-icon class=\"pp\" icon=\"mdi:account\"></ha-icon>'}</span>"
},
{
"t": "r",
"src": "case 'co_s': return P\\(TITLES\\.co_s, \\[[\\s\\S]*?(?=\\s*case 'stats': \\{)",
"fl": "",
"new": "case 'co_s': return P(TITLES.co_s, [\n        e('Temperatura komfortowa [°C]', this._p(this._v('co_comfort'), 1)), e('Temperatura ekonomiczna [°C]', this._p(this._v('co_eco'), 1)),\n        this._prow('Histereza [°C]', this._po(7), 7), this._prow('Kalibracja czujnika pok. [°C]', this._po(8), 8), this._prow('Tryb pracy', this._po(9), 9),\n        this._prow('Temperatura CO zadana ręcznie [°C]', this._po(10), 10), this._prow('Temperatura CO dla -20°C [°C]', this._po(11), 11), this._prow('Temperatura CO dla  0°C [°C]', this._po(12), 12), this._prow('Temperatura CO dla 10°C [°C]', this._po(13), 13)]) + (this._pr ? this._prDlg() : '');\n      case 'cwu_s': return P(TITLES.cwu_s, [\n        e('Temperatura komfortowa [°C]', this._p(this._v('cwu_comfort'), 0)), e('Temperatura ekonomiczna [°C]', this._p(this._v('cwu_eco'), 0)),\n        this._prow('Zagrzej teraz', this._po(14), 14), this._prow('Histereza [°C]', this._po(15), 15), e('Antylegionella', '-'), this._prow('Priorytet CWU', this._po(16), 16)]) + (this._pr ? this._prDlg() : '');"
},
{
"t": "x",
"old": ".row.red .l{color:#ff6b62}",
"new": ".row.red .l{color:#ff6b62}.mi ha-icon{--mdc-icon-size:6.4cqw;color:#e3e9f7;flex:none}.ch2{color:#fff;font-size:6cqw}"
},
{
"t": "r",
"src": "case 'boiler': return P\\(TITLES\\.boiler, \\[[\\s\\S]*?(?=\\s*case 'burner_s')",
"fl": "",
"new": "case 'boiler': return P(TITLES.boiler, [\n        e('Temperatura zadana [°C]', this._p(this._v('boiler_manual'), 0)), this._prow('Histereza załączenia [°C]', this._p(this._v('boiler_hyst_on'), 0), 5),\n        this._prow('Histereza wyłączenia [°C]', this._p(this._v('boiler_hyst_off'), 0), 6)]) + (this._pr ? this._prDlg() : '');"
},
{
"t": "x",
"old": "menu: 'MENU', boiler: 'KOCIOŁ',",
"new": "menu: 'MENU', boiler: 'NASTAWY',"
},
{
"t": "x",
"old": "['boiler', 'Kocioł', 'mdi:water-boiler']",
"new": "['kociol', 'Kocioł', 'mdi:water-boiler']"
},
{
"t": "x",
"old": "const back = ['boiler', 'stats', 'test', 'net', 'info', 'level'].includes(s)",
"new": "const back = ['kociol', 'stats', 'test', 'net', 'info', 'level'].includes(s)"
},
{
"t": "x",
"old": "    else html = this._body(this._scr);",
"new": "    else if (this._scr === 'kociol') html = this._kociol(ctx) + (this._modal === 'boiler' ? this._bDlg() : '');\n    else html = this._body(this._scr);"
},
{
"t": "x",
"old": "  stats: 'statystyki_kotla', mirror: 'tryb_mirror',",
"new": "  stats: 'statystyki_kotla', conf: 'konfiguracja_kotla', burn_ign: 'palnik_zapalarka', fuel_use: 'paliwo_zuzycie_24h', fuel_days: 'paliwo_prognoza', fuel_low: 'paliwo_rezerwa', mirror: 'tryb_mirror', ret_temp: 'temperatura_powrotu', boiler_pump_min: 'kociol_minimalna_temp_pomp', boiler_pump_run: 'kociol_wybieg_pompy', cwu_tmax: 'cwu_temperatura_maksymalna', boil_pwr: 'kociol_moc_palnika', boil_cons: 'kociol_zuzycie_paliwa', grate_t: 'kociol_czas_do_czyszczenia_rusztu', exh_pct: 'kociol_wentylator_spalin_moc', nominal_kw: 'kociol_moc_nominalna', predose_g: 'palnik_dawka_wstepna_g', egt_min: 'palnik_temp_spalin_min', egt_max: 'palnik_temp_spalin_max', exch_int: 'wymiennik_interwal_czyszczenia', exh_c1: 'wentylator_spalin_krzywa_1', exh_c2: 'wentylator_spalin_krzywa_2', exh_c3: 'wentylator_spalin_krzywa_3', exh_c4: 'wentylator_spalin_krzywa_4', exh_c5: 'wentylator_spalin_krzywa_5', alarm_snd: 'alarm_dzwiekowy', alarm_sil_from: 'alarm_cisza_od', alarm_sil_to: 'alarm_cisza_do', boiler_fuel_reserve: 'kociol_rezerwa_paliwa_stop', boiler_ret_min: 'kociol_minimalna_temp_powrotu', boiler_mixer_time: 'kociol_czas_mieszacza', co_room: 'co1_czujnik_pokojowy_0_brak_1_ctp1_2_ctp2_3_videroom_4_termostat_5_can', co_source: 'co1_zrodlo_0_kociol_1_bufor', co_co_sensor: 'co1_czujnik_co_0_1', co_const_pump: 'co1_stala_pompa_0_1', co_ret_protect: 'co1_obnizenie_tco_ochrona_powrotu_0_1', co_src_inc: 'co1_zwiekszenie_temp_zrodla', co_tmax: 'co1_temperatura_maksymalna', co_corr: 'co1_wspolczynnik_korekcji_t_co', co_out_comf: 'co1_max_tzew_pomp_komfort', co_out_eco: 'co1_max_tzew_pomp_ekon', co_lower: 'co1_obnizenie_temperatury_co', co_pump_min: 'co1_min_temperatura_co_pomp', co_mixer_time: 'co1_czas_mieszacza', mix_co1: 'mieszacz_co1_stan', mix_ret: 'mieszacz_powrotu_stan', boiler_hyst_on: 'histereza_zalaczenia_kotla', boiler_hyst_off: 'histereza_wylaczenia_kotla', co_hyst: 'co1_histereza', co_calib: 'co1_kalibracja_czujnika', co_mode_s: 'co1_tryb_pracy_0_reczny_1_pogodowy', co_cur_m20: 'co1_krzywa_pogodowa_20_c', co_cur_0: 'co1_krzywa_pogodowa_0_c', co_cur_10: 'co1_krzywa_pogodowa_10_c', cwu_hyst: 'cwu_histereza', cwu_src: 'cwu_zrodlo', cwu_src_inc: 'cwu_zwiekszenie_temp_zrodla', cwu_delta: 'cwu_delta_zalaczenia_pompy', cwu_boost: 'cwu_zagrzej_teraz_0_1', cwu_prio: 'cwu_priorytet_0_1',"
},
{
"t": "x",
"old": "['outside', 'Temperatura zewnętrzna', S]]],",
"new": "['outside', 'Temperatura zewnętrzna', S], ['ret_temp', 'Temperatura powrotu', S], ['mix_co1', 'Mieszacz CO1 stan (0 stoi, 1 zamyka, 2 otwiera)', S], ['mix_ret', 'Mieszacz powrotu stan (0 stoi, 1 zamyka, 2 otwiera)', S], ['boiler_hyst_on', 'Histereza załączenia kotła', S], ['boiler_hyst_off', 'Histereza wyłączenia kotła', S]]],\n  ['Ogrzewanie 1 – nastawy', [['co_hyst', 'CO1 histereza', S], ['co_calib', 'CO1 kalibracja czujnika', S], ['co_mode_s', 'CO1 tryb pracy (0 ręczny / 1 pogodowy)', S], ['co_cur_m20', 'CO1 krzywa pogodowa -20 °C', S], ['co_cur_0', 'CO1 krzywa pogodowa 0 °C', S], ['co_cur_10', 'CO1 krzywa pogodowa +10 °C', S]]],\n  ['Woda – nastawy', [['cwu_hyst', 'CWU histereza', S], ['cwu_src', 'CWU źródło (0 kocioł, 1 bufor)', S], ['cwu_src_inc', 'CWU zwiększenie temp. źródła', S], ['cwu_delta', 'CWU delta załączenia pompy', S], ['cwu_boost', 'CWU zagrzej teraz (0/1)', S], ['cwu_prio', 'CWU priorytet (0/1)', S]]],"
},
{
"t": "x",
"old": "['Średnia moc palnika z 50 godzin [%]', '-']",
"new": "['Średnia moc palnika z 50 godzin [%]', n(8)]"
},
{
"t": "x",
"old": "['Średni tlen dla mocy 30% [%]', '-']",
"new": "['Średni tlen dla mocy 30% [%]', nz(9)]"
},
{
"t": "x",
"old": "['Średni tlen dla mocy 50% [%]', '-']",
"new": "['Średni tlen dla mocy 50% [%]', nz(10)]"
},
{
"t": "x",
"old": "['Średni tlen dla mocy 70% [%]', '-']",
"new": "['Średni tlen dla mocy 70% [%]', nz(11)]"
},
{
"t": "x",
"old": "['Średni tlen dla mocy 90% [%]', '-']",
"new": "['Średni tlen dla mocy 90% [%]', nz(12)]"
},
{
"t": "x",
"old": "['fan_pct', 'Dmuchawa [%]', S], ",
"new": "['fan_pct', 'Dmuchawa [%]', S], ['burn_ign', 'Palnik zapalarka [%]', S], "
},
{
"t": "x",
"old": "['stats', 'Statystyki'], ['boiler', 'Kocioł – ustawienia']",
"new": "['stats', 'Statystyki'], ['kociol', 'Kocioł'], ['boiler', 'Kocioł – ustawienia']"
},
{
"t": "x",
"old": ".fma{cursor:pointer}",
"new": ".fma{cursor:pointer}.rt{position:absolute;left:30.5cqw;width:46cqw;top:29.5cqw;text-align:center;font-size:5.8cqw;line-height:1;color:#eef3ff}.brow .c1 .bk{width:100%;height:100%;display:flex;align-items:center;justify-content:center;cursor:pointer}.brow .c1 .bk ha-icon{--mdc-icon-size:6.6cqw;color:#e3e9f7}"
},
{
"t": "x",
"old": ".fma{cursor:pointer}",
"new": ".fma{cursor:pointer}.po{position:absolute;left:9cqw;right:9cqw;top:15.5cqw}.opt{padding:2cqw 0;margin-bottom:2cqw;border:.35cqw solid #5b6a8f;border-radius:1cqw;text-align:center;font-size:5cqw;color:#e8eefc;cursor:pointer}.opt.on{background:#f3f7ff;border-color:#f3f7ff;color:#1a3d8f;font-weight:600}"
},
{
"t": "x",
"old": ".fma{cursor:pointer}",
"new": ".fma{cursor:pointer}.hi{gap:.5cqw;margin-right:-.8cqw}.hi>ha-icon:not(.cy),.hi .pp{--mdc-icon-size:7.3cqw;color:#fff}.hi .cy{--mdc-icon-size:7.4cqw;transform:translateY(.9cqw)}"
},
{
"t": "x",
"old": ".fma{cursor:pointer}",
"new": ".fma{cursor:pointer}.row .tgq{position:relative;display:inline-block;vertical-align:middle;left:auto;top:auto;width:11.5cqw;height:5cqw;border-radius:2.5cqw}.row .tgq i{top:.55cqw;width:3.9cqw;height:3.9cqw}.row .tgq.on i{right:.55cqw}.row .tgq:not(.on) i{left:.55cqw}.row .tgq.on::before{left:2.3cqw;top:.55cqw;font-size:3.6cqw;line-height:3.9cqw}.row .tgq:not(.on)::after{content:'';position:absolute;right:1.7cqw;top:1.4cqw;width:2.2cqw;height:2.2cqw;border:.4cqw solid #e3e9f7;border-radius:50%;box-sizing:border-box}"
},
{
"t": "x",
"old": ".fma{cursor:pointer}",
"new": ".fma{cursor:pointer}.plist{overflow-y:auto;scrollbar-width:none;padding:.6cqw 0 0 0!important}.plist::-webkit-scrollbar{display:none}.prow{height:11.3cqw!important;border-bottom:0!important;flex:none!important;align-items:flex-start!important}.prow.td .pn{color:#cfe0ff!important}.pn{width:13.7cqw!important;font-size:5.6cqw!important;font-weight:700;color:#cfe0ff;padding-left:3.6cqw;box-sizing:border-box;margin-top:.2cqw}.pbar{flex:none!important;width:74.7cqw;height:5cqw!important;margin-top:.7cqw}.pbl{display:block!important;bottom:auto!important;top:5.2cqw;font-size:4.2cqw!important;font-weight:700;color:#e3ecff}"
},
{
"t": "r",
"src": "icon=\\\\?\"mdi:home\\\\?\"",
"fl": "g",
"new": "icon=\"mdi:home-variant\""
},
{
"t": "x",
"old": ".pos-tank{position:absolute;left:18.7cqw;top:12cqw;width:18.9cqw;height:35.4cqw}",
"new": ".pos-tank{position:absolute;left:18.7cqw;top:12cqw;width:18.9cqw;height:35.4cqw;object-fit:contain}"
},
{
"t": "x",
"old": "class TeklaPanelCard extends HTMLElement {",
"new": "window.__teklaDefs = { ENT_GROUPS, ROLE_KEY, SCREEN_OPTS };\nclass TeklaPanelCard extends HTMLElement {"
},
{
"t": "x",
"old": "customElements.define('tekla-panel-card', TeklaPanelCard);",
"new": "if (!customElements.get('tekla-panel-card')) customElements.define('tekla-panel-card', TeklaPanelCard);"
},
{
"t": "x",
"old": "['stats', 'Statystyki kotła (jeden sensor tekstowy: 8 liczb)', S]]],",
"new": "['stats', 'Statystyki kotła (jeden sensor tekstowy: 8 liczb)', S], ['fuel_use', 'Paliwo – zużycie 24 h [kg/dobę]', S], ['fuel_days', 'Paliwo – prognoza [dni]', S], ['fuel_low', 'Paliwo – rezerwa (alarm)', B]]],"
},
{
"t": "x",
"old": "['Liczba zaników zasilania', n(7)]].map",
"new": "['Liczba zaników zasilania', n(7)], ['Energia całkowita [kWh]', nz(13)], ['Zużycie paliwa 24 h [kg]', fx(this._v('fuel_use'))], ['Paliwo wystarczy na [dni]', fx(this._v('fuel_days'))], ['Moc palnika z kotła [kW]', this._p(this._v('boil_pwr'), 1)], ['Zużycie paliwa z kotła [kg/h]', this._p(this._v('boil_cons'), 1)], ['Czas do czyszczenia rusztu [min]', this._p(this._v('grate_t'), 0)], ['Wentylator spalin [%]', this._p(this._v('exh_pct'), 0)]].map"
},
{
"t": "x",
"old": "        const sv = this._t('stats', '').trim().split(/\\s+/)",
"new": "        const nz = i => (/^[1-9]\\d*$/.test(sv[i] || '') ? sv[i] : '-'), fx = v => (v == null || isNaN(v) ? '-' : Number(v).toFixed(1)), sv = this._t('stats', '').trim().split(/\\s+/)"
},
{
"t": "x",
"old": "customElements.define('tekla-panel-card-editor', TeklaPanelCardEditor);",
"new": "if (!customElements.get('tekla-panel-card-editor')) customElements.define('tekla-panel-card-editor', TeklaPanelCardEditor);"
}
];
    EDITS.forEach(e => {
      if (e.t === 'x') { if (code.split(e.old).length !== 2) console.error('tekla-panel-card v7.8: nie znaleziono wzorca', e.old.slice(0, 60)); else code = code.replace(e.old, () => e.new); }
      else { const re = new RegExp(e.src, e.fl); if (!re.test(code)) console.error('tekla-panel-card v7.8: nie znaleziono wzorca', e.src.slice(0, 60)); else { re.lastIndex = 0; code = code.replace(re, () => e.new); } }
    });
    const s = document.createElement('script');
    s.text = '(() => {\n' + code + '\n})();\n//# sourceURL=tekla-panel-card-v78.js';
    document.head.appendChild(s);

    const C = customElements.get('tekla-panel-card');
    if (!C) { console.error('pelletcan-card: brak elementu po zaladowaniu'); return; }
    // key -> { tytul, rola encji, min, max, krok, miejsca po przecinku }
    const PR = [
      { t: 'Moc min [%]', r: 'power_min', lo: 30, hi: 100, st: 1, dc: 0 },
      { t: 'Moc max [%]', r: 'power_max', lo: 30, hi: 100, st: 1, dc: 0 },
      { t: 'Wartość opałowa [kWh/kg]', r: 'fuel_heat', lo: 2, hi: 10, st: 0.1, dc: 1 },
      { t: 'Korekta powietrza [%]', r: 'air_corr', lo: -10, hi: 40, st: 1, dc: 0 },
      { t: 'Ilość paliwa test [kg/h]', r: 'fuel_test', lo: 5, hi: 100, st: 0.1, dc: 1 },
      { t: 'Histereza załączenia [°C]', r: 'boiler_hyst_on', lo: 0, hi: 20, st: 1, dc: 0, sk: 10 },
      { t: 'Histereza wyłączenia [°C]', r: 'boiler_hyst_off', lo: 0, hi: 20, st: 1, dc: 0, sk: 11 },
      { t: 'Histereza [°C]', r: 'co_hyst', lo: 0, hi: 5, st: 0.1, dc: 1, sk: 12 },
      { t: 'Kalibracja czujnika pok. [°C]', r: 'co_calib', lo: -3, hi: 3, st: 0.1, dc: 1, sk: 13 },
      { t: 'Tryb pracy', r: 'co_mode_s', opts: ['Ręczny', 'Pogodowy'], sk: 14 },
      { t: 'Temperatura CO zadana ręcznie [°C]', r: 'co_manual', lo: 20, hi: 80, st: 1, dc: 0, sk: 15 },
      { t: 'Temperatura CO dla -20°C [°C]', r: 'co_cur_m20', lo: 20, hi: 80, st: 1, dc: 0, sk: 16 },
      { t: 'Temperatura CO dla 0°C [°C]', r: 'co_cur_0', lo: 20, hi: 80, st: 1, dc: 0, sk: 17 },
      { t: 'Temperatura CO dla 10°C [°C]', r: 'co_cur_10', lo: 20, hi: 80, st: 1, dc: 0, sk: 18 },
      { t: 'Zagrzej teraz', r: 'cwu_boost', opts: ['Wyłączone', 'Włączone'], sk: 20, tog: true },
      { t: 'Histereza [°C]', r: 'cwu_hyst', lo: 0, hi: 20, st: 1, dc: 0, sk: 19 },
      { t: 'Priorytet CWU', r: 'cwu_prio', opts: ['Wyłączony', 'Włączony'], sk: 21, tog: true },
      { t: 'Źródło', r: 'cwu_src', opts: ['Kocioł', 'Bufor'], sk: 44 },
      { t: 'Zwiększenie temperatury źródła [°C]', r: 'cwu_src_inc', lo: 5, hi: 20, st: 1, dc: 0, sk: 45 },
      { t: 'Delta załączenia pompy [°C]', r: 'cwu_delta', lo: 2, hi: 20, st: 1, dc: 0, sk: 46 },
      { t: 'Minimalna temp. pomp [°C]', r: 'boiler_pump_min', lo: 20, hi: 70, st: 1, dc: 0, sk: 48 },
      { t: 'Minimalna temp. powrotu [°C]', r: 'boiler_ret_min', lo: 35, hi: 75, st: 1, dc: 0, sk: 49 },
      { t: 'Czas mieszacza [s]', r: 'boiler_mixer_time', lo: 60, hi: 360, st: 1, dc: 0, sk: 50 },
      { t: 'Zwiększenie temperatury źródła [°C]', r: 'co_src_inc', lo: 0, hi: 30, st: 1, dc: 0, sk: 51 },
      { t: 'Temp. maksymalna [°C]', r: 'co_tmax', lo: 30, hi: 80, st: 1, dc: 0, sk: 52 },
      { t: 'Wsp. korekcji t. CO [°C/°C]', r: 'co_corr', lo: 0, hi: 20, st: 1, dc: 0, sk: 53 },
      { t: 'MAX Tzew pomp komf. [°C]', r: 'co_out_comf', lo: 0, hi: 30, st: 1, dc: 0, sk: 54 },
      { t: 'MAX Tzew pomp ekon. [°C]', r: 'co_out_eco', lo: 0, hi: 30, st: 1, dc: 0, sk: 55 },
      { t: 'Obniżenie temperatury CO [°C]', r: 'co_lower', lo: 0, hi: 40, st: 1, dc: 0, sk: 56 },
      { t: 'MIN temperatura CO pomp [°C]', r: 'co_pump_min', lo: 20, hi: 60, st: 1, dc: 0, sk: 57 },
      { t: 'Czas mieszacza [s]', r: 'co_mixer_time', lo: 60, hi: 360, st: 1, dc: 0, sk: 58 },
      { t: 'Stała pompa', r: 'co_const_pump', opts: ['Wyłączona', 'Włączona'], sk: 59, tog: true },
      { t: 'Obniżenie Tco dla ochrony powrotu', r: 'co_ret_protect', opts: ['Wyłączone', 'Włączone'], sk: 60, tog: true },
      { t: 'Źródło', r: 'co_source', opts: ['Kocioł', 'Bufor'], sk: 61 },
      { t: 'Czujnik CO', r: 'co_co_sensor', opts: ['Wyłączony', 'Włączony'], sk: 62, tog: true },
      { t: 'Czujnik pokojowy', r: 'co_room', opts: ['brak', 'CTP1', 'CTP2', 'videROOM', 'termostat', 'CAN'], sk: 63 },
      { t: 'Wybieg pompy [min]', r: 'boiler_pump_run', lo: 0, hi: 120, st: 1, dc: 0, sk: 64 },
      { t: 'Rezerwa paliwa stop [kg]', r: 'boiler_fuel_reserve', lo: 0, hi: 100, st: 1, dc: 0, sk: 65 },
      { t: 'Temp. maksymalna [°C]', r: 'cwu_tmax', lo: 40, hi: 80, st: 1, dc: 0, sk: 66 },   // 38
      { t: 'Wentylator spalin – krzywa 1 [%]', r: 'exh_c1', lo: 0, hi: 100, st: 1, dc: 0, sk: 68 },   // 39..43
      { t: 'Wentylator spalin – krzywa 2 [%]', r: 'exh_c2', lo: 0, hi: 100, st: 1, dc: 0, sk: 69 },
      { t: 'Wentylator spalin – krzywa 3 [%]', r: 'exh_c3', lo: 0, hi: 100, st: 1, dc: 0, sk: 70 },
      { t: 'Wentylator spalin – krzywa 4 [%]', r: 'exh_c4', lo: 0, hi: 100, st: 1, dc: 0, sk: 71 },
      { t: 'Wentylator spalin – krzywa 5 [%]', r: 'exh_c5', lo: 0, hi: 100, st: 1, dc: 0, sk: 72 },
      { t: 'Alarm dźwiękowy', r: 'alarm_snd', opts: ['Wyłączony', 'Włączony'], sk: 73, tog: true },   // 44
      { t: 'Cisza od [h]', r: 'alarm_sil_from', lo: 0, hi: 24, st: 1, dc: 0, sk: 74 },   // 45
      { t: 'Cisza do [h]', r: 'alarm_sil_to', lo: 0, hi: 24, st: 1, dc: 0, sk: 75 },   // 46
      { t: 'Moc nominalna [kW]', r: 'nominal_kw', lo: 4, hi: 200, st: 1, dc: 0, sk: 76 },   // 47..51 (klucz 1, moc nominalna klucz 2)
      { t: 'Dawka wstępna [g]', r: 'predose_g', lo: 0, hi: 500, st: 10, dc: 0, sk: 77 },
      { t: 'Min. temp. spalin [°C]', r: 'egt_min', lo: 70, hi: 120, st: 1, dc: 0, sk: 78 },
      { t: 'Max. temp. spalin [°C]', r: 'egt_max', lo: 180, hi: 280, st: 1, dc: 0, sk: 79 },
      { t: 'Interwał czyszczenia wymiennika [min]', r: 'exch_int', lo: 10, hi: 600, st: 10, dc: 0, sk: 80 },
    ];
    C.prototype._po = function (k) {
      const c = PR[k], v = this._v(c.r);
      if (isNaN(v)) return '-';
      if (c.tog) return '<span class="tgq' + (v >= 1 ? ' on' : '') + '"><i></i></span>';
      return c.opts ? (c.opts[Math.round(v)] != null ? c.opts[Math.round(v)] : '-') : v.toFixed(c.dc);
    };

    // ekran PROGRAM jak na panelu: naglowek z postacia, slupki pomaranczowe, os z cyframi
    C.prototype._progHdr = function (title, edit) {
      const lab = edit ? 'PROGRAM' : ['WODA', 'OGRZEWANIE 1', 'KOCIOŁ'][(this._prog || {}).kind != null ? this._prog.kind : 2];
      return `<div class="h2"><span class="bk" ${edit ? 'data-act="pcancel"' : `data-go="${this._backTo || 'main'}"`}>&lsaquo; ${lab}</span><span class="tt">${title}</span>
        <span class="hi">${this._unl() ? '<span class="wr"><ha-icon icon="mdi:wrench"></ha-icon><sup>1</sup></span>' : '<ha-icon class="pp" icon="mdi:account"></ha-icon>'}<span data-go="main"><ha-icon class="cy" icon="mdi:home-variant"></ha-icon></span></span></div>`;
    };
    C.prototype._dayBar = function (bits) {
      if (bits == null) return '<svg viewBox="0 0 240 24" preserveAspectRatio="none" class="dbar"><text x="120" y="17" text-anchor="middle" font-size="14" fill="#9fb0d8">--</text></svg>';
      let r = '', t = '';
      (this._bands(bits) || []).forEach(([a, b]) => { r += `<rect x="${a * 10}" y="0.5" width="${(b - a) * 10}" height="14.2" fill="#e8601c"/>`; });
      for (let h = 0; h <= 24; h++) t += `<line x1="${h * 10}" y1="16.4" x2="${h * 10}" y2="${h % 6 === 0 ? 22 : 19.5}" stroke="#dfe8ff" stroke-width="${h % 6 === 0 ? 1.8 : 1}"/>`;
      return `<svg viewBox="0 0 240 24" preserveAspectRatio="none" class="dbar"><rect x="0" y="14.6" width="240" height="1.5" fill="#ff3a2c"/>${r}${t}</svg>`;
    };
    // podglad pojedynczych ekranow PROGRAM w osobnej karcie: screen: prog_0 (woda) / prog_1 (CO) / prog_2 (kociol)
    const _sc = C.prototype.setConfig;
    C.prototype.setConfig = function (c) {
      _sc.call(this, c);
      const m = /^prog_([012])$/.exec((c && c.screen) || '');
      if (m) { this._prog = { kind: +m[1] }; this._scr = 'prog'; this._backTo = ['water', 'heat', 'kociol'][+m[1]]; }
    };

    const VALVE = '<svg viewBox="0 0 24 24" style="width:6.6cqw;height:6.6cqw"><path d="M2.5 9.5L11.5 14.5L2.5 19.5Z M21.5 9.5L12.5 14.5L21.5 19.5Z" fill="#e3e9f7"/><path d="M7 6.5Q12 3 17 6.5" stroke="#8fd6ff" stroke-width="1.7" fill="none" stroke-linecap="round"/><path d="M5.8 4.2L6.9 7.4L9.6 6" fill="#8fd6ff"/></svg>';
    C.prototype._valve = function (mv) { return mv === 1 ? VALVE : mv === 2 ? '<span style="display:inline-block;transform:scaleX(-1)">' + VALVE + '</span>' : ''; };
    C.prototype._kociol = function (ctx) {
      const bm = ctx.bm, rt = this._v('ret_temp');
      // ikona zaworu (jak na panelu): pojawia sie, gdy mieszacz pracuje; 1 = zamyka (strzalka w lewo), 2 = otwiera (w prawo)
      const mx = this._v('mix_co1') || 0, mr = this._v('mix_ret') || 0, mv = mx > 0 ? mx : mr;
      return `${this._hdr('KOCIOŁ', 'menu')}
        ${this._boilerMain(ctx.burning).replace('class="boil"', 'class="boil" style="top:14.6cqw;left:8cqw"')}
        <div class="big" data-act="more" data-e="boiler_temp" style="top:16cqw;font-size:20cqw">${this._p(this._v('boiler_temp'))}</div>
        <div class="rt" style="top:38cqw;font-size:4.7cqw">T. powrotu=${isNaN(rt) ? '-' : rt.toFixed(1)}</div>
        <div class="tag" data-act="bdlg"><b>${isNaN(this._v('boiler_set')) ? '-' : Math.round(this._v('boiler_set'))}</b>${this._chipHtml(bm)}</div>
        ${bm < 2 ? `<div class="tbar" data-act="prog" data-kind="2" data-back="kociol" style="top:23.8cqw">${this._sched(this._todayBands(2, []))}</div>` : ''}
        ${this._brow('<div class="bk" data-go="menu"><ha-icon icon="mdi:arrow-left-circle-outline"></ha-icon></div>', 'boiler', '', this._valve(mv))}`;
    };
    const q = (v, c) => Number(Math.max(c.lo, Math.min(c.hi, Math.round(v / c.st) * c.st)).toFixed(c.dc));
    C.prototype._prow = function (label, val, k) {
      return `<div class="row" data-act="pedit" data-k="${k}"><span class="l">${label}</span><span class="v">${val}</span></div>`;
    };
    C.prototype._prDlg = function () {
      const d = this._pr, c = PR[d.k], f = x => x.toFixed(c.dc);
      if (c.opts) return `<div class="qd"><div class="qx" data-act="prcancel"></div><div class="qbg"></div>
        <span class="fmt" style="top:7.6cqw;font-size:4.2cqw">${c.t}</span>
        <div class="po">${c.opts.map((n, i) => `<div class="opt${i === d.val ? ' on' : ''}" data-act="propt" data-i="${i}">${n}</div>`).join('')}</div>
        <div class="qok" data-act="prok">OK</div></div>`;
      const p = (d.val - c.lo) / (c.hi - c.lo);
      return `<div class="qd"><div class="qx" data-act="prcancel"></div><div class="qbg"></div>
        <span class="fmt" style="top:7.6cqw;font-size:4.2cqw">${c.t}</span>
        <div class="bval" style="top:12.4cqw;font-size:10.5cqw">${f(d.val)}</div>
        <span class="blb" style="left:17cqw">${f(c.lo)}</span><span class="blb" style="left:79cqw">${f(c.hi)}</span>
        ${this._sl('data-act="prslide"', 17, 27, 66, p)}
        <div class="bpm" data-act="prval" data-d="-1" style="left:17cqw"><i></i></div><div class="bpm pl" data-act="prval" data-d="1" style="left:50.5cqw"><i></i><i></i></div>
        <div class="qok" data-act="prok">OK</div></div>`;
    };
    C.prototype._prAct = function (act, a, e) {
      if (this._mirror()) return;
      if (act === 'pedit') {
        const k = +a.dataset.k, c = PR[k], v = this._v(c.r);
        if (c.tog) { if (!isNaN(v)) this._svc('set_param', { key: c.sk, value: v >= 1 ? 0 : 1 }); return; }
        const val = c.opts ? (isNaN(v) ? -1 : Math.round(v)) : (isNaN(v) ? c.lo : q(v, c));
        this._pr = { k, val, v0: isNaN(v) ? NaN : val };
      } else if (!this._pr) return;
      else if (act === 'prcancel') this._pr = null;
      else if (act === 'propt') this._pr.val = +a.dataset.i;
      else if (act === 'prval') { const c = PR[this._pr.k]; this._pr.val = q(this._pr.val + (+a.dataset.d) * c.st, c); }
      else if (act === 'prslide') { const c = PR[this._pr.k]; this._pr.val = q(c.lo + this._slFrac(a, e) * (c.hi - c.lo), c); }
      else if (act === 'prok') {
        const d = this._pr, c = PR[d.k];
        if (d.val !== d.v0) {
          let v = d.val;
          if (d.k === 1 && v < this._v('power_min')) v = this._v('power_min');
          if (d.k === 0 && v > this._v('power_max')) v = this._v('power_max');
          this._svc('set_param', { key: c.sk != null ? c.sk : d.k, value: Number(v.toFixed(c.dc)) });
        }
        this._pr = null;
      }
      this._render(true);
    };

    // ---- modul: paski harmonogramu ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    const o = C.prototype._kociol;
    C.prototype._kociol = function (ctx) {
      let h = o.call(this, ctx);
      if (h.indexOf('data-back="kociol"') < 0) {
        const t = `<div class="tbar" data-act="prog" data-kind="2" data-back="kociol" style="top:23.8cqw">${this._sched(this._todayBands(2, []))}</div>`;
        const i = h.indexOf('<div class="brow"');
        h = i < 0 ? h + t : h.slice(0, i) + t + h.slice(i);
      }
      return h;
    };

    })();

    // ---- modul: poziomy dostepu, menu wg poziomu, nastawy palnika/CWU ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v80) return;
    C.prototype.__v80 = true;

    const W = window.__tekla80 = window.__tekla80 || { t: Date.now(), init: false, card: null };
    const LOCK_MS = 300000;
    // rola -> koncowka entity_id (po nazwach z ESPHome)
    const NEW = {
      burn_kw: 'palnik_moc', burn_kgh: 'palnik_spalanie', burn_bright: 'palnik_jasnosc_plomienia', feeder: 'palnik_czas_podawania_paliwa',
      acc: 'poziom_dostepu', legion: 'cwu_antylegionella', fw_ver: 'wersja_firmware',
      p_prefeed: 'palnik_wstepna_dawka_paliwa', p_feed_max: 'palnik_podawanie_max', p_photo: 'palnik_prog_foto',
      p_blow_ign: 'palnik_moc_dmuchawy_rozpalanie', p_blow_glow: 'palnik_moc_dmuchawy_rozzarzanie', p_blow_stop: 'palnik_moc_dmuchawy_wygaszanie',
      p_glow_time: 'palnik_czas_rozzarzania', p_glow_fuel: 'palnik_rozzarzanie_paliwo', p_stop_time: 'palnik_czas_wygaszania', p_lambda: 'palnik_sterowanie_lambda',
      p_o2_30: 'palnik_tlen_dla_mocy_30', p_o2_100: 'palnik_tlen_dla_mocy_100', p_cleans: 'palnik_liczba_czyszczen_rusztu', p_clean_gap: 'palnik_odstep_czyszczenia',
      p_pause_time: 'palnik_czas_pauzy', p_pause_power: 'palnik_moc_w_pauzie', p_pause_blow: 'palnik_dmuchawa_w_pauzie',
      p_inertia: 'palnik_bezwladnosc', p_grate_time: 'palnik_czas_ruchu_rusztu', p_burner_feed: 'palnik_podawanie_palnika_podajnika_zasobnika',
      p_feeder_period: 'palnik_okres_podajnika_zasobnika', p_min_rpm: 'palnik_minimalne_obroty_dmuchawy',
    };
    W.NEW = NEW;
    // parametry menu palnika i CWU: k = klucz set_param, lv = poziom (0/1/2)
    const PR2 = [
      { k: 22, t: 'Wstępna dawka paliwa [s]', r: 'p_prefeed', lo: 0, hi: 200, st: 1, dc: 0, lv: 1 },
      { k: 23, t: 'Podawanie max [s]', r: 'p_feed_max', lo: 1, hi: 15, st: 0.1, dc: 1, lv: 1 },
      { k: 24, t: 'Próg foto', r: 'p_photo', lo: 5, hi: 100, st: 1, dc: 0, lv: 1 },
      { k: 25, t: 'Moc dmuchawy rozpalanie [%]', r: 'p_blow_ign', lo: 0, hi: 100, st: 1, dc: 0, lv: 1 },
      { k: 26, t: 'Moc dmuchawy rozżarzanie [%]', r: 'p_blow_glow', lo: 0, hi: 100, st: 1, dc: 0, lv: 1 },
      { k: 27, t: 'Moc dmuchawy wygaszanie [%]', r: 'p_blow_stop', lo: 0, hi: 100, st: 1, dc: 0, lv: 1 },
      { k: 28, t: 'Czas rozżarzania [min]', r: 'p_glow_time', lo: 0, hi: 20, st: 1, dc: 0, lv: 1 },
      { k: 29, t: 'Rozżarzanie paliwo [%]', r: 'p_glow_fuel', lo: 20, hi: 100, st: 1, dc: 0, lv: 1 },
      { k: 30, t: 'Czas wygaszania [min]', r: 'p_stop_time', lo: 1, hi: 15, st: 1, dc: 0, lv: 1 },
      { k: 31, t: 'Sterowanie Lambda', r: 'p_lambda', tog: true, lv: 1 },
      { k: 32, t: 'Tlen dla mocy 30 % [%]', r: 'p_o2_30', lo: 5, hi: 15, st: 0.1, dc: 1, lv: 1 },
      { k: 33, t: 'Tlen dla mocy 100 % [%]', r: 'p_o2_100', lo: 5, hi: 15, st: 0.1, dc: 1, lv: 1 },
      { k: 34, t: 'Liczba czyszczeń', r: 'p_cleans', lo: 0, hi: 10, st: 1, dc: 0, lv: 1 },
      { k: 35, t: 'Odstęp czyszczenia [h]', r: 'p_clean_gap', lo: 1, hi: 12, st: 1, dc: 0, lv: 1 },
      { k: 36, t: 'Czas pauzy [min]', r: 'p_pause_time', lo: 0, hi: 60, st: 1, dc: 0, lv: 1 },
      { k: 37, t: 'Moc w pauzie [%]', r: 'p_pause_power', lo: 5, hi: 30, st: 1, dc: 0, lv: 1 },
      { k: 38, t: 'Dmuchawa w pauzie [%]', r: 'p_pause_blow', lo: 10, hi: 50, st: 1, dc: 0, lv: 1 },
      { k: 39, t: 'Bezwładność palnika [min]', r: 'p_inertia', lo: 1, hi: 60, st: 1, dc: 0, lv: 2 },
      { k: 40, t: 'Czas ruchu rusztu [s]', r: 'p_grate_time', lo: 0, hi: 60, st: 0.1, dc: 1, lv: 2 },
      { k: 41, t: 'Pod. palnika [%]', r: 'p_burner_feed', lo: 50, hi: 300, st: 1, dc: 0, lv: 2 },
      { k: 42, t: 'Okres podajnika zasobnika [s]', r: 'p_feeder_period', lo: 5, hi: 180, st: 1, dc: 0, lv: 2 },
      { k: 43, t: 'Minimalne obroty dmuchawy [x100]', r: 'p_min_rpm', lo: 0, hi: 5, st: 1, dc: 0, lv: 2 },
      { k: 67, t: 'Antylegionella', r: 'legion', tog: true, lv: 0 },
    ];
    W.PR2 = PR2; W.PR = PR;
    const L1 = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 'wsp', 13, 14, 15, 16], L2 = [17, 18, 19, 20, 21];
    const q = (v, c) => Number(Math.max(c.lo, Math.min(c.hi, Math.round(v / c.st) * c.st)).toFixed(c.dc));
    const KEYDIV = n => `<div class="svsep"><ha-icon icon="mdi:wrench" style="--mdc-icon-size:5cqw"></ha-icon><sup>${n}</sup></div>`;

    C.prototype.setConfig = (function (o) { return function (c) { this._idn = null; return o.call(this, c); }; })(C.prototype.setConfig);
    /* ---- poziom dostepu ---- */
    C.prototype._lvl = function () { const v = this._v('acc'); return isNaN(v) ? 0 : Math.max(0, Math.min(2, Math.round(v))); };
    C.prototype._unl = function () { return this._lvl() >= 1; };
    C.prototype._lvlSet = function () {};
    C.prototype._lvlTimer = function () {};
    C.prototype._touch = function () { W.t = Date.now(); };
    C.prototype._unlock = function (pin) { this._svc('unlock', { pin: String(pin || '') }); };
    C.prototype._pinOk = (function (o) {
      return function () {
        if (this._scr === 'level') {
          const c = (this._pd || [0, 0, 0, 0]).join('');
          this._pd = [0, 0, 0, 0]; W.t = Date.now();
          this._unlock(c); this._go('menu'); return;
        }
        return o.call(this);
      };
    })(C.prototype._pinOk);

    /* ---- rozpoznawanie encji nowych rol ---- */
    C.prototype._res = function (h) {
      if (!h) return;
      const ids = Object.keys(h.states);
      if (ids.length === this._idn) return;
      this._idn = ids.length;
      for (const r in NEW) {
        if (this.E[r]) continue;
        const sl = NEW[r], re = new RegExp('_' + sl + '(_\\d+)?$');
        const c = ids.filter(id => id.startsWith('sensor.') && id.includes('tekla') && re.test(id)).sort((a, b) => a.length - b.length);
        if (c.length) this.E[r] = c[0];
      }
    };
    const hd = Object.getOwnPropertyDescriptor(C.prototype, 'hass');
    Object.defineProperty(C.prototype, 'hass', {
      configurable: true, get: hd.get,
      set(h) {
        this._res(h);
        W.card = this;
        if (!W.init && h) { W.init = true; W.t = Date.now(); setTimeout(() => this._unlock(''), 1500); } // odswiezenie strony = poziom uzytkownika
        hd.set.call(this, h);
      },
    });
    if (!W.timer) W.timer = setInterval(() => {
      const c = W.card;
      if (c && c._hass && c._lvl() > 0 && Date.now() - W.t > LOCK_MS) { c._unlock(''); W.t = Date.now(); }
    }, 10000);

    const ot = C.prototype._t;
    C.prototype._t = function (k, d) { const r = ot.call(this, k, d); if (k === 'feeder' && r !== d && r !== '') { const x = parseFloat(String(r).replace(',', '.')); return (isNaN(x) ? r : String(Math.round(x * 10) / 10).replace('.', ',')) + ' s'; } return r; };

    /* ---- naglowki: ikona poziomu ---- */
    const fixHdr = function (h, lvl) { return lvl >= 1 ? h.replace(/<sup>[^<]*<\/sup>/, '<sup>' + lvl + '</sup>') : h; };
    C.prototype._hdr = (function (o) { return function () { return fixHdr(o.apply(this, arguments), this._lvl()); }; })(C.prototype._hdr);
    C.prototype._progHdr = (function (o) { return function () { return fixHdr(o.apply(this, arguments), this._lvl()); }; })(C.prototype._progHdr);
    C.prototype._hdrLive = (function (o) {
      return function () {
        const h = o.apply(this, arguments), l = this._lvl();
        return l >= 1 ? h.replace('<ha-icon icon="mdi:account"></ha-icon>', `<span class="wr"><ha-icon icon="mdi:wrench"></ha-icon><sup>${l}</sup></span>`) : h;
      };
    })(C.prototype._hdrLive);

    /* ---- nawigacja ---- */
    C.prototype._go = (function (o) {
      return function (s, b) {
        this._q2 = null; W.t = Date.now();
        if (s === 'test' && this._lvl() >= 1) this._testOk = true;
        return o.call(this, s, b);
      };
    })(C.prototype._go);

    /* ---- menu wg poziomu ---- */
    const mrow = (k, n, ic, v) => `<div class="row go mi"${k ? ` data-go="${k}" data-back="menu"` : ''}><span class="l"><ha-icon icon="${ic}"></ha-icon>${n}</span>${v == null ? '<span class="v ch2">&rsaquo;</span>' : `<span class="v">${v}</span>`}</div>`;
    C.prototype._menu = function () {
      const l = this._lvl(), r = [
        mrow('kociol', 'Kocioł', 'mdi:water-boiler'), mrow('burner_s', 'Palnik', 'mdi:fire'), mrow('co_s', 'Ogrzewanie obwód 1', 'mdi:radiator'),
        mrow('cwu_s', 'Ciepła woda użytkowa', 'mdi:faucet'), mrow('alarm', 'Historia alarmów', 'mdi:clipboard-alert-outline')];
      r.push(mrow('info', 'Informacje o programie', 'mdi:information'));
      r.push(`<div class="row go mi" data-go="level" data-back="menu"><span class="l"><ha-icon icon="mdi:account-lock"></ha-icon>Poziom menu (PIN)</span></div>`);
      // kolejnosc jak na panelu (zdjecia poziom 1 i 2): po Poziomie menu (PIN) dochodzi Jezyk, Alarm, Konfiguracja, Test, Statystyki, Siec
      if (l >= 1) r.push(mrow(null, 'Język', 'mdi:translate', (this._langLbl || 'PL')), mrow(null, 'Alarm dźwiękowy', 'mdi:volume-high', this._po(44)),
        mrow('conf', 'Konfiguracja', 'mdi:cog'), mrow('test', 'Test wyjść', 'mdi:toggle-switch-outline'), mrow('stats', 'Statystyki', 'mdi:chart-box-outline'), mrow('net', 'Sieć', 'mdi:lan'));
      return this._page('MENU', 'main', r.join(''));
    };

    /* ---- wiersze / okno edycji parametrow ---- */
    C.prototype._q2row = function (i) {
      const c = PR2[i], v = this._v(c.r);
      let val = '-';
      if (!isNaN(v)) val = c.tog ? `<span class="tgq${Math.round(v) % 2 === 1 ? ' on' : ''}"><i></i></span>` : v.toFixed(c.dc);
      return `<div class="row" data-act="${c.tog ? 'q2tog' : 'q2edit'}" data-i="${i}"><span class="l">${c.t}</span><span class="v">${val}</span></div>`;
    };
    C.prototype._q2Dlg = function () {
      const d = this._q2, c = PR2[d.i], f = x => x.toFixed(c.dc), p = (d.val - c.lo) / (c.hi - c.lo);
      return `<div class="qd"><div class="qx" data-act="q2cancel"></div><div class="qbg"></div>
        <span class="fmt" style="top:7.6cqw;font-size:4.2cqw">${c.t}</span>
        <div class="bval" style="top:12.4cqw;font-size:10.5cqw">${f(d.val)}</div>
        <span class="blb" style="left:17cqw">${f(c.lo)}</span><span class="blb" style="left:79cqw">${f(c.hi)}</span>
        ${this._sl('data-act="q2slide"', 17, 27, 66, p)}
        <div class="bpm" data-act="q2val" data-d="-1" style="left:17cqw"><i></i></div><div class="bpm pl" data-act="q2val" data-d="1" style="left:50.5cqw"><i></i><i></i></div>
        <div class="qok" data-act="q2ok">OK</div></div>`;
    };
    C.prototype._q2Act = function (act, a, e) {
      if (this._mirror()) return;
      const lvl = this._lvl();
      if (act === 'q2tog' || act === 'q2edit') {
        const i = +a.dataset.i, c = PR2[i], v = this._v(c.r);
        if (c.lv > lvl || isNaN(v)) return;
        if (c.tog) { this._svc('set_param', { key: c.k, value: Math.round(v) % 2 === 1 ? 0 : 1 }); return; }
        const val = q(v, c); this._q2 = { i, val, v0: val };
      } else if (!this._q2) return;
      else if (act === 'q2cancel') this._q2 = null;
      else if (act === 'q2val') { const c = PR2[this._q2.i]; this._q2.val = q(this._q2.val + (+a.dataset.d) * c.st, c); }
      else if (act === 'q2slide') { const c = PR2[this._q2.i]; this._q2.val = q(c.lo + this._slFrac(a, e) * (c.hi - c.lo), c); }
      else if (act === 'q2ok') {
        const d = this._q2, c = PR2[d.i];
        if (d.val !== d.v0) this._svc('set_param', { key: c.k, value: Number(d.val.toFixed(c.dc)) });
        this._q2 = null;
      }
      this._render(true);
    };

    /* ---- ekrany NASTAWY ---- */
    C.prototype._burnS = function () {
      const l = this._lvl(), e = (a, b) => this._row(a, b), P = this._prow.bind(this);
      const r = [P('Korekta powietrza [%]', this._p(this._v('air_corr'), 0), 3), P('Moc min [%]', this._p(this._v('power_min'), 0), 0),
        P('Moc max [%]', this._p(this._v('power_max'), 0), 1), P('Wartość opałowa [kWh/kg]', this._p(this._v('fuel_heat'), 1), 2),
        P('Ilość paliwa test [kg/h]', this._p(this._v('fuel_test'), 1), 4)];
      const item = i => i === 'wsp' ? [39, 40, 41, 42, 43, 47, 48, 49, 50, 51].map(k => this._prow(PR[k].t, this._po(k), k)).join('') : this._q2row(i);
      if (l >= 1) {
        r.push(KEYDIV(1), '<div class="row go" data-go="fanmod" data-back="burner_s"><span class="l">Moc dmuchawy modulacja [%]</span><span class="v ch">&rsaquo;</span></div>');
        L1.forEach(i => r.push(item(i)));
      }
      if (l >= 2) { r.push(KEYDIV(2)); L2.forEach(i => r.push(item(i))); }
      return this._page('NASTAWY', this._backTo, r.join('')) + (this._pr ? this._prDlg() : '') + (this._q2 ? this._q2Dlg() : '');
    };
    C.prototype._cwuS = function () {
      const l = this._lvl(), e = (a, b) => this._row(a, b);
      const r = [e('Temperatura komfortowa [°C]', this._p(this._v('cwu_comfort'), 0)), e('Temperatura ekonomiczna [°C]', this._p(this._v('cwu_eco'), 0)),
        this._prow('Zagrzej teraz', this._po(14), 14), this._prow('Histereza [°C]', this._po(15), 15), this._q2row(22), this._prow('Priorytet CWU', this._po(16), 16)];
      if (l >= 1) r.push(KEYDIV(1), this._prow('Źródło', this._po(17), 17), this._prow('Zwiększenie temperatury źródła [°C]', this._po(18), 18), this._prow('Delta załączenia pompy [°C]', this._po(19), 19), this._prow('Temp. maksymalna [°C]', this._po(38), 38));
      return this._page('NASTAWY', this._backTo, r.join('')) + (this._pr ? this._prDlg() : '') + (this._q2 ? this._q2Dlg() : '');
    };
    const NA = t => `<div class="row na"><span class="l">${t}</span><span class="v">-</span></div>`;
    // Kociol NASTAWY jak na panelu: poziom 0 = Temperatura zadana + histerezy; klucz 1 = pozycje serwisowe (rejestry nieznane -> "-")
    C.prototype._boilS = function () {
      const l = this._lvl(), e = (a, b) => this._row(a, b), P = this._prow.bind(this);
      const sp = this._v('boiler_manual'), sv = isNaN(sp) ? this._v('boiler_set') : sp;
      const r = [e('Temperatura zadana [°C]', this._p(sv, 0)), P('Histereza załączenia [°C]', this._po(5), 5), P('Histereza wyłączenia [°C]', this._po(6), 6)];
      if (l >= 1) r.push(KEYDIV(1), P('Minimalna temp. pomp [°C]', this._po(20), 20), P('Wybieg pompy [min]', this._po(36), 36), P('Minimalna temp. powrotu [°C]', this._po(21), 21), P('Czas mieszacza [s]', this._po(22), 22), P('Rezerwa paliwa stop [kg]', this._po(37), 37));
      return this._page('NASTAWY', this._backTo, r.join('')) + (this._pr ? this._prDlg() : '');
    };
    // pozycje klucza 1 (histerezy kotla, CO1) tylko od poziomu 1
    const hideL1 = function (h, ks, lvl) {
      const re = new RegExp('<div class="row" data-act="pedit" data-k="(' + ks.join('|') + ')">.*?</div>', 'g');
      if (lvl >= 1) { let first = true; return h.replace(re, m => { const o = first ? KEYDIV(1) + m : m; first = false; return o; }); }
      return h.replace(re, '');
    };
    C.prototype._body = (function (o) {
      return function (s) {
        if (s === 'burner_s') return this._burnS();
        if (s === 'cwu_s') return this._cwuS();
        if (s === 'boiler') return this._boilS();
        if (s === 'co_s') return hideL1(o.call(this, s), [7, 8, 9, 10, 11, 12, 13], this._lvl());
        if (s === 'level') return this._pinPg('menu', 'POZIOM MENU', this._lvl() > 0 ? `Poziom ${this._lvl()} aktywny` : 'Wpisz PIN');
        return o.call(this, s);
      };
    })(C.prototype._body);

    /* ---- zdarzenia: okna q2*, klik w nazwe dnia = odczyt ustawien ---- */
    const initQ = function () {
        if (this.__qInit || !this.shadowRoot) return; this.__qInit = true;
        const R = this.shadowRoot, st = document.createElement('style');
        st.textContent = '.dy{cursor:pointer}.row[data-act^="q2"]{cursor:pointer}.row.na{opacity:.5}';
        R.appendChild(st);
        R.addEventListener('click', e => {
          W.t = Date.now();
          const a = e.target.closest('[data-act^="q2"]');
          if (a) { this._q2Act(a.dataset.act, a, e); return; }
          if (e.target.closest('.dy')) this._svc('param_refresh');
        });
    };
    C.prototype._build = (function (o) { return function () { o.apply(this, arguments); initQ.call(this); }; })(C.prototype._build);
    C.prototype._render = (function (o) { return function () { initQ.call(this); return o.apply(this, arguments); }; })(C.prototype._render);

    })();

    // ---- modul: antylegionella ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v81) return;
    C.prototype.__v81 = true;
    const o = C.prototype._cwuS;
    C.prototype._cwuS = function () {
      return o.call(this);
    };

    })();

    // ---- modul: Ogrzewanie 1 nastawy ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v82) return;
    C.prototype.__v82 = true;
    const KEYDIV = n => `<div class="svsep"><ha-icon icon="mdi:wrench" style="--mdc-icon-size:5cqw"></ha-icon><sup>${n}</sup></div>`;
    const TOG = '-';
    const o = C.prototype._body;
    C.prototype._body = function (s) {
      if (s !== 'co_s') return o.call(this, s);
      const e = (a, b) => this._row(a, b), P = this._prow.bind(this), l = this._lvl();
      const r = [e('Temperatura komfortowa [°C]', this._p(this._v('co_comfort'), 1)), e('Temperatura ekonomiczna [°C]', this._p(this._v('co_eco'), 1)),
        P('Histereza [°C]', this._po(7), 7), P('Kalibracja czujnika pok. [°C]', this._po(8), 8), P('Tryb pracy', this._po(9), 9),
        P('Temperatura CO zadana ręcznie [°C]', this._po(10), 10), P('Temperatura CO dla -20°C [°C]', this._po(11), 11),
        P('Temperatura CO dla  0°C [°C]', this._po(12), 12), P('Temperatura CO dla 10°C [°C]', this._po(13), 13)];
      const na = t => `<div class="row na"><span class="l">${t}</span><span class="v">-</span></div>`;
      if (l >= 1) r.push(KEYDIV(1), P('Źródło', this._po(33), 33), P('Zwiększenie temperatury źródła [°C]', this._po(23), 23), P('Czujnik pokojowy', this._po(35), 35), P('Temp. maksymalna [°C]', this._po(24), 24),
        P('Czujnik CO', this._po(34), 34), P('Wsp. korekcji t. CO [°C/°C]', this._po(25), 25), P('MAX Tzew pomp komf. [°C]', this._po(26), 26), P('MAX Tzew pomp ekon. [°C]', this._po(27), 27),
        P('Obniżenie temperatury CO [°C]', this._po(28), 28), P('MIN temperatura CO pomp [°C]', this._po(29), 29), P('Czas mieszacza [s]', this._po(30), 30), P('Stała pompa', this._po(31), 31),
        P('Obniżenie Tco dla ochrony powrotu', this._po(32), 32));
      return this._page('NASTAWY', this._backTo, r.join('')) + (this._pr ? this._prDlg() : '') + (this._q2 ? this._q2Dlg() : '');
    };

    })();

    // ---- modul: czas podawania ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v83) return;
    C.prototype.__v83 = true;
    const o = C.prototype._t;
    C.prototype._t = function (k, d) {
      const r = o.call(this, k, d);
      if (k === 'feeder' && typeof r === 'string' && /^\s*0(\.0+)?\s*s?\s*$/.test(r)) return '';
      return r;
    };

    })();

    // ---- modul: historia alarmow ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v84) return;
    C.prototype.__v84 = true;
    const MAXAL = 20;
    const num = s => { const n = parseFloat(s); return isNaN(n) ? NaN : n; };
    const tm = x => x.lu != null ? x.lu : (x.last_updated ? Date.parse(x.last_updated) / 1000 : (x.lc != null ? x.lc : 0));
    const st = x => x.s != null ? x.s : x.state;

    // v9.1: historia alarmow z KOTLA (firmware >= 2.25: encje "Alarm wpis 1..20" = "kod N (opis)|poczatek|koniec"); rekorder HA tylko jako zapas dla starszego firmware
    C.prototype._alFromSensors = function () {
      const stt = this._hass && this._hass.states; if (!stt) return null;
      const out = []; let found = false;
      for (const id in stt) {
        if (!/^sensor\..*alarm_wpis_\d+$/.test(id)) continue; found = true;
        const p = String(stt[id].state).split('|'); if (p.length < 3) continue;
        const start = num(p[1]), end = num(p[2]); if (!(start > 1e9)) continue;
        out.push({ start, end: end > 1e9 && end >= start ? end : 0, txt: p[0] });
      }
      return found ? out.sort((x, y) => y.start - x.start).slice(0, MAXAL) : null;
    };

    C.prototype._alLoad = async function () {
      const fs = this._alFromSensors();
      if (fs) {
        this._svc('alarm_refresh');
        this._ah = fs; this._ai = 0; this._alBusy = false;
        const tok0 = this._altok = (this._altok || 0) + 1;
        [5000, 12000].forEach(ms => setTimeout(() => { if (tok0 !== this._altok || this._scr !== 'alarm') return; const f = this._alFromSensors(); if (f) { this._ah = f; this._render(true); } }, ms));
        if (this._scr === 'alarm') this._render(true);
        return;
      }
      const E = this.E, ids = [E.alarm_start, E.alarm_end, E.last_alarm].filter(Boolean);
      this._ah = null; this._ai = 0; this._alBusy = true; const tok = this._altok = (this._altok || 0) + 1;
      let list = [];
      try {
        const now = Date.now();
        const res = await this._hass.callWS({ type: 'history/history_during_period', start_time: new Date(now - 60 * 864e5).toISOString(), end_time: new Date(now).toISOString(), entity_ids: ids, include_start_time_state: true, significant_changes_only: false, minimal_response: true, no_attributes: true });
        const g = id => (res[id] || []).map(x => ({ t: tm(x), s: st(x) })).sort((a, b) => a.t - b.t);
        const S = g(E.alarm_start), En = g(E.alarm_end), T = g(E.last_alarm).filter(x => /kod\s+\d+/.test(x.s));
        const seen = new Map();
        for (const e of S) {
          const v = num(e.s); if (!(v > 1e9)) continue;
          let txt = '', end = 0;
          for (const x of T) { if (x.t <= e.t + 0.01) txt = x.s; else break; }
          for (const x of En) { if (x.t <= e.t + 3) { const n = num(x.s); if (n > 1e9) end = n; } else break; }
          if (!seen.has(v) || (!seen.get(v).txt && txt)) seen.set(v, { start: v, end, txt });
        }
        list = [...seen.values()].sort((a, b) => b.start - a.start).slice(0, MAXAL);
      } catch (e) { console.warn('tekla alarm history', e); }
      if (tok !== this._altok) return;
      if (!list.length) { const t0 = num(this._t('alarm_start', '0')); const txt = this._t('last_alarm', ''); if (/kod\s+\d+/.test(txt) && t0 > 1e9) list = [{ start: t0, end: 0, txt }]; }
      this._ah = list; this._ai = 0; this._alBusy = false;
      if (this._scr === 'alarm') this._render(true);
    };

    const og = C.prototype._go;
    C.prototype._go = function (s, b) {
      if (s === 'alarm') { this._ai = 0; this._ah = null; this._alLoad(); }
      return og.call(this, s, b);
    };

    // klikniecia strzalek + styl - podpiecie przy pierwszym rysowaniu (niezaleznie od momentu zbudowania karty)
    const ensure = self => {
      const R = self.shadowRoot; if (!R || self.__alL) return; self.__alL = true;
      const s = document.createElement('style');
      s.textContent = '.alar{opacity:1;width:11cqw;height:7.4cqw;left:85cqw}.alar svg{pointer-events:none}'
        + '.alb.al2{left:50%;transform:translateX(-50%);top:38cqw;width:34cqw;height:9cqw;font-size:5.4cqw;font-weight:500;letter-spacing:.02em;color:#fff;background:linear-gradient(#6a93d8,#5079c0);border:.3cqw solid #86a9e4;border-radius:.5cqw;cursor:pointer}'
        + '.alb.al2:active{filter:brightness(1.15)}.ala.al2{left:50%;transform:translateX(-50%);width:34cqw;top:48cqw;font-size:4.6cqw}';
      R.appendChild(s);
      R.addEventListener('click', e => {
        const a = e.target.closest && e.target.closest('[data-act]'); if (!a) return;
        const act = a.dataset.act;
        if (act === 'alup' && self._ah && self._ai < self._ah.length - 1) { self._ai++; self._render(true); }
        else if (act === 'aldn' && self._ah && self._ai > 0) { self._ai--; self._render(true); }
      });
    };

    const CHEV = up => `<svg viewBox="0 0 24 24" style="width:70%;height:70%"><polyline points="${up ? '5,15 12,8 19,15' : '5,9 12,16 19,9'}" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    const oa = C.prototype._alarmPg;
    C.prototype._alarmPg = function (back) {
      ensure(this);
      if (this._ah === undefined && !this._alBusy && this._hass) this._alLoad();
      const list = this._ah, i = this._ai || 0;
      let h;
      if (!list || !list.length) h = oa.call(this, back);
      else {
        const r = list[Math.min(i, list.length - 1)];
        this._t = (k, d) => k === 'last_alarm' ? r.txt : k === 'alarm_start' ? String(r.start) : C.prototype._t.call(this, k, d);
        try { h = oa.call(this, back); } finally { delete this._t; }
        h = h.replace('NR: 1', `NR: ${i + 1}`);
        if (i > 0) h = h.replace(/<div class="alb"[^>]*>[^<]*<\/div><span class="ala">[^<]*<\/span>/, '');
        const up = i < list.length - 1, dn = i > 0;
        const btn = (top, act, ok, svg) => `<div class="alar" data-act="${ok ? act : 'alnone'}" style="top:${top}cqw;${ok ? 'cursor:pointer;opacity:1' : 'opacity:.35'}">${svg}</div>`;
        h = h.replace(/<div class="alar" style="top:22cqw">[\s\S]*?<\/div><div class="alar" style="top:35\.5cqw">[\s\S]*?<\/div>/,
          list.length > 1 ? btn(22, 'alup', up, CHEV(true)) + btn(35.5, 'aldn', dn, CHEV(false)) : '');
      }
      // przycisk POTWIERDZ na srodku pustego pola (tylko aktywny, najnowszy alarm)
      return h.replace('class="alb" data-act="confirm"', 'class="alb al2" data-act="confirm"').replace('<span class="ala">', '<span class="ala al2">');
    };

    })();

    // ---- modul: grafiki z plikow ----
    (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v85) return;
    C.prototype.__v85 = true;

    const BASE = new URL('.', import.meta.url).pathname + 'img/';
    const EXT = ['png', 'webp', 'jpg', 'jpeg', 'svg'];
    const stamp = Date.now(); // plik jest pobierany swiezo przy kazdym odswiezeniu strony
    const IM = window.__igneoImg = window.__igneoImg || {};
    const probe = url => new Promise(res => { const im = new Image(); im.onload = () => res(true); im.onerror = () => res(false); im.src = url; });
    const pick = async name => {
      const urls = EXT.map(x => BASE + name + '.' + x + '?v=' + stamp);
      const ok = await Promise.all(urls.map(probe));
      const i = ok.indexOf(true);
      return i < 0 ? '' : urls[i];
    };

    const ot = C.prototype._tank;
    C.prototype._tank = function () {
      return IM.tank ? `<img class="tank" alt="Bojler" src="${IM.tank}" draggable="false">` : ot.call(this);
    };

    const [b, p, t] = await Promise.all([pick('kociol'), pick('palnik'), pick('bojler')]);
    IM.boiler = b; IM.burner = p; IM.tank = t;
    for (let i = 0; i < 40 && !(b && p) && !(window.TEKLA_IMG && window.TEKLA_IMG.boiler); i++) await new Promise(r => setTimeout(r, 100));
    const T = window.TEKLA_IMG = window.TEKLA_IMG || {};
    if (b) T.boiler = b;
    if (p) T.burner = p;
    window.dispatchEvent(new Event('tekla-img')); // odswiezenie wszystkich kart

    })();

    // ---- modul: autor na INFO ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v86) return;
    C.prototype.__v86 = true;
    const ob = C.prototype._body;
    C.prototype._body = function (s) {
      const r = ob.call(this, s);
      if (s !== 'info' || typeof r !== 'string') return r;
      return r.replace('Controller by Estyma (www.estyma.pl)</div>', 'Controller by Estyma (www.estyma.pl)</div><div class="dim">Kod EspHome i karta: Gorz Roman</div>');
    };

    })();

    // ---- modul v9.2: automatyczne wykrywanie encji, tryb lite, edytor wizualny ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v92) return;
    C.prototype.__v92 = true;
    const W = window.__tekla80, D = window.__teklaDefs || { ENT_GROUPS: [], ROLE_KEY: {}, SCREEN_OPTS: [] };
    const ROLE_DOM = {};
    D.ENT_GROUPS.forEach(g => g[1].forEach(f => { ROLE_DOM[f[0]] = f[2]; }));
    const keysAll = () => Object.assign({}, D.ROLE_KEY, (W && W.NEW) || {});
    const SENS = ['sensor', 'input_number', 'number'];

    // znajduje encje roli po koncowce entity_id (nazwy z ESPHome tekla_estyma); prefix = fragment nazwy urzadzenia (domyslnie "tekla")
    // S = stany z hass: encja z aktualnym stanem ma pierwszenstwo przed 'unknown/unavailable' (np. stare duplikaty), potem najkrotsza nazwa
    const findRole = (ids, role, key, pf, S) => {
      const doms = ROLE_DOM[role] || SENS, re = new RegExp('(^|_)' + key + '(_\\d+)?$');
      const live = id => !S || !S[id] || (S[id].state !== 'unknown' && S[id].state !== 'unavailable') ? 1 : 0;
      const c = ids.filter(id => { const i = id.indexOf('.'), o = id.slice(i + 1); return doms.includes(id.slice(0, i)) && (!pf || o.includes(pf)) && re.test(o); }).sort((a, b) => (live(b) - live(a)) || a.length - b.length);
      return c[0] || '';
    };
    window.__igneoFind = { findRole, keysAll, ROLE_DOM };
    // wykrywanie urzadzenia: encje-kotwice z ESP (np. ..._poziom_dostepu) -> prefiks = reszta nazwy; najlepsze = najwiecej kotwic
    const ANCH = ['poziom_dostepu', 'test_wyjsc_stany', 'wersja_firmware', 'tryb_mirror', 'can_ok', 'alarm_aktywny'];
    const devices = ids => {
      const m = {};
      ids.forEach(id => { const o = id.slice(id.indexOf('.') + 1); ANCH.forEach(a => { if (o.length > a.length + 1 && o.endsWith('_' + a)) { const p = o.slice(0, -(a.length + 1)); (m[p] = m[p] || new Set()).add(a); } }); });
      return Object.keys(m).map(p => ({ p, n: m[p].size })).sort((a, b) => b.n - a.n || b.p.length - a.p.length);
    };
    const pfOf = (cfg, ids) => {
      const x = cfg && cfg.entity_prefix != null ? String(cfg.entity_prefix).trim().toLowerCase() : '';
      if (x) return x;
      const d = ids ? devices(ids) : []; return d.length ? d[0].p.split('_').pop() : 'tekla';   // prefiks bazowy (czesc nazwy po nazwie pomieszczenia), bo czesc encji ma tylko tekla_, a czesc kotlownia_tekla_
    };
    window.__igneoFind.devices = devices; window.__igneoFind.pfOf = pfOf;
    // usluga ESP: wezel wykrywany z uslug esphome (<wezel>_set_param), chyba ze podano esphome_node
    const on0 = C.prototype._node;
    C.prototype._node = function () {
      if (this._cfg && this._cfg.esphome_node) return this._cfg.esphome_node;
      const sv = this._hass && this._hass.services && this._hass.services[(this._cfg && this._cfg.service_domain) || 'teklapelletcan'];
      if (sv) { const n = Object.keys(sv).filter(k => k.endsWith('_set_param')).map(k => k.slice(0, -10)); if (n.length) return n.find(x => /estyma|tekla/.test(x)) || n[0]; }
      return on0.call(this);
    };

    // brak encji = "-" (jak na panelu); jawne wpisy z konfiguracji maja pierwszenstwo, reszta wykrywana sama
    C.prototype._res = function (h) {
      if (!h || !h.states) return;
      const ids = Object.keys(h.states), pf = pfOf(this._cfg, ids), keys0 = keysAll(), sig = ids.length + '|' + pf + '|' + Object.keys(keys0).length;
      if (sig === this._idn) return;
      this._idn = sig;
      const keys = keysAll();
      for (const r in keys) { if (this.E[r]) continue; const e = findRole(ids, r, keys[r], pf, h.states); if (e) this.E[r] = e; }
    };

    // ---- tryb lite (tylko w YAML: lite: true) = poziom 0 dla zwyklego uzytkownika, bez "Poziom menu" ----
    const LITE_GO = ['level', 'test', 'stats', 'net', 'fanmod'];
    const sc = C.prototype.setConfig;
    C.prototype.setConfig = function (c) { this._lite = !!(c && c.lite === true); return sc.call(this, c); };
    const ol = C.prototype._lvl;
    C.prototype._lvl = function () { return this._lite ? 0 : ol.call(this); };
    const om = C.prototype._menu;
    C.prototype._menu = function () {
      const h = om.call(this);
      return this._lite ? h.replace(/<div class="row go mi" data-go="level"[\s\S]*?<\/div>/, '') : h;
    };
    const og2 = C.prototype._go;
    C.prototype._go = function (s, b) { if (this._lite && LITE_GO.includes(s)) return; return og2.call(this, s, b); };
    // ---- pakiet oryginalnych grafik panela: img/panel/NNN.png (numery jak w tablicy bitmap FW panela) ----
    await (async () => {
      const PB = new URL('.', import.meta.url).pathname + 'img/panel/';
      const stamp = Date.now();
      const has = n => new Promise(r => { const im = new Image(); im.onload = () => r(true); im.onerror = () => r(false); im.src = PB + String(n).padStart(3, '0') + '.png?v=' + stamp; });
      if (!(await has(54))) return;   // brak pakietu = zostaja wektory (wystarczy zbiornik: 48, 49, 50, 54)
      const U = n => PB + String(n).padStart(3, '0') + '.png?v=' + stamp, K = 0.2083;   // 1 px panelu = 0,2083 cqw (480 px = 100 cqw)
      const img = (n, st) => `<img src="${U(n)}" draggable="false" style="${st || ''}">`;
      const seq = (ns, w, h, on) => `<span class="sp ${on ? 'on' : ''}" style="width:${(w * K).toFixed(2)}cqw;height:${(h * K).toFixed(2)}cqw">${ns.map(n => img(n)).join('')}</span>`;
      const oc = C.prototype._css;
      C.prototype._css = function () {
        const BS = { 11: [105, 126], 12: [100.4, 131.1], 14: [73.9, 136.9] } /* 14: wąska szafa 54x100 skalowana do wysokości zbliżonej do pozostałych typów */, bt = this._cfg && FULL(this) ? BS[+this._cfg.boiler_image] : null;
        // obrazy kotla 11/12 maja inne proporcje niz domyslny: skala 1:1 jak w panelu, srodek i podstawa jak dla kociola domyslnego
        const boil = bt ? `.boil{width:${(bt[0] * K).toFixed(2)}cqw!important;left:${(15 - bt[0] * K / 2).toFixed(2)}cqw!important;top:${(35.5 - bt[1] * K).toFixed(2)}cqw!important;height:auto!important}` : '';
        return oc.call(this) + boil + `.sp{position:relative;display:inline-block;line-height:0}.sp img,.mbs{mix-blend-mode:screen}.sp img{position:absolute;left:0;top:0;width:100%;height:100%;opacity:0}.sp img:first-child{opacity:1}
        .sp.on img{animation:spfr .45s linear infinite}.sp.on img:nth-child(2){animation-delay:.15s}.sp.on img:nth-child(3){animation-delay:.3s}
        @keyframes spfr{0%,33.3%{opacity:1}33.4%,100%{opacity:0}}.sp.on img:first-child{opacity:0}.sp.slow img{animation-duration:1.5s}.sp.slow img:nth-child(2){animation-delay:.5s}.sp.slow img:nth-child(3){animation-delay:1s}
        .ftk.pk{background:url(${U(54)}) 0 0/100% 100% no-repeat!important;border:0!important}.ftk.pk .fth,.ftk.pk .fhd{display:none}
        .sq{position:relative;display:inline-block;line-height:0}.sq img{position:absolute;left:0;top:0;width:100%;height:100%;opacity:0;mix-blend-mode:screen;animation:spf4 2s linear infinite}.sq img:nth-child(2){animation-delay:.5s}.sq img:nth-child(3){animation-delay:1s}.sq img:nth-child(4){animation-delay:1.5s}
        @keyframes spf4{0%,25%{opacity:1}25.01%,100%{opacity:0}}`
          + (FULL(this) ? `.tgq,.row .tgq{background:url(${U(184)}) 0 0/100% 100% no-repeat!important;box-shadow:none!important;border-radius:0!important;height:auto!important;aspect-ratio:45/20}.tgq.on,.row .tgq.on{background-image:url(${U(185)})!important}.tgq i,.tgq::before,.tgq::after,.row .tgq::before,.row .tgq::after{display:none!important}
        .fmp{background:url(${U(56)}) 0 0/100% 100% no-repeat!important;border:0!important;box-shadow:none!important;width:4.17cqw!important;height:4.17cqw!important;margin:-2.08cqw 0 0 -2.08cqw!important}.fmp.sel{background-image:url(${U(57)})!important}
        .tr .tb{background:url(${U(19)}) 0 0/100% 100% no-repeat!important;border:0!important;border-radius:0!important;width:6.25cqw!important;height:6.46cqw!important}.tr .tb.ck{background-image:url(${U(20)})!important}.tr .tb svg{display:none!important}
        .sl i{background:url(${U(70)}) center/100% 100% no-repeat!important;box-shadow:none!important;border-radius:0!important;width:6.5cqw!important;height:6.5cqw!important;top:-2.15cqw!important;margin-left:-3.25cqw!important}` : '');
      };
      // grafiki: domyslne = z pakietu tylko zbiornik paliwa (48, 49, 50, 54); bez ustawienia (albo pelne) = wszystkie grafiki panelu
      const FULL = t => !!(t && t._cfg && t._cfg.grafiki !== 'domyslne');   // domyślnie pełne grafiki panelu; 'domyslne' = tylko zbiornik paliwa
      const gate = (name, fn) => { const o = C.prototype[name]; C.prototype[name] = function (...a) { return FULL(this) ? fn.apply(this, a) : o.apply(this, a); }; };
      gate('_fan', function (spin) { return seq([8, 9, 10], 34, 27, spin); });
      gate('_augSvg', function (anim = true) { return seq([36, 37, 38], 34, 27, anim); });
      gate('_auger', function (n, run) { return run ? `<span class="augw">${seq(n === 2 ? [40, 41, 42] : [36, 37, 38], 34, 27, true)}</span>` : ''; });
      gate('_valve', function (mv) {
        if (!mv) return '';
        return `<span class="sp" style="width:${(34 * K).toFixed(2)}cqw;height:${(27 * K).toFixed(2)}cqw">${img(105)}</span><span style="position:absolute;margin-left:-${(24 * K).toFixed(1)}cqw;margin-top:-4.4cqw;width:${(15 * K).toFixed(2)}cqw;line-height:0">${img(mv === 1 ? 106 : 107, 'width:100%').replace('<img ', '<img class="mbs" ')}</span>`;
      });
      const of = C.prototype._fuelDlg;
      C.prototype._fuelDlg = function () {
        let h = of.call(this);
        const W = (29 * K).toFixed(2), H = (155 * K).toFixed(2);
        h = h.replace('<div class="ftk">', '<div class="ftk pk">');
        h = h.replace(/<div class="fbar"><i style="height:([\d.]+)%"><\/i><\/div>/, (m, p) =>
          `<div style="position:absolute;left:9.7cqw;top:9.58cqw;width:${W}cqw;height:${H}cqw">${img(48, 'position:absolute;left:0;top:0;width:100%;height:100%')}<div style="position:absolute;left:0;right:0;bottom:0;height:${p}%;overflow:hidden">${img(49, `position:absolute;left:0;bottom:0;width:100%;height:${H}cqw`)}</div></div>`);
        h = h.replace(/<div class="fhn" style="top:([\d.]+)cqw"><\/div>/, (m, y) => `<img src="${U(50)}" draggable="false" style="position:absolute;left:11.6cqw;top:${(y - 21 * K).toFixed(2)}cqw;width:${(57 * K).toFixed(2)}cqw">`);
        return h.replace(/<svg viewBox="0 0 24 13" class="fch"[\s\S]*?<\/svg>/g, '');
      };
      // zapalarka (grzalka) w trzeciej komorce paska ekranu Palnik: 65 = zimna, 66 = grzeje, 67 = rozgrzana
      const ob = C.prototype._burn;
      C.prototype._burn = function (ctx) {
        const h = ob.call(this, ctx), g = this._v('burn_ign');
        if (!FULL(this) || isNaN(g) || g <= 0) return h;   // grzałka tylko gdy zapalarka pracuje
        const ic = `<span class="sq" style="width:${(34 * K).toFixed(2)}cqw;height:${(15 * K).toFixed(2)}cqw">${img(65)}${img(66)}${img(67)}${img(66)}</span>`;   // animacja 65-66-67-66-65 (tam i z powrotem, 2 s)
        return h.replace('<div class="c"></div>', `<div class="c">${ic}</div>`);
      };
      const T = window.TEKLA_IMG = window.TEKLA_IMG || {}, IM2 = window.__igneoImg = window.__igneoImg || {};
      let BC = null;
      const bi = c => { if (c !== undefined) BC = c; if (!FULL(BC && { _cfg: BC })) return; T.burner = U(17); T.boiler = U([11, 12, 13, 14].includes(+(BC && BC.boiler_image)) ? +BC.boiler_image : 13); };
      bi(null);
      window.addEventListener('tekla-img', () => { if (!FULL(BC && { _cfg: BC })) return; if (T.boiler !== U([11, 12, 13, 14].includes(+(BC && BC.boiler_image)) ? +BC.boiler_image : 13) || T.burner !== U(17)) { bi(); window.dispatchEvent(new Event('tekla-img')); } });
      const sc3 = C.prototype.setConfig;
      C.prototype.setConfig = function (c) { bi(c); return sc3.call(this, c); };
      window.dispatchEvent(new Event('tekla-img'));
    })();

    // ---- tryb demo (YAML: demo: true) = dane przykladowe bez ESP/HA, do zrzutow ekranu i testow wygladu ----
    const DEMO = {
      boil_pwr: 10, boil_cons: 2.3, grate_t: 145, exh_pct: 40, nominal_kw: 18, predose_g: 100, egt_min: 90, egt_max: 220, exch_int: 180, cwu_tmax: 60, legion: 1, exh_c1: 20, exh_c2: 30, exh_c3: 40, exh_c4: 50, exh_c5: 60, alarm_snd: 1, alarm_sil_from: 22, alarm_sil_to: 6, boiler_temp: 68.4, boiler_set: 70, boiler_manual: 70, outside: 3.5, ret_temp: 55.2, on: 'on', power_switch: 'on',
      burner: 'Praca', burner_code: 5, power: 62, burn_kw: 14.8, burn_kgh: 3.1, burn_bright: 74, burn_temp: 412,
      air_corr: 0, power_min: 30, power_max: 100, fuel_heat: 4.8, fuel_test: 21.5, fan_pct: 48, blower_run: 'on', feeder_run: 'on', burn_ign: 60, mix_co1: 1, feeder: 'Stop',
      burn_time: '5 h 12 min', fuel: 183, fuel_cap: 250, fuel_pct: 73, feed_time: 7,
      co_temp: 41.5, co_set: 45, co_manual: 45, co_pump: 'on', co_comfort: 45, co_eco: 38, co_mode: 3,
      cwu_temp: 47.2, cwu_set: 50, cwu_comfort: 50, cwu_eco: 40, cwu_pump: 'off', cwu_mode: 3,
      stats: '214 118 2310 0 4120 37 2 5 43 0 0 0 0 5821', conf: '0 0 1 0 1 0 0 0 0 0 1 2 0 0 0 0 0 0', fuel_use: 62.4, fuel_days: 2.9, fuel_low: 'off',
      fan_mod_1: 30, fan_mod_2: 40, fan_mod_3: 50, fan_mod_4: 60, fan_mod_5: 70,
      alarm: 'off', last_alarm: '-', can_ok: 'on', mirror: 'off', blower_mode: 'Automat', feeder_mode: 'Automat',
      sch_boil: '000000 000000 000000 000000 000000 000000 000000', sch_co: '03FC3C 03FC3C 03FC3C 03FC3C 03FC3C 03FC3C 03FC3C', sch_cwu: 'FFFFFF FFFFFF FFFFFF FFFFFF FFFFFF FFFFFF FFFFFF'
    };
    window.__teklaDemo = DEMO;
    const os0 = C.prototype._s;
    C.prototype._s = function (k) {
      if (this._cfg && this._cfg.demo) { const v = DEMO[k]; return v === undefined ? undefined : { state: String(v), attributes: {} }; }
      return os0.call(this, k);
    };
    const sc2 = C.prototype.setConfig;
    C.prototype.setConfig = function (c) {
      const r = sc2.call(this, c);
      if (c && c.demo) {
        for (const k in keysAll()) if (!this.E[k]) this.E[k] = 'demo.' + k;
        if (!this._hass) this._hass = { states: {}, services: {}, callService() {}, language: 'pl' };
        this._render && this._built && this._render(true);
      }
      return r;
    };
    const ol2 = C.prototype._lvl;
    C.prototype._lvl = function () { return this._cfg && this._cfg.demo ? (window.__demoLvl || 1) : ol2.call(this); };
    const osv = C.prototype._svc;
    C.prototype._svc = function (n, d) { if (this._cfg && this._cfg.demo) return; return osv.call(this, n, d); };

    if (!customElements.get('tekla-panel-card_lite')) {   // zgodnosc wsteczna: stara karta lite = ta sama karta z lite: true
      customElements.define('tekla-panel-card_lite', class extends C { setConfig(c) { super.setConfig(Object.assign({}, c, { lite: true })); } });
    }

    if (!customElements.get('pelletcan-card')) customElements.define('pelletcan-card', class extends C {});   // alias typu: custom:pelletcan-card = custom:tekla-panel-card
    window.customCards = window.customCards || [];   // wybor karty w edytorze dashboardu
    if (!window.customCards.some(c => c.type === 'pelletcan-card')) window.customCards.push({ type: 'pelletcan-card', name: 'PelletCAN-card', description: 'Panel kotła pelletowego (replika panelu Igneo Touch) dla PelletCAN', preview: false });
    // ---- edytor wizualny: sekcje wg ekranow i menu karty ----
    const PR2L = {}; ((W && W.PR) || []).concat((W && W.PR2) || []).forEach(c => { PR2L[c.r] = c.t; });
    const LBL = {}; D.ENT_GROUPS.forEach(g => g[1].forEach(f => { LBL[f[0]] = f[1]; }));
    const lab = r => LBL[r] || PR2L[r] || (r === 'fw_ver' ? 'Wersja firmware (ekran INFO)' : r);
    const GR = [
      ['Ekran główny i ekran Kocioł', ['boiler_temp', 'boiler_set', 'boiler_manual', 'mode', 'sch_boil', 'on', 'power_switch', 'outside', 'ret_temp', 'mix_co1', 'mix_ret'], 0],
      ['Ekran główny – Palnik i zbiornik paliwa', ['burner', 'burner_code', 'power', 'burn_kw', 'burn_kgh', 'burn_bright', 'burn_temp', 'ban', 'fan_pct', 'blower_run', 'feeder_run', 'feeder2_run', 'feeder', 'burn_time', 'fuel', 'fuel_cap', 'fuel_pct', 'feed_time'], 0],
      ['Ekran Ogrzewanie (CO)', ['co_temp', 'co_set', 'co_manual', 'co_pump', 'co_aux', 'co_comfort', 'co_eco', 'sch_co', 'co_mode', 'co_mode_sel'], 0],
      ['Ekran Woda użytkowa (CWU)', ['cwu_temp', 'cwu_set', 'cwu_comfort', 'cwu_eco', 'sch_cwu', 'cwu_mode', 'cwu_mode_sel', 'cwu_pump'], 0],
      ['Menu → Palnik → NASTAWY (użytkownik)', ['air_corr', 'power_min', 'power_max', 'fuel_heat', 'fuel_test'], 0],
      ['Menu → Ciepła woda → NASTAWY', ['cwu_hyst', 'cwu_boost', 'cwu_prio', 'legion'], 0],
      ['Menu → Ciepła woda → NASTAWY (klucz 1)', ['cwu_src', 'cwu_src_inc', 'cwu_delta', 'cwu_tmax'], 1],
      ['Menu → Konfiguracja → Alarm dźwiękowy (klucz 1)', ['alarm_snd', 'alarm_sil_from', 'alarm_sil_to'], 1],
      ['Menu → Statystyki (odczyty z kotła)', ['boil_pwr', 'boil_cons', 'grate_t', 'exh_pct'], 1],
      ['Menu → Palnik → NASTAWY (klucz 1)', ['nominal_kw', 'predose_g', 'egt_min', 'egt_max', 'exch_int'], 1],
      ['Menu → Palnik → NASTAWY → Wentylator spalin (klucz 1)', ['exh_c1', 'exh_c2', 'exh_c3', 'exh_c4', 'exh_c5'], 1],
      ['Menu → Historia alarmów', ['alarm', 'last_alarm', 'alarm_start', 'alarm_end', 'confirm'], 0],
      ['Menu → Kocioł → NASTAWY (użytkownik)', ['boiler_hyst_on', 'boiler_hyst_off'], 0],
      ['Menu → Kocioł → NASTAWY (klucz 1)', ['boiler_pump_min', 'boiler_pump_run', 'boiler_ret_min', 'boiler_mixer_time', 'boiler_fuel_reserve'], 1],
      ['Menu → Ogrzewanie obwód 1 → NASTAWY (użytkownik)', ['co_hyst', 'co_calib', 'co_mode_s', 'co_cur_m20', 'co_cur_0', 'co_cur_10'], 0],
      ['Menu → Ogrzewanie obwód 1 → NASTAWY (klucz 1)', ['co_src_inc', 'co_tmax', 'co_corr', 'co_out_comf', 'co_out_eco', 'co_lower', 'co_pump_min', 'co_mixer_time', 'co_const_pump', 'co_ret_protect', 'co_source', 'co_co_sensor', 'co_room'], 1],
      ['Menu → Palnik → NASTAWY (klucz 1)', ['fan_mod_1', 'fan_mod_2', 'fan_mod_3', 'fan_mod_4', 'fan_mod_5', 'p_prefeed', 'p_feed_max', 'p_photo', 'p_blow_ign', 'p_blow_glow', 'p_blow_stop', 'p_glow_time', 'p_glow_fuel', 'p_stop_time', 'p_lambda', 'p_o2_30', 'p_o2_100', 'p_cleans', 'p_clean_gap', 'p_pause_time', 'p_pause_power', 'p_pause_blow'], 1],
      ['Menu → Palnik → NASTAWY (klucz 2)', ['p_inertia', 'p_grate_time', 'p_burner_feed', 'p_feeder_period', 'p_min_rpm'], 1],
      ['Menu → Statystyki i Test wyjść (klucz 1)', ['stats', 'blower_mode', 'blower_auto', 'blower_off', 'blower_on', 'feeder_mode', 'feeder_auto', 'feeder_off', 'feeder_on'], 1],
      ['System', ['can_ok', 'mirror', 'acc', 'fw_ver'], 0],
    ];
    class IgneoEditor extends HTMLElement {
      setConfig(c) { this._cfg = c || {}; this._draw(); }
      set hass(h) { const first = !this._hass; this._hass = h; if (this._form) this._form.hass = h; if (first) this._draw(); else this._status(); }
      _ids() { return this._hass ? Object.keys(this._hass.states) : []; }
      _groups() {
        const known = new Set(GR.flatMap(g => g[1])), all = Object.keys(keysAll());
        const rest = all.filter(r => !known.has(r));
        const gs = GR.filter(g => !(this._cfg.lite && g[2] === 1));
        if (rest.length && !this._cfg.lite) gs.push(['Inne', rest, 1]);
        return gs;
      }
      _flat() {
        const c = this._cfg, ids = this._ids(), pf = pfOf(c, ids), keys = keysAll(), ex = c.entities || {};
        const d = {
          screen: c.screen || 'main', language: ({ dk: 'da', se: 'sv', cz: 'cs', est: 'et' }[String(c.language || 'pl').toLowerCase()] || c.language || 'pl'), device: c.entity_prefix ? String(c.entity_prefix) : 'auto',
          esphome_node: c.esphome_node || '', grafiki: c.grafiki === 'domyslne' ? 'domyslne' : 'pelne', boiler_image: [11, 12, 13, 14].includes(+c.boiler_image) ? String(c.boiler_image) : '13', lite: !!c.lite, demo: !!c.demo, mirror_mode: typeof c.mirror === 'boolean' ? (c.mirror ? 'on' : 'off') : 'auto',
        };
        Object.keys(keys).forEach(r => { d['e_' + r] = ex[r] || (ids.length ? findRole(ids, r, keys[r], pf, this._hass.states) : ''); });   // pola od razu pokazuja wykryte encje
        return d;
      }
      _draw() {
        if (!this._cfg) return;   // hass bywa ustawiony przed setConfig
        if (!this._form) {
          const info = document.createElement('div');
          info.style.cssText = 'font-size:13px;line-height:1.45;margin:0 0 10px;opacity:.9';
          info.innerHTML = '<b>Nic nie musisz ustawiać.</b> Karta sama wykrywa urządzenie PelletCAN i jego encje. Wybierz tylko ekran startowy. Pola encji poniżej pokazują wykryte encje i można je podmienić na inne z tego samego urządzenia.';
          this.appendChild(info);
          this._st = document.createElement('div');
          this._st.style.cssText = 'font-size:12px;opacity:.85;margin:0 0 10px';
          this.appendChild(this._st);
          this._form = document.createElement('ha-form');
          this._form.computeLabel = s => s.label || s.name;
          this._form.addEventListener('value-changed', ev => this._changed(ev.detail.value));
          this.appendChild(this._form);
        }
        const ids = this._ids(), pf = pfOf(this._cfg, ids), devs = devices(ids), keys = keysAll();
        const mine = ids.filter(id => id.slice(id.indexOf('.') + 1).includes(pf));   // encje wybranego urzadzenia
        const sel = r => { const dm = ROLE_DOM[r] || SENS, inc = mine.filter(id => dm.includes(id.slice(0, id.indexOf('.')))); return { entity: Object.assign({ domain: dm }, ids.length ? { include_entities: inc.length ? inc : ['none.none'] } : {}) }; };
        const schema = [{
          type: 'expandable', title: 'Ogólne', expanded: true, flatten: true, schema: [
            { name: 'screen', label: 'Ekran startowy karty', selector: { select: { mode: 'dropdown', options: D.SCREEN_OPTS.map(o => ({ value: o[0], label: o[1] })) } } },
            { name: 'language', label: 'Język / Language', selector: { select: { mode: 'dropdown', options: [{ value: 'auto', label: 'Auto (język Home Assistant)' }].concat(Object.keys((window.__pcLang || {}).names || {}).map(k => ({ value: k, label: window.__pcLang.names[k] }))) } } },
            { name: 'device', label: 'Urządzenie (prefiks encji)', selector: { select: { mode: 'dropdown', custom_value: true, options: [{ value: 'auto', label: 'Automatycznie' + (devs.length ? ' (' + pf + ')' : '') }].concat(devs.map(d => ({ value: d.p, label: d.p }))) } } },
            { name: 'grafiki', label: 'Grafiki panela', selector: { select: { mode: 'dropdown', options: [{ value: 'domyslne', label: 'Domyślne (tylko zbiornik paliwa)' }, { value: 'pelne', label: 'Pełne (wentylator, podajniki, zawór, grzałka, kocioł, palnik)' }] } } },
            { name: 'boiler_image', label: 'Obraz kotła (grafiki pełne)', selector: { select: { mode: 'dropdown', options: [{ value: '11', label: 'Typ 11' }, { value: '12', label: 'Typ 12' }, { value: '13', label: 'Typ 13 (domyślny)' }, { value: '14', label: 'Typ 14' }] } } },
          ],
        }, {
          type: 'expandable', title: 'Zaawansowane (zwykle zbędne)', flatten: true, schema: [
            { name: 'lite', label: 'Tryb lite (tylko poziom 0, bez PIN-u)', selector: { boolean: {} } },
            { name: 'demo', label: 'Tryb demo (dane przykładowe, bez ESP)', selector: { boolean: {} } },
            { name: 'esphome_node', label: 'Węzeł ESPHome – puste = wykryty automatycznie', selector: { text: {} } },
            { name: 'mirror_mode', label: 'Tryb mirror (blokada zapisów w tej karcie)', selector: { select: { mode: 'dropdown', options: [{ value: 'auto', label: 'wg ESP (domyślnie)' }, { value: 'on', label: 'włączony – tylko podgląd' }, { value: 'off', label: 'wyłączony' }] } } },
          ],
        }];
        this._groups().forEach(g => schema.push({
          type: 'expandable', title: g[0], flatten: true,
          schema: g[1].filter(r => keys[r]).map(r => ({ name: 'e_' + r, label: lab(r), selector: sel(r) })),
        }));
        this._form.schema = schema;
        this._form.data = this._flat();
        if (this._hass) this._form.hass = this._hass;
        this._status();
        this._sync();
      }
      _status() {
        if (!this._st || !this._hass) return;
        const ids = this._ids(), pf = pfOf(this._cfg, ids), keys = keysAll(), ex = this._cfg.entities || {};
        let ok = 0, miss = [];
        Object.keys(keys).forEach(r => { if (ex[r] || findRole(ids, r, keys[r], pf, this._hass.states)) ok++; else miss.push(lab(r)); });
        this._st.textContent = `Urządzenie: ${pf} · encje znalezione dla ${ok} z ${Object.keys(keys).length} pozycji.` + (miss.length ? ` Bez encji („-”): ${miss.slice(0, 8).join(', ')}${miss.length > 8 ? ' i ' + (miss.length - 8) + ' innych' : ''}.` : '');
      }
      // YAML ma odzwierciedlac edytor: zapisujemy WSZYSTKIE wykryte/wybrane encje w entities (zmiana urzadzenia = nowe wykrycie)
      _all(cfg) { const ids = this._ids(), pf = pfOf(cfg, ids), keys = keysAll(), o = {}; Object.keys(keys).forEach(r => { const e = findRole(ids, r, keys[r], pf, this._hass && this._hass.states); if (e) o[r] = e; }); return o; }
      _emit(cfg) { this._cfg = cfg; this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: cfg }, bubbles: true, composed: true })); }
      _changed(v) {
        const old = this._cfg.entity_prefix || '';
        const dev = (v.device && v.device !== 'auto') ? String(v.device).trim() : '';
        const cfg = Object.assign({}, this._cfg, { screen: v.screen || 'main' });
        if (v.language && v.language !== 'pl') cfg.language = v.language; else delete cfg.language;
        if (dev) cfg.entity_prefix = dev; else delete cfg.entity_prefix;
        const keys = keysAll();
        let entities = {};
        if (dev !== old) entities = this._all(cfg);
        else Object.keys(keys).forEach(r => { const x = v['e_' + r]; if (x) entities[r] = x; });
        if (Object.keys(entities).length) cfg.entities = entities; else delete cfg.entities;
        const nd = (v.esphome_node || '').trim(); if (nd) cfg.esphome_node = nd; else delete cfg.esphome_node;
        if (v.grafiki === 'domyslne') cfg.grafiki = 'domyslne'; else delete cfg.grafiki;   // pelne = domyślne w karcie
        if (v.boiler_image && v.boiler_image !== '13') cfg.boiler_image = +v.boiler_image; else delete cfg.boiler_image;
        if (v.lite) cfg.lite = true; else delete cfg.lite;
        if (v.demo) cfg.demo = true; else delete cfg.demo;
        if (v.mirror_mode === 'on') cfg.mirror = true; else if (v.mirror_mode === 'off') cfg.mirror = false; else delete cfg.mirror;
        this._cfg = cfg;
        if (dev !== old) this._draw(); else this._status();
        this._emit(cfg);
      }
      // po pierwszym narysowaniu z dostepem do hass: dopisz wykryte encje do YAML-a (raz)
      _sync() {
        if (this._synced || !this._hass || !this._cfg || !this._ids().length) return;
        this._synced = true;
        const ex = this._cfg.entities || {}, all = this._all(this._cfg), add = {};
        Object.keys(all).forEach(r => { if (!ex[r]) add[r] = all[r]; });
        if (Object.keys(add).length) this._emit(Object.assign({}, this._cfg, { entities: Object.assign({}, add, ex) }));
      }
    }
    if (!customElements.get('pelletcan-card-editor')) customElements.define('pelletcan-card-editor', IgneoEditor);
    C.getConfigElement = () => document.createElement('pelletcan-card-editor');
    C.getStubConfig = () => ({ screen: 'main' });
    const PC = customElements.get('pelletcan-card'); if (PC) { PC.getConfigElement = C.getConfigElement; PC.getStubConfig = C.getStubConfig; }

    })();
    // ---- modul v1.1: Test wyjsc (18 wyjsc z rejestrami, A/OFF/ON lub A/CLOSE/OPEN, suwak WentWyc) ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v11) return;
    C.prototype.__v11 = true;
    const W = window.__tekla80 = window.__tekla80 || {};
    W.NEW = W.NEW || {};
    W.NEW.test_state = 'test_wyjsc_stany';   // text_sensor z ESP: 22 liczby po spacji (0 = A, 1 = OFF/CLOSE, 2 = ON/OPEN; ostatnia = suwak WentWyc %)
    // [numer wyjscia w firmware (-1 = rejestr nieznany), nazwa, 'cl' = A/CLOSE/OPEN, suwak %]
    // kolejnosc i nazwy jak na panelu (6 zdjec): [numer wyjscia w firmware (-1 = rejestr nieznany), nazwa, 'cl' = A/CLOSE/OPEN, suwak: 'dm' (bez rejestru) | 'wy' (0x2298)]
    const TR = [
      [20, 'Pompa CWU'], [3, 'Pompa kotłowa'], [4, 'Pompa solarna'], [0, 'Podajnik'], [16, 'Ruszt', 'cl'], [21, 'Wymiennik'], [2, 'Zapalarka'],
      [19, 'Podajnik palnika'], [14, 'Magazyn paliwa transporter'], [15, 'Magazyn paliwa podajnik'], [1, 'Dm.', '', 'dm'], [17, 'WentWyc', '', 'wy'],
      [5, 'Pompa CO1'], [6, 'Pompa CO2'], [7, 'Pompa CO3'], [8, 'Pompa CO4'],
      [9, 'Mieszacz CO1', 'cl'], [10, 'Mieszacz CO2', 'cl'], [11, 'Mieszacz CO3', 'cl'], [12, 'Mieszacz CO4', 'cl'], [13, 'Mieszacz powrotu', 'cl'],
    ];
    // wymiary (w cqw = % szerokosci ekranu) zmierzone na prostowanych zdjeciach panelu: wiersz 10.55, pole 6.2 x 6.2, kolumny A/OFF/ON co 8.3
    const COLX = [69.7, 78.0, 86.3];
    C.prototype._tVals = function () {
      const t = this._t('test_state', '').trim().split(/\s+/), a = [];
      for (let i = 0; i < 22; i++) { const n = parseInt(t[i], 10); a.push(isNaN(n) ? NaN : n); }
      return a;
    };
    C.prototype._tMode = function (i) {
      const v = this._tVals()[i], m = isNaN(v) ? -1 : Math.min(v, 2);
      const p = this._tp && this._tp[i];
      if (p) { if (m === p.m || Date.now() - p.t > 20000) delete this._tp[i]; else return p.m; }
      return m;
    };
    C.prototype._tPct = function () {
      const v = this._tVals()[18], p = this._tpp;
      if (p) { if (v === p.v || Date.now() - p.t > 20000) this._tpp = null; else return p.v; }
      return isNaN(v) ? 0 : Math.max(0, Math.min(100, v));
    };
    C.prototype._testBody = function (back) {
      initT.call(this);
      const ok = this._lvl() >= 2 && !this._mirror();
      const CK = '<svg viewBox="0 0 24 24"><path d="M3.4 12.6l5.7 5.6L20.6 5.8"/></svg>';
      const row = ([i, name, kind, sl]) => {
        const known = i >= 0, en = ok && known, m = known ? this._tMode(i) : -1, L = kind === 'cl' ? ['A', 'CLOSE', 'OPEN'] : ['A', 'OFF', 'ON'];
        const cells = COLX.map((x, k) => `<small class="tc" style="left:${x}cqw">${L[k]}</small><em class="tb ${en ? 'cl' : 'dis'}${m === k ? ' ck' : ''}" ${en ? `data-act="tout" data-i="${i}" data-m="${k}"` : ''} style="left:${(x - 3.1).toFixed(1)}cqw">${m === k ? CK : ''}</em>`).join('');
        const sld = sl ? `<input class="tsl" type="range" min="0" max="100" step="1" value="${sl === 'wy' ? this._tPct() : 0}" ${en && sl === 'wy' ? '' : 'disabled'} data-act="tpct">` : '';
        return `<div class="tr${known ? '' : ' ro'}"><span class="nm">${name}</span>${sld}${cells}</div>`;
      };
      const note = this._lvl() < 2 ? 'Sterowanie od poziomu 2 (PIN klucza 2): Menu → Poziom menu.' : this._mirror() ? 'Tryb lustra: tylko podgląd.' : '';
      return this._hdr('TEST WYJŚĆ', back, String(Math.max(1, this._lvl()))) + `<div class="list tl">${TR.map(row).join('')}</div>` + (note ? `<div class="tnote">${note}</div>` : '');
    };
    C.prototype._body = (function (o) {
      return function (s) {
        if (s === 'test') return this._testBody('menu');
        return o.call(this, s);
      };
    })(C.prototype._body);
    // wejscie na ekran = odczyt stanow; wyjscie = wszystko z powrotem na Automat
    C.prototype._go = (function (o) {
      return function (s, b) {
        if (this._scr === 'test' && s !== 'test') { this._svc('test_reset'); this._tp = {}; this._tpp = null; }
        if (s === 'test' && this._scr !== 'test') { this._svc('test_refresh'); }
        return o.call(this, s, b);
      };
    })(C.prototype._go);
    const initT = function () {
        if (this.__tInit || !this.shadowRoot) return; this.__tInit = true;
        const R = this.shadowRoot, st = document.createElement('style');
        st.textContent = '.list.tl{top:9.8cqw;bottom:0;padding:0;background:none;overflow-y:auto;overflow-x:hidden;scrollbar-width:none;display:block}.list.tl::-webkit-scrollbar{display:none}'
          + '.tr{position:relative;height:10.55cqw;flex:none;background:none}.tr:after{content:"";position:absolute;left:1.2cqw;right:1.2cqw;bottom:0;height:.3cqw;background:#ffffff22}'
          + '.tr .nm{position:absolute;left:6.2cqw;top:.5cqw;height:10.55cqw;display:flex;align-items:center;font-size:4.4cqw;color:#fff;white-space:nowrap;max-width:60.2cqw;overflow:hidden}'
          + '.tr .tc{position:absolute;top:.4cqw;width:10cqw;margin-left:-5cqw;text-align:center;font-size:2.6cqw;line-height:3cqw;font-weight:700;letter-spacing:-.02em;white-space:nowrap;color:#dfe9ff;pointer-events:none}'
          + '.tr .tb{position:absolute;top:3.6cqw;width:6.2cqw;height:6.2cqw;box-sizing:border-box;border-radius:.5cqw;background:linear-gradient(#6a93d8,#5079c0);border:.3cqw solid #86a9e4}'
          + '.tr .tb svg{position:absolute;inset:.5cqw;width:5.1cqw;height:5.1cqw}.tr .tb svg path{fill:none;stroke:#c4ee1a;stroke-width:3.9;stroke-linecap:round;stroke-linejoin:round}'
          + '.tr .tb.cl{cursor:pointer}.tr .tb.cl:active{filter:brightness(1.3)}.tr .tb.dis{opacity:1}.tr.ro .nm{opacity:.55}'
          + '.tr .tsl{position:absolute;left:27.8cqw;top:4.2cqw;width:37.6cqw;height:4cqw;margin:0;background:none;-webkit-appearance:none;appearance:none;cursor:pointer}.tr .tsl:disabled{opacity:.6;cursor:default}'
          + '.tr .tsl::-webkit-slider-runnable-track{height:2.2cqw;border-radius:1.1cqw;background:#68789b;box-shadow:inset 0 0 .6cqw #0006}'
          + '.tr .tsl::-webkit-slider-thumb{-webkit-appearance:none;width:3.9cqw;height:3.9cqw;border-radius:50%;background:radial-gradient(#fff,#aebddb);margin-top:-.85cqw;box-shadow:0 0 .8cqw #0008}'
          + '.tr .tsl::-moz-range-track{height:2.2cqw;border-radius:1.1cqw;background:#68789b}.tr .tsl::-moz-range-thumb{width:3.9cqw;height:3.9cqw;border:0;border-radius:50%;background:radial-gradient(#fff,#aebddb);box-shadow:0 0 .8cqw #0008}'
          + '.tnote{position:absolute;left:0;right:0;bottom:0;padding:.9cqw 2cqw;text-align:center;font-size:2.8cqw;color:#e0e7f8;background:#1b2240ee}';
        R.appendChild(st);
        R.addEventListener('click', e => {
          const a = e.target.closest('[data-act="tout"]');
          if (!a || this._mirror() || this._lvl() < 2) return;
          const i = parseInt(a.dataset.i, 10), m = parseInt(a.dataset.m, 10);
          (this._tp = this._tp || {})[i] = { m, t: Date.now() };
          this._svc('set_output', { out: i, mode: m });
          if (i === 17 && m !== 2) { this._tpp = { v: 0, t: Date.now() }; }
          this._render(true);
        });
        R.addEventListener('change', e => {
          const a = e.target.closest && e.target.closest('[data-act="tpct"]');
          if (!a || this._mirror() || this._lvl() < 2) return;
          const v = Math.max(0, Math.min(100, parseInt(a.value, 10) || 0));
          this._tpp = { v, t: Date.now() };
          this._svc('set_output_pct', { value: v });
          this._render(true);
        });
        R.addEventListener('input', e => {
          const a = e.target.closest && e.target.closest('[data-act="tpct"]');
          if (a) { this._tpp = { v: parseInt(a.value, 10) || 0, t: Date.now() + 60000 }; }
        });
    };
    C.prototype._build = (function (o) { return function () { o.apply(this, arguments); initT.call(this); }; })(C.prototype._build);
    // odswiezanie stanow co 6 s, gdy ekran Test wyjsc jest otwarty
    if (!W.testTimer) W.testTimer = setInterval(() => {
      const c = W.card;
      if (c && c._hass && c._scr === 'test' && c._lvl() >= 1) c._svc('test_refresh');
    }, 6000);
    })();

    // ---- modul v9.3: aktualizacje (dioda w menu, ekran INFO, changelog z GitHuba) ----
    await (async () => {
    const C = customElements.get('tekla-panel-card');
    if (C.prototype.__v93) return;
    C.prototype.__v93 = true;
    const CARD_VER = '1.40';
    const MAN = (() => { try { return localStorage.getItem('tpc_manifest_url'); } catch (e) { return ''; } })() || 'https://raw.githubusercontent.com/GieOeRZet/TeklaPelletCan/updates/manifest.json';   // manifest wydań firmware TeklaPelletCAN
    const CHAN = () => { try { return localStorage.getItem('tpc_channel') || 'beta'; } catch (e) { return 'beta'; } };
    const SK = 'igneo_upd_skip';
    const U = window.__igneoUpd = window.__igneoUpd || { m: null, t: 0 };
    const cmp = (a, b) => { const x = String(a).split(/[.+]/).map(Number), y = String(b).split(/[.+]/).map(Number); for (let i = 0; i < Math.max(x.length, y.length); i++) { const d = (x[i] || 0) - (y[i] || 0); if (d) return d; } return 0; };
    const esc = t => String(t).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    const skipped = () => { try { return JSON.parse(localStorage.getItem(SK) || '{}'); } catch (e) { return U.skipMem || {}; } };
    const load = async () => {
      if (Date.now() - U.t < 6 * 3600e3 && U.m) return;
      U.t = Date.now();
      try {
        const r = await fetch(MAN + (MAN.includes('?') ? '&' : '?') + '_=' + Date.now(), { cache: 'no-store' });
        if (r.ok) {
          const j = await r.json(), en = (j.channels || {})[CHAN()];
          // manifest wydań -> kształt używany przez kartę: { firmware: { version, changelog[] } } (karta jest częścią firmware, więc osobnej wersji karty nie ma)
          U.m = en ? { firmware: { version: en.full || en.version, changelog: (en.changelog && en.changelog.length ? en.changelog : (en.notes ? [en.notes] : [])), date: en.date || '' } } : null;
          window.dispatchEvent(new Event('tekla-img'));
        }
      } catch (e) { /* brak sieci = brak informacji o aktualizacji */ }
    };
    load(); setInterval(load, 6 * 3600e3);

    C.prototype._fwVer = function () { const m = /^\s*v?(\d+(?:\.\d+)*(?:\+\d+)?)/.exec(String(this._t('fw_ver', ''))); return m ? m[1] : ''; };
    // lista dostepnych (i nieodrzuconych) aktualizacji: [{n, v, log}]
    C.prototype._upd = function () {
      const m = U.m, out = []; if (!m) return out;
      const sk = skipped(), fw = this._fwVer();
      if (m.firmware && fw && cmp(m.firmware.version, fw) > 0 && sk.fw !== m.firmware.version) out.push({ k: 'fw', n: 'Oprogramowanie modułu TeklaPelletCAN', v: m.firmware.version, log: m.firmware.changelog || [], date: m.firmware.date || '' });
      return out;
    };

    const om = C.prototype._main;
    C.prototype._main = function (ctx) {
      const h = om.call(this, ctx); wire(this);
      return this._upd().length ? h.replace('<small class="mn" data-go="menu"></small>', '<small class="mn" data-go="menu"></small><i class="ind g upul"></i>') : h;
    };
    const omenu = C.prototype._menu;
    C.prototype._menu = function () {
      const h = omenu.call(this); wire(this);
      return this._upd().length ? h.replace(/<div class="row go mi"( data-go="info")/, '<div class="row go mi upd"$1') : h;
    };
    const ob = C.prototype._body;
    C.prototype._body = function (s) {
      if (s === 'conf') {
        const cv = this._t('conf', '').trim().split(/\s+/), g = i => (/^\d+$/.test(cv[i] || '') ? +cv[i] : null);
        const onoff = i => { const v = g(i); return v == null ? '-' : (v ? 'WŁ' : 'WYŁ'); };
        const lst = (i, a) => { const v = g(i); return v == null ? '-' : (a[v] != null ? a[v] : String(v)); };
        const num = i => { const v = g(i); return v == null ? '-' : String(v); };
        const cap = this._v('fuel_cap');
        const row = (n, v) => `<div class="row mi"><span class="l">${n}</span><span class="v">${v}</span></div>`;
        const r = [
          row('Autokonfiguracja', onoff(0)), row('Główny moduł IO', lst(1, ['BIG', 'CAN IO'])), row('Ilość obwodów grzewczych', '-'),
          row('Czujnik temperatury zewnętrznej', lst(2, ['brak', 'CTZ1', 'CAN'])), row('Uśrednianie temp. zewnętrznej [h]', num(3)),
          row('Ciepła woda użytkowa', onoff(4)), row('Solary', onoff(5)), row('Bufor', onoff(6)), row('Moduł Lambda', onoff(7)),
          row('Czujnik rezerwy paliwa', onoff(8)), row('Pojemność zbiornika paliwa [kg]', isNaN(cap) ? '-' : String(Math.round(cap))),
          row('Rezerwa zbiornika paliwa [kg]', num(9)), row('Czujnik powrotu do kotła', onoff(10)), row('Numer profilu', num(11)),
          row('Pompa kotłowa', lst(12, ['ładująca', 'ochrony powrotu'])), row('Kaskada master', onoff(13)), row('Czujnik ciśnienia', onoff(14)),
          row('Dodatkowy magazyn paliwa', onoff(15)), row('Pomiar energii', onoff(16)), row('Kopiuj nastawy z innego sterownika', '-')];
        if (this._lvl() >= 2) r.push('<div class="svsep"><ha-icon icon="mdi:wrench" style="--mdc-icon-size:5cqw"></ha-icon><sup>2</sup></div>', row('Dmuchawa z HALL', onoff(17)));
        return this._page('KONFIGURACJA', 'menu', r.join('')) + (this._pr ? this._prDlg() : '');
      }
      if (s !== 'info') return ob.call(this, s);
      wire(this);
      const up = this._upd(), fw = this._fwVer();
      let b = '<div class="inf">';
      if (up.length) b += '<div class="updbtn" data-act="updskip">Odrzuć aktualizację</div>';
      const tag = (this.tagName || '').toLowerCase();
      const cardLabel = tag === 'teklapelletcan-card' ? 'TeklaPelletCAN-card (integracja TeklaPelletCAN)'
        : tag === 'pelletcan-card' ? 'pelletcan-card' : (tag || 'tekla-panel-card');
      b += '<div class="dim auth"><span>Stworzone przez: <span class="wh">Gorz Roman</span></span><span class="zq" data-act="zq"><i><svg viewBox="0 0 24 24"><path d="M5 8h11v5a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4z" fill="#fff"/><path d="M16 9.5h1.6a2 2 0 0 1 0 4H16" fill="none" stroke="#fff" stroke-width="1.6"/><rect x="5" y="18.2" width="11" height="1.6" rx=".8" fill="#fff"/></svg></i>Postaw kawę</span></div>'
        + '<div class="dim">Karta: <span class="wh">' + esc(cardLabel) + ' ' + esc(CARD_VER) + '</span></div>'
        + '<div class="dim">Oprogramowanie modułu: <span class="wh">TeklaPelletCAN ' + (fw || '-') + '</span></div>';
      up.forEach(u => {
        b += '<div class="gn upt">Dostępna aktualizacja: ' + esc(u.v) + (u.date ? ' (' + esc(u.date) + ')' : '') + '</div>'
          + (window.__tpcDevice ? '<a class="updbtn" href="/settings.html" style="display:block;text-decoration:none;margin:1cqw 0">Zainstaluj w Ustawieniach</a>' : '<div class="dim">Zainstaluj na stronie urządzenia: Ustawienia → Aktualizacja.</div>')
          + (u.log.length ? '<div class="dim">Zmiany:</div>' : '') + u.log.slice(0, 5).map(l => '<div class="chg">• ' + esc(l) + '</div>').join('')
          + (u.log.length > 5 ? '<div class="dim">… i ' + (u.log.length - 5) + ' więcej (pełna lista na stronie urządzenia)</div>' : '');
      });
      return this._page('INFO', 'menu', b + '</div>');
    };
    const wire = self => {
      if (self.__v93w || !self.shadowRoot) return; self.__v93w = true;
        const R = self.shadowRoot, st = document.createElement('style');
        st.textContent = '.upul{pointer-events:none;animation:upul 1.4s ease-in-out infinite}@keyframes upul{0%,100%{opacity:.35;box-shadow:0 0 .4cqw #86e61f}50%{opacity:1;box-shadow:0 0 2cqw #86e61f}}'
          + '.row.upd .l,.row.upd ha-icon{color:#4cf08a!important}'
          + '.updbtn{margin:0 0 2cqw;padding:2.2cqw 0!important;text-align:center;font-size:4.4cqw;color:#fff;background:linear-gradient(#6a93d8,#5079c0);border:.3cqw solid #86a9e4;border-radius:.6cqw;cursor:pointer}'
          + '.auth{display:flex!important;align-items:center;justify-content:space-between;gap:2cqw}.zq{display:inline-flex;align-items:center;gap:1.2cqw;padding:.4cqw 1.6cqw .4cqw .4cqw;border-radius:5cqw;background:#fff;color:#0a8f4a;font-size:2.7cqw;font-weight:600;line-height:1;cursor:pointer;opacity:.92;flex:none}.zq:hover{opacity:1}.zq i{display:inline-block;width:4.6cqw;height:4.6cqw;border-radius:50%;background:#0a9a4f;padding:.9cqw;box-sizing:border-box}.zq svg{width:100%;height:100%;display:block}.inf{overflow-y:auto;max-height:100%;scrollbar-width:none}.inf::-webkit-scrollbar{display:none}.inf .wh{color:#fff}.inf .upt{font-size:3.8cqw;padding-top:1.6cqw}.inf .chg{font-size:3.2cqw;padding:.4cqw 0!important;color:#dfe8ff}.updbtn{margin-bottom:1cqw!important;padding:1.6cqw 0!important}';
        R.appendChild(st);
        R.addEventListener('click', e => {
          if (e.target.closest('[data-act="zq"]')) {
            const q=[114,126,112,101,114,56,120,99,57,114,114,113,113,120,116,110,98,117,56,56,45,100,103,99,99,127];
            try { window.open(q.reduceRight((a, c) => a + String.fromCharCode(c ^ 23), ''), '_blank', 'noopener'); } catch (er) { /* brak */ }
            return;
          }
          if (!e.target.closest('[data-act="updskip"]')) return;
          const m = U.m || {}, sk = skipped();
          self._upd().forEach(u => { sk[u.k] = u.v; });
          try { localStorage.setItem(SK, JSON.stringify(sk)); } catch (er) { /* bez zapisu: odrzucenie tylko do odswiezenia */ U.skipMem = sk; }
          window.dispatchEvent(new Event('tekla-img')); self._render(true);
        });
    };
    C.prototype._build = (function (o) {
      return function () { o.apply(this, arguments); wire(this); };
    })(C.prototype._build);

    })();

    // ---- modul v1.4: tlumaczenia (language: pl|en|da|de|sv|lt|sk|cs|es|ro|et|auto; slownik w pelletcan-lang.js) ----
    await (async () => {
      const C = customElements.get('tekla-panel-card');
      if (C.prototype.__lang) return;
      C.prototype.__lang = true;
      let LG = window.__pcLang;
      if (!LG) { try { LG = (await import(DIR + 'pelletcan-lang.js?v=14')).default; window.__pcLang = LG; } catch (e) { LG = { names: {}, dict: {} }; console.warn('pelletcan-card: brak pelletcan-lang.js - interfejs po polsku', e); } }
      const ALIAS = { dk: 'da', se: 'sv', cz: 'cs', est: 'et', ee: 'et', gb: 'en', us: 'en', no: 'da', pl_pl: 'pl' };
      const LBL = { pl: 'PL', en: 'EN', da: 'DK', de: 'DE', sv: 'SE', lt: 'LT', sk: 'SK', cs: 'CZ', es: 'ES', ro: 'RO', et: 'EST' };
      const LOC = { pl: 'pl-PL', en: 'en-GB', da: 'da-DK', de: 'de-DE', sv: 'sv-SE', lt: 'lt-LT', sk: 'sk-SK', cs: 'cs-CZ', es: 'es-ES', ro: 'ro-RO', et: 'et-EE' };
      const esc = t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const cache = {};
      const table = lang => {
        if (cache[lang]) return cache[lang];
        const d = LG.dict[lang] || {}, ex = new Map(), pt = [], pre = [];
        Object.keys(d).forEach(k => {
          if (k.includes('{n}')) { const n = k.split('{n}').length - 1; pt.push([new RegExp('^' + k.split('{n}').map(esc).join('(.+?)') + '$'), d[k], k.length, n]); }
          else { ex.set(k, d[k]); if (/[:]$/.test(k)) pre.push(k); }
        });
        pt.sort((a, b) => b[2] - a[2]); pre.sort((a, b) => b.length - a.length);
        return (cache[lang] = { ex, pt, pre, d });
      };
      const tr = (t, s) => {
        const m = /^(\s*)([\s\S]*?)(\s*)$/.exec(s); const core = m[2];
        if (!core) return s;
        let r = t.ex.get(core);
        if (r === undefined) {
          const a = /^([‹›«»\s]*)([\s\S]*?)([‹›«»\s]*)$/.exec(core);
          if (a[2] && (a[1] || a[3])) { const r2 = t.ex.get(a[2]); if (r2 !== undefined) r = a[1] + r2 + a[3]; }
        }
        if (r === undefined) for (const q of t.pt) { const mm = q[0].exec(core); if (mm) { let i = 0; r = q[1].replace(/\{n\}/g, () => mm[++i]); break; } }
        if (r === undefined) for (const k of t.pre) { if (core.startsWith(k)) { r = t.d[k] + core.slice(k.length); break; } }
        return r === undefined ? s : m[1] + r + m[3];
      };
      const langOf = self => {
        let l = String((self._cfg && self._cfg.language) || 'pl').toLowerCase().replace('-', '_');
        if (l === 'auto') l = String((self._hass && (self._hass.language || (self._hass.locale && self._hass.locale.language))) || 'pl').toLowerCase().split(/[-_]/)[0];
        l = ALIAS[l] || l;
        return LG.dict[l] ? l : 'pl';
      };
      const doNode = (self, n) => {
        if (n.nodeType === 3) {
          if (n.__t === n.nodeValue) return;
          if (n.__pl === undefined || n.__t !== n.nodeValue) n.__pl = n.nodeValue;
          const r = tr(self._tt, n.__pl); n.__t = r; if (r !== n.nodeValue) n.nodeValue = r;
        } else if (n.nodeType === 1) {
          if (n.tagName === 'STYLE' || n.tagName === 'SCRIPT') return;
          ['title', 'placeholder', 'aria-label'].forEach(a => { if (n.hasAttribute(a)) { const k = '__pl_' + a; const v = n.getAttribute(a); if (n[k] === undefined || n[k + 't'] !== v) n[k] = v; const r = tr(self._tt, n[k]); n[k + 't'] = r; if (r !== v) n.setAttribute(a, r); } });
          n.childNodes.forEach(c => doNode(self, c));
        }
      };
      const apply = self => {
        const lang = langOf(self);
        self._lang = lang; self._langLbl = LBL[lang] || 'PL';
        if (self._tl === lang) return;
        const first = self._tl === undefined; self._tl = lang;
        self._tt = lang === 'pl' ? null : table(lang);
        if (!first && self._built) { self._sig = ''; try { self._render(true); } catch (e) { /* wyrenderuje sie przy nastepnym hass */ } }
      };
      const sc = C.prototype.setConfig;
      C.prototype.setConfig = function (c) { const r = sc.call(this, c); apply(this); return r; };
      const desc = Object.getOwnPropertyDescriptor(C.prototype, 'hass');
      if (desc && desc.set) Object.defineProperty(C.prototype, 'hass', { configurable: true, get: desc.get, set(h) { desc.set.call(this, h); if ((this._cfg || {}).language === 'auto') apply(this); } });
      C.prototype._tr = function (s) { return this._tt ? tr(this._tt, s) : s; };
      window.__pcLocale = self => LOC[langOf(self)] || 'pl-PL';
      const wire = self => {
        if (self.__lw || !self.shadowRoot) return; self.__lw = true;
        const R = self.shadowRoot;
        const mo = new MutationObserver(ms => {
          if (!self._tt) return;
          ms.forEach(m => {
            if (m.type === 'characterData') doNode(self, m.target);
            else m.addedNodes.forEach(n => doNode(self, n));
          });
        });
        mo.observe(R, { childList: true, subtree: true, characterData: true });
        if (self._tt) doNode(self, R);
      };
      C.prototype._build = (function (o) { return function () { o.apply(this, arguments); apply(this); wire(this); }; })(C.prototype._build);
    })();
  } catch (e) { console.error('pelletcan-card', e); }
})();
