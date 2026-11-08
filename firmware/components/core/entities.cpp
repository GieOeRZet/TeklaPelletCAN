#include "entities.h"
#include <cctype>
#include <cstring>

namespace tpc {

std::string slugify(const std::string& s) {
    std::string out;
    bool sep = false;
    for (unsigned char c : s) {
        if (std::isalnum(c) && c < 128) {
            if (sep && !out.empty()) out.push_back('_');
            out.push_back((char)std::tolower(c));
            sep = false;
        } else {
            sep = true;
        }
    }
    return out;
}

const char* ha_domain(const char* d) {
    return strcmp(d, "text_sensor") == 0 ? "sensor" : d;
}

std::string entity_id(const Entity& e, const std::string& prefix) {
    return std::string(ha_domain(e.domain)) + "." + prefix + "_" + slugify(e.name);
}

}  // namespace tpc
