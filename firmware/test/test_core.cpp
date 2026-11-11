#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>
#include "../components/core/codec.h"
#include "../components/core/mcp2515.h"
#include "../components/core/sdo.h"
#include "../components/core/version.h"
#include "../components/core/net_fsm.h"
#include "../components/core/access.h"
#include "../components/core/point.h"
#include "../components/core/sdo_queue.h"
#include "../components/core/license.h"
#include "../components/core/ota.h"
#include "../components/core/dns.h"
#include "../components/core/logring.h"
#include "../components/core/antenna.h"
#include "ota_vectors.h"
#include "license_vectors.h"

using namespace tpc;

// Atrapa MCP2515: rejestry, bufor TX i jedna ramka w RXB0.
struct FakeMcp : ISpi {
    uint8_t reg[256] = {0};
    std::vector<std::vector<uint8_t>> log;
    bool rx_pending = false;
    uint8_t rxbuf[13] = {0};
    uint8_t txbuf[13] = {0};
    bool rts = false;

    bool transfer(const uint8_t* tx, uint8_t* rx, size_t len) override {
        log.emplace_back(tx, tx + len);
        memset(rx, 0, len);
        switch (tx[0]) {
            case 0xC0: memset(reg, 0, sizeof reg); reg[0x0E] = 0x80; break;
            case 0x02:
                reg[tx[1]] = tx[2];
                if (tx[1] == 0x0F) reg[0x0E] = tx[2] & 0xE0;
                break;
            case 0x03: rx[2] = reg[tx[1]]; break;
            case 0x05: reg[tx[1]] = (reg[tx[1]] & ~tx[2]) | (tx[3] & tx[2]); break;
            case 0x40: memcpy(txbuf, tx + 1, len - 1); break;
            case 0x81: rts = true; break;
            case 0xA0: rx[1] = reg[0x2C] & 0x03; break;
            case 0x90: memcpy(rx + 1, rxbuf, 13); rx_pending = false; break;
        }
        if (rx_pending) reg[0x2C] |= 0x01; else reg[0x2C] &= ~0x01;
        return true;
    }
};

static void test_sdo() {
    CanFrame r = sdo_read_request(4, 0x2207, 1);
    assert(r.id == 0x604 && r.dlc == 8 && r.data[0] == 0x40);
    assert(r.data[1] == 0x07 && r.data[2] == 0x22 && r.data[3] == 1);

    CanFrame w = sdo_write_request(4, 0x2207, 1, 269, 2);
    assert(w.id == 0x604 && w.data[0] == 0x2B && w.data[4] == 0x0D && w.data[5] == 0x01);
    assert(sdo_write_request(4, 1, 1, 1, 3).id == 0);

    // odpowiedź 2 bajty: 0x4B, wartość 269
    CanFrame a; a.id = 0x584; a.dlc = 8;
    a.data[0] = 0x4B; a.data[1] = 0x07; a.data[2] = 0x22; a.data[3] = 1; a.data[4] = 0x0D; a.data[5] = 0x01;
    SdoReply p = sdo_parse_reply(4, a);
    assert(p.status == SdoStatus::Ok && !p.is_write_ack && p.index == 0x2207 && p.sub == 1);
    assert(p.size == 2 && p.value == 269);
    assert(sdo_parse_reply(5, a).status == SdoStatus::BadFrame);  // zły węzeł

    a.data[0] = 0x43; a.data[4] = 0x78; a.data[5] = 0x56; a.data[6] = 0x34; a.data[7] = 0x12;
    p = sdo_parse_reply(4, a);
    assert(p.size == 4 && p.value == 0x12345678);

    CanFrame ack; ack.id = 0x584; ack.dlc = 8; ack.data[0] = 0x60;
    ack.data[1] = 0x07; ack.data[2] = 0x22; ack.data[3] = 1;
    p = sdo_parse_reply(4, ack);
    assert(p.status == SdoStatus::Ok && p.is_write_ack && p.index == 0x2207);

    CanFrame ab; ab.id = 0x584; ab.dlc = 8; ab.data[0] = 0x80;
    ab.data[1] = 0x07; ab.data[2] = 0x22; ab.data[3] = 1;
    ab.data[4] = 0x02; ab.data[7] = 0x06;  // 0x06000002 – obiekt nie istnieje
    p = sdo_parse_reply(4, ab);
    assert(p.status == SdoStatus::Abort && p.abort_code == 0x06000002);
}

