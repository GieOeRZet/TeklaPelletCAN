#pragma once
#include <string>

// Dziennik zdarzeń: przechwytuje cały log ESP-IDF (ESP_LOGx) do bufora w pamięci RTC, który przeżywa restart,
// panikę i rollback OTA. Dostępny przez API (/api/v1/log, /api/v1/export) i na stronie ustawień.
void log_init();
void log_add(const std::string& line);           // własny wpis (ten sam bufor)
std::string log_get(size_t max_bytes);           // 0 = całość
void log_clear();
bool log_survived();                             // czy w buforze jest zapis sprzed restartu
