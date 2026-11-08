#pragma once
// Minimalny pisarz JSON (bez zależności), wystarczający dla API urządzenia.
#include <cmath>
#include <cstdio>
#include <string>
#include <utility>

namespace tpc {

class JsonWriter {
public:
    JsonWriter& begin_obj() { sep(); s_ += '{'; first_ = true; return *this; }
    JsonWriter& end_obj() { s_ += '}'; first_ = false; return *this; }
    JsonWriter& begin_arr() { sep(); s_ += '['; first_ = true; return *this; }
    JsonWriter& end_arr() { s_ += ']'; first_ = false; return *this; }
    JsonWriter& key(const char* k) { sep(); str_raw(k); s_ += ':'; first_ = true; return *this; }
    JsonWriter& str(const std::string& v) { sep(); str_raw(v.c_str()); return *this; }
    JsonWriter& boolean(bool v) { sep(); s_ += v ? "true" : "false"; return *this; }
    JsonWriter& null() { sep(); s_ += "null"; return *this; }
    // Liczba w zwartej postaci: całkowite bez ułamka, reszta max 4 miejsca bez zer na końcu.
    static std::string fmt(double v) {
        if (!std::isfinite(v)) return "null";
        char b[40];
        if (v == std::floor(v) && std::fabs(v) < 1e12) snprintf(b, sizeof b, "%.0f", v);
        else {
            snprintf(b, sizeof b, "%.4f", v);
            size_t n = strlen_(b);
            while (n > 0 && b[n - 1] == '0') b[--n] = 0;
            if (n > 0 && b[n - 1] == '.') b[--n] = 0;
        }
        return b;
    }
    JsonWriter& num(double v) { sep(); s_ += fmt(v); return *this; }
    // skróty: klucz + wartość
    JsonWriter& kv(const char* k, const std::string& v) { return key(k).str(v); }
    JsonWriter& kv(const char* k, const char* v) { return key(k).str(v); }
    JsonWriter& kv(const char* k, double v) { return key(k).num(v); }
    JsonWriter& kvb(const char* k, bool v) { return key(k).boolean(v); }
    const std::string& out() const { return s_; }
    std::string take() { return std::move(s_); }      // bez kopiowania dużych odpowiedzi
    void reserve(size_t n) { s_.reserve(n); }

private:
    static size_t strlen_(const char* p) { size_t n = 0; while (p[n]) n++; return n; }
    void sep() { if (!first_) s_ += ','; first_ = false; }
    void str_raw(const char* v) {
        s_ += '"';
        for (const unsigned char* p = (const unsigned char*)v; *p; p++) {
            switch (*p) {
                case '"': s_ += "\\\""; break;
                case '\\': s_ += "\\\\"; break;
                case '\n': s_ += "\\n"; break;
                case '\r': s_ += "\\r"; break;
                case '\t': s_ += "\\t"; break;
                default:
                    if (*p < 0x20) { char b[8]; snprintf(b, sizeof b, "\\u%04x", *p); s_ += b; }
                    else s_ += (char)*p;
            }
        }
        s_ += '"';
    }
    std::string s_;
    bool first_ = true;
};

}  // namespace tpc
