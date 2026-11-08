// TeklaPelletCAN – firmware urządzenia: Wi-Fi z portalem, serwer HTTP (karta + API), mDNS, OTA z podpisem,
// silnik kotła (CAN/MCP2515 albo tryb demo), dziennik w pamięci RTC.
#include <cstdio>
#include <cstring>
#include <string>
#include "api.h"
#include "engine.h"
#include "esp_app_desc.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_ota_ops.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "firstboot.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "http_srv.h"
#include "logging.h"
#include "mcp2515.h"
#include "mdns_srv.h"
#include "ota_idf.h"
#include "sim_boiler.h"
#include "spi_idf.h"
#include "store.h"
#include "wifi_mgr.h"

static const char* TAG = "tpc";

// XIAO ESP32-C6 + Seeed CAN Bus Breakout (jak w PelletCAN)
constexpr int PIN_SCK = 19, PIN_MISO = 20, PIN_MOSI = 18, PIN_CS = 17;

static uint32_t now_ms() { return (uint32_t)(esp_timer_get_time() / 1000); }

static const char* reset_reason_name() {
    switch (esp_reset_reason()) {
        case ESP_RST_POWERON: return "power-on"; case ESP_RST_SW: return "software"; case ESP_RST_PANIC: return "PANIKA";
        case ESP_RST_INT_WDT: return "watchdog-int"; case ESP_RST_TASK_WDT: return "watchdog-task"; case ESP_RST_WDT: return "watchdog";
        case ESP_RST_BROWNOUT: return "brownout"; case ESP_RST_DEEPSLEEP: return "deepsleep"; case ESP_RST_EXT: return "external";
        default: return "inne";
    }
}

static void restart_later(uint32_t ms) {
    struct A { uint32_t ms; };
    static A a; a.ms = ms;
    xTaskCreate([](void* p) { vTaskDelay(pdMS_TO_TICKS(((A*)p)->ms)); esp_restart(); }, "restart", 2048, &a, 5, nullptr);
}

static NvsStore g_store;
static Settings g_set;
static SemaphoreHandle_t g_dev_mu;