static void test_codec() {
    assert(decode(Encoding::FlagByte, 269).value == 13);
    assert(encode(Encoding::FlagByte, 13).raw == 269);
    assert(encode(Encoding::FlagByte, 256).ok == false);
    assert(decode(Encoding::Plain, 17).value == 17);
    assert(decode(Encoding::Tenths, 46).value == 4.6);
    assert(encode(Encoding::Tenths, 4.6).raw == 46);
    assert(decode(Encoding::Switch, 257).value == 1);
    assert(!decode(Encoding::Switch, 5).ok);
    assert(encode(Encoding::Switch, 0).raw == 256);
    assert(encode(Encoding::EnumList, 3).raw == 259);
    assert(encode(Encoding::Mask24, 0xFFFFFF).ok);
    assert(!encode(Encoding::Mask24, 0x1000000).ok);
    assert(!encode(Encoding::Plain, -1).ok);
    assert(decode(Encoding::FlagTenths, 256 + 46).value == 4.6);
}

static void test_mcp() {
    FakeMcp spi;
    Mcp2515 can(spi);
    assert(can.begin(CanSpeed::K125, CanClock::MHz16, CanMode::Normal));
    assert(spi.reg[0x2A] == 0x03 && spi.reg[0x29] == 0xF0 && spi.reg[0x28] == 0x86);
    assert(spi.reg[0x0F] == 0x00);

    CanFrame f = sdo_read_request(4, 0x2207, 1);
    assert(can.send(f));
    assert(spi.rts);
    assert(spi.txbuf[0] == (0x604 >> 3) && spi.txbuf[1] == ((0x604 & 7) << 5));
    assert(spi.txbuf[4] == 8 && spi.txbuf[5] == 0x40);

    // przychodzi odpowiedź 0x584
    spi.rxbuf[0] = 0x584 >> 3; spi.rxbuf[1] = (0x584 & 7) << 5; spi.rxbuf[4] = 8;
    spi.rxbuf[5] = 0x4B; spi.rxbuf[6] = 0x07; spi.rxbuf[7] = 0x22; spi.rxbuf[8] = 1;
    spi.rxbuf[9] = 0x0D; spi.rxbuf[10] = 0x01;
    spi.rx_pending = true; spi.reg[0x2C] = 0x01;
    CanFrame in;
    assert(can.receive(in));
    assert(in.id == 0x584 && in.dlc == 8);
    SdoReply p = sdo_parse_reply(4, in);
    assert(p.status == SdoStatus::Ok && p.value == 269);
    assert(!can.receive(in));  // nic więcej

    // zajęty bufor TX
    spi.reg[0x30] = 0x08;
    assert(!can.send(f));
}

static void test_version() {
    Version a = parse_version("1.4.23"), b = parse_version("v1.5.0");
    assert(a.valid && b.valid && a.minor == 4 && b.major == 1);
    assert(compare_versions(a, b) < 0 && compare_versions(b, a) > 0 && compare_versions(a, a) == 0);
    assert(!parse_version("1.4").valid && !parse_version("x.y.z").valid && !parse_version("1.2.3-").valid);
    assert(parse_version("1.10.0").minor == 10 && compare_versions(parse_version("1.10.0"), parse_version("1.9.9")) > 0);
    Version beta = parse_version("1.5.0-beta1");
    assert(beta.valid && beta.prerelease && compare_versions(beta, b) < 0);
    assert(is_update(a, b, false));
    assert(!is_update(a, a, false));
    assert(!is_update(b, a, false));            // starsza nie jest aktualizacją
    assert(!is_update(a, beta, false));         // beta ukryta
    assert(is_update(a, beta, true));
    assert(!is_update(a, parse_version("śmieci"), true));
}

