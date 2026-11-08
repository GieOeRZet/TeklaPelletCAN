#pragma once
// Pierścieniowy bufor logów w zewnętrznej pamięci (na ESP: RTC_NOINIT – przeżywa restart/panikę/rollback OTA).
// Czysty C++, testowany na hoście. Zapisuje całe linie; najstarsze są nadpisywane.
#include <cstddef>
#include <cstdint>
#include <string>

namespace tpc {

class LogRing {
public:
    // `mem` musi mieć co najmniej sizeof(Header) + 64 bajtów. Gdy nagłówek jest poprawny (przeżył restart), zachowuje zawartość.
    LogRing(uint8_t* mem, size_t size);

    void append(const char* line, size_t len);          // dopisuje linię (dodaje '\n' jeśli brak)
    void append(const std::string& s) { append(s.data(), s.size()); }
    std::string dump() const;                            // cała zawartość od najstarszej do najnowszej linii
    std::string tail(size_t max_bytes) const;            // ostatnie ~max_bytes (od początku linii)
    void clear();
    size_t size() const;                                 // liczba zapisanych bajtów
    bool survived() const { return survived_; }          // czy zawartość pochodzi sprzed restartu

private:
    struct Header { uint32_t magic; uint32_t head; uint32_t used; uint32_t check; };
    static uint32_t chk(const Header& h) { return h.magic ^ (h.head * 2654435761u) ^ (h.used * 40503u) ^ 0xA5A5A5A5u; }
    void save(Header h) { h.check = chk(h); *hdr_ = h; }
    Header* hdr_;
    uint8_t* data_;
    size_t cap_;
    bool survived_ = false;
};

}  // namespace tpc
