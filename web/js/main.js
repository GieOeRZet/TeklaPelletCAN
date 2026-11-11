import { nat, onEvent, api } from './native.js';
import { S, LEVEL_MS, startPolling, stopPolling, subscribe, level, refreshInfo } from './store.js';
import { $, el, esc, toast, openSheet, closeSheet, pinSheet, ensureUnlocked, ensureLevel, enterLevelPin, ensurePinSetup, confirmSheet, promptSheet, callService } from './ui.js';
import * as V from './views.js';
import { fuelSheet, zasilanieSheet } from './views.js';
import { checkUpdates, dismissed, dismiss } from './updates.js';
import { getTheme, setTheme, getDefaultStyle, setDefaultStyle } from './theme.js';

// Domyslny styl interfejsu = "klasyczny" (Estyma) -> od razu przeskakujemy do repliki oryginalnego
// panelu, zamiast renderowac styl nowoczesny. Dziala identycznie w apce (przelacza WebView mostem
// natywnym) i w portalu urzadzenia (zwykle przekierowanie na classic.html). Wybor dotyczy TYLKO
// startu - z menu zawsze da sie wejsc w drugi styl ("Panel kotła (oryginał)" / linki w klasyku).
if (getDefaultStyle() === 'classic' && !location.hash.includes('/wyglad')) {
  const st0chk = nat.state();
  if (st0chk.web) location.replace('classic.html');
  else nat.openOriginal();
}

const app = $('#app');
let cur = null, unsub = null, route = '';
let tickT = null;


// ------------------------------------------------------------------ banery aktualizacji (aplikacja / firmware urządzenia)
function updateBanner(kind, info) {
  const e = info.entry;
  const title = kind === 'app' ? `Dostępna aplikacja ${esc(e.full)}` : `Dostępna aktualizacja urządzenia ${esc(e.full)}`;
  const sub = kind === 'app' ? `zainstalowana: ${esc(info.installed)}` : `zainstalowana: ${esc(info.installed || '?')}`;
  const log = (e.changelog && e.changelog.length ? e.changelog : (e.notes ? [e.notes] : [])).map(x => `<li>${esc(x)}</li>`).join('');
  const b = el(`<div class="banner upd"><b>${title}</b> <span class="dim">(${sub})</span>
    <div id="chg" style="display:none;margin-top:6px"><ul style="margin:4px 0 0;padding-left:18px">${log || '<li>brak opisu zmian</li>'}</ul></div>
    <div style="display:flex;gap:14px;margin-top:8px;flex-wrap:wrap"><u id="more">Zobacz zmiany</u>${kind === 'app' ? '<b id="get">Pobierz APK</b><u id="rel">Strona wydania</u>' : '<b id="inst">Zainstaluj w konfiguracji</b>'}<u id="no">Później</u></div></div>`);
  $('#more', b).onclick = () => { const c = $('#chg', b); c.style.display = c.style.display === 'none' ? 'block' : 'none'; };
  $('#no', b).onclick = () => { dismiss(kind, e.full); b.remove(); };
  if (kind === 'app') {
    $('#get', b).onclick = () => nat.openExternal(e.apk);
    $('#rel', b).onclick = () => nat.openExternal(e.url);
  } else {
    $('#inst', b).onclick = () => nat.openDeviceSettings();
  }
  return b;
}

/** Wstawia baner (jeśli jest nowsza wersja i nie została odłożona) na początek kontenera. */
async function showUpdateBanners(container, which) {
  try {
    const st = nat.state();
    const r = await checkUpdates({ appVersion: st.version, fwVersion: S.info && S.info.fw });
    for (const kind of which) {
      const info = r[kind];
      if (info && info.newer && dismissed(kind) !== info.entry.full && container.isConnected) container.prepend(updateBanner(kind, info));
    }
  } catch (e) { /* brak internetu – bez banera */ }
}

// ------------------------------------------------------------------ router
const TITLES = { pulpit: 'Pulpit', instalacja: 'Instalacja', harmonogram: 'Harmonogram', kociol: 'Kocioł', palnik: 'Palnik', co: 'Ogrzewanie (CO)', cwu: 'Ciepła woda (CWU)', test: 'Test wyjść', konf: 'Konfiguracja', alarmy: 'Alarmy', menu: 'Menu', params: 'Parametry' };
const NAVS = [['pulpit', '▦', 'Pulpit'], ['instalacja', '⇵', 'Instalacja'], ['harmonogram', '◷', 'Harmonogram'], ['alarmy', '⚠', 'Alarmy'], ['menu', '≡', 'Menu']];