static void test_net() {
    NetFsm f;
    f.begin(false, 0);                          // pierwsze uruchomienie
    NetOutput o = f.tick(0);
    assert(f.state() == NetState::Provisioning && o.ap_on && !o.sta_on);

    f.on_new_credentials(false, 1000);          // portal: nowe dane
    o = f.tick(1000);
    assert(o.ap_on && o.sta_on && f.state() == NetState::Trial);
    f.on_sta_connected(5000);
    o = f.tick(5000);
    assert(o.trial_ok && o.ap_on);              // AP jeszcze trwa (portal pokazuje IP)
    o = f.tick(16000);
    assert(f.state() == NetState::Online && !o.ap_on && o.sta_on);

    // utrata sieci: najpierw cicha próba, po 30 s wraca AP
    f.on_sta_disconnected(20000);
    o = f.tick(20000);
    assert(f.state() == NetState::Connecting && !o.ap_on && o.sta_on);
    o = f.tick(49000);
    assert(!o.ap_on);
    o = f.tick(50001);
    assert(f.state() == NetState::Fallback && o.ap_on && o.sta_on);
    // sieć wraca: AP znika dopiero po ustabilizowaniu
    f.on_sta_connected(60000);
    o = f.tick(61000);
    assert(o.ap_on);
    o = f.tick(70001);
    assert(f.state() == NetState::Online && !o.ap_on);

    // start z danymi, ale sieć niedostępna
    NetFsm g;
    g.begin(true, 0);
    assert(!g.tick(10000).ap_on);
    o = g.tick(30000);
    assert(g.state() == NetState::Fallback && o.ap_on);

    // zły test nowych danych przy istniejących starych
    NetFsm h;
    h.begin(true, 0);
    h.on_sta_connected(1000); h.tick(1000);
    h.on_new_credentials(true, 5000);
    h.on_sta_disconnected(5000);
    o = h.tick(36000);
    assert(o.trial_failed && o.use_previous_credentials && h.state() == NetState::Connecting);
    o = h.tick(36001);
    assert(!o.trial_failed && !o.use_previous_credentials);   // zdarzenie jednorazowe

    // zły test bez starych danych: wracamy do portalu
    NetFsm k;
    k.begin(false, 0);
    k.on_new_credentials(false, 0);
    o = k.tick(30000);
    assert(o.trial_failed && !o.use_previous_credentials && k.state() == NetState::Provisioning && o.ap_on);
}

static void test_signed_codec() {
    assert(encode(Encoding::PlainS16, -10).raw == 0xFFF6);
    assert(decode(Encoding::PlainS16, 0xFFF6).value == -10);
    assert(decode(Encoding::PlainS16, 5).value == 5);
    assert(encode(Encoding::TenthsS16, -1.5).raw == 0xFFF1);
    assert(decode(Encoding::TenthsS16, 0xFFF1).value == -1.5);
    assert(!encode(Encoding::PlainS16, 40000).ok);
}

static void test_points() {
    assert(kPointCount == 110);
    const Point* p = find_point_by_key(0);
    assert(p && p->index == 0x2270 && p->encoding == Encoding::FlagByte && p->level == 0);
    p = find_point_by_key(3);                       // korekta powietrza, ze znakiem
    assert(p && p->index == 0x2273 && p->encoding == Encoding::PlainS16 && p->min == -10);
    assert(find_point_by_index(0x2261)->level == 1);
    assert(find_point_by_key(200) == nullptr);
    // zakresy muszą być kodowalne na krańcach
    for (unsigned i = 0; i < kPointCount; i++) {
        assert(encode(kPoints[i].encoding, kPoints[i].min).ok);
        assert(encode(kPoints[i].encoding, kPoints[i].max).ok);
    }
}

