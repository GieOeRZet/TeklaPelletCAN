#include "http_srv.h"
#include <cstring>
#include <string>
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/task.h"
#include "logging.h"
#include "ota.h"
#include "ota_idf.h"
#include "web_assets.h"
#include "wifi_mgr.h"

static const char* TAG = "http";
static tpc::Api* g_api = nullptr;
static SemaphoreHandle_t g_mu = nullptr;
constexpr size_t kMaxBody = 4096;

static const char* status_text(int c) {
    switch (c) {
        case 200: return "200 OK"; case 204: return "204 No Content"; case 302: return "302 Found";
        case 400: return "400 Bad Request"; case 401: return "401 Unauthorized"; case 403: return "403 Forbidden";
        case 404: return "404 Not Found"; case 409: return "409 Conflict"; case 413: return "413 Payload Too Large";
        case 422: return "422 Unprocessable Entity"; case 501: return "501 Not Implemented"; default: return "500 Internal Server Error";
    }
}

static std::string hdr(httpd_req_t* req, const char* name) {
    size_t n = httpd_req_get_hdr_value_len(req, name);
    if (!n) return "";
    std::string v(n + 1, '\0');
    if (httpd_req_get_hdr_value_str(req, name, &v[0], n + 1) != ESP_OK) return "";
    v.resize(n);
    return v;
}

static void cors(httpd_req_t* req) {
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Authorization, X-Token, X-Signature, Content-Type");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
}

static esp_err_t send_json(httpd_req_t* req, int code, const std::string& body) {
    cors(req);
    httpd_resp_set_status(req, status_text(code));
    httpd_resp_set_type(req, "application/json");
    return httpd_resp_send(req, body.data(), body.size());
}

static esp_err_t redirect_portal(httpd_req_t* req) {
    httpd_resp_set_status(req, status_text(302));
    httpd_resp_set_hdr(req, "Location", "http://10.77.77.1/portal.html");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_send(req, nullptr, 0);
}

static const WebAsset* find_asset(const std::string& path) {
    for (unsigned i = 0; i < kWebAssetCount; i++) if (path == kWebAssets[i].path) return &kWebAssets[i];
    return nullptr;
}

static bool is_captive_probe(const std::string& p) {
    static const char* probes[] = {"/generate_204", "/gen_204", "/hotspot-detect.html", "/library/test/success.html", "/connecttest.txt",
                                   "/ncsi.txt", "/redirect", "/canonical.html", "/success.txt", "/fwlink"};
    for (auto* s : probes) if (p == s) return true;
    return false;
}

static esp_err_t handle(httpd_req_t* req) {
    std::string uri = req->uri, query, path = uri;
    const size_t q = uri.find('?');
    if (q != std::string::npos) { path = uri.substr(0, q); query = uri.substr(q + 1); }
    const char* m = req->method == HTTP_GET ? "GET" : req->method == HTTP_POST ? "POST" : req->method == HTTP_DELETE ? "DELETE" : "OPTIONS";

    if (req->method == HTTP_OPTIONS) { cors(req); httpd_resp_set_status(req, status_text(204)); return httpd_resp_send(req, nullptr, 0); }

    const tpc::WifiStatus ws = g_wifi.status();
    const std::string host = hdr(req, "Host");
    const bool our_host = host.rfind("10.77.77.", 0) == 0 || host.rfind(g_wifi.hostname(), 0) == 0 || host == g_wifi.ip() ||
                          host.rfind(g_wifi.ip() + ":", 0) == 0;

    if (path.rfind("/api/", 0) == 0) {
        std::string body;
        if (req->method == HTTP_POST) {
            if (req->content_len > kMaxBody) return send_json(req, 413, "{\"ok\":false,\"error\":\"too_large\"}");
            body.resize(req->content_len);
            size_t got = 0;
            while (got < req->content_len) {
                int r = httpd_req_recv(req, &body[got], req->content_len - got);
                if (r == HTTPD_SOCK_ERR_TIMEOUT) continue;
                if (r <= 0) return ESP_FAIL;
                got += (size_t)r;
            }
        }
        tpc::HttpRequest r;
        r.method = m; r.path = path; r.query = query; r.body = body;
        for (const char* h : {"Authorization", "X-Token", "X-Signature", "Origin", "Host"}) {
            std::string v = hdr(req, h);
            if (!v.empty()) { std::string k = h; for (auto& c : k) c = (char)tolower((unsigned char)c); r.headers[k] = v; }
        }
        tpc::HttpResponse resp;
        xSemaphoreTake(g_mu, portMAX_DELAY);
        resp = g_api->handle(r);
        xSemaphoreGive(g_mu);
        cors(req);
        httpd_resp_set_status(req, status_text(resp.status));
        httpd_resp_set_type(req, resp.ctype.c_str());
        for (auto& h : resp.headers) httpd_resp_set_hdr(req, h.first.c_str(), h.second.c_str());
        httpd_resp_set_hdr(req, "Cache-Control", "no-store");
        return httpd_resp_send(req, resp.body.data(), resp.body.size());
    }

    // captive portal: w trybie AP wszystko, co nie jest naszym adresem, kieruj na portal
    if (ws.ap_active && (is_captive_probe(path) || (!host.empty() && !our_host))) return redirect_portal(req);

    if (path == "/") path = "/index.html";   // pierwsze wejście bez hasła przekierowuje strona (JS) na /portal.html
    const WebAsset* a = find_asset(path);
    if (!a) {
        if (ws.ap_active) return redirect_portal(req);
        httpd_resp_set_status(req, status_text(404));
        return httpd_resp_send(req, "nie ma", 6);
    }
    httpd_resp_set_type(req, a->mime);
    if (a->gzip) httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache");
    return httpd_resp_send(req, (const char*)a->data, a->size);
}

