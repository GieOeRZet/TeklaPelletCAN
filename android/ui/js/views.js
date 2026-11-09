// Widoki: pulpit, instalacja, kocioł, alarmy, parametry, menu.
import { nat, api } from './native.js';
import { S, v, num, pv, pn, level, subscribe } from './store.js';
import { $, el, esc, f1, fmt, toast, openSheet, closeSheet, ensureUnlocked, editPoint, callService, writePoint, confirmSheet } from './ui.js';

/** Zbiornik jak w oknie „Paliwo” oryginalnej karty: różowy korpus z czerwoną pokrywą i uchwytem, szary wskaźnik wypełniany od dołu
 *  żółtym pelletem, litera „E” (pusty). Wymiary z CSS karty (.ftk/.fth/.fbar); poziom = pct 0..100. Bez suwaka – tylko poziom. */
let tankSeq = 0;
const TANK = (pct, w = 96) => {
  const f = Math.max(0, Math.min(100, Number.isFinite(pct) ? pct : 0)) / 100, u = 'tk' + (++tankSeq);
  const barH = 327, barY = 95.8, fillH = Math.round(barH * f * 10) / 10;
  return `<svg width="${w}" viewBox="0 0 256 445" aria-label="zbiornik paliwa" data-tank="${Math.round(f * 100)}"><defs>
      <linearGradient id="${u}b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4b5b8"/><stop offset="1" stop-color="#f09aa2"/></linearGradient>
      <linearGradient id="${u}t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6604f"/><stop offset="1" stop-color="#e5352b"/></linearGradient>
      <pattern id="${u}p" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="10" fill="#f3e24f"/><rect x="5" width="5" height="10" fill="#e1c92f"/></pattern></defs>
    <rect x="1.25" y="1.25" width="253.5" height="442.5" fill="url(#${u}b)" stroke="#e0453b" stroke-width="2.5"/>
    <rect x="1.25" y="1.25" width="253.5" height="68.5" fill="url(#${u}t)"/><rect x="1.25" y="67" width="253.5" height="3" fill="#b8352c"/>
    <svg x="94.7" y="27" width="64" height="30" viewBox="0 0 42 20"><path d="M3 20V9Q3 2.2 9.5 2.2H32.5Q39 2.2 39 9V20" fill="none" stroke="#f9d3cf" stroke-width="4.4"/></svg>
    <rect x="97" y="${barY}" width="60.6" height="${barH}" fill="#6c7898" stroke="#e9edf8" stroke-width="2.5"/>
    <rect x="98.3" y="${(barY + barH - fillH).toFixed(1)}" width="58.1" height="${Math.max(0, fillH - 1.3).toFixed(1)}" fill="url(#${u}p)"/>
    <text x="64" y="412" font-size="42" font-weight="700" fill="#f5a21a" font-family="Roboto,sans-serif">E</text></svg>`;
};

/** Okno „Paliwo”: grafika zbiornika z poziomem pelletu (jak w karcie), ilość w kg z przyciskami ±1 kg (przytrzymanie powtarza),
 *  wpisanie wartości, szybkie kroki i ręczne podawanie paliwa. Zapis: punkt tank_kg. */
