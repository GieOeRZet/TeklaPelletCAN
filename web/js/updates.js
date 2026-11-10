// Sprawdzanie aktualizacji: manifest z gałęzi `updates` (ten sam, z którego korzysta strona urządzenia). Telefon ma internet, urządzenie nie.
export const MANIFEST = 'https://raw.githubusercontent.com/GieOeRZet/TeklaPelletCan/updates/manifest.json';
const ls = k => { try { return localStorage.getItem(k) || ''; } catch (e) { return ''; } };
const setLs = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* ignoruj */ } };

export function parseVer(s) {
  const m = /^v?(\d+)\.(\d+)\.(\d+)(?:\+(\d+))?/.exec(String(s || ''));
  return m ? [+m[1], +m[2], +m[3], +(m[4] || 0)] : null;
}
export function cmpVer(a, b) { for (let i = 0; i < 4; i++) if (a[i] !== b[i]) return a[i] < b[i] ? -1 : 1; return 0; }

let memo = null;
/** Zwraca { app, fw } – każde: { entry, newer, installed } albo null (brak danych). Wynik pamiętany 6 h (force = pomiń). */
export async function checkUpdates({ appVersion, fwVersion, force = false } = {}) {
  const cached = memo || (() => { try { return JSON.parse(ls('tpc_upd_cache') || 'null'); } catch (e) { return null; } })();
  let m = cached && !force && Date.now() - cached.at < 6 * 3600 * 1000 ? cached.m : null;
  if (!m) {
    const r = await fetch(MANIFEST + '?t=' + Date.now(), { cache: 'no-store' });
    if (!r.ok) throw new Error('manifest: HTTP ' + r.status);
    m = await r.json();
    memo = { m, at: Date.now() };
    setLs('tpc_upd_cache', JSON.stringify(memo));
  }
  const out = { app: null, fw: null };
  const a = m.app, f = (m.channels || {}).stable;
  if (a && appVersion) { const i = parseVer(appVersion), r = parseVer(a.full); if (i && r) out.app = { entry: a, newer: cmpVer(r, i) > 0, installed: appVersion }; }
  if (f && fwVersion) { const i = parseVer(fwVersion), r = parseVer(f.full); if (i && r) out.fw = { entry: f, newer: cmpVer(r, i) > 0, installed: fwVersion }; }
  return out;
}

export const dismissed = key => ls('tpc_dismiss_' + key);
export const dismiss = (key, ver) => setLs('tpc_dismiss_' + key, ver);
