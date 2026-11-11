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


// Ikona grzejnika (kafelek CO na pulpicie) - glif "mdi:radiator" (ten sam co w menu karty classic),
// zeby wyglad byl spojny i czytelny zamiast recznie odrysowanego ksztaltu.
const RADI_SVG = `<svg class="ico" viewBox="0 0 24 24" fill="currentColor"><path d="M7.95,3L6.53,5.19L7.95,7.4H7.94L5.95,10.5L4.22,9.6L5.64,7.39L4.22,5.19L6.22,2.09L7.95,3M13.95,2.89L12.53,5.1L13.95,7.3L13.94,7.31L11.95,10.4L10.22,9.5L11.64,7.3L10.22,5.1L12.22,2L13.95,2.89M20,2.89L18.56,5.1L20,7.3V7.31L18,10.4L16.25,9.5L17.67,7.3L16.25,5.1L18.25,2L20,2.89M2,22V14A2,2 0 0,1 4,12H20A2,2 0 0,1 22,14V22H20V20H4V22H2M6,14A1,1 0 0,0 5,15V17A1,1 0 0,0 6,18A1,1 0 0,0 7,17V15A1,1 0 0,0 6,14M10,14A1,1 0 0,0 9,15V17A1,1 0 0,0 10,18A1,1 0 0,0 11,17V15A1,1 0 0,0 10,14M14,14A1,1 0 0,0 13,15V17A1,1 0 0,0 14,18A1,1 0 0,0 15,17V15A1,1 0 0,0 14,14M18,14A1,1 0 0,0 17,15V17A1,1 0 0,0 18,18A1,1 0 0,0 19,17V15A1,1 0 0,0 18,14Z"/></svg>`;

