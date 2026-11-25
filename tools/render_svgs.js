// Renderuje liste SVG (jobs.json: {svg,w,h,out}) do PNG 1x z przezroczystoscia w Chromium (playwright). Uzycie: node tools/render_svgs.js jobs.json
const { chromium } = require('playwright');
const jobs = require(require('path').resolve(process.argv[2]));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const j of jobs) {
    await p.setViewportSize({ width: j.w, height: j.h });
    await p.goto('file://' + j.svg);   // SVG otwierany bezposrednio (img z about:blank nie ladowal plikow file://)
    await p.screenshot({ path: j.out, omitBackground: true, clip: { x: 0, y: 0, width: j.w, height: j.h } });
  }
  await b.close();
})();
