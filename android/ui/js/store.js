// Stan urządzenia: stany encji (odpytywane co 2 s), opis punktów, konfiguracja; wartości z pamięci, gdy urządzenie jest poza zasięgiem.
import { api } from './native.js';

export const S = { states: new Map(), byId: new Map(), points: [], pointById: new Map(), info: {}, config: {}, cachedAt: 0, online: false, loaded: false, fails: 0 };
const subs = new Set();
export const subscribe = fn => { subs.add(fn); return () => subs.delete(fn); };
let timer = null;

export const v = id => { const s = S.states.get(id); return s ? s.state : undefined; };
export const num = id => { const x = parseFloat(v(id)); return Number.isFinite(x) ? x : NaN; };
export const level = () => { const x = num('sensor.tekla_poziom_dostepu'); return Number.isFinite(x) ? x : 0; };
/** Wartość punktu po jego id z opisu punktów (np. "boiler_temp"). */
export const pv = pid => { const s = S.byId.get(pid); return s ? s.state : undefined; };
export const pn = pid => { const x = parseFloat(pv(pid)); return Number.isFinite(x) ? x : NaN; };

async function pull() {
  const r = await api('GET', '/api/v1/states');
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