// ------------------------------------------------------------------ pulpit
export function pulpit(go) {
  const root = el(`<div>
    <div id="bn"></div>
    <div class="land2">
    <div class="hero" data-go="kociol"><div class="stage"><img id="kimg" alt="kocioł"></div>
      <div class="tx"><div class="big"><span data-b="t_boiler"></span><small> °C</small></div><div data-b="pill"></div></div>
      <div class="st"><div data-b="hero_sub"></div></div></div>
    <div class="g2">
      <button class="cd im" data-go="palnik"><small>Palnik</small><b data-b="burner_pct"></b><span class="u"> %</span><div class="dots"><span><i data-b="dot_ign"></i>zapalarka</span><span><i data-b="dot_blower"></i>dmuchawa</span><span><i data-b="dot_feeder"></i>podajnik</span><span><i data-b="dot_feeder2"></i>podajnik 2</span></div><img src="img/palnik.webp" style="height:50px" alt=""></button>
      <button class="cd im" data-go="cwu"><small>CWU</small><b data-b="t_cwu"></b><span class="u"> °C</span><div class="u" data-b="cwu_sub"></div><div class="dots"><span><i data-b="dot_cwu_pump"></i>pompa</span></div><img src="img/bojler.webp" style="height:76px;right:10px;top:8px;border-radius:8px" alt=""></button>
      <button class="cd im" data-go="co"><small>CO</small><b data-b="t_co"></b><span class="u"> °C</span><div class="u" data-b="co_sub"></div><div class="dots"><span><i data-b="dot_co_pump"></i>pompa</span><span><i data-b="dot_co_mixer"></i>mieszacz</span></div>${RADI_SVG}</button>
      <button class="cd" data-fuel="1"><small>Paliwo</small><b data-b="fuel"></b><span class="u"> kg</span><div class="u" data-b="fuel_sub"></div><div style="position:absolute;right:12px;top:12px" data-b="hopper"></div></button>
      <button class="cd" data-go="instalacja"><small>Zewnętrzna</small><b data-b="t_out"></b><span class="u"> °C</span><div class="u" data-b="out_sub"></div></button>
      <button class="cd" data-go="instalacja"><small>Moc palnika</small><b data-b="kw"></b><span class="u"> kW</span><div class="u" data-b="kw_sub"></div></button>
    </div>
    <button class="cd full" data-go="alarmy" data-b="alarm_card"><span data-b="alarm_ico" style="font-size:26px"></span><div><b data-b="alarm_t" style="font-size:16px"></b><div class="u" data-b="alarm_sub"></div></div></button>
    </div></div>`);
  const pct = () => { const x = pn('tank_pct'); return Number.isFinite(x) ? x : num('sensor.tekla_zbiornik_zapelnienie'); };
  const set = (k, fn) => { const n = root.querySelector(`[data-b="${k}"]`); if (n) bind(n, 'pulpit_' + k, fn); if (n) n.dataset.b = 'pulpit_' + k; };
  set('t_boiler', n => { n.textContent = f1(num('sensor.tekla_kociol_temperatura')); });
  set('pill', n => { n.innerHTML = burnerPill(); });
  set('hero_sub', n => { n.innerHTML = `zadana <b style="color:var(--txt)">${fmt(num('sensor.tekla_kociol_zadana_wynikowa'), 0)} °C</b> · tryb <b style="color:var(--txt)">${esc((S.states.get('sensor.tekla_kociol_tryb_pracy') || {}).state || '–')}</b><br>${v('binary_sensor.tekla_can_ok') === 'on' ? 'CAN OK' : '<span class="er">brak CAN</span>'}`; });
  set('burner_pct', n => { n.textContent = Number.isFinite(num('sensor.tekla_moc_palnika')) ? fmt(num('sensor.tekla_moc_palnika'), 0) : '–'; });
  set('dot_ign', n => { const x = num('sensor.tekla_palnik_zapalarka'); n.className = Number.isFinite(x) && x > 0 ? 'on' : ''; });
  set('dot_blower', n => { n.className = v('binary_sensor.tekla_dmuchawa_pracuje') === 'on' ? 'on' : ''; });
  set('dot_feeder', n => { n.className = v('binary_sensor.tekla_podajnik_pracuje') === 'on' ? 'on' : ''; });
  set('dot_feeder2', n => { n.className = v('binary_sensor.tekla_podajnik_palnika_pracuje') === 'on' ? 'on' : ''; });
  set('t_cwu', n => { n.textContent = f1(num('sensor.tekla_cwu_temperatura')); });
  set('cwu_sub', n => { n.textContent = `zadana ${fmt(num('sensor.tekla_cwu_zadana_wynikowa'), 0)} °C`; });
  set('dot_cwu_pump', n => { n.className = v('binary_sensor.tekla_cwu_pompa') === 'on' ? 'on' : ''; });
  set('t_co', n => { n.textContent = f1(num('sensor.tekla_co_temperatura')); });
  set('co_sub', n => { n.textContent = `zadana ${fmt(num('sensor.tekla_co_zadana_wynikowa'), 0)} °C`; });
  set('dot_co_pump', n => { n.className = v('binary_sensor.tekla_co_pompa') === 'on' ? 'on' : ''; });
  set('dot_co_mixer', n => { const x = num('sensor.tekla_mieszacz_co1_stan'); n.className = Number.isFinite(x) && x > 0 ? 'on' : ''; });
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
  set('alarm_card', n => { n.classList.toggle('alarm-active', alarmActive()); });
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
// Punkty 0/1 (bez opcji nazwanych) - prawdziwy przelacznik wl/wyl zamiast wiersza z liczba i
// strzalka (klik na caly wiersz jak wczesniej - editPoint() juz ma galaz dla bool: zapis od razu,
// z potwierdzeniem na poziomie 1/2 - tu zmienia sie tylko wyglad, nie logika zapisu).
function pointRow(p) {
  const isBool = p.writable && !p.options && p.min === 0 && p.max === 1 && (p.step || 1) === 1;
  const b = isBool
    ? el(`<button class="row" data-p="${esc(p.id)}"><span>${esc(p.name)}</span><span class="tg" data-b="pv_${esc(p.id)}"></span></button>`)
    : el(`<button class="row ${p.writable ? 'nav2' : ''}" data-p="${esc(p.id)}"><span>${esc(p.name)}${p.writable ? '' : '<div class="hint">tylko odczyt</div>'}</span><span class="v" data-b="pv_${esc(p.id)}"></span></button>`);
  binders.set('pv_' + p.id, n => {
    const s = pv(p.id);
    if (isBool) { n.classList.toggle('on', Math.round(parseFloat(s)) === 1); return; }
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
function appendLevelGroups(container, points, shownLevel, { skipIds = new Set(), includeReadOnly = false, order = null } = {}) {
  const rest = points.filter(p => !skipIds.has(p.id) && (p.writable || includeReadOnly));
  const lvOf = p => (p.writable ? (p.level || 0) : -1);
  // order: kolejnosc dokladnie jak w oryginalnym panelu (zweryfikowana zdjeciami ekranu) - punkty spoza
  // tej listy (np. nowe w przyszlosci) ladują sie na koniec swojego poziomu, nic nie znika.
  const sortByOrder = arr => {
    if (!order) return arr;
    const idx = id => { const i = order.indexOf(id); return i < 0 ? 1e9 : i; };
    return arr.slice().sort((a, b) => idx(a.id) - idx(b.id));
  };
  const base = sortByOrder(rest.filter(p => lvOf(p) === 0));
  base.forEach(p => container.appendChild(pointRow(p)));
  for (const lv of [1, 2]) {
    if (shownLevel < lv) continue;
    const items = sortByOrder(rest.filter(p => lvOf(p) === lv));
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

// Kolejnosc dokladnie jak na prawdziwym panelu (sprawdzona zdjeciami ekranu Kociol -> NASTAWY).
const ORDER_KOCIOL = ['boiler_hyst_on', 'boiler_hyst_off', 'boiler_pump_min', 'boil_pump_run', 'boiler_ret_min', 'boiler_mixer_time', 'boil_fuel_reserve'];
export function kociol() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    const k = sec('Kocioł');
    k.append(stepperRow('Zadana temperatura kotła (ręczna)', 'boiler_set_manual'),
      modeChips('Tryb pracy kotła', 'boiler_mode', MODE, m => callService('tekla_estyma_set_boiler_mode', { mode: m }), 'sensor.tekla_kociol_tryb_pracy'));
    appendLevelGroups(k, byGroup['Kocioł'] || [], shownLevel, { skipIds: new Set(['boiler_set_manual', 'boiler_mode']), order: ORDER_KOCIOL });
  });
}

// Krzywa (np. modulacji dmuchawy) - w oryginale osobny ekran z Menu: wiersz w liście nastaw ("Moc
// dmuchawy modulacja [%]" / "Wentylator wspomagający [%]") otwiera okno z wykresem. Tu ten sam uklad:
// zwykly wiersz z chevronem w miejscu nastaw -> dotkniecie otwiera okno (curveSheet).
// Obsluga jak w oryginale: dotkniecie punktu zaznacza go (aktywny, podswietlony) - mozna go wtedy
// przeciagac palcem (zgrubnie) ALBO korygowac +/- po prawej (precyzyjnie, o jeden krok). Zapis
// TYLKO po "Zapisz" (jak kazda inna nastawa w aplikacji - nigdy na zywo w trakcie przeciagania czy
// klikania +/-): zmiany siedza lokalnie w oknie, przycisk "Zapisz" pojawia sie gdy cos sie zmienilo
// i wysyla na raz wszystkie zmienione punkty.
const CHART_ICO = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px"><path d="M3 17l5-5 4 3 7-8"/></svg>';
function curveRow(ids, xLabels, title) {
  const b = el(`<button class="row nav2"><span>${esc(title)}</span><span class="v">${CHART_ICO}</span></button>`);
  b.onclick = () => curveSheet(ids, xLabels, title);
  return b;
}
function curveSheet(ids, xLabels, title) {
  const pts = ids.map(id => S.pointById.get(id));
  const step = pts.find(p => p && p.step)?.step || 1;
  const dc = step < 1 ? 1 : 0;
  const lo = Math.min(...pts.map(p => p ? p.min : 0)), hi = Math.max(...pts.map(p => p ? p.max : 100));
  // PAD_L/PAD_R = krawedzie linii siatki (odstep miedzy skala Y a wykresem zostaje). PTS_INSET dodatkowo
  // wsuwa same punkty do srodka wzgledem tych linii, zeby pierwszy/ostatni punkt nie siedzial dokladnie
  // na krawedzi siatki, tylko kawalek dalej (linie siatki sa szersze niz rozstaw punktow).
  const W = 100, H = 54, PAD_L = 17, PAD_R = 2, PAD_T = 7, PTS_INSET = 6, n = ids.length;
  const X = i => n > 1 ? (i / (n - 1)) * (W - PAD_L - PAD_R - 2 * PTS_INSET) + PAD_L + PTS_INSET : (W + PAD_L) / 2;
  const Y = v => Number.isFinite(v) ? PAD_T + H - ((v - lo) / (hi - lo)) * H : PAD_T + H / 2;
  const Vfrom = y => lo + (1 - Math.max(0, Math.min(H, y - PAD_T)) / H) * (hi - lo);
  const snap = v => Math.round(Math.max(lo, Math.min(hi, v)) / step) * step;
  // Linie siatki co 20% zakresu (0/20/40/60/80/100%) z wartoscia opisana po lewej - "podzialka" osi Y,
  // ta sama gestosc co opisy na osi X.
  const grid = [0, 0.2, 0.4, 0.6, 0.8, 1].map(f => {
    const gv = Math.round((lo + (hi - lo) * (1 - f)) / step) * step;
    const gy = PAD_T + f * H;
    return `<line x1="${PAD_L}" y1="${gy.toFixed(1)}" x2="${W - PAD_R}" y2="${gy.toFixed(1)}" stroke="var(--line)" stroke-width="0.6"/>
      <text x="${(PAD_L - 8).toFixed(1)}" y="${(gy + 1.6).toFixed(1)}" font-size="4.6" fill="var(--dim)" text-anchor="end">${fmt(gv, dc)}</text>`;
  }).join('');
  // Elementy SVG punktow tworzone RAZ (nie przy kazdym przerysowaniu) - zamiana innerHTML w trakcie
  // przeciagania niszczylaby wlasnie przeciagany element (i jego pointer capture) w polowie gestu.
  // Etykieta pierwszego punktu przesunieta w prawo (zamiast wyosiowana na nim) - inaczej nachodzi na
  // opisy osi Y, ktore siedza dokladnie w tym samym miejscu po lewej stronie wykresu.
  const ptsSvg = ids.map((id, i) => `
    <text data-t="${i}" x="${(i === 0 ? X(i) + 3 : X(i)).toFixed(1)}" font-size="5" fill="var(--txt)" text-anchor="${i === 0 ? 'start' : 'middle'}"></text>
    <circle data-k="${i}" r="3.4"></circle>`).join('');
  const sh = openSheet(`<h3>${esc(title)}</h3>
    <div style="display:flex;align-items:center;gap:10px">
      <svg viewBox="0 0 ${W} ${PAD_T + H + 14}" style="flex:1 1 auto;min-width:0;height:160px;overflow:visible;touch-action:none">
        <g id="grid">${grid}</g>
        <polyline id="ln" points="" fill="none" stroke="var(--acc)" stroke-width="1.6" vector-effect="non-scaling-stroke"/>
        <g id="pts">${ptsSvg}</g>
        ${xLabels.map((l, i) => `<text x="${X(i).toFixed(1)}" y="${PAD_T + H + 10}" font-size="4.6" fill="var(--dim)" text-anchor="middle">${esc(l)}</text>`).join('')}
      </svg>
      <div style="display:flex;flex-direction:column;gap:10px;flex:0 0 auto">
        <button class="ico" id="pl" style="width:44px;height:44px;font-size:22px">+</button>
        <button class="ico" id="mi" style="width:44px;height:44px;font-size:22px">−</button>
      </div>
    </div>
    <div class="hint" style="margin-top:4px">Dotknij punkt, aby go wybrać - przeciągnij palcem (zgrubnie) albo koryguj +/− (precyzyjnie).</div>
    <button class="btn acc hideable" id="save" style="margin-top:8px">Zapisz</button>
    <button class="btn sec" id="no">Zamknij</button>`);
  const svg = $('svg', sh), ln = $('#ln', sh), saveBtn = $('#save', sh), plBtn = $('#pl', sh), miBtn = $('#mi', sh);
  const circles = sh.querySelectorAll('#pts circle'), texts = sh.querySelectorAll('#pts text[data-t]');
  let orig = ids.map(id => pn(id));
  let vals = orig.slice();
  let sel = -1;
  const dirty = () => vals.some((v, i) => v !== orig[i]);
  const redraw = () => {
    ln.setAttribute('points', vals.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(' '));
    vals.forEach((v, i) => {
      circles[i].setAttribute('cx', X(i).toFixed(1)); circles[i].setAttribute('cy', Y(v).toFixed(1));
      circles[i].setAttribute('r', i === sel ? '4.2' : '3.4');
      circles[i].setAttribute('stroke', i === sel ? 'var(--acc)' : 'none');
      circles[i].setAttribute('stroke-width', i === sel ? '2' : '0');
      circles[i].setAttribute('fill', v !== orig[i] ? '#fff' : 'var(--acc)');
      const yv = Y(v), below = yv - PAD_T < 9;
      texts[i].setAttribute('y', (below ? yv + 9 : yv - 5).toFixed(1));
      texts[i].textContent = Number.isFinite(v) ? fmt(v, dc) : '-';
    });
    saveBtn.classList.toggle('hideable', !dirty());   // miejsce na przycisk zawsze zarezerwowane (visibility, nie display) - bez skoku wysokosci okienka
    plBtn.classList.toggle('dis', sel < 0); miBtn.classList.toggle('dis', sel < 0);
  };
  const toSvgY = clientY => { const r = svg.getBoundingClientRect(); return (clientY - r.top) / r.height * (PAD_T + H + 14); };
  circles.forEach(c => {
    const i = +c.dataset.k;
    let dragging = false;
    c.style.cursor = 'pointer';
    c.addEventListener('pointerdown', e => { dragging = true; sel = i; c.setPointerCapture(e.pointerId); redraw(); });
    c.addEventListener('pointermove', e => {
      if (!dragging) return;
      vals[i] = snap(Vfrom(toSvgY(e.clientY)));
      redraw();
    });
    const finish = () => { dragging = false; };
    c.addEventListener('pointerup', finish);
    c.addEventListener('pointercancel', finish);
  });
  redraw();
  plBtn.onclick = () => { if (sel < 0) return; vals[sel] = snap(Math.min(hi, vals[sel] + step)); redraw(); };
  miBtn.onclick = () => { if (sel < 0) return; vals[sel] = snap(Math.max(lo, vals[sel] - step)); redraw(); };
  $('#no', sh).onclick = closeSheet;
  saveBtn.onclick = async () => {
    let ok = true;
    for (let i = 0; i < ids.length; i++) if (vals[i] !== orig[i]) { if (!(await writePoint(ids[i], vals[i]))) ok = false; }
    if (!ok) vals = ids.map(id => pn(id));
    orig = vals.slice();
    redraw();
  };
}

// Kolejnosc dokladnie jak na prawdziwym panelu (sprawdzona zdjeciami ekranu Palnik -> NASTAWY): dwie
// krzywe (dmuchawa, wentylator wspomagajacy) sa wierszami w tym samym miejscu co na urzadzeniu, nie
// osobnymi "wynalezionymi" ekranami.
const FANMOD_IDS = ['fan_mod_1', 'fan_mod_2', 'fan_mod_3', 'fan_mod_4', 'fan_mod_5'];
const EXHC_IDS = ['exh_c1', 'exh_c2', 'exh_c3', 'exh_c4', 'exh_c5'];
const ORDER_PALNIK_0 = ['air_corr', 'power_min', 'power_max', 'fuel_heat', 'fuel_test'];
const ORDER_PALNIK_1 = [
  '__fanmod__', 'p_feed_max', 'p_prefeed', 'p_photo', 'p_blow_ign', 'p_blow_glow', 'p_blow_stop',
  'p_glow_time', 'p_glow_fuel', 'p_stop_time', 'p_lambda', 'p_o2_30', 'p_o2_100', 'p_cleans',
  'k_predose_g', 'k_egt_min', 'k_egt_max', 'k_exch_int', '__exhc__',
  'p_clean_gap', 'p_pause_time', 'p_pause_power', 'p_pause_blow',
];
const ORDER_PALNIK_2 = ['k_nominal', 'p_inertia', 'p_grate_time', 'p_burner_feed', 'p_feeder_period', 'p_min_rpm'];
export function palnik() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    // feeder_mode/blower_mode ("Test wyjsc") to w oryginale osobna strona z Menu, nie czesc ekranu Palnik.
    const skip = new Set(['feeder_mode', 'blower_mode', ...FANMOD_IDS, ...EXHC_IDS]);
    const byId = new Map((byGroup['Palnik'] || []).map(p => [p.id, p]));
    const p = sec('Palnik');
    ORDER_PALNIK_0.forEach(id => { const pt = byId.get(id); if (pt && !skip.has(id)) p.appendChild(pointRow(pt)); });
    if (shownLevel >= 1) {
      p.appendChild(el('<div class="lvh" data-lvh="1">Poziom 1</div>'));
      ORDER_PALNIK_1.forEach(id => {
        if (id === '__fanmod__') { p.appendChild(curveRow(FANMOD_IDS, ['20%', '40%', '60%', '80%', '100%'], 'Moc dmuchawy modulacja [%]')); return; }
        if (id === '__exhc__') { p.appendChild(curveRow(EXHC_IDS, ['1', '2', '3', '4', '5'], 'Wentylator wspomagający [%]')); return; }
        const pt = byId.get(id); if (pt && !skip.has(id)) p.appendChild(pointRow(pt));
      });
    }
    if (shownLevel >= 2) {
      p.appendChild(el('<div class="lvh" data-lvh="2">Poziom 2</div>'));
      ORDER_PALNIK_2.forEach(id => { const pt = byId.get(id); if (pt && !skip.has(id)) p.appendChild(pointRow(pt)); });
    }
  });
}

