#include "ota_idf.h"
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_partition.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "logging.h"

static const char* TAG = "ota";

size_t EspOtaTarget::max_image_size() {
    const esp_partition_t* p = esp_ota_get_next_update_partition(nullptr);
    return p ? p->size : 0;
}

bool EspOtaTarget::begin(size_t total) {
    const esp_partition_t* p = esp_ota_get_next_update_partition(nullptr);
    if (!p || total > p->size) { log_add("OTA: brak partycji docelowej lub obraz za duzy"); return false; }
    esp_ota_handle_t h = 0;
    esp_err_t e = esp_ota_begin(p, OTA_WITH_SEQUENTIAL_WRITES, &h);
    if (e != ESP_OK) { log_add(std::string("OTA: esp_ota_begin: ") + esp_err_to_name(e)); return false; }
    part_ = p; handle_ = h; open_ = true;
    log_add(std::string("OTA: start, partycja ") + p->label + ", " + std::to_string(total) + " B");
    return true;
}

bool EspOtaTarget::write(const uint8_t* d, size_t n) {
    if (!open_) return false;
    esp_err_t e = esp_ota_write((esp_ota_handle_t)handle_, d, n);
    if (e != ESP_OK) { log_add(std::string("OTA: blad zapisu: ") + esp_err_to_name(e)); return false; }
    return true;
}

bool EspOtaTarget::end() {
    if (!open_) return false;
    open_ = false;
    esp_err_t e = esp_ota_end((esp_ota_handle_t)handle_);
    if (e != ESP_OK) { log_add(std::string("OTA: esp_ota_end: ") + esp_err_to_name(e)); return false; }
    e = esp_ota_set_boot_partition((const esp_partition_t*)part_);
    if (e != ESP_OK) { log_add(std::string("OTA: set_boot_partition: ") + esp_err_to_name(e)); return false; }
    log_add("OTA: podpis OK, nowa partycja ustawiona jako startowa");
    return true;
}

void EspOtaTarget::abort() {
    if (open_) { esp_ota_abort((esp_ota_handle_t)handle_); open_ = false; log_add("OTA: przerwano, partycja nieaktywowana"); }
}

// Po restarcie z nowym obrazem (stan PENDING_VERIFY): potwierdź, gdy aplikacja działa stabilnie przez 25 s.
// Jeśli bootloader ma włączony rollback, a aplikacja się zawiesza/restartuje przed potwierdzeniem – wraca poprzednia wersja.
static void health_task(void*) {
    vTaskDelay(pdMS_TO_TICKS(25000));
    esp_err_t e = esp_ota_mark_app_valid_cancel_rollback();
    log_add(std::string("OTA: aplikacja potwierdzona jako dzialajaca (") + esp_err_to_name(e) + ")");
    vTaskDelete(nullptr);
}

void ota_health_start() {
    const esp_partition_t* run = esp_ota_get_running_partition();
    esp_ota_img_states_t st;
    if (run && esp_ota_get_state_partition(run, &st) == ESP_OK && st == ESP_OTA_IMG_PENDING_VERIFY) {
        log_add("OTA: nowa wersja czeka na potwierdzenie (25 s pracy bez restartu)");
        xTaskCreate(health_task, "ota_health", 3072, nullptr, 3, nullptr);
    }
}

std::string ota_status_text() {
    const esp_partition_t* run = esp_ota_get_running_partition();
    const esp_partition_t* nxt = esp_ota_get_next_update_partition(nullptr);
    esp_ota_img_states_t st = ESP_OTA_IMG_UNDEFINED;
    if (run) esp_ota_get_state_partition(run, &st);
    const char* sn = st == ESP_OTA_IMG_NEW ? "new" : st == ESP_OTA_IMG_PENDING_VERIFY ? "pending" : st == ESP_OTA_IMG_VALID ? "valid" :
                     st == ESP_OTA_IMG_INVALID ? "invalid" : st == ESP_OTA_IMG_ABORTED ? "aborted" : "undefined";
    return std::string("{\"running\":\"") + (run ? run->label : "?") + "\",\"next\":\"" + (nxt ? nxt->label : "?") +
           "\",\"state\":\"" + sn + "\",\"max_image\":" + std::to_string(nxt ? nxt->size : 0) + "}";
}

std::string ota_rollback_previous() {
    const esp_partition_t* other = esp_ota_get_next_update_partition(nullptr);
    if (!other) return "no_partition";
    esp_app_desc_t desc;
    if (esp_ota_get_partition_description(other, &desc) != ESP_OK) return "no_valid_image";   // druga partycja jest pusta/uszkodzona
    esp_err_t e = esp_ota_set_boot_partition(other);
    if (e != ESP_OK) return std::string("set_boot_failed");
    log_add(std::string("ROLLBACK: nastepny start z partycji ") + other->label + " (" + desc.project_name + " " + desc.version + ")");
    return "";
}