export function fuelSheet() {
  const cap = num('sensor.tekla_zbiornik_pojemnosc'), cur = num('sensor.tekla_zbiornik_paliwo'), days = num('sensor.tekla_paliwo_prognoza');
  const p = S.pointById.get('tank_kg') || { min: 0, max: 1500 };
  let val = Number.isFinite(cur) ? cur : 0;
  let feedT = null, feedLeft = 0;
  const sh = openSheet(`<h3>Paliwo</h3>
    <div style="display:flex;gap:18px;align-items:center">
      <div id="tk" style="flex:0 0 112px"></div>
      <div style="flex:1;text-align:center">
        <button class="ico" id="pl" style="width:56px;height:56px;margin:0 auto;font-size:28px">+</button>
        <div style="font-size:36px;font-weight:500;margin:6px 0" id="big"></div>
        <button class="ico" id="mi" style="width:56px;height:56px;margin:0 auto;font-size:28px">−</button>
        <div class="hint" id="info" style="margin-top:6px"></div></div></div>
    <div class="hint" style="margin-top:10px">Wpisz ilość lub użyj szybkich kroków</div>
    <div style="display:flex;gap:8px;align-items:center"><input class="t" id="kg" type="number" inputmode="numeric" min="${p.min}" max="${p.max}" step="1"><span class="dim">kg</span></div>
    <div class="chips"><button data-d="-50">−50</button><button data-d="-10">−10</button><button data-d="10">+10</button><button data-d="25">+25</button><button data-d="50">+50</button><button data-d="100">+100</button><button data-full="1">Pełny</button><button data-zero="1">Pusty</button></div>
    <div class="hint" style="margin-top:8px">Pojemność zbiornika (${Number.isFinite(cap) ? fmt(cap, 0) : '–'} kg) kocioł podaje tylko do odczytu.${Number.isFinite(days) ? ' Prognoza: ok. ' + fmt(days, 0) + ' dni.' : ''}</div>
    <button class="btn sec" id="feed">Podaj paliwo ręcznie (30 s)</button>
    <button class="btn acc" id="ok">Zapisz ilość paliwa</button><button class="btn sec" id="no">Anuluj</button>`, () => { clearInterval(feedT); });
  const inp = $('#kg', sh);
  const draw = () => {
    const pct = cap > 0 ? val / cap * 100 : NaN;
    $('#tk', sh).innerHTML = TANK(pct, 112);
    $('#big', sh).textContent = Math.round(val) + ' kg';
    $('#info', sh).innerHTML = Number.isFinite(pct) ? `${fmt(pct, 0)} % pojemności` + (val > cap ? '<br><span class="wr">powyżej pojemności</span>' : '') : '';
  };
  const setVal = x => { val = Math.max(p.min ?? 0, Math.min(p.max ?? 1500, Math.round(x))); inp.value = String(val); draw(); };
  inp.value = String(Math.round(val)); draw();
  inp.oninput = () => { const x = parseFloat(inp.value); val = Number.isFinite(x) ? x : 0; draw(); };
  sh.querySelectorAll('[data-d]').forEach(b => b.onclick = () => setVal(val + parseInt(b.dataset.d, 10)));
  $('[data-full]', sh).onclick = () => { if (Number.isFinite(cap)) setVal(cap); };
  $('[data-zero]', sh).onclick = () => setVal(0);
  // ±1 kg: stuknięcie = 1 kg, przytrzymanie (0,45 s) powtarza co 0,12 s – jak w karcie
  const hold = (btn, d) => {
    let t0 = null, t1 = null, held = false;
    const stop = () => { clearTimeout(t0); clearInterval(t1); };
    btn.addEventListener('pointerdown', () => { stop(); held = false; t0 = setTimeout(() => { held = true; setVal(val + d); t1 = setInterval(() => setVal(val + d), 120); }, 450); });
    ['pointerup', 'pointerleave', 'pointercancel'].forEach(e => btn.addEventListener(e, stop));
    btn.addEventListener('click', () => { if (held) { held = false; return; } setVal(val + d); });
  };
  hold($('#pl', sh), 1); hold($('#mi', sh), -1);
  // ręczne podawanie (jak ślimak w karcie): 30 s; ponowne stuknięcie wraca do automatu
  $('#feed', sh).onclick = async () => {
    if (feedLeft > 0) {
      clearInterval(feedT); feedLeft = 0; $('#feed', sh).textContent = 'Podaj paliwo ręcznie (30 s)';
      await callService('press', { entity_id: 'button.tekla_podajnik_automat' }, 'button'); return;
    }
    if (!(await confirmSheet('Podawanie paliwa', 'Włączyć ręczne podawanie paliwa na 30 s?', 'Podaj'))) return;
    if (!(await callService('press', { entity_id: 'button.tekla_podajnik_podaj_paliwo_30_s' }, 'button'))) return;
    feedLeft = 30;
  };
  $('#no', sh).onclick = closeSheet;
  $('#ok', sh).onclick = async () => {
    if (val > (p.max ?? 1500) || val < 0) { toast('Wartość poza zakresem'); return; }
    closeSheet();
    if (await writePoint('tank_kg', val)) toast('Ilość paliwa zapisana: ' + val + ' kg');
  };
}