/** "Konfiguracja" (kotla) jak w oryginale: profil instalacji odczytany z kotla (sensor "conf_txt" -
 * ciag liczb rozdzielonych spacja, dekodowany tak samo jak w oryginalnej karcie). Widoczna w Menu od
 * poziomu 1, ostatnia pozycja ("Dmuchawa z HALL") dopiero od poziomu 2 - identycznie jak w oryginale. */
export function konfiguracja() {
  const root = el('<div><div id="bn"></div></div>');
  let shownLevel = -1;
  const draw = () => {
    shownLevel = level();
    root.innerHTML = ''; root.appendChild(el('<div id="bn"></div>'));
    const raw = (v('sensor.tekla_konfiguracja_kotla') || '').trim().split(/\s+/);
    const g = i => (/^-?\d+$/.test(raw[i] || '') ? parseInt(raw[i], 10) : null);
    const onoff = i => { const x = g(i); return x == null ? '-' : (x ? 'WŁ' : 'WYŁ'); };
    const lst = (i, a) => { const x = g(i); return x == null ? '-' : (a[x] != null ? a[x] : String(x)); };
    const numv = i => { const x = g(i); return x == null ? '-' : String(x); };
    const cap = num('sensor.tekla_zbiornik_pojemnosc');
    const sec = el('<div class="sec"><h5>Konfiguracja</h5></div>'); root.appendChild(sec);
    const row = (n, val) => sec.appendChild(el(`<div class="row"><span>${esc(n)}</span><span class="v">${esc(String(val))}</span></div>`));
    row('Autokonfiguracja', onoff(0));
    row('Główny moduł IO', lst(1, ['BIG', 'CAN IO']));
    row('Ilość obwodów grzewczych', '-');
    row('Czujnik temperatury zewnętrznej', lst(2, ['brak', 'CTZ1', 'CAN']));
    row('Uśrednianie temp. zewnętrznej [h]', numv(3));
    row('Ciepła woda użytkowa', onoff(4));
    row('Solary', onoff(5));
    row('Bufor', onoff(6));
    row('Moduł Lambda', onoff(7));
    row('Czujnik rezerwy paliwa', onoff(8));
    row('Pojemność zbiornika paliwa [kg]', Number.isFinite(cap) ? fmt(cap, 0) : '-');
    row('Rezerwa zbiornika paliwa [kg]', numv(9));
    row('Czujnik powrotu do kotła', onoff(10));
    row('Numer profilu', numv(11));
    row('Pompa kotłowa', lst(12, ['ładująca', 'ochrony powrotu']));
    row('Kaskada master', onoff(13));
    row('Czujnik ciśnienia', onoff(14));
    row('Dodatkowy magazyn paliwa', onoff(15));
    row('Pomiar energii', onoff(16));
    row('Kopiuj nastawy z innego sterownika', '-');
    if (shownLevel >= 2) row('Dmuchawa z HALL', onoff(17));
  };
  draw();
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); if (level() !== shownLevel) draw(); } };
}

