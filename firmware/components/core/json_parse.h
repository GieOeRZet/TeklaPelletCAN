#pragma once
// Minimalny parser JSON (obiekty, tablice, napisy, liczby, bool, null) do ciał żądań API.
#include <map>
#include <string>
#include <vector>

namespace tpc {

struct Json {
    enum Type { Null, Bool, Num, Str, Obj, Arr } type = Null;
    bool b = false;
    double n = 0;
    std::string s;
    std::map<std::string, Json> o;
    std::vector<Json> a;

    const Json* get(const std::string& k) const {
        auto it = o.find(k);
        return it == o.end() ? nullptr : &it->second;
    }
    std::string str(const std::string& k, const std::string& def = "") const {
        const Json* j = get(k);
        return j && j->type == Str ? j->s : def;
    }
    double num(const std::string& k, double def = 0) const {
        const Json* j = get(k);
        return j && j->type == Num ? j->n : def;
    }
    bool has_num(const std::string& k) const { const Json* j = get(k); return j && j->type == Num; }
};

// Zwraca false przy błędzie składni. Głębokość ograniczona (ochrona stosu).
bool json_parse(const std::string& text, Json& out);

}  // namespace tpc