static void test_access() {
    Access a;
    uint32_t raw = 0;
    const Point* lvl0 = find_point_by_key(0);   // Moc min, poziom 0
    const Point* lvl1 = find_point_by_key(5);   // krzywa dmuchawy, poziom 1
    assert(a.check_write(*lvl0, 50, 0, raw) == WriteResult::Ok && raw == 256 + 50);
    assert(a.check_write(*lvl0, 20, 0, raw) == WriteResult::Range);   // poniżej 30
    assert(a.check_write(*lvl1, 50, 0, raw) == WriteResult::Level);
    assert(a.unlock(1234, 0) == 0);                                    // zły PIN
    assert(a.unlock(900, 1000) == 1);
    assert(a.check_write(*lvl1, 50, 2000, raw) == WriteResult::Ok);
    assert(a.tick(2000 + 299999) == 1);
    assert(a.tick(2000 + 300000) == 0);                                // autoblokada po 5 min
    assert(a.unlock(999, 0) == 2);

    AccessConfig c; c.mirror = true;
    Access m(c);
    assert(m.check_write(*lvl0, 50, 0, raw) == WriteResult::Mirror);
}

static void test_queue() {
    std::vector<CanFrame> sent;
    std::vector<SdoResult> done;
    SdoQueue q(4, [&](const CanFrame& f) { sent.push_back(f); return true; },
               [&](const SdoResult& r) { done.push_back(r); });
    SdoJob rd; rd.index = 0x2207; rd.tag = 1;
    SdoJob wr; wr.write = true; wr.index = 0x2270; wr.value = 300; wr.tag = 2;
    q.push(rd);
    q.push(wr);                       // zapis wyprzedza odczyt
    q.tick(0);
    assert(sent.size() == 1 && sent[0].data[0] == 0x2B);              // pierwszy poszedł zapis
    CanFrame ack; ack.id = 0x584; ack.dlc = 8; ack.data[0] = 0x60; ack.data[1] = 0x70; ack.data[2] = 0x22; ack.data[3] = 1;
    q.on_frame(ack, 5);
    assert(done.size() == 1 && done[0].outcome == SdoOutcome::Ok && done[0].job.tag == 2);

    q.tick(10);                       // odczyt
    assert(sent.size() == 2 && sent[1].data[0] == 0x40);
    CanFrame other = ack; other.data[1] = 0x01;                        // inna odpowiedź – ignorowana
    q.on_frame(other, 12);
    assert(done.size() == 1);
    q.tick(10 + 200);                                                  // limit czasu -> ponowienie
    assert(sent.size() == 3);
    q.tick(10 + 400);
    assert(sent.size() == 4);
    q.tick(10 + 600);                                                  // po 2 ponowieniach: Timeout
    assert(done.size() == 2 && done[1].outcome == SdoOutcome::Timeout && q.pending() == 0);

    // abort
    q.push(rd); q.tick(1000);
    CanFrame ab; ab.id = 0x584; ab.dlc = 8; ab.data[0] = 0x80; ab.data[1] = 0x07; ab.data[2] = 0x22; ab.data[3] = 1; ab.data[7] = 0x06;
    q.on_frame(ab, 1010);
    assert(done.size() == 3 && done[2].outcome == SdoOutcome::Abort);

    // odczyt z wartością
    q.push(rd); q.tick(2000);
    CanFrame ok; ok.id = 0x584; ok.dlc = 8; ok.data[0] = 0x4B; ok.data[1] = 0x07; ok.data[2] = 0x22; ok.data[3] = 1;
    ok.data[4] = 0x0D; ok.data[5] = 0x01;
    q.on_frame(ok, 2005);
    assert(done[3].outcome == SdoOutcome::Ok && done[3].value == 269);
}

