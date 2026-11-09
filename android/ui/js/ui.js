// Wspólne elementy interfejsu: okna dolne, klawiatura PIN, powiadomienia, formatowanie.
import { nat, onEvent, api } from './native.js';
import { S, pv, pn, level, refreshSoon, pullNow } from './store.js';

export const $ = (s, r = document) => r.querySelector(s);
export const el = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstElementChild; };
export const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
export const fmt = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d).replace(/\.0+$/, d === 0 ? '' : '.0') : '–';
export const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–';

let toastT = null;
export function toast(t) {
  const e = $('#toast'); e.textContent = t; e.style.display = 'block';
  clearTimeout(toastT); toastT = setTimeout(() => { e.style.display = 'none'; }, 3200);
}

let sheetClose = null;
export function closeSheet() { $('#overlay').innerHTML = ''; if (sheetClose) { const f = sheetClose; sheetClose = null; f(); } }
export function openSheet(html, onClose) {
  closeSheet();
  const o = $('#overlay');
  o.innerHTML = '<div class="scrim"></div><div class="sheet"><div class="grab"></div>' + html + '</div>';
  $('.scrim', o).onclick = closeSheet;
  sheetClose = onClose || null;
  return $('.sheet', o);
}

/** Klawiatura PIN w oknie dolnym. Zwraca Promise<string|null> (null = anulowano). check(pin) -> Promise<string|null komunikat błędu>. */
export function pinSheet({ title, sub, digits = [4, 12], check, extra = '' }) {
  return new Promise(resolve => {
    let pin = '', busy = false;
    const sh = openSheet(`<h3>${esc(title)}</h3><div class="hint">${esc(sub || '')}</div><div class="pin" id="dots"></div><div class="msg" id="pmsg"></div>
      <div class="pad">${[1,2,3,4,5,6,7,8,9].map(n => `<button data-k="${n}">${n}</button>`).join('')}<button class="s" data-k="x">⌫</button><button data-k="0">0</button><button class="s" data-k="ok">OK</button></div>${extra}`, () => resolve(null));
    const dots = () => { $('#dots', sh).innerHTML = Array.from({ length: Math.max(digits[0], pin.length) }, (_, i) => `<i class="${i < pin.length ? 'f' : ''}"></i>`).join(''); };
    dots();
    sh.querySelectorAll('.pad button').forEach(b => b.onclick = async () => {
      if (busy) return;
      const k = b.dataset.k;
      if (k === 'x') pin = pin.slice(0, -1);
      else if (k === 'ok' || (k !== 'x' && pin.length + 1 >= digits[1])) {
        if (k !== 'ok') pin += k;
        if (pin.length < digits[0]) { $('#pmsg', sh).textContent = `PIN: min. ${digits[0]} cyfry`; dots(); return; }
        busy = true;
        const err = check ? await check(pin) : null;
        busy = false;
        if (err) { $('#pmsg', sh).textContent = err; pin = ''; dots(); return; }
        const p = pin; sheetClose = null; closeSheet(); resolve(p); return;
      } else pin += k;
      $('#pmsg', sh).textContent = ''; dots();
    });
    sh.__setMsg = t => { $('#pmsg', sh).textContent = t; };
  });
}

export function confirmSheet(title, text, okLabel = 'Zastosuj') {
  return new Promise(resolve => {
    let done = false;
    const sh = openSheet(`<h3>${esc(title)}</h3><div class="hint" style="font-size:14px;margin:6px 0 10px">${text}</div><button class="btn acc" id="yes">${esc(okLabel)}</button><button class="btn sec" id="no">Anuluj</button>`, () => { if (!done) resolve(false); });
    $('#yes', sh).onclick = () => { done = true; sheetClose = null; closeSheet(); resolve(true); };
    $('#no', sh).onclick = () => closeSheet();
  });
}

/** Pierwsze ustawienie PIN-u aplikacji (wywolywane leniwie przy pierwszej probie odblokowania sterowania,
 * nie od razu po instalacji - uzytkownik moze wpierw przejrzec/dodac urzadzenie bez zadnego hasla). */