export function go(r) { location.hash = '#/' + r; }
window.addEventListener('hashchange', render);

// Naglowek pokazuje TYLKO sesje poziomu kotla (PIN 0900/0999) - to jedyna ochrona zapisu, ktora ma sens
// pokazywac stale (ile czasu zostalo). Status "poziom menu" jako taki widac juz w Menu - nie dublujemy go
// tutaj. PIN aplikacji/odcisk palca chronia tylko start aplikacji, wiec nie maja tu oddzielnego znacznika.
function chip() {
  if (S.cachedAt || (!S.online && S.loaded === false && S.fails > 1)) return '<button class="chip off" id="chip">⏸ offline</button>';
  const left = S.levelAt ? LEVEL_MS - (Date.now() - S.levelAt) : 0;
  if (level() > 0 && left > 0) {
    const m = Math.floor(left / 60000), s = Math.floor(left / 1000) % 60;
    const sup = { 1: '¹', 2: '²' }[level()] || '';
    return `<button class="chip open" id="chip">🔓${sup} ${m}:${String(s).padStart(2, '0')}</button>`;
  }
  return '';
}

function chrome(title, body, nav) {
  app.innerHTML = '';
  // Strzalka powrotu jako SVG, nie znak "←" - ten glif rozjezdza sie (nie jest wyosiowany) w domyslnej
  // czcionce na czesci urzadzen/Androidow, przez co wyglada krzywo w okraglym przycisku .ico.
  const BACK_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>';
  // Na glownych ekranach (zakladki dolnego paska) ikona hamburgera w naglowku dublowalaby zakladke
  // "Menu" w prawym dolnym rogu (ten sam cel: go('d/menu')) - zostaje tylko dolna. Strzalka powrotu na
  // podekranach to nie duplikat (inny cel: history.back()), wiec tam ikona zostaje.
  const showHm = nav !== 'main';
  const hdr = el(`<div class="hdr${showHm ? '' : ' noicon'}">${showHm ? `<button class="ico" id="hm">${nav === 'sub' ? BACK_SVG : '☰'}</button>` : ''}<b>${esc(title)}</b><span id="chipbox">${chip()}</span></div>`);
  const sc = el('<div class="scroll"></div>');
  app.append(hdr, sc);
  if (nav === 'main') {
    const n = el(`<div class="nav">${NAVS.map(([k, i, l]) => `<button data-k="${k}" class="${route.split('/')[1] === k ? 'on' : ''}"><i>${i}</i>${l}</button>`).join('')}</div>`);
    n.querySelectorAll('button').forEach(b => b.onclick = () => go('d/' + b.dataset.k));
    app.append(n);
  }
  if ($('#hm')) $('#hm').onclick = () => nav === 'sub' ? history.back() : go('d/menu');
  bindChip();
  sc.appendChild(body);
  return sc;
}

function bindChip() {
  const c = $('#chip');
  if (!c) return;
  // widoczny tylko gdy poziom kotla aktywny (patrz chip()) - klik blokuje sesje od razu (PIN 0000, jak w oryginale)
  c.onclick = async () => {
    if (S.cachedAt) { toast('Brak połączenia z modułem – tryb podglądu ostatnich danych'); return; }
    await callService('tekla_estyma_unlock', { pin: 0 });
    S.levelAt = 0; refreshChip(); toast('Poziom kotła zablokowany');
  };
}
function refreshChip() { const b = $('#chipbox'); if (b) { b.innerHTML = chip(); bindChip(); } }

