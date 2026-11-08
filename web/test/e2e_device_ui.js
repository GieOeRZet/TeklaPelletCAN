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
  await p.check('#c_mirror'); await p.click('#cfgsave'); await p.waitForTimeout(1200);
  const cfg = await (await fetch(BASE + '/api/v1/config')).json();
  check('konfiguracja zapisana (tylko odczyt)', cfg.mirror === true, JSON.stringify(cfg));

  // 4. OTA: poprawny podpis
  await p.setInputFiles('#otabin', OTA + '/good.bin'); await p.setInputFiles('#otasigf', OTA + '/good.sig');
  await p.waitForTimeout(500);
  check('podpis wczytany z pliku .sig', (await p.inputValue('#otasig')).length === 128);
  await p.click('#otago'); await p.waitForFunction(() => /zweryfikowano podpis/.test(document.getElementById('msg').textContent), null, { timeout: 10000 });
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

  // 5. OTA: podmieniony plik
  await p.setInputFiles('#otabin', OTA + '/tampered.bin'); await p.click('#otago');
  await p.waitForFunction(() => /odrzucona/.test(document.getElementById('msg').textContent), null, { timeout: 10000 });
  check('OTA z podmienionym plikiem odrzucone', /bad_signature/.test(await p.locator('#msg').innerText()));

  // 5b. powrot do poprzedniego firmware
  await p.click('#rollback'); await p.waitForFunction(() => /poprzedni firmware/.test(document.getElementById('msg').textContent), null, { timeout: 8000 });
  check('powrot do poprzedniego firmware (rollback)', true);

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