export async function ensurePinSetup() {
  const pin1 = await pinSheet({ title: 'Ustaw PIN aplikacji', sub: 'PIN chroni sterowanie kotłem (4–12 cyfr). Bez niego aplikacja działa tylko jako podgląd.' });
  if (!pin1) return false;
  const pin2 = await pinSheet({ title: 'Powtórz PIN', sub: 'Wpisz ten sam PIN jeszcze raz', check: async p => (p === pin1 ? null : 'PIN-y się różnią') });
  if (!pin2) return false;
  const r = nat.setupPin(pin1);
  if (!r.ok) { toast(r.error); return false; }
  nat.setBio(false);
  return true;
}

/** Odblokowanie zapisu PIN-em aplikacji lub odciskiem. Zwraca true po sukcesie. */
export async function ensureUnlocked() {
  if (nat.state().unlocked) return true;
  if (!nat.state().hasPin && !(await ensurePinSetup())) return false;
  const st = nat.state();
  const useBio = st.bio && st.bioAvailable;
  let bioOk = null;
  const off = onEvent(e => { if (e.type === 'bio' && e.ok) { bioOk = true; closeSheet(); } });
  if (useBio) nat.unlockBio();
  const extra = useBio ? '<button class="btn sec" id="bio">☝ Użyj odcisku palca</button>' : '';
  const p = pinSheet({
    title: 'Odblokuj sterowanie', sub: 'Podaj PIN aplikacji. Zapis do kotła włączy się na 5 minut bezczynności.',
    extra,
    check: async pin => {
      const r = nat.unlockPin(pin);
      if (r.ok) return null;
      if (r.lockedUntil) return `Za dużo prób. Spróbuj za ${Math.ceil(r.waitMs / 1000)} s`;
      return `Zły PIN (pozostało prób: ${r.attemptsLeft})`;
    },
  });
  setTimeout(() => { const b = $('#bio'); if (b) b.onclick = () => nat.unlockBio(); }, 0);
  const pin = await p;
  off();
  return bioOk === true || nat.state().unlocked;
}

/** Poziom kotła (PIN 0900/0999) – wymaga odblokowanej aplikacji. Zwraca true, gdy poziom >= need. */
export async function ensureLevel(need) {
  if (level() >= need) return true;
  if (!(await ensureUnlocked())) return false;
  const pin = await pinSheet({
    title: 'Poziom dostępu kotła', sub: `Ta pozycja wymaga poziomu ${need}. Podaj PIN poziomu (jak w panelu kotła). Wygasa po 5 minutach bezczynności.`, digits: [4, 6],
    check: async p => {
      const r = await api('POST', '/api/v1/call', { domain: 'teklapelletcan', service: 'tekla_estyma_unlock', data: { pin: parseInt(p, 10) } });
      if (r.status === 403 && r.json.error === 'app_locked') return 'Aplikacja zablokowana';
      if (r.status !== 200) return 'Błąd połączenia z urządzeniem';
      // odczyt poziomu potwierdzany asynchronicznie przez urzadzenie - pojedyncze 700ms nie zawsze wystarcza
      // (wolniejsza siec/urzadzenie), wiec odpytujemy do skutku zamiast raz, do ok. 4 s.
      let cur = r.json.level || 0;
      for (let i = 0; i < 10 && cur < need; i++) {
        await new Promise(res => setTimeout(res, 400));
        const s = await api('GET', '/api/v1/states');
        const lv = (s.json.states || []).find(x => x.entity_id === 'sensor.tekla_poziom_dostepu');
        if (lv) cur = parseInt(lv.state, 10);
      }
      return cur >= need ? null : (cur > 0 ? `Ten PIN daje tylko poziom ${cur}` : 'Zły PIN poziomu');
    },
  });
  await pullNow();   // widoki od razu widzą nowy poziom
  return pin !== null;
}

/** Zapis punktu przez API z obsługą typowych odmów. Zwraca true przy powodzeniu. */
export async function writePoint(id, value) {
  const p = S.pointById.get(id);
  if (p && p.level && level() < p.level && !(await ensureLevel(p.level))) return false;
  let r = await api('POST', '/api/v1/write', { id, value });
  if (r.status === 403 && r.json.error === 'app_locked') {
    if (!(await ensureUnlocked())) return false;
    r = await api('POST', '/api/v1/write', { id, value });
  }
  return handleResult(r);
}