/** Panel „Zasilanie" jak w oryginalnej karcie (szybki dostęp): włącznik kotła + szybki wybór trybu CO/CWU. */
export function zasilanieSheet() {
  const sh = openSheet(`<h3>Zasilanie</h3>
    <div class="sw"><span>Kocioł włączony</span><button class="tg" id="pw"></button></div>
    <div id="comode"></div><div id="cwmode"></div>`, () => unsub());
  const MODES4 = { 0: 'Off', 1: 'Eko', 2: 'Harmonogram', 3: 'Komfort' };
  const co = modeChips('Tryb CO', 'co_mode', MODES4, m => callService('select_option', { entity_id: 'select.tekla_co_tryb_ustaw', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_co_tryb');
  const cw = modeChips('Tryb CWU', 'cwu_mode', MODES4, m => callService('select_option', { entity_id: 'select.tekla_cwu_tryb_ustaw', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_cwu_tryb');
  $('#comode', sh).replaceWith(co); $('#cwmode', sh).replaceWith(cw);
  const pw = $('#pw', sh);
  const isOn = () => v('binary_sensor.tekla_kociol_wlaczony') === 'on' || v('switch.tekla_kociol_wlacz_wylacz') === 'on';
  pw.onclick = async () => { await callService(isOn() ? 'turn_off' : 'turn_on', { entity_id: 'switch.tekla_kociol_wlacz_wylacz' }, 'switch'); draw(); };
  const draw = () => { pw.classList.toggle('on', isOn()); updateBound(sh); };
  draw();
  const unsub = subscribe(draw);
}

const MODE = { 0: 'Czasowy auto', 1: 'Czasowy ręczny', 2: 'Auto', 3: 'Ręczny' };

/** Aktualizacja wartości w miejscu (bez przebudowy widoku): elementy z atrybutem data-b="funkcja". */
const binders = new Map();
export function bind(node, key, fn) { node.dataset.b = key; binders.set(key, fn); }
export function updateBound(root = document) {
  root.querySelectorAll('[data-b]').forEach(n => { const f = binders.get(n.dataset.b); if (f) { try { f(n); } catch (e) { /* pole puste */ } } });
}

const burnerPill = () => {
  const code = pn('burner_state_code'), t = pv('burner_state') || pv('sensor.tekla_palnik_stan');
  const name = (S.states.get('sensor.tekla_palnik_stan') || {}).state || '–';
  const cls = code === 5 ? '' : code === 10 ? 'r' : code === 0 || code === 9 ? 'd' : 'o';
  return `<span class="pill ${cls}">${esc(name)}${code === 5 && Number.isFinite(pn('burner_power')) ? ' · ' + fmt(pn('burner_power'), 0) + ' %' : ''}</span>`;
};
const alarmActive = () => v('binary_sensor.tekla_alarm_aktywny') === 'on';
const lastAlarm = () => (S.states.get('sensor.tekla_ostatni_alarm') || {}).state || '–';
const T = (id, d = 1) => f1(num(id)).replace('–', '–');

function boilerImg() {
  const t = S.config.boiler_image;
  return [11, 12, 13, 14].includes(t) && t !== 13 ? `img/panel/0${t}.png` : 'img/kociol.webp';
}

export function offlineBanner() {
  if (!S.cachedAt && S.online) return '';
  if (!S.loaded) return `<div class="banner off"><b>Brak połączenia z kotłem.</b> Nie mam jeszcze żadnych zapisanych danych z tego urządzenia.</div>`;
  const d = new Date(S.cachedAt);
  const when = d.toLocaleDateString() === new Date().toLocaleDateString() ? 'dziś' : d.toLocaleDateString();
  return `<div class="banner off"><b>Brak połączenia z kotłem.</b> Pokazuję ostatnie dane z <b>${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</b> (${when}). Wrócę do danych na żywo, gdy będziesz w domowej sieci.</div>`;
}


// ------------------------------------------------------------------ pulpit
export function pulpit(go) {
  const root = el(`<div>
    <div id="bn"></div>
    <div class="land2">
    <div class="hero" data-go="kociol"><div class="stage"><img id="kimg" alt="kocioł"></div>
      <div class="tx"><div class="big"><span data-b="t_boiler"></span><small> °C</small></div><div data-b="pill"></div></div>
      <div class="st"><div data-b="hero_sub"></div></div></div>
    <div class="g2">
      <button class="cd im" data-go="palnik"><small>Palnik</small><b data-b="burner_pct"></b><span class="u"> %</span><div class="dots"><span><i data-b="dot_blower"></i>dmuchawa</span><span><i data-b="dot_feeder"></i>podajnik</span></div><img src="img/palnik.webp" style="height:50px" alt=""></button>
      <button class="cd im" data-go="cwu"><small>CWU</small><b data-b="t_cwu"></b><span class="u"> °C</span><div class="u" data-b="cwu_sub"></div><img src="img/bojler.webp" style="height:76px;right:10px;top:8px;border-radius:8px" alt=""></button>
      <button class="cd" data-go="co"><small>CO</small><b data-b="t_co"></b><span class="u"> °C</span><div class="u" data-b="co_sub"></div></button>
      <button class="cd" data-fuel="1"><small>Paliwo</small><b data-b="fuel"></b><span class="u"> kg</span><div class="u" data-b="fuel_sub"></div><div style="position:absolute;right:12px;top:12px" data-b="hopper"></div></button>
      <button class="cd" data-go="instalacja"><small>Zewnętrzna</small><b data-b="t_out"></b><span class="u"> °C</span><div class="u" data-b="out_sub"></div></button>
      <button class="cd" data-go="instalacja"><small>Moc palnika</small><b data-b="kw"></b><span class="u"> kW</span><div class="u" data-b="kw_sub"></div></button>
      <button class="cd full" data-go="alarmy"><span data-b="alarm_ico" style="font-size:26px"></span><div><b data-b="alarm_t" style="font-size:16px"></b><div class="u" data-b="alarm_sub"></div></div></button>
    </div></div></div>`);
  const pct = () => { const x = pn('tank_pct'); return Number.isFinite(x) ? x : num('sensor.tekla_zbiornik_zapelnienie'); };
  const set = (k, fn) => { const n = root.querySelector(`[data-b="${k}"]`); if (n) bind(n, 'pulpit_' + k, fn); if (n) n.dataset.b = 'pulpit_' + k; };
  set('t_boiler', n => { n.textContent = f1(num('sensor.tekla_kociol_temperatura')); });
  set('pill', n => { n.innerHTML = burnerPill(); });
  set('hero_sub', n => { n.innerHTML = `zadana <b style="color:var(--txt)">${fmt(num('sensor.tekla_kociol_zadana_wynikowa'), 0)} °C</b> · tryb <b style="color:var(--txt)">${esc((S.states.get('sensor.tekla_kociol_tryb_pracy') || {}).state || '–')}</b><br>${v('binary_sensor.tekla_can_ok') === 'on' ? 'CAN OK' : '<span class="er">brak CAN</span>'}`; });
  set('burner_pct', n => { n.textContent = Number.isFinite(num('sensor.tekla_moc_palnika')) ? fmt(num('sensor.tekla_moc_palnika'), 0) : '–'; });
  set('dot_blower', n => { n.className = v('binary_sensor.tekla_dmuchawa_pracuje') === 'on' ? 'on' : ''; });
  set('dot_feeder', n => { n.className = (v('binary_sensor.tekla_podajnik_pracuje') === 'on' || v('binary_sensor.tekla_podajnik_palnika_pracuje') === 'on') ? 'on' : ''; });
  set('t_cwu', n => { n.textContent = f1(num('sensor.tekla_cwu_temperatura')); });
  set('cwu_sub', n => { n.innerHTML = `zadana ${fmt(num('sensor.tekla_cwu_zadana_wynikowa'), 0)} · pompa ${v('binary_sensor.tekla_cwu_pompa') === 'on' ? '<span class="ok">wł.</span>' : 'wył.'}`; });
  set('t_co', n => { n.textContent = f1(num('sensor.tekla_co_temperatura')); });
  set('co_sub', n => { n.innerHTML = `zadana ${fmt(num('sensor.tekla_co_zadana_wynikowa'), 0)} · pompa ${v('binary_sensor.tekla_co_pompa') === 'on' ? '<span class="ok">wł.</span>' : 'wył.'}`; });
  set('fuel', n => { n.textContent = fmt(num('sensor.tekla_zbiornik_paliwo'), 0); });
  set('fuel_sub', n => { const d = num('sensor.tekla_paliwo_prognoza'); n.textContent = Number.isFinite(d) ? `ok. ${fmt(d, 0)} dni` : `${fmt(pct(), 0)} %`; });
  set('hopper', n => { n.innerHTML = TANK(Number.isFinite(pct()) ? pct() : 0, 40); });
  set('t_out', n => { n.textContent = f1(num('sensor.tekla_temperatura_zewnetrzna')); });
  set('out_sub', n => { n.textContent = 'powrót ' + f1(num('sensor.tekla_temperatura_powrotu')) + ' °C'; });
  set('kw', n => { n.textContent = f1(num('sensor.tekla_palnik_moc')); });
  set('kw_sub', n => { n.textContent = 'palnik ' + fmt(num('sensor.tekla_temperatura_palnika'), 0) + ' °C'; });
  set('alarm_ico', n => { n.innerHTML = alarmActive() ? '<span class="er">⚠</span>' : '<span class="ok">✓</span>'; });
  set('alarm_t', n => { n.textContent = alarmActive() ? 'Alarm aktywny' : 'Brak alarmów'; n.className = alarmActive() ? 'er' : ''; });
  set('alarm_sub', n => { n.textContent = 'ostatni: ' + lastAlarm(); });
  root.querySelector('#kimg').src = boilerImg();
  root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  root.querySelectorAll('[data-fuel]').forEach(b => b.onclick = fuelSheet);
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); root.classList.toggle('offline', !!S.cachedAt); updateBound(root); } };
}

// ------------------------------------------------------------------ instalacja
export function instalacja(go) {
  const root = el(`<div class="flow"><div id="bn"></div>
    <button class="node" data-fuel="1"><span data-b="in_hop"></span><div><b>Zbiornik</b><span class="u" data-b="in_hop_t"></span></div><div class="r"><span class="pill" data-b="in_hop_p"></span></div></button>
    <div class="arrow">▼ ▼ ▼</div>
    <button class="node" data-go="palnik"><img src="img/palnik.webp" alt=""><div><b>Palnik</b><span class="u" data-b="in_burn_t"></span></div><div class="r"><b data-b="in_burn_p"></b></div></button>
    <div class="arrow">▼ ▼ ▼</div>
    <button class="node" data-go="kociol"><img src="${boilerImg()}" style="height:60px" alt=""><div><b>Kocioł</b><span class="u" data-b="in_k_t"></span></div><div class="r"><b data-b="in_k_p"></b></div></button>
    <div class="arrow" style="letter-spacing:70px">▼ ▼</div>
    <div class="split">
      <button class="node" data-go="co"><b>CO</b><span class="u" data-b="in_co_t"></span><b style="font-size:22px" data-b="in_co_p"></b><span class="u" data-b="in_co_v"></span></button>
      <button class="node" data-go="cwu"><b>CWU</b><span class="u" data-b="in_cwu_t"></span><b style="font-size:22px" data-b="in_cwu_p"></b></button>
    </div>
    <div class="sec" style="margin-top:12px"><h5>Dodatkowe</h5>
      <div class="row"><span>Temperatura powrotu</span><span class="v" data-b="in_ret"></span></div>
      <div class="row"><span>Temperatura palnika</span><span class="v" data-b="in_bt"></span></div>
      <div class="row"><span>Temperatura zewnętrzna</span><span class="v" data-b="in_out"></span></div>
      <div class="row"><span>Moc palnika</span><span class="v" data-b="in_kw"></span></div></div></div>`);
  const set = (k, fn) => { const n = root.querySelector(`[data-b="${k}"]`); if (n) { n.dataset.b = 'inst_' + k; binders.set('inst_' + k, fn); } };
  const pct = () => { const x = num('sensor.tekla_zbiornik_zapelnienie'); return Number.isFinite(x) ? x : 50; };
  set('in_hop', n => { n.innerHTML = TANK(pct(), 38); });
  set('in_hop_t', n => { n.textContent = `${fmt(num('sensor.tekla_zbiornik_paliwo'), 0)} / ${fmt(num('sensor.tekla_zbiornik_pojemnosc'), 0)} kg`; });
  set('in_hop_p', n => { n.textContent = fmt(pct(), 0) + ' %'; n.className = 'pill' + (v('binary_sensor.tekla_paliwo_rezerwa') === 'on' ? ' r' : ''); });
  set('in_burn_t', n => { n.innerHTML = `${esc((S.states.get('sensor.tekla_palnik_stan') || {}).state || '–')} · podajnik ${v('binary_sensor.tekla_podajnik_pracuje') === 'on' || v('binary_sensor.tekla_podajnik_palnika_pracuje') === 'on' ? '<span class="ok">wł.</span>' : 'wył.'}`; });
  set('in_burn_p', n => { n.textContent = Number.isFinite(num('sensor.tekla_moc_palnika')) ? fmt(num('sensor.tekla_moc_palnika'), 0) + ' %' : '–'; });
  set('in_k_t', n => { n.textContent = `zadana ${fmt(num('sensor.tekla_kociol_zadana_wynikowa'), 0)} °C · ${(S.states.get('sensor.tekla_kociol_tryb_pracy') || {}).state || '–'}`; });
  set('in_k_p', n => { n.textContent = f1(num('sensor.tekla_kociol_temperatura')) + ' °C'; });
  set('in_co_t', n => { n.innerHTML = `pompa ${v('binary_sensor.tekla_co_pompa') === 'on' ? '<span class="ok">wł.</span>' : 'wył.'} · zadana ${fmt(num('sensor.tekla_co_zadana_wynikowa'), 0)}`; });
  set('in_co_p', n => { n.textContent = f1(num('sensor.tekla_co_temperatura')) + ' °C'; });
  set('in_co_v', n => { n.textContent = ''; });
  set('in_cwu_t', n => { n.innerHTML = `pompa ${v('binary_sensor.tekla_cwu_pompa') === 'on' ? '<span class="ok">wł.</span>' : 'wył.'} · zadana ${fmt(num('sensor.tekla_cwu_zadana_wynikowa'), 0)}`; });
  set('in_cwu_p', n => { n.textContent = f1(num('sensor.tekla_cwu_temperatura')) + ' °C'; });
  set('in_ret', n => { n.textContent = f1(num('sensor.tekla_temperatura_powrotu')) + ' °C'; });
  set('in_bt', n => { n.textContent = f1(num('sensor.tekla_temperatura_palnika')) + ' °C'; });
  set('in_out', n => { n.textContent = f1(num('sensor.tekla_temperatura_zewnetrzna')) + ' °C'; });
  set('in_kw', n => { n.textContent = f1(num('sensor.tekla_palnik_moc')) + ' kW'; });
  root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  root.querySelectorAll('[data-fuel]').forEach(b => b.onclick = fuelSheet);
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); root.classList.toggle('offline', !!S.cachedAt); updateBound(root); } };
}

