// Widoki: pulpit, instalacja, kocioł, alarmy, parametry, menu.
import { nat, api } from './native.js';
import { S, v, num, pv, pn, level, subscribe } from './store.js';
import { $, el, esc, f1, fmt, toast, openSheet, closeSheet, ensureLevel, ensureUnlocked, editPoint, callService, writePoint, confirmSheet } from './ui.js';

const MODE = { 0: 'Czasowy auto', 1: 'Czasowy ręczny', 2: 'Auto', 3: 'Ręczny' };
const HOPPER = (pct = 60, h = 54) => `<svg height="${h}" viewBox="0 0 70 78"><path d="M4 6h62l-14 62H18z" fill="#12151b" stroke="#4a4f5c" stroke-width="2"/><path d="M${12 + (100 - pct) * 0.04} ${68 - 38 * pct / 100}h${46 - (100 - pct) * 0.08}l-8 ${38 * pct / 100}H20z" fill="#c98a4a"/></svg>`;

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
    <div class="hero"><div class="stage"><img id="kimg" alt="kocioł"></div>
      <div class="tx"><div class="big"><span data-b="t_boiler"></span><small> °C</small></div><div data-b="pill"></div></div>
      <div class="st"><div data-b="hero_sub"></div></div></div>
    <div class="g2">
      <button class="cd im" data-go="kociol"><small>Palnik</small><b data-b="burner_pct"></b><span class="u"> %</span><div class="dots"><span><i data-b="dot_blower"></i>dmuchawa</span><span><i data-b="dot_feeder"></i>podajnik</span></div><img src="img/palnik.webp" style="height:50px" alt=""></button>
      <button class="cd im" data-go="kociol"><small>CWU</small><b data-b="t_cwu"></b><span class="u"> °C</span><div class="u" data-b="cwu_sub"></div><img src="img/bojler.webp" style="height:76px;right:10px;top:8px;border-radius:8px" alt=""></button>
      <button class="cd" data-go="kociol"><small>CO</small><b data-b="t_co"></b><span class="u"> °C</span><div class="u" data-b="co_sub"></div></button>
      <button class="cd" data-go="instalacja"><small>Paliwo</small><b data-b="fuel"></b><span class="u"> kg</span><div class="u" data-b="fuel_sub"></div><div style="position:absolute;right:10px;bottom:8px" data-b="hopper"></div></button>
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
  set('hopper', n => { n.innerHTML = HOPPER(Number.isFinite(pct()) ? pct() : 50, 62); });
  set('t_out', n => { n.textContent = f1(num('sensor.tekla_temperatura_zewnetrzna')); });
  set('out_sub', n => { n.textContent = 'powrót ' + f1(num('sensor.tekla_temperatura_powrotu')) + ' °C'; });
  set('kw', n => { n.textContent = f1(num('sensor.tekla_palnik_moc')); });
  set('kw_sub', n => { n.textContent = 'palnik ' + fmt(num('sensor.tekla_temperatura_palnika'), 0) + ' °C'; });
  set('alarm_ico', n => { n.innerHTML = alarmActive() ? '<span class="er">⚠</span>' : '<span class="ok">✓</span>'; });
  set('alarm_t', n => { n.textContent = alarmActive() ? 'Alarm aktywny' : 'Brak alarmów'; n.className = alarmActive() ? 'er' : ''; });
  set('alarm_sub', n => { n.textContent = 'ostatni: ' + lastAlarm(); });
  root.querySelector('#kimg').src = boilerImg();
  root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); root.classList.toggle('offline', !!S.cachedAt); updateBound(root); } };
}

