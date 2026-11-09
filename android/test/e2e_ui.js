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
  // ensureLevel() odpytuje urzadzenie do ok. 4 s przed pokazaniem bledu PIN-u poziomu - dajemy wiecej marginesu.
  const waitSheet = async re => { for (let i = 0; i < 80; i++) { if (re.test(await sheetText())) return true; await sleep(100); } return false; };
  const noSheet = async () => { for (let i = 0; i < 80; i++) { if (!(await p.locator('.sheet').count())) return true; await sleep(100); } return false; };
  const waitFor = async fn => { for (let i = 0; i < 40; i++) { if (await fn().catch(() => false)) return true; await sleep(100); } return false; };
  const closeAny = async () => { for (let i = 0; i < 3; i++) { if (await p.locator('.scrim').count()) await p.locator('.scrim').click({ position: { x: 5, y: 5 } }).catch(() => {}); } };
  const nat = (fn, ...a) => p.evaluate(([f, args]) => JSON.parse(window.TPCNative[f](...args) || '{}'), [fn, a]);
  const goHash = async h => { await p.evaluate(hh => { location.hash = hh; }, h); await sleep(800); };

  // ---------------------------------------------------------------- pierwsze uruchomienie: BEZ wymuszonego PIN-u
  // (PIN aplikacji chroni tylko start, nie jest juz wymagany od razu - patrz main.js render('start'))
  await ctx.route('**/raw.githubusercontent.com/**/manifest.json*', r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' },
    body: JSON.stringify({ channels: { stable: { version: '9.9.9', build: 9, full: '9.9.9+9', changelog: ['Nowy układ', 'Poprawki'], notes: 'x' } },
      app: { version: '9.9.9', build: 9, full: '9.9.9+9', tag: 'v9.9.9', url: 'https://github.com/x/releases/tag/v9.9.9', apk: 'https://github.com/x/releases/download/v9.9.9/teklapelletcan.apk', changelog: ['Nowy układ', 'Poprawki'] } }) }));
  await p.goto(BASE + '/');
  await p.waitForSelector('#mine');
  check('start: lista urządzeń od razu, bez wymuszania PIN-u', /moje urządzenia/i.test(await p.innerText('body')));

  // ---------------------------------------------------------------- urządzenia
  await p.waitForSelector('#found .dev', { timeout: 4000 });
  await sleep(800);
  check('aktualizacje: baner nowej wersji aplikacji na liście urządzeń', /Dostępna aplikacja 9\.9\.9\+9/.test(await p.innerText('body')));
  await p.click('#more'); await sleep(100);
  check('aktualizacje: lista zmian po rozwinięciu', /Nowy układ/.test(await p.innerText('#chg')));
  await p.click('#get');
  check('aktualizacje: Pobierz APK otwiera adres pliku', await p.evaluate(() => window.__nativeCalls.some(c => c[0] === 'ext' && /teklapelletcan\.apk$/.test(c[1]))));
  await p.screenshot({ path: OUT + '/ui_devices.png', fullPage: true });
  // Klik „Dodaj” na znalezionym urządzeniu od razu wybiera je i nawiguje do pulpitu (patrz open() w main.js).
  await p.locator('#found .dev button').click();
  await p.waitForSelector('[data-b="pulpit_t_boiler"]', { timeout: 4000 });
  check('urządzenia: dodanie znalezionego nawiguje do pulpitu', /#\/d\/pulpit$/.test(p.url()), p.url());

  // ---------------------------------------------------------------- pulpit
  await p.waitForSelector('[data-b="pulpit_t_boiler"]');
  await sleep(2500);
  const t1 = await txt('[data-b="pulpit_t_boiler"]');
  check('pulpit: temperatura kotła wyświetlona', /^\d+\.\d$/.test(t1), t1);
  check('pulpit: stan palnika', /Modulacja/.test(await txt('[data-b="pulpit_pill"]')));
  check('pulpit: domyślnie brak plakietki w nagłówku (bez aktywnej sesji poziomu)', (await p.locator('#chip').count()) === 0);
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

  // ---------------------------------------------------------------- zapis dziala od razu, bez PIN-u aplikacji
  // (PIN chroni tylko opcjonalnie start apki - nie warunkuje juz zapisu, patrz Proxy.handle() w Kotlinie)
  await goHash('#/d/kociol');
  await p.click('[data-edit="boiler_set_manual"]');
  check('zapis: okno edycji od razu, bez PIN-u aplikacji', await waitSheet(/Kociol zadana reczna/));
  const before = parseFloat((await txt('[data-b="st_boiler_set_manual"]')));
  await p.click('#p'); await p.click('#ok');
  await sleep(3200);
  const after = parseFloat(await txt('[data-b="st_boiler_set_manual"]'));
  check('zapis: nowa zadana widoczna po zapisie', after === before + 1, before + ' -> ' + after);
  await p.getByRole('button', { name: 'Ręczny', exact: true }).click(); await sleep(3200);
  check('zapis: zmiana trybu kotła', /Ręczny/.test(await p.locator('.chips button.on').innerText()));
  await p.screenshot({ path: OUT + '/ui_kociol.png', fullPage: true });
  const stateOf = id => p.evaluate(async id => { const r = await new Promise(res => { const q = 's' + Math.random(); const o = window.__tpcResp; window.__tpcResp = (i, x) => { if (i === q) { window.__tpcResp = o; res(x); } else o && o(i, x); }; TPCNative.request(q, 'GET', '/api/v1/states', ''); }); return (JSON.parse(r.body).states.find(s => s.entity_id === id) || {}).state; }, id);

  // ---------------------------------------------------------------- ekran Ogrzewanie (CO) - osobny ekran jak w oryginale
  await goHash('#/d/co');
  check('CO: osobny ekran (nie w jednym koszu z kotłem/CWU)', /Ogrzewanie/i.test(await p.innerText('.hdr, h3, body')));
  await p.getByRole('button', { name: 'Eko', exact: true }).click(); await sleep(3200);
  check('zapis: tryb CO „Eko” (select) dotarł do kotła', (await stateOf('sensor.tekla_co_tryb')) === 'Eko', await stateOf('sensor.tekla_co_tryb'));
  await p.getByRole('button', { name: 'Harmonogram', exact: true }).click(); await sleep(3200);
  check('zapis: tryb CO „Harmonogram” (błąd unknown_entity z telefonu)', (await stateOf('sensor.tekla_co_tryb')) === 'Harmonogram', await stateOf('sensor.tekla_co_tryb') + ' | ' + await p.locator('#toast').innerText());
  await p.screenshot({ path: OUT + '/ui_co.png', fullPage: true });

  // ---------------------------------------------------------------- ekran Ciepła woda (CWU) - osobny ekran
  await goHash('#/d/cwu');
  await p.getByRole('button', { name: 'Eko', exact: true }).click(); await sleep(3200);
  check('zapis: tryb CWU „Eko” (select) dotarł do kotła', (await stateOf('sensor.tekla_cwu_tryb')) === 'Eko', await stateOf('sensor.tekla_cwu_tryb'));
  check('CWU: przycisk „Zagrzej CWU teraz” obecny', (await p.locator('#boost').count()) === 1);
  await p.screenshot({ path: OUT + '/ui_cwu.png', fullPage: true });

  // ---------------------------------------------------------------- poziomy kotła: zablokowane calkowicie niewidoczne, odblokowanie przez Menu
  await goHash('#/d/palnik');
  check('poziomy: przed PIN-em zero śladu (krzywa modulacji i test wyjść nieobecne)', !/Dmuchawa modulacja|tryb testowy/i.test(await p.innerText('body')));
  await goHash('#/d/menu');
  await p.click('#lvl');
  check('poziom: okno PIN kotła', await waitSheet(/Poziom dostępu kotła/));
  await pin('1234');
  check('poziom: zły PIN poziomu odrzucony', await waitSheet(/Zły PIN poziomu/));
  await pin('0900');
  // ensureLevel() odswieza stan (pullNow()) PO zamknieciu okna PIN-u - margines na ten dodatkowy odczyt.
  await noSheet();
  check('poziom: status widoczny tylko w Menu', await waitFor(async () => /poziom 1/i.test(await p.innerText('#lvv'))));
  await goHash('#/d/palnik');
  await sleep(1000);
  check('poziom 1: krzywa modulacji dmuchawy widoczna po PIN 0900', /Dmuchawa modulacja/i.test(await p.innerText('body')));
  check('poziom 1: test wyjść (poziom 2) wciąż niewidoczny', !/tryb testowy/i.test(await p.innerText('body')));
  check('poziom: plakietka odliczania w nagłówku (jedyny sygnał w nagłówku)', /🔓/.test(await txt('#chip')));
  await p.screenshot({ path: OUT + '/ui_palnik_poziom1.png', fullPage: true });
  // Przycisk "Poziom kotła" w Menu zawsze pyta o poziom 1 (ensureLevel(1)) - gdy poziom 1 juz jest aktywny,
  // nic nie robi. Najpierw blokujemy sesje klikiem plakietki w naglowku (jak w oryginale), potem wchodzimy
  // ponownie z PIN-em 0999, zeby dostac poziom 2.
  await p.click('#chip'); await sleep(500);
  check('poziom: klik plakietki blokuje sesję', (await p.locator('#chip').count()) === 0);
  await goHash('#/d/menu');
  await p.click('#lvl');
  check('poziom 2: okno PIN po ponownym zablokowaniu', await waitSheet(/Poziom dostępu kotła/));
  await pin('0999'); await noSheet(); await sleep(1500);
  await goHash('#/d/palnik');
  await sleep(1000);
  // nazwa wyswietlana to nazwa z reads_table ("Podajnik tryb"/"Dmuchawa tryb") - nazwa wlasna z punkty.csv
  // nie jest uzywana przez points_json(); liczy sie to, ze punkt jest teraz zapisywalny (poziom 2).
  check('poziom 2: test wyjść (feeder/blower tryb testowy) widoczny po PIN 0999', /Podajnik tryb/i.test(await p.innerText('body')) && /Dmuchawa tryb/i.test(await p.innerText('body')));
  await p.screenshot({ path: OUT + '/ui_palnik_poziom2.png', fullPage: true });

  // ---------------------------------------------------------------- wygasanie "aktywnosci" po 5 min (bezpiecznik: zdjecie poziomu kotla)
  // Zapis dziala caly czas - to juz nie jest blokada zapisu, tylko automatyczne zdjecie poziomu kotla po bezczynnosci.
  const urlBefore = p.url();
  await p.evaluate(() => { window.__skew = 301000; }); await sleep(1800);
  check('wygasanie: nie przenosi na pulpit (zapis dziala caly czas, bez PIN-u)', p.url() === urlBefore, p.url());
  check('wygasanie: zdjecie poziomu kotla po bezczynnosci (dropLevel)', (await p.evaluate(() => window.__nativeCalls.some(c => c[0] === 'dropLevel'))));
  check('wygasanie: komunikat', /Poziom kotła zablokowany/.test(await p.locator('#toast').innerText()));

  // ---------------------------------------------------------------- menu: oryginalna karta i konfiguracja otwieraja sie bez PIN-u
  await goHash('#/d/menu');
  await p.click('#orig'); await p.click('#cfg'); await sleep(300);
  check('menu: oryginał i konfiguracja otwierają się bez PIN-u', await p.evaluate(() => { const c = window.__nativeCalls.map(x => x[0]); return c.includes('original') && c.includes('settings'); }));

  // ---------------------------------------------------------------- zbiornik paliwa i zasilanie: ogólnie dostępne z Menu (jak w oryginale)
  await goHash('#/d/menu');
  check('menu: pozycja „Zbiornik paliwa”', (await p.locator('#fuel').count()) === 1);
  check('menu: pozycja „Zasilanie i tryby”', (await p.locator('#pwr').count()) === 1);
  const fuel0 = parseFloat(await p.evaluate(async () => { const r = await new Promise(res => { const q='f0'; const o=window.__tpcResp; window.__tpcResp=(i,x)=>{ if(i===q){window.__tpcResp=o;res(x);} else o&&o(i,x); }; TPCNative.request(q,'GET','/api/v1/states',''); }); return (JSON.parse(r.body).states.find(s=>s.entity_id==='sensor.tekla_zbiornik_paliwo')||{}).state; }));
  await p.click('#fuel');
  check('zbiornik: okno z grafiką i edycją ilości', await waitSheet(/Podaj paliwo ręcznie/) && (await p.locator('.sheet svg').count()) >= 1);
  check('zbiornik: pole ilości ma bieżącą wartość', Math.abs(parseFloat(await p.inputValue('#kg')) - fuel0) <= 1);
  await p.screenshot({ path: OUT + '/ui_zbiornik.png' });
  await p.click('[data-d="50"]');
  check('zbiornik: przycisk +50 zmienia ilość', Math.abs(parseFloat(await p.inputValue('#kg')) - (fuel0 + 50)) <= 1);
  await p.fill('#kg', '222');
  await p.click('.sheet #ok'); await sleep(3500);
  await goHash('#/d/pulpit');
  check('zbiornik: zapisana ilość widoczna na pulpicie', parseFloat(await txt('[data-b="pulpit_fuel"]')) === 222, await txt('[data-b="pulpit_fuel"]'));
  await goHash('#/d/menu');
  await p.click('#fuel'); await waitSheet(/Podaj paliwo ręcznie/); await p.click('[data-full]');
  check('zbiornik: „Pełny” ustawia pojemność zbiornika', Math.abs(parseFloat(await p.inputValue('#kg')) - 300) <= 1, await p.inputValue('#kg'));
  await p.click('#feed'); await waitSheet(/Podawanie paliwa/); await p.click('.sheet #yes'); await sleep(1200);
  check('zbiornik: ręczne podawanie paliwa bez błędu', !/Błąd/.test(await p.locator('#toast').innerText()), await p.locator('#toast').innerText());
  await closeAny();

  await goHash('#/d/menu');
  await p.click('#pwr');
  check('zasilanie: panel z włącznikiem kotła i trybami CO/CWU', await waitSheet(/Zasilanie/) && (await p.locator('.sheet .tg').count()) === 1 && (await p.locator('.sheet .chips').count()) === 2);
  await p.click('.sheet .chips button >> text="Komfort" >> nth=0'); await sleep(2500);
  check('zasilanie: zmiana trybu CO z panelu dotarła do kotła', (await stateOf('sensor.tekla_co_tryb')) === 'Komfort', await stateOf('sensor.tekla_co_tryb'));
  await closeAny();

  // ---------------------------------------------------------------- brak połączenia: ostatnie dane
  await goHash('#/d/pulpit');
  await p.evaluate(() => { window.__offline = true; }); await sleep(3500);
  check('offline: baner z godziną ostatnich danych', /Brak połączenia z kotłem.*Pokazuję ostatnie dane z/s.test(await p.innerText('#bn')));
  check('offline: wartości z pamięci zostają', /^\d+\.\d$/.test(await txt('[data-b="pulpit_t_boiler"]')));
  check('offline: plakietka', /offline/.test(await txt('#chip')));
  await p.screenshot({ path: OUT + '/ui_offline.png' });
  await p.evaluate(() => { window.__offline = false; }); await sleep(3500);
  check('offline: powrót do danych na żywo', (await p.locator('#bn .banner').count()) === 0);

  // ---------------------------------------------------------------- harmonogramy (CWU/CO/kocioł)
  await p.click('.nav button[data-k="harmonogram"]'); await sleep(1500);
  check('harmonogram: siedem dni tygodnia z paskami godzin', (await p.locator('.dayrow').count()) === 7 && (await p.locator('.dayrow .hbar i').count()) === 7 * 24);
  check('harmonogram: wszystkie dni mają odczyt (demo ma pełne dane)', !/brak odczytu/.test(await p.innerText('#days')));
  await p.screenshot({ path: OUT + '/ui_harmonogram.png', fullPage: true });
  await p.locator('.dayrow').nth(1).click();
  check('harmonogram: okno edycji godzin', await waitSheet(/Wtorek/) && (await p.locator('.hgrid button').count()) === 24);
  const h12 = p.locator('.hgrid button[data-h="12"]');
  const was12 = await h12.evaluate(n => n.classList.contains('on'));
  await h12.click();
  check('harmonogram: stuknięcie godziny przełącza ją', (await h12.evaluate(n => n.classList.contains('on'))) === !was12);
  await p.click('[data-cp="wk"]');
  await p.click('.sheet #ok'); await sleep(4500);
  const co = await p.evaluate(async () => { const r = await new Promise(res => { const id='h1'; const o=window.__tpcResp; window.__tpcResp=(i,x)=>{ if(i===id){window.__tpcResp=o;res(x);} else o&&o(i,x); }; TPCNative.request(id,'GET','/api/v1/states',''); }); return (JSON.parse(r.body).states.find(s=>s.entity_id==='sensor.tekla_co_harmonogram_rejestry')||{}).state; });
  const days = co.split(' ').map(x => parseInt(x, 16));
  check('harmonogram: zapis dotarł do kotła (godzina 12 przełączona we wtorek)', (((days[1] >> 12) & 1) === 1) === !was12, co);
  check('harmonogram: dni Pn–Pt mają ten sam harmonogram', days.slice(0, 5).every(x => x === days[1]), co);

  // ---------------------------------------------------------------- alarmy
  await p.click('.nav button[data-k="alarmy"]'); await sleep(1200);
  check('alarmy: historia z wpisami', /Przegrzanie|Brak ognia/.test(await p.innerText('#alist')));
  await p.screenshot({ path: OUT + '/ui_alarmy.png' });

  // ---------------------------------------------------------------- ustawienia aplikacji
  // PIN juz nie jest ustawiany w trakcie normalnego uzytkowania (zapis nie wymaga PIN-u) - seedujemy go tu,
  // zeby przetestowac zmiane/usuniecie PIN-u w Ustawieniach (opcjonalna blokada startu apki).
  await nat('setupPin', '2468');
  await goHash('#/app');
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
