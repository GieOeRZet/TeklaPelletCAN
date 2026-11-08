#pragma once
// Router API urządzenia (REST) – czysty C++: ten sam kod działa na ESP (esp_http_server) i na hoście (testy, symulator).
#include <functional>
#include <map>
#include <string>
#include "clients.h"
#include "engine.h"

namespace tpc {

struct HttpRequest {
    std::string method;                              // GET, POST, DELETE
    std::string path;                                // bez zapytania
    std::string query;                               // po '?'
    std::string body;
    std::map<std::string, std::string> headers;      // klucze małymi literami
};

struct HttpResponse {
    int status = 200;
    std::string ctype = "application/json";
    std::string body;
};

struct ApiConfig {
    std::string prefix = "tekla";                    // prefiks entity_id wystawianych encji
    std::string node = "tekla_estyma";               // nazwa węzła w usługach karty
    std::string fw = "0.1.0";
    bool dev_key = false;
};

class Api {
public:
    using Clock = std::function<uint32_t()>;               // ms od startu
    using Random = std::function<std::string(size_t)>;     // losowe znaki hex (tokeny)
    using Hook = std::function<void()>;

    Api(Engine& engine, ClientStore& clients, ApiConfig cfg, Clock clock, Random rnd)
        : e_(engine), c_(clients), cfg_(std::move(cfg)), clock_(std::move(clock)), rnd_(std::move(rnd)) {}

    HttpResponse handle(const HttpRequest& r);
    void on_restart(Hook h) { restart_ = std::move(h); }

private:
    bool authorized(const HttpRequest& r) const;
    HttpResponse err(int status, const std::string& code) const;
    HttpResponse call(const HttpRequest& r);
    HttpResponse pair(const HttpRequest& r);
    std::string find_entity(const std::string& domain, const std::string& id) const;

    Engine& e_;
    ClientStore& c_;
    ApiConfig cfg_;
    Clock clock_;
    Random rnd_;
    Hook restart_;
};

}  // namespace tpc
