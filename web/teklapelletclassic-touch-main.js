// teklapelletclassic-touch-main.js
// Produkcyjna warstwa wygladu ekranu HOME/PULPIT.
// Nie tworzy drugiego silnika: zachowuje caly mechanizm TeklaPanelCard
// (data-act/data-go, HA services, odczyt stanow, alarmy, modalne okna).
// Zmienia tylko warstwe wizualna na bitmapy wyciagniete 1:1 z FW2213TK.
//
// Zasada:
//   oryginalny _main() -> zachowujemy cala semantyke i obsluge dotyku
//   -> podmieniamy tylko grafiki SVG na zasoby panelu 77/144/174/115
//   -> zasobnik korzysta z 051/052/053
//   -> przy braku tekstur wracamy do oryginalnego HTML.
//
// Bitmapy sa ladowane z tego samego katalogu img/panel/ co karta.
// Nie ma zadnych nowych encji ani nowych uslug.

(async () => {
  try {
    await customElements.whenDefined('tekla-panel-card');
    const C = customElements.get('tekla-panel-card');
    if (!C || C.prototype.__touchMainOriginal) return;

    const DIR = new URL('./img/panel/', import.meta.url).href;
    const stamp = Date.now();
    const U = n => DIR + String(n).padStart(3, '0') + '.png?v=' + stamp;

    const NEED = [51, 52, 53, 77, 115, 144, 174];
    const loaded = new Map();

    const probe = n => new Promise(resolve => {
      const im = new Image();
      im.onload = () => { loaded.set(n, true); resolve(true); };
      im.onerror = () => { loaded.set(n, false); resolve(false); };
      im.src = U(n);
    });

    const ok = await Promise.all(NEED.map(probe));
    // Jesli pakiet grafik nie jest dostepny, nie psujemy karty.
    if (!ok.every(Boolean)) {
      console.warn('TeklaPelletClassic: pakiet bitmap Home nie jest kompletny; pozostaje bazowy renderer.');
      return;
    }

    const img = (n, cls, extra = '') =>
      '<img class="' + (cls || '') + '" src="' + U(n) +
      '" draggable="false" aria-hidden="true" style="' + extra + '">';

    // Zachowujemy semantyczny _main bazowego silnika.
    const baseMain = C.prototype._main;

    // Bitmapowy zasobnik: zgodnie z zamknieta analiza BIN:
    // 051 = niski zasobnik, 052 = stan normalny/pelny, 053 = rezerwa/E.
    const baseHopper = C.prototype._hopper;
    C.prototype._hopper = function () {
      const pct = this._fuelPct();
      const n = pct <= 0 ? 53 : pct < 0.15 ? 51 : 52;
      return img(n, 'tpc-hopper', 'width:100%;height:100%;display:block;object-fit:fill;');
    };

    C.prototype._main = function (ctx) {
      let h = baseMain.call(this, ctx);

      // MENU 77
      h = h.replace(
        /<svg viewBox="0 0 35 30\.2" class="ic mic">[\\s\\S]*?<\/svg>/,
        img(77, 'ic mic', 'object-fit:contain;')
      );

      // CO1 144
      h = h.replace(
        /<span class="radi"><svg[^>]*class="ic2"[^>]*>[\\s\\S]*?<\/svg><sup>1<\/sup><\/span>/,
        '<span class="radi">' + img(144, 'ic2', 'object-fit:contain;') + '<sup>1</sup></span>'
      );

      // CWU 174
      h = h.replace(
        /(<div class="cell" data-go="water">(?:<i class="ind[^>]*><\/i>)?)<svg[^>]*class="ic2"[^>]*>[\\s\\S]*?<\/svg>/,
        '$1' + img(174, 'ic2', 'object-fit:contain;')
      );

      // Zasilanie / quick 115
      h = h.replace(
        /(<div class="cell" data-act="quick">(?:<i class="ind[^>]*><\/i>)?)<svg[^>]*class="ic2"[^>]*>[\\s\\S]*?<\/svg>/,
        '$1' + img(115, 'ic2', 'object-fit:contain;')
      );

      return h;
    };

    const oldCss = C.prototype._css;
    C.prototype._css = function () {
      return oldCss.call(this) + `
        /* --- Touch Home: prawdziwe bitmapy panelu --- */
        .s-main .cell > img.ic,
        .s-main .cell > img.ic2 {
          position:absolute !important;
          display:block !important;
          margin:0 !important;
          transform:translateX(-50%) !important;
        }
        .s-main .cell:first-child > img.mic {
          width:5.9cqw !important;
          height:5.08cqw !important;
          left:50% !important;
          top:6.0cqw !important;
        }
        .s-main .cell[data-go="heat"] > .radi {
          top:5.47cqw !important;
          left:calc(50% - .56cqw) !important;
          display:block !important;
        }
        .s-main .cell[data-go="heat"] .radi img.ic2 {
          width:5.02cqw !important;
          height:6.14cqw !important;
          left:50% !important;
          top:0 !important;
        }
        .s-main .cell[data-go="heat"] .radi sup {
          right:auto !important;
          left:calc(100% + .9cqw) !important;
          top:-.1cqw !important;
        }
        .s-main .cell[data-go="water"] > img.ic2 {
          width:6.83cqw !important;
          height:7.32cqw !important;
          left:calc(50% + .16cqw) !important;
          top:4.88cqw !important;
        }
        .s-main .cell[data-act="quick"] > img.ic2 {
          width:7.59cqw !important;
          height:7.41cqw !important;
          left:calc(50% + .24cqw) !important;
          top:4.88cqw !important;
        }
        .s-main .cell[data-act="fuel"] > img.tpc-hopper {
          position:absolute !important;
          left:50% !important;
          top:6.75cqw !important;
          width:6.66cqw !important;
          height:5.52cqw !important;
          transform:translateX(-50%) !important;
        }
        .s-main .cell[data-act="fuel"] small.fl {
          z-index:2;
        }
      `;
    };

    C.prototype.__touchMainOriginal = true;
    window.dispatchEvent(new Event('tekla-img'));
  } catch (e) {
    console.error('teklapelletclassic-touch-main:', e);
  }
})();
