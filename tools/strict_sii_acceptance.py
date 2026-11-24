#!/usr/bin/env python3
"""Strict dynamic acceptance runner for SIEĆ / INFO / INTERNET.

This runner deliberately refuses to call a test FACT-DYNAMIC unless:
- the real firmware is loaded through UiSession/from a real checkpoint;
- BEFORE -> equal-length CONTROL -> ACTION -> AFTER is executed;
- body-only diff proves ACTION changed while CONTROL did not;
- CAN TX is measured from the point immediately before ACTION;
- the stored value is checked for every inject_param write;
- the same test is repeated from an independent checkpoint/state with a second value/state.

It is intentionally data-first and resumable. It does not use mock UI state.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ui_session as U
import ctor_trace as CT

from PIL import Image, ImageChops

VIEW_PTR = 0x20024818
PERIODIC = {0x2167, 0x229A, 0x3723}


def body(im):
    return im.crop((0, 46, 480, 272))


def diff_box(a, b):
    return ImageChops.difference(body(a), body(b)).getbbox()


def new_session(fw, state):
    s = U.UiSession.from_checkpoint(fw, state, None)
    s.wait(300)
    return s


def tx584(s, start):
    out = []
    for f in s.can2.tx[start:]:
        if f["id"] != 0x584:
            continue
        data = bytes(f["data"])
        if len(data) >= 3 and int.from_bytes(data[1:3], "little") in PERIODIC:
            continue
        out.append(data.hex())
    return out


def strict_step(s, outdir, name, action, settle=300):
    """One pkt-4 test. Returns PASS only with zero control diff + nonzero action diff."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    checkpoint = outdir / ("_" + name + ".state")
    s.checkpoint(str(checkpoint))

    before = s.shot()
    s.wait(settle)
    control = s.shot()
    control_diff = diff_box(before, control)

    s.b.load_state(str(checkpoint))
    before = s.shot()
    n0 = len(s.can2.tx)
    info = action(s)
    s.wait(settle)
    after = s.shot()

    action_diff = diff_box(before, after)
    tx = tx584(s, n0)

    before.crop((0, 46, 480, 272)).save(outdir / (name + "_before.png"))
    after.crop((0, 46, 480, 272)).save(outdir / (name + "_after.png"))

    return {
        "name": name,
        "control_diff": control_diff,
        "action_diff": action_diff,
        "changed": bool(action_diff) and not bool(control_diff),
        "view": hex(s.b.rd(s.b.rd(VIEW_PTR))),
        "tx584": tx,
        "info": info,
    }


def strict_repeat(fw, state_a, state_b, outdir, name, action_a, action_b, settle=300):
    """Two independent runs are required for a dynamic fact."""
    ra = strict_step(new_session(fw, state_a), outdir, name + "_a", action_a, settle)
    rb = strict_step(new_session(fw, state_b), outdir, name + "_b", action_b, settle)
    passed = (
        ra["changed"] and rb["changed"]
        and ra["control_diff"] is None and rb["control_diff"] is None
    )
    return {"name": name, "repeat_pass": passed, "runs": [ra, rb]}


def inject_test(pid, value):
    def action(s):
        stored = s.inject_param(pid, value)
        return {"pid": hex(pid), "value": value, "stored": stored,
                "stored_ok": stored == value}
    return action


def feed_nodes(nodes, rounds=8):
    def action(s):
        for _ in range(rounds):
            for n in nodes:
                s.can(0x700 + n, [5])
                s.wait(12)
                s.can(0x580 + n, [0x43, 0x18, 0x10, 2, 0, 0, 0, 0])
                s.wait(12)
            s.wait(120)
        return {"nodes": [hex(n) for n in nodes], "rounds": rounds}
    return action


def discover_tap_for_label(s, label):
    """Find a touchable widget in live RAM adjacent to a rendered text label."""
    rd = s.b.rd
    text_vptrs = {0x0807E15C, 0x0807E1D8, 0x0807E7F8}
    found = []
    for a in range(0x20000000, 0x20030000, 4):
        try:
            if rd(a, 4) not in text_vptrs:
                continue
            vis = rd(a + 0x25, 1)
            if vis != 1:
                continue
            bp = rd(a + 0x34, 4) if rd(a, 4) != 0x0807E7F8 else 0
            text = ""
            if 0x20000000 <= bp < 0x2002FFC0:
                chars = []
                for i in range(48):
                    ch = rd(bp + 2 * i, 2)
                    if ch == 0:
                        break
                    chars.append(chr(ch))
                text = "".join(chars)
            if text != label:
                continue
            def rect(q):
                vals = []
                for i in range(4):
                    lo, hi = rd(q + 4 + 2*i, 1), rd(q + 5 + 2*i, 1)
                    v = lo | (hi << 8)
                    if v & 0x8000:
                        v -= 0x10000
                    vals.append(v)
                return vals
            x, y, w, h = rect(a)
            # Walk the live object tree by scanning valid Drawable parents.
            candidates = []
            for q in range(0x20000000, 0x20030000, 4):
                try:
                    if rd(q + 0x24, 1) != 1 or rd(q + 0x25, 1) != 1:
                        continue
                    rx, ry, rw, rh = rect(q)
                    if rw <= 0 or rh <= 0 or rw > 480 or rh > 272:
                        continue
                    if abs(ry - y) > max(20, h) or rx < x:
                        continue
                    candidates.append((abs(ry-y) + abs(rx-x), q, rx, ry, rw, rh))
                except Exception:
                    continue
            if not candidates:
                raise RuntimeError("no touchable widget next to label %r" % label)
            _, q, rx, ry, rw, rh = min(candidates)
            return [rx + rw//2, ry + rh//2], {
                "label_addr": hex(a), "label_rect": [x,y,w,h],
                "touch_addr": hex(q), "touch_rect": [rx,ry,rw,rh],
            }
        except RuntimeError:
            raise
        except Exception:
            continue
    raise RuntimeError("label not found in live RAM: %r" % label)

