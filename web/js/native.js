// Webowa wersja mostu natywnego (zamiast js/native.js z android/ui, ktory mowi do mostu JNI/Kotlina).
// Portal urzadzenia jest serwowany przez samo urzadzenie, wiec zamiast API Androida uzywamy zwyklego
// fetch() na ten sam adres. Odczyty (/api/v1/states, /points, /config, /info) sa otwarte; zapisy czasem
// wymagaja tokenu (gdy panel WWW nie jest w trybie otwartym) - przy 401 parujemy przegladarke haslem
// urzadzenia (jak stara karta w web/shim.js) i zapamietujemy token w localStorage tej przegladarki.
const token = {
  get: () => { try { return localStorage.getItem('tpc_token') || ''; } catch (e) { return ''; } },
  set: v => { try { localStorage.setItem('tpc_token', v); } catch (e) { /* ignoruj */ } },
};
function clientId() {
  let id; try { id = localStorage.getItem('tpc_client_id'); } catch (e) { /* ignoruj */ }
  if (!id) { id = 'web-' + Math.random().toString(16).slice(2) + Date.now().toString(16); try { localStorage.setItem('tpc_client_id', id); } catch (e) { /* ignoruj */ } }
  return id;
}

async function raw(method, pathQuery, bodyObj) {
  const headers = {};
  const t = token.get(); if (t) headers.Authorization = 'Bearer ' + t;
  if (bodyObj !== undefined) headers['Content-Type'] = 'application/json';
  let r;
  try { r = await fetch(pathQuery, { method, headers, body: bodyObj === undefined ? undefined : JSON.stringify(bodyObj), cache: 'no-store' }); }
  catch (e) { return { status: 0, json: {}, body: '' }; }
  const body = await r.text().catch(() => '');
  let json = {}; try { json = JSON.parse(body); } catch (e) { /* nie JSON */ }
  return { status: r.status, json, body };
}

async function pair() {
  const info = (await raw('GET', '/api/v1/info')).json;
  const pw = (window.prompt(info.password_set ? 'Hasło urządzenia:' : 'Ustaw hasło urządzenia (min. 4 znaki). Będzie potrzebne do sterowania kotłem:') || '').trim();
  if (!pw) return false;
  if (!info.password_set) { const r = await raw('POST', '/api/v1/password', { password: pw }); if (r.status !== 200) return false; }
  const r = await raw('POST', '/api/v1/pair', { password: pw, client_id: clientId(), name: 'Przeglądarka' });
  if (r.status !== 200 || !r.json.token) return false;
  token.set(r.json.token);
  return true;
}

export const onEvent = () => () => {};

export async function api(method, pathQuery, bodyObj) {
  let r = await raw(method, pathQuery, bodyObj);
  if (r.status === 401 || (r.status === 403 && r.json.error === 'setup_required' && pathQuery.startsWith('/api/v1/call'))) {
    if (await pair()) r = await raw(method, pathQuery, bodyObj);
  }
  return { status: r.status, json: r.json, body: r.body, cachedAt: 0 };
}

const noop = () => {};
export const nat = {
  state: () => ({ hasPin: false, bio: false, bioAvailable: false, lockOnStart: false, unlocked: true, deviceName: 'Kocioł', demo: false, version: 'web', sdk: 0, web: true }),
  devices: () => [{ id: 'self', name: '', base: '' }],
  saveDevices: noop, ping: noop, startDiscovery: noop, stopDiscovery: noop,
  selectDevice: noop, deselect: noop,
  setupPin: () => ({ ok: true, error: '' }), changePin: () => ({ ok: true, error: '' }), unlockPin: () => ({ ok: true }),
  unlockBio: noop, lock: noop, setBio: noop, setLockOnStart: noop,
  clearCache: noop, resetSecurity: noop,
  openOriginal: () => { location.href = 'classic.html'; },
  openDeviceSettings: () => { location.href = 'settings.html'; },
  openSetup: noop,
  openExternal: url => window.open(url, '_blank', 'noopener'),
  summary: () => ({}),
};