/** "Test wyjść" jak w oryginale (21 pozycji, dokladnie w tej kolejnosci i z tymi rejestrami co na prawdziwym
 * panelu - sprawdzone zdjeciami ekranu i stara integracja ESPHome, PelletCAN_packages.yaml, akcja set_output):
 * kazdy wiersz to trzy zwarte pola "A / OFF / ON" (pompy/dmuchawy/podajniki) albo "A / CLOSE / OPEN"
 * (mieszacze, ruszt) z ptaszkiem na aktywnym trybie - bez lampki stanu (oryginal jej tu nie ma). */
const TST_LABELS = { '0': 'A', '1': 'OFF', '2': 'ON' };
const TST_LABELS_CO = { '0': 'A', '1': 'CLOSE', '2': 'OPEN' };
let tstSeq = 0;
// Encje trybow testowych nie maja wlasnej liczbowej wartosci - kociol zglasza tylko etykiete tekstowa
// (sensor "..._tryb..."), wiec biezacy klucz trzeba dopasowac po tekscie, dokladnie jak w modeChips() wyzej
// (bez tego pn(id) zawsze NaN i ptaszek nigdy by sie nie zaznaczal, mimo ze zapis dziala).
function testOutRow(id, label, textEntityId, closeOpen) {
  const p = S.pointById.get(id);
  const labels = closeOpen ? TST_LABELS_CO : TST_LABELS;
  const opts = {}; if (p && p.options) Object.entries(p.options).forEach(([k]) => { opts[k] = labels[k] || k; });
  const r = el(`<div class="row tst"><span class="l">${esc(label)}</span><span class="abo">${Object.entries(opts).map(([k, l]) => `<em data-k="${k}"><small>${esc(l)}</small><b></b></em>`).join('')}</span></div>`);
  r.querySelectorAll('.abo em').forEach(e => e.onclick = () => writePoint(id, parseInt(e.dataset.k, 10)));
  bind(r, 'tst_' + (tstSeq++), n => {
    const lblNow = (S.states.get(textEntityId) || {}).state;
    const hit = Object.entries(p && p.options || {}).find(([k, l]) => norm(l) === norm(lblNow));
    const x = pn(id);
    const cur = hit ? hit[0] : (Number.isFinite(x) ? String(Math.round(x)) : null);
    n.querySelectorAll('.abo em').forEach(e => { const ck = e.dataset.k === cur; e.classList.toggle('ck', ck); e.querySelector('b').textContent = ck ? '✓' : ''; });
  });
  return r;
}
// Dmuchawa/WentWyc maja na panelu dodatkowo suwak mocy [%] w tym samym wierszu - u nas osobny wiersz
// zapisywalny (otwiera standardowy edytor +/-, jak kazdy inny punkt liczbowy w appce).
function testPctRow(id, label) {
  const r = el(`<button class="row nav2"><span>${esc(label)}</span><span class="v"></span></button>`);
  r.onclick = () => editPoint(id);
  bind(r.querySelector('.v'), 'tstpct_' + id, n => { const x = pn(id); n.textContent = (Number.isFinite(x) ? Math.round(x) : '–') + ' %'; });
  return r;
}
export function testWyjsc() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    const t = sec('Test wyjść');
    if (shownLevel < 2) { t.append(el('<div class="hint">Sterowanie od poziomu 2 (PIN 0999): Menu → Poziom kotła.</div>')); return; }
    t.append(testOutRow('cwu_pump_mode', 'Pompa CWU', 'sensor.tekla_pompa_cwu_tryb_testowy'));
    t.append(testOutRow('boiler_pump_mode', 'Pompa kotłowa', 'sensor.tekla_pompa_kotlowa_tryb_testowy'));
    t.append(testOutRow('solar_pump_mode', 'Pompa solarna', 'sensor.tekla_pompa_solarna_tryb_testowy'));
    t.append(testOutRow('feeder_mode', 'Podajnik', 'sensor.tekla_podajnik_tryb'));
    t.append(testOutRow('grate_mode', 'Ruszt', 'sensor.tekla_ruszt_tryb_testowy', true));
    t.append(testOutRow('exchanger_mode', 'Wymiennik', 'sensor.tekla_wymiennik_tryb_testowy'));
    t.append(testOutRow('igniter_mode', 'Zapalarka', 'sensor.tekla_zapalarka_tryb_testowy'));
    t.append(testOutRow('burner_feeder_mode', 'Podajnik palnika', 'sensor.tekla_podajnik_palnika_tryb_testowy'));
    t.append(testOutRow('fuel_transporter_mode', 'Magazyn paliwa transporter', 'sensor.tekla_magazyn_paliwa_transporter_tryb_testowy'));
    t.append(testOutRow('fuel_storage_feeder_mode', 'Magazyn paliwa podajnik', 'sensor.tekla_magazyn_paliwa_podajnik_tryb_testowy'));
    t.append(testOutRow('blower_mode', 'Dmuchawa', 'sensor.tekla_dmuchawa_tryb'));
    t.append(testPctRow('blower_test_pct', 'Dmuchawa – moc testowa'));
    t.append(testOutRow('exh_fan_mode', 'WentWyc', 'sensor.tekla_wentwyc_tryb_testowy'));
    t.append(testPctRow('exh_fan_pct', 'WentWyc – moc testowa'));
    t.append(testOutRow('co1_pump_mode', 'Pompa CO1', 'sensor.tekla_pompa_co1_tryb_testowy'));
    t.append(testOutRow('co2_pump_mode', 'Pompa CO2', 'sensor.tekla_pompa_co2_tryb_testowy'));
    t.append(testOutRow('co3_pump_mode', 'Pompa CO3', 'sensor.tekla_pompa_co3_tryb_testowy'));
    t.append(testOutRow('co4_pump_mode', 'Pompa CO4', 'sensor.tekla_pompa_co4_tryb_testowy'));
    t.append(testOutRow('co1_mixer_mode', 'Mieszacz CO1', 'sensor.tekla_mieszacz_co1_tryb_testowy', true));
    t.append(testOutRow('co2_mixer_mode', 'Mieszacz CO2', 'sensor.tekla_mieszacz_co2_tryb_testowy', true));
    t.append(testOutRow('co3_mixer_mode', 'Mieszacz CO3', 'sensor.tekla_mieszacz_co3_tryb_testowy', true));
    t.append(testOutRow('co4_mixer_mode', 'Mieszacz CO4', 'sensor.tekla_mieszacz_co4_tryb_testowy', true));
    t.append(testOutRow('ret_mixer_mode', 'Mieszacz powrotu', 'sensor.tekla_mieszacz_powrotu_tryb_testowy', true));
  });
}

