#include "license.h"
#include <cctype>
#include <cstring>
#include "mbedtls/ecdsa.h"
#include "mbedtls/ecp.h"
#include "mbedtls/sha256.h"

namespace tpc {

bool base32_decode(const std::string& in, uint8_t* out, size_t& out_len, size_t max_len) {
    uint32_t buffer = 0;
    int bits = 0;
    size_t n = 0;
    for (char ch : in) {
        int v;
        if (ch >= 'A' && ch <= 'Z') v = ch - 'A';
        else if (ch >= '2' && ch <= '7') v = ch - '2' + 26;
        else return false;
        buffer = (buffer << 5) | v;
        bits += 5;
        if (bits >= 8) {
            bits -= 8;
            if (n >= max_len) return false;
            out[n++] = (buffer >> bits) & 0xFF;
        }
    }
    out_len = n;
    return true;
}

static bool is_zero(const uint8_t* p, size_t n) {
    for (size_t i = 0; i < n; i++) if (p[i]) return false;
    return true;
}

LicenseResult license_verify(const std::string& code, const uint8_t device_id[6],
                             const uint8_t pubkey[65], LicenseInfo& out) {
    // Normalizacja: wielkie litery, bez separatorów.
    std::string c;
    for (char ch : code) {
        if (ch == '-' || ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n') continue;
        c.push_back((char)toupper((unsigned char)ch));
    }
    if (c.size() != 4 + 120 || c.compare(0, 4, "TPC1") != 0) return LicenseResult::Format;

    uint8_t raw[80];
    size_t n = 0;
    if (!base32_decode(c.substr(4), raw, n, sizeof(raw)) || n != 75) return LicenseResult::Format;
    const uint8_t* payload = raw;      // 11 B
    const uint8_t* sig = raw + 11;     // 64 B (r||s)
    if (payload[0] != 0x54) return LicenseResult::Format;
    if (payload[1] != 1 || payload[2] != 1) return LicenseResult::Unsupported;

    // SHA-256("TPC-LIC1" || payload)
    uint8_t msg[8 + 11];
    memcpy(msg, "TPC-LIC1", 8);
    memcpy(msg + 8, payload, 11);
    uint8_t hash[32];
    mbedtls_sha256(msg, sizeof(msg), hash, 0);

    mbedtls_ecp_group grp;
    mbedtls_ecp_point Q;
    mbedtls_mpi r, s;
    mbedtls_ecp_group_init(&grp);
    mbedtls_ecp_point_init(&Q);
    mbedtls_mpi_init(&r);
    mbedtls_mpi_init(&s);
    LicenseResult res = LicenseResult::Signature;
    if (mbedtls_ecp_group_load(&grp, MBEDTLS_ECP_DP_SECP256R1) == 0 &&
        mbedtls_ecp_point_read_binary(&grp, &Q, pubkey, 65) == 0 &&
        mbedtls_mpi_read_binary(&r, sig, 32) == 0 &&
        mbedtls_mpi_read_binary(&s, sig + 32, 32) == 0 &&
        mbedtls_ecdsa_verify(&grp, hash, sizeof(hash), &Q, &r, &s) == 0) {
        res = LicenseResult::Ok;
    }
    mbedtls_ecp_group_free(&grp);
    mbedtls_ecp_point_free(&Q);
    mbedtls_mpi_free(&r);
    mbedtls_mpi_free(&s);
    if (res != LicenseResult::Ok) return res;

    const uint8_t* bound = payload + 3;
    if (!is_zero(bound, 6) && memcmp(bound, device_id, 6) != 0) return LicenseResult::Device;

    out.tier = Tier::Full;
    memcpy(out.device, bound, 6);
    out.serial = (uint16_t)((payload[9] << 8) | payload[10]);
    return LicenseResult::Ok;
}

}  // namespace tpc
