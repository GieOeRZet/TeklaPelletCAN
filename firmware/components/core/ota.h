#pragma once
// Aktualizacja OTA: strumieniowy zapis obrazu na nieaktywną partycję + weryfikacja podpisu ECDSA P-256 (SHA-256 obrazu).
// Czysty C++ (cel zapisu wstrzykiwany), więc testowalny na hoście.
#include <cstddef>
#include <cstdint>
#include <string>
#include "mbedtls/sha256.h"

namespace tpc {

extern const uint8_t kOtaPubKey[65];   // wygenerowany z tools/ota_sign.py
extern const bool kOtaDevKey;

class OtaTarget {
public:
    virtual ~OtaTarget() = default;
    virtual bool begin(size_t total_size) = 0;
    virtual bool write(const uint8_t* data, size_t len) = 0;
    virtual bool end() = 0;       // ustawia nową partycję jako startową – wołane dopiero po poprawnym podpisie
    virtual void abort() = 0;
};

enum class OtaResult : uint8_t { Ok, Busy, BadSignature, BadImage, WriteFailed, TooBig, NotStarted };

constexpr uint16_t kChipEsp32C6 = 13;   // pole chip_id w nagłówku obrazu ESP

class OtaSession {
public:
    OtaSession(OtaTarget& target, const uint8_t pubkey[65], size_t max_size, uint16_t chip_id = kChipEsp32C6)
        : t_(target), pub_(pubkey), max_(max_size), chip_(chip_id) {}
    ~OtaSession();

    // sig_hex = 128 znaków hex (r||s). Zwraca Ok albo przyczynę odmowy (wtedy nic nie zostało aktywowane).
    OtaResult begin(size_t total_size, const std::string& sig_hex);
    OtaResult feed(const uint8_t* data, size_t len);
    OtaResult finish();      // sprawdza podpis i dopiero wtedy aktywuje obraz
    void abort();
    bool active() const { return active_; }
    size_t received() const { return got_; }

private:
    OtaTarget& t_;
    const uint8_t* pub_;
    size_t max_;
    uint16_t chip_;
    mbedtls_sha256_context sha_;
    uint8_t sig_[64];
    size_t total_ = 0, got_ = 0;
    uint8_t head_[16];
    bool active_ = false, sha_init_ = false;
};

const char* ota_result_name(OtaResult r);

}  // namespace tpc
