// Test oryginalnych stron urządzenia (karta, konfiguracja) w TRYBIE DEMO aplikacji
// (strony urządzenia + most fetch -> DemoDevice, ten sam kod co w bibliotece JNI aplikacji).
// Użycie: node e2e_app.js <katalog_ui> <katalog_web> <url_demo_server>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const SHELL = process.argv[2] || path.join(__dirname, '../ui');
const DEMO = process.argv[4] || 'http://127.0.0.1:8098';
const OUT = process.argv[5] || '/tmp';
const fail = [];
const check = (name, cond, extra = '') => { console.log((cond ? 'OK   ' : 'FAIL ') + name + (cond ? '' : ' ' + extra)); if (!cond) fail.push(name); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await chromium.launch();

  // ---------------------------------------------------------------- tryb demo (strony urządzenia przez most fetch)
  const fetchJs = fs.readFileSync(path.join(SHELL, 'demo-fetch.js'), 'utf8');
  const ctx = await b.newContext({ viewport: { width: 400, height: 860 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(`
    window.TPCDemo = { request: (m, pth, q, a, body) => {
      const x = new XMLHttpRequest(); x.open('POST', '/__demo', false);
      x.send(JSON.stringify({ method: m, path: pth, query: q, authorization: a, body })); return x.responseText;
    } };
    window.TPCApp = { isApp: () => true, saveText: (n, m, t) => { window.__saved = [n, m, t]; } };
  ` + fetchJs);
  const p = await ctx.newPage();
  const derrs = []; p.on('pageerror', e => derrs.push(e.message)); p.on('dialog', d => d.accept('x'));
  const nonDemoReq = []; p.on('request', r => { const u = r.url(); if (!u.startsWith(DEMO) && !u.startsWith('data:') && !/githubusercontent|fonts\.(googleapis|gstatic)\.com/.test(u)) nonDemoReq.push(u); });
  await p.goto(DEMO + '/classic.html');
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
  await b.close();
  console.log(fail.length ? '\nNIEPOWODZENIA: ' + fail.join('; ') : '\nWSZYSTKO OK');
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
