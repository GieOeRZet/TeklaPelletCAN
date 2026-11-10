// teklapelletcan-modern-card: nowa karta w stylu aplikacji Android (pulpit z grafikami Tekli, schemat instalacji,
// nastawy, harmonogramy, alarmy). Wylacznie integracja TeklaPelletCAN – urzadzenie z rejestru HA, jak w
// teklapelletcan-card. Punkty adresowane po ID z firmware (atrybut "tpc_id" na kazdej encji integracji),
// WIEC bez zgadywania po nazwach encji – metadane (zakres/krok/poziom) z teklapelletcan-points.js, generowanych
// z tego samego zrodla co firmware (rejestry/*.csv). PIN tylko do poziomu menu (1/2), jak w oryginalnej karcie –
// bez biometrii (to przegladarka HA, nie telefon).
import { TPC_POINTS, TPC_POINTS_BY_ID } from './teklapelletcan-points.js';

// Baza zasobow (img/) wyliczona wzgledem adresu TEGO pliku – dziala i w HA (/teklapelletcan_static/...),
// i w testach lokalnych (karta serwowana z korzenia web/), bez zalezenia od adresu strony/dashboardu.
// Mozna nadpisac w configu karty (asset_base) – przydatne, gdy sam plik karty jest serwowany z innego
// miejsca niz obrazki (np. karta wgrana tymczasowo do /local/ do testow, obrazki wciaz w /teklapelletcan_static/).
const DEFAULT_ASSET_BASE = new URL('.', import.meta.url).href;

const DOMAIN = 'teklapelletcan';
const LOCK_MS = 300000;

function ourDevices(hass) {
  if (!hass || !hass.devices) return [];
  return Object.values(hass.devices)
    .filter(d => Array.isArray(d.identifiers) && d.identifiers.some(id => Array.isArray(id) && id[0] === DOMAIN))
    .map(d => ({ id: d.id, name: (d.name_by_user || d.name || d.id) }))
    .sort((a, b) => a.name.localeCompare(b.name));
}
// Mapa punkt (id z firmware) -> stan HA, zbudowana z atrybutu "tpc_id" encji nalezacych do urzadzenia (bez
// zgadywania po nazwach). Dziala dla kazdej wersji jezykowej/zmienionej nazwy encji w HA.
function buildIndex(hass, deviceId) {
  const byId = new Map(), byEntity = new Map();
  if (!hass || !hass.entities || !hass.states) return { byId, byEntity };
  for (const e of Object.values(hass.entities)) {
    if (e.device_id !== deviceId) continue;
    const st = hass.states[e.entity_id];
    if (!st) continue;
    byEntity.set(e.entity_id, st);
    const pid = st.attributes && st.attributes.tpc_id;
    if (!pid) continue;
    const prev = byId.get(pid);
    // Osierocone encje po przeladowaniu integracji moga dzielic ten sam tpc_id z aktualnymi (ten sam
    // punkt zarejestrowany dwa razy, stara kopia utyka na "unavailable") – wygrywa ta z realnym odczytem.
    if (!prev || prev.state === 'unavailable' || prev.state === 'unknown') byId.set(pid, st);
  }
  return { byId, byEntity };
}
// Wezel uslug HA tej integracji (jak w pelletcan-card: skanuje zarejestrowane uslugi domeny, nie zaklada nazwy).
function nodeOf(hass) {
  const sv = hass && hass.services && hass.services[DOMAIN];
  if (!sv) return '';
  const n = Object.keys(sv).filter(k => k.endsWith('_set_param')).map(k => k.slice(0, -10));
  return n[0] || '';
}

const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–';
const fmt = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d) : '–';
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const el = html => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstElementChild; };

const TANK = (pct, w = 96) => {
  const f = Math.max(0, Math.min(100, Number.isFinite(pct) ? pct : 0)), u = 'tk' + Math.random().toString(36).slice(2);
  const barH = 327, barY = 95.8, fillH = Math.round(barH * f / 100 * 10) / 10;
  return `<svg width="${w}" viewBox="0 0 256 445"><defs>
      <linearGradient id="${u}b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4b5b8"/><stop offset="1" stop-color="#f09aa2"/></linearGradient>
      <linearGradient id="${u}t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6604f"/><stop offset="1" stop-color="#e5352b"/></linearGradient>
      <pattern id="${u}p" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="10" fill="#f3e24f"/><rect x="5" width="5" height="10" fill="#e1c92f"/></pattern></defs>
    <rect x="1.25" y="1.25" width="253.5" height="442.5" fill="url(#${u}b)" stroke="#e0453b" stroke-width="2.5"/>
    <rect x="1.25" y="1.25" width="253.5" height="68.5" fill="url(#${u}t)"/><rect x="1.25" y="67" width="253.5" height="3" fill="#b8352c"/>
    <rect x="97" y="${barY}" width="60.6" height="${barH}" fill="#6c7898" stroke="#e9edf8" stroke-width="2.5"/>
    <rect x="98.3" y="${(barY + barH - fillH).toFixed(1)}" width="58.1" height="${Math.max(0, fillH - 1.3).toFixed(1)}" fill="url(#${u}p)"/>
    <text x="64" y="412" font-size="42" font-weight="700" fill="#f5a21a" font-family="Roboto,sans-serif">E</text></svg>`;
};
const HOPPER = (pct, h = 54) => TANK(pct, Math.round(h * 0.62));

