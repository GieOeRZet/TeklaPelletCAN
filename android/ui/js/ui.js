// Wspólne elementy interfejsu: okna dolne, klawiatura PIN, powiadomienia, formatowanie.
import { nat, onEvent, api } from './native.js';
import { S, pv, pn, level, refreshSoon, pullNow, pausePolling, resumePolling } from './store.js';

export const $ = (s, r = document) => r.querySelector(s);
export const el = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstElementChild; };
export const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
export const fmt = (x, d = 1) => Number.isFinite(x) ? x.toFixed(d).replace(/\.0+$/, d === 0 ? '' : '.0') : '–';
export const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–';

// Haszujemy PIN zamiast trzymac go jawnie w kodzie - nie jest to sekret kryptograficzny chroniacy
// cokolwiek wrazliwego, tylko "ukryte drzwi" do trybu developera (chodzi o to, zeby nie bylo widac
// samej liczby w grep/diff/czytaniu kodu). CELOWO bez Web Crypto (crypto.subtle) - ten dziala tylko
// w "bezpiecznym kontekscie" (HTTPS albo localhost/127.0.0.1), a strona urzadzenia w realnej sieci
// lokalnej jest zwyklym http://<adres-ip> - tam crypto.subtle jest undefined i kazde (nie tylko
// "1948") wywolanie check() w pinSheet konczylo sie wyjatkiem (zgloszony blad: "1948 nie dziala,
// pozostale tez cos nie graja"). Prosty, synchroniczny FNV-1a dziala wszedzie, bez zadnych wyjatkow.
function fnv1aHex(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
const DEV_PIN_FNV1A = '99511f4b';
export function isDevPin(p) { return fnv1aHex(p) === DEV_PIN_FNV1A; }

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

/** Okno z polem tekstowym (np. nazwa urządzenia). Zwraca Promise<string|null> (null = anulowano/puste). */
export function promptSheet({ title, sub, value = '', placeholder = '', okLabel = 'Zapisz' }) {
  return new Promise(resolve => {
    let done = false;
    const sh = openSheet(`<h3>${esc(title)}</h3>${sub ? `<div class="hint" style="font-size:14px;margin:6px 0 10px">${esc(sub)}</div>` : ''}
      <input class="t" id="pv" value="${esc(value)}" placeholder="${esc(placeholder)}" maxlength="40" style="margin-bottom:10px">
      <button class="btn acc" id="yes">${esc(okLabel)}</button><button class="btn sec" id="no">Anuluj</button>`, () => { if (!done) resolve(null); });
    const inp = $('#pv', sh);
    inp.focus(); inp.setSelectionRange(0, inp.value.length);
    const submit = () => { const v = inp.value.trim(); done = true; sheetClose = null; closeSheet(); resolve(v || null); };
    $('#yes', sh).onclick = submit;
    inp.onkeydown = e => { if (e.key === 'Enter') submit(); };
    $('#no', sh).onclick = () => closeSheet();
  });
}

/** Pierwsze ustawienie PIN-u aplikacji (wywolywane leniwie przy pierwszej probie odblokowania sterowania,
 * nie od razu po instalacji - uzytkownik moze wpierw przejrzec/dodac urzadzenie bez zadnego hasla). */
export async function ensurePinSetup() {
  const pin1 = await pinSheet({ title: 'Ustaw PIN aplikacji', sub: 'PIN chroni uruchomienie aplikacji (4–12 cyfr).' });
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
    title: 'Odblokuj aplikację', sub: 'Podaj PIN aplikacji.',
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

/** Poziom kotła (PIN 0900/0999) – niezalezny od PIN-u aplikacji (ten chroni juz tylko start apki).
 * Zwraca true, gdy poziom >= need. */
export async function ensureLevel(need) {
  if (level() >= need) return true;
  pausePolling();   // patrz store.js: wstrzymanie na czas PIN-u, zeby w tle lecace pull() nie wyscigowo
  // nadpisal swiezy poziom starsza wartoscia (numer seryjny w pull() chroni tylko przed odwrotna kolejnoscia)
  const pin = await pinSheet({
    title: 'Poziom dostępu kotła', sub: `Ta pozycja wymaga poziomu ${need}. Podaj PIN poziomu (jak w panelu kotła). Wygasa po 5 minutach bezczynności.`, digits: [4, 6],
    check: async p => {
      const r = await api('POST', '/api/v1/call', { domain: 'teklapelletcan', service: 'tekla_estyma_unlock', data: { pin: parseInt(p, 10) } });
      if (r.status !== 200) return 'Brak połączenia z kotłem';
      // UWAGA: r.json.level z odpowiedzi POST jest JUZ aktualny (silnik aktualizuje go synchronicznie),
      // ale osobny endpoint GET /api/v1/states (na ktorym opiera sie cala reszta interfejsu - pull(),
      // pullNow()) potrafi pokazac STARA wartosc jeszcze przez ok. 2 s po udanym odblokowaniu. Jesli
      // zaufamy tu r.json.level i przez to pominiemy petle ponizej (co bylo dawnym bledem - "cur" od razu
      // >= need, petla z warunkiem "cur < need" nigdy sie nie wykonywala), funkcja zwroci sukces, ZANIM
      // GET faktycznie zacznie widziec nowy poziom - kolejny pullNow() (i caly reszta UI) pokaze wtedy
      // przez chwile stary poziom. Dlatego cur startuje od 0 i ZAWSZE czekamy na GET-owe potwierdzenie,
      // niezaleznie od tego, co juz zglosil POST.
      let cur = 0;
      for (let i = 0; i < 10 && cur < need; i++) {
        await new Promise(res => setTimeout(res, 400));
        const s = await api('GET', '/api/v1/states');
        if (s.cachedAt) continue;   // odpowiedz podstawiona z pamieci podrecznej (urzadzenie chwilowo nieosiagalne)
        // - nie jest potwierdzeniem nowego poziomu, moze byc stara z poprzedniej sesji - probuj dalej
        const lv = (s.json.states || []).find(x => x.entity_id === 'sensor.tekla_poziom_dostepu');
        if (lv) cur = parseInt(lv.state, 10);
      }
      return cur >= need ? null : (cur > 0 ? `Ten PIN daje tylko poziom ${cur}` : 'Zły PIN poziomu');
    },
  });
  if (pin !== null) S.levelAt = Date.now();   // liczniik sesji poziomu w naglowku (patrz main.js chip())
  await pullNow();   // widoki od razu widzą nowy poziom
  resumePolling();
  return pin !== null;
}

/** Recznie wpisany PIN poziomu z Menu ("Poziom kotła") - w odroznieniu od ensureLevel() ZAWSZE pyta o PIN,
 * nawet gdy jakis poziom juz jest aktywny (np. ktos ma poziom 1, ale chce wejsc PIN-em 0999 na poziom 2 bez
 * czekania az wygasnie poprzednia sesja), i akceptuje KAZDY poprawny PIN poziomu (1 lub 2), nie tylko taki,
 * ktory daje poziom >= jakiegos wymaganego minimum. Zwraca true po poprawnym PIN-ie (dowolnego poziomu). */
export async function enterLevelPin() {
  let dev = false;
  pausePolling();   // jak w ensureLevel() - patrz store.js
  const pin = await pinSheet({
    title: 'Poziom dostępu kotła', sub: 'Podaj PIN poziomu (jak w panelu kotła). Wygasa po 5 minutach bezczynności.', digits: [4, 6],
    check: async p => {
      if (isDevPin(p)) { dev = true; return null; }   // "drzwi" do trybu developera - nic nie idzie do kotla
      const r = await api('POST', '/api/v1/call', { domain: 'teklapelletcan', service: 'tekla_estyma_unlock', data: { pin: parseInt(p, 10) } });
      if (r.status !== 200) return 'Brak połączenia z kotłem';
      // patrz ensureLevel() wyzej - nie ufamy r.json.level, zawsze czekamy na potwierdzenie przez GET.
      let cur = 0;
      for (let i = 0; i < 10 && cur < 1; i++) {
        await new Promise(res => setTimeout(res, 400));
        const s = await api('GET', '/api/v1/states');
        if (s.cachedAt) continue;   // patrz ensureLevel() wyzej - odpowiedz z cache nie potwierdza nic nowego
        const lv = (s.json.states || []).find(x => x.entity_id === 'sensor.tekla_poziom_dostepu');
        if (lv) cur = parseInt(lv.state, 10);
      }
      return cur > 0 ? null : 'Zły PIN poziomu';
    },
  });
  if (pin !== null && !dev) S.levelAt = Date.now();   // "1948" nie jest prawdziwym PIN-em poziomu
  await pullNow();
  resumePolling();
  if (dev) return 'dev';
  return pin !== null;
}

/** Zapis punktu przez API z obsługą typowych odmów. Zwraca true przy powodzeniu. */
export async function writePoint(id, value) {
  const p = S.pointById.get(id);
  if (p && p.level && level() < p.level && !(await ensureLevel(p.level))) return false;
  const r = await api('POST', '/api/v1/write', { id, value });
  return handleResult(r);
}

export async function callService(service, data, domain = 'teklapelletcan') {
  const r = await api('POST', '/api/v1/call', { domain, service, data });
  return handleResult(r);
}

function handleResult(r) {
  if (r.status === 200) { refreshSoon(); toast('Zapisano'); return true; }
  const e = r.json.error || r.json.result || '';
  const m = {
    level: 'Za niski poziom dostępu kotła', mirror: 'Urządzenie jest w trybie tylko do odczytu', disabled: 'Zapis wyłączony w urządzeniu',
    range: 'Wartość poza dozwolonym zakresem', rejected: 'Kocioł odrzucił zmianę', blocked: 'Operacja zablokowana', offline: 'Brak połączenia z modułem',
    unauthorized: 'Urządzenie wymaga hasła (sparuj w konfiguracji)', setup_required: 'Urządzenie wymaga pierwszej konfiguracji',
  }[e] || ('Błąd (' + (e || r.status) + ')');
  toast(m);
  return false;
}

/** Okno edycji wartości punktu: krokowe +/− albo wybór opcji; zatwierdzenie z potwierdzeniem na wyższych poziomach. */
export async function editPoint(pid) {
  const p = S.pointById.get(pid);
  if (!p || !p.writable) return;
  if (p.level && level() < p.level && !(await ensureLevel(p.level))) return;
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
  const lo = p.min ?? 0, hi = p.max ?? (lo + 100);
  // Suwak do zgrubnego ustawienia (przeciagnij/stuknij pasek) + plusy/minusy do precyzyjnej korekty o
  // jeden krok, gdy palcem nie da sie trafic dokladnie - jak w karcie classic (suwak + +/-).
  const sh = openSheet(`<h3>${esc(p.name)}</h3><div class="hint">Zakres ${p.min ?? ''}…${p.max ?? ''} ${esc(p.unit || '')}${p.level ? ` · poziom ${p.level}` : ''}</div>
    <div class="slider" id="sl"><div class="fill" id="fill"></div><div class="thumb" id="thumb"></div></div>
    <div class="stepper"><button id="m">−</button><b id="val"></b><button id="p">+</button></div><button class="btn acc" id="ok">Zastosuj</button><button class="btn sec" id="no">Anuluj</button>`);
  const draw = () => {
    $('#val', sh).textContent = val.toFixed(dec) + (p.unit ? ' ' + p.unit : '');
    const f = hi > lo ? Math.max(0, Math.min(1, (val - lo) / (hi - lo))) : 0;
    $('#fill', sh).style.width = (f * 100) + '%'; $('#thumb', sh).style.left = (f * 100) + '%';
  };
  draw();
  const bump = d => { val = Math.min(p.max ?? Infinity, Math.max(p.min ?? -Infinity, Math.round((val + d) / step) * step)); val = Number(val.toFixed(dec)); draw(); };
  const setFromFrac = f => { val = lo + Math.max(0, Math.min(1, f)) * (hi - lo); val = Math.min(hi, Math.max(lo, Math.round(val / step) * step)); val = Number(val.toFixed(dec)); draw(); };
  const track = $('#sl', sh);
  let dragging = false;
  const fracOf = e => { const r = track.getBoundingClientRect(); return (e.clientX - r.left) / r.width; };
  track.addEventListener('pointerdown', e => { dragging = true; track.setPointerCapture(e.pointerId); setFromFrac(fracOf(e)); });
  track.addEventListener('pointermove', e => { if (dragging) setFromFrac(fracOf(e)); });
  track.addEventListener('pointerup', () => { dragging = false; });
  track.addEventListener('pointercancel', () => { dragging = false; });
  $('#m', sh).onclick = () => bump(-step); $('#p', sh).onclick = () => bump(step);
  $('#no', sh).onclick = closeSheet;
  $('#ok', sh).onclick = async () => {
    if (p.level >= 1 && !(await confirmSheet(p.name, `Zmienić z <b>${fmt(cur, dec)}</b> na <b>${fmt(val, dec)}</b> ${esc(p.unit || '')}?`))) return;
    closeSheet(); await writePoint(pid, val);
  };
}
