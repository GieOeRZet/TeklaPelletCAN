import { nat, onEvent, api } from './native.js';
import { S, startPolling, stopPolling, subscribe, level } from './store.js';
import { $, el, esc, toast, openSheet, closeSheet, pinSheet, ensureUnlocked, ensureLevel, confirmSheet } from './ui.js';
import * as V from './views.js';

const app = $('#app');
let cur = null, unsub = null, route = '';
let tickT = null;

// ------------------------------------------------------------------ router
const TITLES = { pulpit: 'Pulpit', instalacja: 'Instalacja', kociol: 'Nastawy', alarmy: 'Alarmy', menu: 'Menu', params: 'Parametry' };
const NAVS = [['pulpit', '▦', 'Pulpit'], ['instalacja', '⇵', 'Instalacja'], ['alarmy', '⚠', 'Alarmy'], ['menu', '≡', 'Menu']];

export function go(r) { location.hash = '#/' + r; }
window.addEventListener('hashchange', render);

function chip() {
  const st = nat.state();
  if (S.cachedAt || (!S.online && S.loaded === false && S.fails > 1)) return '<button class="chip off" id="chip">⏸ offline</button>';
  if (st.unlocked) {
    const m = Math.floor(st.remainingMs / 60000), s = Math.floor(st.remainingMs / 1000) % 60;
    return `<button class="chip open" id="chip">🔓 ${m}:${String(s).padStart(2, '0')}${level() > 0 ? ' · P' + level() : ''}</button>`;
  }
  return '<button class="chip" id="chip">🔒 tylko odczyt</button>';
}

function chrome(title, body, nav) {
  app.innerHTML = '';
  const hdr = el(`<div class="hdr"><button class="ico" id="hm">${nav === 'sub' ? '←' : '☰'}</button><b>${esc(title)}</b><span id="chipbox">${chip()}</span></div>`);
  const sc = el('<div class="scroll"></div>');
  app.append(hdr, sc);
  if (nav === 'main') {
    const n = el(`<div class="nav">${NAVS.map(([k, i, l]) => `<button data-k="${k}" class="${route.split('/')[1] === k ? 'on' : ''}"><i>${i}</i>${l}</button>`).join('')}</div>`);
    n.querySelectorAll('button').forEach(b => b.onclick = () => go('d/' + b.dataset.k));
    app.append(n);
  }
  $('#hm').onclick = () => nav === 'sub' ? history.back() : go('d/menu');
  bindChip();
  sc.appendChild(body);
  return sc;
}

function bindChip() {
  const c = $('#chip');
  if (!c) return;
  c.onclick = async () => {
    const st = nat.state();
    if (S.cachedAt) { toast('Brak połączenia z urządzeniem – tryb podglądu ostatnich danych'); return; }
    if (st.unlocked) { nat.lock(); refreshChip(); toast('Sterowanie zablokowane'); }
    else { if (await ensureUnlocked()) { refreshChip(); toast('Sterowanie odblokowane na 5 min'); } }
  };
}
function refreshChip() { const b = $('#chipbox'); if (b) { b.innerHTML = chip(); bindChip(); } }

