"""Responder mDNS sprawdzany prawdziwym parserem pakietów (biblioteka zeroconf, ta sama, której używa Home Assistant)."""
import os
import subprocess
from pathlib import Path

import pytest
from zeroconf import DNSIncoming, DNSOutgoing, DNSQuestion, const

ROOT = Path(__file__).resolve().parent.parent
TOOL = Path(os.environ.get("MDNS_TOOL", ROOT / "build-host" / "mdns_tool"))
SERVICE = "_teklapelletcan._tcp.local."
INSTANCE = "TeklaPelletCAN A1B2C3." + SERVICE


@pytest.fixture(autouse=True)
def _need_tool():
    if not TOOL.exists():
        pytest.skip(f"brak {TOOL}")


def _ask(*questions, announce=False):
    out = DNSOutgoing(const._FLAGS_QR_QUERY, multicast=True)
    for name, qtype in questions:
        out.add_question(DNSQuestion(name, qtype, const._CLASS_IN))
    pkt = b"".join(out.packets())
    args = [str(TOOL)] + (["announce"] if announce else [])
    res = subprocess.run(args, input=pkt.hex() + "\n", capture_output=True, text=True, check=True).stdout.strip()
    return DNSIncoming(bytes.fromhex(res)) if res else None


def test_ptr_query_returns_service_srv_txt_and_address():
    r = _ask((SERVICE, const._TYPE_PTR))
    assert r is not None and r.is_response()
    recs = {(x.name, x.type): x for x in r.answers()}
    assert recs[(SERVICE, const._TYPE_PTR)].alias == INSTANCE
    srv = recs[(INSTANCE, const._TYPE_SRV)]
    assert srv.port == 80 and srv.server == "teklapelletcan-a1b2c3.local."
    txt = recs[(INSTANCE, const._TYPE_TXT)]
    assert b"id=A1B2C3D4E5F6" in txt.text and b"api=1" in txt.text
    a = recs[("teklapelletcan-a1b2c3.local.", const._TYPE_A)]
    assert a.address == bytes([192, 168, 10, 250])


def test_a_query_for_host():
    r = _ask(("teklapelletcan-a1b2c3.local.", const._TYPE_A))
    assert r is not None
    assert [x.address for x in r.answers() if x.type == const._TYPE_A] == [bytes([192, 168, 10, 250])]


def test_meta_query_lists_service_type():
    r = _ask(("_services._dns-sd._udp.local.", const._TYPE_PTR))
    assert r is not None and any(x.alias == SERVICE for x in r.answers())


def test_unrelated_query_gets_no_answer():
    assert _ask(("inne-urzadzenie.local.", const._TYPE_A)) is None
    assert _ask(("_http._tcp.local.", const._TYPE_PTR)) is None


def test_announcement_is_valid_response():
    r = _ask(announce=True) if False else None
    out = subprocess.run([str(TOOL), "announce"], input="\n", capture_output=True, text=True, check=True).stdout.strip()
    r = DNSIncoming(bytes.fromhex(out))
    assert r.is_response() and len(r.answers()) == 4