// ------------------------------------------------------------------ instalacja
export function instalacja(go) {
  const root = el(`<div class="flow"><div id="bn"></div>
    <button class="node" data-go="params/Paliwo"><span data-b="in_hop"></span><div><b>Zbiornik</b><span class="u" data-b="in_hop_t"></span></div><div class="r"><span class="pill" data-b="in_hop_p"></span></div></button>
    <div class="arrow">▼ ▼ ▼</div>
    <button class="node" data-go="params/Palnik"><img src="img/palnik.webp" alt=""><div><b>Palnik</b><span class="u" data-b="in_burn_t"></span></div><div class="r"><b data-b="in_burn_p"></b></div></button>
    <div class="arrow">▼ ▼ ▼</div>
    <button class="node" data-go="kociol"><img src="${boilerImg()}" style="height:60px" alt=""><div><b>Kocioł</b><span class="u" data-b="in_k_t"></span></div><div class="r"><b data-b="in_k_p"></b></div></button>
    <div class="arrow" style="letter-spacing:70px">▼ ▼</div>
    <div class="split">
      <button class="node" data-go="kociol"><b>CO</b><span class="u" data-b="in_co_t"></span><b style="font-size:22px" data-b="in_co_p"></b><span class="u" data-b="in_co_v"></span></button>
      <button class="node" data-go="kociol"><b>CWU</b><span class="u" data-b="in_cwu_t"></span><b style="font-size:22px" data-b="in_cwu_p"></b></button>
    </div>
    <div class="sec" style="margin-top:12px"><h5>Dodatkowe</h5>
      <div class="row"><span>Temperatura powrotu</span><span class="v" data-b="in_ret"></span></div>
      <div class="row"><span>Temperatura palnika</span><span class="v" data-b="in_bt"></span></div>
      <div class="row"><span>Temperatura zewnętrzna</span><span class="v" data-b="in_out"></span></div>
      <div class="row"><span>Moc palnika</span><span class="v" data-b="in_kw"></span></div></div></div>`);
  const set = (k, fn) => { const n = root.querySelector(`[data-b="${k}"]`); if (n) { n.dataset.b = 'inst_' + k; binders.set('inst_' + k, fn); } };
  const pct = () => { const x = num('sensor.tekla_zbiornik_zapelnienie'); return Number.isFinite(x) ? x : 50; };
  set('in_hop', n => { n.innerHTML = HOPPER(pct(), 54); });
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

export function kociol() {
  const root = el('<div><div id="bn"></div></div>');
  const sec = (h) => { const s = el(`<div class="sec"><h5>${h}</h5></div>`); root.appendChild(s); return s; };
  const k = sec('Kocioł');
  k.append(stepperRow('Zadana temperatura kotła (ręczna)', 'boiler_set_manual'),
    modeChips('Tryb pracy kotła', 'boiler_mode', MODE, m => callService('tekla_estyma_set_boiler_mode', { mode: m }), 'sensor.tekla_kociol_tryb_pracy'));
  const c = sec('CO (ogrzewanie)');
  c.append(stepperRow('Zadana CO (ręczna)', 'ch1_set_manual'), stepperRow('Zadana CO – komfort', 'co_set_comfort'), stepperRow('Zadana CO – eko', 'co_set_eco'),
    modeChips('Tryb CO', 'co_mode', { 0: 'Off', 1: 'Eko', 2: 'Harmonogram', 3: 'Komfort' }, m => callService('select_option', { entity_id: 'select.tekla_co_mode_sel', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_co_tryb'));
  const w = sec('CWU (ciepła woda)');
  w.append(stepperRow('Zadana CWU – komfort', 'hw_set_comfort'), stepperRow('Zadana CWU – eko', 'hw_set_eco'),
    modeChips('Tryb CWU', 'cwu_mode', { 0: 'Off', 1: 'Eko', 2: 'Harmonogram', 3: 'Komfort' }, m => callService('select_option', { entity_id: 'select.tekla_cwu_mode_sel', option: ['Off', 'Eko', 'Harmonogram', 'Komfort'][m] }, 'select'), 'sensor.tekla_cwu_tryb'));
  w.append(el('<button class="btn sec" id="boost">Zagrzej CWU teraz</button>'));
  root.querySelector('#boost').onclick = async () => { if (await confirmSheet('Zagrzej CWU teraz', 'Włączyć jednorazowe dogrzanie wody?')) await writePoint('cwu_boost', 1); };
  root.querySelectorAll('[data-edit]').forEach(b => b.onclick = () => editPoint(b.dataset.edit));
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); updateBound(root); } };
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
export const GROUPS = [['Kocioł', /^(Kociol|Moc|Histereza zal|Wartosc|Korekta)/i], ['Palnik', /^(Palnik|Dmuchawa|Ilosc paliwa)/i], ['CO', /^CO/i], ['CWU', /^CWU/i], ['Paliwo', /^(Zbiornik|Paliwo)/i], ['Alarmy', /^Alarm/i]];
export const groupOf = p => { for (const [g, re] of GROUPS) if (re.test(p.name)) return g; return 'Inne'; };

export function paramGroups(go) {
  const cnt = {};
  for (const p of S.points) { const g = groupOf(p); cnt[g] = (cnt[g] || 0) + 1; }
  const names = [...GROUPS.map(g => g[0]), 'Inne'].filter(g => cnt[g]);
  const root = el(`<div><div id="bn"></div><div class="sec"><h5>Parametry i odczyty</h5>${names.map(g => `<button class="row nav2" data-go="params/${g}"><span>${g}</span><span class="v">${cnt[g]}</span></button>`).join('')}</div>
    <div class="hint" style="padding:0 6px">Wszystkie punkty urządzenia – tak jak w oryginalnej karcie. Pozycje z 🔒 wymagają poziomu 1 lub 2 (PIN kotła).</div></div>`);
  root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); } };
}

export function paramList(group) {
  const pts = S.points.filter(p => groupOf(p) === group);
  const root = el(`<div><div id="bn"></div><div class="sec"><h5>${esc(group)}</h5><div id="plist"></div></div></div>`);
  const L = $('#plist', root);
  for (const p of pts) {
    const b = el(`<button class="row ${p.writable ? 'nav2' : ''}" data-p="${esc(p.id)}"><span>${esc(p.name)}<span data-b="pk_${esc(p.id)}"></span>${p.writable ? '' : '<div class="hint">tylko odczyt</div>'}</span><span class="v" data-b="pv_${esc(p.id)}"></span></button>`);
    binders.set('pv_' + p.id, n => {
      const s = pv(p.id);
      let t = s === undefined || s === 'unknown' ? '–' : s;
      if (p.options && p.options[String(Math.round(parseFloat(s)))] !== undefined && !Number.isNaN(parseFloat(s))) t = p.options[String(Math.round(parseFloat(s)))];
      n.textContent = t + (p.unit && t !== '–' && !p.options ? ' ' + p.unit : '');
    });
    binders.set('pk_' + p.id, n => { n.innerHTML = p.writable && p.level && level() < p.level ? `<span class="lk">🔒 P${p.level}</span>` : ''; });
    if (p.writable) b.onclick = () => editPoint(p.id);
    L.appendChild(b);
  }
  return { node: root, update() { $('#bn', root).innerHTML = offlineBanner(); updateBound(root); root.querySelectorAll('.lk').forEach(() => {}); } };
}