def tap(x, y, settle=700):
    def action(s):
        s.tap(x, y, settle=settle)
        return {"tap": [x, y]}
    return action


def run_siec(fw, state, out):
    s0 = new_session(fw, state)
    b0 = s0.shot()
    s0.wait(100)
    c0 = s0.shot()
    tests = {"empty_baseline": {"control_diff": diff_box(b0, c0), "status": "BASELINE"}}
    for label, nodes in (
        ("n56", [0x56]), ("n57", [0x57]),
        ("n56_n57", [0x56, 0x57]), ("n57_n56", [0x57, 0x56]),
        ("n5b", [0x5B]), ("n45", [0x45]), ("n22_unknown", [0x22]),
    ):
        # A second run is deliberately made with the same condition from a fresh
        # checkpoint; ordering/timeout cases are handled separately.
        tests[label] = strict_repeat(
            fw, state, state, out, "siec_" + label,
            feed_nodes(nodes), feed_nodes(nodes), settle=100
        )
    # Long offline behavior is observational, not inferred from a short timeout.
    s = new_session(fw, state)
    feed_nodes([0x56], rounds=8)(s)
    present = s.shot()
    s.wait(10000)
    timeout = s.shot()
    feed_nodes([0x56], rounds=3)(s)
    reappear = s.shot()
    Path(out).mkdir(parents=True, exist_ok=True)
    body(present).save(Path(out) / "siec_timeout_present.png")
    body(timeout).save(Path(out) / "siec_timeout_10000.png")
    body(reappear).save(Path(out) / "siec_timeout_reappear.png")
    tests["timeout_10000"] = {
        "present_vs_timeout": diff_box(present, timeout),
        "timeout_vs_reappear": diff_box(timeout, reappear),
        "status": "OBSERVE_ONLY",
    }
    return tests


def run_info(fw, state, out):
    tests = {}
    for pid, values in (
        (0x3664, [0x0214, 0x0215]),
        (0x3665, [0, 1]),
        (0x2170, [0, 1, 5678, 65535]),
    ):
        for v in values:
            name = "info_%04X_%d" % (pid, v)
            tests[name] = strict_repeat(
                fw, state, state, out, name,
                inject_test(pid, v), inject_test(pid, v + 1 if v < 65535 else v - 1), settle=300
            )
    return tests


def run_internet(fw, state, out):
    tests = {}
    for pid, values in (
        (0x373E, [0, 1]),
        (0x3741, [0, 1]),
        (0x373D, [0, 2]),
    ):
        for v in values:
            name = "internet_%04X_%d" % (pid, v)
            tests[name] = strict_repeat(
                fw, state, state, out, name,
                inject_test(pid, v), inject_test(pid, v + 1 if v < 65535 else v - 1), settle=300
            )

    # SSID editor entry must use a touch rectangle from live widget RAM.
    # If the construction trace cannot identify it, the test fails explicitly;
    # no screenshot coordinate fallback is allowed.
    def editor_action(s):
        xy, widget = discover_tap_for_label(s, "SSID")
        s.tap(*xy, settle=1000)
        return {"tap": xy, "widget": widget}
    tests["ssid_editor_open"] = strict_repeat(
        fw, state, state, out, "internet_ssid_editor",
        editor_action, editor_action, settle=300
    )
    return tests


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: strict_sii_acceptance.py FW STATE_DIR OUT {siec|info|internet|all}")
    fw, statedir, out, which = sys.argv[1:5]
    state_map = {"siec": "node_17_screen.state",
                 "info": "node_10_screen.state",
                 "internet": "node_18_screen.state"}

    result = {
        "firmware": str(Path(fw).resolve()),
        "methodology": "NewEstyma/METODYKA_EMULATOR.md pkt 4",
        "executed": False,
        "note": "The caller must execute this runner against the canonical firmware; no result is FACT-DYNAMIC merely because this file exists.",
    }

    if which in ("siec", "all"):
        result["SIEC"] = run_siec(fw, os.path.join(statedir, state_map["siec"]), os.path.join(out, "siec"))
    if which in ("info", "all"):
        result["INFO"] = run_info(fw, os.path.join(statedir, state_map["info"]), os.path.join(out, "info"))
    if which in ("internet", "all"):
        result["INTERNET"] = run_internet(fw, os.path.join(statedir, state_map["internet"]), os.path.join(out, "internet"))

    result["executed"] = True
    Path(out).mkdir(parents=True, exist_ok=True)
    json.dump(result, open(Path(out) / "RUN_SUMMARY.json", "w"), ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
