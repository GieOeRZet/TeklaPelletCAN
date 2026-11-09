// Cienka warstwa nad mostem natywnym (TPCNative): żądania API do wybranego urządzenia, blokada zapisu, urządzenia.
const N = window.TPCNative;
let seq = 0;
const pending = new Map();
const listeners = new Set();

window.__tpcResp = (id, o) => { const p = pending.get(id); if (p) { pending.delete(id); p(o); } };
window.__tpcEvent = e => listeners.forEach(fn => { try { fn(e); } catch (err) { /* ignoruj */ } });
export const onEvent = fn => { listeners.add(fn); return () => listeners.delete(fn); };

/** Żądanie do urządzenia: { status, json, body, cachedAt }. status 0 = brak odpowiedzi mostu. */
export function api(method, pathQuery, bodyObj) {
  return new Promise(resolve => {
    const id = 'r' + (++seq);
    const t = setTimeout(() => { pending.delete(id); resolve({ status: 0, json: {}, body: '', cachedAt: 0 }); }, 20000);
    pending.set(id, o => {
      clearTimeout(t);
      let json = {}; try { json = JSON.parse(o.body); } catch (e) { /* nie JSON */ }
      resolve({ status: o.status, json, body: o.body, cachedAt: o.cachedAt || 0, ctype: o.ctype });
    });
    N.request(id, method, pathQuery, bodyObj === undefined ? '' : JSON.stringify(bodyObj));
  });
}

const j = s => { try { return JSON.parse(s); } catch (e) { return {}; } };
export const nat = {
  state: () => j(N.state()),
  devices: () => { try { return JSON.parse(N.getDevices()); } catch (e) { return []; } },
  saveDevices: list => N.saveDevices(JSON.stringify(list)),
  ping: (id, base) => N.ping(id, base),
  startDiscovery: () => N.startDiscovery(),
  stopDiscovery: () => N.stopDiscovery(),
  selectDevice: (base, name) => N.selectDevice(base, name),
  deselect: () => N.deselect(),
  setupPin: pin => j(N.setupPin(pin)),
  changePin: (a, b) => j(N.changePin(a, b)),
  unlockPin: pin => j(N.unlockPin(pin)),
  unlockBio: () => N.unlockBio(),
  lock: () => N.lock(),
  setBio: on => N.setBio(on),
  setLockOnStart: on => N.setLockOnStart(on),
  clearCache: () => N.clearCache(),
  resetSecurity: () => N.resetSecurity(),
  openOriginal: () => N.openOriginal(),
  openDeviceSettings: () => N.openDeviceSettings(),
  openSetup: () => N.openSetup(),
  openExternal: url => N.openExternalUrl(url),
  summary: base => j(N.deviceSummary(base)),
};
