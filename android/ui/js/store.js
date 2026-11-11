// Stan urządzenia: stany encji (odpytywane co 2 s), opis punktów, konfiguracja; wartości z pamięci, gdy urządzenie jest poza zasięgiem.
import { api } from './native.js';

export const S = { states: new Map(), byId: new Map(), points: [], pointById: new Map(), info: {}, config: {}, cachedAt: 0, online: false, loaded: false, fails: 0, levelAt: 0 };
export const LEVEL_MS = 300000;   // sesja poziomu kotla (PIN 0900/0999) - tyle samo co w oryginalnej karcie
const subs = new Set();
export const subscribe = fn => { subs.add(fn); return () => subs.delete(fn); };
let timer = null;

export const v = id => { const s = S.states.get(id); return s ? s.state : undefined; };
export const num = id => { const x = parseFloat(v(id)); return Number.isFinite(x) ? x : NaN; };
export const level = () => { const x = num('sensor.tekla_poziom_dostepu'); return Number.isFinite(x) ? x : 0; };
// Role skonsolidowane w grupy (patrz AttrGroup w firmware/engine.cpp): encja osobna nie istnieje juz w
// odczycie, wartosc jest atrybutem encji grupy - ta sama mapa co w teklapelletcan-modern-card.js (GROUP_OF).
const GROUP_OF = {
  p_prefeed: 'palnik_nastawy_p1', p_feed_max: 'palnik_nastawy_p1', p_photo: 'palnik_nastawy_p1', p_blow_ign: 'palnik_nastawy_p1',
  p_blow_glow: 'palnik_nastawy_p1', p_blow_stop: 'palnik_nastawy_p1', p_glow_time: 'palnik_nastawy_p1', p_glow_fuel: 'palnik_nastawy_p1',
  p_stop_time: 'palnik_nastawy_p1', p_lambda: 'palnik_nastawy_p1', p_o2_30: 'palnik_nastawy_p1', p_o2_100: 'palnik_nastawy_p1',
  p_cleans: 'palnik_nastawy_p1', p_clean_gap: 'palnik_nastawy_p1', p_pause_time: 'palnik_nastawy_p1', p_pause_power: 'palnik_nastawy_p1',
  p_pause_blow: 'palnik_nastawy_p1',
  p_inertia: 'palnik_nastawy_p2', p_grate_time: 'palnik_nastawy_p2', p_burner_feed: 'palnik_nastawy_p2', p_feeder_period: 'palnik_nastawy_p2',
  p_min_rpm: 'palnik_nastawy_p2',
  co1_calib: 'co1_krzywa_p0', co1_curve_0: 'co1_krzywa_p0', co1_curve_10: 'co1_krzywa_p0', co1_curve_m20: 'co1_krzywa_p0',
  co1_hyst: 'co1_krzywa_p0', co1_mode: 'co1_krzywa_p0',
  co1_co_sensor: 'co1_krzywa_p1', co1_const_pump: 'co1_krzywa_p1', co1_corr: 'co1_krzywa_p1', co1_lower: 'co1_krzywa_p1',
  co1_mixer_time: 'co1_krzywa_p1', co1_out_comf: 'co1_krzywa_p1', co1_out_eco: 'co1_krzywa_p1', co1_pump_min: 'co1_krzywa_p1',
  co1_ret_protect: 'co1_krzywa_p1', co1_room_sensor: 'co1_krzywa_p1', co1_source: 'co1_krzywa_p1', co1_src_inc: 'co1_krzywa_p1',
  co1_tmax: 'co1_krzywa_p1',
  air_corr: 'kociol_konf_p0', power_min: 'kociol_konf_p0', power_max: 'kociol_konf_p0', fuel_heat: 'kociol_konf_p0',
  fuel_test: 'kociol_konf_p0', boiler_hyst_on: 'kociol_konf_p0', boiler_hyst_off: 'kociol_konf_p0',
  boiler_mixer_time: 'kociol_konf_p1', boiler_pump_min: 'kociol_konf_p1', boiler_ret_min: 'kociol_konf_p1',
  boil_fuel_reserve: 'kociol_konf_p1', boil_pump_run: 'kociol_konf_p1', k_predose_g: 'kociol_konf_p1',
  k_egt_min: 'kociol_konf_p1', k_egt_max: 'kociol_konf_p1', k_exch_int: 'kociol_konf_p1',
  k_nominal: 'kociol_konf_p2',
  fan_mod_1: 'palnik_krzywe_p1', fan_mod_2: 'palnik_krzywe_p1', fan_mod_3: 'palnik_krzywe_p1', fan_mod_4: 'palnik_krzywe_p1',
  fan_mod_5: 'palnik_krzywe_p1', exh_c1: 'palnik_krzywe_p1', exh_c2: 'palnik_krzywe_p1', exh_c3: 'palnik_krzywe_p1',
  exh_c4: 'palnik_krzywe_p1', exh_c5: 'palnik_krzywe_p1',
  cwu_hyst: 'cwu_konf_p0', cwu_boost: 'cwu_konf_p0', cwu_prio: 'cwu_konf_p0', cwu_legion: 'cwu_konf_p0',
  cwu_src: 'cwu_konf_p1', cwu_src_inc: 'cwu_konf_p1', cwu_delta: 'cwu_konf_p1', cwu_tmax: 'cwu_konf_p1',
  alarm_snd: 'alarm_konf_p1', alarm_sil_from: 'alarm_konf_p1', alarm_sil_to: 'alarm_konf_p1',
};
/** Wartość punktu po jego id z opisu punktów (np. "boiler_temp"). Dla punktow skonsolidowanych w grupe
 *  (patrz GROUP_OF) czyta atrybut encji grupy, gdy wlasna encja juz nie istnieje. */
