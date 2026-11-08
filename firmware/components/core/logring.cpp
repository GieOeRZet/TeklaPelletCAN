#include "logring.h"
#include <cstring>

namespace tpc {

static const uint32_t kMagic = 0x4C4F4752;   // "LOGR"

LogRing::LogRing(uint8_t* mem, size_t size) {
    hdr_ = reinterpret_cast<Header*>(mem);
    data_ = mem + sizeof(Header);
    cap_ = size > sizeof(Header) ? size - sizeof(Header) : 0;
    Header h = *hdr_;
    if (h.magic == kMagic && h.check == chk(h) && h.head < cap_ && h.used <= cap_) {
        survived_ = h.used > 0;
    } else {
        Header z{kMagic, 0, 0, 0};
        save(z);
    }
}

void LogRing::clear() { Header z{kMagic, 0, 0, 0}; save(z); survived_ = false; }

size_t LogRing::size() const { return hdr_->used; }

void LogRing::append(const char* line, size_t len) {
    if (cap_ == 0) return;
    Header h = *hdr_;
    bool nl = len > 0 && line[len - 1] == '\n';
    for (size_t i = 0; i < len + (nl ? 0 : 1); i++) {
        const char c = i < len ? line[i] : '\n';
        data_[h.head] = (uint8_t)c;
        h.head = (h.head + 1) % cap_;
        if (h.used < cap_) h.used++;
    }
    save(h);
}

std::string LogRing::dump() const {
    std::string out;
    const Header h = *hdr_;
    out.reserve(h.used);
    size_t start = (h.head + cap_ - h.used) % cap_;
    for (size_t i = 0; i < h.used; i++) out.push_back((char)data_[(start + i) % cap_]);
    // jeśli bufor się zawinął, pierwsza linia jest ucięta – pomiń ją
    if (h.used == cap_) { size_t nl = out.find('\n'); if (nl != std::string::npos) out.erase(0, nl + 1); }
    return out;
}

std::string LogRing::tail(size_t max_bytes) const {
    std::string all = dump();
    if (all.size() <= max_bytes) return all;
    std::string t = all.substr(all.size() - max_bytes);
    size_t nl = t.find('\n');
    return nl == std::string::npos ? t : t.substr(nl + 1);
}

}  // namespace tpc
