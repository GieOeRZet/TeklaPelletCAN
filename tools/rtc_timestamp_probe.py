#!/usr/bin/env python3
"""PASS 62: dynamiczna weryfikacja toru CAN -> PID 0x2165 (Compatibility timestamp) -> auto-sync (0x372F) -> RTC panelu
(statyka: ChatGPT PASS 73-78). Rozruch z modelem RTC (start 2000-11-30 00:00), ustawienie 0x372F (0/1), wstrzykniecie
ramki 0x584 `42 65 21 01 <u32 LE>` przez prawdziwy handler RX (UiSession.inject_param), obserwacja zapisow RTC (TR/DR w trybie INIT).
Uzycie: python3 -I tools/rtc_timestamp_probe.py FW.bin OUT.json [--ts UNIX] [--shots DIR]"""
import argparse, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U

def run(fw, autosync, ts, shots=None, tag=""):
    s = U.UiSession(fw, shots, rtc_start=datetime.datetime(2000, 11, 30, 0, 0, 0)); s.boot(500)
    s.set_local(0x372F, autosync); s.wait(100)
    before = s.rtc.now(); st0 = (s.rtc.start, s.rtc.t0)
    got = s.inject_param(0x2165, ts) if ts is not None else None
    s.wait(1500); after = s.rtc.now(); written = (s.rtc.start, s.rtc.t0) != st0
    if shots: s.shot("rtc_%s_autosync%d" % (tag, autosync))
    return dict(autosync=autosync, ts=ts, storage_0x2165=got, rtc_before=before.isoformat(), rtc_after=after.isoformat(),
                rtc_written=written, rtc_set_to=s.rtc.start.isoformat() if written else None,
                obj_10=s.b.rd(0x20008D1C + 0x10), obj_0c=s.b.rd(0x20008D1C + 0x0C))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("out")
    ap.add_argument("--ts", type=int, default=int(datetime.datetime(2026, 11, 23, 12, 34, 56, tzinfo=datetime.timezone.utc).timestamp()))
    ap.add_argument("--shots"); a = ap.parse_args()
    res = [run(a.bin, 0, a.ts, a.shots, "ts"), run(a.bin, 1, a.ts, a.shots, "ts"), run(a.bin, 1, None, a.shots, "none")]
    for r in res: print(r, flush=True)
    json.dump(res, open(a.out, "w"), indent=1)

if __name__ == "__main__":
    main()