extern "C" void app_main(void) {
    log_init();
    const esp_app_desc_t* desc = esp_app_get_description();
    const std::string fw = desc->version;
    log_add(std::string("=== START fw=") + fw + " reset=" + reset_reason_name() + (log_survived() ? " (dziennik sprzed restartu powyzej)" : "") + " ===");

    if (!g_store.init()) log_add("NVS: BLAD inicjalizacji");
    g_set = g_store.load();

    // Dane wpisane w plik .bin skryptem patch_firstboot.py (Wi-Fi + hasło). Stosowane, gdy numer wsadu jest NOWY – czyli przy
    // pierwszym starcie albo po ponownym wgraniu pliku z innymi danymi (zdalne odzyskanie po zapomnianym haśle lub zmianie sieci).
    const uint32_t fb_serial = (uint32_t)g_firstboot.serial[0] | ((uint32_t)g_firstboot.serial[1] << 8) |
                               ((uint32_t)g_firstboot.serial[2] << 16) | ((uint32_t)g_firstboot.serial[3] << 24);
    if (g_firstboot.valid && fb_serial != g_set.fb_serial) {
        if (g_firstboot.ssid[0]) {
            g_set.ssid = (const char*)g_firstboot.ssid; g_set.pass = (const char*)g_firstboot.pass;
            g_set.dhcp = g_firstboot.dhcp != 0;
            g_set.ip = (const char*)g_firstboot.ip; g_set.gw = (const char*)g_firstboot.gw;
            g_set.mask = (const char*)g_firstboot.mask; g_set.dns = (const char*)g_firstboot.dns;
            log_add(std::string("DANE Z PLIKU: siec Wi-Fi '") + g_set.ssid + "' (wsad " + std::to_string(fb_serial) + ")");
            g_store.save_wifi(g_set);
        }
        if (g_firstboot.dev_pass[0]) {
            g_store.set_password((const char*)g_firstboot.dev_pass);
            log_add("DANE Z PLIKU: ustawiono haslo urzadzenia");
        }
        g_set.fb_serial = fb_serial;
        g_store.save_fb_serial(fb_serial);
    }

    g_dev_mu = xSemaphoreCreateMutex();
    if (g_set.cfg.external_antenna) {   // XIAO ESP32-C6: GPIO3 = zasilanie przełącznika RF (niski), GPIO14 = wybór anteny (wysoki = zewnętrzna U.FL)
        gpio_config_t ac = {};
        ac.pin_bit_mask = (1ULL << 3) | (1ULL << 14); ac.mode = GPIO_MODE_OUTPUT;
        gpio_config(&ac);
        gpio_set_level(GPIO_NUM_3, 0);
        vTaskDelay(pdMS_TO_TICKS(100));
        gpio_set_level(GPIO_NUM_14, 1);
        log_add("Antena: zewnetrzna (U.FL)");
    }
    g_wifi.start(g_set, g_store);

    uint8_t mac[6];
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    tpc::EngineConfig ec;
    ec.access.mirror = g_set.cfg.mirror;
    ec.access.write_enabled = g_set.cfg.write_enabled;
    ec.two_circuits = g_set.cfg.two_circuits;
    ec.fw = fw;
    static tpc::SimBoiler sim;
    static IdfSpi spi;
    static tpc::Mcp2515 can(spi);
    static bool spi_ok = false, can_ok_hw = false;
    const bool demo = g_set.cfg.demo;
    if (demo) { tpc::populate_demo(sim); log_add("TRYB DEMO: symulator kotla (bez magistrali CAN)"); }

    static SemaphoreHandle_t can_mu = xSemaphoreCreateMutex();      // dostęp do SPI/MCP2515 (zadanie odbioru + silnik)
    static QueueHandle_t rxq = xQueueCreate(256, sizeof(tpc::CanFrame));
    static uint32_t rx_dropped = 0, rx_total = 0, mcp_overflows = 0;
    static tpc::Engine engine(ec, [](const tpc::CanFrame& f) {
        if (g_set.cfg.demo) return sim.on_can(f);
        if (!can_ok_hw) return false;
        xSemaphoreTake(can_mu, portMAX_DELAY);
        const bool ok = can.send(f);
        xSemaphoreGive(can_mu);
        return ok;
    }, mac);
    engine.set_logger([](const std::string& l) { log_add(l); });
    log_add(std::string("Silnik: tryb ") + (ec.access.mirror ? "TYLKO ODCZYT" : "zapis wlaczony") + ", id " + engine.device_id_hex() +
            (demo ? ", demo" : ", CAN"));

    tpc::ApiConfig ac;
    ac.fw = fw;
    ac.prefix = "tekla";
    ac.dev_key = tpc::kOtaDevKey;
    static tpc::Api api(engine, g_store, ac, [] { return now_ms(); }, [](size_t n) {
        std::string s;
        for (size_t i = 0; i < n; i++) { char b[3]; snprintf(b, sizeof b, "%02x", (unsigned)(esp_random() & 0xFF)); s += b; }
        return s;
    });
    api.on_restart([] { log_add("Restart na zadanie uzytkownika"); restart_later(800); });

    tpc::ApiHooks hk;
    hk.scan = [] {
        xSemaphoreGive(g_dev_mu);                  // skan trwa kilka sekund – nie blokuj silnika
        auto r = g_wifi.scan();
        xSemaphoreTake(g_dev_mu, portMAX_DELAY);
        return r;
    };
    hk.wifi_apply = [](const tpc::WifiSettings& w) { g_wifi.apply(w); };
    hk.wifi_status = [] { return g_wifi.status(); };
    hk.config_get = [] { return g_set.cfg; };
    hk.config_set = [](const tpc::DeviceConfig& c) {
        g_set.cfg = c;
        g_store.save_cfg(c, g_set.firstboot_done);
        log_add(std::string("Konfiguracja zapisana: mirror=") + (c.mirror ? "1" : "0") + " write=" + (c.write_enabled ? "1" : "0") +
                " demo=" + (c.demo ? "1" : "0") + " two_circuits=" + (c.two_circuits ? "1" : "0") + " (wymaga restartu)");
    };
    hk.ota_rollback = [] { return ota_rollback_previous(); };
    hk.log_get = [](size_t n) { return log_get(n); };
    hk.log_clear = [] { log_clear(); };
    hk.factory_reset = [] { log_add("RESET FABRYCZNY"); g_store.factory_reset(); restart_later(800); };
    hk.diag_extra = [fw]() {
        char b[600];
        const esp_partition_t* run = esp_ota_get_running_partition();
        snprintf(b, sizeof b,
                 "{\"reset_reason\":\"%s\",\"heap_free\":%u,\"heap_min\":%u,\"wifi_ssid\":\"%s\",\"wifi_ip\":\"%s\",\"wifi_rssi\":%d,"
                 "\"ap_ssid\":\"%s\",\"partition\":\"%s\",\"ota\":%s,\"demo\":%s,\"mcp2515\":%s,\"log_survived\":%s,\"idf\":\"%s\"}",
                 reset_reason_name(), (unsigned)esp_get_free_heap_size(), (unsigned)esp_get_minimum_free_heap_size(),
                 g_wifi.status().ssid.c_str(), g_wifi.ip().c_str(), g_wifi.status().rssi, g_wifi.ap_ssid().c_str(),
                 run ? run->label : "?", ota_status_text().c_str(), g_set.cfg.demo ? "true" : "false", can_ok_hw ? "true" : "false",
                 log_survived() ? "true" : "false", esp_get_idf_version());
        return std::string(b);
    };
    api.set_hooks(hk);

    http_start(&api, g_dev_mu);
    mdns_start(g_wifi.hostname(), std::string("TeklaPelletCAN ") + g_wifi.mac_hex().substr(8), engine.device_id_hex(), fw);
    ota_health_start();

    // Przycisk BOOT (GPIO9 na XIAO ESP32-C6) trzymany 10 s = reset fabryczny (hasło, sieć, ustawienia) – gdy masz fizyczny dostęp.
    gpio_config_t bc = {};
    bc.pin_bit_mask = 1ULL << 9; bc.mode = GPIO_MODE_INPUT; bc.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&bc);
    uint32_t boot_pressed_at = 0;

    // Odbiór CAN w osobnym zadaniu o wyższym priorytecie: ramki nie giną, gdy HTTP/JSON chwilowo zajmuje główną pętlę
    xTaskCreate([](void*) {
        for (;;) {
            if (can_ok_hw && !g_set.cfg.demo) {
                tpc::CanFrame f;
                int n = 0;
                xSemaphoreTake(can_mu, portMAX_DELAY);
                while (n++ < 24 && can.receive(f)) {
                    rx_total++;
                    if (xQueueSend(rxq, &f, 0) != pdTRUE) rx_dropped++;
                }
                xSemaphoreGive(can_mu);
            }
            vTaskDelay(pdMS_TO_TICKS(1));
        }
    }, "can_rx", 4096, nullptr, 6, nullptr);

    uint32_t last_can_try = 0, last_sum = 0, rx = 0;
    for (;;) {
        const uint32_t t = now_ms();
        xSemaphoreTake(g_dev_mu, portMAX_DELAY);
        if (g_set.cfg.demo) {
            engine.tick(t);
            auto frames = sim.to_engine; sim.to_engine.clear();
            for (auto& f : frames) { rx++; engine.on_frame(f, t); }
        } else {
            if (!can_ok_hw && t - last_can_try > 10000) {      // CAN niegotowy: ponawiamy co 10 s, sieć działa niezależnie
                last_can_try = t;
                xSemaphoreTake(can_mu, portMAX_DELAY);
                if (!spi_ok) spi_ok = spi.init(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS, 4'000'000);
                const bool up = spi_ok && can.begin(tpc::CanSpeed::K125, tpc::CanClock::MHz16, tpc::CanMode::Normal);
                xSemaphoreGive(can_mu);
                if (up) { can_ok_hw = true; log_add("MCP2515 OK, CAN 125 kbit/s"); }
                else log_add(spi_ok ? "MCP2515 nie odpowiada (sprawdz okablowanie SPI/zasilanie modulu)" : "blad SPI");
            }
            tpc::CanFrame f;
            int guard = 0;
            while (guard++ < 64 && xQueueReceive(rxq, &f, 0) == pdTRUE) { rx++; engine.on_frame(f, t); }
            engine.tick(t);
        }
        if (t - last_sum >= 30000) {                           // podsumowanie co 30 s do dziennika
            last_sum = t;
            char b[220];
            unsigned eflg = 0;
            if (can_ok_hw) {   // flagi błędów MCP2515 są „lepkie": odczytaj i wyzeruj, żeby widzieć tylko NOWE przepełnienia
                xSemaphoreTake(can_mu, portMAX_DELAY);
                eflg = can.error_flags();
                if (eflg) can.clear_error_flags();
                xSemaphoreGive(can_mu);
                if (eflg & 0xC0) mcp_overflows++;
            }
            snprintf(b, sizeof b, "STAN t=%us can_ok=%d ramek=%u odrzuc=%u wifi=%s heap=%u mcp_err=0x%02X przepelnien=%u", (unsigned)(t / 1000),
                     engine.can_ok(t) ? 1 : 0, (unsigned)rx_total, (unsigned)rx_dropped, g_wifi.online() ? g_wifi.ip().c_str() : "AP/brak",
                     (unsigned)esp_get_free_heap_size(), eflg, (unsigned)mcp_overflows);
            log_add(b);
        }
        xSemaphoreGive(g_dev_mu);
        if (gpio_get_level(GPIO_NUM_9) == 0) {
            if (!boot_pressed_at) boot_pressed_at = t;
            if (t - boot_pressed_at > 10000) { log_add("RESET FABRYCZNY (przycisk BOOT 10 s)"); g_store.factory_reset(); vTaskDelay(pdMS_TO_TICKS(300)); esp_restart(); }
        } else boot_pressed_at = 0;
        vTaskDelay(pdMS_TO_TICKS(2));
    }
}
