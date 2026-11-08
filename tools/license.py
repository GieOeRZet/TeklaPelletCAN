#!/usr/bin/env python3
"""Generator kodow odblokowujacych TeklaPelletCAN (podpis ECDSA P-256).

Format kodu:  TPC1-<base32 z (payload 11 B || podpis 64 B)> w grupach po 6 znakow.
payload = 0x54 'T' | wersja(1) | poziom(1: 1 = pelna) | id urzadzenia (6 B, same zera = dowolne) | numer seryjny (u16 BE)
podpis  = ECDSA P-256 (r||s, 64 B) z SHA-256("TPC-LIC1" || payload)

Polecenia:
  init    --out klucz.pem                       nowa para kluczy (klucz prywatny trzymaj w sekrecie!)
  pubkey  --key klucz.pem [--dev]               zapisuje klucz publiczny do firmware (license_pubkey.cpp)
  issue   --key klucz.pem --device ID|any [--tier full] [--serial N]   wypisuje kod
  verify  --key klucz.pem --code KOD [--device ID]                    sprawdza kod
"""
import argparse, base64, hashlib, os, sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature

ROOT = Path(__file__).resolve().parent.parent
PUBKEY_CPP = ROOT / "firmware/components/core/license_pubkey.cpp"
DOMAIN = b"TPC-LIC1"
TIERS = {"full": 1}


def load_key(path):
    return serialization.load_pem_private_key(Path(path).read_bytes(), password=None)


def parse_device(s):
    if s.lower() == "any":
        return bytes(6)
    s = s.replace(":", "").replace("-", "").strip()
    if len(s) != 12:
        raise SystemExit("ID urzadzenia: 12 znakow hex (np. A1B2C3D4E5F6) albo 'any'")
    return bytes.fromhex(s)


def make_code(key, tier, device, serial):
    payload = bytes([0x54, 1, TIERS[tier]]) + device + serial.to_bytes(2, "big")
    der = key.sign(DOMAIN + payload, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    b32 = base64.b32encode(payload + sig).decode().rstrip("=")
    groups = [b32[i:i + 6] for i in range(0, len(b32), 6)]
    return "TPC1-" + "-".join(groups)


def parse_code(code):
    c = code.strip().upper().replace(" ", "").replace("-", "")
    if not c.startswith("TPC1"):
        raise ValueError("zly prefiks")
    c = c[4:]
    raw = base64.b32decode(c + "=" * (-len(c) % 8))
    if len(raw) != 75:
        raise ValueError("zla dlugosc")
    return raw[:11], raw[11:]


def verify_code(pub, code, device=None):
    payload, sig = parse_code(code)
    if payload[0] != 0x54 or payload[1] != 1:
        raise ValueError("zly naglowek")
    der = encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big"))
    pub.verify(der, DOMAIN + payload, ec.ECDSA(hashes.SHA256()))  # wyjatek gdy zly
    bound = payload[3:9]
    if any(bound) and device is not None and bound != device:
        raise ValueError("kod dla innego urzadzenia")
    return {"tier": payload[2], "device": bound.hex().upper() or "any", "serial": int.from_bytes(payload[9:11], "big")}


def cmd_init(a):
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    out = Path(a.out)
    out.write_bytes(pem)
    os.chmod(out, 0o600)
    print(f"zapisano klucz prywatny: {out}\nNIE commituj go do repozytorium. Dodaj jako sekret LICENSE_SIGNING_KEY w GitHub (Settings > Secrets).")


def cmd_pubkey(a):
    pub = load_key(a.key).public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    body = ",".join(f"0x{b:02X}" for b in pub)
    PUBKEY_CPP.write_text(
        "// PLIK WYGENEROWANY przez tools/license.py pubkey – nie edytuj recznie.\n"
        '#include "license.h"\n\nnamespace tpc {\n\n'
        f"const uint8_t kLicensePubKey[65] = {{{body}}};\n"
        f"const bool kLicenseDevKey = {'true' if a.dev else 'false'};\n\n}}  // namespace tpc\n",
        encoding="utf-8")
    print(f"zapisano {PUBKEY_CPP} ({'KLUCZ TESTOWY' if a.dev else 'klucz produkcyjny'})")


def cmd_issue(a):
    print(make_code(load_key(a.key), a.tier, parse_device(a.device), a.serial))


def cmd_verify(a):
    dev = parse_device(a.device) if a.device else None
    print(verify_code(load_key(a.key).public_key(), a.code, dev))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("init"); s.add_argument("--out", required=True); s.set_defaults(f=cmd_init)
    s = sp.add_parser("pubkey"); s.add_argument("--key", required=True); s.add_argument("--dev", action="store_true"); s.set_defaults(f=cmd_pubkey)
    s = sp.add_parser("issue"); s.add_argument("--key", required=True); s.add_argument("--device", required=True)
    s.add_argument("--tier", default="full", choices=list(TIERS)); s.add_argument("--serial", type=int, default=0); s.set_defaults(f=cmd_issue)
    s = sp.add_parser("verify"); s.add_argument("--key", required=True); s.add_argument("--code", required=True); s.add_argument("--device"); s.set_defaults(f=cmd_verify)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
