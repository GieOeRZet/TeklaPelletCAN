const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const errs = [];
  for (const scr of ['burn', 'heat', 'water', 'menu', 'alarm', 'info']) {
    const p = await b.newPage({ viewport: { width: 480, height: 330 } });
    p.on('pageerror', e => errs.push(scr + ': ' + e.message));
    await p.goto('http://127.0.0.1:8099/classic.html?screen=' + scr);
    await p.waitForTimeout(5000);
    await p.screenshot({ path: `/tmp/claude-0/scr_${scr}.png` });
    await p.close();
  }
  const r = await fetch('http://127.0.0.1:8099/api/v1/calls'); const calls = await r.json();
  console.log('PAGEERRORS', JSON.stringify(errs));
  console.log('CALLS', JSON.stringify([...new Set(calls.map(c => c.domain + '.' + c.service))]));
  await b.close();
})();