export async function callService(service, data, domain = 'teklapelletcan') {
  let r = await api('POST', '/api/v1/call', { domain, service, data });
  if (r.status === 403 && r.json.error === 'app_locked') {
    if (!(await ensureUnlocked())) return false;
    r = await api('POST', '/api/v1/call', { domain, service, data });
  }
  return handleResult(r);
}

function handleResult(r) {
  if (r.status === 200) { refreshSoon(); toast('Zapisano'); return true; }
  const e = r.json.error || r.json.result || '';
  const m = {
    level: 'Za niski poziom dostępu kotła', mirror: 'Urządzenie jest w trybie tylko do odczytu', disabled: 'Zapis wyłączony w urządzeniu',
    range: 'Wartość poza dozwolonym zakresem', rejected: 'Kocioł odrzucił zmianę', blocked: 'Operacja zablokowana', offline: 'Brak połączenia z urządzeniem',
    app_locked: 'Sterowanie zablokowane', unauthorized: 'Urządzenie wymaga hasła (sparuj w konfiguracji)', setup_required: 'Urządzenie wymaga pierwszej konfiguracji',
  }[e] || ('Błąd (' + (e || r.status) + ')');
  toast(m);
  return false;
}

/** Okno edycji wartości punktu: krokowe +/− albo wybór opcji; zatwierdzenie z potwierdzeniem na wyższych poziomach. */
export async function editPoint(pid) {
  const p = S.pointById.get(pid);
  if (!p || !p.writable) return;
  if (p.level && level() < p.level && !(await ensureLevel(p.level))) return;
  if (!nat.state().unlocked && !(await ensureUnlocked())) return;
  const cur = pn(pid);
  if (p.options) {
    const opts = Object.entries(p.options);
    const sh = openSheet(`<h3>${esc(p.name)}</h3><div class="chips">${opts.map(([k, l]) => `<button data-k="${k}" class="${String(Math.round(cur)) === k ? 'on' : ''}">${esc(l)}</button>`).join('')}</div>`);
    sh.querySelectorAll('.chips button').forEach(b => b.onclick = async () => {
      const val = parseInt(b.dataset.k, 10);
      closeSheet();
      if (pid === 'boiler_mode') await callService('tekla_estyma_set_boiler_mode', { mode: val }); else await writePoint(pid, val);
    });
    return;
  }
  const isBool = p.min === 0 && p.max === 1 && (p.step || 1) === 1;
  if (isBool) {
    if (p.level >= 1 && !(await confirmSheet(p.name, `Zmienić na <b>${cur ? 'wyłączone (0)' : 'włączone (1)'}</b>?`))) return;
    await writePoint(pid, cur ? 0 : 1); return;
  }
  const step = p.step || 1, dec = String(step).includes('.') ? String(step).split('.')[1].length : 0;
  let val = Number.isFinite(cur) ? cur : (p.min ?? 0);
  const sh = openSheet(`<h3>${esc(p.name)}</h3><div class="hint">Zakres ${p.min ?? ''}…${p.max ?? ''} ${esc(p.unit || '')}${p.level ? ` · poziom ${p.level}` : ''}</div>
    <div class="stepper"><button id="m">−</button><b id="val"></b><button id="p">+</button></div><button class="btn acc" id="ok">Zastosuj</button><button class="btn sec" id="no">Anuluj</button>`);
  const draw = () => { $('#val', sh).textContent = val.toFixed(dec) + (p.unit ? ' ' + p.unit : ''); };
  draw();
  const bump = d => { val = Math.min(p.max ?? Infinity, Math.max(p.min ?? -Infinity, Math.round((val + d) / step) * step)); val = Number(val.toFixed(dec)); draw(); };
  $('#m', sh).onclick = () => bump(-step); $('#p', sh).onclick = () => bump(step);
  $('#no', sh).onclick = closeSheet;
  $('#ok', sh).onclick = async () => {
    if (p.level >= 1 && !(await confirmSheet(p.name, `Zmienić z <b>${fmt(cur, dec)}</b> na <b>${fmt(val, dec)}</b> ${esc(p.unit || '')}?`))) return;
    closeSheet(); await writePoint(pid, val);
  };
}
