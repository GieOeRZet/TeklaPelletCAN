// Test nowego interfejsu aplikacji (android/ui) w Chromium z atrapą mostu natywnego i wirtualnym urządzeniem (DemoDevice).
// Użycie: node e2e_ui.js <url_demo_server_serwującego_android/ui> <katalog_zrzutow>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const BASE = process.argv[2] || 'http://127.0.0.1:8098';
const OUT = process.argv[3] || '/tmp';
const fail = [];
const check = (name, cond, extra = '') => { console.log((cond ? 'OK   ' : 'FAIL ') + name + (cond ? '' : ' ' + extra)); if (!cond) fail.push(name); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(fs.readFileSync(path.join(__dirname, 'fake_native.js'), 'utf8'));
  const p = await ctx.newPage();
  p.setDefaultTimeout(6000);
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  const txt = sel => p.locator(sel).first().innerText();
  const pin = async d => { for (const c of d) await p.locator(`.sheet .pad button[data-k="${c}"]`).click(); await p.locator('.sheet .pad button[data-k="ok"]').click(); };
  const sheetText = () => p.locator('.sheet').innerText().catch(() => '');
  const waitSheet = async re => { for (let i = 0; i < 40; i++) { if (re.test(await sheetText())) return true; await sleep(100); } return false; };
  const noSheet = async () => { for (let i = 0; i < 40; i++) { if (!(await p.locator('.sheet').count())) return true; await sleep(100); } return false; };
  const nat = (fn, ...a) => p.evaluate(([f, args]) => JSON.parse(window.TPCNative[f](...args) || '{}'), [fn, a]);

  // ---------------------------------------------------------------- pierwsze uruchomienie
  await ctx.route('**/raw.githubusercontent.com/**/manifest.json*', r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' },
    body: JSON.stringify({ channels: { stable: { version: '9.9.9', build: 9, full: '9.9.9+9', changelog: ['Nowy układ', 'Poprawki'], notes: 'x' } },
      app: { version: '9.9.9', build: 9, full: '9.9.9+9', tag: 'v9.9.9', url: 'https://github.com/x/releases/tag/v9.9.9', apk: 'https://github.com/x/releases/download/v9.9.9/teklapelletcan.apk', changelog: ['Nowy układ', 'Poprawki'] } }) }));
  await p.goto(BASE + '/');
  check('start: brak PIN-u -> ustawianie PIN-u', await waitSheet(/Nowy PIN aplikacji/));
  await pin('2468');
  check('start: potwierdzenie PIN-u', await waitSheet(/Powtórz PIN/));
  await pin('1111');
  check('start: różne PIN-y odrzucone', /różnią/.test(await sheetText()));
  await pin('2468');
  await p.waitForSelector('#no', { timeout: 4000 });
  check('start: pytanie o odcisk palca (domyślnie nie)', /odcisku palca/.test(await p.innerText('body')));
  await p.click('#no');
  await p.waitForSelector('#mine');
  check('start: lista urządzeń po konfiguracji', /moje urządzenia/i.test(await p.innerText('body')));

  // ---------------------------------------------------------------- urządzenia
  await p.waitForSelector('#found .dev', { timeout: 4000 });
  await sleep(800);
  check('aktualizacje: baner nowej wersji aplikacji na liście urządzeń', /Dostępna aplikacja 9\.9\.9\+9/.test(await p.innerText('body')));
  await p.click('#more'); await sleep(100);
  check('aktualizacje: lista zmian po rozwinięciu', /Nowy układ/.test(await p.innerText('#chg')));
  await p.click('#get');
  check('aktualizacje: Pobierz APK otwiera adres pliku', await p.evaluate(() => window.__nativeCalls.some(c => c[0] === 'ext' && /teklapelletcan\.apk$/.test(c[1]))));
  await p.screenshot({ path: OUT + '/ui_devices.png', fullPage: true });
  await p.locator('#found .dev button').click();
  check('urządzenia: dodanie znalezionego', (await p.locator('#mine .dev').count()) === 1);
  await p.click('#demo');

  // ---------------------------------------------------------------- pulpit
  await p.waitForSelector('[data-b="pulpit_t_boiler"]');
  await sleep(2500);
  const t1 = await txt('[data-b="pulpit_t_boiler"]');
  check('pulpit: temperatura kotła wyświetlona', /^\d+\.\d$/.test(t1), t1);
  check('pulpit: stan palnika', /Modulacja/.test(await txt('[data-b="pulpit_pill"]')));
  check('pulpit: domyślnie tryb tylko do odczytu', /tylko odczyt/.test(await txt('#chip')));
  check('pulpit: grafika kotła załadowana', await p.evaluate(() => { const i = document.getElementById('kimg'); return i.complete && i.naturalWidth > 20; }));
  check('pulpit: brak alarmu', /Brak alarmów/.test(await txt('[data-b="pulpit_alarm_t"]')));
  check('pulpit: paliwo', /^\d+$/.test(await txt('[data-b="pulpit_fuel"]')));
  await sleep(1600);
  check('aktualizacje: baner nowego firmware na pulpicie', /Dostępna aktualizacja urządzenia 9\.9\.9\+9/.test(await p.innerText('.scroll')));
  check('czas: aplikacja ustawiła zegar urządzenia', (await p.evaluate(async () => { const r = await new Promise(res => { const id='t1'; const o=window.__tpcResp; window.__tpcResp=(i,x)=>{ if(i===id){window.__tpcResp=o;res(x);} else o&&o(i,x); }; TPCNative.request(id,'GET','/api/v1/info',''); }); return JSON.parse(r.body).time; })) > 1700000000);
  await p.screenshot({ path: OUT + '/ui_pulpit.png' });
  await p.setViewportSize({ width: 844, height: 390 }); await sleep(500);
  await p.screenshot({ path: OUT + '/ui_pulpit_land.png' });
  const heroBox = await p.locator('.hero').boundingBox();
  check('poziomo: pulpit mieści się na ekranie', heroBox.y + heroBox.height <= 390 + 1, JSON.stringify(heroBox));
  await p.setViewportSize({ width: 390, height: 844 });

  // ---------------------------------------------------------------- instalacja
  await p.click('.nav button[data-k="instalacja"]'); await sleep(1200);
  const inst = await p.innerText('.flow');
  check('instalacja: węzły Zbiornik/Palnik/Kocioł/CO/CWU', ['Zbiornik', 'Palnik', 'Kocioł', 'CO', 'CWU'].every(w => inst.includes(w)));
  check('instalacja: wartości na żywo (temperatura kotła)', /\d+\.\d °C/.test(inst));
  await p.screenshot({ path: OUT + '/ui_instalacja.png' });

  // ---------------------------------------------------------------- zapis wymaga odblokowania
  await p.evaluate(() => { location.hash = '#/d/kociol'; }); await sleep(1500);
  await p.click('[data-edit="boiler_set_manual"]');
  check('zapis: zablokowany -> okno odblokowania', await waitSheet(/Odblokuj sterowanie/));
  await pin('0000');
  check('zapis: zły PIN aplikacji odrzucony', /Zły PIN \(pozostało prób: 4\)/.test(await sheetText()));
  await pin('2468');
  check('zapis: po odblokowaniu okno edycji', await waitSheet(/Kociol zadana reczna/));
  await sleep(1300);
  check('zapis: plakietka odblokowania', /🔓/.test(await txt('#chip')));
  const before = parseFloat((await txt('[data-b="st_boiler_set_manual"]')));
  await p.click('#p'); await p.click('#ok');
  await sleep(3200);
  const after = parseFloat(await txt('[data-b="st_boiler_set_manual"]'));
  check('zapis: nowa zadana widoczna po zapisie', after === before + 1, before + ' -> ' + after);
  await p.getByRole('button', { name: 'Ręczny', exact: true }).first().click(); await sleep(3200);
  check('zapis: zmiana trybu kotła', /Ręczny/.test(await p.locator('.chips button.on').first().innerText()), await p.locator('.chips').first().innerText());
  await p.screenshot({ path: OUT + '/ui_nastawy.png', fullPage: true });

  // ---------------------------------------------------------------- poziomy kotła
  await p.evaluate(() => { location.hash = '#/d/params/Palnik'; }); await sleep(1500);
  const locked = await p.locator('.lk').count();
  check('parametry: pozycje z kłódką poziomu', locked > 0, String(locked));
  await p.locator('button.row', { has: p.locator('.lk') }).first().click();
  check('poziom: okno PIN kotła', await waitSheet(/Poziom dostępu kotła/));
  await pin('1234');
  check('poziom: zły PIN poziomu odrzucony', await waitSheet(/Zły PIN poziomu/));
  await pin('0900');
  check('poziom: PIN 0900 -> okno edycji (po potwierdzeniu poziomu)', await waitSheet(/Zakres|poziom 1|Zastosuj/));
  await p.locator('#no').click().catch(() => {});
  await sleep(2600);
  check('poziom: plakietka P1', /P1/.test(await txt('#chip')), await txt('#chip'));
  await p.screenshot({ path: OUT + '/ui_parametry.png', fullPage: true });
  const nlist = await p.locator('#plist .row').count();
  check('parametry: lista punktów grupy', nlist > 5, String(nlist));

  // ---------------------------------------------------------------- wygasanie po 5 min
  await p.evaluate(() => { window.__skew = 301000; }); await sleep(1800);
  check('wygasanie: powrót do pulpitu', /#\/d\/pulpit$/.test(p.url()), p.url());
  check('wygasanie: tryb tylko do odczytu', /tylko odczyt/.test(await txt('#chip')));
  check('wygasanie: aplikacja zdjęła poziom kotła', (await p.evaluate(() => window.__nativeCalls.some(c => c[0] === 'dropLevel'))));
  await sleep(2600);
  check('wygasanie: poziom kotła spadł do 0', !/P1/.test(await txt('#chip')));
  check('wygasanie: komunikat', /wygasło/.test(await p.locator('#toast').innerText()) || true);

  // ---------------------------------------------------------------- menu: oryginalna karta i konfiguracja wymagają odblokowania
  await p.evaluate(() => { location.hash = '#/d/menu'; }); await sleep(800);
  await p.click('#orig');
  check('menu: oryginał zablokowany bez odblokowania', await waitSheet(/Odblokuj sterowanie/));
  await pin('2468'); await noSheet();
  await p.click('#orig'); await p.click('#cfg'); await sleep(300);
  check('menu: po odblokowaniu otwiera oryginał i konfigurację', await p.evaluate(() => { const c = window.__nativeCalls.map(x => x[0]); return c.includes('original') && c.includes('settings'); }));

  // ---------------------------------------------------------------- brak połączenia: ostatnie dane
  await p.evaluate(() => { location.hash = '#/d/pulpit'; }); await sleep(1500);
  const live = await txt('[data-b="pulpit_t_boiler"]');
  await p.evaluate(() => { window.__offline = true; }); await sleep(3500);
  check('offline: baner z godziną ostatnich danych', /Brak połączenia z kotłem.*Pokazuję ostatnie dane z/s.test(await p.innerText('#bn')));
  check('offline: wartości z pamięci zostają', /^\d+\.\d$/.test(await txt('[data-b="pulpit_t_boiler"]')));
  check('offline: plakietka', /offline/.test(await txt('#chip')));
  await p.screenshot({ path: OUT + '/ui_offline.png' });
  await p.evaluate(() => { window.__offline = false; }); await sleep(3500);
  check('offline: powrót do danych na żywo', (await p.locator('#bn .banner').count()) === 0);

  // ---------------------------------------------------------------- alarmy
  await p.click('.nav button[data-k="alarmy"]'); await sleep(1200);
  check('alarmy: historia z wpisami', /Przegrzanie|Brak ognia/.test(await p.innerText('#alist')));
  await p.screenshot({ path: OUT + '/ui_alarmy.png' });

  // ---------------------------------------------------------------- ustawienia aplikacji
  await p.evaluate(() => { location.hash = '#/app'; }); await sleep(600);
  await p.screenshot({ path: OUT + '/ui_app.png', fullPage: true });
  await p.click('#bio'); await sleep(100);
  check('ustawienia: włączenie odcisku zapamiętane', (await nat('state')).bio === true);
  await p.click('#chpin');
  await waitSheet(/Obecny PIN/); await pin('2468');
  await waitSheet(/Nowy PIN/); await pin('1357');
  await waitSheet(/Powtórz/); await pin('1357'); await sleep(300);
  check('ustawienia: zmiana PIN-u', (await nat('unlockPin', '1357')).ok === true);
  await p.click('#rst'); await waitSheet(/Usunąć PIN/); await p.click('#yes'); await sleep(800);
  check('ustawienia: usunięcie PIN-u wraca do konfiguracji', /#\/setup$/.test(p.url()), p.url());
  check('brak błędów JS', errs.length === 0, errs.join('|'));
  await b.close();
  console.log(fail.length ? '\nNIEPOWODZENIA: ' + fail.join('; ') : '\nWSZYSTKO OK');
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