static void test_license() {
    const uint8_t dev[6] = {0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6};
    const uint8_t other[6] = {0, 0, 0, 0, 0, 1};
    LicenseInfo info;
    assert(license_verify(kCodeAny, dev, kLicensePubKey, info) == LicenseResult::Ok);
    assert(info.tier == Tier::Full && info.serial == 1);
    assert(license_verify(kCodeAny, other, kLicensePubKey, info) == LicenseResult::Ok);   // dla dowolnego
    assert(license_verify(kCodeBound, dev, kLicensePubKey, info) == LicenseResult::Ok);
    assert(info.serial == 7 && info.device[0] == 0xA1);
    assert(license_verify(kCodeBound, other, kLicensePubKey, info) == LicenseResult::Device);
    assert(license_verify(kCodeTampered, dev, kLicensePubKey, info) == LicenseResult::Signature);
    // tolerancja zapisu: małe litery, spacje
    std::string lower = kCodeBound;
    for (auto& ch : lower) ch = (char)tolower((unsigned char)ch);
    assert(license_verify(" " + lower + " ", dev, kLicensePubKey, info) == LicenseResult::Ok);
    assert(license_verify("", dev, kLicensePubKey, info) == LicenseResult::Format);
    assert(license_verify("TPC1-AAAA", dev, kLicensePubKey, info) == LicenseResult::Format);
    assert(license_verify(std::string("XXXX") + std::string(kCodeBound).substr(4), dev, kLicensePubKey, info) == LicenseResult::Format);
    // inny klucz publiczny -> podpis nie pasuje
    uint8_t wrong[65]; memcpy(wrong, kLicensePubKey, 65); wrong[64] ^= 1;
    assert(license_verify(kCodeBound, dev, wrong, info) == LicenseResult::Signature);
    assert(kLicenseDevKey);  // w repo jest klucz testowy
}

struct MemTarget : OtaTarget {
    std::vector<uint8_t> data; bool began = false, ended = false, aborted = false;
    bool begin(size_t) override { began = true; return true; }
    bool write(const uint8_t* d, size_t n) override { data.insert(data.end(), d, d + n); return true; }
    bool end() override { ended = true; return true; }
    void abort() override { aborted = true; }
};

