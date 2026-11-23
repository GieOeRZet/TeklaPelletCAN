# PASS 56 — czcionki TouchGFX wyeksportowane i zweryfikowane (A1 planu 1:1)
## Wynik (HARD)
- **6 czcionek** (GeneratedFont, 4 bpp), fabryki: 6 wywolan konstruktora `0x0805B75C` (`0x080517E8..0x0805190E`). Wysokosci: **12, 20, 26, 36, 64, 92 px**; glify: 76, 152, 127, 95, 19, 19 (cyfry/znaki dla duzych). Zakres Unicode 0x02..0x21B (lacinica rozszerzona: PL, CZ, SK, LT, RO, EST, ES).
- Listy glifow (14 B/wezel: dataOffset u32, unicode u16, width, height, top, left, advance, 0xFF, kerning u16) pod `0x0806F030, 0x08068218, 0x0806DCD0, 0x0806EAFC, 0x08074730, 0x0807483C`; **dane glifow** pod `0x0806D598, 0x08037978, 0x080319B4, 0x08029490, 0x08039E20, 0x0802D90C` — to blok, ktory narzedzie pokrycia widzialo jako "niewykonany kod" `0x802C000..0x8038000`: **to dane czcionek, nie biblioteka/kod**.
- Format pikseli: 4 bpp alfa, **nibble niski pierwszy**, upakowanie ciagle bez wyrownania wierszy (potwierdzone statystyka rozmiarow i wizualnie).
- **TypedText -> czcionka/wyrownanie**: tablica `0x08071958` (496 wpisow x 2 B: font_index, wyrownanie 0=lewo 1=srodek 2=prawo) -> `data/typedtext_database.csv` (id, font, flagi, tekst PL). Uzycie: font 2 (26 px) 265 tekstow, font 1 (20 px) 184, font 3 (36 px) 26, font 0 (12 px) 15, font 4 (64 px) 4, font 5 (92 px) 2.
- **Weryfikacja renderera**: `tools/render_text.py` (uklad advance/left/top, baseline = wysokosc − pixBelowBase, bez kerningu) dla "Ochrona kotla" (font 2) vs zrzut z emulatora: **korelacja 0.982**.
## Pliki
`data/fonts/font{0..5}_h{12,20,26,36,64,92}/{atlas.png,glyphs.csv,glyph_data_4bpp.bin}`, `data/fonts/fonts.json`, `data/fonts_glyph_pngs.zip` (PNG kazdego glifu), `data/typedtext_database.csv`. Narzedzia: `tools/export_fonts.py`, `tools/render_text.py`.
## Otwarte
Kerning (pole +12 wezla / tablica `[sp+0x14]`), czcionki innych skryptow (tylko lacinica), pixBelowBase/baseline dla wszystkich rozmiarow potwierdzic na wiecej tekstow.
