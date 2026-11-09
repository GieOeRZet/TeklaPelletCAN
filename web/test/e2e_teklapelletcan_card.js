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

  await b.close();
  console.log(fail.length ? '\nNIEPOWODZENIA: ' + fail.join('; ') : '\nWSZYSTKO OK');
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
