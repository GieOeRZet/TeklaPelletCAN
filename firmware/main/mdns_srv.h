#pragma once
#include <string>
// Ogłasza usługę _teklapelletcan._tcp przez mDNS (Home Assistant i aplikacja znajdują urządzenie same).
void mdns_start(const std::string& host, const std::string& instance, const std::string& id_hex, const std::string& fw);
