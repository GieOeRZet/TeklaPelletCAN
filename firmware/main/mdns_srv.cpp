#include "mdns_srv.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/inet.h"
#include "lwip/sockets.h"
#include "mdns.h"
#include "wifi_mgr.h"

static const char* TAG = "mdns";
static tpc::MdnsConfig g_cfg;

static void task(void*) {
    int s = -1;
    uint32_t last_ip = 0;
    int64_t last_announce = 0;
    uint8_t buf[512];
    for (;;) {
        const std::string ip = g_wifi.online() ? g_wifi.ip() : "";
        uint32_t ipv4 = 0;
        if (!ip.empty()) ipv4 = ntohl(inet_addr(ip.c_str()));
        if (ipv4 == 0) {                         // brak sieci STA: zamknij gniazdo i czekaj
            if (s >= 0) { close(s); s = -1; }
            last_ip = 0;
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }
        if (s < 0 || ipv4 != last_ip) {
            if (s >= 0) close(s);
            s = socket(AF_INET, SOCK_DGRAM, 0);
            int one = 1;
            setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
            sockaddr_in a = {};
            a.sin_family = AF_INET; a.sin_port = htons(5353); a.sin_addr.s_addr = htonl(INADDR_ANY);
            if (bind(s, (sockaddr*)&a, sizeof a) != 0) { ESP_LOGW(TAG, "bind 5353 nieudany"); close(s); s = -1; vTaskDelay(pdMS_TO_TICKS(3000)); continue; }
            ip_mreq mr = {};
            mr.imr_multiaddr.s_addr = inet_addr("224.0.0.251");
            mr.imr_interface.s_addr = inet_addr(ip.c_str());
            setsockopt(s, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mr, sizeof mr);
            timeval tv{1, 0};
            setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
            last_ip = ipv4;
            g_cfg.ipv4 = ipv4;
            last_announce = 0;
        }
        const int64_t now = esp_timer_get_time() / 1000000;
        sockaddr_in grp = {};
        grp.sin_family = AF_INET; grp.sin_port = htons(5353); grp.sin_addr.s_addr = inet_addr("224.0.0.251");
        if (now - last_announce >= 60) {          // ogłoszenie przy starcie/zmianie IP i co minutę
            auto pkt = tpc::mdns_announce(g_cfg);
            sendto(s, pkt.data(), pkt.size(), 0, (sockaddr*)&grp, sizeof grp);
            last_announce = now;
        }
        sockaddr_in from; socklen_t fl = sizeof from;
        int n = recvfrom(s, buf, sizeof buf, 0, (sockaddr*)&from, &fl);
        if (n > 0) {
            auto resp = tpc::mdns_respond(g_cfg, buf, (size_t)n);
            if (!resp.empty()) sendto(s, resp.data(), resp.size(), 0, (sockaddr*)&grp, sizeof grp);
        }
    }
}

void mdns_start(const std::string& host, const std::string& instance, const std::string& id_hex, const std::string& fw) {
    g_cfg.host = host;
    g_cfg.instance = instance;
    g_cfg.port = 80;
    g_cfg.txt = {"id=" + id_hex, "fw=" + fw, "api=1"};
    xTaskCreate(task, "mdns", 4096, nullptr, 4, nullptr);
}
