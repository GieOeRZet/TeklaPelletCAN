#include "version.h"
#include <cctype>

namespace tpc {

Version parse_version(const std::string& in) {
    Version v;
    size_t i = 0;
    if (i < in.size() && (in[i] == 'v' || in[i] == 'V')) i++;
    uint32_t parts[3] = {0, 0, 0};
    for (int p = 0; p < 3; p++) {
        if (i >= in.size() || !isdigit((unsigned char)in[i])) return Version{};
        uint32_t n = 0;
        while (i < in.size() && isdigit((unsigned char)in[i])) {
            n = n * 10 + (in[i] - '0');
            if (n > 65535) return Version{};
            i++;
        }
        parts[p] = n;
        if (p < 2) {
            if (i >= in.size() || in[i] != '.') return Version{};
            i++;
        }
    }
    if (i < in.size()) {
        if (in[i] != '-' || i + 1 >= in.size()) return Version{};
        v.prerelease = true;
    }
    v.major = parts[0]; v.minor = parts[1]; v.patch = parts[2];
    v.valid = true;
    return v;
}

int compare_versions(const Version& a, const Version& b) {
    if (a.valid != b.valid) return a.valid ? 1 : -1;
    if (!a.valid) return 0;
    if (a.major != b.major) return a.major < b.major ? -1 : 1;
    if (a.minor != b.minor) return a.minor < b.minor ? -1 : 1;
    if (a.patch != b.patch) return a.patch < b.patch ? -1 : 1;
    if (a.prerelease != b.prerelease) return a.prerelease ? -1 : 1;
    return 0;
}

bool is_update(const Version& current, const Version& candidate, bool allow_prerelease) {
    if (!candidate.valid) return false;
    if (candidate.prerelease && !allow_prerelease) return false;
    return compare_versions(current, candidate) < 0;
}

}  // namespace tpc