static void test_ota() {
    const size_t n = sizeof kOtaGood;
    {   // poprawny obraz, podawany kawałkami
        MemTarget t; OtaSession s(t, kOtaPubKey, 1 << 20);
        assert(s.begin(n, kOtaGoodSig) == OtaResult::Ok);
        for (size_t off = 0; off < n; off += 37) assert(s.feed(kOtaGood + off, std::min<size_t>(37, n - off)) == OtaResult::Ok);
        assert(!t.ended);                                   // przed podpisem nic nie jest aktywowane
        assert(s.finish() == OtaResult::Ok && t.ended && t.data.size() == n);
    }
    {   // zmieniony bajt -> zły podpis, partycja NIE jest aktywowana
        MemTarget t; OtaSession s(t, kOtaPubKey, 1 << 20);
        assert(s.begin(n, kOtaGoodSig) == OtaResult::Ok);
        assert(s.feed(kOtaTampered, n) == OtaResult::Ok);
        assert(s.finish() == OtaResult::BadSignature && !t.ended && t.aborted);
    }
    {   // zły chip_id (np. obraz dla ESP32) -> odrzucony od razu
        MemTarget t; OtaSession s(t, kOtaPubKey, 1 << 20);
        assert(s.begin(sizeof kOtaWrongChip, kOtaWrongChipSig) == OtaResult::Ok);
        assert(s.feed(kOtaWrongChip, sizeof kOtaWrongChip) == OtaResult::BadImage && !t.ended && t.aborted);
    }
    {   // brak magic 0xE9
        MemTarget t; OtaSession s(t, kOtaPubKey, 1 << 20);
        uint8_t junk[200] = {0};
        assert(s.begin(sizeof junk, kOtaGoodSig) == OtaResult::Ok);
        assert(s.feed(junk, sizeof junk) == OtaResult::BadImage);
    }
    {   // za duży, zły format podpisu, podpis od innego obrazu
        MemTarget t; OtaSession s(t, kOtaPubKey, 500);
        assert(s.begin(n, kOtaGoodSig) == OtaResult::TooBig);
        MemTarget t2; OtaSession s2(t2, kOtaPubKey, 1 << 20);
        assert(s2.begin(n, "zzzz") == OtaResult::BadSignature);
        MemTarget t3; OtaSession s3(t3, kOtaPubKey, 1 << 20);
        assert(s3.begin(n, kOtaWrongChipSig) == OtaResult::Ok);
        assert(s3.feed(kOtaGood, n) == OtaResult::Ok && s3.finish() == OtaResult::BadSignature && !t3.ended);
    }
    {   // pakiet z podpisem wbudowanym w plik: bez osobnego .sig, podawany kawałkami o różnych rozmiarach (też przez granicę trailera)
        for (size_t chunk : {1u, 37u, 71u, 72u, 73u, 500u, 5000u}) {
            MemTarget t; OtaSession s(t, kOtaPubKey, 1 << 20);
            assert(s.begin(sizeof kOtaPackage, "") == OtaResult::Ok);
            for (size_t off = 0; off < sizeof kOtaPackage; off += chunk) assert(s.feed(kOtaPackage + off, std::min<size_t>(chunk, sizeof kOtaPackage - off)) == OtaResult::Ok);
            assert(!t.ended);
            assert(s.finish() == OtaResult::Ok && t.ended);
            assert(t.data.size() == sizeof kOtaGood && memcmp(t.data.data(), kOtaGood, sizeof kOtaGood) == 0);   // na partycję trafia sam obraz, bez trailera
        }
        MemTarget t2; OtaSession s2(t2, kOtaPubKey, 1 << 20);      // zmieniony obraz z poprawnym trailerem -> zły podpis
        assert(s2.begin(sizeof kOtaPackageTampered, "") == OtaResult::Ok);
        assert(s2.feed(kOtaPackageTampered, sizeof kOtaPackageTampered) == OtaResult::Ok && s2.finish() == OtaResult::BadSignature && !t2.ended);
        MemTarget t3; OtaSession s3(t3, kOtaPubKey, 1 << 20);      // plik bez podpisu (trailer pusty)
        assert(s3.begin(sizeof kOtaPackageNoSig, "") == OtaResult::Ok);
        assert(s3.feed(kOtaPackageNoSig, sizeof kOtaPackageNoSig) == OtaResult::Ok && s3.finish() == OtaResult::BadImage && !t3.ended);
        MemTarget t4; OtaSession s4(t4, kOtaPubKey, 1 << 20);      // zwykły obraz bez trailera podany bez podpisu
        assert(s4.begin(sizeof kOtaGood, "") == OtaResult::Ok);
        assert(s4.feed(kOtaGood, sizeof kOtaGood) == OtaResult::Ok && s4.finish() == OtaResult::BadImage && !t4.ended);
    }
    {   // przerwane przesyłanie (za mało bajtów)
        MemTarget t; OtaSession s(t, kOtaPubKey, 1 << 20);
        assert(s.begin(n, kOtaGoodSig) == OtaResult::Ok);
        assert(s.feed(kOtaGood, n - 10) == OtaResult::Ok && s.finish() == OtaResult::BadImage && !t.ended);
    }
}