// Strumieniowa aktualizacja OTA: ciało = obraz .bin, nagłówek X-Signature = podpis ECDSA (128 hex).
static esp_err_t ota_handler(httpd_req_t* req) {
    tpc::HttpRequest r;
    r.method = "POST"; r.path = "/api/v1/ota";
    for (const char* h : {"Authorization", "X-Token", "X-Signature", "Origin", "Host"}) {
        std::string v = hdr(req, h);
        if (!v.empty()) { std::string k = h; for (auto& c : k) c = (char)tolower((unsigned char)c); r.headers[k] = v; }
    }
    xSemaphoreTake(g_mu, portMAX_DELAY);
    const bool ok_auth = g_api->is_authorized(r);
    xSemaphoreGive(g_mu);
    if (!ok_auth) { log_add("OTA: odmowa (brak/zly token)"); return send_json(req, 401, "{\"ok\":false,\"error\":\"unauthorized\"}"); }

    const std::string sig = r.headers.count("x-signature") ? r.headers["x-signature"] : "";
    EspOtaTarget target;
    tpc::OtaSession sess(target, tpc::kOtaPubKey, EspOtaTarget::max_image_size());
    tpc::OtaResult res = sess.begin(req->content_len, sig);
    if (res != tpc::OtaResult::Ok) {
        log_add(std::string("OTA: odrzucone na starcie: ") + tpc::ota_result_name(res));
        return send_json(req, 400, std::string("{\"ok\":false,\"error\":\"") + tpc::ota_result_name(res) + "\"}");
    }
    static uint8_t buf[2048];
    size_t left = req->content_len;
    int idle = 0;
    while (left > 0 && res == tpc::OtaResult::Ok) {
        int n = httpd_req_recv(req, (char*)buf, left < sizeof buf ? left : sizeof buf);
        if (n == HTTPD_SOCK_ERR_TIMEOUT) { if (++idle > 20) { sess.abort(); res = tpc::OtaResult::WriteFailed; } continue; }
        if (n <= 0) { sess.abort(); res = tpc::OtaResult::WriteFailed; break; }
        idle = 0;
        res = sess.feed(buf, (size_t)n);
        left -= (size_t)n;
    }
    if (res == tpc::OtaResult::Ok) res = sess.finish();
    log_add(std::string("OTA: wynik ") + tpc::ota_result_name(res));
    if (res != tpc::OtaResult::Ok) return send_json(req, 400, std::string("{\"ok\":false,\"error\":\"") + tpc::ota_result_name(res) + "\"}");
    send_json(req, 200, "{\"ok\":true}");
    vTaskDelay(pdMS_TO_TICKS(1500));
    esp_restart();
    return ESP_OK;
}

bool http_start(tpc::Api* api, SemaphoreHandle_t dev_mutex) {
    g_api = api;
    g_mu = dev_mutex;
    httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
    cfg.stack_size = 10240;
    cfg.max_uri_handlers = 8;
    cfg.max_open_sockets = 7;
    cfg.lru_purge_enable = true;
    cfg.uri_match_fn = httpd_uri_match_wildcard;
    cfg.recv_wait_timeout = 10;
    cfg.send_wait_timeout = 10;
    httpd_handle_t srv = nullptr;
    if (httpd_start(&srv, &cfg) != ESP_OK) { ESP_LOGE(TAG, "nie mozna uruchomic serwera HTTP"); return false; }
    httpd_uri_t ota = {"/api/v1/ota", HTTP_POST, ota_handler, nullptr};
    httpd_register_uri_handler(srv, &ota);
    for (httpd_method_t me : {HTTP_GET, HTTP_POST, HTTP_DELETE, HTTP_OPTIONS}) {
        httpd_uri_t u = {"/*", me, handle, nullptr};
        httpd_register_uri_handler(srv, &u);
    }
    log_add("HTTP: serwer uruchomiony (port 80)");
    return true;
}
