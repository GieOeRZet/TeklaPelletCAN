#pragma once
// Prosty serwer DNS dla portalu (captive portal): każde zapytanie A dostaje adres urządzenia (10.77.77.1).
// Czysta funkcja budująca odpowiedź – gniazdo UDP obsługuje warstwa platformy.
#include <cstddef>
#include <cstdint>
#include <vector>

namespace tpc {

// `ipv4_be` – adres w porządku sieciowym (bajty a.b.c.d jako a<<24|...). Zwraca pustą odpowiedź dla śmieci.
std::vector<uint8_t> dns_captive_response(const uint8_t* query, size_t len, uint32_t ipv4);

}  // namespace tpc
