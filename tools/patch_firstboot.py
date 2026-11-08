#!/usr/bin/env python3
"""Wpisuje dane pierwszego uruchomienia (Wi-Fi, stały IP, haslo urzadzenia) do pliku firmware .bin – LOKALNIE.

Po zdalnym wgraniu (OTA z ESPHome) nowy firmware nie ma jak poznac Twojej sieci, a nie masz fizycznego dostepu do
urzadzenia. Ten skrypt wpisuje dane w pole `g_firstboot` obrazu i przelicza sume kontrolna oraz skrot SHA-256, zeby
bootloader zaakceptowal plik. Dane zostaja tylko w Twoim pliku (nie trafiaja do repozytorium ani do CI).

Przyklad (stale IP jak w dotychczasowym ESPHome):
  python3 patch_firstboot.py teklapelletcan.bin teklapelletcan-moj.bin --ssid MojaSiec --password 'haslo' \
      --ip 192.168.10.250 --mask 255.255.254.0 --gateway 192.168.10.1 --device-password 'haslo-urzadzenia'
DHCP: pomin --ip. Podglad zawartosci pliku: --show.
"""
import argparse, getpass, hashlib, ipaddress, struct, sys
from pathlib import Path

MAGIC = b"TPC-FIRSTBOOT-v1"
# uklad struktury FirstBoot (firmware/main/firstboot.h)
OFF = dict(valid=16, dhcp=17, ssid=20, ssid_n=33, pass_=53, pass_n=65, ip=118, gw=134, mask=150, dns=166, dev=182, dev_n=33)
SIZE = 218


def fix_image(b: bytearray) -> None:
    """Przelicza sume kontrolna segmentow i skrot SHA-256 obrazu aplikacji ESP (format esptool)."""
    if b[0] != 0xE9:
        raise SystemExit("to nie jest obraz aplikacji ESP (brak 0xE9)")
    nseg, hash_appended = b[1], b[23]
    pos, chk = 24, 0xEF
    for _ in range(nseg):
        _addr, size = struct.unpack_from("<II", b, pos)
        pos += 8
        for x in b[pos:pos + size]:
            chk ^= x
        pos += size
    cs_pos = pos + (15 - pos % 16)
    b[cs_pos] = chk
    if hash_appended:
        b[cs_pos + 1:cs_pos + 33] = hashlib.sha256(bytes(b[:cs_pos + 1])).digest()


def put_str(b, off, maxlen, s, what):
    raw = s.encode("utf-8")
    if len(raw) > maxlen:
        raise SystemExit(f"{what}: za dlugie ({len(raw)} > {maxlen} bajtow)")
    b[off:off + maxlen + 1] = raw + b"\0" * (maxlen + 1 - len(raw))


def get_str(b, off, n):
    return bytes(b[off:off + n]).split(b"\0", 1)[0].decode("utf-8", "replace")


def check_ip(s, what):
    try:
        ipaddress.IPv4Address(s)
    except ValueError:
        raise SystemExit(f"{what}: niepoprawny adres IPv4: {s}")
    return s


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("infile"); p.add_argument("outfile", nargs="?")
    p.add_argument("--ssid"); p.add_argument("--password")
    p.add_argument("--ip"); p.add_argument("--mask", default="255.255.255.0"); p.add_argument("--gateway"); p.add_argument("--dns", default="")
    p.add_argument("--device-password", dest="dev")
    p.add_argument("--show", action="store_true", help="tylko pokaz zawartosc pola (haslo zamaskowane)")
    a = p.parse_args()

    data = bytearray(Path(a.infile).read_bytes())
    if data.count(MAGIC) != 1:
        raise SystemExit(f"znacznik pola firstboot wystepuje {data.count(MAGIC)} razy (powinien raz) – zly plik?")
    base = data.index(MAGIC)

    if a.show:
        v = data[base:base + SIZE]
        print("wypelnione:", bool(v[OFF['valid']]), "| DHCP:", bool(v[OFF['dhcp']]), "| SSID:", get_str(v, OFF['ssid'], 33) or "-",
              "| haslo Wi-Fi:", "***" if get_str(v, OFF['pass_'], 65) else "-", "| IP:", get_str(v, OFF['ip'], 16) or "-",
              "| haslo urzadzenia:", "***" if get_str(v, OFF['dev'], 33) else "-")
        return
    if not a.outfile or not a.ssid:
        p.error("podaj plik wyjsciowy i --ssid")
    pw = a.password if a.password is not None else getpass.getpass("Haslo Wi-Fi (puste = siec otwarta): ")
    s = data[base:base + SIZE]
    s[OFF['valid']] = 1
    s[OFF['dhcp']] = 0 if a.ip else 1
    put_str(s, OFF['ssid'], 32, a.ssid, "SSID")
    put_str(s, OFF['pass_'], 64, pw, "haslo Wi-Fi")
    if a.ip:
        if not a.gateway:
            raise SystemExit("przy stalym IP podaj --gateway")
        put_str(s, OFF['ip'], 15, check_ip(a.ip, "ip"), "ip")
        put_str(s, OFF['gw'], 15, check_ip(a.gateway, "gateway"), "gateway")
        put_str(s, OFF['mask'], 15, check_ip(a.mask, "mask"), "mask")
        put_str(s, OFF['dns'], 15, check_ip(a.dns, "dns") if a.dns else "", "dns")
    if a.dev:
        if len(a.dev) < 4:
            raise SystemExit("haslo urzadzenia: min. 4 znaki")
        put_str(s, OFF['dev'], 32, a.dev, "haslo urzadzenia")
    data[base:base + SIZE] = s
    fix_image(data)
    Path(a.outfile).write_bytes(data)
    print(f"zapisano {a.outfile}: siec '{a.ssid}', {'stale IP ' + a.ip if a.ip else 'DHCP'}" + (", haslo urzadzenia ustawione" if a.dev else ""))
    print("Sprawdz plik:  python -m esptool image-info " + a.outfile)


if __name__ == "__main__":
    main()
