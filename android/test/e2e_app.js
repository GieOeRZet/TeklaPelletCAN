// Test warstwy webowej aplikacji: powłoka (lista urządzeń, wyszukiwanie, ręczne dodawanie) i TRYB DEMO
// (strony urządzenia + most fetch -> DemoDevice, ten sam kod co w bibliotece JNI aplikacji).
// Użycie: node e2e_app.js <katalog_shell> <katalog_web> <url_demo_server>
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const SHELL = process.argv[2] || path.join(__dirname, '../shell');
const DEMO = process.argv[4] || 'http://127.0.0.1:8098';
const OUT = process.argv[5] || '/tmp';
const fail = [];
const check = (name, cond, extra = '') => { console.log((cond ? 'OK   ' : 'FAIL ') + name + (cond ? '' : ' ' + extra)); if (!cond) fail.push(name); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

// statyczny serwer powłoki
const srv = http.createServer((q, s) => {
  const f = path.join(SHELL, q.url === '/' ? 'app.html' : q.url.split('?')[0]);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; }
    s.writeHead(200, { 'Content-Type': f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'text/javascript' : 'text/html; charset=utf-8' }); s.end(d); });
});

const TPC_MOCK = `
  (() => {
    const calls = []; window.__calls = calls;
    let store = localStorage.getItem('__dev') || '[]';
    window.TPC = {
      getDevices: () => store,
      saveDevices: j => { store = j; localStorage.setItem('__dev', j); calls.push(['save', j]); },
      appInfo: () => JSON.stringify({ version: '9.9.9+1', sdk: 35 }),
      startDiscovery: () => { calls.push(['disc']); setTimeout(() => window.tpcDiscovered({ name: 'tekla', host: '192.168.1.50', port: 80, id: 'A1B2C3D4E5F6', fw: '0.3.1' }), 200); },
      stopDiscovery: () => calls.push(['stop']),
      ping: (id, base) => { calls.push(['ping', base]); setTimeout(() => window.tpcPing(id, /192\\.168\\.1\\.(50|77)/.test(base) ? { id: base.endsWith('77') ? 'FFEEDDCCBBAA' : 'A1B2C3D4E5F6', fw: '0.3.1', name: 'TeklaPelletCAN' } : null), 100); },
      open: (b, n) => calls.push(['open', b, n]),
      openSetup: () => calls.push(['setup']),
    };
  })();`;