const CSS = `
:root { --bg:#111318; --card:#1c1f27; --card2:#12151b; --line:#2b303b; --txt:#e8eaf0; --dim:#9aa1b2; --acc:#ff7a1a; --ok:#4cc38a; --err:#ef5350; --blue:#4a86e8; --warn:#f2b441; }
* { box-sizing:border-box; }
:host { display:block; }
/* Karta ma STAŁĄ wysokość (jak classic) – ekrany (pulpit/instalacja/.../parametry) przewijają się w swoim
   wnętrzu (.body), więc długie listy (Parametry, Harmonogram) nie rozpychają już całej karty na dashboardzie. */
.wrap { background:var(--bg); color:var(--txt); font:15px/1.4 Roboto, system-ui, sans-serif; border-radius:var(--ha-card-border-radius,12px); overflow:hidden; display:flex; flex-direction:column; height:480px; }
.hdr { flex:0 0 auto; display:flex; align-items:center; gap:10px; padding:10px 12px; }
.hdr b { flex:1; font-size:16px; }
.ico { width:36px; height:36px; border-radius:50%; background:var(--card); border:0; color:inherit; display:flex; align-items:center; justify-content:center; font-size:18px; cursor:pointer; }
.chip { display:inline-flex; gap:6px; align-items:center; padding:5px 10px; border-radius:999px; font-size:12px; background:#2b303b; border:0; color:inherit; cursor:pointer; white-space:nowrap; }
.chip.open { background:rgba(76,195,138,.18); color:var(--ok); }
.nav { flex:0 0 auto; display:flex; gap:3px; padding:0 10px 8px; overflow-x:auto; scrollbar-width:none; } .nav::-webkit-scrollbar { display:none; }
.nav button { background:#2b303b; color:var(--dim); border:0; border-radius:999px; padding:6px 9px; font-size:11.5px; white-space:nowrap; cursor:pointer; flex:0 0 auto; }
.nav button.on { background:var(--acc); color:#1a1208; font-weight:700; }
.dots { flex:0 0 auto; display:flex; justify-content:center; gap:5px; padding-bottom:6px; }
.dots i { width:5px; height:5px; border-radius:50%; background:var(--line); display:inline-block; }
.dots i.on { background:var(--acc); width:12px; border-radius:3px; }
.body { flex:1 1 auto; min-height:0; overflow-y:auto; -webkit-overflow-scrolling:touch; overscroll-behavior:contain; padding:0 12px 12px; touch-action:pan-y; }
.hero { border-radius:14px; background:linear-gradient(160deg,#2a2f3b,#1c1f27 70%); border:1px solid var(--line); position:relative; overflow:hidden; height:168px; margin-top:4px; }
.hero .stage { position:absolute; left:0; top:0; bottom:0; width:42%; display:flex; align-items:flex-end; justify-content:center; padding-bottom:10px; }
.hero .stage img { max-height:140px; max-width:86%; object-fit:contain; filter:drop-shadow(0 8px 10px rgba(0,0,0,.45)); }
.hero .tx { position:absolute; right:14px; top:12px; text-align:right; }
.hero .big { font-size:42px; line-height:1; font-weight:300; } .hero .big small { font-size:18px; color:var(--dim); }
.hero .st { position:absolute; right:14px; bottom:10px; text-align:right; font-size:12px; color:var(--dim); }
.pill { display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; background:rgba(76,195,138,.16); color:var(--ok); }
.pill.o { background:rgba(255,122,26,.16); color:var(--acc); } .pill.r { background:rgba(239,83,80,.16); color:var(--err); }
.g2 { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:8px; }
.cd { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:9px 11px; min-height:76px; text-align:left; width:100%; color:inherit; cursor:pointer; border:1px solid var(--line); }
.cd small { color:var(--dim); font-size:10px; text-transform:uppercase; letter-spacing:.5px; display:block; }
.cd b { font-size:21px; font-weight:500; } .cd .u { color:var(--dim); font-size:11px; }
.cd.full { grid-column:span 2; min-height:56px; display:flex; align-items:center; gap:10px; }
.ok { color:var(--ok); } .er { color:var(--err); } .wr { color:var(--warn); } .dim { color:var(--dim); }
.sec { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:12px 14px; margin:10px 0; }
.sec h5 { margin:0 0 8px; font-size:11px; letter-spacing:.7px; text-transform:uppercase; color:var(--dim); font-weight:600; }
.row { display:flex; justify-content:space-between; align-items:center; gap:10px; padding:10px 0; border-top:1px solid var(--line); width:100%; background:none; border-left:0; border-right:0; border-bottom:0; color:inherit; text-align:left; cursor:pointer; }
.row:first-of-type { border-top:0; }
.row .v { color:var(--dim); flex:0 0 auto; min-width:4.2em; text-align:right; }
.row .lk { color:var(--warn); font-size:11px; margin-left:6px; }
.hint { color:var(--dim); font-size:12px; margin-top:4px; }
.stepper { display:flex; align-items:center; justify-content:space-between; background:var(--card2); border:1px solid var(--line); border-radius:12px; padding:8px 12px; margin:6px 0; }
.stepper button { width:42px; height:42px; border-radius:50%; border:0; background:#2b303b; color:#fff; font-size:22px; cursor:pointer; }
.chips { display:flex; gap:6px; margin-top:6px; flex-wrap:wrap; } .chips button { padding:7px 12px; border-radius:999px; background:#2b303b; border:0; color:inherit; font-size:12px; cursor:pointer; } .chips button.on { background:var(--acc); color:#1a1208; font-weight:700; }
.btn { display:block; width:100%; text-align:center; padding:11px; border-radius:12px; background:var(--blue); color:#fff; font-weight:600; margin-top:8px; border:0; cursor:pointer; }
.btn.acc { background:var(--acc); color:#1a1208; } .btn.sec { background:#2b303b; color:inherit; }
.scrim { position:absolute; inset:0; background:rgba(0,0,0,.55); z-index:20; }
.sheet { position:absolute; left:0; right:0; bottom:0; z-index:21; background:#1c1f27; border-top-left-radius:18px; border-top-right-radius:18px; border-top:1px solid var(--line); padding:12px 16px 16px; max-height:85%; overflow-y:auto; }
.grab { width:36px; height:4px; border-radius:2px; background:#4a4f5c; margin:0 auto 10px; } .sheet h3 { margin:0 0 6px; font-size:16px; }
.pin { display:flex; justify-content:center; gap:10px; margin:12px 0; } .pin i { width:12px; height:12px; border-radius:50%; border:2px solid #4a4f5c; display:inline-block; } .pin i.f { background:var(--acc); border-color:var(--acc); }
.pad { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; max-width:260px; margin:6px auto; } .pad button { height:48px; border-radius:12px; border:0; background:#2b303b; color:inherit; font-size:20px; cursor:pointer; } .pad button.s { background:transparent; font-size:14px; color:var(--dim); }
.msg { text-align:center; min-height:18px; font-size:12px; color:var(--err); }
.sched { display:flex; gap:2px; margin:6px 0; } .sched i { flex:1; height:16px; border-radius:2px; background:#2b303b; } .sched i.on { background:var(--acc); }
.hgrid { display:grid; grid-template-columns:repeat(6,1fr); gap:6px; margin:8px 0; } .hgrid button { padding:10px 0; border-radius:8px; border:0; background:#2b303b; color:inherit; font-size:13px; cursor:pointer; } .hgrid button.on { background:var(--acc); color:#1a1208; font-weight:700; }
.dayrow { display:block; width:100%; text-align:left; background:none; border:0; border-top:1px solid var(--line); padding:9px 0; cursor:pointer; color:inherit; } .dayrow:first-of-type { border-top:0; }
.dayrow .dn { display:flex; justify-content:space-between; font-size:13px; }
.hbar { display:flex; gap:1px; margin-top:5px; } .hbar i { flex:1; height:13px; border-radius:1px; background:#2b303b; } .hbar i.on { background:var(--acc); }
`;