// ------------------------------------------------------------------ kocioł: nastawy i tryby
function stepperRow(title, pid, getUnit = '°C') {
  const id = 'st_' + pid;
  const n = el(`<div><div class="hint">${esc(title)}</div><button class="stepper" style="width:100%;text-align:center" data-edit="${pid}"><span style="width:46px;height:46px"></span><b data-b="${id}"></b><span style="width:46px;height:46px;color:var(--dim);font-size:13px;line-height:46px">edytuj</span></button></div>`);
  binders.set(id, x => { x.textContent = f1(pn(pid)) + ' ' + getUnit; });
  return n;
}
const norm = x => String(x == null ? '' : x).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ł/g, 'l').toLowerCase();
function modeChips(title, pid, labels, apply, entityId) {
  const id = 'mc_' + pid;
  const n = el(`<div><div class="hint" style="margin-top:8px">${esc(title)}</div><div class="chips" data-b="${id}"></div></div>`);
  binders.set(id, c => {
    const lblNow = (S.states.get(entityId) || {}).state;
    const hit = Object.entries(labels).find(([k, l]) => norm(l) === norm(lblNow));
    const cur = hit ? hit[0] : String(Math.round(pn(pid)));
    c.innerHTML = Object.entries(labels).map(([k, l]) => `<button data-k="${k}" class="${cur === k ? 'on' : ''}">${esc(l)}</button>`).join('');
    c.querySelectorAll('button').forEach(b => b.onclick = () => apply(parseInt(b.dataset.k, 10)));
  });
  return n;
}

