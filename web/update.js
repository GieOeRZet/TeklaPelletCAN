// Aktualizacje OTA „jak w WLED”: przeglądarka (ma internet) pobiera manifest i pliki z GitHuba i wgrywa je do urządzenia.
// Urządzenie samo nie ma dostępu do internetu i weryfikuje podpis ECDSA każdego pliku – obcy firmware odrzuci.
export const MANIFEST_DEFAULT = 'https://raw.githubusercontent.com/GieOeRZet/TeklaPelletCan/updates/manifest.json';

const ls = k => { try { return localStorage.getItem(k) || ''; } catch (e) { return ''; } };
export const manifestUrl = () => ls('tpc_manifest_url') || MANIFEST_DEFAULT;
export const channel = () => ls('tpc_channel') || 'beta';

// "0.3.0+17" -> [0,3,0,17]; wersja nieznana (np. symulator) -> null
export function parseVer(s) {
  const m = /^v?(\d+)\.(\d+)\.(\d+)(?:\+(\d+))?/.exec(String(s || ''));
  return m ? [+m[1], +m[2], +m[3], +(m[4] || 0)] : null;
}
export function cmpVer(a, b) {
  for (let i = 0; i < 4; i++) if (a[i] !== b[i]) return a[i] < b[i] ? -1 : 1;
  return 0;
}

export async function fetchManifest(url = manifestUrl()) {
  const sep = url.includes('?') ? '&' : '?';
  const r = await fetch(url + sep + 't=' + Date.now(), { cache: 'no-store' });
  if (!r.ok) throw new Error('manifest: HTTP ' + r.status);
  return r.json();
}

// Zwraca { installed, entry, newer, remoteFull } albo rzuca błąd (brak internetu, brak kanału).
export async function checkUpdate(installedFw, chan = channel(), url = manifestUrl()) {
  const m = await fetchManifest(url);
  const entry = (m.channels || {})[chan];
  if (!entry) throw new Error('brak wydania w kanale „' + chan + '”');
  const installed = parseVer(installedFw) || [0, 0, 0, 0];
  const remote = parseVer(entry.full) || [0, 0, 0, 0];
  return { installed, entry, newer: cmpVer(remote, installed) > 0, remoteFull: entry.full, base: url.replace(/[^/]*$/, '') };
}

export async function downloadFirmware(entry, base, onProgress) {
  const rb = await fetch(base + entry.file + '?t=' + entry.sha256.slice(0, 8));
  if (!rb.ok) throw new Error('plik firmware: HTTP ' + rb.status);
  const total = +rb.headers.get('content-length') || entry.size || 0;
  const reader = rb.body.getReader(); const parts = []; let got = 0;
  for (;;) { const { done, value } = await reader.read(); if (done) break; parts.push(value); got += value.length; if (onProgress && total) onProgress(got / total); }
  const blob = new Blob(parts, { type: 'application/octet-stream' });
  if (entry.size && blob.size !== entry.size) throw new Error('rozmiar pliku się nie zgadza (' + blob.size + ' ≠ ' + entry.size + ')');
  const rs = await fetch(base + entry.sig + '?t=' + entry.sha256.slice(0, 8));
  if (!rs.ok) throw new Error('podpis: HTTP ' + rs.status);
  return { blob, sig: (await rs.text()).trim() };
}

// Wgranie do urządzenia (to samo co ręczne wskazanie pliku). Rozwiązuje { status, body }.
export function uploadFirmware(blob, sig, token, onProgress) {
  return new Promise((resolve, reject) => {
    const x = new XMLHttpRequest();
    x.open('POST', '/api/v1/ota');
    if (token) x.setRequestHeader('Authorization', 'Bearer ' + token);
    x.setRequestHeader('X-Signature', sig);
    x.upload.onprogress = e => { if (onProgress && e.lengthComputable) onProgress(e.loaded / e.total); };
    x.onload = () => { let b = {}; try { b = JSON.parse(x.responseText); } catch (e) { /* pusty */ } resolve({ status: x.status, body: b }); };
    x.onerror = () => reject(new Error('błąd połączenia podczas wgrywania'));
    x.send(blob);
  });
}