async function render() {
  const r = location.hash.replace(/^#\//, '') || 'start';
  route = r;
  if (unsub) { unsub(); unsub = null; }
  closeSheet();
  const st = nat.state();
  if (!st.hasPin && r !== 'setup') return go('setup');
  if (r === 'setup') return viewSetup();
  if (r === 'start' || r === 'devices') return viewDevices();
  if (r === 'app') return viewAppSettings();
  if (r.startsWith('d/')) {
    if (!st.deviceName) return go('devices');
    const parts = r.split('/'), page = parts[1];
    let view;
    if (page === 'pulpit') view = V.pulpit(p => go('d/' + p));
    else if (page === 'instalacja') view = V.instalacja(p => go('d/' + p));
    else if (page === 'kociol') view = V.kociol();
    else if (page === 'alarmy') view = V.alarmy();
    else if (page === 'menu') return viewMenu();
    else if (page === 'params' && parts[2]) view = V.paramList(decodeURIComponent(parts[2]));
    else if (page === 'params') view = V.paramGroups(p => go('d/' + p));
    else return go('d/pulpit');
    const title = page === 'pulpit' ? (st.deviceName || 'Kocioł') : parts[2] ? decodeURIComponent(parts[2]) : (TITLES[page] || '');
    const nav = ['pulpit', 'instalacja', 'alarmy'].includes(page) ? 'main' : 'sub';
    chrome(title, view.node, nav);
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
  if (r === 'devices' || r === 'start' || r === 'setup' || r === '') return false;
  if (r === 'd/pulpit') { toLeave(); return true; }
  if (r.startsWith('d/') && r !== 'd/menu' && !['d/instalacja', 'd/alarmy'].includes(r)) { history.back(); return true; }
  if (r === 'd/menu' || r === 'app') { r === 'app' ? history.back() : go('d/pulpit'); return true; }
  go('d/pulpit'); return true;
};
function toLeave() { go('d/menu'); }   // z pulpitu „wstecz” otwiera menu (nie zamyka aplikacji)

// ------------------------------------------------------------------ zdarzenia z aplikacji natywnej
onEvent(e => {
  if (e.type === 'locked') {
    closeSheet();
    refreshChip();
    if (location.hash.startsWith('#/d/') && !location.hash.startsWith('#/d/menu')) go('d/pulpit');
    toast(e.reason === 'idle' ? 'Odblokowanie wygasło – tryb podglądu' : 'Sterowanie zablokowane');
  } else if (e.type === 'needs_unlock') {
    ensureUnlocked().then(ok => { if (ok) toast('Odblokowano – spróbuj ponownie'); });
  } else if (e.type === 'device_closed') { refreshChip(); }
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
  nat.deselect(); stopPolling();
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
  const sc = chrome('Urządzenia', root, 'none');
  $('#hm').style.visibility = 'hidden'; $('#chipbox').innerHTML = '';
  const open = (base, name) => { nat.selectDevice(base, name); go('d/pulpit'); startPolling(); };
  const renderMine = () => {
    const box = $('#mine', root); box.innerHTML = '';
    if (!devices.length) { box.innerHTML = '<div class="hint">Brak zapisanych urządzeń. Dodaj znalezione poniżej albo wpisz adres IP.</div>'; return; }
    devices.forEach(d => {
      const b = el(`<button class="dev"><span class="dot ${d.up === true ? 'on' : d.up === false ? 'off' : ''}"></span><div class="t"><b>${esc(d.name)}</b><small>${esc(d.base.replace('http://', ''))}${d.fw ? ' · fw ' + esc(d.fw) : ''}${d.up === false ? ' · poza zasięgiem' : ''}</small></div><div class="v"><b data-b2="t"></b><br><small data-b2="s"></small></div><span class="x">✕</span></button>`);
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
      $('button', b).onclick = () => { devices.push({ id: f.id, name: f.name, base: f.base, fw: f.fw, up: true }); save(); renderMine(); renderFound(); };
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
    window.__addPing = (i, info) => {
      if (i !== key) return; window.__addPing = null;
      if (!info || !info.id) return msg('Pod tym adresem nie ma urządzenia TeklaPelletCAN (brak odpowiedzi).');
      devices.push({ id: info.id, name: 'TeklaPelletCAN ' + info.id.slice(-4), base, fw: info.fw, up: true }); save(); renderMine(); renderFound(); $('#addr', root).value = ''; msg('Dodano.');
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
  const body = el(`<div><div class="sec"><h5>Widoki</h5>
    <button class="row nav2" data-go="d/pulpit"><span>Pulpit</span></button>
    <button class="row nav2" data-go="d/instalacja"><span>Instalacja</span></button>
    <button class="row nav2" data-go="d/kociol"><span>Nastawy: kocioł, CO, CWU</span></button>
    <button class="row nav2" data-go="d/alarmy"><span>Alarmy i historia</span></button>
    <button class="row nav2" data-go="d/params"><span>Wszystkie parametry</span></button></div>
    <div class="sec"><h5>Dostęp</h5>
    <button class="row nav2" id="lvl"><span>Poziom kotła (PIN)</span><span class="v" id="lvv"></span></button></div>
    <div class="sec"><h5>Urządzenie</h5>
    <button class="row nav2" id="orig"><span>Panel kotła (oryginał)</span></button>
    <button class="row nav2" id="cfg"><span>Konfiguracja urządzenia</span></button>
    <button class="row nav2" data-go="devices"><span>Zmień urządzenie</span></button></div>
    <div class="sec"><h5>Aplikacja</h5><button class="row nav2" data-go="app"><span>Ustawienia aplikacji</span></button></div>
    <div class="hint" style="text-align:center">Aplikacja ${esc(st.version)} · firmware ${esc(S.info.fw || '?')}</div></div>`);
  const sc = chrome('Menu', body, 'main');
  $('#lvv', body).textContent = level() > 0 ? 'poziom ' + level() : 'poziom 0';
  body.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  $('#lvl', body).onclick = async () => { if (await ensureLevel(1)) { toast('Poziom kotła aktywny'); $('#lvv', body).textContent = 'poziom ' + level(); } };
  $('#orig', body).onclick = () => nat.openOriginal();
  $('#cfg', body).onclick = () => nat.openDeviceSettings();
  unsub = subscribe(() => { refreshChip(); const l = $('#lvv', body); if (l) l.textContent = 'poziom ' + level(); });
}

// ------------------------------------------------------------------ ustawienia aplikacji
function viewAppSettings() {
  const st = nat.state();
  const body = el(`<div>
    <div class="sec"><h5>Bezpieczeństwo</h5>
      <button class="row nav2" id="chpin"><span>Zmień PIN aplikacji</span></button>
      <div class="sw"><span>Odcisk palca zamiast PIN-u<div class="hint">${st.bioAvailable ? 'Odblokowuje sterowanie na 5 minut' : 'Brak skonfigurowanej biometrii w telefonie'}</div></span><button class="tg ${st.bio ? 'on' : ''}" id="bio" ${st.bioAvailable ? '' : 'disabled'}></button></div>
      <div class="sw"><span>Blokuj aplikację przy uruchomieniu<div class="hint">Wymaga odblokowania, żeby w ogóle zobaczyć dane</div></span><button class="tg ${st.lockOnStart ? 'on' : ''}" id="los"></button></div>
      <div class="hint">Odblokowanie wygasa po 5 minutach bezczynności, po wyłączeniu ekranu i po wyjściu z aplikacji.</div></div>
    <div class="sec"><h5>Dane</h5><button class="row nav2" id="cc"><span>Wyczyść zapisane odczyty</span></button></div>
    <div class="sec"><h5>Aplikacja</h5><div class="row"><span>Wersja</span><span class="v">${esc(st.version)}</span></div>
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
  $('#rel', body).onclick = () => nat.openExternal('https://github.com/GieOeRZet/TeklaPelletCan/releases');
  $('#rst', body).onclick = async () => { if (await confirmSheet('Usunąć PIN?', 'Zostanie usunięty PIN i ustawienia biometrii. Aplikacja poprosi o nowy PIN.', 'Usuń')) { nat.resetSecurity(); go('setup'); } };
}

// ------------------------------------------------------------------ start
const st0 = nat.state();
if (!location.hash) location.hash = '#/start'; else render();
if (st0.hasPin && st0.lockOnStart && !st0.unlocked) setTimeout(() => ensureUnlocked(), 100);
window.__tpcReady = true;
