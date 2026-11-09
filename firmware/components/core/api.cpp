#include "api.h"
#include <cstdlib>
#include "json_parse.h"
#include "json_writer.h"

namespace tpc {

namespace {
const char* kActions[] = {"unlock", "set_setpoint", "set_boiler_mode", "set_param", "set_schedule", "set_output_pct",
                          "set_output", "test_refresh", "test_reset", "alarm_refresh", "param_refresh", "schedule_refresh",
                          "sdo_read", "sdo_scan_stop", "sdo_scan", "sdo_write", "sdo_poll_add", "sdo_poll_clear"};

bool ends_with(const std::string& s, const std::string& suf) {
    return s.size() >= suf.size() && s.compare(s.size() - suf.size(), suf.size(), suf) == 0;
}

std::string query_param(const std::string& q, const std::string& key) {
    size_t i = 0;
    while (i < q.size()) {
        size_t amp = q.find('&', i);
        std::string kv = q.substr(i, amp == std::string::npos ? std::string::npos : amp - i);
        size_t eq = kv.find('=');
        if (kv.substr(0, eq) == key) return eq == std::string::npos ? "" : kv.substr(eq + 1);
        if (amp == std::string::npos) break;
        i = amp + 1;
    }
    return "";
}

int http_status(Svc s) {
    switch (s) {
        case Svc::Ok: return 200;
        case Svc::BadArgs: return 400;
        case Svc::Mirror: case Svc::Disabled: case Svc::Level: return 403;
        case Svc::Range: return 422;
        case Svc::Rejected: case Svc::Blocked: return 409;
        case Svc::Unsupported: return 501;
        case Svc::UnknownAction: return 404;
    }
    return 500;
}
const char* svc_code(Svc s) {
    switch (s) {
        case Svc::Ok: return "ok"; case Svc::BadArgs: return "bad_args"; case Svc::Mirror: return "mirror";
        case Svc::Disabled: return "disabled"; case Svc::Level: return "level"; case Svc::Range: return "range";
        case Svc::Rejected: return "rejected"; case Svc::Blocked: return "blocked"; case Svc::Unsupported: return "unsupported";
        case Svc::UnknownAction: return "unknown_action";
    }
    return "error";
}
}  // namespace

HttpResponse Api::err(int status, const std::string& code) const {
    HttpResponse r;
    r.status = status;
    r.body = JsonWriter().begin_obj().kvb("ok", false).kv("error", code).end_obj().out();
    return r;
}

bool Api::authorized(const HttpRequest& r) const {
    std::string tok;
    auto a = r.headers.find("authorization");
    if (a != r.headers.end() && a->second.rfind("Bearer ", 0) == 0) tok = a->second.substr(7);
    auto x = r.headers.find("x-token");
    if (tok.empty() && x != r.headers.end()) tok = x->second;
    if (c_.valid_token(tok)) return true;
    if (!web_open()) return false;
    // Otwarty panel WWW: bez tokenu wolno tylko stronom serwowanym przez samo urządzenie. Przeglądarka dołącza Origin do żądań
    // zmieniających stan – inny origin (obca strona w Twojej przeglądarce) odrzucamy. Klienci spoza przeglądarki (curl) nie mają Origin.
    auto o = r.headers.find("origin");
    if (o == r.headers.end() || o->second.empty()) return true;
    std::string host_of_origin = o->second;
    const size_t sch = host_of_origin.find("://");
    if (sch != std::string::npos) host_of_origin = host_of_origin.substr(sch + 3);
    auto h = r.headers.find("host");
    return h != r.headers.end() && h->second == host_of_origin;
}

std::string Api::find_entity(const std::string& domain, const std::string& raw) const {
    std::string id = raw;
    const size_t dot = id.find('.');
    if (dot != std::string::npos) {
        if (id.substr(0, dot) != domain) return "";
        id = id.substr(dot + 1);
    }
    const Entity* best = nullptr;
    size_t best_len = 0;
    for (unsigned i = 0; i < kEntityCount; i++) {
        const Entity& e = kEntities[i];
        if (domain != ha_domain(e.domain)) continue;
        const std::string slug = slugify(e.name);
        if (id == slug || id == e.id || (ends_with(id, "_" + slug) && slug.size() > best_len)) {
            if (id == e.id || id == slug) return e.id;
            best = &e; best_len = slug.size();
        }
    }
    return best ? best->id : "";
}

HttpResponse Api::handle(const HttpRequest& r) {
    const uint32_t now = clock_();
    if (r.path == "/api/v1/info" && r.method == "GET") {
        InfoExtras x;
        x.fw = cfg_.fw; x.uptime_s = now / 1000; x.clients = (uint32_t)c_.list().size();
        x.dev_key = cfg_.dev_key; x.password_set = c_.has_password();
        x.time_s = hooks_.get_time ? hooks_.get_time() : 0;
        HttpResponse res; res.body = e_.info_json(x, now); return res;
    }
    if (r.path == "/api/v1/time" && r.method == "POST") {   // zegar od klienta (przeglądarka/aplikacja): ESP nie ma internetu ani RTC
        if (!c_.has_password()) return err(403, "setup_required");
        if (!authorized(r)) return err(401, "unauthorized");
        Json j;
        if (!json_parse(r.body, j)) return err(400, "bad_json");
        double s = j.has_num("epoch_ms") ? j.num("epoch_ms") / 1000.0 : j.has_num("epoch") ? j.num("epoch") : -1;
        if (s < 1700000000.0 || s > 4102444800.0) return err(422, "range");     // 2023-11 … 2100
        if (!hooks_.set_time) return err(501, "unsupported");
        hooks_.set_time((int64_t)s);
        HttpResponse res; res.body = JsonWriter().begin_obj().kvb("ok", true).key("time").num((double)(int64_t)s).end_obj().out(); return res;
    }
    if (r.path == "/api/v1/points" && r.method == "GET") { HttpResponse res; res.body = e_.points_json(); return res; }
    if (r.path == "/api/v1/state" && r.method == "GET") { HttpResponse res; res.body = e_.state_json(now); return res; }
    if (r.path == "/api/v1/states" && r.method == "GET") {
        std::string pf = query_param(r.query, "prefix");
        HttpResponse res; res.body = e_.states_json(pf.empty() ? cfg_.prefix : pf, now); return res;
    }
    if (r.path == "/api/v1/password" && r.method == "POST") {
        Json j;
        if (!json_parse(r.body, j)) return err(400, "bad_json");
        const std::string pw = j.str("password");
        if (pw.size() < 4) return err(400, "password_too_short");
        if (j.get("confirm") && j.str("confirm") != pw) return err(400, "password_mismatch");   // literówka w haśle
        if (c_.has_password() && !authorized(r)) return err(401, "unauthorized");   // zmiana hasła wymaga tokenu sparowanego klienta
        c_.set_password(pw);
        HttpResponse res; res.body = "{\"ok\":true}"; return res;
    }
    if (r.path == "/api/v1/pair" && r.method == "POST") return pair(r);
    if (r.path == "/api/v1/clients" && r.method == "GET") {
        if (!authorized(r)) return err(401, "unauthorized");
        JsonWriter w; w.begin_obj().key("clients").begin_arr();
        for (auto& c : c_.list()) w.begin_obj().kv("id", c.id).kv("name", c.name).end_obj();
        w.end_arr().end_obj();
        HttpResponse res; res.body = w.out(); return res;
    }
    if (r.path.rfind("/api/v1/clients/", 0) == 0 && r.method == "DELETE") {
        if (!authorized(r)) return err(401, "unauthorized");
        {
            if (!c_.remove(r.path.substr(16))) return err(404, "not_found");
            HttpResponse res; res.body = "{\"ok\":true}"; return res;
        }
    }
    if (r.path == "/api/v1/restart" && r.method == "POST") {
        if (!authorized(r)) return err(401, "unauthorized");
        if (restart_) restart_();
        HttpResponse res; res.body = "{\"ok\":true}"; return res;
    }
    {
        bool handled = false;
        HttpResponse pr = platform(r, handled);
        if (handled) return pr;
    }
    if (r.path == "/api/v1/call" && r.method == "POST") return call(r);
    if (r.path == "/api/v1/write" && r.method == "POST") {
        if (!c_.has_password()) return err(403, "setup_required");
        if (!authorized(r)) return err(401, "unauthorized");
        Json j;
        if (!json_parse(r.body, j) || !j.has_num("value")) return err(400, "bad_json");
        const WriteStatus s = e_.write(j.str("id"), j.num("value"), now);
        switch (s) {
            case WriteStatus::Ok: { HttpResponse res; res.body = "{\"ok\":true}"; return res; }
            case WriteStatus::UnknownPoint: return err(404, "unknown_point");
            case WriteStatus::NotWritable: return err(400, "not_writable");
            case WriteStatus::Mirror: return err(403, "mirror");
            case WriteStatus::Level: return err(403, "level");
            case WriteStatus::Range: return err(422, "range");
            case WriteStatus::Rejected: return err(409, "rejected");
        }
    }
    return err(404, "not_found");
}

HttpResponse Api::platform(const HttpRequest& r, bool& handled) {
    handled = true;
    auto ok = [] { HttpResponse res; res.body = "{\"ok\":true}"; return res; };
    auto wifi_from = [](const Json& j, WifiSettings& w) {
        w.ssid = j.str("ssid"); w.password = j.str("wifi_password", j.str("password"));
        const Json* d = j.get("dhcp");
        w.dhcp = !(d && d->type == Json::Bool && !d->b);
        w.ip = j.str("ip"); w.gateway = j.str("gateway"); w.mask = j.str("mask"); w.dns = j.str("dns");
    };
    const uint32_t now = clock_();

    if (r.path == "/api/v1/wifi/status" && r.method == "GET") {
        if (!hooks_.wifi_status) return err(501, "unsupported");
        WifiStatus s = hooks_.wifi_status();
        JsonWriter w;
        w.begin_obj().kv("state", s.state).kv("ssid", s.ssid).kv("ip", s.ip).kv("ap_ssid", s.ap_ssid).key("rssi").num(s.rssi);
        w.kvb("ap_active", s.ap_active).kv("trial", s.trial).kv("antenna", s.antenna).end_obj();
        HttpResponse res; res.body = w.out(); return res;
    }
    if (r.path == "/api/v1/wifi/scan" && r.method == "GET") {
        if (!hooks_.scan) return err(501, "unsupported");
        if (c_.has_password() && !authorized(r)) return err(401, "unauthorized");   // przed ustawieniem hasła skan dostępny dla portalu
        JsonWriter w; w.begin_obj().key("networks").begin_arr();
        for (auto& n : hooks_.scan()) w.begin_obj().kv("ssid", n.ssid).key("rssi").num(n.rssi).kvb("secure", n.secure).end_obj();
        w.end_arr().end_obj();
        HttpResponse res; res.body = w.out(); return res;
    }
    if (r.path == "/api/v1/setup" && r.method == "POST") {   // pierwsza konfiguracja: hasło urządzenia + Wi-Fi
        if (c_.has_password()) return err(403, "already_configured");
        Json j;
        if (!json_parse(r.body, j)) return err(400, "bad_json");
        const std::string pw = j.str("password"), cid = j.str("client_id", "portal");
        if (pw.size() < 4) return err(400, "password_too_short");
        if (j.get("confirm") && j.str("confirm") != pw) return err(400, "password_mismatch");
        c_.set_password(pw);
        ClientInfo ci; ci.id = cid; ci.name = j.str("name", "Portal"); ci.token = rnd_(32);
        c_.put(ci);
        WifiSettings w;
        if (!j.str("ssid").empty()) { wifi_from(j, w); if (hooks_.wifi_apply) hooks_.wifi_apply(w); }
        JsonWriter out; out.begin_obj().kvb("ok", true).kv("token", ci.token).end_obj();
        HttpResponse res; res.body = out.out(); return res;
    }
    if (r.path == "/api/v1/wifi" && r.method == "POST") {
        if (!authorized(r)) return err(401, "unauthorized");
        Json j;
        if (!json_parse(r.body, j) || j.str("ssid").empty()) return err(400, "bad_json");
        WifiSettings w; wifi_from(j, w);
        if (hooks_.wifi_apply) hooks_.wifi_apply(w);
        return ok();
    }
    if (r.path == "/api/v1/config" && r.method == "GET") {
        DeviceConfig cfg = hooks_.config_get ? hooks_.config_get() : DeviceConfig();
        JsonWriter w;
        w.begin_obj().kvb("mirror", cfg.mirror).kvb("write_enabled", cfg.write_enabled).kvb("demo", cfg.demo)
            .kvb("two_circuits", cfg.two_circuits).kvb("external_antenna", cfg.external_antenna).kvb("web_open", cfg.web_open).key("boiler_image").num(cfg.boiler_image).end_obj();
        HttpResponse res; res.body = w.out(); return res;
    }
    if (r.path == "/api/v1/config" && r.method == "POST") {
        if (!authorized(r)) return err(401, "unauthorized");
        Json j;
        if (!json_parse(r.body, j)) return err(400, "bad_json");
        DeviceConfig cfg = hooks_.config_get ? hooks_.config_get() : DeviceConfig();
        const DeviceConfig before = cfg;
        auto b = [&](const char* k, bool& dst) { const Json* v = j.get(k); if (v && v->type == Json::Bool) dst = v->b; };
        b("mirror", cfg.mirror); b("write_enabled", cfg.write_enabled); b("demo", cfg.demo); b("two_circuits", cfg.two_circuits); b("external_antenna", cfg.external_antenna); b("web_open", cfg.web_open);
        if (j.has_num("boiler_image")) { const int v = (int)j.num("boiler_image"); if (v >= 11 && v <= 14) cfg.boiler_image = (uint8_t)v; }
        if (hooks_.config_set) hooks_.config_set(cfg);
        // restart tylko dla ustawień czytanych przy starcie; wygląd (grafika kotła) i panel WWW działają od razu
        const bool restart = cfg.mirror != before.mirror || cfg.write_enabled != before.write_enabled || cfg.demo != before.demo ||
                             cfg.two_circuits != before.two_circuits || cfg.external_antenna != before.external_antenna;
        JsonWriter w; w.begin_obj().kvb("ok", true).kvb("restart_required", restart).end_obj();
        HttpResponse res; res.body = w.out(); return res;
    }
    if (r.path == "/api/v1/log" && r.method == "GET") {
        if (!hooks_.log_get) return err(501, "unsupported");
        HttpResponse res; res.ctype = "text/plain; charset=utf-8";
        res.body = hooks_.log_get(0);
        if (r.query.find("download=1") != std::string::npos)
            res.headers["Content-Disposition"] = "attachment; filename=\"teklapelletcan-" + e_.device_id_hex() + "-log.txt\"";
        return res;
    }
    if (r.path == "/api/v1/log" && r.method == "DELETE") {
        if (!authorized(r)) return err(401, "unauthorized");
        if (hooks_.log_clear) hooks_.log_clear();
        return ok();
    }
    if (r.path == "/api/v1/diag" && r.method == "GET") {
        JsonWriter w;
        w.begin_obj().kv("id", e_.device_id_hex()).kv("fw", cfg_.fw).key("uptime_s").num(now / 1000);
        std::string out = w.out();
        out.pop_back();   // zdejmij zamykające '}', dopisz pola
        out += ",\"engine\":" + e_.diag_json(now);
        out += ",\"platform\":" + (hooks_.diag_extra ? hooks_.diag_extra() : std::string("{}")) + "}";
        HttpResponse res; res.body = out; return res;
    }
    if (r.path == "/api/v1/export" && r.method == "GET") {   // raport do wklejenia/wysłania: diagnostyka + dziennik
        HttpResponse res; res.ctype = "text/plain; charset=utf-8";
        std::string rep = "=== TeklaPelletCAN raport ===\nid: " + e_.device_id_hex() + "\nfw: " + cfg_.fw + "\nuptime_s: " +
                          std::to_string(now / 1000) + "\n\n--- silnik ---\n" + e_.diag_json(now) + "\n";
        if (hooks_.diag_extra) rep += "\n--- platforma ---\n" + hooks_.diag_extra() + "\n";
        if (hooks_.log_get) rep += "\n--- dziennik ---\n" + hooks_.log_get(0);
        res.body = rep;
        res.headers["Content-Disposition"] = "attachment; filename=\"teklapelletcan-" + e_.device_id_hex() + "-raport.txt\"";
        return res;
    }
    if (r.path == "/api/v1/ota/rollback" && r.method == "POST") {
        if (!authorized(r)) return err(401, "unauthorized");
        if (!hooks_.ota_rollback) return err(501, "unsupported");
        const std::string e = hooks_.ota_rollback();
        if (!e.empty()) return err(409, e);
        return ok();
    }
    if (r.path == "/api/v1/factory_reset" && r.method == "POST") {
        if (!authorized(r)) return err(401, "unauthorized");
        Json j;
        if (!json_parse(r.body, j) || !j.get("confirm")) return err(400, "confirm_required");
        if (hooks_.factory_reset) hooks_.factory_reset();
        return ok();
    }
    handled = false;
    return HttpResponse();
}

HttpResponse Api::pair(const HttpRequest& r) {
    Json j;
    if (!json_parse(r.body, j)) return err(400, "bad_json");
    const std::string pw = j.str("password"), id = j.str("client_id"), name = j.str("name", "klient");
    if (id.empty() || id.size() > 64) return err(400, "bad_client_id");
    if (!c_.has_password()) return err(403, "setup_required");
    if (!c_.check_password(pw)) return err(401, "bad_password");
    // Ta sama instalacja nie dubluje wpisu: ponowne parowanie zwraca istniejący token (działający klient się nie psuje).
    ClientInfo ci;
    bool already = false;
    for (auto& c : c_.list()) if (c.id == id) { ci = c; already = true; }
    if (!already) { ci.id = id; ci.name = name; ci.token = rnd_(32); c_.put(ci); }
    JsonWriter w;
    w.begin_obj().kvb("ok", true).kv("token", ci.token).kvb("already_paired", already).end_obj();
    HttpResponse res; res.body = w.out(); return res;
}

HttpResponse Api::call(const HttpRequest& r) {
    if (!c_.has_password()) return err(403, "setup_required");
    if (!authorized(r)) return err(401, "unauthorized");
    Json j;
    if (!json_parse(r.body, j)) return err(400, "bad_json");
    const std::string domain = j.str("domain"), service = j.str("service");
    const Json* data = j.get("data");
    const uint32_t now = clock_();
    auto reply = [](Svc s) {
        HttpResponse res; res.status = http_status(s);
        res.body = JsonWriter().begin_obj().kvb("ok", s == Svc::Ok).kv("result", svc_code(s)).end_obj().out();
        return res;
    };
    if (domain == "teklapelletcan" || domain == "esphome") {
        std::string action;
        for (const char* a : kActions)
            if (service == a || ends_with(service, std::string("_") + a)) { action = a; break; }
        if (action.empty()) return reply(Svc::UnknownAction);
        Args args;
        if (data && data->type == Json::Obj)
            for (auto& kv : data->o) {
                if (kv.second.type == Json::Num) args[kv.first] = kv.second.n;
                else if (kv.second.type == Json::Str && !kv.second.s.empty()) args[kv.first] = strtod(kv.second.s.c_str(), nullptr);
                else if (kv.second.type == Json::Bool) args[kv.first] = kv.second.b ? 1 : 0;
            }
        if (action == "unlock") {   // PIN nie wraca do klienta; odpowiedź zawiera aktualny poziom
            e_.call(action, args, now);
            HttpResponse res; res.body = JsonWriter().begin_obj().kvb("ok", true).key("level").num(e_.level()).end_obj().out();
            return res;
        }
        return reply(e_.call(action, args, now));
    }
    if (domain == "button" || domain == "switch" || domain == "select") {
        std::string eid;
        if (data) {
            const Json* ent = data->get("entity_id");
            if (ent && ent->type == Json::Str) eid = ent->s;
            else if (ent && ent->type == Json::Arr && !ent->a.empty()) eid = ent->a[0].s;
        }
        const std::string yaml = find_entity(domain, eid);
        if (yaml.empty()) return err(404, "unknown_entity");
        if (domain == "button" && service == "press") return reply(e_.press(yaml, now));
        if (domain == "switch" && (service == "turn_on" || service == "turn_off")) {
            if (yaml == "restart") { if (restart_) restart_(); return reply(Svc::Ok); }
            return reply(e_.set_switch(yaml, service == "turn_on", now));
        }
        if (domain == "select" && service == "select_option") return reply(e_.select(yaml, data ? data->str("option") : "", now));
    }
    return reply(Svc::UnknownAction);
}

}  // namespace tpc
