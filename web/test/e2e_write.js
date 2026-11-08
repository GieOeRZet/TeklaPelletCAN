// Pelny obieg zapisu z karty: parowanie (okno hasla), PIN, zmiana nastawy -> sprawdzenie w API urzadzenia.
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8100';
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 480, height: 330 } });
  const dialogs = [];
  p.on('dialog', async d => { dialogs.push(d.message()); await d.accept('qwerty123'); });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(BASE + '/index.html?screen=main'); await p.waitForTimeout(4000);
  // wywolanie uslugi tak, jak robi to karta (przez hass.callService zbudowany przez shim)
  const res = await p.evaluate(async () => {
    const card = document.querySelector('pelletcan-card');
    const h = card._hass;
    const out = {};
    out.unlock = await h.callService('teklapelletcan', 'tekla_estyma_unlock', { pin: 900 });
    out.setpoint = await h.callService('teklapelletcan', 'tekla_estyma_set_setpoint', { which: 4, value: 72 });
    try { await h.callService('teklapelletcan', 'tekla_estyma_set_setpoint', { which: 4, value: 99 }); out.range = 'brak bledu'; }
    catch (e) { out.range = e.message; }
    out.token = !!h.token;
    return out;
  });
  await p.waitForTimeout(2500);
  const st = await (await fetch(BASE + '/api/v1/states')).json();
  const sp = st.states.find(x => x.entity_id === 'sensor.tekla_kociol_zadana_reczna');
  console.log('DIALOGS', JSON.stringify(dialogs));
  console.log('RESULT', JSON.stringify(res));
  console.log('ZADANA_RECZNA_W_URZADZENIU', sp.state, '| poziom', st.level);
  console.log('PAGEERRORS', JSON.stringify(errs));
  await b.close();
})();
