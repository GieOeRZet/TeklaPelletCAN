"""Wspolna nawigacja po MENU: tap_incremental(session, nav, i) - stuka wiersz i (cy = 29 + 50 i) przewijajac po 60 px i sumujac przesuniecia miedzy zrzutami
(ListNav.build/tap_row_from_top bywaja zawodne, gdy zszyty obraz jest niepelny)."""
def tap_incremental(s, nav, i):
    cy = 29 + 50 * i; off = 0; prev = s.shot()
    for _ in range(40):
        y = nav.BODY0 + cy - off
        if 70 <= y <= 250: s.tap(240, y, settle=800); return True
        if not s.drag_until_change(240, 235, 240, 175, attempts=4, ticks=240, pause_end=160): return False
        cur = s.shot(); err, d = nav._shift(prev, cur)
        if d == 0: return False
        off += d; prev = cur
    return False

def tap_tail(s, nav, i, n_total):
    """ogon MENU: przewin do konca (dragi 200->80 do braku zmiany), stuknij od dolu (ostatni wiersz y=227, pitch 50); zwraca True gdy widok sie zmienil"""
    for _ in range(40):
        if not s.drag_until_change(240, 200, 240, 80, attempts=6, ticks=240, pause_end=160): break
    s.wait(900); y = 227 - 50 * (n_total - 1 - i)
    if not (60 <= y <= 250): return False
    s.tap(240, y, settle=800); s.wait(300); return hex(s.b.rd(s.b.rd(0x20024818))) != "0x808f66c"