async function render() {
  const r = location.hash.replace(/^#\//, '') || 'start';
  route = r;
  if (unsub) { unsub(); unsub = null; }
  closeSheet();
  const st = nat.state();
  // PIN aplikacji pyta sie dopiero przy pierwszej probie sterowania (ensureUnlocked), nie od razu po instalacji -
  // przegladanie listy/dodawanie urzadzenia i podglad pulpitu (odczyt) dzialaja bez PIN-u.
  if (r === 'setup') return viewSetup();
  if (r === 'start') {
    // uruchomienie apki z jednym zapisanym urzadzeniem -> od razu pulpit kotla, bez listy do klikniecia
    const devices = nat.devices();
    if (devices.length === 1) { nat.selectDevice(devices[0].base, devices[0].name); go('d/pulpit'); startPolling(); return; }
    return viewDevices();
  }
  if (r === 'devices') return viewDevices();
  if (r === 'app') return viewAppSettings();
  if (r === 'wyglad') return viewAppearance();
  if (r.startsWith('d/')) {
    if (!st.deviceName) return go('devices');
    const parts = r.split('/'), page = parts[1];
    let view;
    if (page === 'pulpit') view = V.pulpit(p => go('d/' + p));
    else if (page === 'instalacja') view = V.instalacja(p => go('d/' + p));
    else if (page === 'kociol') view = V.kociol();
    else if (page === 'palnik') view = V.palnik();
    else if (page === 'co') view = V.ogrzewanie();
    else if (page === 'cwu') view = V.cieplaWoda();
    else if (page === 'test') view = V.testWyjsc();
    else if (page === 'konf') view = V.konfiguracja();
    else if (page === 'harmonogram') view = V.harmonogram();
    else if (page === 'alarmy') view = V.alarmy();
    else if (page === 'menu') return viewMenu();
    else if (page === 'params' && parts[2]) view = V.paramList(decodeURIComponent(parts[2]));
    else if (page === 'params') view = V.paramGroups(p => go('d/' + p));
    else return go('d/pulpit');
    const title = page === 'pulpit' ? (st.deviceName || 'Kocioł') : parts[2] ? decodeURIComponent(parts[2]) : (TITLES[page] || '');
    const nav = ['pulpit', 'instalacja', 'harmonogram', 'alarmy'].includes(page) ? 'main' : 'sub';
    const sc0 = chrome(title, view.node, nav);
    // 'app' tutaj tez, nie tylko 'fw': przy jednym zapisanym urzadzeniu start apki idzie prosto na pulpit
    // (patrz 'start' nizej) i viewDevices() z jej wlasnym showUpdateBanners(['app']) nigdy sie nie renderuje -
    // bez tego aktualizacja samej apki nigdy by sie nie pokazala.
    if (page === 'pulpit') setTimeout(() => showUpdateBanners(sc0, ['fw', 'app']), 1500);
    const upd = () => { view.update(); refreshChip(); };
    upd();
    unsub = subscribe(upd);
    return;
  }
  go('devices');
}

// backend dla przycisku „wstecz” z Androida: true = obsłużone w interfejsie
window.__tpcBack = () => {
  if ($('#overlay').innerHTML) { closeSheet(); return true; }
  const r = location.hash.replace(/^#\//, '');
  if (r === 'devices') { if (nat.state().deviceName) { history.back(); return true; } return false; }
  if (r === 'start' || r === 'setup' || r === '') return false;
  if (r === 'd/pulpit') { toLeave(); return true; }
  if (r.startsWith('d/') && r !== 'd/menu' && !['d/instalacja', 'd/alarmy', 'd/harmonogram'].includes(r)) { history.back(); return true; }
  if (r === 'd/menu' || r === 'app' || r === 'wyglad') { r === 'd/menu' ? go('d/pulpit') : history.back(); return true; }
  go('d/pulpit'); return true;
};
function toLeave() { go('d/menu'); }   // z pulpitu „wstecz” otwiera menu (nie zamyka aplikacji)

// ------------------------------------------------------------------ zdarzenia z aplikacji natywnej
onEvent(e => {
  if (e.type === 'locked') {
    // Zapis dziala zawsze (PIN aplikacji chroni tylko start) - to zdarzenie znaczy juz tylko, ze po
    // bezczynnosci/wyjsciu z apki zdjelismy poziom dostepu kotla (bezpiecznik, nie blokada zapisu).
    closeSheet();
    refreshChip();
    toast('Poziom kotła zablokowany' + (e.reason === 'idle' ? ' (bezczynność)' : ''));
  } else if (e.type === 'device_closed') {
    refreshChip();
    // po powrocie z konfiguracji urzadzenia (mogla tam byc instalacja aktualizacji OTA) odswiez fw i,
    // jesli jestesmy na pulpicie, przerysuj go - inaczej baner "dostepna aktualizacja" wisi do nastepnej nawigacji
    refreshInfo().then(() => { if (location.hash === '#/d/pulpit') render(); });
  }
});
setInterval(refreshChip, 1000);

// ------------------------------------------------------------------ pierwsze uruchomienie: PIN aplikacji + biometria
function viewSetup() {
  app.innerHTML = '<div class="scroll"><div class="center"><div class="big-ico">🔐</div><div class="brand">Tekla<span>PelletCAN</span></div><h2>Ustaw PIN aplikacji</h2><div class="hint" style="font-size:14px">PIN chroni sterowanie kotłem. Bez niego aplikacja działa tylko jako podgląd. Nie da się go odzyskać – jeśli go zapomnisz, trzeba wyczyścić dane aplikacji.</div><button class="btn acc" id="start">Ustaw PIN</button></div></div>';
  const flow = async () => {
    const pin1 = await pinSheet({ title: 'Nowy PIN aplikacji', sub: '4–12 cyfr' });
    if (!pin1) return;
    const pin2 = await pinSheet({ title: 'Powtórz PIN', sub: 'Wpisz ten sam PIN jeszcze raz', check: async p => (p === pin1 ? null : 'PIN-y się różnią') });
    if (!pin2) return;
    const r = nat.setupPin(pin1);
    if (!r.ok) { toast(r.error); return; }
    if (nat.state().bioAvailable) {
      app.innerHTML = '<div class="scroll"><div class="center"><div class="big-ico">☝</div><h2>Używać odcisku palca?</h2><div class="hint" style="font-size:14px">Odcisk palca będzie odblokowywał sterowanie zamiast PIN-u. Możesz to zmienić w Ustawieniach aplikacji.</div><button class="btn acc" id="yes">Włącz odcisk palca</button><button class="btn sec" id="no">Nie teraz</button></div></div>';
      await new Promise(res => { $('#yes').onclick = () => { nat.setBio(true); res(); }; $('#no').onclick = () => { nat.setBio(false); res(); }; });
    } else nat.setBio(false);
    go('devices');
  };
  $('#start').onclick = flow;
  setTimeout(flow, 0);   // od razu pokaż klawiaturę; anulowanie zostawia ekran z przyciskiem
}

// ------------------------------------------------------------------ lista urządzeń
function viewDevices() {
  // "Zmien urzadzenie" z Menu nawiguje tu z AKTYWNYM urzadzeniem - w tym przypadku NIE wylaczamy go
  // od razu (dopiero przy faktycznym wyborze nowego, patrz open() nizej - selectDevice() samo czysci
  // poprzednie), zeby "wstecz"/anulowanie wracalo do pulpitu zamiast uwiezic uzytkownika na tym ekranie
  // (system back wtedy po prostu zamykal aplikacje). Pierwsze uruchomienie (brak urzadzenia) - bez zmian.
  const cameFromActive = !!nat.state().deviceName;
  if (!cameFromActive) nat.deselect();
  stopPolling();
  let devices = nat.devices();
  const found = {};
  const save = () => nat.saveDevices(devices.map(d => ({ id: d.id, name: d.name, base: d.base })));
  const norm = s => { s = (s || '').trim().replace(/^https?:\/\//i, '').replace(/\/.*$/, ''); return /^[A-Za-z0-9.\-]+(:\d{1,5})?$/.test(s) ? 'http://' + s : ''; };
  const same = (a, b) => a.base === b.base || (a.id && b.id && a.id === b.id);
  const root = el(`<div><div class="brand" style="padding:8px 2px 0">Tekla<span>PelletCAN</span></div><div class="hint" style="margin:0 2px 10px">Sterowanie kotłem Tekla / Estyma</div>
    <div class="sec"><h5>Moje urządzenia</h5><div id="mine"></div></div>
    <div class="sec"><h5><span class="spin"></span>Znalezione w sieci</h5><div id="found"></div><button class="btn sec" id="rescan">Szukaj ponownie</button></div>
    <div class="sec"><h5>Dodaj ręcznie</h5><div style="display:flex;gap:8px"><input class="t" id="addr" inputmode="url" autocapitalize="none" placeholder="adres IP, np. 192.168.1.50"><button class="btn" id="add" style="margin:0;width:auto">Dodaj</button></div><div class="msg" id="amsg" style="text-align:left"></div></div>
    <div class="sec"><h5>Nowe urządzenie</h5><div class="hint" style="margin-bottom:8px">Pierwsze uruchomienie: połącz telefon z siecią Wi‑Fi <b>TeklaPelletCAN-XXXX</b>, potem stuknij poniżej.</div><button class="btn sec" id="setup">Konfiguruj nowe urządzenie</button></div>
    <div class="sec"><h5>Tryb demo</h5><div class="hint" style="margin-bottom:8px">Wirtualny kocioł z żywymi odczytami – bez sieci i bez kotła.</div><button class="btn acc" id="demo">Uruchom demo</button></div>
    <button class="row nav2" id="appset" style="margin-top:6px"><span>Ustawienia aplikacji</span></button></div>`);
  const sc = chrome('Urządzenia', root, cameFromActive ? 'sub' : 'none');
  if (!cameFromActive) $('#hm').style.visibility = 'hidden';
  $('#chipbox').innerHTML = '';
  showUpdateBanners(root, ['app']);
  const open = (base, name) => { nat.selectDevice(base, name); go('d/pulpit'); startPolling(); };
  const renderMine = () => {
    const box = $('#mine', root); box.innerHTML = '';
    if (!devices.length) { box.innerHTML = '<div class="hint">Brak zapisanych urządzeń. Dodaj znalezione poniżej albo wpisz adres IP.</div>'; return; }
    devices.forEach(d => {
      const b = el(`<button class="dev"><span class="dot ${d.up === true ? 'on' : d.up === false ? 'off' : ''}"></span><div class="t"><b>${esc(d.name)}</b><small>${esc(d.base.replace('http://', ''))}${d.fw ? ' · fw ' + esc(d.fw) : ''}${d.up === false ? ' · poza zasięgiem' : ''}</small></div><div class="v"><b data-b2="t"></b><br><small data-b2="s"></small></div><span class="edit">✎</span><span class="x">✕</span></button>`);
      const sm = nat.summary(d.base);
      if (sm && sm.body) {
        try {
          const st = JSON.parse(sm.body).states || [];
          const g = id => (st.find(x => x.entity_id === id) || {}).state;
          const t = parseFloat(g('sensor.tekla_kociol_temperatura'));
          $('[data-b2="t"]', b).textContent = Number.isFinite(t) ? t.toFixed(1) + '°' : '';
          $('[data-b2="s"]', b).textContent = d.up === true ? (g('sensor.tekla_palnik_stan') || '') : 'dane z ' + new Date(sm.at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) { /* bez podsumowania */ }
      }
      b.onclick = () => open(d.base, d.name);
      $('.edit', b).onclick = async ev => {
        ev.stopPropagation();
        const nn = await promptSheet({ title: 'Nazwa urządzenia', sub: 'Własna nazwa pokazywana w nagłówku aplikacji.', value: d.name, placeholder: d.name });
        if (!nn || nn === d.name) return;
        const wasActive = nat.state().deviceName === d.name;
        d.name = nn; save(); renderMine();
        if (wasActive) { nat.selectDevice(d.base, nn); render(); }   // odswieza naglowek od razu, bez przechodzenia na pulpit
      };
      $('.x', b).onclick = async ev => { ev.stopPropagation(); if (await confirmSheet('Usunąć urządzenie?', `„${esc(d.name)}” zniknie z listy.`, 'Usuń')) { devices = devices.filter(x => x !== d); save(); renderMine(); renderFound(); } };
      box.appendChild(b);
    });
  };
  const renderFound = () => {
    const box = $('#found', root); box.innerHTML = '';
    const list = Object.values(found).filter(f => !devices.some(d => same(d, f)));
    if (!list.length) { box.innerHTML = `<div class="hint">${Object.keys(found).length ? 'Wszystkie znalezione urządzenia są już na liście.' : 'Nic nie znaleziono. Upewnij się, że telefon jest w tej samej sieci Wi‑Fi co urządzenie, albo dodaj adres ręcznie.'}</div>`; return; }
    list.forEach(f => {
      const b = el(`<div class="dev"><span class="dot on"></span><div class="t"><b>${esc(f.name)}</b><small>${esc(f.base.replace('http://', ''))}${f.fw ? ' · fw ' + esc(f.fw) : ''}</small></div><button class="btn acc" style="margin:0;width:auto;padding:9px 14px">Dodaj</button></div>`);
      $('button', b).onclick = async () => {
        const nn = await promptSheet({ title: 'Nazwa urządzenia', sub: 'Jak nazwać to urządzenie? Zobaczysz tę nazwę w nagłówku aplikacji.', value: f.name, placeholder: f.name });
        const name = nn || f.name;
        devices.push({ id: f.id, name, base: f.base, fw: f.fw, up: true }); save(); open(f.base, name);
      };
      box.appendChild(b);
    });
  };
  const pingAll = () => devices.forEach((d, i) => nat.ping(String(i), d.base));
  window.tpcPing = (i, info) => {
    const d = devices[+i]; if (i.startsWith('add')) return window.__addPing && window.__addPing(i, info);
    if (!d) return; d.up = !!info; if (info) { d.fw = info.fw || d.fw; if (info.id && !d.id) { d.id = info.id; save(); } }
    renderMine();
  };
  window.tpcDiscovered = f => {
    const base = 'http://' + f.host + (f.port && f.port !== 80 ? ':' + f.port : '');
    found[base] = { id: f.id || '', name: f.id ? 'TeklaPelletCAN ' + f.id.slice(-4) : (f.name || 'TeklaPelletCAN'), base, fw: f.fw || '' };
    devices.forEach(d => { if (d.id && f.id && d.id === f.id && d.base !== base) { d.base = base; save(); } });
    renderFound(); renderMine(); pingAll();
  };
  $('#add', root).onclick = () => {
    const base = norm($('#addr', root).value), msg = t => { $('#amsg', root).textContent = t; };
    if (!base) return msg('Wpisz poprawny adres IP lub nazwę hosta.');
    if (devices.some(d => d.base === base)) return msg('To urządzenie jest już na liście.');
    msg('Sprawdzam…');
    const key = 'add' + Date.now();
    window.__addPing = async (i, info) => {
      if (i !== key) return; window.__addPing = null;
      if (!info || !info.id) return msg('Pod tym adresem nie ma urządzenia TeklaPelletCAN (brak odpowiedzi).');
      const defName = 'TeklaPelletCAN ' + info.id.slice(-4);
      const nn = await promptSheet({ title: 'Nazwa urządzenia', sub: 'Jak nazwać to urządzenie? Zobaczysz tę nazwę w nagłówku aplikacji.', value: defName, placeholder: defName });
      const name = nn || defName;
      devices.push({ id: info.id, name, base, fw: info.fw, up: true }); save(); open(base, name);
    };
    nat.ping(key, base);
  };
  $('#rescan', root).onclick = () => { Object.keys(found).forEach(k => delete found[k]); renderFound(); nat.stopDiscovery(); nat.startDiscovery(); };
  $('#setup', root).onclick = () => nat.openSetup();
  $('#demo', root).onclick = () => open('demo', 'Demo – wirtualny kocioł');
  $('#appset', root).onclick = () => go('app');
  renderMine(); renderFound(); pingAll(); nat.startDiscovery();
  const iv = setInterval(() => { if (!location.hash.includes('devices') && location.hash !== '#/start') clearInterval(iv); else pingAll(); }, 8000);
}

// ------------------------------------------------------------------ menu urządzenia
function viewMenu() {
  const st = nat.state();
  // Jak w oryginale: "Test wyjść" i "Konfiguracja modułu" sa calkowicie niewidoczne, dopoki nie wpisze
  // sie PIN-u poziomu kotla (0900/0999) w "Poziom kotła" nizej - nie tylko ich zawartosc, caly wpis w Menu.
  const unlocked1 = level() >= 1;
  const body = el(`<div><div class="sec"><h5>Widoki</h5>
    <button class="row nav2" data-go="d/pulpit"><span>Pulpit</span></button>
    <button class="row nav2" data-go="d/instalacja"><span>Instalacja</span></button>
    <button class="row nav2" data-go="d/kociol"><span>Kocioł</span></button>
    <button class="row nav2" data-go="d/palnik"><span>Palnik</span></button>
    <button class="row nav2" data-go="d/co"><span>Ogrzewanie (CO)</span></button>
    <button class="row nav2" data-go="d/cwu"><span>Ciepła woda (CWU)</span></button>
    ${unlocked1 ? '<button class="row nav2" data-go="d/konf"><span>Konfiguracja</span></button>' : ''}
    ${unlocked1 ? '<button class="row nav2" data-go="d/test"><span>Test wyjść</span></button>' : ''}
    <button class="row nav2" data-go="d/harmonogram"><span>Harmonogramy</span></button>
    <button class="row nav2" data-go="d/alarmy"><span>Alarmy i historia</span></button>
    <button class="row nav2" data-go="d/params"><span>Wszystkie parametry</span></button>
    <button class="row nav2" id="fuel"><span>Zbiornik paliwa</span></button>
    <button class="row nav2" id="pwr"><span>Zasilanie i tryby</span></button></div>
    <div class="sec"><h5>Dostęp</h5>
    <button class="row nav2" id="lvl"><span>Poziom kotła (PIN)</span><span class="v" id="lvv"></span></button></div>
    <div class="sec"><h5>Urządzenie</h5>
    <button class="row nav2" id="orig"><span>Panel kotła (oryginał)</span></button>
    <button class="row nav2" id="cfg"><span>Konfiguracja modułu</span></button>
    ${st.web ? '' : '<button class="row nav2" data-go="devices"><span>Zmień urządzenie</span></button>'}</div>
    <div class="sec"><h5>Wygląd</h5><button class="row nav2" data-go="wyglad"><span>Motyw i styl interfejsu</span></button></div>
    ${st.web ? '' : '<div class="sec"><h5>Aplikacja</h5><button class="row nav2" data-go="app"><span>Ustawienia aplikacji</span></button></div>'}
    <div class="hint" style="text-align:center">${st.web ? '' : 'Aplikacja ' + esc(st.version) + ' · '}firmware ${esc(S.info.fw || '?')}</div></div>`);
  const sc = chrome('Menu', body, 'main');
  $('#lvv', body).textContent = level() > 0 ? 'poziom ' + level() : 'poziom 0';
  body.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  $('#lvl', body).onclick = async () => { if (await enterLevelPin()) { toast('Poziom kotła ' + level()); $('#lvv', body).textContent = 'poziom ' + level(); } };
  $('#fuel', body).onclick = fuelSheet;
  $('#pwr', body).onclick = zasilanieSheet;
  // PIN aplikacji chroni tylko start apki - otwarcie oryginalu/konfiguracji nie wymaga PIN-u.
  $('#orig', body).onclick = () => nat.openOriginal();
  const cfgBtn = $('#cfg', body); if (cfgBtn) cfgBtn.onclick = () => nat.openDeviceSettings();
  unsub = subscribe(() => {
    refreshChip();
    const l = $('#lvv', body); if (l) l.textContent = 'poziom ' + level();
    if ((level() >= 1) !== unlocked1) render();   // "Test wyjść"/"Konfiguracja" pojawiaja/chowaja sie od razu
  });
}

// ------------------------------------------------------------------ wyglad (motyw + domyslny styl)
function viewAppearance() {
  const st = nat.state();
  const themeNow = getTheme();
  const styleNow = getDefaultStyle();
  const chipRow = (id, opts, cur) => `<div class="chips" id="${id}">${opts.map(([k, l]) => `<button data-k="${k}" class="${cur === k ? 'on' : ''}">${esc(l)}</button>`).join('')}</div>`;
  const body = el(`<div>
    <div class="sec"><h5>Motyw</h5><div class="hint" style="margin-bottom:6px">Dotyczy tego, nowoczesnego stylu interfejsu (nie karty klasycznej).</div>
      ${chipRow('thm', [['dark', 'Ciemny'], ['light', 'Jasny'], ['auto', 'Systemowy']], themeNow)}</div>
    ${st.web ? '' : `<div class="sec"><h5>Domyślny styl</h5><div class="hint" style="margin-bottom:6px">Który interfejs otwiera się przy starcie aplikacji. Drugi zawsze dostępny z Menu.</div>
      ${chipRow('sty', [['modern', 'Nowoczesny'], ['classic', 'Estyma']], styleNow)}</div>`}</div>`);
  chrome('Wygląd', body, 'sub');
  $('#thm', body).querySelectorAll('button').forEach(b => b.onclick = () => {
    setTheme(b.dataset.k);
    $('#thm', body).querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
  });
  const styBox = $('#sty', body);
  if (styBox) styBox.querySelectorAll('button').forEach(b => b.onclick = () => {
    setDefaultStyle(b.dataset.k);
    styBox.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
    if (b.dataset.k === 'classic') nat.openOriginal();
  });
}

// ------------------------------------------------------------------ ustawienia aplikacji
function viewAppSettings() {
  const st = nat.state();
  const body = el(`<div>
    <div class="sec"><h5>Bezpieczeństwo</h5>
      <button class="row nav2" id="chpin"><span>Zmień PIN aplikacji</span></button>
      <div class="sw"><span>Odcisk palca zamiast PIN-u<div class="hint">${st.bioAvailable ? 'Odblokowuje uruchomienie aplikacji' : 'Brak skonfigurowanej biometrii w telefonie'}</div></span><button class="tg ${st.bio ? 'on' : ''}" id="bio" ${st.bioAvailable ? '' : 'disabled'}></button></div>
      <div class="sw"><span>Blokuj aplikację przy uruchomieniu<div class="hint">Wymaga PIN-u/odcisku tylko przy starcie aplikacji - sterowanie kotłem działa bez PIN-u</div></span><button class="tg ${st.lockOnStart ? 'on' : ''}" id="los"></button></div></div>
    <div class="sec"><h5>Tryb demo</h5><div class="hint" style="margin-bottom:8px">Wirtualny kocioł z żywymi odczytami – bez sieci i bez modułu. Przełącza bieżący widok; zapisane urządzenie zostaje na liście.</div><button class="btn acc" id="demo">Uruchom demo</button></div>
    <div class="sec"><h5>Dane</h5><button class="row nav2" id="cc"><span>Wyczyść zapisane odczyty</span></button></div>
    <div class="sec"><h5>Aplikacja</h5><div class="row"><span>Wersja</span><span class="v">${esc(st.version)}</span></div>
      <div class="row"><span>Najnowsza</span><span class="v" id="latest">…</span></div><div id="updbox"></div>
      <button class="row nav2" id="chk"><span>Sprawdź aktualizacje</span></button>
      <button class="row nav2" id="rel"><span>Wydania na GitHubie</span></button></div>
    <div class="sec"><h5>Zapomniany PIN</h5><div class="hint">PIN nie da się odzyskać. Usunięcie PIN-u kasuje ustawienia bezpieczeństwa i wymaga ustawienia nowego.</div><button class="btn err" id="rst">Usuń PIN i ustawienia bezpieczeństwa</button></div></div>`);
  chrome('Ustawienia aplikacji', body, 'sub');
  $('#chpin', body).onclick = async () => {
    const old = await pinSheet({ title: 'Obecny PIN', sub: 'Podaj obecny PIN aplikacji', check: async p => { const r = nat.unlockPin(p); return r.ok ? null : (r.lockedUntil ? `Za dużo prób. Za ${Math.ceil(r.waitMs / 1000)} s` : `Zły PIN (pozostało prób: ${r.attemptsLeft})`); } });
    if (!old) return;
    const n1 = await pinSheet({ title: 'Nowy PIN', sub: '4–12 cyfr' }); if (!n1) return;
    const n2 = await pinSheet({ title: 'Powtórz nowy PIN', check: async p => (p === n1 ? null : 'PIN-y się różnią') }); if (!n2) return;
    const r = nat.changePin(old, n1); toast(r.ok ? 'PIN zmieniony' : (r.error || 'Nie udało się zmienić PIN-u'));
  };
  const tgl = (id, fn) => { const b = $(id, body); b.onclick = () => { b.classList.toggle('on'); fn(b.classList.contains('on')); }; };
  tgl('#bio', on => nat.setBio(on)); tgl('#los', on => nat.setLockOnStart(on));
  $('#cc', body).onclick = async () => { if (await confirmSheet('Wyczyścić zapisane odczyty?', 'Po wyjściu z domowej sieci aplikacja nie pokaże ostatnich danych, dopóki nie połączy się z urządzeniem.', 'Wyczyść')) { nat.clearCache(); toast('Wyczyszczono'); } };
  $('#demo', body).onclick = () => { nat.selectDevice('demo', 'Demo – wirtualny kocioł'); go('d/pulpit'); startPolling(); };
  $('#rel', body).onclick = () => nat.openExternal('https://github.com/GieOeRZet/TeklaPelletCan/releases');
  const check = async force => {
    $('#latest', body).textContent = '…';
    try {
      const r = await checkUpdates({ appVersion: st.version, fwVersion: S.info && S.info.fw, force });
      const a = r.app;
      $('#latest', body).textContent = a ? a.entry.full : 'brak danych';
      $('#updbox', body).innerHTML = '';
      if (a && a.newer) $('#updbox', body).appendChild(updateBanner('app', a)); else if (a) $('#latest', body).textContent = a.entry.full + ' (masz najnowszą)';
    } catch (e) { $('#latest', body).textContent = 'brak internetu'; }
  };
  $('#chk', body).onclick = () => check(true);
  check(false);
  $('#rst', body).onclick = async () => { if (await confirmSheet('Usunąć PIN?', 'Zostanie usunięty PIN i ustawienia biometrii. Aplikacja poprosi o nowy PIN.', 'Usuń')) { nat.resetSecurity(); go('setup'); } };
}

// ------------------------------------------------------------------ start
const st0 = nat.state();
if (!location.hash) location.hash = '#/start'; else render();
if (st0.hasPin && st0.lockOnStart && !st0.unlocked) setTimeout(() => ensureUnlocked(), 100);
window.__tpcReady = true;
