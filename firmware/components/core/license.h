#pragma once
// Kod odblokowujący pełną wersję: podpis ECDSA P-256, weryfikowany w urządzeniu (offline).
// Format opisany w docs/LICENCJA.md; generator: tools/license.py.
#include <cstddef>
#include <cstdint>
#include <string>

namespace tpc {

enum class Tier : uint8_t { Basic = 0, Full = 1 };

enum class LicenseResult : uint8_t {
    Ok,
    Format,       // zły format/prefiks/długość kodu
    Signature,    // podpis nie pasuje (kod sfałszowany lub z innego klucza)
    Device,       // kod wystawiony dla innego urządzenia
    Unsupported,  // nieznana wersja lub poziom
};

struct LicenseInfo {
    Tier tier = Tier::Basic;
    uint8_t device[6] = {0, 0, 0, 0, 0, 0};  // same zera = kod dla dowolnego urządzenia
    uint16_t serial = 0;
};

// Klucz publiczny wbudowany w firmware (license_pubkey.cpp, wygenerowany z klucza prywatnego).
extern const uint8_t kLicensePubKey[65];
extern const bool kLicenseDevKey;  // true = klucz testowy (buildy deweloperskie)

// Sprawdza kod dla urządzenia `device_id`. Przy Ok wypełnia `out`.
LicenseResult license_verify(const std::string& code, const uint8_t device_id[6],
                             const uint8_t pubkey[65], LicenseInfo& out);

// Pomocnicze (testowalne osobno).
bool base32_decode(const std::string& in, uint8_t* out, size_t& out_len, size_t max_len);

}  // namespace tpc
