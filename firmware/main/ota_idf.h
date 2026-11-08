#pragma once
#include <string>
#include "ota.h"

// Cel zapisu OTA na nieaktywną partycję aplikacji (esp_ota_*). Obraz jest aktywowany dopiero po poprawnym podpisie.
class EspOtaTarget : public tpc::OtaTarget {
public:
    bool begin(size_t total_size) override;
    bool write(const uint8_t* data, size_t len) override;
    bool end() override;
    void abort() override;
    static size_t max_image_size();

private:
    const void* part_ = nullptr;
    unsigned handle_ = 0;
    bool open_ = false;
};

// Po aktualizacji: potwierdza nową wersję, gdy działa (patrz main), albo wraca do poprzedniej.
void ota_health_start();
std::string ota_status_text();
// Przełącza start na poprzednią partycję (np. stary firmware ESPHome), jeśli zawiera poprawny obraz. "" = OK, inaczej komunikat.
std::string ota_rollback_previous();
