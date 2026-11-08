#pragma once
#include <cstdint>

// Pole na dane pierwszego uruchomienia – wypełniane w pliku .bin lokalnym skryptem tools/patch_firstboot.py
// (SSID, hasło Wi-Fi, stały IP, hasło urządzenia), żeby nowy firmware wgrany zdalnie sam dołączył do sieci.
// Sekrety nie trafiają do repozytorium ani do CI. Magic występuje w pliku dokładnie raz.
struct FirstBoot {
    char magic[16];        // "TPC-FIRSTBOOT-v1"
    uint8_t valid;         // 0 = puste, 1 = wypełnione
    uint8_t dhcp;          // 1 = DHCP
    uint8_t rsv[2];
    char ssid[33];
    char pass[65];
    char ip[16], gw[16], mask[16], dns[16];
    char dev_pass[33];     // hasło urządzenia (opcjonalne)
    char pad[3];
};
extern volatile FirstBoot g_firstboot;