/** Wiersz jednego punktu z katalogu (/api/v1/points) - uzywany i w ekranach domenowych (kociol/palnik/co/cwu),
 * i w "Wszystkich parametrach". Zapisywalny -> otwiera editPoint (sam rozpoznaje suwak/stepper czy opcje). */
function pointRow(p) {
  const b = el(`<button class="row ${p.writable ? 'nav2' : ''}" data-p="${esc(p.id)}"><span>${esc(p.name)}${p.writable ? '' : '<div class="hint">tylko odczyt</div>'}</span><span class="v" data-b="pv_${esc(p.id)}"></span></button>`);
  binders.set('pv_' + p.id, n => {
    const s = pv(p.id);
    let t = s === undefined || s === 'unknown' ? '–' : s;
    if (p.options && p.options[String(Math.round(parseFloat(s)))] !== undefined && !Number.isNaN(parseFloat(s))) t = p.options[String(Math.round(parseFloat(s)))];
    n.textContent = t + (p.unit && t !== '–' && !p.options ? ' ' + p.unit : '');
  });
  if (p.writable) b.onclick = () => editPoint(p.id);
  return b;
}

/** Dopisuje do sekcji (domenowej albo grupy w "Wszystkich parametrach") punkty podzielone na poziomy dostepu -
 * poziom 0 bez naglowka (juz tam sa recznie dobrane najwazniejsze pola), poziom 1/2 za wyraznym podkresleniem
 * "— POZIOM N —" (replika oryginalnej karty: wrench + numer poziomu). Zablokowany poziom jest CALKOWICIE
 * niewidoczny (zero sladu, zero przycisku) - dokladnie jak w oryginale: zwykly uzytkownik nie ma wiedziec,
 * ze cos tam jeszcze jest. Pojawia sie dopiero po PIN-ie danego poziomu (wpisywanym w Menu). */
