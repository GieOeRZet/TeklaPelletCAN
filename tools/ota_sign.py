#!/usr/bin/env python3
"""Podpisywanie firmware do aktualizacji OTA (ECDSA P-256 nad SHA-256 obrazu).

  init   --out klucz.pem                 nowa para kluczy (prywatny trzymaj w sekrecie: sekret OTA_SIGNING_KEY w GitHub)
  pubkey --key klucz.pem [--dev]         zapisuje klucz publiczny do firmware (ota_pubkey.cpp)
  sign   --key klucz.pem --bin plik.bin  wypisuje podpis (128 znakow hex, r||s) i zapisuje plik.bin.sig
  verify --key klucz.pem --bin plik.bin --sig HEX
  package --key klucz.pem --bin plik.bin --out pakiet.bin   plik z podpisem WBUDOWANYM (obraz + "TPCSIG01" + podpis 64 B):
                                                            do aktualizacji z przegladarki nie trzeba osobnego pliku .sig
"""
import argparse, hashlib, os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature, Prehashed

ROOT = Path(__file__).resolve().parent.parent
TRAILER_MAGIC = b"TPCSIG01"
PUBKEY_CPP = ROOT / "firmware/components/core/ota_pubkey.cpp"


def load(path):
    return serialization.load_pem_private_key(Path(path).read_bytes(), password=None)


def sign_image(key, data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    der = key.sign(digest, ec.ECDSA(Prehashed(hashes.SHA256())))
    r, s = decode_dss_signature(der)
    return (r.to_bytes(32, "big") + s.to_bytes(32, "big")).hex()


def verify_image(pub, data: bytes, sig_hex: str) -> None:
    sig = bytes.fromhex(sig_hex)
    der = encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big"))
    pub.verify(der, hashlib.sha256(data).digest(), ec.ECDSA(Prehashed(hashes.SHA256())))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("init"); s.add_argument("--out", required=True)
    s = sp.add_parser("pubkey"); s.add_argument("--key", required=True); s.add_argument("--dev", action="store_true")
    s = sp.add_parser("sign"); s.add_argument("--key", required=True); s.add_argument("--bin", required=True)
    s = sp.add_parser("package"); s.add_argument("--key", required=True); s.add_argument("--bin", required=True); s.add_argument("--out", required=True)
    s = sp.add_parser("verify"); s.add_argument("--key", required=True); s.add_argument("--bin", required=True); s.add_argument("--sig", required=True)
    a = p.parse_args()
    if a.cmd == "init":
        key = ec.generate_private_key(ec.SECP256R1())
        out = Path(a.out)
        out.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        os.chmod(out, 0o600)
        print(f"zapisano {out} – NIE commituj; dodaj jako sekret OTA_SIGNING_KEY")
    elif a.cmd == "pubkey":
        pub = load(a.key).public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        PUBKEY_CPP.write_text(
            "// PLIK WYGENEROWANY przez tools/ota_sign.py pubkey – nie edytuj recznie.\n"
            '#include "ota.h"\n\nnamespace tpc {\n\n'
            f"const uint8_t kOtaPubKey[65] = {{{','.join(f'0x{b:02X}' for b in pub)}}};\n"
            f"const bool kOtaDevKey = {'true' if a.dev else 'false'};\n\n}}  // namespace tpc\n", encoding="utf-8")
        print(f"zapisano {PUBKEY_CPP} ({'KLUCZ TESTOWY' if a.dev else 'produkcyjny'})")
    elif a.cmd == "package":
        data = Path(a.bin).read_bytes()
        if data.endswith(b"") and TRAILER_MAGIC in data[-72:-64]:
            data = data[:-72]                      # nie dubluj trailera
        sig = bytes.fromhex(sign_image(load(a.key), data))
        Path(a.out).write_bytes(data + TRAILER_MAGIC + sig)
        print(f"zapisano {a.out}: {len(data)} B obrazu + 72 B podpisu")
    elif a.cmd == "sign":
        data = Path(a.bin).read_bytes()
        sig = sign_image(load(a.key), data)
        Path(a.bin + ".sig").write_text(sig + "\n")
        print(sig)
    else:
        verify_image(load(a.key).public_key(), Path(a.bin).read_bytes(), a.sig)
        print("podpis poprawny")


if __name__ == "__main__":
    main()