const SCH = [['CWU', 'sch_cwu_txt', 0], ['CO', 'sch_co_txt', 1], ['Kocioł', 'sch_boil_txt', 2]];
const DAYS = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'];
const SCREENS = [['pulpit', 'Pulpit'], ['instalacja', 'Instalacja'], ['nastawy', 'Nastawy'], ['parametry', 'Parametry'], ['harmonogram', 'Harmonogram'], ['alarmy', 'Alarmy']];
const DEFAULT_HEIGHT = 480;

class TeklaModernCard extends HTMLElement {
  setConfig(c) {
    if (!c || typeof c !== 'object') throw new Error('Nieprawidłowa konfiguracja karty');
    this._cfg = Object.assign({ boiler_image: '13' }, c);
    this._assetBase = this._cfg.asset_base || DEFAULT_ASSET_BASE;
    this._screen = this._screen || 'pulpit';
    this._unlockedAt = this._unlockedAt || 0;
    this._schedKind = this._schedKind || 1;
    this._scroll = this._scroll || {};
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
  }
  _height() { const h = parseInt(this._cfg && this._cfg.height, 10); return Number.isFinite(h) && h >= 280 ? h : DEFAULT_HEIGHT; }
  getCardSize() { return Math.max(1, Math.round(this._height() / 50)); }
  set hass(hass) {
    this._hass = hass;
    this._render();
  }
  get hass() { return this._hass; }

  _unlocked() { return this._unlockedAt && Date.now() - this._unlockedAt < LOCK_MS; }
  _remaining() { return this._unlocked() ? Math.max(0, LOCK_MS - (Date.now() - this._unlockedAt)) : 0; }
  _touch() { if (this._unlocked()) this._unlockedAt = Date.now(); }

  _idx() {
    const devs = ourDevices(this._hass);
    const want = this._cfg.device_id;
    const dev = (want && devs.find(d => d.id === want)) || devs[0];
    return { devs, dev, idx: dev ? buildIndex(this._hass, dev.id) : { byId: new Map(), byEntity: new Map() } };
  }
  pv(id) { const s = this._lastIdx && this._lastIdx.byId.get(id); return s ? s.state : undefined; }
  pn(id) { const x = parseFloat(this.pv(id)); return Number.isFinite(x) ? x : NaN; }
  pb(id) { return this.pv(id) === 'on'; }
  // Atrybut encji (np. wpisy historii alarmow ah_0..ah_19 na encji alarm_history, skonsolidowane
  // zamiast wielu osobnych encji) - przekazywany przez integracje jako extra_state_attributes.
  pattr(id, key) { const s = this._lastIdx && this._lastIdx.byId.get(id); return s && s.attributes ? s.attributes[key] : undefined; }
  level() { const x = this.pn('access_level_sensor'); return Number.isFinite(x) ? x : 0; }
  // Biezacy klucz enuma: niektore punkty (np. boiler_mode) firmware zglasza tylko jako etykiete tekstowa
  // na encji "<id>_text" (bez liczbowego odczytu), wiec przy braku liczby szukamy klucza po dopasowaniu
  // tekstu etykiety do opcji punktu – zapis zawsze idzie po numerycznym kluczu (set_param/set_boiler_mode).
  _enumKey(id, opts) {
    const n = this.pn(id);
    if (Number.isFinite(n)) return String(Math.round(n));
    const t = this.pv(id + '_text');
    if (t) { const k = Object.keys(opts).find(k => opts[k] === t); if (k) return k; }
    return null;
  }