function appendLevelGroups(container, points, shownLevel, { skipIds = new Set(), includeReadOnly = false } = {}) {
  const rest = points.filter(p => !skipIds.has(p.id) && (p.writable || includeReadOnly));
  const lvOf = p => (p.writable ? (p.level || 0) : -1);
  const base = rest.filter(p => lvOf(p) === 0);
  base.forEach(p => container.appendChild(pointRow(p)));
  for (const lv of [1, 2]) {
    if (shownLevel < lv) continue;
    const items = rest.filter(p => lvOf(p) === lv);
    if (!items.length) continue;
    container.appendChild(el(`<div class="lvh" data-lvh="${lv}">Poziom ${lv}</div>`));
    items.forEach(p => container.appendChild(pointRow(p)));
  }
  const ro = includeReadOnly ? rest.filter(p => lvOf(p) === -1) : [];
  if (ro.length) { container.appendChild(el('<div class="lvh" style="color:var(--dim)">Odczyty</div>')); ro.forEach(p => container.appendChild(pointRow(p))); }
}

function pointsByGroup() {
  const byGroup = {};
  for (const p of S.points) { const g = groupOf(p); (byGroup[g] = byGroup[g] || []).push(p); }
  return byGroup;
}

/** Ekran domenowy (Kocioł / Palnik / Ogrzewanie / Woda) – jak w oryginalnej karcie: osobny pełny ekran
 * dla każdej instalacji, z własnymi nastawami podzielonymi na poziomy dostępu. */
function domainScreen(build) {
  const root = el('<div><div id="bn"></div></div>');
  let shownLevel = -1;
  const draw = () => {
    shownLevel = level();
    root.innerHTML = ''; root.appendChild(el('<div id="bn"></div>'));
    const sec = (h) => { const s = el(`<div class="sec"><h5>${h}</h5></div>`); root.appendChild(s); return s; };
    build(root, sec, pointsByGroup(), shownLevel);
    root.querySelectorAll('[data-edit]').forEach(b => b.onclick = () => editPoint(b.dataset.edit));
    updateBound(root);
  };
  draw();
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); if (level() !== shownLevel) draw(); else updateBound(root); } };
}

export function kociol() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    const k = sec('Kocioł');
    k.append(stepperRow('Zadana temperatura kotła (ręczna)', 'boiler_set_manual'),
      modeChips('Tryb pracy kotła', 'boiler_mode', MODE, m => callService('tekla_estyma_set_boiler_mode', { mode: m }), 'sensor.tekla_kociol_tryb_pracy'));
    appendLevelGroups(k, byGroup['Kocioł'] || [], shownLevel, { skipIds: new Set(['boiler_set_manual', 'boiler_mode']) });
  });
}

export function palnik() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    appendLevelGroups(sec('Palnik'), byGroup['Palnik'] || [], shownLevel);
  });
}

export function ogrzewanie() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    const c = sec('Ogrzewanie (CO)');
    c.append(stepperRow('Zadana CO (ręczna)', 'ch1_set_manual'), stepperRow('Zadana CO – komfort', 'co_set_comfort'), stepperRow('Zadana CO – eko', 'co_set_eco'),
      modeChips('Tryb CO', 'co_mode', { 0: 'Off', 1: 'Eko', 2: 'Harmonogram', 3: 'Komfort' }, m => callService('select_option', { entity_id: 'select.tekla_co_tryb_ustaw', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_co_tryb'));
    appendLevelGroups(c, byGroup['CO'] || [], shownLevel, { skipIds: new Set(['ch1_set_manual', 'co_set_comfort', 'co_set_eco']) });
  });
}

export function cieplaWoda() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    const w = sec('Ciepła woda (CWU)');
    w.append(stepperRow('Zadana CWU – komfort', 'hw_set_comfort'), stepperRow('Zadana CWU – eko', 'hw_set_eco'),
      modeChips('Tryb CWU', 'cwu_mode', { 0: 'Off', 1: 'Eko', 2: 'Harmonogram', 3: 'Komfort' }, m => callService('select_option', { entity_id: 'select.tekla_cwu_tryb_ustaw', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_cwu_tryb'));
    w.append(el('<button class="btn sec" id="boost">Zagrzej CWU teraz</button>'));
    appendLevelGroups(w, byGroup['CWU'] || [], shownLevel, { skipIds: new Set(['hw_set_comfort', 'hw_set_eco']) });
    const b = $('#boost', root); if (b) b.onclick = async () => { if (await confirmSheet('Zagrzej CWU teraz', 'Włączyć jednorazowe dogrzanie wody?')) await writePoint('cwu_boost', 1); };
  });
}

// ------------------------------------------------------------------ alarmy
export function alarmy() {
  const root = el('<div><div id="bn"></div><div class="sec"><h5>Stan</h5><div class="row"><span>Alarm</span><span class="v" data-b="al_state"></span></div><div class="row"><span>Ostatni</span><span class="v" data-b="al_last"></span></div></div><div class="sec"><h5>Historia alarmów</h5><div id="alist"></div></div><button class="btn sec" id="ack">Potwierdź alarm</button></div>');
  binders.set('al_state', n => { n.innerHTML = alarmActive() ? '<span class="er">aktywny</span>' : '<span class="ok">brak</span>'; });
  binders.set('al_last', n => { n.textContent = lastAlarm(); });
  const fmtT = s => { const x = parseInt(s, 10); return x > 1e9 ? new Date(x * 1000).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : '–'; };
  const draw = () => {
    const rows = [];
    for (let i = 1; i <= 20; i++) {
      const e = S.states.get('sensor.tekla_alarm_wpis_' + i);
      if (!e || e.state === '-' || e.state === 'unknown') continue;
      const [txt, a, b] = String(e.state).split('|');
      rows.push(`<div class="row"><span>${esc(txt)}<div class="hint">${fmtT(a)} → ${parseInt(b, 10) > 1e9 ? fmtT(b) : 'trwa'}</div></span></div>`);
    }
    $('#alist', root).innerHTML = rows.join('') || '<div class="hint">Brak wpisów.</div>';
  };
  root.querySelector('#ack').onclick = async () => { if (await confirmSheet('Potwierdź alarm', 'Potwierdzić aktywny alarm w kotle?')) await callService('press', { entity_id: 'button.tekla_potwierdz_alarm' }, 'button'); };
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); draw(); updateBound(root); } };
}

