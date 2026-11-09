// Test karty teklapelletcan-card (tylko nasza integracja, auto-wykrywanie urzadzenia po rejestrze HA, bez zgadywania).
// Wymaga demo_server (silnik firmware + API) serwujacego katalog web/ (web/test/hacard.html buduje fikcyjny obiekt hass).
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8098';
const OUT = process.argv[3] || '/tmp';
const fail = [];
const check = (n, c, x = '') => { console.log((c ? 'OK   ' : 'FAIL ') + n + (c ? '' : ' ' + x)); if (!c) fail.push(n); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function cardText(page) {
  return page.evaluate(() => {
    const out = [];
    const walk = n => { if (n.nodeType === 3) out.push(n.textContent.trim()); if (n.shadowRoot) walk(n.shadowRoot); n.childNodes && n.childNodes.forEach(walk); };
    walk(document.getElementById('root'));
    return out.filter(Boolean).join(' | ');
  });
}

(async () => {
  const b = await chromium.launch();

  // ---- 1 urzadzenie: karta renderuje sie sama, bez zadnej konfiguracji ----
  {
    const ctx = await b.newContext({ viewport: { width: 480, height: 900 }, deviceScaleFactor: 2 });
    const p = await ctx.newPage();
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto(BASE + '/test/hacard.html?mode=one');
    await p.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
    await sleep(2500);
    const txt = await cardText(p);
    check('1 urządzenie: karta renderuje temperaturę kotła (bez entity_prefix w configu)', /\d\d\.\d/.test(txt), txt.slice(0, 120));
    check('1 urządzenie: brak błędu "nie znaleziono integracji"', !/Nie znaleziono/.test(txt));
    check('1 urządzenie: edytor nie pokazuje pola wyboru urządzenia (tylko jedno)', (await p.locator('#ed ha-form').evaluate(f => JSON.stringify(f.schema))).indexOf('device_id') < 0);
    check('brak błędów JS', errs.length === 0, errs.join('|'));
    await p.screenshot({ path: OUT + '/ha_teklapelletcan_card_one.png' });
    await ctx.close();
  }

  // ---- 2 urzadzenia: domyslnie pierwsze + baner, edytor pozwala wybrac konkretne ----
  {
    const ctx = await b.newContext({ viewport: { width: 480, height: 940 }, deviceScaleFactor: 2 });
    const p = await ctx.newPage();
    await p.goto(BASE + '/test/hacard.html?mode=two');
    await p.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
    await sleep(2500);
    const txt = await cardText(p);
    check('2 urządzenia: karta i tak się renderuje (domyślnie pierwsze)', /\d\d\.\d/.test(txt), txt.slice(0, 120));
    check('2 urządzenia: baner informujący o kilku urządzeniach', /Wykryto kilka urządzeń/.test(txt));
    check('2 urządzenia: edytor ma pole wyboru urządzenia z dwiema opcjami', await p.evaluate(() => {
      const f = document.querySelector('#ed ha-form'); const sch = f.schema.find(s => s.name === 'device_id');
      return !!sch && sch.selector.select.options.length === 3;   // auto + 2 urzadzenia
    }));
    // wybór konkretnego urządzenia w edytorze usuwa baner i karta zostaje przy nim
    await p.evaluate(() => {
      const f = document.querySelector('#ed ha-form');
      f.dispatchEvent(new CustomEvent('value-changed', { detail: { value: Object.assign({}, f.data, { device_id: 'dev2' }) } }));
    });
    await sleep(2500);
    const cfgOk = await p.evaluate(() => window.__cfgEvents.some(c => c.device_id === 'dev2'));
    check('2 urządzenia: config-changed z wybranym device_id', cfgOk);
    const txt2 = await cardText(p);
    check('2 urządzenia: po wyborze konkretnego urządzenia baner znika', !/Wykryto kilka urządzeń/.test(txt2), txt2.slice(0, 120));
    await p.screenshot({ path: OUT + '/ha_teklapelletcan_card_two.png', fullPage: true });
    await ctx.close();
  }

  // ---- regresja: klikniecie w ekran karty nie cofa sie po kolejnym odswiezeniu stanow z HA ----
  {
    const ctx = await b.newContext({ viewport: { width: 480, height: 900 }, deviceScaleFactor: 2 });
    const p = await ctx.newPage();
    await p.goto(BASE + '/test/hacard.html?mode=one');
    await p.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
    await sleep(2000);
    check('nawigacja: start na ekranie głównym', (await p.evaluate(() => window.__cardScreen())) === 'main');
    // wejscie w podmenu "Historia alarmów" (nie wymaga PIN-u, jak w oryginalnej karcie)
    await p.evaluate(() => { document.querySelector('#root teklapelletcan-card')._go('alarm'); });
    const scrAfterClick = await p.evaluate(() => window.__cardScreen());
    check('nawigacja: klik zmienia ekran', scrAfterClick === 'alarm', scrAfterClick);
    // symulacja kilku kolejnych odswiezen z HA (jak coordinator co 2 s) – ekran MUSI zostac
    for (let i = 0; i < 4; i++) { await p.evaluate(() => window.__pushHassTick()); await sleep(600); }
    const scrAfterTicks = await p.evaluate(() => window.__cardScreen());
    check('nawigacja: ekran NIE wraca do głównego po odświeżeniach stanów', scrAfterTicks === 'alarm', 'było: ' + scrAfterTicks);
    await ctx.close();
  }

  // ---- 0 urzadzen: czytelny komunikat, karta nie wybucha ----
  {
    const ctx = await b.newContext({ viewport: { width: 480, height: 300 } });
    const p = await ctx.newPage();
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto(BASE + '/test/hacard.html?mode=none');
    await p.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
    await sleep(800);
    const txt = await cardText(p);
    check('0 urządzeń: czytelny komunikat zamiast pustej/zepsutej karty', /Nie znaleziono/.test(txt) && /Urządzenia i usługi/.test(txt), txt);
    check('0 urządzeń: brak błędów JS (karta nie wybucha)', errs.length === 0, errs.join('|'));
    await p.screenshot({ path: OUT + '/ha_teklapelletcan_card_none.png' });
    await ctx.close();
  }

  // ---- grafiki pełne domyślnie, boiler_image z konfiguracji ----
  {
    const ctx = await b.newContext({ viewport: { width: 480, height: 900 }, deviceScaleFactor: 2 });
    const p = await ctx.newPage();
    await p.goto(BASE + '/test/hacard.html?mode=one&cfg=' + encodeURIComponent(JSON.stringify({ boiler_image: '11' })));
    await p.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
    await sleep(2500);
    const grafiki = await p.evaluate(() => document.querySelector('#root teklapelletcan-card')._cfg.grafiki);
    const img = await p.evaluate(() => document.querySelector('#root teklapelletcan-card')._cfg.boiler_image);
    check('grafiki pełne domyślnie (bez ustawiania w configu)', grafiki === 'pelne', grafiki);
    check('boiler_image przekazany do karty wewnętrznej', img === '11', img);
    await ctx.close();
  }

  await modernTests(b);

  await b.close();
  console.log(fail.length ? '\nNIEPOWODZENIA: ' + fail.join('; ') : '\nWSZYSTKO OK');
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });

// ==================================================================================================
// teklapelletcan-modern-card: pulpit/instalacja/nastawy/harmonogram/alarmy, adresowanie po tpc_id,
// zapisy przez prawdziwe uslugi HA (forwardowane w tescie do demo_server – ten sam silnik co firmware).
// ==================================================================================================
async function modernTests(b) {
  const ctx = await b.newContext({ viewport: { width: 440, height: 1400 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  p.setDefaultTimeout(8000);
  await p.goto(BASE + '/test/hacard.html?mode=one');
  await p.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
  await p.waitForFunction(() => typeof window.__modernReady === 'function', null, { timeout: 15000 });
  await p.evaluate(() => window.__modernReady());
  await p.waitForFunction(() => !!window.__mcard, null, { timeout: 10000 });
  await sleep(1500);

  const mtxt = sel => p.evaluate(sel => document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelector(sel).textContent, sel);
  const mhas = sel => p.evaluate(sel => !!document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelector(sel), sel);
  const mclick = sel => p.evaluate(sel => document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelector(sel).click(), sel);
  const mtext = () => p.evaluate(() => document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.getElementById('body').textContent);

  check('modern: pulpit renderuje temperaturę kotła (po tpc_id, bez zgadywania)', /\d\d\.\d/.test(await mtxt('.hero .big')));
  check('modern: grafika kotła załadowana', await p.evaluate(() => { const i = document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelector('.hero img'); return i.complete && i.naturalWidth > 20; }));
  check('modern: kafelek paliwa', /\d+/.test(await mtxt('[data-fuel] b')));
  await p.screenshot({ path: OUT + '/ha_modern_pulpit.png' });

  // nawigacja + regresja (ten sam blad co w teklapelletcan-card: setConfig nie wolno wywolywac na kazdym hass ticku)
  await mclick('[data-s="instalacja"]');
  check('modern: nawigacja do Instalacja', (await mtext()).includes('Zbiornik'));
  await p.evaluate(() => window.__pushHassTick());
  await p.evaluate(() => { document.querySelector('#rootm teklapelletcan-modern-card').hass = window.__hass; });
  await sleep(300);
  check('modern: ekran NIE wraca do pulpitu po odświeżeniu hass', await mhas('#nav button[data-s="instalacja"].on'));

  // odblokowanie poziomu 1 (PIN 0900) i zapis nastawy wymagajacej poziomu
  const stateOfM = () => p.evaluate(() => (window.__hass.states['sensor.tekla_kociol_zadana_reczna'] || {}).state);
  await mclick('[data-s="nastawy"]');
  const before = parseFloat(await stateOfM());
  await mclick('.stepper[data-id="boiler_set_manual"]');
  await sleep(300);
  check('modern: edycja prostego pola (poziom 0) nie wymaga PIN-u', !(await mhas('.sheet .pin')));
  check('modern: okno edycji pokazuje bieżącą wartość', (await mtxt('.sheet #val')).startsWith(String(Math.round(before))), await mtxt('.sheet #val'));
  // zmiana zadanej kotla (set_setpoint which=4) i weryfikacja na silniku (wartosc wzgledna – odporne na kolejnosc testow)
  await p.evaluate(() => { const r = document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot; r.querySelector('.sheet #p').click(); });
  check('modern: stepper pokazuje nową wartość przed zapisem', (await mtxt('.sheet #val')).startsWith(String(Math.round(before + 1))), await mtxt('.sheet #val'));
  await p.evaluate(() => { const r = document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot; r.querySelector('.sheet #ok').click(); });
  // odpytywanie silnika do skutku (CI bywa wolniejsze niz lokalna piaskownica – silnik potwierdza zapis asynchronicznie)
  let after = NaN;
  for (let i = 0; i < 20; i++) { await sleep(400); await p.evaluate(() => window.__refreshFromDevice()); after = parseFloat(await stateOfM()); if (after === before + 1) break; }
  check('modern: zapis zadanej kotła trafił do silnika (set_setpoint)', after === before + 1, `było ${before}, oczekiwano ${before + 1}, jest ${after}`);

  // harmonogram: edycja dnia i zapis (realny set_schedule)
  await mclick('[data-s="harmonogram"]');
  check('modern: siedem dni w harmonogramie', (await p.evaluate(() => document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelectorAll('.dayrow').length)) === 7);
  await p.evaluate(() => { document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelectorAll('.dayrow')[1].click(); });
  await sleep(300);
  check('modern: okno edycji dnia harmonogramu', await mhas('.hgrid'));
  const was12 = await p.evaluate(() => document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelector('.hgrid button[data-h="12"]').classList.contains('on'));
  await p.evaluate(() => { document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelector('.hgrid button[data-h="12"]').click(); });
  await p.evaluate(() => { document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.querySelector('.sheet #ok').click(); });
  // odpytywanie silnika do skutku (jak przy nastawie – zapis harmonogramu potwierdzany asynchronicznie)
  let co2 = '', bitMatches = false;
  for (let i = 0; i < 20; i++) {
    await sleep(400); await p.evaluate(() => window.__refreshFromDevice());
    co2 = await p.evaluate(() => window.__hass.states['sensor.tekla_co_harmonogram_rejestry'].state.split(' ')[1]);
    bitMatches = (((parseInt(co2, 16) >> 12) & 1) === 1) === !was12;
    if (bitMatches) break;
  }
  check('modern: zapis harmonogramu (godzina 12, wtorek) trafił do silnika', bitMatches, co2);

  // alarmy
  await mclick('[data-s="alarmy"]');
  check('modern: historia alarmów z wpisami', /Przegrzanie|Brak ognia/.test(await mtext()));
  check('modern: puste wpisy historii (\'-\') nie są pokazywane', !(await mtext()).includes('trwa'));
  await p.screenshot({ path: OUT + '/ha_modern_alarmy.png' });

  // brak urzadzenia: czytelny komunikat
  await p.goto(BASE + '/test/hacard.html?mode=none');
  await p.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
  await p.waitForFunction(() => typeof window.__modernReady === 'function', null, { timeout: 15000 });
  await p.evaluate(() => window.__modernReady());
  await sleep(600);
  check('modern: brak urządzenia -> czytelny komunikat', (await p.evaluate(() => document.querySelector('#rootm teklapelletcan-modern-card').shadowRoot.getElementById('body').textContent)).includes('Nie znaleziono'));

  check('modern: brak błędów JS', errs.length === 0, errs.join('|'));
  await ctx.close();
}
