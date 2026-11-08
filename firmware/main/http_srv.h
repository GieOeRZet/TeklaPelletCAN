#pragma once
#include "api.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

// Serwer HTTP: API (tpc::Api), strony (karta, portal, ustawienia – osadzone w obrazie), captive portal i OTA (strumieniowo).
// `dev_mutex` chroni Engine i Api (ten sam muteks bierze pętla silnika).
bool http_start(tpc::Api* api, SemaphoreHandle_t dev_mutex);
