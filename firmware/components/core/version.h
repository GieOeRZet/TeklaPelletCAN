#pragma once
// Wersje w formacie MAJOR.MINOR.PATCH (opcjonalnie z prefiksem "v" i sufiksem "-beta1").
#include <cstdint>
#include <string>

namespace tpc {

struct Version {
    bool valid = false;
    uint16_t major = 0, minor = 0, patch = 0;
    bool prerelease = false;  // sufiks "-xxx"
};

Version parse_version(const std::string& s);

// -1 gdy a < b, 0 gdy równe, 1 gdy a > b. Wersja stabilna > prerelease tej samej liczby.
// Niepoprawna wersja jest traktowana jako starsza od poprawnej.
int compare_versions(const Version& a, const Version& b);

// Czy `candidate` jest nowsza od `current` i nadaje się do instalacji
// (prerelease tylko gdy allow_prerelease).
bool is_update(const Version& current, const Version& candidate, bool allow_prerelease);

}  // namespace tpc