// ------------------------------------------------------------------ parametry (z metadanych punktów)
export const GROUPS = [['Kocioł', /^(Kociol|Moc|Histereza|Wartosc|Korekta)/i], ['Palnik', /^(Palnik|Dmuchawa|Podajnik|Ilosc paliwa|Wentylator|Wymiennik)/i], ['CO', /^CO/i], ['CWU', /^CWU/i], ['Paliwo', /^(Zbiornik|Paliwo)/i], ['Alarmy', /^Alarm/i]];
export const groupOf = p => { for (const [g, re] of GROUPS) if (re.test(p.name)) return g; return 'Inne'; };

export function paramGroups(go) {
  const cnt = {};
  for (const p of S.points) { const g = groupOf(p); cnt[g] = (cnt[g] || 0) + 1; }
  const names = [...GROUPS.map(g => g[0]), 'Inne'].filter(g => cnt[g]);
  const root = el(`<div><div id="bn"></div><div class="sec"><h5>Parametry i odczyty</h5>${names.map(g => `<button class="row nav2" data-go="params/${g}"><span>${g}</span><span class="v">${cnt[g]}</span></button>`).join('')}</div>
    <div class="hint" style="padding:0 6px">Wszystkie punkty urządzenia – tak jak w oryginalnej karcie.</div></div>`);
  root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); } };
}

export function paramList(group) {
  const pts = S.points.filter(p => groupOf(p) === group);
  const root = el(`<div><div id="bn"></div><div id="plist"></div></div>`);
  const L = $('#plist', root);
  const lvOf = p => (p.writable ? (p.level || 0) : -1);          // -1 = tylko odczyt
  let shownLevel = -1;
  const row = p => {
    const b = el(`<button class="row ${p.writable ? 'nav2' : ''}" data-p="${esc(p.id)}"><span>${esc(p.name)}${p.writable ? '' : '<div class="hint">tylko odczyt</div>'}</span><span class="v" data-b="pv_${esc(p.id)}"></span></button>`);
    binders.set('pv_' + p.id, n => {
      const s = pv(p.id);
      let t = s === undefined || s === 'unknown' ? '–' : s;
      if (p.options && p.options[String(Math.round(parseFloat(s)))] !== undefined && !Number.isNaN(parseFloat(s))) t = p.options[String(Math.round(parseFloat(s)))];
      n.textContent = t + (p.unit && t !== '–' && !p.options ? ' ' + p.unit : '');
    });
    if (p.writable) b.onclick = () => editPoint(p.id);
    return b;
  };
  const section = (title, items) => { const s = el(`<div class="sec"><h5>${title}</h5></div>`); items.forEach(p => s.appendChild(row(p))); return s; };
  // jak w oryginalnej karcie: po odblokowaniu poziomu pojawia się wyraźny podział „— 1 —” / „— 2 —” z opcjami tego poziomu
  const draw = () => {
    shownLevel = level();
    L.innerHTML = '';
    const by = l => pts.filter(p => lvOf(p) === l);
    const base = by(0);
    if (base.length) L.appendChild(section('Ustawienia podstawowe', base));
    for (const lv of [1, 2]) {
      if (shownLevel < lv) continue;
      const items = by(lv);
      if (!items.length) continue;
      L.appendChild(el(`<div class="lvh" data-lvh="${lv}">Poziom ${lv}</div>`));
      L.appendChild(section(`Poziom ${lv}`, items));
    }
    const ro = by(-1);
    if (ro.length) L.appendChild(section('Odczyty (tylko do odczytu)', ro));
    updateBound(root);
  };
  draw();
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); if (level() !== shownLevel) draw(); else updateBound(root); } };
}

