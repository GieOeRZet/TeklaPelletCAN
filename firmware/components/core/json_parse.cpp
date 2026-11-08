#include "json_parse.h"
#include <cstdlib>

namespace tpc {

namespace {
struct P {
    const std::string& t;
    size_t i = 0;
    explicit P(const std::string& text) : t(text) {}
    void ws() { while (i < t.size() && (t[i] == ' ' || t[i] == '\n' || t[i] == '\r' || t[i] == '\t')) i++; }
    bool lit(const char* w) {
        size_t n = 0; while (w[n]) n++;
        if (t.compare(i, n, w) == 0) { i += n; return true; }
        return false;
    }
    bool str(std::string& out) {
        if (i >= t.size() || t[i] != '"') return false;
        i++;
        while (i < t.size() && t[i] != '"') {
            char c = t[i++];
            if (c == '\\') {
                if (i >= t.size()) return false;
                char e = t[i++];
                switch (e) {
                    case 'n': out += '\n'; break; case 't': out += '\t'; break; case 'r': out += '\r'; break;
                    case 'b': out += '\b'; break; case 'f': out += '\f'; break;
                    case 'u': {
                        if (i + 4 > t.size()) return false;
                        unsigned cp = (unsigned)strtoul(t.substr(i, 4).c_str(), nullptr, 16); i += 4;
                        if (cp < 0x80) out += (char)cp;
                        else if (cp < 0x800) { out += (char)(0xC0 | (cp >> 6)); out += (char)(0x80 | (cp & 0x3F)); }
                        else { out += (char)(0xE0 | (cp >> 12)); out += (char)(0x80 | ((cp >> 6) & 0x3F)); out += (char)(0x80 | (cp & 0x3F)); }
                        break;
                    }
                    default: out += e;
                }
            } else out += c;
        }
        if (i >= t.size()) return false;
        i++;
        return true;
    }
    bool val(Json& j, int depth) {
        if (depth > 8) return false;
        ws();
        if (i >= t.size()) return false;
        char c = t[i];
        if (c == '{') {
            j.type = Json::Obj; i++; ws();
            if (i < t.size() && t[i] == '}') { i++; return true; }
            for (;;) {
                ws(); std::string k;
                if (!str(k)) return false;
                ws(); if (i >= t.size() || t[i] != ':') return false; i++;
                if (!val(j.o[k], depth + 1)) return false;
                ws();
                if (i < t.size() && t[i] == ',') { i++; continue; }
                if (i < t.size() && t[i] == '}') { i++; return true; }
                return false;
            }
        }
        if (c == '[') {
            j.type = Json::Arr; i++; ws();
            if (i < t.size() && t[i] == ']') { i++; return true; }
            for (;;) {
                j.a.emplace_back();
                if (!val(j.a.back(), depth + 1)) return false;
                ws();
                if (i < t.size() && t[i] == ',') { i++; continue; }
                if (i < t.size() && t[i] == ']') { i++; return true; }
                return false;
            }
        }
        if (c == '"') { j.type = Json::Str; return str(j.s); }
        if (lit("true")) { j.type = Json::Bool; j.b = true; return true; }
        if (lit("false")) { j.type = Json::Bool; j.b = false; return true; }
        if (lit("null")) { j.type = Json::Null; return true; }
        char* end = nullptr;
        const char* st = t.c_str() + i;
        double d = strtod(st, &end);
        if (end == st) return false;
        j.type = Json::Num; j.n = d; i += (size_t)(end - st);
        return true;
    }
};
}  // namespace

bool json_parse(const std::string& text, Json& out) {
    P p(text);
    out = Json();
    if (!p.val(out, 0)) return false;
    p.ws();
    return p.i == text.size();
}

}  // namespace tpc
