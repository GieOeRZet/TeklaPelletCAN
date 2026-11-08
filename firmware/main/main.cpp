// TeklaPelletCAN – etap uruchomieniowy (bring-up): silnik na prawdziwym CAN, wyniki w logu szeregowym.
// BEZPIECZNIE: tryb mirror włączony – urządzenie TYLKO CZYTA z kotła, niczego nie zapisuje.
#include <cstdio>
#include <string>
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "engine.h"
#include "mcp2515.h"
#include "spi_idf.h"

static const char* TAG = "tpc";

// XIAO ESP32-C6 + Seeed CAN Bus Breakout (jak w PelletCAN)
constexpr int PIN_SCK = 19, PIN_MISO = 20, PIN_MOSI = 18, PIN_CS = 17;

static uint32_t now_ms() { return (uint32_t)(esp_timer_get_time() / 1000); }

extern "C" void app_main(void) {
    static IdfSpi spi;
    if (!spi.init(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS, 4'000'000)) { ESP_LOGE(TAG, "blad SPI"); return; }
    static tpc::Mcp2515 can(spi);
    if (!can.begin(tpc::CanSpeed::K125, tpc::CanClock::MHz16, tpc::CanMode::Normal)) {
        ESP_LOGE(TAG, "MCP2515 nie odpowiada (sprawdz okablowanie SPI i zasilanie 5 V modulu)");
        return;
    }
    ESP_LOGI(TAG, "MCP2515 OK, CAN 125 kbit/s");

    uint8_t mac[6];
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    tpc::EngineConfig cfg;
    cfg.access.mirror = true;      // bring-up: tylko odczyt
    cfg.boot_delay_ms = 3000;
    cfg.fw = "0.1.0-bringup";
    static tpc::Engine engine(cfg, [](const tpc::CanFrame& f) { return can.send(f); }, mac);
    ESP_LOGI(TAG, "id urzadzenia %s, tryb: tylko odczyt", engine.device_id_hex().c_str());

    uint32_t last_log = 0, rx = 0, rx_pdo = 0;
    for (;;) {
        tpc::CanFrame f;
        while (can.receive(f)) {
            rx++;
            if (f.id == 0x356 || f.id == 0x456) rx_pdo++;
            engine.on_frame(f, now_ms());
        }
        engine.tick(now_ms());

        const uint32_t t = now_ms();
        if (t - last_log >= 5000) {
            last_log = t;
            uint32_t eflg = can.error_flags();
            ESP_LOGI(TAG, "t=%us can_ok=%d ramek=%u (PDO %u) bledy_mcp=0x%02X", (unsigned)(t / 1000), engine.can_ok(t) ? 1 : 0,
                     (unsigned)rx, (unsigned)rx_pdo, (unsigned)eflg);
            const char* ids[] = {"boiler_temp", "boiler_set_manual", "burner_state", "hw_temp", "ch1_temp", "ret_temp",
                                 "outside_temp", "tank_kg", "boiler_on"};
            std::string line;
            for (const char* id : ids) {
                uint32_t raw;
                char b[40];
                if (engine.raw_of(id, raw)) snprintf(b, sizeof b, " %s=0x%X", id, (unsigned)raw);
                else snprintf(b, sizeof b, " %s=-", id);
                line += b;
            }
            ESP_LOGI(TAG, "odczyty (surowe):%s", line.c_str());
            ESP_LOGI(TAG, "alarm: %s | podajnik PDO: %s", engine.text_of("alarm_last_text").c_str(),
                     engine.text_of("feeder_running").c_str());
        }
        vTaskDelay(pdMS_TO_TICKS(2));
    }
}
