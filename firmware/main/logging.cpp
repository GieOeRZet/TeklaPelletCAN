#include "logging.h"
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include "esp_attr.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "logring.h"

static RTC_NOINIT_ATTR uint8_t g_ring_mem[8192];
static tpc::LogRing* g_ring = nullptr;
static SemaphoreHandle_t g_mu = nullptr;
static vprintf_like_t g_prev = nullptr;

static void ring_append(const char* s, size_t n) {
    if (!g_ring || !g_mu) return;
    if (xSemaphoreTake(g_mu, pdMS_TO_TICKS(20)) != pdTRUE) return;   // nigdy nie blokuj logowania
    g_ring->append(s, n);
    xSemaphoreGive(g_mu);
}

static int hook(const char* fmt, va_list ap) {
    char buf[256];
    va_list ap2;
    va_copy(ap2, ap);
    int n = vsnprintf(buf, sizeof buf, fmt, ap2);
    va_end(ap2);
    if (n > 0) {
        size_t len = (size_t)n < sizeof buf ? (size_t)n : sizeof buf - 1;
        // usuń sekwencje kolorów ANSI (ESC[...m)
        char clean[256];
        size_t j = 0;
        for (size_t i = 0; i < len && j < sizeof clean - 1; i++) {
            if (buf[i] == 0x1B) { while (i < len && buf[i] != 'm') i++; continue; }
            clean[j++] = buf[i];
        }
        ring_append(clean, j);
    }
    return g_prev ? g_prev(fmt, ap) : vprintf(fmt, ap);
}

void log_init() {
    g_mu = xSemaphoreCreateMutex();
    static tpc::LogRing ring(g_ring_mem, sizeof g_ring_mem);
    g_ring = &ring;
    g_prev = esp_log_set_vprintf(hook);
    // Bufor RTC jest mały (8 KB): wycisz gadatliwe komponenty, żeby zmieściło się to, co ważne
    esp_log_level_set("*", ESP_LOG_INFO);
    esp_log_level_set("wifi", ESP_LOG_ERROR);   // sterownik Wi-Fi zalewa log wieloliniowymi ostrzeżeniami
    for (const char* t : {"wifi_init", "phy_init", "esp_netif_handlers", "net80211", "pp", "esp_image", "boot", "cpu_start", "httpd_txrx"})
        esp_log_level_set(t, ESP_LOG_ERROR);
}

void log_add(const std::string& line) { ESP_LOGI("tpc", "%s", line.c_str()); }   // hak vprintf zapisuje też do bufora
std::string log_get(size_t n) {
    if (!g_ring || !g_mu) return "";
    std::string s;
    if (xSemaphoreTake(g_mu, pdMS_TO_TICKS(200)) == pdTRUE) { s = n ? g_ring->tail(n) : g_ring->dump(); xSemaphoreGive(g_mu); }
    return s;
}
void log_clear() { if (g_ring && g_mu && xSemaphoreTake(g_mu, pdMS_TO_TICKS(200)) == pdTRUE) { g_ring->clear(); xSemaphoreGive(g_mu); } }
bool log_survived() { return g_ring && g_ring->survived(); }