  async _call(service, data) {
    const node = nodeOf(this._hass);
    if (!node) { this._toast('Brak usług integracji (restart HA?)'); return false; }
    try {
      await this._hass.callService(DOMAIN, node + '_' + service, data || {});
      this._toast('Zapisano');
      return true;
    } catch (e) {
      this._toast('Błąd: ' + (e && e.message || e));
      return false;
    }
  }
  async _callDomain(domain, service, data) {
    try { await this._hass.callService(domain, service, data || {}); return true; } catch (e) { this._toast('Błąd: ' + (e && e.message || e)); return false; }
  }
  _toast(t) {
    const r = this.shadowRoot; if (!r) return;
    let b = r.getElementById('toast');
    if (!b) { b = document.createElement('div'); b.id = 'toast'; b.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#2a2d36;color:#e8eaf0;padding:9px 14px;border-radius:10px;font-size:12px;z-index:40;box-shadow:0 6px 20px rgba(0,0,0,.5)'; r.appendChild(b); }
    b.textContent = t; clearTimeout(this._toastT); this._toastT = setTimeout(() => b.remove(), 2600);
  }

  async _ensureLevel(need) {
    if (this.level() >= need) return true;
    const pin = await this._pinSheet('Poziom dostępu kotła', `Ta pozycja wymaga poziomu ${need}. Podaj PIN (jak w panelu kotła).`, async p => {
      const ok = await this._call('unlock', { pin: parseInt(p, 10) });
      if (!ok) return 'Błąd połączenia';
      await new Promise(r => setTimeout(r, 700));
      const cur = this.level();
      return cur >= need ? null : (cur > 0 ? `Ten PIN daje tylko poziom ${cur}` : 'Zły PIN poziomu');
    });
    if (pin !== null) this._unlockedAt = Date.now();
    return pin !== null;
  }

  // ---------------------------------------------------------------- okna (sheet/pin)
  _closeSheet() { const o = this.shadowRoot.getElementById('overlay'); if (o) o.innerHTML = ''; }
  _openSheet(html) {
    this._closeSheet();
    const o = this.shadowRoot.getElementById('overlay');
    o.innerHTML = '<div class="scrim"></div><div class="sheet"><div class="grab"></div>' + html + '</div>';
    o.querySelector('.scrim').onclick = () => this._closeSheet();
    return o.querySelector('.sheet');
  }
  _pinSheet(title, sub, check) {
    return new Promise(resolve => {
      let pin = '';
      const sh = this._openSheet(`<h3>${esc(title)}</h3><div class="hint">${esc(sub)}</div><div class="pin" id="dots"></div><div class="msg" id="pmsg"></div>
        <div class="pad">${[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => `<button data-k="${n}">${n}</button>`).join('')}<button class="s" data-k="x">⌫</button><button data-k="0">0</button><button class="s" data-k="ok">OK</button></div>`);
      const draw = () => { sh.querySelector('#dots').innerHTML = Array.from({ length: Math.max(4, pin.length) }, (_, i) => `<i class="${i < pin.length ? 'f' : ''}"></i>`).join(''); };
      draw();
      let done = false;
      sh.querySelectorAll('.pad button').forEach(b => b.onclick = async () => {
        const k = b.dataset.k;
        if (k === 'x') pin = pin.slice(0, -1);
        else if (k === 'ok') {
          if (pin.length < 4) { sh.querySelector('#pmsg').textContent = 'PIN: min. 4 cyfry'; return; }
          const err = await check(pin);
          if (err) { sh.querySelector('#pmsg').textContent = err; pin = ''; draw(); return; }
          done = true; this._closeSheet(); resolve(pin); return;
        } else pin += k;
        sh.querySelector('#pmsg').textContent = ''; draw();
      });
      const obs = new MutationObserver(() => { if (!this.shadowRoot.contains(sh) && !done) { resolve(null); obs.disconnect(); } });
      obs.observe(this.shadowRoot.getElementById('overlay'), { childList: true });
    });
  }
  async _confirm(title, text, okLabel) {
    return new Promise(resolve => {
      let done = false;
      const sh = this._openSheet(`<h3>${esc(title)}</h3><div class="hint" style="font-size:13px">${text}</div><button class="btn acc" id="yes">${esc(okLabel || 'Zastosuj')}</button><button class="btn sec" id="no">Anuluj</button>`);
      sh.querySelector('#yes').onclick = () => { done = true; this._closeSheet(); resolve(true); };
      sh.querySelector('#no').onclick = () => { this._closeSheet(); resolve(false); };
      const obs = new MutationObserver(() => { if (!this.shadowRoot.contains(sh) && !done) { resolve(false); obs.disconnect(); } });
      obs.observe(this.shadowRoot.getElementById('overlay'), { childList: true });
    });
  }

  async _editPoint(id) {
    const p = TPC_POINTS_BY_ID[id];
    if (!p || !p.writable) return;
    if (p.level && this.level() < p.level && !(await this._ensureLevel(p.level))) return;
    const cur = this.pn(id);
    if (p.options) {
      const opts = {}; p.options.split(',').forEach(kv => { const i = kv.indexOf(':'); opts[kv.slice(0, i)] = kv.slice(i + 1); });
      const curKey = this._enumKey(id, opts);
      const sh = this._openSheet(`<h3>${esc(p.name)}</h3><div class="chips">${Object.entries(opts).map(([k, l]) => `<button data-k="${k}" class="${curKey === k ? 'on' : ''}">${esc(l)}</button>`).join('')}</div>`);
      sh.querySelectorAll('.chips button').forEach(b => b.onclick = async () => {
        const val = parseInt(b.dataset.k, 10); this._closeSheet();
        if (id === 'boiler_mode') await this._call('set_boiler_mode', { mode: val }); else await this._call('set_param', { key: p.key, value: val });
      });
      return;
    }
    const step = p.step || 1, dec = step < 1 ? 1 : 0;
    let val = Number.isFinite(cur) ? cur : (p.min || 0);
    const sh = this._openSheet(`<h3>${esc(p.name)}</h3><div class="hint">Zakres ${p.min}…${p.max} ${esc(p.unit || '')}${p.level ? ' · poziom ' + p.level : ''}</div>
      <div class="stepper"><button id="m">−</button><b id="val"></b><button id="p">+</button></div><button class="btn acc" id="ok">Zapisz</button><button class="btn sec" id="no">Anuluj</button>`);
    const draw = () => { sh.querySelector('#val').textContent = val.toFixed(dec) + (p.unit ? ' ' + p.unit : ''); };
    draw();
    sh.querySelector('#m').onclick = () => { val = Math.max(p.min, Number((val - step).toFixed(dec))); draw(); };
    sh.querySelector('#p').onclick = () => { val = Math.min(p.max, Number((val + step).toFixed(dec))); draw(); };
    sh.querySelector('#no').onclick = () => this._closeSheet();
    sh.querySelector('#ok').onclick = async () => {
      this._closeSheet();
        // piec pol zadanych ma dedykowana usluge (set_setpoint, which 0..4 – kolejnosc z firmware, nie z nazw pol);
      // pozostale zapisywalne punkty ida przez ogolny set_param z kluczem zapisu z metadanych (teklapelletcan-points.js).
      const SETPOINT_WHICH = { hw_set_comfort: 0, hw_set_eco: 1, co_set_comfort: 2, co_set_eco: 3, boiler_set_manual: 4 };
      if (id in SETPOINT_WHICH) { await this._call('set_setpoint', { which: SETPOINT_WHICH[id], value: val }); return; }
      await this._call('set_param', { key: p.key, value: val });
    };
  }
  async _fuelSheet() {
    const cap = this.pn('tank_cap'), days = this.pn('fuel_days'); let val = this.pn('tank_kg'); if (!Number.isFinite(val)) val = 0;
    const sh = this._openSheet(`<h3>Paliwo</h3>
      <div style="display:flex;gap:14px;align-items:center"><div id="tk"></div>
        <div style="flex:1;text-align:center"><button class="ico" id="pl" style="width:48px;height:48px;margin:0 auto;font-size:24px">+</button>
        <div style="font-size:28px;margin:4px 0" id="big"></div><button class="ico" id="mi" style="width:48px;height:48px;margin:0 auto;font-size:24px">−</button></div></div>
      <div class="chips"><button data-d="-50">−50</button><button data-d="-10">−10</button><button data-d="10">+10</button><button data-d="25">+25</button><button data-d="50">+50</button><button data-d="100">+100</button><button data-full="1">Pełny</button></div>
      <div class="hint">Pojemność: ${Number.isFinite(cap) ? fmt(cap, 0) : '–'} kg.${Number.isFinite(days) ? ' Prognoza: ok. ' + fmt(days, 0) + ' dni.' : ''}</div>
      <button class="btn acc" id="ok">Zapisz ilość paliwa</button><button class="btn sec" id="no">Anuluj</button>`);
    const draw = () => { sh.querySelector('#tk').innerHTML = TANK(cap > 0 ? val / cap * 100 : 0, 92); sh.querySelector('#big').textContent = Math.round(val) + ' kg'; };
    draw();
    const setVal = x => { val = Math.max(0, Math.min(1500, Math.round(x))); draw(); };
    sh.querySelectorAll('[data-d]').forEach(b => b.onclick = () => setVal(val + parseInt(b.dataset.d, 10)));
    sh.querySelector('[data-full]').onclick = () => { if (Number.isFinite(cap)) setVal(cap); };
    sh.querySelector('#pl').onclick = () => setVal(val + 1); sh.querySelector('#mi').onclick = () => setVal(val - 1);
    sh.querySelector('#no').onclick = () => this._closeSheet();
    sh.querySelector('#ok').onclick = async () => {
      if (TPC_POINTS_BY_ID.tank_kg.level && this.level() < TPC_POINTS_BY_ID.tank_kg.level && !(await this._ensureLevel(TPC_POINTS_BY_ID.tank_kg.level))) return;
      this._closeSheet(); await this._call('set_param', { key: TPC_POINTS_BY_ID.tank_kg.key, value: val });
    };
  }

  // ---------------------------------------------------------------- harmonogram
  _bandsText(hex) {
    if (!/^[0-9A-Fa-f]{6}$/.test(hex || '')) return 'brak odczytu';
    const bits = parseInt(hex, 16), o = []; let st = null;
    for (let i = 0; i <= 24; i++) { const b = i < 24 && ((bits >> i) & 1); if (b && st === null) st = i; if (!b && st !== null) { o.push(`${st}–${i}`); st = null; } }
    return o.length ? o.join(', ') + ' h' : 'wyłączone';
  }
  _schedBits(kind) {
    const id = SCH[kind][1];
    return Array.from({ length: 7 }, (_, d) => { const x = this.pattr(id, 'd' + d); return /^[0-9A-Fa-f]{6}$/.test(x || '') ? parseInt(x, 16) : null; });
  }
  async _editDay(kind, day) {
    const cur = this._schedBits(kind)[day];
    if (cur == null) { this._toast('Brak odczytu tego dnia'); return; }
    let bits = cur, copy = null;
    const sh = this._openSheet(`<h3>${SCH[kind][0]} · ${DAYS[day]}</h3><div class="hint">Stuknij godziny, w których ma być włączone.</div>
      <div class="hgrid">${Array.from({ length: 24 }, (_, h) => `<button data-h="${h}" class="${(bits >> h) & 1 ? 'on' : ''}">${h}</button>`).join('')}</div>
      <div class="hint" id="txt"></div><div class="chips"><button data-all="1">Wszystkie</button><button data-none="1">Żadna</button></div>
      <div class="hint" style="margin-top:6px">Zastosuj również do:</div><div class="chips" id="cp"><button data-cp="wk">Pn–Pt</button><button data-cp="we">Sob–Nd</button><button data-cp="all">Cały tydzień</button></div>
      <button class="btn acc" id="ok">Zapisz</button><button class="btn sec" id="no">Anuluj</button>`);
    const draw = () => { sh.querySelectorAll('[data-h]').forEach(b => b.classList.toggle('on', !!((bits >> +b.dataset.h) & 1))); sh.querySelector('#txt').textContent = this._bandsText(bits.toString(16).padStart(6, '0')); };
    draw();
    sh.querySelectorAll('[data-h]').forEach(b => b.onclick = () => { bits ^= (1 << +b.dataset.h); draw(); });
    sh.querySelector('[data-all]').onclick = () => { bits = 0xFFFFFF; draw(); };
    sh.querySelector('[data-none]').onclick = () => { bits = 0; draw(); };
    sh.querySelectorAll('#cp button').forEach(b => b.onclick = () => { copy = copy === b.dataset.cp ? null : b.dataset.cp; sh.querySelectorAll('#cp button').forEach(x => x.classList.toggle('on', x.dataset.cp === copy)); });
    sh.querySelector('#no').onclick = () => this._closeSheet();
    sh.querySelector('#ok').onclick = async () => {
      const days = copy === 'wk' ? [0, 1, 2, 3, 4] : copy === 'we' ? [5, 6] : copy === 'all' ? [0, 1, 2, 3, 4, 5, 6] : [day];
      this._closeSheet();
      for (const d of days) await this._call('set_schedule', { kind, day: d, bits });
    };
  }

  // ---------------------------------------------------------------- render
  _render() {
    const root = this.shadowRoot;
    if (!root.querySelector('style')) {
      const st = document.createElement('style'); st.textContent = CSS; root.appendChild(st);
      root.appendChild(el('<div class="wrap"><div id="hdr"></div><div id="nav" class="nav"></div><div id="body" class="body"></div><div id="dots" class="dots"></div><div id="overlay"></div></div>'));
    }
    const wrap = root.querySelector('.wrap'); wrap.style.height = this._height() + 'px';
    const { devs, dev, idx } = this._idx();
    this._lastIdx = idx;
    const body = root.getElementById('body');
    if (!dev) {
      root.getElementById('hdr').innerHTML = '';
      root.getElementById('nav').innerHTML = '';
      root.getElementById('dots').innerHTML = '';
      body.innerHTML = '<div class="sec"><b style="color:var(--err)">TeklaPelletCAN-modern</b><div class="hint" style="margin-top:6px">Nie znaleziono żadnego urządzenia integracji TeklaPelletCAN. Dodaj ją w Ustawienia → Urządzenia i usługi.</div></div>';
      return;
    }
    const hdr = root.getElementById('hdr');
    const unlocked = this._unlocked();
    hdr.innerHTML = `<div class="hdr"><b>${esc(dev.name)}</b><button class="chip ${unlocked ? 'open' : ''}" id="chip">${unlocked ? '🔓 ' + Math.ceil(this._remaining() / 60000) + ' min' : '🔒 poziom ' + this.level()}</button></div>`
      + (devs.length > 1 && !this._cfg.device_id ? '<div class="hint" style="padding:0 12px 6px">Wykryto kilka urządzeń – pokazuję „' + esc(dev.name) + '” (wybierz w edytorze karty).</div>' : '');
    hdr.querySelector('#chip').onclick = () => { if (!unlocked) this._ensureLevel(1).then(() => this._render()); else { this._unlockedAt = 0; this._render(); } };
    const nav = root.getElementById('nav');
    nav.innerHTML = SCREENS.map(([k, l]) => `<button data-s="${k}" class="${this._screen === k ? 'on' : ''}">${l}</button>`).join('');
    nav.querySelectorAll('button').forEach(b => b.onclick = () => this._goScreen(b.dataset.s));
    root.getElementById('dots').innerHTML = SCREENS.map(([k]) => `<i class="${this._screen === k ? 'on' : ''}"></i>`).join('');
    // Ekran przewija się we własnym wnętrzu (wysokość karty jest stała – jak classic) – zapamietujemy
    // scrollTop per ekran, bo kazda aktualizacja hass() przebudowuje body od zera (traci scroll bez tego).
    const savedScroll = this._scroll[this._screen] || 0;
    body.innerHTML = '';
    const fn = { pulpit: this._pulpit, instalacja: this._instalacja, nastawy: this._nastawy, parametry: this._parametry, harmonogram: this._harmonogram, alarmy: this._alarmy }[this._screen] || this._pulpit;
    body.appendChild(fn.call(this));
    body.scrollTop = savedScroll;
    body.onscroll = () => { this._scroll[this._screen] = body.scrollTop; };
    this._bindSwipe(body);
  }

  // Zmiana ekranu (nawigacja i swipe) w jednym miejscu, żeby oba sposoby dzialaly tak samo.
  _goScreen(k) { if (k !== this._screen) { this._screen = k; this._render(); } }
  // Przesuwanie palcem w lewo/prawo = nastepny/poprzedni ekran (jak karty w aplikacji) – tylko gdy ruch jest
  // bardziej horyzontalny niz wertykalny, zeby nie przeszkadzac normalnemu przewijaniu listy w gore/dol.
  _bindSwipe(body) {
    let sx = 0, sy = 0, tracking = false;
    body.ontouchstart = e => { const t = e.touches[0]; sx = t.clientX; sy = t.clientY; tracking = true; };
    body.ontouchend = e => {
      if (!tracking) return; tracking = false;
      const t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
      if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy) * 1.4) return;
      const i = SCREENS.findIndex(([k]) => k === this._screen);
      const ni = dx < 0 ? Math.min(SCREENS.length - 1, i + 1) : Math.max(0, i - 1);
      if (ni !== i) this._goScreen(SCREENS[ni][0]);
    };
  }

  _boilerImg() { const t = this._cfg.boiler_image; return this._assetBase + (['11', '12', '14'].includes(String(t)) ? `img/panel/0${t}.png` : 'img/kociol.webp'); }

  _pulpit() {
    const alarmOn = this.pb('alarm_active');
    const root = el(`<div>
      <div class="hero"><div class="stage"><img src="${this._boilerImg()}" alt="kocioł"></div>
        <div class="tx"><div class="big">${f1(this.pn('boiler_temp'))}<small> °C</small></div>
          <div class="pill ${/alarm/i.test(this.pv('burner_state_text') || '') ? 'r' : /modulacj/i.test(this.pv('burner_state_text') || '') ? '' : 'o'}">${esc(this.pv('burner_state_text') || '–')}${Number.isFinite(this.pn('burner_power')) ? ' · ' + fmt(this.pn('burner_power'), 0) + ' %' : ''}</div></div>
        <div class="st">zadana ${fmt(this.pn('boiler_set_result'), 0)} °C · tryb ${esc(this.pv('boiler_mode_text') || '–')}</div></div>
      <div class="g2">
        <button class="cd" data-go="nastawy"><small>CWU</small><b>${f1(this.pn('hw_temp'))}</b><span class="u"> °C</span><div class="u">zadana ${fmt(this.pn('hw_set_result'), 0)} · pompa ${this.pb('hw_pump') ? '<span class="ok">wł.</span>' : 'wył.'}</div></button>
        <button class="cd" data-go="nastawy"><small>CO</small><b>${f1(this.pn('ch1_temp'))}</b><span class="u"> °C</span><div class="u">zadana ${fmt(this.pn('ch1_set_result'), 0)} · pompa ${this.pb('ch1_pump') ? '<span class="ok">wł.</span>' : 'wył.'}</div></button>
        <button class="cd" data-fuel="1"><small>Paliwo</small><b>${fmt(this.pn('tank_kg'), 0)}</b><span class="u"> kg</span><div class="u">${Number.isFinite(this.pn('fuel_days')) ? 'ok. ' + fmt(this.pn('fuel_days'), 0) + ' dni' : fmt(this.pn('tank_pct'), 0) + ' %'}</div></button>
        <button class="cd" data-go="instalacja"><small>Zewnętrzna</small><b>${f1(this.pn('outside_temp'))}</b><span class="u"> °C</span><div class="u">powrót ${f1(this.pn('ret_temp'))} °C</div></button>
        <button class="cd full" data-go="alarmy"><span style="font-size:22px">${alarmOn ? '<span class="er">⚠</span>' : '<span class="ok">✓</span>'}</span><div><b style="font-size:15px${alarmOn ? ';color:var(--err)' : ''}">${alarmOn ? 'Alarm aktywny' : 'Brak alarmów'}</b><div class="u">ostatni: ${esc(this.pv('alarm_last_text') || '–')}</div></div></button>
      </div></div>`);
    root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => { this._screen = b.dataset.go; this._render(); });
    root.querySelectorAll('[data-fuel]').forEach(b => b.onclick = () => this._fuelSheet());
    return root;
  }

  _instalacja() {
    const root = el(`<div>
      <button class="row" style="border-radius:14px;background:var(--card);border:1px solid var(--line);padding:12px" data-fuel="1">
        <span><b>Zbiornik</b><div class="hint">${fmt(this.pn('tank_kg'), 0)} / ${fmt(this.pn('tank_cap'), 0)} kg</div></span><span class="pill">${fmt(this.pn('tank_pct'), 0)} %</span></button>
      <div style="text-align:center;color:var(--acc);padding:4px 0">▼ ▼ ▼</div>
      <button class="row" style="border-radius:14px;background:var(--card);border:1px solid var(--line);padding:12px" data-go="nastawy">
        <span><b>Palnik</b><div class="hint">${esc(this.pv('burner_state_text') || '–')}</div></span><span><b>${fmt(this.pn('burner_power'), 0)} %</b></span></button>
      <div style="text-align:center;color:var(--acc);padding:4px 0">▼ ▼ ▼</div>
      <button class="row" style="border-radius:14px;background:var(--card);border:1px solid var(--line);padding:12px" data-go="nastawy">
        <span><b>Kocioł</b><div class="hint">zadana ${fmt(this.pn('boiler_set_result'), 0)} °C · ${esc(this.pv('boiler_mode_text') || '–')}</div></span><span><b>${f1(this.pn('boiler_temp'))} °C</b></span></button>
      <div class="sec"><h5>Dodatkowe</h5>
        <div class="row"><span>Temperatura powrotu</span><span class="v">${f1(this.pn('ret_temp'))} °C</span></div>
        <div class="row"><span>Temperatura palnika</span><span class="v">${f1(this.pn('burner_temp'))} °C</span></div>
        <div class="row"><span>Temperatura zewnętrzna</span><span class="v">${f1(this.pn('outside_temp'))} °C</span></div>
        <div class="row"><span>Moc palnika</span><span class="v">${f1(this.pn('burner_kw'))} kW</span></div></div></div>`);
    root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => { this._screen = b.dataset.go; this._render(); });
    root.querySelectorAll('[data-fuel]').forEach(b => b.onclick = () => this._fuelSheet());
    return root;
  }

  _stepperRow(title, id) {
    const p = TPC_POINTS_BY_ID[id];
    const r = el(`<div><div class="hint">${esc(title)}</div><button class="stepper" data-id="${esc(id)}" style="width:100%;justify-content:center;gap:16px"><b>${f1(this.pn(id))} ${p ? esc(p.unit) : ''}</b><span class="dim" style="font-size:12px">edytuj</span></button></div>`);
    r.querySelector('button').onclick = () => this._editPoint(id);
    return r;
  }
  _modeChips(title, id, labelsStr, applyMode) {
    const opts = {}; (labelsStr || '').split(',').forEach(kv => { const i = kv.indexOf(':'); if (i > 0) opts[kv.slice(0, i)] = kv.slice(i + 1); });
    const cur = this._enumKey(id, opts);
    const r = el(`<div><div class="hint" style="margin-top:8px">${esc(title)}</div><div class="chips">${Object.entries(opts).map(([k, l]) => `<button data-k="${k}" class="${cur === k ? 'on' : ''}">${esc(l)}</button>`).join('')}</div></div>`);
    r.querySelectorAll('button').forEach(b => b.onclick = () => applyMode(parseInt(b.dataset.k, 10)));
    return r;
  }
  _nastawy() {
    const root = el('<div></div>');
    const sec = h => { const s = el(`<div class="sec"><h5>${h}</h5></div>`); root.appendChild(s); return s; };
    sec('Kocioł').append(this._stepperRow('Zadana temperatura kotła (ręczna)', 'boiler_set_manual'),
      this._modeChips('Tryb pracy kotła', 'boiler_mode', TPC_POINTS_BY_ID.boiler_mode.options, m => this._call('set_boiler_mode', { mode: m })));
    sec('CO (ogrzewanie)').append(this._stepperRow('Zadana CO (ręczna)', 'ch1_set_manual'), this._stepperRow('Zadana CO – komfort', 'co_set_comfort'), this._stepperRow('Zadana CO – eko', 'co_set_eco'));
    const w = sec('CWU (ciepła woda)');
    w.append(this._stepperRow('Zadana CWU – komfort', 'hw_set_comfort'), this._stepperRow('Zadana CWU – eko', 'hw_set_eco'));
    return root;
  }

  // Wiersz pojedynczego parametru (dowolny punkt zapisywalny) – wartosc + poziom wymagany, klik otwiera
  // ten sam edytor co _stepperRow/_modeChips (_editPoint rozpoznaje liczbowy/enum i wybiera usluge sam).
  _paramRow(id) {
    const p = TPC_POINTS_BY_ID[id];
    if (!p) return el('<div></div>');
    let val;
    if (p.options) {
      const opts = {}; p.options.split(',').forEach(kv => { const i = kv.indexOf(':'); if (i > 0) opts[kv.slice(0, i)] = kv.slice(i + 1); });
      const k = this._enumKey(id, opts);
      val = k != null ? opts[k] : '–';
    } else {
      val = f1(this.pn(id)) + (p.unit ? ' ' + p.unit : '');
    }
    const r = el(`<button class="row"><span>${esc(p.name)}${p.level ? ' <span class="lk">🔒' + p.level + '</span>' : ''}</span><span class="v">${esc(val)}</span></button>`);
    r.onclick = () => this._editPoint(id);
    return r;
  }
  // Pelna lista wszystkich parametrow zapisywalnych urzadzenia (jak "Palnik/CO/CWU – ustawienia" w karcie
  // oryginalnej) – pogrupowana wg prefiksu id z rejestry/punkty.csv, bez recznego katalogu nazw encji.
  _parametry() {
    const GROUPS = [
      ['Kocioł', /^(boiler_|k_nominal|boil_|fuel_heat|fuel_test|air_corr|power_(min|max))/],
      ['Palnik', /^(p_|fan_mod_|exh_c|k_predose|k_egt|k_exch_int)/],
      ['CO (ogrzewanie)', /^(co1_|ch1_|ch2_|co_set)/],
      ['CWU (ciepła woda)', /^(cwu_|hw_set)/],
      ['Alarmy', /^alarm_/],
    ];
    const writable = TPC_POINTS.filter(p => p.writable && p.id !== 'tank_kg');
    const used = new Set();
    const root = el('<div></div>');
    for (const [label, re] of GROUPS) {
      const pts = writable.filter(p => re.test(p.id));
      if (!pts.length) continue;
      pts.forEach(p => used.add(p.id));
      const s = el(`<div class="sec"><h5>${esc(label)}</h5></div>`);
      pts.forEach(p => s.appendChild(this._paramRow(p.id)));
      root.appendChild(s);
    }
    const rest = writable.filter(p => !used.has(p.id));
    if (rest.length) {
      const s = el('<div class="sec"><h5>Inne</h5></div>');
      rest.forEach(p => s.appendChild(this._paramRow(p.id)));
      root.appendChild(s);
    }
    return root;
  }

  _harmonogram() {
    const today = (new Date().getDay() + 6) % 7;
    const root = el(`<div><div class="chips" id="kinds"></div><div class="sec" id="days"></div></div>`);
    const draw = () => {
      root.querySelector('#kinds').innerHTML = SCH.map((s, i) => `<button data-k="${i}" class="${i === this._schedKind ? 'on' : ''}">${s[0]}</button>`).join('');
      root.querySelectorAll('#kinds button').forEach(b => b.onclick = () => { this._schedKind = +b.dataset.k; draw(); });
      const all = this._schedBits(this._schedKind);
      const box = root.querySelector('#days'); box.innerHTML = '<h5>' + SCH[this._schedKind][0] + ' · tydzień</h5>';
      DAYS.forEach((dn, d) => {
        const b = all[d];
        const r = el(`<button class="dayrow"><div class="dn"><b${d === today ? ' style="color:var(--acc)"' : ''}>${dn}${d === today ? ' · dziś' : ''}</b><span class="dim">${this._bandsText(b != null ? b.toString(16).padStart(6, '0') : '')}</span></div>
          <div class="hbar">${Array.from({ length: 24 }, (_, h) => `<i class="${b != null && ((b >> h) & 1) ? 'on' : ''}"></i>`).join('')}</div></button>`);
        r.onclick = () => this._editDay(this._schedKind, d);
        box.appendChild(r);
      });
    };
    draw();
    return root;
  }

  _alarmy() {
    const root = el('<div><div class="sec"><h5>Stan</h5></div><div class="sec"><h5>Historia alarmów</h5><div id="alist"></div></div></div>');
    const s = root.querySelector('.sec');
    s.innerHTML = '<h5>Stan</h5><div class="row"><span>Alarm</span><span class="v">' + (this.pb('alarm_active') ? '<span class="er">aktywny</span>' : '<span class="ok">brak</span>') + '</span></div><div class="row"><span>Ostatni</span><span class="v">' + esc(this.pv('alarm_last_text') || '–') + '</span></div>';
    const L = root.querySelector('#alist'), rows = [];
    const fmtT = raw => { const x = parseInt(raw, 10); return x > 1e9 ? new Date(x * 1000).toLocaleString('pl-PL', { dateStyle: 'short', timeStyle: 'short' }) : '–'; };
    for (let i = 0; i < 20; i++) {
      const v = this.pattr('alarm_history', 'ah_' + i);
      if (!v || v === '-' || v === 'unknown') continue;
      const [txt, a, b] = String(v).split('|');
      rows.push(`<div class="row" style="cursor:default"><span>${esc(txt)}<div class="hint">${fmtT(a)} → ${parseInt(b, 10) > 1e9 ? fmtT(b) : 'trwa'}</div></span></div>`);
    }
    L.innerHTML = rows.join('') || '<div class="hint">Brak wpisów.</div>';
    const btn = el('<button class="btn sec">Potwierdź alarm</button>');
    btn.onclick = async () => { if (await this._confirm('Potwierdź alarm', 'Potwierdzić aktywny alarm w kotle?', 'Potwierdź')) await this._callDomain('button', 'press', { entity_id: this._lastIdx.byId.get('potwierdz_alarm') ? this._lastIdx.byId.get('potwierdz_alarm').entity_id : undefined }); };
    root.appendChild(btn);
    return root;
  }

  static getConfigElement() { return document.createElement('teklapelletcan-modern-card-editor'); }
  static getStubConfig() { return { boiler_image: '13' }; }
}
if (!customElements.get('teklapelletcan-modern-card')) customElements.define('teklapelletcan-modern-card', TeklaModernCard);