// ------------------------------------------------------------------ harmonogramy (CWU / CO / kocioł) – bit i = godzina i, jak w karcie
const SCH = [['CWU', 'sensor.tekla_cwu_harmonogram_rejestry', 0], ['CO', 'sensor.tekla_co_harmonogram_rejestry', 1], ['Kocioł', 'sensor.tekla_kociol_harmonogram_rejestry', 2]];
const DAYS = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'];
const schedBits = k => ((S.states.get(SCH[k][1]) || {}).state || '').split(' ').map(x => (/^[0-9A-Fa-f]{6}$/.test(x) ? parseInt(x, 16) : null));
const bandsText = bits => {
  if (bits == null) return 'brak odczytu';
  const o = []; let st = null;
  for (let i = 0; i <= 24; i++) { const b = i < 24 && ((bits >> i) & 1); if (b && st === null) st = i; if (!b && st !== null) { o.push(`${st}–${i}`); st = null; } }
  return o.length ? o.join(', ') + ' h' : 'wyłączone';
};
let schedKind = 1;

async function editDay(kind, day) {
  const cur = schedBits(kind)[day];
  if (cur == null) { toast('Brak odczytu tego dnia – poczekaj chwilę'); return; }
  if (!(await ensureUnlocked())) return;
  let bits = cur;
  const sh = openSheet(`<h3>${SCH[kind][0]} · ${DAYS[day]}</h3><div class="hint">Stuknij godziny, w których ma być włączone (podświetlone = włączone).</div>
    <div class="hgrid">${Array.from({ length: 24 }, (_, h) => `<button data-h="${h}" class="${(bits >> h) & 1 ? 'on' : ''}">${h}</button>`).join('')}</div>
    <div class="hint" id="txt"></div>
    <div class="chips"><button data-all="1">Wszystkie</button><button data-none="1">Żadna</button></div>
    <div class="hint" style="margin-top:8px">Zastosuj również do:</div>
    <div class="chips" id="cp"><button data-cp="wk">Pn–Pt</button><button data-cp="we">Sob–Nd</button><button data-cp="all">Cały tydzień</button></div>
    <button class="btn acc" id="ok">Zapisz</button><button class="btn sec" id="no">Anuluj</button>`);
  let copy = null;
  const draw = () => { sh.querySelectorAll('[data-h]').forEach(b => b.classList.toggle('on', !!((bits >> +b.dataset.h) & 1))); $('#txt', sh).textContent = bandsText(bits); };
  draw();
  sh.querySelectorAll('[data-h]').forEach(b => b.onclick = () => { bits ^= (1 << +b.dataset.h); draw(); });
  $('[data-all]', sh).onclick = () => { bits = 0xFFFFFF; draw(); };
  $('[data-none]', sh).onclick = () => { bits = 0; draw(); };
  $('#cp', sh).querySelectorAll('button').forEach(b => b.onclick = () => { copy = copy === b.dataset.cp ? null : b.dataset.cp; $('#cp', sh).querySelectorAll('button').forEach(x => x.classList.toggle('on', x.dataset.cp === copy)); });
  $('#no', sh).onclick = closeSheet;
  $('#ok', sh).onclick = async () => {
    const days = copy === 'wk' ? [0, 1, 2, 3, 4] : copy === 'we' ? [5, 6] : copy === 'all' ? [0, 1, 2, 3, 4, 5, 6] : [day];
    if (copy && !days.includes(day)) days.push(day);
    closeSheet();
    let ok = true;
    for (const d of days) ok = (await callService('tekla_estyma_set_schedule', { kind: SCH[kind][2], day: d, bits })) && ok;
    if (ok) toast(days.length > 1 ? 'Harmonogram zapisany dla ' + days.length + ' dni' : 'Harmonogram zapisany');
  };
}

export function harmonogram() {
  const root = el('<div><div id="bn"></div><div class="chips" id="kinds" style="margin:4px 0 8px"></div><div class="sec" id="days"></div><div class="hint" style="padding:0 6px">Godziny pracy w poszczególne dni tygodnia. Zmiany wymagają odblokowanej aplikacji.</div></div>');
  const today = (new Date().getDay() + 6) % 7;
  const draw = () => {
    $('#kinds', root).innerHTML = SCH.map((s, i) => `<button data-k="${i}" class="${i === schedKind ? 'on' : ''}">${s[0]}</button>`).join('');
    $('#kinds', root).querySelectorAll('button').forEach(b => b.onclick = () => { schedKind = +b.dataset.k; draw(); });
    const all = schedBits(schedKind);
    const box = $('#days', root); box.innerHTML = '<h5>' + SCH[schedKind][0] + ' · tydzień</h5>';
    DAYS.forEach((dn, d) => {
      const b = all[d];
      const r = el(`<button class="dayrow" data-d="${d}"><div class="dn"><b class="${d === today ? 'today' : ''}">${dn}${d === today ? ' · dziś' : ''}</b><span class="dim" style="font-size:12px">${bandsText(b)}</span></div>
        <div class="hbar">${Array.from({ length: 24 }, (_, h) => `<i class="${b != null && ((b >> h) & 1) ? 'on' : ''}"></i>`).join('')}</div>
        <div class="hscale"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div></button>`);
      r.onclick = () => editDay(schedKind, d);
      box.appendChild(r);
    });
  };
  draw();
  let sig = '';
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); const s = SCH.map(x => (S.states.get(x[1]) || {}).state).join('|'); if (s !== sig) { sig = s; draw(); } } };
}