static void test_dns() {
    // zapytanie A o "example.com"
    const uint8_t qa[] = {0x12, 0x34, 0x01, 0x00, 0, 1, 0, 0, 0, 0, 0, 0,
                          7, 'e','x','a','m','p','l','e', 3, 'c','o','m', 0, 0, 1, 0, 1};
    auto r = dns_captive_response(qa, sizeof qa, (192u << 24) | (168u << 16) | (4u << 8) | 1u);
    assert(r.size() == sizeof qa + 16);
    assert(r[0] == 0x12 && r[1] == 0x34 && (r[2] & 0x80) && r[7] == 1);
    assert(r[r.size() - 4] == 192 && r[r.size() - 3] == 168 && r[r.size() - 2] == 4 && r[r.size() - 1] == 1);
    // AAAA -> pusta odpowiedź (bez rekordu), też poprawna
    uint8_t qaaaa[sizeof qa]; memcpy(qaaaa, qa, sizeof qa); qaaaa[sizeof qa - 4] = 0; qaaaa[sizeof qa - 3] = 28;
    auto r2 = dns_captive_response(qaaaa, sizeof qaaaa, 0);
    assert(r2.size() == sizeof qa && r2[7] == 0);
    assert(dns_captive_response(qa, 5, 0).empty());               // śmieci
}

static void test_logring() {
    uint8_t mem[256];
    memset(mem, 0xAB, sizeof mem);                       // "śmieci" jak w RTC po włączeniu zasilania
    {
        LogRing r(mem, sizeof mem);
        assert(!r.survived() && r.size() == 0);
        r.append("pierwsza"); r.append("druga\n");
        assert(r.dump() == "pierwsza\ndruga\n");
    }
    {
        LogRing r2(mem, sizeof mem);                      // "po restarcie": zawartość przeżywa
        assert(r2.survived() && r2.dump() == "pierwsza\ndruga\n");
        for (int i = 0; i < 100; i++) r2.append("linia numer " + std::to_string(i));   // zawinięcie bufora
        std::string d = r2.dump();
        assert(d.size() < sizeof mem && d.find("linia numer 99\n") != std::string::npos);
        assert(d.find("pierwsza") == std::string::npos);  // najstarsze nadpisane
        assert(d[0] != '\n' && d.rfind("linia", 0) == 0);  // ucięta pierwsza linia pominięta
        assert(r2.tail(40).size() <= 40);
        r2.clear();
        assert(r2.dump().empty());
    }
    uint8_t bad[256]; memset(bad, 0, sizeof bad);
    bad[0] = 0x52; bad[1] = 0x47; bad[2] = 0x4F; bad[3] = 0x4C;   // poprawny magic, zły checksum -> reset
    LogRing r3(bad, sizeof bad);
    assert(!r3.survived() && r3.size() == 0);
}

static void test_antenna() {
    {   // antena zewnętrzna działa: nic się nie zmienia
        AntennaFailover a(true);
        for (auto st : {NetState::Connecting, NetState::Online, NetState::Online}) { AntennaOut o = a.tick(st); assert(o.external && !o.changed); }
        assert(a.using_external() && !a.auto_fallback());
    }
    {   // brak połączenia (Fallback) na antenie zewnętrznej -> przełącz na wewnętrzną dokładnie raz
        AntennaFailover a(true);
        assert(!a.tick(NetState::Connecting).changed);
        AntennaOut o = a.tick(NetState::Fallback);
        assert(o.changed && !o.external && a.auto_fallback());
        o = a.tick(NetState::Fallback);                  // kolejne wywołania: bez zmian
        assert(!o.changed && !o.external);
        o = a.tick(NetState::Online);
        assert(!o.changed && !o.external);               // zostaje na wewnętrznej do restartu
    }
    {   // antena wewnętrzna wybrana od początku: nigdy nie „przełącza"
        AntennaFailover a(false);
        AntennaOut o = a.tick(NetState::Fallback);
        assert(!o.changed && !o.external && !a.auto_fallback());
    }
    {   // brak zapisanej sieci (Provisioning) to nie awaria anteny
        AntennaFailover a(true);
        assert(!a.tick(NetState::Provisioning).changed && a.using_external());
    }
}

int main() {
    test_sdo();
    test_codec();
    test_mcp();
    test_version();
    test_net();
    test_signed_codec();
    test_points();
    test_access();
    test_queue();
    test_license();
    test_ota();
    test_dns();
    test_logring();
    test_antenna();
    puts("OK: wszystkie testy przeszly");
    return 0;
}