class TeklaModernCardEditor extends HTMLElement {
  setConfig(c) { this._cfg = Object.assign({ boiler_image: '13' }, c || {}); this._draw(); }
  set hass(h) { this._hass = h; this._draw(); }
  _draw() {
    if (!this._cfg) return;
    if (!this._form) {
      const info = document.createElement('div');
      info.style.cssText = 'font-size:13px;line-height:1.45;margin:0 0 10px;opacity:.9';
      info.textContent = 'Nowa karta (styl aplikacji) wyłącznie dla integracji TeklaPelletCAN – encje dobierane automatycznie po ID punktu. Karta ma stałą wysokość – dłuższe ekrany (Parametry, Harmonogram) przewijają się w jej wnętrzu.';
      this.appendChild(info);
      this._form = document.createElement('ha-form');
      this._form.computeLabel = s => s.label || s.name;
      this._form.addEventListener('value-changed', ev => this._changed(ev.detail.value));
      this.appendChild(this._form);
    }
    const devs = this._hass ? ourDevices(this._hass) : [];
    const schema = [
      { name: 'boiler_image', label: 'Grafika kotła', selector: { select: { mode: 'dropdown', options: [{ value: '11', label: 'Typ 11' }, { value: '12', label: 'Typ 12' }, { value: '13', label: 'Typ 13' }, { value: '14', label: 'Typ 14' }] } } },
      { name: 'height', label: 'Wysokość karty (px)', selector: { number: { mode: 'box', min: 320, max: 900, step: 10 } } },
    ];
    if (devs.length > 1) schema.unshift({ name: 'device_id', label: 'Urządzenie', selector: { select: { mode: 'dropdown', options: [{ value: 'auto', label: 'Automatycznie' }].concat(devs.map(d => ({ value: d.id, label: d.name }))) } } });
    this._form.schema = schema;
    this._form.data = Object.assign({ height: DEFAULT_HEIGHT }, this._cfg, { device_id: this._cfg.device_id || 'auto' });
    if (this._hass) this._form.hass = this._hass;
  }
  _changed(v) {
    const cfg = Object.assign({}, this._cfg, { boiler_image: v.boiler_image || '13' });
    if (v.height && +v.height !== DEFAULT_HEIGHT) cfg.height = +v.height; else delete cfg.height;
    if (v.device_id && v.device_id !== 'auto') cfg.device_id = v.device_id; else delete cfg.device_id;
    this._cfg = cfg;
    this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: cfg }, bubbles: true, composed: true }));
  }
}
if (!customElements.get('teklapelletcan-modern-card-editor')) customElements.define('teklapelletcan-modern-card-editor', TeklaModernCardEditor);

window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === 'teklapelletcan-modern-card')) {
  window.customCards.push({ type: 'teklapelletcan-modern-card', name: 'TeklaPelletModern-card', description: 'Panel kotła w stylu aplikacji Android – pulpit, instalacja, nastawy, parametry, harmonogramy, alarmy.', preview: true });
}
