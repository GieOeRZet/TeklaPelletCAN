// Test karty w prawdziwej przegladarce (Playwright): ladowanie strony urzadzenia, render, klikniecie.
const { chromium } = require('playwright');
(async () => {
  const url = process.argv[2] || 'http://127.0.0.1:8099/index.html';
  const out = process.argv[3] || '/tmp/claude-0/card.png';
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 480, height: 900 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));
  await page.goto(url);
  await page.waitForTimeout(7000);
  const text = await page.evaluate(() => {
    const out = [];
    const walk = n => { if (n.nodeType === 3) out.push(n.textContent.trim()); if (n.shadowRoot) walk(n.shadowRoot); n.childNodes && n.childNodes.forEach(walk); };
    walk(document.body);
    return out.filter(Boolean).join(' | ');
  });
  await page.screenshot({ path: out });
  console.log('TEXT:', text.slice(0, 700));
  console.log('ERRORS:', JSON.stringify(errors.slice(0, 8)));
  await browser.close();
})();
