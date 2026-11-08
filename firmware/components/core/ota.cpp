#include "ota.h"
#include <cstring>
#include "mbedtls/ecdsa.h"
#include "mbedtls/ecp.h"
#include "mbedtls/version.h"

namespace tpc {

namespace {
// mbedTLS 2.x (host, testy) i 3.x (ESP-IDF 5.x) różnią się nazwami funkcji SHA-256.
#if MBEDTLS_VERSION_MAJOR >= 3
inline void sha_start(mbedtls_sha256_context* c) { mbedtls_sha256_starts(c, 0); }
inline void sha_update(mbedtls_sha256_context* c, const uint8_t* d, size_t n) { mbedtls_sha256_update(c, d, n); }
inline void sha_finish(mbedtls_sha256_context* c, uint8_t* o) { mbedtls_sha256_finish(c, o); }
#else
inline void sha_start(mbedtls_sha256_context* c) { mbedtls_sha256_starts_ret(c, 0); }
inline void sha_update(mbedtls_sha256_context* c, const uint8_t* d, size_t n) { mbedtls_sha256_update_ret(c, d, n); }
inline void sha_finish(mbedtls_sha256_context* c, uint8_t* o) { mbedtls_sha256_finish_ret(c, o); }
#endif
}  // namespace

namespace {
bool hex_to_bytes(const std::string& h, uint8_t* out, size_t n) {
    if (h.size() != n * 2) return false;
    for (size_t i = 0; i < n; i++) {
        auto d = [](char c) -> int { return c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10 : c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1; };
        int a = d(h[2 * i]), b = d(h[2 * i + 1]);
        if (a < 0 || b < 0) return false;
        out[i] = (uint8_t)(a * 16 + b);
    }
    return true;
}
}  // namespace

OtaSession::~OtaSession() { abort(); }

void OtaSession::abort() {
    if (active_) t_.abort();
    if (sha_init_) { mbedtls_sha256_free(&sha_); sha_init_ = false; }
    active_ = false;
}

OtaResult OtaSession::begin(size_t total, const std::string& sig_hex) {
    if (active_) return OtaResult::Busy;
    embedded_ = sig_hex.empty();
    if (total < 64 + (embedded_ ? kSigTrailer : 0) || total > max_ + (embedded_ ? kSigTrailer : 0)) return OtaResult::TooBig;
    if (!embedded_ && !hex_to_bytes(sig_hex, sig_, 64)) return OtaResult::BadSignature;
    image_len_ = embedded_ ? total - kSigTrailer : total;
    trailer_got_ = 0;
    if (!t_.begin(total)) return OtaResult::WriteFailed;
    mbedtls_sha256_init(&sha_);
    sha_start(&sha_);
    sha_init_ = true;
    total_ = total; got_ = 0;
    active_ = true;
    return OtaResult::Ok;
}

OtaResult OtaSession::feed(const uint8_t* data, size_t len) {
    if (!active_) return OtaResult::NotStarted;
    if (got_ + len > total_) { abort(); return OtaResult::TooBig; }
    const size_t base = got_;                 // pozycja pierwszego bajtu tego kawałka w pliku
    // Pakiet z podpisem wbudowanym: bajty od image_len_ to trailer (znacznik + podpis) – nie trafiają na partycję ani do skrótu.
    if (embedded_ && base + len > image_len_) {
        const size_t img_part = base < image_len_ ? image_len_ - base : 0;
        const size_t tr_part = len - img_part;
        memcpy(trailer_ + trailer_got_, data + img_part, tr_part);
        trailer_got_ += tr_part;
        got_ += tr_part;
        len = img_part;
        if (len == 0) return OtaResult::Ok;
    }
    // nagłówek obrazu ESP: bajt 0 = 0xE9, bajty 12..13 = chip_id
    for (size_t i = 0; i < len && base + i < sizeof head_; i++) head_[base + i] = data[i];
    if (base < sizeof head_ && base + len >= sizeof head_) {
        const uint16_t chip = (uint16_t)(head_[12] | (head_[13] << 8));
        if (head_[0] != 0xE9 || chip != chip_) { abort(); return OtaResult::BadImage; }
    }
    sha_update(&sha_, data, len);
    if (!t_.write(data, len)) { abort(); return OtaResult::WriteFailed; }
    got_ += len;
    return OtaResult::Ok;
}

OtaResult OtaSession::finish() {
    if (!active_) return OtaResult::NotStarted;
    if (got_ != total_) { abort(); return OtaResult::BadImage; }
    if (embedded_) {   // podpis z końca pliku
        if (memcmp(trailer_, kSigMagic, 8) != 0) { abort(); return OtaResult::BadImage; }   // plik bez podpisu
        memcpy(sig_, trailer_ + 8, 64);
    }
    uint8_t hash[32];
    sha_finish(&sha_, hash);
    mbedtls_sha256_free(&sha_); sha_init_ = false;

    mbedtls_ecp_group grp; mbedtls_ecp_point Q; mbedtls_mpi r, s;
    mbedtls_ecp_group_init(&grp); mbedtls_ecp_point_init(&Q); mbedtls_mpi_init(&r); mbedtls_mpi_init(&s);
    bool ok = mbedtls_ecp_group_load(&grp, MBEDTLS_ECP_DP_SECP256R1) == 0 &&
              mbedtls_ecp_point_read_binary(&grp, &Q, pub_, 65) == 0 &&
              mbedtls_mpi_read_binary(&r, sig_, 32) == 0 && mbedtls_mpi_read_binary(&s, sig_ + 32, 32) == 0 &&
              mbedtls_ecdsa_verify(&grp, hash, sizeof hash, &Q, &r, &s) == 0;
    mbedtls_ecp_group_free(&grp); mbedtls_ecp_point_free(&Q); mbedtls_mpi_free(&r); mbedtls_mpi_free(&s);
    if (!ok) { abort(); return OtaResult::BadSignature; }
    active_ = false;               // od teraz target.end() decyduje o wyniku
    if (!t_.end()) return OtaResult::WriteFailed;
    return OtaResult::Ok;
}

const char* ota_result_name(OtaResult r) {
    switch (r) {
        case OtaResult::Ok: return "ok"; case OtaResult::Busy: return "busy"; case OtaResult::BadSignature: return "bad_signature";
        case OtaResult::BadImage: return "bad_image"; case OtaResult::WriteFailed: return "write_failed";
        case OtaResult::TooBig: return "too_big"; case OtaResult::NotStarted: return "not_started";
    }
    return "error";
}

}  // namespace tpc
