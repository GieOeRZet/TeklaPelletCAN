// TeklaPelletCAN – punkt wejścia. Na tym etapie: start MCP2515 i test odczytu jednego rejestru.
#include <cstdio>
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "mcp2515.h"
#include "sdo.h"
#include "spi_idf.h"

static const char* TAG = "tpc";

// XIAO ESP32-C6 + Seeed CAN Bus Breakout (jak w PelletCAN)
constexpr int PIN_SCK = 19, PIN_MISO = 20, PIN_MOSI = 18, PIN_CS = 17;
constexpr uint8_t BOILER_NODE = 4;

extern "C" void app_main(void) {
    static IdfSpi spi;
    if (!spi.init(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS, 4'000'000)) {
        ESP_LOGE(TAG, "blad SPI");
        return;
    }
    static tpc::Mcp2515 can(spi);
    if (!can.begin(tpc::CanSpeed::K125, tpc::CanClock::MHz16, tpc::CanMode::Normal)) {
        ESP_LOGE(TAG, "MCP2515 nie odpowiada");
        return;
    }
    ESP_LOGI(TAG, "CAN gotowy");

    for (;;) {
        // Próbny odczyt: 0x2207 sub 1 (min. temp. pomp).
        can.send(tpc::sdo_read_request(BOILER_NODE, 0x2207, 1));
        const int64_t t0 = esp_timer_get_time();
        while (esp_timer_get_time() - t0 < 200'000) {
            tpc::CanFrame f;
            if (can.receive(f)) {
                tpc::SdoReply r = tpc::sdo_parse_reply(BOILER_NODE, f);
                if (r.status == tpc::SdoStatus::Ok && !r.is_write_ack)
                    ESP_LOGI(TAG, "0x%04X.%u = %u", r.index, r.sub, (unsigned)r.value);
                else if (r.status == tpc::SdoStatus::Abort)
                    ESP_LOGW(TAG, "abort 0x%08X", (unsigned)r.abort_code);
            }
            vTaskDelay(1);
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
