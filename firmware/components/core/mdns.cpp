#include "mdns.h"
#include <cctype>

namespace tpc {

namespace {
using Bytes = std::vector<uint8_t>;
constexpr uint16_t T_A = 1, T_PTR = 12, T_TXT = 16, T_SRV = 33, T_ANY = 255;

void put16(Bytes& b, uint16_t v) { b.push_back((uint8_t)(v >> 8)); b.push_back((uint8_t)v); }
void put32(Bytes& b, uint32_t v) { put16(b, (uint16_t)(v >> 16)); put16(b, (uint16_t)v); }

void put_name(Bytes& b, const std::string& name) {          // "a.b.c" -> etykiety
    size_t i = 0;
    while (i <= name.size()) {
        size_t dot = name.find('.', i);
        if (dot == std::string::npos) dot = name.size();
        const size_t len = dot - i;
        if (len > 0 && len < 64) { b.push_back((uint8_t)len); b.insert(b.end(), name.begin() + i, name.begin() + dot); }
        i = dot + 1;
    }
    b.push_back(0);
}

std::string lower(std::string s) { for (auto& c : s) c = (char)tolower((unsigned char)c); return s; }

// Czyta nazwę (z obsługą wskaźników kompresji); zwraca pozycję za nazwą w oryginalnym strumieniu albo 0 przy błędzie.
size_t read_name(const uint8_t* p, size_t n, size_t pos, std::string& out) {
    size_t next = 0;
    bool jumped = false;
    int guard = 0;
    out.clear();
    while (pos < n && guard++ < 40) {
        const uint8_t l = p[pos];
        if (l == 0) { if (!jumped) next = pos + 1; return next ? next : pos + 1; }
        if ((l & 0xC0) == 0xC0) {
            if (pos + 1 >= n) return 0;
            if (!jumped) next = pos + 2;
            pos = (size_t)(((l & 0x3F) << 8) | p[pos + 1]);
            jumped = true;
            continue;
        }
        if (pos + 1 + l > n) return 0;
        if (!out.empty()) out += '.';
        out.append((const char*)p + pos + 1, l);
        pos += 1 + l;
    }
    return 0;
}

struct Rec { std::string name; uint16_t type; Bytes rdata; bool flush; uint32_t ttl; };

void add_rec(Bytes& b, const Rec& r) {
    put_name(b, r.name);
    put16(b, r.type);
    put16(b, (uint16_t)(1 | (r.flush ? 0x8000 : 0)));
    put32(b, r.ttl);
    put16(b, (uint16_t)r.rdata.size());
    b.insert(b.end(), r.rdata.begin(), r.rdata.end());
}

Rec rec_a(const MdnsConfig& c) {
    Rec r{c.host + ".local", T_A, {}, true, 120};
    r.rdata = {(uint8_t)(c.ipv4 >> 24), (uint8_t)(c.ipv4 >> 16), (uint8_t)(c.ipv4 >> 8), (uint8_t)c.ipv4};
    return r;
}
Rec rec_ptr(const MdnsConfig& c) {
    Rec r{c.service + ".local", T_PTR, {}, false, 4500};
    put_name(r.rdata, c.instance + "." + c.service + ".local");
    return r;
}
Rec rec_srv(const MdnsConfig& c) {
    Rec r{c.instance + "." + c.service + ".local", T_SRV, {}, true, 120};
    put16(r.rdata, 0); put16(r.rdata, 0); put16(r.rdata, c.port);
    put_name(r.rdata, c.host + ".local");
    return r;
}
Rec rec_txt(const MdnsConfig& c) {
    Rec r{c.instance + "." + c.service + ".local", T_TXT, {}, true, 4500};
    if (c.txt.empty()) r.rdata.push_back(0);
    for (auto& t : c.txt) { r.rdata.push_back((uint8_t)t.size()); r.rdata.insert(r.rdata.end(), t.begin(), t.end()); }
    return r;
}
Rec rec_meta(const MdnsConfig& c) {   // _services._dns-sd._udp.local PTR -> typ usługi
    Rec r{"_services._dns-sd._udp.local", T_PTR, {}, false, 4500};
    put_name(r.rdata, c.service + ".local");
    return r;
}

Bytes build(const std::vector<Rec>& answers, const std::vector<Rec>& extra) {
    Bytes b;
    put16(b, 0); put16(b, 0x8400);               // id 0, odpowiedź autorytatywna
    put16(b, 0); put16(b, (uint16_t)answers.size()); put16(b, 0); put16(b, (uint16_t)extra.size());
    for (auto& r : answers) add_rec(b, r);
    for (auto& r : extra) add_rec(b, r);
    return b;
}
}  // namespace

std::vector<uint8_t> mdns_respond(const MdnsConfig& c, const uint8_t* q, size_t n) {
    if (n < 12 || (q[2] & 0x80)) return {};                       // tylko zapytania
    const uint16_t qd = (uint16_t)((q[4] << 8) | q[5]);
    size_t pos = 12;
    std::vector<Rec> answers, extra;
    const std::string host = lower(c.host + ".local"), svc = lower(c.service + ".local"),
                      inst = lower(c.instance + "." + c.service + ".local");
    bool want_ptr = false, want_a = false, want_srv = false, want_txt = false, want_meta = false;
    for (uint16_t i = 0; i < qd; i++) {
        std::string name;
        pos = read_name(q, n, pos, name);
        if (pos == 0 || pos + 4 > n) return {};
        const uint16_t type = (uint16_t)((q[pos] << 8) | q[pos + 1]);
        pos += 4;
        name = lower(name);
        const bool any = type == T_ANY;
        if (name == host && (type == T_A || any)) want_a = true;
        if (name == svc && (type == T_PTR || any)) want_ptr = true;
        if (name == inst && (type == T_SRV || any)) want_srv = true;
        if (name == inst && (type == T_TXT || any)) want_txt = true;
        if (name == "_services._dns-sd._udp.local" && (type == T_PTR || any)) want_meta = true;
    }
    if (want_meta) answers.push_back(rec_meta(c));
    if (want_ptr) {
        answers.push_back(rec_ptr(c));
        extra.push_back(rec_srv(c)); extra.push_back(rec_txt(c)); extra.push_back(rec_a(c));
    }
    if (want_srv) { answers.push_back(rec_srv(c)); extra.push_back(rec_a(c)); }
    if (want_txt) answers.push_back(rec_txt(c));
    if (want_a) answers.push_back(rec_a(c));
    if (answers.empty()) return {};
    return build(answers, extra);
}

std::vector<uint8_t> mdns_announce(const MdnsConfig& c) {
    return build({rec_ptr(c), rec_srv(c), rec_txt(c), rec_a(c)}, {});
}

}  // namespace tpc
