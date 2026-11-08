// Test UI urzadzenia w przegladarce: portal pierwszej konfiguracji, ustawienia, OTA, logi.
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8102';
const OTA = process.argv[3] || '/tmp/claude-0/ota';
const fail = [];
const check = (name, cond, extra = '') => { console.log((cond ? 'OK   ' : 'FAIL ') + name + (cond ? '' : ' ' + extra)); if (!cond) fail.push(name); };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 420, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  p.on('dialog', async d => { await d.accept('qwerty123'); });

  // 1. pierwsze wejscie na / -> portal
  await p.goto(BASE + '/index.html'); await p.waitForTimeout(1500);
  check('przekierowanie na portal przy braku hasla', p.url().endsWith('/portal.html'), p.url());

  // 2. portal: skan, wybor sieci, zapis
  await p.waitForSelector('.net', { timeout: 5000 });
  check('skan pokazuje sieci', (await p.locator('.net').count()) === 3);
  await p.locator('.net', { hasText: 'Dom-2.4G' }).click();
  check('klik w siec wpisuje SSID', (await p.inputValue('#ssid')) === 'Dom-2.4G');
  // literowka w powtorzeniu hasla jest wychwycona zanim cokolwiek trafi do urzadzenia
  await p.fill('#pw', 'qwerty123'); await p.fill('#pw2', 'qwerty124'); await p.fill('#wpw', 'haslo-wifi');
  await p.click('#save'); await p.waitForTimeout(400);
  check('rozne hasla w portalu odrzucone', /różnią/.test(await p.locator('#msg').innerText()));
  check('urzadzenie nadal bez hasla po literowce', (await (await fetch(BASE + '/api/v1/info')).json()).password_set === false);
  await p.fill('#pw2', 'qwerty123');
  await p.check('#static'); await p.fill('#ip', '192.168.10.250'); await p.fill('#mask', '255.255.254.0'); await p.fill('#gw', '192.168.10.1');
  await p.screenshot({ path: '/tmp/claude-0/ui_portal.png', fullPage: true });
  await p.click('#save');
  await p.waitForFunction(() => /Połączono/.test(document.getElementById('msg').textContent), null, { timeout: 15000 });
  check('portal potwierdza polaczenie', true);
  check('token zapisany w przegladarce', await p.evaluate(() => !!localStorage.getItem('tpc_token')));
  const info = await (await fetch(BASE + '/api/v1/info')).json();
  check('urzadzenie ma ustawione haslo', info.password_set === true);
  const dup = await fetch(BASE + '/api/v1/setup', { method: 'POST', body: JSON.stringify({ password: 'inne1234', ssid: 'x' }) });
  check('ponowny setup odrzucony (nie da sie przejac urzadzenia)', dup.status === 403);

  // 3. ustawienia
  await p.goto(BASE + '/settings.html'); await p.waitForTimeout(2000);
  const status = await p.locator('#status').innerText();
  check('ustawienia pokazuja ID urzadzenia', status.includes('A1B2C3D4E5F6'), status);
  await p.uncheck('#c_write'); await p.click('#cfgsave'); await p.waitForTimeout(1200);
  const cfg = await (await fetch(BASE + '/api/v1/config')).json();
  check('konfiguracja zapisana (zapis wylaczony = tylko odczyt)', cfg.mirror === true, JSON.stringify(cfg));

  // 3b. zmiana Wi-Fi z potwierdzeniem (sim: sukces po ~1,5 s; zle haslo 'zle' -> niepowodzenie)
  await p.fill('#ssid', 'NowaSiec'); await p.fill('#wpw', 'ok-haslo'); await p.click('#wifisave');
  await p.waitForFunction(() => /Wysłano dane sieci/.test(document.getElementById('msg').textContent), null, { timeout: 4000 });
  check('zmiana Wi-Fi: od razu potwierdzenie wyslania', true);
  await p.waitForFunction(() => /Połączono z siecią/.test(document.getElementById('msg').textContent), null, { timeout: 20000 });
  check('zmiana Wi-Fi: potwierdzenie polaczenia z adresem', true);
  await p.fill('#wpw', 'zle'); await p.click('#wifisave');
  await p.waitForFunction(() => /Nie udało się połączyć/.test(document.getElementById('msg').textContent), null, { timeout: 20000 });
  check('zmiana Wi-Fi: komunikat przy zlym hasle', true);

  // 3a. grafiki panelu: domyslnie PELNE (bez ustawienia w konfiguracji karty); 'domyslne' wylacza. Czerwony kociol = img/panel/013.png
  const panelFiles = async q => { const pg = await b.newPage({ viewport: { width: 520, height: 420 } }); const f = new Set(); pg.on('request', r => { if (r.url().includes('/img/panel/')) f.add(r.url().split('/img/panel/')[1].split('?')[0]); });
    await pg.goto(BASE + '/index.html' + q); await pg.waitForTimeout(7000); await pg.close(); return f; };
  const fDefault = await panelFiles(''), fBasic = await panelFiles('?grafiki=domyslne');
  check('grafiki pelne domyslnie (karta bez ustawienia): oryginalny kociol Estyma', fDefault.has('013.png'), [...fDefault].join(','));
  check('grafiki: domyslne wylacza pelne (bez kotla Estyma)', !fBasic.has('013.png'), [...fBasic].join(','));

  // 3a2. grafika kotla: wybor w ustawieniach (bez restartu) i geometria na karcie (ta sama podstawa i srodek dla kazdego typu)
  await p.reload(); await p.waitForTimeout(2500);
  check('ustawienia: cztery miniatury kotla', (await p.locator('#boilers .net').count()) === 4);
  await p.locator('#boilers .net').nth(1).click(); await p.waitForTimeout(800);      // typ 12
  check('wybor grafiki kotla zapisany (typ 12)', (await (await fetch(BASE + '/api/v1/config')).json()).boiler_image === 12);
  const rr = await (await fetch(BASE + '/api/v1/config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ boiler_image: 14 }) })).json();
  check('zmiana samej grafiki nie wymaga restartu', rr.restart_required === false, JSON.stringify(rr));
  const geo = {};
  for (const w of [360, 520, 900]) for (const n of [11, 12, 13, 14]) {
    const pg = await b.newPage({ viewport: { width: w, height: Math.round(w * 0.8) } });
    await pg.goto(BASE + '/index.html?boiler=' + n); await pg.waitForTimeout(4500);
    const r = await pg.evaluate(() => { let o = null; const f = x => { if (o) return; if (x.shadowRoot) { const e = x.shadowRoot.querySelector('.boil'); if (e) { o = e; return; } f(x.shadowRoot); } x.childNodes && x.childNodes.forEach(f); }; f(document.body); if (!o) return null; const bb = o.getBoundingClientRect(); return { cx: Math.round(bb.x + bb.width / 2), bottom: Math.round(bb.bottom), h: Math.round(bb.height) }; });
    (geo[w] = geo[w] || {})[n] = r; await pg.close();
  }
  for (const w of [360, 520, 900]) {
    const v = Object.values(geo[w]);
    check('kociol: kazdy typ ma ta sama podstawe i srodek (szer. ' + w + ')', v.every(x => x) && v.every(x => Math.abs(x.bottom - v[0].bottom) <= 2 && Math.abs(x.cx - v[0].cx) <= 2), JSON.stringify(geo[w]));
    const hs = v.map(x => x.h); check('kociol: wysokosci porownywalne (szer. ' + w + ')', Math.max(...hs) / Math.min(...hs) < 1.25, hs.join(','));
  }

  // 3b2. karta: ekran "Informacje o programie" pokazuje nowa wersje modulu i changelog z manifestu
  const mf = { channels: { beta: { version: '0.3.0', build: 99, full: '0.3.0+99', date: '2026-11-08 20:00 UTC', notes: 'x', changelog: ['Pierwsza zmiana testowa', 'Druga zmiana testowa'] } } };
  const ip2 = await b.newPage({ viewport: { width: 520, height: 420 } });
  await ip2.route('**/updates/manifest.json*', r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(mf) }));
  await ip2.goto(BASE + '/index.html?screen=info'); await ip2.waitForTimeout(8000);
  const infoText = await ip2.evaluate(() => { const o = []; const w = n => { if (n.nodeType === 3) o.push(n.textContent.trim()); if (n.shadowRoot) w(n.shadowRoot); n.childNodes && n.childNodes.forEach(w); }; w(document.body); return o.filter(Boolean).join(' | '); });
  check('INFO karty: wersja modulu z urzadzenia', /TeklaPelletCAN 0\.3\.0\+1\b/.test(infoText), infoText.slice(0, 200));
  check('INFO karty: dostepna aktualizacja 0.3.0+99 z data', /Dostępna aktualizacja: 0\.3\.0\+99/.test(infoText) && /2026-11-08/.test(infoText));
  check('INFO karty: changelog z manifestu', /Pierwsza zmiana testowa/.test(infoText) && /Druga zmiana testowa/.test(infoText));
  check('INFO karty: link do instalacji w Ustawieniach', /Zainstaluj w Ustawieniach/.test(infoText));
  await ip2.screenshot({ path: '/tmp/claude-0/ui_info.png' });
  await ip2.close();

  // 3c. aktualizacja jednym kliknieciem: manifest + plik + podpis "z internetu" (przechwycone), wgranie do urzadzenia
  const fs = require('fs');
  const good = fs.readFileSync(OTA + '/good.bin'), goodSig = fs.readFileSync(OTA + '/good.sig', 'utf8').trim(), pkg = fs.readFileSync(OTA + '/good.pkg.bin');
  const manifest = { channels: { beta: { version: '0.3.0', build: 99, full: '0.3.0+99', file: 'beta/teklapelletcan.bin', sig: 'beta/teklapelletcan.bin.sig',
    sha256: 'ab'.repeat(32), embedded: true, size: pkg.length, notes: 'Test aktualizacji', date: '2026-11-08 20:00 UTC' } } };
  await p.route('**/fake-updates/manifest.json*', r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(manifest) }));
  await p.route('**/fake-updates/beta/teklapelletcan.bin*', r => r.fulfill({ status: 200, contentType: 'application/octet-stream', headers: { 'access-control-allow-origin': '*' }, body: pkg }));
  let sigFetched = false;
  await p.route('**/fake-updates/beta/teklapelletcan.bin.sig*', r => { sigFetched = true; r.fulfill({ status: 200, contentType: 'text/plain', headers: { 'access-control-allow-origin': '*' }, body: goodSig }); });
  await p.evaluate(u => localStorage.setItem('tpc_manifest_url', u), BASE + '/fake-updates/manifest.json');
  await p.reload(); await p.waitForTimeout(2500);
  check('ustawienia: automatyczna kontrola pokazuje nowa wersje', /0\.3\.0\+99/.test(await p.locator('#upmsg').innerText()) && /Test aktualizacji/.test(await p.locator('#upmsg').innerText()));
  check('przycisk "Pobierz i zainstaluj" widoczny', await p.locator('#upgo').isVisible());
  await p.click('#upgo');
  await p.waitForFunction(() => /zweryfikowano podpis/.test(document.getElementById('upmsg').textContent), null, { timeout: 15000 });
  check('aktualizacja pobrana z "internetu" i przyjeta przez urzadzenie (podpis OK)', true);
  check('pakiet z wbudowanym podpisem: osobny plik .sig NIE jest pobierany', sigFetched === false);
  const idx = await (async () => { const pg = await b.newPage(); await pg.route(u => !u.href.startsWith(BASE), r => r.abort()); /* przeglądarka bez internetu: blokuj wszystko poza urządzeniem */ await pg.goto(BASE + '/index.html'); await pg.waitForTimeout(3000); const t = await pg.locator('#setlink').innerText(); await pg.close(); return t; })();
  check('brak internetu w przegladarce: strona dziala bez wskaznika', /Ustawienia, aktualizacja, dziennik/.test(idx), idx);

  // 4. OTA: poprawny podpis
  await p.evaluate(() => document.querySelector('details').open = true);
  await p.setInputFiles('#otabin', OTA + '/good.bin'); await p.setInputFiles('#otasigf', OTA + '/good.sig');
  await p.waitForTimeout(500);
  check('podpis wczytany z pliku .sig', (await p.inputValue('#otasig')).length === 128);
  await p.click('#otago'); await p.waitForFunction(() => /zweryfikowano podpis/.test(document.getElementById('upmsg').textContent), null, { timeout: 10000 });
  check('OTA z poprawnym podpisem przyjete', true);
  // 4b. zmiana hasla w ustawieniach (rozne hasla -> blad; poprawne -> zmiana, klient nadal sparowany)
  await p.fill('#np1', 'nowe-haslo-1'); await p.fill('#np2', 'nowe-haslo-2'); await p.click('#pwsave'); await p.waitForTimeout(300);
  check('zmiana hasla: rozne hasla odrzucone', /różnią/.test(await p.locator('#msg').innerText()));
  await p.fill('#np2', 'nowe-haslo-1'); await p.click('#pwsave'); await p.waitForFunction(() => /Hasło zmienione/.test(document.getElementById('msg').textContent), null, { timeout: 5000 });
  check('zmiana hasla zadziałała', true);
  const pr = await fetch(BASE + '/api/v1/pair', { method: 'POST', body: JSON.stringify({ password: 'nowe-haslo-1', client_id: 'nowy-klient' }) });
  const po = await fetch(BASE + '/api/v1/pair', { method: 'POST', body: JSON.stringify({ password: 'qwerty123', client_id: 'nowy-klient2' }) });
  check('nowe haslo dziala przy parowaniu, stare juz nie', pr.status === 200 && po.status === 401);
  check('sparowana przegladarka dziala dalej po zmianie hasla', (await (await fetch(BASE + '/api/v1/clients', { headers: { Authorization: 'Bearer ' + await p.evaluate(() => localStorage.getItem('tpc_token')) } })).json()).clients.length >= 1);

  // 4b. reczne wgranie: sam plik pakietu (podpis w srodku), bez pola podpisu
  await p.evaluate(() => { document.getElementById('otasig').value = ''; });
  await p.setInputFiles('#otabin', OTA + '/good.pkg.bin'); await p.click('#otago');
  await p.waitForFunction(() => /zweryfikowano podpis/.test(document.getElementById('upmsg').textContent), null, { timeout: 10000 });
  check('reczne wgranie samego pliku z wbudowanym podpisem (bez .sig)', true);
  await p.setInputFiles('#otabin', OTA + '/good.bin'); await p.click('#otago');   // goly obraz bez podpisu
  await p.waitForFunction(() => /odrzucona/.test(document.getElementById('upmsg').textContent), null, { timeout: 10000 });
  check('goly obraz bez podpisu odrzucony', /bad_image/.test(await p.locator('#upmsg').innerText()));
  await p.evaluate(() => { document.getElementById('otasig').value = ''; });

  // 5. OTA: podmieniony plik
  await p.evaluate(s => { document.getElementById('otasig').value = s; document.getElementById('upmsg').textContent = ''; }, goodSig);   // stary tryb: osobny podpis od INNEGO pliku
  await p.setInputFiles('#otabin', OTA + '/tampered.bin'); await p.click('#otago');
  await p.waitForFunction(() => /odrzucona/.test(document.getElementById('upmsg').textContent), null, { timeout: 10000 });
  check('OTA z podmienionym plikiem odrzucone', /bad_signature/.test(await p.locator('#upmsg').innerText()));

  // 5b. powrot do poprzedniego firmware
  await p.click('#rollback'); await p.waitForFunction(() => /poprzedni firmware/.test(document.getElementById('msg').textContent), null, { timeout: 8000 });
  check('powrot do poprzedniego firmware (rollback)', true);

  // 5c. panel WWW otwarty: zapis bez tokenu z tego samego origin dziala, z obcego origin jest odrzucany; po wylaczeniu wymaga hasla
  const http = require('http');
  const post = (path, body, headers) => new Promise(res => { const u = new URL(BASE); const rq = http.request({ host: u.hostname, port: u.port, path, method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json', Host: u.host }, headers) }, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => res({ s: r.statusCode, b: d })); }); rq.end(JSON.stringify(body)); });
  const call = { domain: 'teklapelletcan', service: 'tekla_estyma_unlock', data: { pin: 900 } };
  check('panel otwarty: zapis bez hasla z tego samego origin', (await post('/api/v1/call', call, { Origin: BASE })).s === 200);
  check('panel otwarty: zapis bez przegladarki (bez Origin)', (await post('/api/v1/call', call, {})).s === 200);
  check('obca strona w przegladarce (inny Origin) odrzucona', (await post('/api/v1/call', call, { Origin: 'https://zla-strona.example' })).s === 401);
  await p.uncheck('#c_web'); await p.click('#cfgsave'); await p.waitForTimeout(1200);
  check('po wylaczeniu panelu otwartego zapis wymaga hasla', (await post('/api/v1/call', call, { Origin: BASE })).s === 401);
  await p.check('#c_web'); await p.click('#cfgsave'); await p.waitForTimeout(1200);
  check('ponowne wlaczenie panelu otwartego', (await post('/api/v1/call', call, { Origin: BASE })).s === 200);

  // 6. logi i raport
  await p.click('#logrefresh'); await p.waitForTimeout(600);
  const log = await p.locator('#log').innerText();
  check('dziennik zawiera wpisy OTA i konfiguracji', log.includes('OTA: ok') && log.includes('OTA: bad_signature') && log.includes('Konfiguracja zapisana'), log.slice(0, 300));
  const dl = await fetch(BASE + '/api/v1/log?download=1');
  check('pobieranie dziennika (Content-Disposition)', /attachment; filename="teklapelletcan-A1B2C3D4E5F6-log.txt"/.test(dl.headers.get('content-disposition') || ''));
  const rep = await (await fetch(BASE + '/api/v1/export')).text();
  check('raport zawiera diagnostyke i dziennik', rep.includes('--- silnik ---') && rep.includes('--- dziennik ---') && rep.includes('sdo_ok'));
  check('raport nie zawiera hasel', !/qwerty123|haslo-wifi/.test(rep));
  const diag = await (await fetch(BASE + '/api/v1/diag')).json();
  check('diagnostyka: silnik widzi ramki CAN', diag.engine.rx_frames > 0 && diag.engine.sdo_ok > 0, JSON.stringify(diag.engine));
  await p.screenshot({ path: '/tmp/claude-0/ui_settings.png', fullPage: true });

  check('brak bledow JS', errs.length === 0, JSON.stringify(errs));
  await b.close();
  console.log(fail.length ? 'NIEPOWODZENIA: ' + fail.join(', ') : 'WSZYSTKO OK');
  process.exit(fail.length ? 1 : 0);
})();
