// Serwer testowy trybu DEMO aplikacji: serwuje web/ i udostępnia DemoDevice (ten sam kod co w bibliotece JNI aplikacji Android)
// pod /__demo (POST JSON {method,path,query,authorization,body} -> {status,ctype,body}) – tak jak most JavaScript w WebView.
// Użycie: demo_server <port> <katalog_web>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include "../components/core/demo_device.h"
#include "../components/core/json_parse.h"
#include "../components/core/json_writer.h"

using namespace tpc;

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
    const int port = argc > 1 ? atoi(argv[1]) : 8098;
    const std::string web = argc > 2 ? argv[2] : "web";
    DemoDevice demo("0.0.0-demo");
    int srv = socket(AF_INET, SOCK_STREAM, 0);
    int one = 1; setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_addr.s_addr = inet_addr("127.0.0.1"); addr.sin_port = htons(port);
    if (bind(srv, (sockaddr*)&addr, sizeof addr) != 0 || listen(srv, 16) != 0) { perror("bind"); return 1; }
    fprintf(stderr, "[demo] nasluchuje na 127.0.0.1:%d, web=%s\n", port, web.c_str());
    for (;;) {
        timeval tv{0, 2000};
        fd_set fds; FD_ZERO(&fds); FD_SET(srv, &fds);
        const int ready = select(srv + 1, &fds, nullptr, nullptr, &tv);
        demo.tick();
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
        std::istringstream hs(buf.substr(0, hdr_end));
        std::string line; std::getline(hs, line);
        std::istringstream rl(line); std::string method, target, ver; rl >> method >> target >> ver;
        size_t clen = 0;
        while (std::getline(hs, line)) {
            const size_t c = line.find(':');
            if (c == std::string::npos) continue;
            std::string k = line.substr(0, c);
            for (auto& ch : k) ch = (char)tolower((unsigned char)ch);
            if (k == "content-length") clen = (size_t)atol(line.c_str() + c + 1);
        }
        std::string body = buf.substr(hdr_end + 4);
        while (body.size() < clen) {
            ssize_t n = recv(fd, tmp, sizeof tmp, 0);
            if (n <= 0) break;
            body.append(tmp, (size_t)n);
        }
        int status = 200; std::string ctype = "application/json", out;
        if (method == "POST" && target == "/__demo") {
            Json j; HttpRequest req;
            if (json_parse(body, j)) {
                req.method = j.str("method", "GET"); req.path = j.str("path"); req.query = j.str("query"); req.body = j.str("body");
                if (!j.str("authorization").empty()) req.headers["authorization"] = j.str("authorization");
            }
            HttpResponse r = demo.handle(req);
            JsonWriter w;
            w.begin_obj().key("status").num(r.status).kv("ctype", r.ctype).kv("body", r.body).end_obj();
            out = w.out();
        } else if (target.rfind("/api/", 0) == 0) {          // jak shouldInterceptRequest w aplikacji: /api/* trafia do wirtualnego urządzenia
            HttpRequest req;
            req.method = method;
            const size_t q = target.find('?');
            req.path = target.substr(0, q);
            if (q != std::string::npos) req.query = target.substr(q + 1);
            req.body = body;
            HttpResponse r = demo.handle(req);
            status = r.status; ctype = r.ctype; out = r.body;
        } else {
            std::string p = target.substr(0, target.find('?'));
            if (p == "/") p = "/index.html";
            if (p.find("..") != std::string::npos) p = "/index.html";
            std::ifstream f(web + p, std::ios::binary);
            if (!f) { status = 404; ctype = "text/plain"; out = "nie ma"; }
            else { std::ostringstream ss; ss << f.rdbuf(); out = ss.str(); ctype = mime(p); }
        }
        std::ostringstream o;
        o << "HTTP/1.1 " << status << " X\r\nContent-Type: " << ctype << "\r\nContent-Length: " << out.size()
          << "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n" << out;
        send_all(fd, o.str());
        close(fd);
    }
}
