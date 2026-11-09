// Test dymny aplikacji na emulatorze Androida: łączy się z prawdziwym WebView przez Chrome DevTools Protocol (adb forward),
// sprawdza start interfejsu, most natywny (JNI + tryb demo), blokadę zapisu i okno oryginalnej karty. Zrzuty ekranu robi skrypt powłoki.
// Użycie: node cdp_smoke.js <katalog_zrzutow>   (wymaga: adb forward tcp:9222 localabstract:webview_devtools_remote_<pid>)
const http = require('http');
const { execSync } = require('child_process');
const WebSocket = require('ws');
const OUT = process.argv[2] || '.';
const fail = [];
const check = (n, c, x = '') => { console.log((c ? 'OK   ' : 'FAIL ') + n + (c ? '' : ' ' + x)); if (!c) fail.push(n); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const shot = name => { try { execSync(`adb exec-out screencap -p > ${OUT}/${name}.png`, { shell: '/bin/bash' }); } catch (e) { console.log('screencap nieudany', e.message); } };
const getJson = url => new Promise((res, rej) => http.get(url, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } }); }).on('error', rej));

async function connect(match) {
  for (let i = 0; i < 40; i++) {
    try {
      const pages = await getJson('http://127.0.0.1:9222/json');
      const pg = pages.find(p => p.url && p.url.includes(match));
      if (pg) return pg;
    } catch (e) { /* jeszcze nie gotowe */ }
    await sleep(1000);
  }
  return null;
}

(async () => {
  const pg = await connect('ui.tpc');
  check('WebView z interfejsem aplikacji wystartował', !!pg);
  if (!pg) { process.exit(1); }
  const ws = new WebSocket(pg.webSocketDebuggerUrl);
  await new Promise(r => ws.on('open', r));
  let id = 0; const wait = new Map(); const logs = [];
  ws.on('message', m => {
    const o = JSON.parse(m);
    if (o.id && wait.has(o.id)) { wait.get(o.id)(o); wait.delete(o.id); }
    if (o.method === 'Runtime.exceptionThrown') logs.push('EXC ' + JSON.stringify(o.params.exceptionDetails.exception || o.params.exceptionDetails.text).slice(0, 300));
    if (o.method === 'Runtime.consoleAPICalled' && ['error', 'assert'].includes(o.params.type)) logs.push('CONSOLE ' + o.params.args.map(a => a.value || a.description).join(' ').slice(0, 300));
  });
  const send = (method, params = {}) => new Promise(r => { const i = ++id; wait.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
  await send('Runtime.enable');

  await sleep(2500);
  const body0 = await ev('document.body.innerText');
  console.log('--- ekran startowy ---\n' + String(body0).slice(0, 300));
  check('interfejs się wyrenderował (nie czarny ekran)', /PIN|Urządzenia|TeklaPelletCAN/.test(body0 || ''), String(body0).slice(0, 120));
  check('most natywny dostępny (TPCNative.state)', (await ev("typeof TPCNative !== 'undefined' && !!JSON.parse(TPCNative.state()).sdk")) === true);
  shot('01_start');

  // pierwsze uruchomienie: ustaw PIN natywnie i przejdź dalej
  await ev("(() => { const s = JSON.parse(TPCNative.state()); if (!s.hasPin) { TPCNative.setupPin('2468'); TPCNative.setBio(false); } location.hash = '#/devices'; return 1; })()");
  await sleep(1500);
  const dev = await ev('document.body.innerText');
  check('lista urządzeń widoczna', /urządzenia/i.test(dev || ''), String(dev).slice(0, 100));
  shot('02_urzadzenia');

  // tryb demo = rdzeń firmware przez JNI
  await ev("document.querySelector('#demo').click()");
  await sleep(6000);
  const t = await ev("(document.querySelector('[data-b=\"pulpit_t_boiler\"]')||{}).textContent");
  check('demo: pulpit pokazuje temperaturę z JNI', /^\d+\.\d$/.test(t || ''), String(t));
  check('demo: stan palnika', /Modulacja|Pauza|Wy/.test((await ev("(document.querySelector('[data-b=\"pulpit_pill\"]')||{}).textContent")) || ''));
  shot('03_pulpit');

  // blokada zapisu w warstwie natywnej
  const req = (m, p, b) => ev(`new Promise(r => { const id = 'q' + Math.random(); const old = window.__tpcResp; window.__tpcResp = (i, o) => { if (i === id) { window.__tpcResp = old; r(o.status + ' ' + o.body); } else old && old(i, o); }; TPCNative.request(id, '${m}', '${p}', '${b}'); })`);
  const locked = await req('POST', '/api/v1/write', '{"id":"boiler_set_manual","value":71}');
  check('zapis zablokowany przy zablokowanej aplikacji', /^403 .*app_locked/.test(locked), String(locked));
  const wrong = JSON.parse(await ev("TPCNative.unlockPin('0000')"));
  check('zły PIN aplikacji odrzucony', wrong.ok === false);
  const good = JSON.parse(await ev("TPCNative.unlockPin('2468')"));
  check('dobry PIN odblokowuje', good.ok === true);
  const open = await req('POST', '/api/v1/write', '{"id":"boiler_set_manual","value":71}');
  check('zapis po odblokowaniu dociera do urządzenia', /^200 /.test(open), String(open));
  await sleep(3000);
  const sp = await ev("(async () => { const r = await new Promise(res => { const id='z'+Math.random(); const o=window.__tpcResp; window.__tpcResp=(i,x)=>{ if(i===id){window.__tpcResp=o;res(x);} else o&&o(i,x); }; TPCNative.request(id,'GET','/api/v1/states',''); }); return (JSON.parse(r.body).states.find(s=>s.entity_id==='sensor.tekla_kociol_zadana_reczna')||{}).state; })()");
  check('nowa zadana odczytana z kotła', String(sp) === '71', String(sp));

  // oryginalna karta w osobnym oknie (przy odblokowanej aplikacji)
  await ev('TPCNative.openOriginal()');
  await sleep(7000);
  shot('04_oryginal');
  const dpages = await getJson('http://127.0.0.1:9222/json');
  check('okno oryginalnej karty (demo.tpc) otwarte', dpages.some(p => (p.url || '').includes('demo.tpc')), JSON.stringify(dpages.map(p => p.url)));

  // wygaszenie: blokada ręczna
  await ev('TPCNative.lock()');
  await sleep(1500);
  const after = JSON.parse(await ev('TPCNative.state()'));
  check('blokada ręczna zamyka odblokowanie', after.unlocked === false);
  shot('05_po_blokadzie');
  check('brak wyjątków JS w interfejsie', logs.length === 0, logs.join(' | '));
  console.log(fail.length ? '\nNIEPOWODZENIA: ' + fail.join('; ') : '\nWSZYSTKO OK');
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