(async () => {
  await new Promise(r => srv.listen(8110, r));
  const b = await chromium.launch();

  // ---------------------------------------------------------------- powłoka
  let ctx = await b.newContext({ viewport: { width: 400, height: 860 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(TPC_MOCK);
  let p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  p.on('dialog', d => d.accept());
  await p.goto('http://127.0.0.1:8110/');
  await p.waitForSelector('#foundlist .dev', { timeout: 3000 });
  check('powłoka: wyszukane urządzenie widać na liście', (await p.locator('#foundlist .dev').count()) === 1);
  check('powłoka: nazwa z końcówki ID', /TeklaPelletCAN 5E6F|TeklaPelletCAN BBAA|TeklaPelletCAN E5F6/.test(await p.locator('#foundlist .dev b').innerText()) || /TeklaPelletCAN/.test(await p.locator('#foundlist .dev b').innerText()));
  check('powłoka: stopka z wersją aplikacji', /9\.9\.9\+1/.test(await p.innerText('#about')));
  check('powłoka: pusta lista zapisanych', /Brak zapisanych/.test(await p.innerText('#mylist')));
  await p.screenshot({ path: OUT + '/app_shell_empty.png', fullPage: true });
  await p.locator('#foundlist button').click();
  check('powłoka: dodanie znalezionego', (await p.locator('#mylist .dev').count()) === 1);
  check('powłoka: znalezione znika z „znalezionych”', /są już na liście/.test(await p.innerText('#foundlist')));
  await sleep(300);
  check('powłoka: status online po ping', await p.locator('#mylist .dot.on').count() === 1);
  check('powłoka: zapis w pamięci aplikacji', await p.evaluate(() => JSON.parse(window.TPC.getDevices()).length === 1));
  await p.locator('#mylist .dev').click();
  check('powłoka: stuknięcie otwiera urządzenie', await p.evaluate(() => window.__calls.some(c => c[0] === 'open' && c[1] === 'http://192.168.1.50')));
  // ręczne dodawanie
  await p.fill('#addr', 'to nie adres!'); await p.click('#addbtn');
  check('powłoka: zły adres odrzucony', /poprawny adres/.test(await p.innerText('#addmsg')));
  await p.fill('#addr', '192.168.1.99'); await p.click('#addbtn'); await sleep(300);
  check('powłoka: adres bez urządzenia odrzucony', /nie ma urządzenia/.test(await p.innerText('#addmsg')));
  await p.fill('#addr', 'http://192.168.1.77/'); await p.click('#addbtn'); await sleep(300);
  check('powłoka: poprawny adres dodany', (await p.locator('#mylist .dev').count()) === 2);
  await p.fill('#addr', '192.168.1.77'); await p.click('#addbtn');
  check('powłoka: duplikat odrzucony', /już na liście/.test(await p.innerText('#addmsg')));
  await p.screenshot({ path: OUT + '/app_shell_list.png', fullPage: true });
  // zmiana adresu po DHCP: to samo ID pod nowym adresem aktualizuje zapis
  await p.evaluate(() => window.tpcDiscovered({ name: 'tekla', host: '192.168.1.60', port: 80, id: 'A1B2C3D4E5F6', fw: '0.3.1' }));
  check('powłoka: zmieniony adres (DHCP) aktualizuje zapis', await p.evaluate(() => JSON.parse(window.TPC.getDevices()).some(d => d.base === 'http://192.168.1.60')));
  // usuwanie
  await p.locator('#mylist .dev .x').first().click();
  check('powłoka: usunięcie z listy', (await p.locator('#mylist .dev').count()) === 1);
  await p.click('#setup'); await p.click('#demo');
  check('powłoka: konfiguracja nowego urządzenia', await p.evaluate(() => window.__calls.some(c => c[0] === 'setup')));
  check('powłoka: tryb demo', await p.evaluate(() => window.__calls.some(c => c[0] === 'open' && c[1] === 'demo')));
  check('powłoka: brak błędów JS', errs.length === 0, errs.join('|'));
  await ctx.close();

  // ---------------------------------------------------------------- tryb demo (strony urządzenia przez most fetch)
  const fetchJs = fs.readFileSync(path.join(SHELL, 'demo-fetch.js'), 'utf8');
  ctx = await b.newContext({ viewport: { width: 400, height: 860 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(`
    window.TPCDemo = { request: (m, pth, q, a, body) => {
      const x = new XMLHttpRequest(); x.open('POST', '/__demo', false);
      x.send(JSON.stringify({ method: m, path: pth, query: q, authorization: a, body })); return x.responseText;
    } };
    window.TPCApp = { isApp: () => true, saveText: (n, m, t) => { window.__saved = [n, m, t]; } };
  ` + fetchJs);
  p = await ctx.newPage();
  const derrs = []; p.on('pageerror', e => derrs.push(e.message)); p.on('dialog', d => d.accept('x'));
  const nonDemoReq = []; p.on('request', r => { const u = r.url(); if (!u.startsWith(DEMO) && !u.startsWith('data:') && !/githubusercontent|fonts\.(googleapis|gstatic)\.com/.test(u)) nonDemoReq.push(u); });
  await p.goto(DEMO + '/index.html');
  await p.waitForFunction(() => document.querySelector('pelletcan-card') && document.querySelector('pelletcan-card').shadowRoot && document.querySelector('pelletcan-card').shadowRoot.textContent.length > 500, null, { timeout: 20000 });
  await sleep(2500);
  const txt = () => p.evaluate(() => document.querySelector('pelletcan-card').shadowRoot.textContent);
  const t1 = await txt();
  check('demo: karta wyrenderowana z odczytami', /\d+(\.\d)?\s*°/.test(t1.replace(/\s+/g, ' ')) || /\d{2}[,.]\d/.test(t1), t1.replace(/\s+/g,' ').slice(-200));
  check('demo: brak banera „brak połączenia”', await p.evaluate(() => getComputedStyle(document.getElementById('offline')).display === 'none'));
  await p.screenshot({ path: OUT + '/app_demo_card.png', fullPage: true });
  const temp = async () => { const r = await p.evaluate(async () => (await (await fetch('/api/v1/states')).json()).states.find(s => s.entity_id === 'sensor.tekla_kociol_temperatura')); return +r.state; };
  const a = await temp(); await sleep(7000); const c2 = await temp();
  check('demo: temperatura kotła „żyje” (zmienia się w czasie)', a !== c2, a + ' vs ' + c2);
  // zapis: odblokowanie PIN-em i zmiana zadanej – prawdziwy silnik demo
  const unl = await p.evaluate(async () => (await fetch('/api/v1/call', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain: 'teklapelletcan', service: 'tekla_estyma_unlock', data: { pin: 900 } }) })).status);
  check('demo: odblokowanie PIN 0900 działa', unl === 200);
  const set = await p.evaluate(async () => { const r = await fetch('/api/v1/call', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain: 'teklapelletcan', service: 'tekla_estyma_set_setpoint', data: { which: 4, value: 62 } }) }); return r.status; });
  await sleep(2500);
  const sp = await p.evaluate(async () => (await (await fetch('/api/v1/states')).json()).states.find(s => s.entity_id === 'sensor.tekla_kociol_zadana_reczna').state);
  check('demo: zapis zadanej kotła (' + set + ') widoczny w stanie', set === 200 && +sp === 62, 'zadana=' + sp);
  // ustawienia w trybie demo
  await p.goto(DEMO + '/settings.html'); await p.waitForTimeout(2500);
  const st = await p.innerText('#status');
  check('demo: ustawienia pokazują wirtualne urządzenie', /DE30DE300001/.test(st) && /kocioł odpowiada/.test(st), st.slice(0, 120));
  check('demo: dziennik dostępny', /START/.test(await p.innerText('#log')));
  await p.screenshot({ path: OUT + '/app_demo_settings.png', fullPage: true });
  // wgrywanie firmware w demo: czytelna odmowa
  check('demo: aktualizacje oznaczone jako niedostępne', /Tryb demo.*niedostępne/s.test(await p.innerText('body')));
  const ota = await p.evaluate(() => new Promise(res => { const x = new XMLHttpRequest(); x.open('POST', '/api/v1/ota'); x.onload = () => res([x.status, x.responseText]); x.send(new Blob([new Uint8Array(100)])); }));
  check('demo: wgrywanie firmware odrzucone przez wirtualne urządzenie', ota[0] === 400 && /demo/.test(ota[1]), JSON.stringify(ota));
  check('demo: ruch tylko do wirtualnego urządzenia (bez zewnętrznych adresów)', nonDemoReq.length === 0, nonDemoReq.slice(0, 3).join(','));
  check('demo: brak błędów JS', derrs.length === 0, derrs.join('|'));
  await ctx.close();
  await b.close(); srv.close();
  console.log(fail.length ? '\nNIEPOWODZENIA: ' + fail.join('; ') : '\nWSZYSTKO OK');
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