// Kolejnosc dokladnie jak na prawdziwym panelu (sprawdzona zdjeciami ekranu Ogrzewanie 1 -> NASTAWY).
const ORDER_CO = [
  'co1_hyst', 'co1_calib', 'co1_mode', 'co1_curve_m20', 'co1_curve_0', 'co1_curve_10',
  'co1_source', 'co1_src_inc', 'co1_room_sensor', 'co1_tmax', 'co1_co_sensor', 'co1_corr',
  'co1_out_comf', 'co1_out_eco', 'co1_lower', 'co1_pump_min', 'co1_mixer_time', 'co1_const_pump', 'co1_ret_protect',
];
export function ogrzewanie() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    const c = sec('Ogrzewanie (CO)');
    c.append(stepperRow('Zadana CO (ręczna)', 'ch1_set_manual'), stepperRow('Zadana CO – komfort', 'co_set_comfort'), stepperRow('Zadana CO – eko', 'co_set_eco'),
      modeChips('Tryb CO', 'co_mode', { 0: 'Off', 1: 'Eko', 2: 'Harmonogram', 3: 'Komfort' }, m => callService('select_option', { entity_id: 'select.tekla_co_tryb_ustaw', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_co_tryb'));
    appendLevelGroups(c, byGroup['CO'] || [], shownLevel, { skipIds: new Set(['ch1_set_manual', 'co_set_comfort', 'co_set_eco']), order: ORDER_CO });
  });
}

// Kolejnosc dokladnie jak na prawdziwym panelu (sprawdzona zdjeciami ekranu Ciepla woda -> NASTAWY).
// "Zagrzej teraz" to zwykly wiersz-przelacznik (cwu_boost) jak na urzadzeniu, nie osobny przycisk z
// potwierdzeniem - oryginal nie ma takiego potwierdzenia.
const ORDER_CWU = ['cwu_boost', 'cwu_hyst', 'cwu_legion', 'cwu_prio', 'cwu_src', 'cwu_src_inc', 'cwu_delta', 'cwu_tmax'];
export function cieplaWoda() {
  return domainScreen((root, sec, byGroup, shownLevel) => {
    const w = sec('Ciepła woda (CWU)');
    w.append(stepperRow('Zadana CWU – komfort', 'hw_set_comfort'), stepperRow('Zadana CWU – eko', 'hw_set_eco'),
      modeChips('Tryb CWU', 'cwu_mode', { 0: 'Off', 1: 'Eko', 2: 'Harmonogram', 3: 'Komfort' }, m => callService('select_option', { entity_id: 'select.tekla_cwu_tryb_ustaw', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_cwu_tryb'));
    appendLevelGroups(w, byGroup['CWU'] || [], shownLevel, { skipIds: new Set(['hw_set_comfort', 'hw_set_eco']), order: ORDER_CWU });
  });
}

// ------------------------------------------------------------------ alarmy
export function alarmy() {
  const root = el('<div><div id="bn"></div><div class="sec"><h5>Stan</h5><div class="row"><span>Alarm</span><span class="v" data-b="al_state"></span></div><div class="row"><span>Ostatni</span><span class="v" data-b="al_last"></span></div></div><div class="sec"><h5>Historia alarmów</h5><div id="alist"></div></div><button class="btn sec" id="ack" data-b="al_ack">Potwierdź alarm</button></div>');
  binders.set('al_state', n => { n.innerHTML = alarmActive() ? '<span class="er">aktywny</span>' : '<span class="ok">brak</span>'; });
  // przycisk widoczny TYLKO przy aktywnym alarmie - jak w oryginale, nie ma sensu potwierdzac czegos czego nie ma.
  binders.set('al_ack', n => { n.classList.toggle('hideable', !alarmActive()); });
  binders.set('al_last', n => { n.textContent = lastAlarm(); });
  const fmtT = s => { const x = parseInt(s, 10); return x > 1e9 ? new Date(x * 1000).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : '–'; };
  const draw = () => {
    const rows = [];
    // Historia alarmow: skonsolidowana w 1 encje (sensor.tekla_historia_alarmow) - 20 wpisow jako
    // atrybuty ah_0..ah_19 zamiast dawnych 20 osobnych encji.
    const hist = S.states.get('sensor.tekla_historia_alarmow');
    const attrs = (hist && hist.attributes) || {};
    for (let i = 0; i < 20; i++) {
      const v = attrs['ah_' + i];
      if (!v || v === '-' || v === 'unknown') continue;
      const [txt, a, b] = String(v).split('|');
      rows.push(`<div class="row"><span>${esc(txt)}<div class="hint">${fmtT(a)} → ${parseInt(b, 10) > 1e9 ? fmtT(b) : 'trwa'}</div></span></div>`);
    }
    $('#alist', root).innerHTML = rows.join('') || '<div class="hint">Brak wpisów.</div>';
  };
  root.querySelector('#ack').onclick = async () => { if (await confirmSheet('Potwierdź alarm', 'Potwierdzić aktywny alarm w kotle?')) await callService('press', { entity_id: 'button.tekla_potwierdz_alarm' }, 'button'); };
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); draw(); updateBound(root); } };
}

// ------------------------------------------------------------------ parametry (z metadanych punktów)
// Przynaleznosc punktu do ekranu domenowego - NIE zgadywana po nazwie (nazwy czesto zwodza, np. "Palnik
// dawka wstepna g"/"Wymiennik interwal czyszczenia" naleza w oryginale do menu Palnik mimo brzmienia, a
// "Korekta powietrza"/"Moc min/max"/"Wartosc opalowa" tez do Palnik, nie Kociol). Zrodlo: katalog
// "Menu -> X -> NASTAWY" w web/pelletcan-card.js (zweryfikowane na prawdziwym kotle), ta sama przynaleznosc
// co w karcie classic i co w konsolidacji encji (patrz AttrGroup w firmware/engine.cpp).
const POINT_GROUP = {
  boiler_hyst_on: 'Kocioł', boiler_hyst_off: 'Kocioł', boiler_pump_min: 'Kocioł', boil_pump_run: 'Kocioł',
  boiler_ret_min: 'Kocioł', boiler_mixer_time: 'Kocioł', boil_fuel_reserve: 'Kocioł',
  air_corr: 'Palnik', power_min: 'Palnik', power_max: 'Palnik', fuel_heat: 'Palnik', fuel_test: 'Palnik',
  k_nominal: 'Palnik', k_predose_g: 'Palnik', k_egt_min: 'Palnik', k_egt_max: 'Palnik', k_exch_int: 'Palnik',
  exh_c1: 'Palnik', exh_c2: 'Palnik', exh_c3: 'Palnik', exh_c4: 'Palnik', exh_c5: 'Palnik',
  fan_mod_1: 'Palnik', fan_mod_2: 'Palnik', fan_mod_3: 'Palnik', fan_mod_4: 'Palnik', fan_mod_5: 'Palnik',
  p_prefeed: 'Palnik', p_feed_max: 'Palnik', p_photo: 'Palnik', p_blow_ign: 'Palnik', p_blow_glow: 'Palnik',
  p_blow_stop: 'Palnik', p_glow_time: 'Palnik', p_glow_fuel: 'Palnik', p_stop_time: 'Palnik', p_lambda: 'Palnik',
  p_o2_30: 'Palnik', p_o2_100: 'Palnik', p_cleans: 'Palnik', p_clean_gap: 'Palnik', p_pause_time: 'Palnik',
  p_pause_power: 'Palnik', p_pause_blow: 'Palnik',
  p_inertia: 'Palnik', p_grate_time: 'Palnik', p_burner_feed: 'Palnik', p_feeder_period: 'Palnik', p_min_rpm: 'Palnik',
  feeder_mode: 'Palnik', blower_mode: 'Palnik',
  co1_hyst: 'CO', co1_calib: 'CO', co1_mode: 'CO', co1_curve_m20: 'CO', co1_curve_0: 'CO', co1_curve_10: 'CO',
  co1_src_inc: 'CO', co1_tmax: 'CO', co1_corr: 'CO', co1_out_comf: 'CO', co1_out_eco: 'CO', co1_lower: 'CO',
  co1_pump_min: 'CO', co1_mixer_time: 'CO', co1_const_pump: 'CO', co1_ret_protect: 'CO', co1_source: 'CO',
  co1_co_sensor: 'CO', co1_room_sensor: 'CO',
  cwu_hyst: 'CWU', cwu_boost: 'CWU', cwu_prio: 'CWU', cwu_legion: 'CWU', cwu_src: 'CWU', cwu_src_inc: 'CWU',
  cwu_delta: 'CWU', cwu_tmax: 'CWU',
  alarm_snd: 'Alarmy', alarm_sil_from: 'Alarmy', alarm_sil_to: 'Alarmy',
  tank_kg: 'Paliwo',
};
export const GROUP_NAMES = ['Kocioł', 'Palnik', 'CO', 'CWU', 'Paliwo', 'Alarmy'];
export const groupOf = p => POINT_GROUP[p.id] || 'Inne';

export function paramGroups(go) {
  const cnt = {};
  for (const p of S.points) { const g = groupOf(p); cnt[g] = (cnt[g] || 0) + 1; }
  const names = [...GROUP_NAMES, 'Inne'].filter(g => cnt[g]);
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
const schedBits = k => {
  const attrs = (S.states.get(SCH[k][1]) || {}).attributes || {};
  return Array.from({ length: 7 }, (_, d) => { const x = attrs['d' + d]; return /^[0-9A-Fa-f]{6}$/.test(x || '') ? parseInt(x, 16) : null; });
};
const schedSig = k => {
  const attrs = (S.states.get(SCH[k][1]) || {}).attributes || {};
  return Array.from({ length: 7 }, (_, d) => attrs['d' + d]).join('|');
};
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
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); const s = SCH.map((_, i) => schedSig(i)).join('#'); if (s !== sig) { sig = s; draw(); } } };
}
