#pragma once
// Minimalny responder mDNS: ogłasza usługę _teklapelletcan._tcp (wykrywanie przez Home Assistant / aplikację).
// Czyste funkcje budujące pakiety; gniazdo multicast (224.0.0.251:5353) obsługuje warstwa platformy.
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace tpc {

struct MdnsConfig {
    std::string host;                       // nazwa hosta bez ".local", np. "teklapelletcan-a1b2c3"
    std::string instance;                   // nazwa instancji usługi, np. "TeklaPelletCAN A1B2C3"
    std::string service = "_teklapelletcan._tcp";
    uint16_t port = 80;
    uint32_t ipv4 = 0;                      // a<<24|b<<16|c<<8|d
    std::vector<std::string> txt;           // np. {"id=A1B2C3D4E5F6", "fw=0.1.0", "api=1"}
};

// Odpowiedź na pakiet zapytania mDNS (pusty wektor = nie mamy nic do powiedzenia).
std::vector<uint8_t> mdns_respond(const MdnsConfig& cfg, const uint8_t* query, size_t len);

// Niezamawiane ogłoszenie (po uzyskaniu IP i okresowo).
std::vector<uint8_t> mdns_announce(const MdnsConfig& cfg);

}  // namespace tpc
