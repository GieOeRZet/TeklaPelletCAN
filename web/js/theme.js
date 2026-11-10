// Motyw (ciemny/jasny/systemowy) i domyslny styl interfejsu (nowoczesny/klasyczny) - dotyczy TYLKO
// stylu "nowoczesnego" (ten plik), nie karty klasycznej, ktora ma wlasny, stary wyglad. Zapisywane w
// localStorage (per przegladarka/instalacja WebView) - nie wymaga parowania ani sieci.
const THEME_KEY = 'tpc_theme';
const STYLE_KEY = 'tpc_default_style';
const ls = (k, d) => { try { return localStorage.getItem(k) || d; } catch (e) { return d; } };
const setLs = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* ignoruj */ } };

export const getTheme = () => ls(THEME_KEY, 'dark');   // 'dark' | 'light' | 'auto'
export const getDefaultStyle = () => ls(STYLE_KEY, 'modern');   // 'modern' | 'classic'
export const setDefaultStyle = v => setLs(STYLE_KEY, v);

function resolve(theme) {
  if (theme === 'auto') return (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) ? 'light' : 'dark';
  return theme === 'light' ? 'light' : 'dark';
}
function apply(theme) {
  document.documentElement.setAttribute('data-theme', resolve(theme));
}
export function setTheme(theme) { setLs(THEME_KEY, theme); apply(theme); }

// Zmiana motywu systemowego "w locie" dziala tylko gdy wybrano "systemowy".
if (window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => { if (getTheme() === 'auto') apply('auto'); });
}
apply(getTheme());
