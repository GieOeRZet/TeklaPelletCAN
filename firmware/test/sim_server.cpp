// Symulator urządzenia na hoście: prawdziwy Engine + Api (ten sam kod co na ESP) + atrapa kotła + prosty serwer HTTP.
// Użycie: sim_server <port> <katalog_web> [--password=HASLO]
// Służy do testów karty w przeglądarce i integracji HA bez sprzętu.
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <random>
#include <sstream>
#include "../components/core/api.h"
#include "fake_boiler.h"

using namespace tpc;

static uint32_t now_ms() {
    static const auto t0 = std::chrono::steady_clock::now();
    return (uint32_t)std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0).count();
}

static std::string mime(const std::string& p) {
    auto ends = [&](const char* e) { size_t n = strlen(e); return p.size() >= n && p.compare(p.size() - n, n, e) == 0; };
    if (ends(".html")) return "text/html; charset=utf-8";
    if (ends(".js")) return "text/javascript; charset=utf-8";
    if (ends(".css")) return "text/css";
    if (ends(".svg")) return "image/svg+xml";
    if (ends(".png")) return "image/png";
    if (ends(".webp")) return "image/webp";
    if (ends(".json")) return "application/json";
    return "application/octet-stream";
}

static void send_all(int fd, const std::string& s) {
    size_t off = 0;
    while (off < s.size()) { ssize_t n = send(fd, s.data() + off, s.size() - off, MSG_NOSIGNAL); if (n <= 0) return; off += (size_t)n; }
}

int main(int argc, char** argv) {
    const int port = argc > 1 ? atoi(argv[1]) : 8099;
    const std::string web = argc > 2 ? argv[2] : "web";
    std::string password;
    for (int i = 3; i < argc; i++) if (!strncmp(argv[i], "--password=", 11)) password = argv[i] + 11;

    FakeBoiler boiler;
    populate_demo(boiler);
    const uint8_t dev[6] = {0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6};
    EngineConfig cfg;
    cfg.boot_delay_ms = 500;
    cfg.boot_guard_ms = 0;
    cfg.fw = "sim-0.1.0";
    Engine engine(cfg, [&](const CanFrame& f) { return boiler.on_can(f); }, dev);
    MemoryClientStore clients;
    if (!password.empty()) clients.set_password(password);
    std::mt19937 rng(12345);
    ApiConfig acfg; acfg.fw = cfg.fw; acfg.dev_key = true;
    Api api(engine, clients, acfg, now_ms, [&](size_t n) {
        static const char* hex = "0123456789abcdef"; std::string s;
        for (size_t i = 0; i < n; i++) s += hex[rng() & 15];
        return s;
    });
    api.on_restart([] { fprintf(stderr, "[sim] restart\n"); });

    int srv = socket(AF_INET, SOCK_STREAM, 0);
    int one = 1; setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_addr.s_addr = inet_addr("127.0.0.1"); addr.sin_port = htons(port);
    if (bind(srv, (sockaddr*)&addr, sizeof addr) != 0 || listen(srv, 16) != 0) { perror("bind"); return 1; }
    fprintf(stderr, "[sim] nasluchuje na 127.0.0.1:%d, web=%s\n", port, web.c_str());

    for (;;) {
        // silnik tyka co ~2 ms, gdy brak połączeń
        timeval tv{0, 2000};
        fd_set fds; FD_ZERO(&fds); FD_SET(srv, &fds);
        const int ready = select(srv + 1, &fds, nullptr, nullptr, &tv);
        const uint32_t t = now_ms();
        engine.tick(t);
        auto frames = boiler.to_engine; boiler.to_engine.clear();
        for (auto& f : frames) engine.on_frame(f, t);
        if (ready <= 0) continue;

        int fd = accept(srv, nullptr, nullptr);
        if (fd < 0) continue;
        timeval rt{2, 0}; setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &rt, sizeof rt);
        std::string buf; char tmp[4096];
        size_t hdr_end = std::string::npos;
        while (hdr_end == std::string::npos) {
            ssize_t n = recv(fd, tmp, sizeof tmp, 0);
            if (n <= 0) break;
            buf.append(tmp, (size_t)n);
            hdr_end = buf.find("\r\n\r\n");
        }
        if (hdr_end == std::string::npos) { close(fd); continue; }
        HttpRequest req;
        std::istringstream hs(buf.substr(0, hdr_end));
        std::string line; std::getline(hs, line);
        std::istringstream rl(line); std::string target, ver; rl >> req.method >> target >> ver;
        const size_t q = target.find('?');
        req.path = target.substr(0, q);
        if (q != std::string::npos) req.query = target.substr(q + 1);
        size_t clen = 0;
        while (std::getline(hs, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            const size_t c = line.find(':');
            if (c == std::string::npos) continue;
            std::string k = line.substr(0, c), v = line.substr(c + 1);
            for (auto& ch : k) ch = (char)tolower((unsigned char)ch);
            while (!v.empty() && v[0] == ' ') v.erase(0, 1);
            req.headers[k] = v;
            if (k == "content-length") clen = (size_t)atol(v.c_str());
        }
        req.body = buf.substr(hdr_end + 4);
        while (req.body.size() < clen) {
            ssize_t n = recv(fd, tmp, sizeof tmp, 0);
            if (n <= 0) break;
            req.body.append(tmp, (size_t)n);
        }
        HttpResponse res;
        const std::string cors = "Access-Control-Allow-Origin: *\r\nAccess-Control-Allow-Headers: Authorization, X-Token, Content-Type\r\n"
                                 "Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS\r\n";
        if (req.method == "OPTIONS") { res.status = 204; res.body = ""; }
        else if (req.path.rfind("/api/", 0) == 0) { res = api.handle(req); }
        else {
            std::string p = req.path == "/" ? "/index.html" : req.path;
            if (p.find("..") != std::string::npos) p = "/index.html";
            std::ifstream f(web + p, std::ios::binary);
            if (!f) { res.status = 404; res.ctype = "text/plain"; res.body = "nie ma"; }
            else { std::ostringstream ss; ss << f.rdbuf(); res.body = ss.str(); res.ctype = mime(p); }
        }
        std::ostringstream out;
        out << "HTTP/1.1 " << res.status << " X\r\nContent-Type: " << res.ctype << "\r\nContent-Length: " << res.body.size()
            << "\r\n" << cors << "Cache-Control: no-store\r\nConnection: close\r\n\r\n" << res.body;
        send_all(fd, out.str());
        close(fd);
    }
}