export const pv = pid => {
  const s = S.byId.get(pid);
  if (s) return s.state;
  const g = GROUP_OF[pid];
  if (g) { const gs = S.byId.get(g); if (gs && gs.attributes && gs.attributes[pid] !== undefined) return gs.attributes[pid]; }
  return undefined;
};
export const pn = pid => { const x = parseFloat(pv(pid)); return Number.isFinite(x) ? x : NaN; };

// Watek wywolan do /api/v1/states (odpytywanie co 2 s + recznie wymuszone pullNow() np. po PIN-ie) moga
// nachodzic na siebie - starsze zapytanie (np. z poprzedniego ticku) moze wrocic PO nowszym (np. przy
// wolniejszej/przeciazonej sieci/CAN) i nadpisac swiezy stan (np. poziom dostepu zaraz po odblokowaniu)
// stara wartoscia. Numer seryjny odrzuca taka spozniona, nieaktualna odpowiedz.
let pullSeq = 0;
async function pull() {
  const seq = ++pullSeq;
  const r = await api('GET', '/api/v1/states');
  if (seq !== pullSeq) return;   // przyszla pozniejsza odpowiedz w miedzyczasie - ta jest nieaktualna
  if (r.status === 200 && Array.isArray(r.json.states)) {
    const m = new Map(), b = new Map();
    for (const s of r.json.states) { m.set(s.entity_id, s); if (s.id) b.set(s.id, s); }
    S.states = m; S.byId = b; S.cachedAt = r.cachedAt || 0; S.online = !r.cachedAt; S.loaded = true; S.fails = 0;
  } else {
    S.fails++; S.online = false;
  }
  subs.forEach(fn => { try { fn(); } catch (e) { /* widok odświeży się następnym razem */ } });
}

export async function startPolling() {
  stopPolling();
  S.loaded = false; S.states = new Map(); S.byId = new Map(); S.cachedAt = 0; S.online = false; S.fails = 0;
  const [pts, info, cfg] = await Promise.all([api('GET', '/api/v1/points'), api('GET', '/api/v1/info'), api('GET', '/api/v1/config')]);
  if (pts.status === 200) { S.points = pts.json.points || []; S.pointById = new Map(S.points.map(p => [p.id, p])); }
  if (info.status === 200) {
    S.info = info.json;
    // ESP nie ma internetu ani RTC: aplikacja ustawia mu zegar przy każdym otwarciu (znaczniki czasu w dzienniku/alarmach)
    if (!info.cachedAt && Array.isArray(info.json.features) && info.json.features.includes('time')) api('POST', '/api/v1/time', { epoch_ms: Date.now() });
  }
  if (cfg.status === 200) S.config = cfg.json;
  await pull();
  timer = setInterval(pull, 2000);
}
export function stopPolling() { if (timer) clearInterval(timer); timer = null; }
export const refreshSoon = () => setTimeout(pull, 450);
export const pullNow = pull;

/** Doczytuje /api/v1/info (wersja firmware itp.) bez czekania na kolejny cykl pull() – wolniej zmienne niz
 * stany, ale musi sie odswiezyc np. zaraz po aktualizacji OTA (strona konfiguracji zamknieta), zeby baner
 * "dostepna aktualizacja" zniknal od razu, a nie dopiero po ponownym wybraniu urzadzenia. */
export async function refreshInfo() {
  const info = await api('GET', '/api/v1/info');
  if (info.status === 200) { S.info = info.json; subs.forEach(fn => { try { fn(); } catch (e) { /* widok odswiezy sie nastepnym razem */ } }); }
}
